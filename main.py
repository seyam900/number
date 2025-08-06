from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import phonenumbers
from phonenumbers import geocoder, carrier
import os
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@SL_TooL_HuB"

async def is_subscribed(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    res = requests.get(url)
    data = res.json()
    status = data.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 Just send a phone number with +countrycode (e.g. +88017xxxxxxx)")

async def phone_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_subscribed(user_id):
        await update.message.reply_text(
            f"🔒 Please join our channel first to use this bot:\n👉 {CHANNEL_USERNAME}"
        )
        return

    number = update.message.text.strip()

    try:
        parsed_number = phonenumbers.parse(number, None)

        if not phonenumbers.is_valid_number(parsed_number):
            await update.message.reply_text("❌ Invalid phone number format.")
            return

        country = geocoder.country_name_for_number(parsed_number, "en")
        network = carrier.name_for_number(parsed_number, "en")
        line_type = phonenumbers.number_type(parsed_number)

        type_str = {
            0: "Fixed Line",
            1: "Mobile",
            2: "Fixed Line or Mobile",
            3: "Toll Free",
            4: "Premium Rate",
            5: "Shared Cost",
            6: "VoIP",
            7: "Personal Number",
            8: "Pager",
            9: "UAN",
            10: "Voice Mail",
            27: "Unknown"
        }.get(line_type, "Unknown")

        number_clean = number.replace("+", "")

        reply = f"✅ *Phone Number Details:*\n"
        reply += f"• Number: `{phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}`\n"
        reply += f"• Country: {country}\n"
        reply += f"• Carrier: {network or 'Unknown'}\n"
        reply += f"• Line Type: {type_str}\n\n"
        reply += f"📱 *Check Social:*\n"
        reply += f"• WhatsApp: [Click to open](https://wa.me/{number_clean})\n"
        reply += f"• Telegram: [Click to open](https://t.me/{number_clean})"

        await update.message.reply_text(reply, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        await update.message.reply_text("⚠️ Could not process the number. Please check format.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, phone_lookup))
app.run_polling()
