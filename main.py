import asyncio
import gspread
import time
import base64
import json
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- НАСТРОЙКИ ---
TOKEN = "8401646010:AAGiv6GCb6bkAwZ0wUjzBC86cXFPHf-kvfg"
TABLE_NAME = "SBERBANK таблица" 

# Ваш ключ, закодированный в Base64 для защиты от ошибок копирования
B64_DATA = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAic2JlcmJhbmstNDg0NzA5IiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiMTVlODlhYjUwZDQ3NzA2ODUwM2Q2ODBhNjczYjdhNjIxYjEyOTkwZCIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZRSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2N3Z2dTakFnRUFBb0lCQVREYVpISHVrNFFhQVFFOFxuOGptdE5RTjZFaHYzWVNyWUlMN1ZjYWNZVXllNjA0SlhhT2IwamtJOXpTUjJZZm1JNUt1VzlzclMwcU1jZC9yXG45SEpLMDFqMGxIbDU5aXVmWmRIZ1JnNDhTQ2hDZG93ZklvQ2ZBbklHT0pmZnpXNmwvakdpMTJBOXcyL1hRczI1XG4yUUU5M2VybzRRMU0wTGFiUEVPaEQ0c2Vwdi9kQWN3eTQ1Y3pnaXc2K0ZYTTJoTXl5NS80cWpFTStQUlc4Snhcbm1oajhzOEVGRUwrczNCcWxxZHp3c2ZDSkUmazYzRUlTSU9mU280U21aS0NDVllZenNxV1NIdVZpN05xaHRJY0F2XG43YnNoOGxWM3hMR2Zhbk9zNXkzYzliUzJHNzd1dGZsdGhaQTJOR3FTcytWOGl2SkhVY1NtWGw1Ymg3TFN2L3NqXG4vZ0YweFluUkFnTUJBQUVDZ2dFQUEydHVMMkVCYm1JRC9qK1kvMFpjOWJlQjFRclpSY0t4aXJqVy84ZlEvWk5RXG5XZ0dNNFJVVnNPTEw4WXUvK2dBbkVtRWg5QnNpaXdhajdGS2JlZ0FoY0M0VmIvdm5XdjFoe2tBWUJtQWVqa0w4XG4zUkRQYUh2bkhVR0ZLTTBucEFSbzRxMmJpQm5MZWdsMytYeUZGQkR3VWlIZ2I0ZmgrNThIWFFwN2FLT0FaQk8zXG5VWEliT2hNM3V5Tjcyd1NIZjZtcG5JTEsrMS9CenRNODdjY05ZQTR5U3cyb0tSYngvSXk3ckZ1VW5uWSsvcE1cbmtRTE5CcklEb2FiSjF1YmlXRXZPei8vKzN6d3lRQWZQV0ZacitYODNHSjU2NWUvNFF0MnpPalBYYnoxSHl2XG5oM3V6NEZ2VUUxSVVraXVGbDFXekZsaUtNZjBDTGJMT3N1ODJ1UndZdHdLQmdRRDNCVmNFd3lZaUpHSnQyTXZDXG52WXRDUVJkNktuaFRCTGMzRmE5QVBMVDVkMTBqQzBrMFpZYzNEeUtzcmoyNjBqNy9oZXcyT0Y3Zk5HNXlGcDZWXG50SEs2Tk9MSVFhVTYwekwvcGNOT1EzSy9zdHRhWHhFRXBJRWlLbGdQYjBjMWhGTVJQb05kaHd3WEZ6cGI1SlJyXG5HVklkaWl1VmpzYTBiR2tIeHo0TE1CVitvd0tCZ1FEa1oxQW9EMzExYmIySklsZVBSNktGS3hxWFpJaTNBWitnXG4wcEdSTDcydHRUN3RrUDZqWk5ETWM5bkhDVXoxQTdMSjNMM1pQVmZYbVMvYWxmY2EybGM0WTI4ZndKY29PODBEXG5xM1lNaUJuclR4TjRNY2RqODBaYmU5eWk1ZVdCUlA5S3k0QU14Vk95dUIzbUlyWXJuYk1oaEVQRVlKL3FIR01SXG44bkpMNE9KcmJ3S0JnSDI1amd5eWRwY3lBcGIrSE5kRk9iZkRBWHdBQmJXSFZPa0lkR1l4ZjdybzhkS0FVQVlOXG5PbldmS25wbk8zdjJ2bkczYS80OHVyelpOdDZDZkx5ZUt2SHpNT25UMzVFTkpZdlFoclNERmZmc3RKQk9qZDNKXG5ES0NqQktiMmNEdmcyYVBNOFhlTTRLNXYrQmdGUXpVdmNnZnU1emY3cjA3dFRwZlM1TlU2QnhycEFvR0JBS0N3XG4vdmZ3TEl6cmRGbXl5NStHYXBUK1Ntc1ExQTdOQXhvR2kxdDJGeURMVDBhY3FFb1VkOElnRDZ2OXpvTGk0enFhXG5Ed2R6M1FWV1JSQ29TWDJlOTVZN2ZzbjhHVnk1RmZmcS9kYTdP bUJBMmZ2S0tkbnNJaWZpOE11NnFzbFQzYmlsXG5pNlZ3ZnY1U0F0Y1N2TS9hMTFoUlVjd3JudFo2dWtpNkppZTBSZ0pBb0dBVktjVVBBakI2M2NFVkxQVzlZc1NcbmwrYS8wc21ZUEhjQ21uQStJdlMxZlZqRTdlVUR3OFBob2prejNHbm1WTmR4VUxnUFpiS3JQakRqTGdBQkNoV3Vcbkp5eG5Obk4zQmVVZE5FQi9QeDBabTUwWS9EUzdQUVV4WjViRDFVMWdOVDViaUZoYlRRUkFzRCtCYnNJbUtyeDNcbmFTcFExQ29yNVNhTUJwQ3F4b3Raby9RPSIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvdGVsZWdyYW0tYm90LXNiZXJiYW5rJTQwc2JlcmJhbmstNDg0NzA5LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9"

dp = Dispatcher()

def get_google_client():
    # Декодируем ключ из Base64 обратно в JSON
    json_creds = json.loads(base64.b64decode(B64_DATA).decode('utf-8'))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
    return gspread.authorize(creds)

def get_data_from_google(user_id):
    try:
        client = get_google_client()
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
    await message.answer(f"🏦 **SberBank онлайн приветствует вас!**\n\n🆔 Ваш ID: `{message.from_user.id}`", reply_markup=main_menu(), parse_mode="Markdown")

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
            "━━━━━━━━━━━━━━━━━━",
            f"👤 **Сотрудник:** {data['name']}",
            f"💵 **Сумма к выплате:** {data['total']} руб.",
            "━━━━━━━━━━━━━━━━━━"
        ]
        if data['details']:
            text.append("📅 **Детализация:**")
            for item in data['details']:
                text.append(f"▫️ {item}")
            text.append("━━━━━━━━━━━━━━━━━━")
        
        # Время на сервере (МСК)
        text.append(f"🕒 _Дата запроса: {time.strftime('%d.%m.%Y %H:%M:%S')}_")
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
