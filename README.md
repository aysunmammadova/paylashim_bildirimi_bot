# Facebook → Telegram Monitor
> Tam pulsuz · GitHub Actions · Heç bir server lazım deyil

DSMF və Əmək Nazirliyi Facebook səhifələrini hər 2 saatdan bir yoxlayır.
Yeni post gəldikdə Telegram-a avtomatik göndərir.

---

## Qurulum — 4 addım

### 1. Telegram Bot yarat

1. Telegram-da **@BotFather**-ə yaz
2. `/newbot` → ad ver (məs. `DSMF Xəbər`) → username ver (məs. `dsmf_xeber_bot`)
3. Sənə token gələcək: `7123456789:AAFxxx...` — **saxla**

4. Chat ID-ni tap:
   - Bota `/start` yaz
   - Brauzerdə bu URL-i aç (token-i əvəz et):
     ```
     https://api.telegram.org/bot<TOKEN>/getUpdates
     ```
   - Cavabda `"chat":{"id": 123456789}` — bu rəqəm sənin **Chat ID**-ndir

---

### 2. Facebook slug-larını düzəlt

`scraper.py` faylında `FB_PAGES` siyahısını öz slug-larınla dəyişdir:

```python
FB_PAGES = [
    "sosialmudafiefondu",   # facebook.com/sosialmudafiefondu
    "mlsoc.gov.az",         # facebook.com/mlsoc.gov.az
]
```

Slug = Facebook səhifəsinin URL-indəki son hissə.

---

### 3. GitHub repo yarat və yüklə

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/SƏNİN_USERNAME/fb-monitor.git
git push -u origin main
```

---

### 4. GitHub Secrets əlavə et

GitHub repo-nda: **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `TELEGRAM_TOKEN` | BotFather-dən aldığın token |
| `TELEGRAM_CHAT_ID` | Yuxarıda tapdığın rəqəm |

---

## İşə salma

- Avtomatik: hər 2 saatdan bir işləyir (UTC ilə `0 */2 * * *`)
- Əl ilə test: **Actions → FB Monitor → Run workflow**

---

## Saat tənzimlənməsi

`monitor.yml`-də cron-u dəyişdir:

```yaml
- cron: "0 */2 * * *"    # hər 2 saatdan bir
- cron: "0 8,12,16 * * *" # gündə 3 dəfə: 08:00, 12:00, 16:00 UTC
- cron: "0 6 * * *"       # gündə bir dəfə saat 06:00 UTC-də (= 10:00 Bakı)
```

> Bakı vaxtı = UTC + 4

---

## Fayllar

| Fayl | Məqsəd |
|------|--------|
| `scraper.py` | FB scraping + Telegram göndərmə |
| `seen_posts.json` | Görülmüş post ID-ləri (avtomatik yenilənir) |
| `.github/workflows/monitor.yml` | GitHub Actions cron job |
| `requirements.txt` | Python asılılıqları |
