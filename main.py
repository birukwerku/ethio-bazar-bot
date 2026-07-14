import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- የባለቤት እና የቦት መረጃዎች ---
BOT_TOKEN = "8892099703:AAFMUqAHVfV13fnf9-SgQTr6IbZEDbOZpqE"
ADMIN_ID = 123456789  # ⚠️ እዚህ ላይ የራስህን የቴሌግራም ID ቁጥር ተካ! (በ @userinfobot ማግኘት ትችላለህ)

# --- የመጻሕፍት ማኅደር (DATABASE) ---
BOOKS_DATABASE = {
    "psych_bundle": {
        "name": "🧠 የ5 ምርጥ ስነ-ልቦና መጻሕፍት ጥቅል (PDF)",
        "price": "80 ETB",
        "link": "https://drive.google.com/drive/folders/psych_link"
    },
    "wealth_audio": {
        "name": "💰 የሀብት ማፍሪያ መጻሕፍት ትረካ (Audiobook)",
        "price": "100 ETB",
        "link": "https://drive.google.com/drive/folders/wealth_link"
    },
    "history_pack": {
        "name": "📜 የታሪክ እና የፍልስፍና መጻሕፍት ማኅደር",
        "price": "70 ETB",
        "link": "https://drive.google.com/drive/folders/history_link"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 የስነ-ልቦና መጻሕፍት (80 ETB)", callback_data="buy_psych_bundle")],
        [InlineKeyboardButton("💰 የድምፅ መጻሕፍት / Audiobooks (100 ETB)", callback_data="buy_wealth_audio")],
        [InlineKeyboardButton("📜 የታሪክና ፍልስፍና ጥቅል (70 ETB)", callback_data="buy_history_pack")],
        [InlineKeyboardButton("📞 ያግኙን / Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💙 **እንኳን ወደ Ethio Bazar ዲጂታል መደብር በሰላም መጡ!** 💙\n\n"
        "ለዲዛይነሮች እና ለንባብ አፍቃሪያን የተዘጋጁ ምርጥ የዲጂታል ጥቅሎችን ከታች ያሉትን በተኖች በመጫን መግዛት ይችላሉ፦",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        book_key = query.data.replace("buy_", "")
        book = BOOKS_DATABASE[book_key]
        context.user_data["pending_item"] = book_key
        
        payment_msg = (
            f"🛒 **የመረጡት ምርት:** {book['name']}\n"
            f"💵 **ዋጋ:** {book['price']}\n\n"
            "📌 **የክፍያ አማራጮች (Payment Methods):**\n"
            "▪️ Telebirr / CBE Birr: `0912345678` (Biruk Werku)\n"
            "▪️ የንግድ ባንክ (CBE): `1000123456789`\n\n"
            "⚠️ **ቀጣይ እርምጃ:** ክፍያውን እንደፈጸሙ፣ እባክዎ **የክፍያ ደረሰኝ (Screenshot)** አሁን ወደዚህ ቦት ይላኩ።"
        )
        await query.edit_message_text(text=payment_msg, parse_mode="Markdown")
        
    elif query.data == "help":
        await query.edit_message_text("📞 ለእርዳታ ወይም ለጥያቄዎች በ @EthioBazarSupport ያግኙን።")
        
    elif query.data.startswith("approve_"):
        parts = query.data.split("_")
        user_id = int(parts[1])
        item_key = parts[2]
        book = BOOKS_DATABASE[item_key]
        
        success_text = (
            "✅ **ክፍያዎ በተሳካ ሁኔታ ተረጋግጧል!**\n\n"
            f"🎁 **የእርስዎ ምርት:** {book['name']}\n"
            f"🔗 **ማውረጃ ሊንክ:** {book['link']}\n\n"
            "ሊንኩን ተጭነው መጻሕፍቱን ማውረድ ይችላሉ። መልካም ንባብ!"
        )
        await context.bot.send_message(chat_id=user_id, text=success_text, parse_mode="Markdown")
        await query.edit_message_text(text=f"✅ ሽያጭ ጸድቋል! ለተጠቃሚው ({user_id}) ሊንኩ ተልኳል።")
        
    elif query.data.startswith("decline_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="❌ ይቅርታ፣ የላኩት የክፍያ ደረሰኝ ትክክል አይደለም። እባክዎ ድጋሚ ትክክለኛውን ይላኩ።")
        await query.edit_message_text(text="❌ ደረሰኙ ውድቅ ተደርጓል።")

async def receipt_receiver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "pending_item" not in context.user_data:
        await update.message.reply_text("❌ እባክዎ መጀመሪያ መግዛት የሚፈልጉትን መጽሐፍ ከሜኑው ላይ ይምረጡ።")
        return
        
    item_key = context.user_data["pending_item"]
    book = BOOKS_DATABASE[item_key]
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    await update.message.reply_text("⏳ ደረሰኝዎ ደርሶናል! አድሚኑ ወዲያውኑ አረጋግጦ መጽሐፉን ይልክልዎታል። እባክዎ ጥቂት ደቂቃዎችን ይጠብቁ።")
    
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ አጽድቅ (Approve)", callback_data=f"approve_{user.id}_{item_key}"),
            InlineKeyboardButton("❌ ውድቅ አድርግ (Decline)", callback_data=f"decline_{user.id}")
        ]
    ]
    admin_markup = InlineKeyboardMarkup(admin_keyboard)
    admin_alert = (
        "🔔 **አዲስ የገዢ ደረሰኝ መጥቷል!**\n\n"
        f"👤 **ገዢ:** {user.first_name} (@{user.username})\n"
        f"📦 **የፈለገው ምርት:** {book['name']}\n"
        f"💰 **ዋጋ:** {book['price']}"
    )
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_alert, reply_markup=admin_markup)
    del context.user_data["pending_item"]

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, receipt_receiver))
    
    print("Ethio Bazar Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
