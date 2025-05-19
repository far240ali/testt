import os
import instaloader
from pyrogram import Client, filters

# تنظیمات
API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '5355055672:AAHoidc0x6nM3g2JHmb7xhWKmwGJOoKFNXY'


# ربات را با اطلاعات خود راه‌اندازی کنید
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تابع دانلود اینستاگرام
def download_instagram_post(url: str, user_id: int) -> list:
    loader = instaloader.Instaloader(
        save_metadata=False,
        download_comments=False,
        dirname_pattern=f"downloads/{user_id}",
        filename_pattern="{shortcode}"
    )

    shortcode = url.strip("/").split("/")[-1]
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    loader.download_post(post, target=f"{user_id}")

    media_dir = f"downloads/{user_id}"
    files = [os.path.join(media_dir, f) for f in os.listdir(media_dir)]
    return files

# شروع
@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text("سلام! لینک پست یا ریلز اینستاگرام رو بفرست تا دانلود کنم.")

# دریافت لینک
@bot.on_message(filters.text & ~filters.command())
async def insta_handler(client, message):
    url = message.text.strip()

    if "instagram.com" not in url:
        await message.reply_text("لینک معتبر اینستاگرام ارسال کن.")
        return

    await message.reply_text("در حال پردازش لینک... لطفاً صبر کن.")

    try:
        files = download_instagram_post(url, message.from_user.id)

        for file_path in files:
            if file_path.endswith((".jpg", ".jpeg", ".png")):
                await message.reply_photo(photo=file_path)
            elif file_path.endswith(".mp4"):
                await message.reply_video(video=file_path)

        # حذف فایل‌ها بعد از ارسال
        for file_path in files:
            os.remove(file_path)
        os.rmdir(f"downloads/{message.from_user.id}")

    except Exception as e:
        await message.reply_text(f"خطا در دانلود: {e}")

# اجرای ربات
bot.run()
