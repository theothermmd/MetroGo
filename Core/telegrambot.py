from core import find_best_route
from telegram import Update
from datetime import datetime
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
# وضعیت‌ها
USER_ID = 5912913717 

from telegram import InlineQueryResultPhoto, Update
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import InlineQueryHandler, Application, CommandHandler, CallbackContext, MessageHandler, filters
from uuid import uuid4

START, DESTINATION, TIME_INPUT = range(3)

async def send_message_to_user(context: CallbackContext , str : str):
    try:
        await context.bot.send_message(USER_ID, str)
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")

# هندلر شروع
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("سلام ✋🏻✋🏿 به متروگو خوش اومدی. \n\n"
                                    "💌 این *نسخه آلفا* متروگو هستش. پر از باگ. پر از شگفتی.\n\n"
                                    "🍬 برای پیدا کردن مسیر از دستور /route استفاده کنید.\n\n"
                                     "🌀 خط 5 مترو تهران و مترو های بقیه شهر ها رو نداریم بوس." , parse_mode='Markdown')
    if update.message.from_user.username :
        await send_message_to_user(context , f"کاربر {update.message.from_user.username} به بات متروگو وارد شد.")
    else :
        await send_message_to_user(context , f"کاربر {update.message.from_user.first_name} به بات متروگو وارد شد.")
    return ConversationHandler.END

async def get_user_time(update: Update, context: CallbackContext):
    # گرفتن زمان وارد شده توسط کاربر
    user_time = update.message.text

    try:
        # تبدیل زمان وارد شده به فرمت datetime
        time_user = datetime.strptime(user_time, "%H:%M")
        if (datetime.strptime("22:00", "%H:%M") <= time_user <= datetime.strptime("23:59", "%H:%M")) or (datetime.strptime("00:00", "%H:%M") <= time_user <= datetime.strptime("05:30", "%H:%M")):
            await update.message.reply_text("ساعت واردشده در بازه زمانی غیرمجاز است (بین 22:00 و 05:30). لطفاً زمان دیگری وارد کنید.")
            return TIME_INPUT
        context.user_data['time_user'] = user_time
        await update.message.reply_text(f"زمان شما با موفقیت ثبت شد: {time_user.strftime('%H:%M')}. حالا لطفاً مبدا را وارد کنید.")
        return START
    except ValueError:
        await update.message.reply_text("فرمت زمان صحیح نیست. لطفاً دوباره تلاش کنید (فرمت: ساعت:دقیقه).")
        return TIME_INPUT
# هندلر جستجوی مسیر، در صورت عدم ورود مبدا و مقصد
async def route(update: Update, context: CallbackContext):
    now = datetime.strptime(f"{datetime.now().hour}:{ datetime.now().minute}", "%H:%M")
    if update.message.from_user.username :
        await send_message_to_user(context , f"کاربر {update.message.from_user.username} درحال مسیریابی به شکل داخل ربات است")
    else :
        await send_message_to_user(context , f"کاربر {update.message.from_user.first_name} درحال مسیریابی به شکل داخل ربات است")

    # زمان‌های مورد نظر برای بررسی
    night_start = "22:00"
    early_morning_start = "03:00"
    early_morning_end = "05:30"
    

    if datetime.strptime(night_start, "%H:%M") <= now <= datetime.strptime(early_morning_start, "%H:%M"):
            await update.message.reply_text(f"والا الان که کله شبه، قطار نیستش که آخه \n\n" 
                                            "ولی میتونی با فرمت (دقیقه : ساعت) زمان مورد نظرت رو بهم بگی" , parse_mode='Markdown')
            return TIME_INPUT

    elif datetime.strptime(early_morning_start, "%H:%M") <= now <= datetime.strptime(early_morning_end, "%H:%M"):
            await update.message.reply_text(f"والا الان که کله سحره، قطار نیستش که آخه \n\n" 
                                            "ولی میتونی با فرمت (دقیقه : ساعت) زمان مورد نظرت رو بهم بگی" , parse_mode='Markdown')
            return TIME_INPUT

   
     
    await update.message.reply_text("لطفاً مبدا را وارد کنید.")
    return START


# مرحله سوم دریافت زمان از کاربر

# مرحله اول دریافت مبدا
async def get_start_station(update: Update, context: CallbackContext):
    context.user_data['start_station'] = update.message.text
    await update.message.reply_text("مبدا شما ثبت شد. حالا لطفاً مقصد را وارد کنید.")
    return DESTINATION

