# ====================== CONFIG ======================
TOKEN = "8721576580:AAFOr6jLhcQNZc1iDJALflTTOlBRmq6baLI"
ADMIN_ID = 7095525795
SY_CURRENCY = "SY"
REFERRAL_BONUS = 20  # مكافأة الإحالات الافتراضية

# ====================== DATABASE ======================
import sqlite3
conn = sqlite3.connect("bot.db", check_same_thread=False)
c = conn.cursor()

# جدول المستخدمين
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    sy_balance INTEGER DEFAULT 0
)
''')

# جدول عجلة الحظ
c.execute('''
CREATE TABLE IF NOT EXISTS wheel_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prize_name TEXT,
    prize_amount INTEGER,
    probability REAL
)
''')

# جدول الإحالات
c.execute('''
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER,
    referred_id INTEGER,
    bonus_given INTEGER DEFAULT 0
)
''')
conn.commit()

# ====================== IMPORTS ======================
import telebot
from telebot import types
import random

bot = telebot.TeleBot(TOKEN)

# ====================== HELPERS ======================
def register_user(user):
    c.execute("SELECT id FROM users WHERE id=?", (user.id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (id, username, sy_balance) VALUES (?, ?, ?)",
                  (user.id, user.username or user.first_name, 0))
        conn.commit()

def update_balance(user_id, amount):
    c.execute("UPDATE users SET sy_balance = sy_balance + ? WHERE id=?", (amount, user_id))
    conn.commit()

# ====================== WHEEL OF FORTUNE ======================
def spin_wheel(user_id):
    c.execute("SELECT prize_name, prize_amount, probability FROM wheel_config")
    prizes = c.fetchall()
    if not prizes:
        return "لم يتم إعداد عجلة الحظ بعد من الأدمن!"
    total = sum(p[2] for p in prizes)
    r = random.uniform(0, total)
    upto = 0
    for prize_name, prize_amount, probability in prizes:
        if upto + probability >= r:
            if prize_name == 'SY':
                update_balance(user_id, prize_amount)
            return f"لقد حصلت على {prize_amount} {prize_name}!"
        upto += probability
    return "حظ أوفر في المرة القادمة!"

# ====================== GAMES ======================
def guess_number_game(bot, message):
    number = random.randint(1, 10)
    bot.send_message(message.chat.id, f"تخمين رقم بين 1 و 10. الرقم السري: {number}")

def rock_paper_scissors_game(bot, message):
    choices = ["حجر", "ورق", "مقص"]
    bot_choice = random.choice(choices)
    bot.send_message(message.chat.id, f"اختر: حجر، ورق، مقص. البوت اختار: {bot_choice}")

def dice_roll_game(bot, message):
    roll = random.randint(1, 6)
    bot.send_message(message.chat.id, f"تم رمي الزهر وظهر: {roll}")

def blackjack_game(bot, message):
    player = random.randint(15, 21)
    dealer = random.randint(15, 21)
    if player > dealer:
        bot.send_message(message.chat.id, f"انت: {player} | البوت: {dealer} → فزت!")
        update_balance(message.from_user.id, 10)
    else:
        bot.send_message(message.chat.id, f"انت: {player} | البوت: {dealer} → خسرت!")

def roulette_game(bot, message):
    number = random.randint(0, 36)
    bot.send_message(message.chat.id, f"تم دوران الروليت وظهر الرقم: {number}")

def speed_quiz_game(bot, message):
    bot.send_message(message.chat.id, f"سؤال سريع: ما هو 2 + 2؟ (أجب خلال 10 ثواني)")

def race_game(bot, message):
    positions = ["أنت الأول", "أنت الثاني", "أنت الثالث"]
    result = random.choice(positions)
    bot.send_message(message.chat.id, f"نتيجة السباق: {result}")

def memory_game(bot, message):
    sequence = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    bot.send_message(message.chat.id, f"تذكر هذا الرقم: {sequence}")

def luck_draw_game(bot, message):
    amount = random.randint(-10, 50)
    update_balance(message.from_user.id, amount)
    bot.send_message(message.chat.id, f"لقد حصلت على {amount} {SY_CURRENCY}")

def daily_challenges_game(bot, message):
    reward = random.randint(5, 20)
    update_balance(message.from_user.id, reward)
    bot.send_message(message.chat.id, f"لقد أكملت التحدي اليومي وربحت {reward} {SY_CURRENCY}")

# ====================== REFERRALS ======================
def referral_button_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("الإحالات")
    return markup

@bot.message_handler(func=lambda m: m.text == "الإحالات")
def referrals(message):
    ref_link = f"https://t.me/اسم_البوت?start={message.from_user.id}"
    bot.send_message(message.chat.id,
                     f"شارك رابطك مع أصدقائك:\n{ref_link}\nكل صديق ينضم تحصل على {REFERRAL_BONUS} {SY_CURRENCY}")

# ====================== ADMIN PANEL ======================
def show_admin_panel(bot, chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = ["إضافة جائزة عجلة", "تعديل جائزة", "إيداع SY", "سحب SY",
               "عرض المستخدمين", "تعديل مكافأة الدعوات"]
    markup.add(*buttons)
    bot.send_message(chat_id, "لوحة الأدمن:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "تعديل مكافأة الدعوات")
def admin_update_referral_bonus(message):
    global REFERRAL_BONUS
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "ليس لديك صلاحيات الأدمن.")
        return
    msg = bot.send_message(message.chat.id, "أدخل قيمة مكافأة الدعوة الجديدة:")
    bot.register_next_step_handler(msg, set_new_referral_bonus)

def set_new_referral_bonus(message):
    global REFERRAL_BONUS
    try:
        REFERRAL_BONUS = int(message.text)
        bot.send_message(message.chat.id, f"تم تحديث مكافأة الدعوة إلى {REFERRAL_BONUS} {SY_CURRENCY}")
    except:
        bot.send_message(message.chat.id, "الرجاء إدخال رقم صحيح.")

# ====================== COMMANDS ======================
@bot.message_handler(commands=['start'])
def start(message):
    register_user(message.from_user)
    # تحقق من وجود إحالة
    if message.text.startswith("/start "):
        try:
            ref_id = int(message.text.split()[1])
            if ref_id != message.from_user.id:
                c.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)", (ref_id, message.from_user.id))
                update_balance(ref_id, REFERRAL_BONUS)
                conn.commit()
                bot.send_message(message.chat.id, "تم تسجيلك مع مكافأة لصاحب الدعوة!")
        except:
            pass
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = ["عجلة الحظ", "تخمين رقم", "حجر ورق مقص", "رول زهر", "بلاك جاك", "روليت",
               "سريع", "سباق", "ذاكرة", "سحب الحظ", "تحديات يومية", "الإحالات"]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "اختر اللعبة:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        show_admin_panel(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "ليس لديك صلاحيات الأدمن.")

# ====================== PLAY GAMES ======================
@bot.message_handler(func=lambda m: True)
def play_game(message):
    text = message.text
    if text == "عجلة الحظ":
        bot.send_message(message.chat.id, spin_wheel(message.from_user.id))
    elif text == "تخمين رقم":
        guess_number_game(bot, message)
    elif text == "حجر ورق مقص":
        rock_paper_scissors_game(bot, message)
    elif text == "رول زهر":
        dice_roll_game(bot, message)
    elif text == "بلاك جاك":
        blackjack_game(bot, message)
    elif text == "روليت":
        roulette_game(bot, message)
    elif text == "سريع":
        speed_quiz_game(bot, message)
    elif text == "سباق":
        race_game(bot, message)
    elif text