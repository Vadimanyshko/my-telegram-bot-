import asyncio
import gspread
import os
import time
import json
from google.oauth2.service_account import Credentials
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession

# --- НАСТРОЙКИ ---
TOKEN = "8401646010:AAGiv6GCb6bkAwZ0wUjzBC86cXFPHf-kvfg"
TABLE_NAME = "SBERBANK таблица" 

dp = Dispatcher()

def get_data_from_google(user_id):
    try:
        if not os.path.exists("creds.json"):
            return "Ошибка: файл creds.json не найден!"
            
        # Читаем файл как JSON
        with open("creds.json", "r") as f:
            info = json.load(f)
            
        # ВАЖНО: Исправляем проблему двойных слешей для Linux
        if "private_key" in info:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Авторизация через исправленный словарь
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open(TABLE_NAME).sheet1 
        all_values = sheet.get_all_values()
        
        for row in all_values[1:]:
            if len(row) < 3: continue
            if str(row[0]).strip() == str(user_id):
                res = {
                    "name": row[1],
                    "total": row[2],
                    "details": []
                }
                if len(row) > 3:
                    for extra in row[3:]:
                        if extra.strip():
                            res["details"].append(extra.strip())
                return res
        return None
        
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return f"Ошибка базы: {str(e)}"

# --- ХЕНДЛЕРЫ ---
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="💰 Проверить начисления")
    kb.button(text="🔄 Перезагрузить")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        f"🏦 **SberBank онлайн приветствует вас!**\n\n🆔 Ваш ID: `{message.from_user.id}`",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "💰 Проверить начисления")
async def show_salary(message: types.Message):
    status_msg = await message.answer("🔄 Связь с сервером SberBank...")
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, get_data_from_google, message.from_user.id)
    
    if isinstance(data, str):
        await status_msg.edit_text(f"⚠️ {data}")
    elif data:
        text = [
            "✅ **Данные найдены:**",
            f"👤 **Сотрудник:** {data['name']}",
            f"💵 **Сумма:** {data['total']} руб."
        ]
        await status_msg.edit_text("\n".join(text), parse_mode="Markdown")
    else:
        await status_msg.edit_text(f"🚫 ID `{message.from_user.id}` не найден.")

@dp.message(F.text == "🔄 Перезагрузить")
async def reload(message: types.Message):
    await start_cmd(message)

async def main():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("--- БОТ ЗАПУЩЕН ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
