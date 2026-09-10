import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiohttp import web
from predictor import generate_prediction_plot

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN-ը գտնված չէ Environment Variables-ում։")

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
        extremas, img_path = generate_prediction_plot(db_name="data.db", output_img="prediction.png")
        
        text = "<b>📊 Կանխատեսման Արդյունքներ</b>\n\n"
        text += "<b>🎯 Ապագա Էքստրեմումներ․</b>\n"
        
        if not extremas:
            text += "Ապագա տիրույթում էքստրեմումներ չեն գտնվել։\n"
        else:
            for ext in extremas:
                icon = "🔺" if ext['type'] == 'MAX' else "🔻"
                text += f"{icon} <b>{ext['type']}</b>: x = <code>{ext['x']:.2f}</code>, y = <code>{ext['y']:.2f}</code>\n"
        
        photo = FSInputFile(img_path)
        await message.answer_photo(photo, caption=text, parse_mode="HTML")
        
        if os.path.exists(img_path):
            os.remove(img_path)
            
    except Exception as e:
        await message.answer(f"❌ Սխալ տեղի ունեցավ: {str(e)}")

# Web Server Render-ի և UptimeRobot-ի համար
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/health', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Fake Web Server started on port {port}")

async def main():
    await start_web_server()
    print("🤖 Բոտը գործարկված է...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
