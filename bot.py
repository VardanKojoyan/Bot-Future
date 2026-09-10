import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiohttp import web
from fill_db import update_binance_data
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
        "Ուղարկիր /predict հրամանը, որպեսզի Binance-ից վերցնեմ BTC/USDT-ի թարմ ժամային տվյալները, "
        "կատարեմ Ֆուրյեի + Թրենդի կանխատեսում առաջիկա 48 ժամվա համար և ուղարկեմ գրաֆիկը։"
    )

@dp.message(Command("predict"))
async def cmd_predict(message: types.Message):
    await message.answer("🔄 Վերցնում եմ Binance-ի թարմ տվյալները և հաշվում կանխատեսումը...")
    
    try:
        # 1. Թարմացնում ենք բազան Binance API-ից
        update_binance_data(symbol="BTCUSDT", interval="1h", limit=200, db_name="data.db")
        
        # 2. Գեներացնում ենք կանխատեսումը 48 ժամվա համար
        extremas, img_path = generate_prediction_plot(db_name="data.db", output_img="prediction.png", future_hours=48)
        
        text = "<b>📊 Binance BTC/USDT Կանխատեսում (+48Ժ)</b>\n\n"
        text += "<b>🎯 Ապագա Գնային Էքստրեմումներ․</b>\n"
        
        if not extremas:
            text += "Առաջիկա 48 ժամում հստակ էքստրեմումներ չեն գտնվել։\n"
        else:
            for ext in extremas:
                icon = "🔺" if ext['type'] == 'MAX' else "🔻"
                text += f"{icon} <b>{ext['type']}</b> (+{ext['hours_ahead']}ժ հետո): <b>${ext['y']:.2f}</b>\n"
        
        photo = FSInputFile(img_path)
        await message.answer_photo(photo, caption=text, parse_mode="HTML")
        
        if os.path.exists(img_path):
            os.remove(img_path)
            
    except Exception as e:
        await message.answer(f"❌ Սխալ տեղի ունեցավ: {str(e)}")

# Web Server Render-ի համար
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    # Ստեղծում ենք aiohttp app-ը
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/health', handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Fake Web Server started on port {port}")
    
    print("🤖 Բոտը գործարկված է...")
    # Ջնջում ենք հին webhook-ները, որպեսզի conflict չլինի
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
