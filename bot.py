from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_webhook
import random
import json
import os

TOKEN = "8594594585:AAGHLB9D6qcn6J32fAEOsR-cm2BGCW6j4b0
CHANNEL_USERNAME = "teleegram_gmr_bot"
ADMIN_ID = 7095525795

WEBHOOK_HOST = https://dev-ichancy.pantheonsite.io
WEBHOOK_PATH = "/bot"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 5000))

DATA_FILE = "data.json"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

admin_state = {}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "wheel": ["10 ل.س", "20 ل.س", "50 ل.س", "خسرت 😢"]}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def main_keyboard(is_admin=False):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("💰 شحن رصيد", "💸 سحب رصيد")
    kb.row("🔥 نظام الإحالات", "🎁 كود هدية")
    kb.row("🎉 إهداء رصيد", "📩 تواصل معنا")
    kb.row("📜 الشروط والأحكام", "📱 ichancy apk")
    kb.row("🧾 السجل", "🌐 اللغة / الحسابات")
    kb.row("📊 البونصات والعروض الحالية", "🎡 عجلة الحظ")
    if is_admin:
        kb.row("🛠 لوحة الأدمن")
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not await check_subscription(message.from_user.id):
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME}")
        )
        await message.answer("⚠️ يجب الاشتراك أولاً", reply_markup=keyboard)
        return

    uid = str(message.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {"balance": 0}
        save_data(data)

    await message.answer("مرحبًا بك 👋", reply_markup=main_keyboard(message.from_user.id == ADMIN_ID))

@dp.message_handler()
async def handle(message: types.Message):
    uid = str(message.from_user.id)
    text = message.text

    if uid not in data["users"]:
        data["users"][uid] = {"balance": 0}

    if text == "🎡 عجلة الحظ":
        prize = random.choice(data["wheel"])
        if "ل.س" in prize:
            amount = int(prize.replace(" ل.س", ""))
            data["users"][uid]["balance"] += amount
            save_data(data)
            await message.answer(f"🎉 ربحت {amount} ل.س\\n💰 رصيدك: {data['users'][uid]['balance']}")
        else:
            await message.answer("😢 خسرت")
    elif text == "🔥 نظام الإحالات":
        await message.answer(f"https://t.me/{CHANNEL_USERNAME}?start={message.from_user.id}")
    else:
        await message.answer("اختر من القائمة")

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
