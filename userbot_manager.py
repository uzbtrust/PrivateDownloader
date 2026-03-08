import os
import asyncio
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
import config
import database

clients = {}
auth_sessions = {}

def get_client(phone_number: str) -> Client:
    if phone_number in clients:
        return clients[phone_number]
    
    session_name = os.path.join(config.SESSION_DIR, phone_number.replace("+", ""))
    client = Client(
        name=session_name,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        in_memory=False
    )
    clients[phone_number] = client
    return client

async def start_auth(phone_number: str):
    client = get_client(phone_number)
    await client.connect()
    try:
        sent_code = await client.send_code(phone_number)
        auth_sessions[phone_number] = {
            "phone_code_hash": sent_code.phone_code_hash,
            "client": client
        }
        return {"ok": True, "phone_code_hash": sent_code.phone_code_hash}
    except Exception as e:
        if client.is_connected:
            await client.disconnect()
        await disconnect_auth(phone_number)
        return {"ok": False, "error": str(e)}

async def sign_in(phone_number: str, phone_code: str):
    if phone_number not in auth_sessions:
        return {"ok": False, "error": "Auth session topilmadi"}
        
    client = auth_sessions[phone_number]["client"]
    phone_code_hash = auth_sessions[phone_number]["phone_code_hash"]
    
    try:
        user = await client.sign_in(phone_number, phone_code_hash, phone_code)
        session_string = await client.export_session_string()
        await database.add_account(phone_number)
        await database.update_account_session(phone_number, session_string)
        del auth_sessions[phone_number]
        return {"ok": True, "user": user}
    except SessionPasswordNeeded:
        return {"ok": True, "requires_password": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def check_password(phone_number: str, password: str):
    if phone_number not in auth_sessions:
        return {"ok": False, "error": "Auth session topilmadi"}
        
    client = auth_sessions[phone_number]["client"]
    
    try:
        user = await client.check_password(password)
        session_string = await client.export_session_string()
        await database.add_account(phone_number)
        await database.update_account_session(phone_number, session_string)
        del auth_sessions[phone_number]
        return {"ok": True, "user": user}
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def disconnect_auth(phone_number: str):
    if phone_number in auth_sessions:
        client = auth_sessions[phone_number]["client"]
        if client.is_connected:
            await client.disconnect()
        del auth_sessions[phone_number]
        
    if phone_number in clients:
        del clients[phone_number]
        
    has_account = await database.get_account_session(phone_number)
    if not has_account:
        session_name = os.path.join(config.SESSION_DIR, phone_number.replace("+", ""))
        for ext in [".session", ".session-journal"]:
            file_path = f"{session_name}{ext}"
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

async def download_message_media(phone_number: str, link: str, progress_callback=None):
    client = get_client(phone_number)
    try:
        if not client.is_connected:
            await client.connect()
            
        parts = link.rstrip('/').split('/')
        if len(parts) < 2:
            return {"ok": False, "error": "Link noto'g'ri formatda"}
            
        message_id = int(parts[-1])
        chat_id = None
        
        if "c" in parts:
            chat_id = int(f"-100{parts[-2]}")
        else:
            chat_id = parts[-2]
            
        try:
            message = await client.get_messages(chat_id, message_id)
        except Exception as msg_err:
            if "PeerIdInvalid" in str(msg_err) or "Peer id invalid" in str(msg_err) or "PEER_ID_INVALID" in str(msg_err):
                try:
                    found = False
                    async for dialog in client.get_dialogs():
                        if dialog.chat and dialog.chat.id == chat_id:
                            found = True
                            break
                    
                    if not found:
                        return {"ok": False, "error": f"Siz bu kanalga a'zo emassiz yoki kanal mavjud emas: {chat_id}"}
                        
                    message = await client.get_messages(chat_id, message_id)
                except Exception as inner_err:
                     return {"ok": False, "error": f"Kanalni topib bo'lmadi:\n{str(inner_err)}"}
            else:
                return {"ok": False, "error": f"Xabarni olishda xatolik:\n{str(msg_err)}"}
            
        if not message or message.empty:
             return {"ok": False, "error": "Xabarni topib bo'lmadi yoki ruxsat yo'q"}
             
        if message.media:
            file_path = await client.download_media(message, file_name=config.DATA_DIR + "/", progress=progress_callback)
            return {"ok": True, "type": "media", "file_path": file_path, "caption": message.caption, "text": None, "message": message}
        elif message.text:
            return {"ok": True, "type": "text", "text": message.text, "file_path": None, "message": message}
        else:
            return {"ok": False, "error": "Qo'llab-quvvatlanmaydigan xabar turi"}
            
    except Exception as e:
        return {"ok": False, "error": str(e)}
