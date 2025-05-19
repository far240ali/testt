from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '5355055672:AAHoidc0x6nM3g2JHmb7xhWKmwGJOoKFNXY'


# ربات را با اطلاعات خود راه‌اندازی کنید
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# هندلر برای دستور /start
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await message.reply_text("سلام! به ربات خوش آمدید.")

    def new_user(self, id: int):
        """ایجاد یک دیکشنری برای کاربر جدید با مقادیر پیش‌فرض."""
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            plan="free",  # پلن پیش‌فرض
            plan_expiry=None,  # تاریخ انقضای پلن برای پلن‌های غیر رایگان
            daily_usage=0,  # میزان استفاده روزانه کاربر
            daily_link_count=0,  # تعداد لینک‌های ایجاد شده در روز جاری
            daily_limit=DAILY_LIMITS.get("free", 2 * 1024 * 1024 * 1024),  # محدودیت روزانه از DAILY_LIMITS
            last_reset_date=str(datetime.date.today()), # تاریخ آخرین ریست آمار روزانه
            is_banned=False, # وضعیت بن کاربر، پیش‌فرض غیر بن شده
            invited_count=0,  # تعداد کاربرانی که این کاربر دعوت کرده
            points=0          # امتیاز کاربر برای سیستم دعوت
        )
async def get_invite_stats(self, user_id: int):
    """دریافت آمار دعوت کاربر."""
    user = await self.col.find_one({'id': user_id})
    if user:
        invited_count = user.get('invited_count', 0)
        points = user.get('points', 0)

async def update_invite_stats(self, inviter_id: int):
    """افزایش تعداد دعوت و امتیاز کاربر دعوت کننده."""
    await self.col.update_one(
        {'id': inviter_id},
        {'$inc': {'invited_count': 1, 'points': INVITE_REWARD}},
        upsert=True
    )


#db = Database(Var.DATABASE_URL, Var.name)
#UPDATES_CHANNEL = Var.UPDATES_CHANNEL
INVITE_REWARD = 5

async def get_invite_link(user_id: int):
    """تولید لینک دعوت برای کاربر."""
    link = f"https://t.me/{app.me.username}?start={user_id}"
    return link

async def get_invite_stats(user_id: int):
    """دریافت آمار دعوت کاربر."""
    user = await db.col.find_one({'id': user_id})
    if user:
        invited_count = user.get('invited_count', 0)
        points = user.get('points', 0)
        return invited_count, points
    return 0, 0

async def update_invite_stats(inviter_id: int):
    """افزایش تعداد دعوت و امتیاز کاربر دعوت کننده."""
    await db.col.update_one(
        {'id': inviter_id},
        {'$inc': {'invited_count': 1, 'points': INVITE_REWARD}},
        upsert=True
    )

@app.on_message(filters.private & filters.command(["invite"]))
async def invite_command(bot: Client, message):
    user_id = message.from_user.id
    invite_link = await get_invite_link(user_id)
    invited_count, points = await get_invite_stats(user_id)

    text = f"🔗 **لینک دعوت اختصاصی شما:**\n`{invite_link}`\n\n" \
           f"👤 **تعداد دعوت‌های شما:** {invited_count}\n" \
           f"💰 **امتیاز شما:** {points}\n\n" \
           f"📤 این لینک را با دوستان خود به اشتراک بگذارید و به ازای هر عضویت {INVITE_REWARD} امتیاز دریافت کنید!"

    await message.reply_text(text, quote=True)

@app.on_message(filters.private & filters.incoming & filters.regex(r"^/start (\d+)$"))
async def handle_invite(bot: Client, message):
    try:
        invited_by = int(message.matches[0].group(1))
        new_user_id = message.from_user.id

        if invited_by == new_user_id:
            return # Don't reward self-invites

        # بررسی اینکه آیا کاربر جدید قبلاً ثبت نام کرده است یا خیر
        if not await db.is_user_exist(new_user_id):
            await db.add_user(new_user_id)
            try:
                await bot.send_message(
                    Var.BIN_CHANNEL,
                    f"**<u>✅ کاربر جدیدی از طریق لینک دعوت پیوست 😍</u> \n\n__🔺 نام کاربر  :__ [{message.from_user.first_name}](tg://user?id={new_user_id}) \n __👤 دعوت کننده :__ `{invited_by}`\n __🤖 ربات : @{StreamBot.me.username}__ **"
                )
            except Exception as e:
                print(f"Error sending join log to BIN_CHANNEL: {e}")

            await update_invite_stats(invited_by)
            try:
                inviter_name = (await bot.get_users(invited_by)).first_name
            except Exception:
                inviter_name = invited_by
            await bot.send_message(
                invited_by,
                f"🎉 کاربر **{message.from_user.first_name}** با لینک دعوت شما به ربات پیوست!\n💰 {INVITE_REWARD} امتیاز به حساب شما اضافه شد."
            )
        else:
            # اگر کاربر قبلاً ثبت نام کرده است، نیازی به انجام مجدد عملیات نیست.
            pass

    except IndexError:
        # اگر پارامتر در /start وجود نداشت، این خطا رخ می‌دهد.
        pass
    except ValueError:
        # اگر پارامتر /start یک عدد معتبر نبود، این خطا رخ می‌دهد.
        pass
    except Exception as e:
        print(f"Error in handle_invite: {e}")




# اجرای ربات
app.run()
