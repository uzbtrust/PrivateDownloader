import re

def is_valid_telegram_link(link: str) -> bool:
    pattern = r"https?://t\.me/(?:c/)?(?:[a-zA-Z0-9_]+|[0-9]+)/[0-9]+"
    return bool(re.match(pattern, link))

import time

def format_progress(current: int, total: int, start_time: float, prefix: str = "") -> str:
    if total <= 0:
        return f"{prefix} Yuklanmoqda..."
        
    percent = current / total
    filled_len = int(15 * percent)
    bar = "█" * filled_len + "░" * (15 - filled_len)
    
    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    
    elapsed = time.time() - start_time
    if elapsed > 0 and current > 0:
        speed_bps = current / elapsed
        speed_mbps = speed_bps / (1024 * 1024)
        
        remaining_bytes = total - current
        eta_seconds = remaining_bytes / speed_bps
        
        if eta_seconds >= 86400:
            eta_str = f"{int(eta_seconds // 86400)}d {int((eta_seconds % 86400) // 3600)}h"
        elif eta_seconds >= 3600:
            eta_str = f"{int(eta_seconds // 3600)}h {int((eta_seconds % 3600) // 60)}m"
        elif eta_seconds >= 60:
            eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
        else:
            eta_str = f"{int(eta_seconds)}s"
            
        speed_str = f"{speed_mbps:.1f} MB/s"
    else:
        speed_str = "0.0 MB/s"
        eta_str = "--s"

    return (
        f"{prefix} [{bar}] {percent * 100:.1f}%\n"
        f"📦 {current_mb:.1f}MB / {total_mb:.1f}MB\n"
        f"🚀 Tezlik: {speed_str} | ⏳ Vaqt: {eta_str}"
    )
