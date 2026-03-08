import re

def is_valid_telegram_link(link: str) -> bool:
    pattern = r"https?://t\.me/(?:c/)?(?:[a-zA-Z0-9_]+|[0-9]+)/[0-9]+"
    return bool(re.match(pattern, link))

def format_progress(current: int, total: int) -> str:
    if total <= 0:
        return "Yuklanmoqda..."
    percent = (current / total) * 100
    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    return f"{percent:.1f}% ({current_mb:.1f}MB / {total_mb:.1f}MB)"
