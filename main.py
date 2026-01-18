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
TOKEN = "8536656939:AAFw-laE_jlbzYBYd7seZNeAxF_9cn4f_qE"
TABLE_NAME = "SBERBANK таблица" 

dp = Dispatcher()

# Функция для получения данных из Google Таблиц
def get_data_from_google(user_id):
    try:
        # Проверка наличия файла ключей
        if not os.path.exists("creds.json"):
            return "Ошибка: файл creds.json не найден!"
            
        # Настройка доступов
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Читаем файл ключа и исправляем возможные ошибки с переносом строк
        with open("creds.json", "r", encoding="utf-8") as f:
            creds_info = json.load(f)
            
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
        
        # Авторизация по новому стандарту (google-auth)
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Открытие таблицы
        sheet = client.open(TABLE_NAME).sheet1 
        all_values = sheet.get_all_values()
        
        # Поиск пользователя по ID (столбец A)
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
        print(f"DEBUG LOG ERROR: {e}")
        return f"Ошибка базы: {str(e)}"

# Главное меню (кнопки)
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
    
    # Запуск поиска данных в отдельном потоке
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, get_data_from_google, message.from_user.id)
    
    if isinstance(data, str):
        await status_msg.edit_text(f"⚠️ {data}")
    elif data:
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
    session = AiohttpSession()
    bot = Bot(token=TOKEN, session=session)
    
    # Пропускаем накопившиеся сообщения
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
