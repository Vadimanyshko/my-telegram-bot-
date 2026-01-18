import asyncio
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- НАСТРОЙКИ ---
TOKEN = "8401646010:AAGiv6GCb6bkAwZ0wUjzBC86cXFPHf-kvfg"
TABLE_NAME = "SBERBANK таблица" 

# ДАННЫЕ ВАШЕГО КЛЮЧА
CLIENT_EMAIL = "telegram-bot-sberbank@sberbank-484709.iam.gserviceaccount.com"
# Ключ вставлен максимально аккуратно
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDcZHH+k4QaAQE8\n8jmtNQN6Ehv3YSrYIL7VcacYUye604JXaOb0jkI9zSR2yYfuI5KuW9srS0qMcd/r\n9HJK01j0lHl59iufZdHgRg48SChCdowfIoCfAnIGOJfdzW6l/jGi12A9c2/XQs25\n2QE93ero4Q1M0LabPEVOhD4sepv/dAcwy45czgiw6+FXM2hMyy5/4qjEM+PRW8Jx\nmhj8s8EFEL+x3BqlqxzwsfCJE3k63EISIOfSo4SmZKCVaYzsqwSHuVi7NqhtIcAv\n7bsh8lV3xLGfanOs5y3c9bS2G57utflUhZA2NDqSs+V8ivKHUcSmXl5bh7LSv/sj\n/gF0xYnRAgMBAAECggEAA2tuL2EBbmID/j+Y/0Zc9beB1QrZRcKxirjW/8fQ/ZNQ\nWgGM4RUVsOLL8Yu/+gAnEmEh9Bsiiwaj7FKbegAhcC4Vb/vnWv1hzkAYBmAejkL8\n3RDPaHvnHUGFKM0npARo4q2biBnLegl3+XyFFBDwUiHgb4fh+58HXQp7aKOAZBO3\nUXCbOhM3uyN72wSHf6mpnILK+1/BztM87cYcNYA4ySw2oKRbx/Iy7rFuUnnY+/pM\nKQNIBrIDoabJ1ubiWFEvOz//+3zwyyQAfPWFZr+X83GJ565e/4Qt2zOjPXbz1Hyv\nh3uz4FvUE1IUkiuFl1WzFliKMf0CLbLOsu82uRwYtwKBgQD3BVcEwyYiJGJt2MvC\nvYtCQRd6KnhTBLc3Fa9APLT5d10jC0k0cZc3DyKsqj260j7/hew2OF7fNG5yFp6V\nthK6NOLIQaU60zL/pcONQ3K/sttaXxeEpIEiKlgPb0c1hFMrPoNdhwwXFzpb5JRr\nGVIdiiuVjsa0bGkHxz4LMBW+vwKBgQDkZ1AoD031bb2JIlePR6KFKxqXZIi3AX+g\n0pGRL72ttT7tkP6jZNDMc9nHcUz1A7LJ3L3ZPVfXmS/alfca2lc4Y28fwJcoO80D\nq3YMiBnqTxN4Mcdj80Zbe9yi5eWBRP9Ky4AMxVOyuB3mIrYrnbMhhEPEYJ/qHGMR\n8nJL4OJrbwKBgH25jgyydpoyApb+HNdFObfDAXwAWbWHVOkIdGYxf7ro8dKAUAYN\nOnWfknpnO3v2vnG3a/48uqzINt6CfLyeKvHzMOnT35ENJYvQhrNDfQfstJBOjd3J\nDKCjBKb2cDvg2aPM8XeM4K5v+BgFQzUvcgfu5zf7r07tTpfS5NU06BxpAoGBAKCw\n/vfwLIzrdFmyy5+GapT+SmsQ1A7NAxoGi1t2FyDLT0acqEoUd8IgD6v9zoLi4zqa\nDwdz3QVWRRCoSX2e95Y4fsn8GVy5Fffq/da7OmBa2fvKKdnsIifi8Mu6qslT3bil\ni6Vwfv5SAtcSvM/a11hRUcwrntZ6uki6Jie0RBgJAoGAVKcUPAjB63cEVLPWp9Ys\nl+a/0smYpHcCmnA+IvS1fVjE7eUDw8Phojkz3GnmVNdxULgPZbKrPjDjLgABChwu\nJyxnNnN3BeUdNEB/Px0Zm50Y/DS7PQUxZ5bD1U0gNT5biFhbTQRAsD+BbsImKrx3\nASpQ1Cor5SaMBpCqxotZo/Q=\n-----END PRIVATE KEY-----"

dp = Dispatcher()

def get_data_from_google(user_id):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Ручная сборка данных для авторизации
        creds = ServiceAccountCredentials.from_json_keyfile_dict({
            "type": "service_account",
            "client_email": CLIENT_EMAIL,
            "private_key": PRIVATE_KEY.replace('\\n', '\n'),
            "token_uri": "https://oauth2.googleapis.com/token",
        }, scope)
        
        client = gspread.authorize(creds)
        sheet = client.open(TABLE_NAME).sheet1 
        all_values = sheet.get_all_values()
        
        for row in all_values[1:]:
            if len(row) < 3: continue
            if str(row[0]).strip() == str(user_id):
                res = {"name": row[1], "total": row[2], "details": []}
                if len(row) > 3:
                    for extra in row[3:]:
                        if extra.strip():
                            res["details"].append(extra.strip())
                return res
        return None
    except Exception as e:
        return f"Ошибка базы: {str(e)}"

def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="💰 Проверить начисления")
    kb.button(text="🔄 Перезагрузить")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"🏦 **SberBank приветствует!**\n🆔 ID: `{message.from_user.id}`", reply_markup=main_menu(), parse_mode="Markdown")

@dp.message(F.text == "💰 Проверить начисления")
async def show_salary(message: types.Message):
    status_msg = await message.answer("🔄 Связь с сервером...")
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, get_data_from_google, message.from_user.id)
    
    if isinstance(data, str):
        await status_msg.edit_text(f"⚠️ {data}")
    elif data:
        text = [
            f"👤 **Сотрудник:** {data['name']}",
            f"💵 **Сумма:** {data['total']} руб.",
            "━━━━━━━━━━━━━━━━━━"
        ]
        if data['details']:
            for item in data['details']:
                text.append(f"▫️ {item}")
        text.append(f"🕒 _Запрос: {time.strftime('%d.%m.%Y %H:%M:%S')}_")
        await status_msg.edit_text("\n".join(text), parse_mode="Markdown")
    else:
        await status_msg.edit_text(f"🚫 ID `{message.from_user.id}` не найден.")

async def main():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("--- БОТ ЗАПУЩЕН ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
