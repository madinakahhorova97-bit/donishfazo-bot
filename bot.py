import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Салом! Хуш омадӣ ба Донишфазо! 🎉\n\nМан ёрдамчии ту дар математика ҳастам.")
    
    keyboard = [
        [InlineKeyboardButton("📚 Дарсҳо", callback_data="lessons"),
         InlineKeyboardButton("🎥 Видеодарсҳо", callback_data="videos")],
        [InlineKeyboardButton("📝 Тестҳо", callback_data="tests"),
         InlineKeyboardButton("🧮 Формулаҳо", callback_data="formulas")],
        [InlineKeyboardButton("📁 Маводҳои иловагӣ", callback_data="extra"),
         InlineKeyboardButton("🆘 Ёрдам", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👇 Меню - Якеро интихоб кун:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "lessons":
        keyboard = [[InlineKeyboardButton(f"Синфи {i}", callback_data=f"grade_{i}") for i in range(5, 8)],
                    [InlineKeyboardButton(f"Синфи {i}", callback_data=f"grade_{i}") for i in range(8, 12)]]
        await query.edit_message_text("📚 Дарсҳо - Синфро интихоб кун:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "videos":
        keyboard = [[InlineKeyboardButton(f"Синфи {i}", callback_data=f"video_{i}") for i in range(5, 8)],
                    [InlineKeyboardButton(f"Синфи {i}", callback_data=f"video_{i}") for i in range(8, 12)]]
        await query.edit_message_text("🎥 Видеодарсҳо - Синфро интихоб кун:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "tests":
        await query.edit_message_text("📝 Тестҳо ба наздикӣ илова мешаванд! 💪")
    elif data == "formulas":
        await query.edit_message_text("🧮 Формулаҳо:\n\n📐 Масоҳати росткунҷа: S = a * b\n📐 Масоҳати секунҷа: S = (a * h) / 2\n📐 Теоремаи Пифагор: a² + b² = c²")
    elif data == "extra":
        keyboard = [
            [InlineKeyboardButton("📖 Китобҳо", callback_data="books")],
            [InlineKeyboardButton("📊 Ҷадвалҳо", callback_data="tables")],
            [InlineKeyboardButton("✍️ Машқҳои иловагӣ", callback_data="exercises")],
        ]
        await query.edit_message_text("📁 Маводҳои иловагӣ - Якеро интихоб кун:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "books":
        await query.edit_message_text("📖 Китобҳо ба наздикӣ илова мешаванд!")
    elif data == "tables":
        await query.edit_message_text("📊 Ҷадвалҳо:\n\n🔢 Ҷадвали зарб\n1x1=1, 2x2=4, 3x3=9, 4x4=16, 5x5=25\n\nБа наздикӣ ҷадвали пурра!")
    elif data == "exercises":
        await query.edit_message_text("✍️ Машқҳои иловагӣ ба наздикӣ илова мешаванд!")
    elif data == "help":
        await query.edit_message_text("🆘 Ёрдам:\n\n📚 Дарсҳо - мавзӯъҳоро хондан\n🎥 Видеодарсҳо - видео тамошо кардан\n📝 Тестҳо - худро санҷидан\n🧮 Формулаҳо - формулаҳои муҳим\n📁 Маводҳои иловагӣ - китоб ва машқҳо")
    elif data.startswith("grade_"):
        grade = data.split("_")[1]
        await query.edit_message_text(f"📚 Синфи {grade} - Дарсҳо ба наздикӣ илова мешаванд!")
    elif data.startswith("video_"):
        grade = data.split("_")[1]
        await query.edit_message_text(f"🎥 Синфи {grade} - Видеодарсҳо ба наздикӣ илова мешаванд!")

def main():
    token = os.environ.get("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), BaseHTTPRequestHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
