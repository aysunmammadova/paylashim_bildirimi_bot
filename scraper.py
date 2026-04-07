import os
import json
import time
import logging
import requests
from facebook_scraper import get_posts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Facebook səhifə slug-ları — URL-dəki hissə
# Məs: facebook.com/sosialmudafiefondu → "sosialmudafiefondu"
FB_PAGES = [
    "https://www.facebook.com/dsmf.sosial.gov.az",   # ← öz slug-unla dəyişdir
    "https://www.facebook.com/sosial.gov.az",         # ← öz slug-unla dəyişdir
]

SEEN_FILE       = "seen_posts.json"
MAX_POSTS       = 5   # hər səhifədən son neçə post yoxlansın
# ──────────────────────────────────────────────────────────────────────────────


def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(list(seen)), f, indent=2)


def send_telegram(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if not r.ok:
            log.error(f"Telegram xəta: {r.status_code} {r.text}")
        return r.ok
    except Exception as e:
        log.error(f"Telegram göndərmə xətası: {e}")
        return False


def format_message(page: str, post: dict) -> str:
    text     = post.get("text") or post.get("post_text") or ""
    post_url = post.get("post_url") or f"https://facebook.com/{page}"
    time_str = ""
    if post.get("time"):
        try:
            time_str = post["time"].strftime("%d.%m.%Y %H:%M")
        except Exception:
            pass

    if len(text) > 800:
        text = text[:800] + "…"

    lines = [f"📢 <b>{page}</b>"]
    if time_str:
        lines.append(f"🕐 {time_str}")
    if text:
        lines.append(f"\n{text}")
    lines.append(f"\n🔗 <a href='{post_url}'>Postun linki</a>")
    return "\n".join(lines)


def check_page(page: str, seen: set) -> list:
    new_posts = []
    try:
        log.info(f"Yoxlanır: {page}")
        for post in get_posts(
            page,
            pages=1,
            options={"posts_per_page": MAX_POSTS}
        ):
            pid = post.get("post_id")
            if not pid:
                continue
            if pid not in seen:
                new_posts.append(post)
                seen.add(pid)
        log.info(f"{page}: {len(new_posts)} yeni post tapıldı")
    except Exception as e:
        log.error(f"{page} scrape xəta: {e}")
    return new_posts


def run():
    seen      = load_seen()
    total_new = 0

    for page in FB_PAGES:
        new_posts = check_page(page, seen)
        for post in reversed(new_posts):  # köhnədən yeniyə
            msg = format_message(page, post)
            ok  = send_telegram(msg)
            if ok:
                log.info(f"Göndərildi: {post.get('post_id')}")
            time.sleep(2)
        total_new += len(new_posts)
        time.sleep(4)

    save_seen(seen)
    log.info(f"Tamamlandı. Cəmi {total_new} yeni post göndərildi.")
    return total_new


if __name__ == "__main__":
    run()
