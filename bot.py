import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from predictor import generate_prediction_plot

# Տեղադրեք ձեր Telegram Bot Token-ը այստեղ
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Բարև 👋\n\n"
        "Ուղարկիր /predict հրամանը, որպեսզի բազայից վերցնեմ տվյալները, "
        "հաշվեմ ապագա էքստրեմումները և ուղարկեմ գրաֆիկը։"
    )

@dp.message(Command("predict"))
async def cmd_predict(message: types.Message):
    await message.answer("🔄 Տվյալները մշակվում են, կատարվում է կանխատեսում...")
    
    try:
        # Գեներացնում ենք գրաֆիկը և ստանում էքստրեմումները
        extremas, img_path = generate_prediction_plot(db_name="data.db", output_img="prediction.png")
        
        # Պատրաստում ենք տեքստային հաղորդագրությունը
        text = "<b>📊 Կանխատեսման Արդյունքներ</b>\n\n"
        text += "<b>🎯 Ապագա Էքստրեմումներ․</b>\n"
        
        if not extremas:
            text += "Ապագա տիրույթում էքստրեմումներ չեն գտնվել։\n"
        else:
            for ext in extremas:
                icon = "🔺" if ext['type'] == 'MAX' else "🔻"
                text += f"{icon} <b>{ext['type']}</b>: x = <code>{ext['x']:.2f}</code>, y = <code>{ext['y']:.2f}</code>\n"
        
        # Ուղարկում ենք նկարը Telegram-ով
        photo = FSInputFile(img_path)
        await message.answer_photo(photo, caption=text, parse_mode="HTML")
        
        # Ջնջում ենք ժամանակավոր նկարը
        if os.path.exists(img_path):
            os.remove(img_path)
            
    except Exception as e:
        await message.answer(f"❌ Սխալ տեղի ունեցավ: {str(e)}")

async def main():
    print("🤖 Բոտը գործարկված է...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