# مرحله دوم دریافت مقصد
async def get_destination_station(update: Update, context: CallbackContext):
    context.user_data['destination_station'] = update.message.text

    start_station = context.user_data['start_station']
    destination_station = context.user_data['destination_station']

    # فراخوانی تابع find_best_route
    if 'time_user' in context.user_data:
        try :
            data = find_best_route(start_station, destination_station , context.user_data['time_user'])
        except :
                await update.message.reply_text("متروگو رو از دست دادیم!\n\n یا مبدا یا مقصد رو اشتباه وارد کردی.\n\nبا زدن روی /route دوباره مسیریابی کنید.")
                return ConversationHandler.END 
    else :
        try :
            data = find_best_route(start_station, destination_station , f"{datetime.now().hour}:{ datetime.now().minute}")
        except :
                await update.message.reply_text("متروگو رو از دست دادیم!\n\n یا مبدا یا مقصد رو اشتباه وارد کردی.\n\nبا زدن روی /route دوباره مسیریابی کنید.")
                return ConversationHandler.END 


    msg = []
    for i in data['route']:
        try :
            if i['message'] == "":
                msg.append(f"ایستگاه {i['station_name']} | زمان : {i['time']} \n")
            else:
                msg.append(f"ایستگاه : {i['station_name']} | زمان : {i['time']} \n\n ⚠️ توجه : {i['message']} \n")
        except:
            await update.message.reply_text(data)
    route_message = "\n".join(msg)
    guid = "\n".join(data['travel_guide'])
    message = (
            f"🚉 *مسیر پیشنهادی:* \n\n{route_message}\n\n"
            f"⏳ *مدت زمان سفر:* {data['travel_duration']}\n"
            f"💰 *هزینه سفر:* {data['travel_cost']} تومان\n"
            f"🕒 *زمان رسیدن قطار به ایستگاه مبدا :* {data['next_train']} دقیقه دیگر\n"
            f"🛬 *زمان رسیدن به مقصد:* {data['arrival time']}\n\n"
            f"📜 *راهنمای سفر:*\n\n {guid} \n\n" 
            f"🤍 *متروگو. راه بلد شهر، همسفر هوشمند شما :)*"
            )

    await update.message.reply_text(message, parse_mode='Markdown')
    return ConversationHandler.END

# راه‌اندازی بات


from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import InlineQueryHandler, Application, CommandHandler, CallbackContext, MessageHandler, filters
from uuid import uuid4
from core import find_best_route

async def inline_query(update: Update, context: CallbackContext):
    if update.inline_query.from_user.username :
        await send_message_to_user(context , f"کاربر {update.inline_query.from_user.username} درحال استفاده از این لاین مود است.")
    else :
        await send_message_to_user(context , f"کاربر {update.inline_query.from_user.username} درحال استفاده از این لاین مود است.")
    query = update.inline_query.query

    # جداسازی مبدا و مقصد
    try:
        start_station, destination_station = query.split(' ')
    except ValueError:
        # اگر فرمت اشتباه بود، پیامی مناسب برگردانید
        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="مسیری یافت نشد. برای مشاهده راهنما ضربه بزنید.",
                input_message_content=InputTextMessageContent(
                    "فرمت صحیح به صورت زیر میباشد :\n\n@MetrogoRobot مبدا مقصد\n\n✅ توجه : ایستگاه های مبدا و مقصد را با یک فاصله از هم جدا کنید.\n\n✅ توجه : ایستگاه هایی که شامل چند کلمه هستند (مانند تئاتر شهر) به صورت بدون فاصله (مانند تئاترشهر) بنویسید."
                ),
            )
        ])
        return

    # محاسبه مسیر
    try:
        # فراخوانی تابع find_best_route
        data = find_best_route(start_station, destination_station, f"{datetime.now().hour}:{datetime.now().minute}")
        
        # ایجاد پیام برای مسیر پیشنهادی
        msg = []
        for i in data['route']:
            try :
                if i['message'] == "":
                    msg.append(f"ایستگاه {i['station_name']} | زمان : {i['time']} \n")
                else:
                    msg.append(f"ایستگاه : {i['station_name']} | زمان : {i['time']} \n\n ⚠️ توجه : {i['message']} \n")
            except:
                msg.append("error")
        route_message = "\n".join(msg)
        guid = "\n".join(data['travel_guide'])
        message = (
                f"🚉 *مسیر پیشنهادی:* \n\n{route_message}\n\n"
                f"⏳ *مدت زمان سفر:* {data['travel_duration']}\n"
                f"💰 *هزینه سفر:* {data['travel_cost']} تومان\n"
                f"🕒 *زمان رسیدن قطار به ایستگاه مبدا :* {data['next_train']} دقیقه دیگر\n"
                f"🛬 *زمان رسیدن به مقصد:* {data['arrival time']}\n\n"
                f"📜 *راهنمای سفر:*\n\n {guid} \n\n" 
                f"🤍 *متروگو. راه بلد شهر، همسفر هوشمند شما :)*"
                )



        # برگرداندن نتیجه به کاربر
        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=f"مسیر از {start_station} به {destination_station}",
                input_message_content=InputTextMessageContent(message , parse_mode='Markdown' ),
            )
        ])
    except Exception as e:
        # در صورت خطا، پیام مناسبی نمایش دهید
        await update.inline_query.answer([
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="مسیری یافت نشد. برای مشاهده راهنما ضربه بزنید.",
                input_message_content=InputTextMessageContent(
                    "فرمت صحیح به صورت زیر میباشد :\n\n@MetrogoRobot مبدا مقصد\n\n✅ توجه : ایستگاه های مبدا و مقصد را با یک فاصله از هم جدا کنید.\n\n✅ توجه : ایستگاه هایی که شامل چند کلمه هستند (مانند تئاتر شهر) به صورت بدون فاصله (مانند تئاترشهر) بنویسید."
                ),
            )
        ])


def main():
    # توکن بات خود را جایگزین کنید
    TOKEN = "7617209555:AAH4tN-rukNYBLbHo9-MgmtqwSNu0zoxYio"

    # ساخت Application
    application = Application.builder().token(TOKEN).build()

    # هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('route', route)],
        states={
            START: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_start_station)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_destination_station)],
            TIME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_time)],
        },
        fallbacks=[],
    ))

    # هندلر Inline Mode
    

    # اجرای بات
    application.run_polling()

if __name__ == "__main__":
    main()