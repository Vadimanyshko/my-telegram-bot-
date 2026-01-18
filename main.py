import asyncio
import gspread
import os
import time
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession

# --- НАСТРОЙКИ ---
TOKEN = "8401646010:AAGiv6GCb6bkAwZ0wUjzBC86cXFPHf-kvfg"
TABLE_NAME = "SBERBANK таблица" 

dp = Dispatcher()

# Функция для получения данных из Google Таблиц
def get_data_from_google(user_id):
    try:
        if not os.path.exists("creds.json"):
            return "Ошибка: файл creds.json не найден на хостинге!"
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
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
                # Собираем данные из всех колонок после C (D, E, F...)
                if len(row) > 3:
                    for extra in row[3:]:
                        if extra.strip():
                            res["details"].append(extra.strip())
                return res
        return None
        
    except Exception as e:
        return f"Ошибка базы: {str(e)}"

# Главное меню
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="💰 Проверить начисления")
    kb.button(text="🔄 Перезагрузить")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

# Обработка команды /start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    welcome_text = (
        f"🏦 **SberBank онлайн приветствует вас!**\n\n"
        f"🆔 Ваш ID: `{message.from_user.id}`\n"
        f"📊 Состояние: Подключено к SberBank онлайн\n\n"
        f"Нажмите кнопку ниже, чтобы получить выписку."
    )
    await message.answer(welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

# Обработка кнопки начислений
@dp.message(F.text == "💰 Проверить начисления")
async def show_salary(message: types.Message):
    status_msg = await message.answer("🔄 Связь с сервером SberBank...")
    
    # Запуск поиска данных
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, get_data_from_google, message.from_user.id)
    
    if isinstance(data, str):
        await status_msg.edit_text(f"⚠️ {data}")
    elif data:
        # Формирование красивого сообщения-чека
        text = [
            "✅ **Данные найдены:**",
            "━━━━━━━━━━━━━━━━━━",
            f"👤 **Сотрудник:** {data['name']}",
            f"💵 **Сумма к выплате:** {data['total']} руб.",
            "━━━━━━━━━━━━━━━━━━"
        ]
        
        if data['details']:
            text.append("📅 **Детализация по периодам:**")
            for item in data['details']:
                text.append(f"▫️ {item}")
            text.append("━━━━━━━━━━━━━━━━━━")
            
        text.append(f"🕒 _Дата запроса: {time.strftime('%d.%m.%Y %H:%M')}_")
        
        await status_msg.edit_text("\n".join(text), parse_mode="Markdown")
    else:
        await status_msg.edit_text(f"🚫 ID `{message.from_user.id}` не найден в системе.")

@dp.message(F.text == "🔄 Перезагрузить")
async def reload(message: types.Message):
    await start_cmd(message)

# Запуск бота
async def main():
    # Настройка сессии для стабильной работы на сервере
    session = AiohttpSession()
    bot = Bot(token=TOKEN, session=session)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print(f"--- БОТ УСПЕШНО ЗАПУЩЕН ---")
    
    try:
        await dp.start_polling(bot, polling_timeout=30)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот выключен")