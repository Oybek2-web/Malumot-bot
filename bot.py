import sqlite3
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Holatlar
NAME, SURNAME, AGE = range(3)

# Database yaratish
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    name TEXT,
    surname TEXT,
    age INTEGER
)
""")
conn.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum!\nIsmingizni kiriting:")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Familiyangizni kiriting:")
    return SURNAME


async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["surname"] = update.message.text
    await update.message.reply_text("Yoshingizni kiriting:")
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text

    if not age.isdigit():
        await update.message.reply_text("Yosh faqat son bo'lishi kerak!")
        return AGE

    context.user_data["age"] = int(age)

    # DB ga saqlash
    cursor.execute(
        """
        INSERT INTO users (telegram_id, name, surname, age)
        VALUES (?, ?, ?, ?)
        """,
        (
            update.effective_user.id,
            context.user_data["name"],
            context.user_data["surname"],
            context.user_data["age"],
        ),
    )
    conn.commit()

    # JSON ko'rinish
    data = {
        "telegram_id": update.effective_user.id,
        "name": context.user_data["name"],
        "surname": context.user_data["surname"],
        "age": context.user_data["age"],
    }

    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    await update.message.reply_text(
        f"Ma'lumotlar saqlandi ✅\n\n<pre>{json_data}</pre>",
        parse_mode="HTML",
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END


def main():
    TOKEN = "8773874748:AAF-1Uda-gUOkyYBL6yAnyFP5a83vwqyHjE"

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()