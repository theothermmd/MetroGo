from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from core import find_best_route
# تابع find_fast که داده‌ها را برمی‌گرداند


# هندلر شروع
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! به متروگو خوش آمدید.\n"
                              "برای پیدا کردن مسیر از دستور /route استفاده کنید.")

# هندلر جستجوی مسیر
def route(update: Update, context: CallbackContext):
    # بررسی تعداد ورودی‌ها
    if len(context.args) != 2:
        update.message.reply_text("لطفاً مبدا و مقصد را به صورت زیر وارد کنید:\n"
                                  "/route [مبدا] [مقصد]")
        return

    start_station = context.args[0]
    destination_station = context.args[1]

    # فراخوانی تابع find_fast
    data = find_best_route(start_station, destination_station)

    # ساخت پیام خروجی
    route_info = "\n".join([f"{i+1}. {step['station']} - {step['arrival_time']}" for i, step in enumerate(data["route"])])
    travel_guide = "\n".join([f"- {step}" for step in data["travel_guide"]])

    message = (
        f"🚉 **مسیر پیشنهادی:**\n{route_info}\n\n"
        f"⏳ **مدت زمان سفر:** {data['travel_duration']}\n"
        f"💰 **هزینه سفر:** {data['travel_cost']}\n"
        f"🕒 **زمان حرکت قطار بعدی:** {data['next_train']}\n"
        f"🛬 **زمان رسیدن به مقصد:** {data['arrival_time']}\n\n"
        f"📜 **راهنمای سفر:**\n{travel_guide}"
    )

    update.message.reply_text(message)

# راه‌اندازی بات
def main():
    # توکن بات خود را جایگزین کنید
    TOKEN = "7617209555:AAH4tN-rukNYBLbHo9-MgmtqwSNu0zoxYio"
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # ثبت هندلرها
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("route", route))

    # اجرای بات
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
