import os
import json
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

USERS_FILE = "users.json"
users = set()
users_names = {}

def load_users():
    global users, users_names
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for u in data:
                    users.add(u["id"])
                    users_names[u["id"]] = u["name"]
        except:
            pass

def save_users():
    data = [{"id": uid, "name": users_names.get(uid, "")} for uid in users]
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main_menu():
    return [
        [InlineKeyboardButton("📚 Дарсҳо", callback_data="lessons"),
         InlineKeyboardButton("🎥 Видеодарсҳо", callback_data="videos")],
        [InlineKeyboardButton("📝 Тестҳо", callback_data="tests"),
         InlineKeyboardButton("🧮 Формулаҳо", callback_data="formulas")],
        [InlineKeyboardButton("📁 Маводҳои иловагӣ", callback_data="extra"),
         InlineKeyboardButton("🆘 Ёрдам", callback_data="help")],
        [InlineKeyboardButton("❓ Саволҳои иловагӣ (AI)", callback_data="ai_info")],
    ]

def ask_gemini(question):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Калиди AI ҳанӯз гузошта нашудааст. Ба муаллима бигӯ!"
    try:
        data = json.dumps({
            "contents": [{"parts": [{"text": f"Ту муаллими меҳрубон ва донои тоҷик ҳастӣ. Ба хонандагони синфи 5 то 11 ба забони тоҷикӣ содда ва фаҳмо ҷавоб деҳ. Ҳамеша мисол овар. Савол: {question}"}]}]
        }).encode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode("utf-8"))
            return res["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"GEMINI ХАТО: {e}")
        return f"Хатои AI: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    is_new = user.id not in users
    users.add(user.id)
    users_names[user.id] = user.first_name
    if is_new:
        save_users()
    await update.message.reply_text("Салом! Хуш омадӣ ба Донишфазо! 🎉\n\nМан ёрдамчии ту дар математика ҳастам.")
    await update.message.reply_text("👇 Меню - Якеро интихоб кун:", reply_markup=InlineKeyboardMarkup(main_menu()))

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    names = "\n".join([f"👤 {name}" for name in users_names.values()])
    if not names:
        names = "Ҳанӯз касе нест"
    await update.message.reply_text(f"📊 Омори Донишфазо:\n\n👥 Ҳамагӣ: {len(users)} нафар /start додаанд!\n\n{names}")

async def hisob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👥 Ҳозир дар боти ДонишФазо:\n\n🎉 {len(users)} нафар /start додаанд!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await update.message.reply_text("Фикр мекунам... 🤔")
    answer = ask_gemini(question)
    await update.message.reply_text(answer)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "back_menu":
        await query.edit_message_text("👇 Меню - Якеро интихоб кун:", reply_markup=InlineKeyboardMarkup(main_menu()))
    elif data == "ai_info":
        keyboard = [[InlineKeyboardButton("⬅️ Ба меню", callback_data="back_menu")]]
        await query.edit_message_text("❓ Саволҳои иловагӣ (AI)\n\nҲар саволеро, ки дораӣ - дар ин ҷо навишта равон кун! ✍️\n\nМасалан:\n• 2 + 2 чанд мешавад?\n• Теоремаи Пифагор чист?\n• Масоҳати секунҷаро чӣ хел ёбем?\n\nМан ҳозир ҷавоб медиҳам! 🤖", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "lessons":
        keyboard = [[InlineKeyboardButton(f"Синфи {i}", callback_data=f"grade_{i}") for i in range(5, 8)],
                    [InlineKeyboardButton(f"Синфи {i}", callback_data=f"grade_{i}") for i in range(8, 12)],
                    [InlineKeyboardButton("⬅️ Ба меню", callback_data="back_menu")]]
        await query.edit_message_text("📚 Дарсҳо - Синфро интихоб кун:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "videos":
        keyboard = [[InlineKeyboardButton(f"Синфи {i}", callback_data=f"video_{i}") for i in range(5, 8)],
                    [InlineKeyboardButton(f"Синфи {i}", callback_data=f"video_{i}") for i in range(8, 12)],
                    [InlineKeyboardButton("⬅️ Ба меню", callback_data="back_menu")]]
        await query.edit_message_text("🎥 Видеодарсҳо - Синфро интихоб кун:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "tests":
        keyboard = [[InlineKeyboardButton("⬅️ Ба меню", callback_data="back_menu")]]
        await query.edit_message_text("📝 Тестҳо ба наздикӣ илова мешаванд! 💪", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "formulas":
        keyboard = [[InlineKeyboardButton("⬅️ Ба меню", callback_data="back_menu")]]
        await query.edit_message_text("🧮 Формулаҳо:\n\n📐 Масоҳати росткунҷа: S = a * b\n📐 Масоҳати секунҷа: S = (a * h) / 2\n📐 Теоремаи Пифагор: a² + b² = c²", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "extra":
        keyboard = [
            [InlineKeyboardButton("📖 Китобҳо", callback_data="books")],
            [InlineKeyboardButton("📊 Ҷадвалҳо", callback_data="tables")],
            [InlineKeyboardButton("✍️ Машқҳои иловагӣ", callback_data="exercises")],
            [InlineKeyboardButton("⬅️ Ба меню", callback_data="back_menu")],
        ]
        await query.edit_message_text("📁 Маводҳои иловагӣ - Якеро интихоб кун:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "books":
        await query.edit_message_text("📖 Китобҳо ба наздикӣ илова мешаванд!")
    elif data == "tables":
        await query.edit_message_text("📊 Ҷадвалҳо:\n\n🔢 Ҷадвали зарб\n1x1=1, 2x2=4, 3x3=9, 4x4=16, 5x5=25")
    elif data == "exercises":
        await query.edit_message_text("✍️ Машқҳои иловагӣ ба наздикӣ илова мешаванд!")
    elif data == "help":
        keyboard = [
            [InlineKeyboardButton("✍️ Ба муаллима навиштан", url="https://t.me/mad1na_qahhorova")],
            [InlineKeyboardButton("⬅️ Ба меню", callback_data="back_menu")],
        ]
        await query.edit_message_text("🆘 Ёрдам:\n\n📚 Дарсҳо - мавзӯъҳоро хондан\n🎥 Видеодарсҳо - видео тамошо кардан\n📝 Тестҳо - худро санҷидан\n🧮 Формулаҳо - формулаҳои муҳим\n📁 Маводҳои иловагӣ - китоб ва машқҳо\n❓ Саволҳои иловагӣ (AI) - савол диҳӣ, ҷавоб мегирӣ!\n\nАгар саволатон монд, ба муаллима нависед! 👇", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("grade_"):
        grade = data.split("_")[1]
        await query.edit_message_text(f"📚 Синфи {grade} - Дарсҳо ба наздикӣ илова мешаванд!")
    elif data.startswith("video_"):
        grade = data.split("_")[1]
        await query.edit_message_text(f"🎥 Синфи {grade} - Видеодарсҳо ба наздикӣ илова мешаванд!")

def main():
    load_users()
    token = os.environ.get("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("hisob", hisob))
    app.add_handler(CommandHandler("count", hisob))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), BaseHTTPRequestHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
