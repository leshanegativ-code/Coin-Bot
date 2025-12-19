import os
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot token from environment or default
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7251764087:AAGq2c9KYLyqDZ6ci_cXgjfFEvSJxfoKhmc')
EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest"

CURRENCIES = {
    "USD": "🇺🇸 Dollar",
    "EUR": "🇪🇺 Euro",
    "GBP": "🇬🇧 Pound",
    "JPY": "🇯🇵 Yen",
    "AUD": "🇦🇺 AUD",
    "CAD": "🇨🇦 CAD",
    "CHF": "🇨🇭 CHF",
    "CNY": "🇨🇳 Yuan",
    "SEK": "🇸🇪 Krona",
    "NZD": "🇳🇿 NZD",
}

async def fetch_rates(base_currency: str) -> dict:
    """Fetch currency exchange rates"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{EXCHANGE_API}/{base_currency}") as resp:
                if resp.status == 200:
                    return await resp.json()
        return None
    except Exception:
        return None

def create_currency_keyboard() -> InlineKeyboardMarkup:
    """Create currency selection keyboard"""
    buttons = []
    currency_list = list(CURRENCIES.items())
    
    for i in range(0, len(currency_list), 2):
        row = []
        for j in range(2):
            if i + j < len(currency_list):
                code, name = currency_list[i + j]
                row.append(InlineKeyboardButton(text=f"{code}", callback_data=f"select:{code}"))
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def create_main_menu() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    buttons = [
        [InlineKeyboardButton("📊 Rates", callback_data="rates"),
         InlineKeyboardButton("💱 Convert", callback_data="convert")],
        [InlineKeyboardButton("❤️ Favorites", callback_data="favorites"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    await update.message.reply_text(
        "Welcome to Currency Bot!\nChoose what you want to do:",
        reply_markup=create_main_menu()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "main_menu":
        await query.edit_message_text(
            text="Choose what you want to do:",
            reply_markup=create_main_menu()
        )
    elif query.data == "rates":
        data = await fetch_rates("USD")
        if data:
            rates = data.get('rates', {})
            text = "💱 Current Rates (base USD):\n\n"
            for code in list(CURRENCIES.keys())[:5]:
                if code in rates:
                    text += f"{code}: {rates[code]:.2f}\n"
            await query.edit_message_text(text=text, reply_markup=create_main_menu())
        else:
            await query.edit_message_text(text="Error fetching rates", reply_markup=create_main_menu())
    elif query.data == "convert":
        await query.edit_message_text(
            text="Select base currency:",
            reply_markup=create_currency_keyboard()
        )
    elif query.data.startswith("select:"):
        currency = query.data.split(":")[1]
        data = await fetch_rates(currency)
        if data:
            rates = data.get('rates', {})
            text = f"1 {currency} = \n\n"
            for code in list(CURRENCIES.keys())[:5]:
                if code in rates:
                    text += f"{code}: {rates[code]:.2f}\n"
            await query.edit_message_text(text=text, reply_markup=create_main_menu())
    elif query.data == "about":
        await query.edit_message_text(
            text="Currency Bot v1.0\nPowered by exchangerate-api.com\n\nFast & Reliable currency conversion",
            reply_markup=create_main_menu()
        )

async def main() -> None:
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
