import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# ----------------- ዋና መረጃዎች -----------------
BOT_TOKEN = "8745539916:AAHk9a_mFuE8JRuSfYqVaU8KaUbIJPNeozs"
ADMIN_ID = 7889289204
TELEBIRR_NO = "0934642358"
GAME_URL = "https://your-bingo-game-website.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------- ዳታቤዝ -----------------
conn = sqlite3.connect("bingo_bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        phone_number TEXT,
        balance REAL DEFAULT 0,
        turnover REAL DEFAULT 0,
        is_registered INTEGER DEFAULT 0
    )
""")
conn.commit()

# ----------------- ኪቦርዶች -----------------
contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 ስልክ ቁጥር አጋራ (Share Contact)", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎮 ቢንጎ ተጫወት (Chrome)"), KeyboardButton(text="💰 ሂሳብ (Balance)")],
        [KeyboardButton(text="📥 ብር አስገባ (Deposit)"), KeyboardButton(text="📤 ብር አውጣ (Withdraw)")],
        [KeyboardButton(text="ℹ️ ህጎችና መመሪያዎች")]
    ],
    resize_keyboard=True
)

# ----------------- Start & Registration -----------------
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT is_registered FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user or user[0] == 0:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        await message.answer(
            "🎲 **እንኳን ወደ MyFishe Bingo በደህና መጡ!**\n\n"
            "🎁 **የ10 ብር የመመዝገቢያ ቦነስ** ለማግኘት ከታች ያለውን "
            "**«ስልክ ቁጥር አጋራ»** የሚለውን ቁልፍ ይጫኑ!",
            parse_mode="Markdown",
            reply_markup=contact_kb
        )
    else:
        await message.answer("እንኳን ደህና ተመለሱ! ከታች ካሉት አማራጮች ይምረጡ፡", reply_markup=main_kb)

@dp.message(F.contact)
async def process_contact(message: types.Message):
    user_id = message.from_user.id
    contact = message.contact

    if contact.user_id != user_id:
        await message.answer("እባክዎ የራስዎን እውነተኛ ስልክ ቁጥር ያጋሩ!", reply_markup=contact_kb)
        return

    cursor.execute("SELECT is_registered FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] == 1:
        await message.answer("ቀድመው ተመዝግበዋል!", reply_markup=main_kb)
        return

    cursor.execute("""
        UPDATE users
        SET phone_number = ?, balance = balance + 10.0, is_registered = 1
        WHERE user_id = ?
    """, (contact.phone_number, user_id))
    conn.commit()

    await message.answer(
        "✅ **ምዝገባዎ ተሳክቷል!**\n\n"
        "🎉 **10 ብር ቦነስ** ሂሳብዎ ላይ ገብቷል።\n"
        "ለመጫወት ከታች ያለውን ሜኑ ይጠቀሙ።",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

# ----------------- በ Chrome መጫወቻ -----------------
@dp.message(F.text == "🎮 ቢንጎ ተጫወት (Chrome)")
async def play_game(message: types.Message):
    play_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 በ Chrome ክፈትና ተጫወት", url=f"{GAME_URL}?user={message.from_user.id}")]
        ]
    )
    await message.answer(
        "🎲 **ወደ ቢንጎ ጨዋታ መግቢያ**\n\n"
        "ከታች ያለውን ሊንክ በመጫን በቀጥታ በ Chrome ውስጥ ያለምንም ዳታ መጫወት ይችላሉ፡",
        reply_markup=play_kb
    )

# ----------------- ሂሳብ (Balance) -----------------
@dp.message(F.text == "💰 ሂሳብ (Balance)")
async def check_balance(message: types.Message):
    cursor.execute("SELECT balance, turnover FROM users WHERE user_id = ?", (message.from_user.id,))
    row = cursor.fetchone()
    if row:
        bal, to = row
        await message.answer(
            f"👤 **የአካውንትዎ መረጃ:**\n\n"
            f"💵 **ቀሪ ሂሳብ:** {bal:.2f} ብር\n"
            f"🎯 **የተጫወቱበት ድምር (Turnover):** {to:.2f} / 1,500.00 ብር",
            parse_mode="Markdown"
        )

# ----------------- ብር ማስገባት (Deposit) -----------------
@dp.message(F.text == "📥 ብር አስገባ (Deposit)")
async def deposit_info(message: types.Message):
    msg = (
        f"💳 **ብር ማስገቢያ (Deposit)**\n\n"
        f"📌 ዝቅተኛ ማስገባት የሚቻለው፡ **50 ብር**\n\n"
        f"📱 **Telebirr:** `{TELEBIRR_NO}`\n\n"
        f"ብር ካስገቡ በኋላ የከፈሉበትን **Screenshot (ደረሰኝ)** እዚህ ቻት ላይ በቀጥታ ይላኩ።"
    )
    await message.answer(msg, parse_mode="Markdown")

# ደረሰኝ ማስተላለፍ
@dp.message(F.photo)
async def handle_receipt(message: types.Message):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id

    admin_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ 50 ብር ሙላ", callback_data=f"add_50_{user_id}"),
                InlineKeyboardButton(text="✅ 100 ብር ሙላ", callback_data=f"add_100_{user_id}")
            ],
            [
                InlineKeyboardButton(text="❌ ውድቅ አድርግ", callback_data=f"reject_{user_id}")
            ]
        ]
    )

    caption = (
        f"📥 **አዲስ የክፍያ ደረሰኝ!**\n\n"
        f"👤 User ID: `{user_id}`\n"
        f"ስም: {message.from_user.full_name}\n"
        f"ደረሰኙን አረጋግጠው ሂሳብ ይሙሉለት።"
    )

    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=caption, reply_markup=admin_kb)
    await message.answer("✅ ደረሰኝዎ ደርሶናል! አድሚን አረጋግጦ እስኪጨምር ጥቂት ደቂቃ ይጠብቁ።")

# አድሚን ሲያረጋግጥ
@dp.callback_query(F.data.startswith("add_"))
async def approve_deposit(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    _, amount, target_user_id = callback.data.split("_")
    amount = float(amount)
    target_user_id = int(target_user_id)

    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user_id))
    conn.commit()

    await bot.send_message(target_user_id, f"🎉 ክፍያዎ ተረጋግጧል! **{amount:.2f} ብር** ሂሳብዎ ላይ ተጨምሯል።")
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n✅ **ተረጋግጧል ({amount} ብር ተሞልቷል)**")
    await callback.answer("ሂሳብ ተሞልቷል!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_deposit(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    target_user_id = int(callback.data.split("_")[1])
    await bot.send_message(target_user_id, "❌ የላኩት ደረሰኝ ውድቅ ተደርጓል። እባክዎ ትክክለኛ ደረሰኝ ይላኩ።")
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n❌ **ውድቅ ተደርጓል**")
    await callback.answer("ውድቅ ተደርጓል!")

# ----------------- ብር ማውጣት (Withdraw) -----------------
@dp.message(F.text == "📤 ብር አውጣ (Withdraw)")
async def withdraw_info(message: types.Message):
    cursor.execute("SELECT balance, turnover FROM users WHERE user_id = ?", (message.from_user.id,))
    row = cursor.fetchone()
    if not row:
        return

    bal, to = row
    if to < 1500:
        await message.answer(
            f"⚠️ **ብር ማውጣት አይችሉም!**\n\n"
            f"የቦነስ ገንዘብ ለማውጣት ቢያንስ **1,500 ብር** መጫወት አለብዎት።\n"
            f"• የተጫወቱት፡ **{to:.2f} ብር**\n"
            f"• የሚቀርዎት፡ **{1500 - to:.2f} ብር**",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"✅ ማውጣት ይችላሉ! የአሁኑ ሂሳብዎ፡ **{bal:.2f} ብር** ነው።\n"
            f"የሚያወጡትን መጠን እና የቴሌብር ቁጥርዎን ይላኩ።"
        )

# ----------------- መመሪያዎች -----------------
@dp.message(F.text == "ℹ️ ህጎችና መመሪያዎች")
async def show_rules(message: types.Message):
    await message.answer(
        "📜 **የጨዋታ ህጎችና መመሪያዎች:**\n\n"
        "1. ስልክ ሲያጋሩ የ 10 ብር ቦነስ ይሰጣል።\n"
        "2. ዝቅተኛ የማስገቢያ መጠን 50 ብር ነው።\n"
        "3. ገንዘብ ማውጣት የሚቻለው ጠቅላላ የተጫወቱበት ድምር 1,500 ብር ሲደርስ ብቻ ነው።",
        parse_mode="Markdown"
    )

# ----------------- ማስጀመሪያ -----------------
async def main():
    print("ቦቱ እየሰራ ነው...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
