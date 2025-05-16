from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = ''


# ربات را با اطلاعات خود راه‌اندازی کنید
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# هندلر برای دستور /start
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await message.reply_text("سلام! به ربات خوش آمدید.")

# اجرای ربات
app.run()
