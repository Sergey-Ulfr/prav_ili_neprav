import logging
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os
from dotenv import load_dotenv


# Загружаем переменные окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Проверяем, что переменные установлены
if not API_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")
if not ADMIN_ID:
    raise ValueError("Переменная окружения ADMIN_ID не установлена!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище ID пользователей, связанных с сообщениями админу
user_message_mapping = {}

# Создаем клавиатуру с кнопками
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="FAQ"), KeyboardButton(text="Консультант")],
            [KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True  # Сделать клавиатуру компактной
    )
    return keyboard

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет! Я помогу тебе найти ответ на частые вопросы, а также передать твой вопрос специалисту. Используй кнопки ниже для навигации.",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("faq"))
async def faq_command(message: types.Message):
    image_path = "faq_image.jpg"
    if os.path.exists(image_path):
        photo = FSInputFile(image_path)  # Используем FSInputFile вместо InputFile
        await message.answer_photo(photo)
    else:
        await message.answer("❗ Изображение FAQ не найдено.")

    faq_text = """
📌 1. Могу ли я вернуть товар надлежащего качества, если он мне не подошёл?
Да. По закону «О защите прав потребителей» вы можете вернуть неиспользованный товар в течение 14 дней после покупки (не считая дня приобретения), при условии сохранения товарного вида, упаковки и пломбы.

📌 2. Как оформить претензию на некачественный товар?
Составьте заявление в свободной форме: 

1. Наименование продавца (исполнителя). Можно обратиться с претензией к продавцу, изготовителю или импортеру, их представителям. 
2. Ваши данные. Обязательно нужно указать контактный телефон и адрес (почтовый или электронный) для ответа на претензию. 
3. Информацию о приобретённом товаре. Следует указать дату покупки, оплаты и поставки, описание товара и его стоимость. 
4. Суть претензии. Нужно подробно описать, когда был обнаружен недостаток товара и в чём он проявляется, в чём выражаются нарушения условий оказания услуги (выполнения работы). 
5. Требования. Следует указать требования, которые предъявляются к продавцу (исполнителю). Они должны быть предусмотрены законодательством. 
6. Перечень прилагаемых документов. Нужно указать, копии каких документов к претензии прилагаются (кассовый или товарный чек, договор, гарантийный талон, акты, заключения и другие). 
7. Дату и подпись. Претензию необходимо составить в двух экземплярах — для себя и для продавца (исполнителя). 

📌 3. В какой срок продавец обязан рассмотреть претензию?
Не более 10 календарных дней с момента получения вашего письма или заявления. Если нарушены сроки, вы можете потребовать штраф — 1% от стоимости товара за каждый день просрочки.

📌 4. Как вернуть деньги за услугу, оказанную некачественно?
Для составления претензии на некачественную услугу рекомендуется включить в неё следующую информацию:
1. Сведения об адресате претензии . Нужно указать руководителя организации, её наименование, местонахождение и иные индивидуализирующие признаки (например, ИНН).
2. Наименование и почтовый адрес заявителя.
3. Дату и исходящий номер требования.
4. Реквизиты договора на оказание услуг, по обязательствам из которого возник спор.
5. Описание нарушения получателем претензии обязательства со ссылками на пункты договора.
6. Конкретные требования к получателю претензии (компенсация понесённых убытков, уплата штрафных санкций, выполнение надлежащим образом взятого по договору обязательства).
7. Ссылки на нормы закона, в соответствии с которыми составлена претензия и предъявлены те или иные требования.
8. Перечень прилагаемых документов (если таковые имеются). 

В течение 10 дней он должен устранить недостатки или вернуть уплаченную сумму и компенсировать убытки.

📌 5. Что делать, если продавец отказывается принять претензию?
Направьте претензию письмом с уведомлением. Если и это не помогает — обращайтесь в Роспотребнадзор, его территориальное управление или в суд.

📌 6. Кто оплачивает доставку при возврате товара?
Надлежащее качество: расходы несёт покупатель.
Некачественный товар: все расходы (доставка, пересылка) оплачивает продавец.

📌 7. Как вернуть технически сложный товар?
Если товар в порядке — вернуть нельзя. При наличии дефекта в течение гарантийного срока (или 15 дней для первичной оценки) вы можете требовать ремонта, замены или возврата денег.

📌 8. Можно ли вернуть купленный в интернете товар?
Да. Правила такие же, как в офлайн‑магазине. Письменная претензия и возврат товара в течение 7 дней после получения (14 дней по «надлежащему качеству»).

📌 9. Имею ли я право на моральный вред и компенсацию убытков?
Если действия продавца причинили вам физический или нравственный ущерб, вы можете требовать компенсацию морального вреда и возмещения прямых убытков в суде.

📌 10. Как контролировать сроки выполнения требований?
Ведите учёт дат:
10 дней на рассмотрение претензии;
10 дней на устранение недостатков;
3 дня на возврат денег после вашего требования.
При нарушении — начисляется неустойка (1% стоимости товара/услуги за каждый день просрочки)."""
    await message.answer(faq_text)

@dp.message(Command("konsultant"))
async def konsultant_command(message: types.Message):
    if os.path.exists("konsultant.jpg"):
        await message.answer_photo(FSInputFile("konsultant.jpg"))
    await message.answer(
        "Пожалуйста, опишите свою проблему — специалист свяжется с вами.",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "FAQ")
async def faq_button_handler(message: types.Message):
    await faq_command(message)

@dp.message(F.text == "Консультант")
async def konsultant_button_handler(message: types.Message):
    await konsultant_command(message)

@dp.message(F.text == "Помощь")
async def help_button_handler(message: types.Message):
    await message.answer(
        "Если у вас возникли вопросы, используйте кнопки ниже или напишите администратору.",
        reply_markup=get_main_keyboard()
    )

# Обработка сообщений пользователей (пересылаем админу)
@dp.message(F.from_user.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or 'без ника'
        text = message.text or "<нет текста>"

        sent = await bot.send_message(
            ADMIN_ID,
            f"📩 Вопрос от @{username} (ID: {user_id}):\n{text}"
        )

        user_message_mapping[sent.message_id] = user_id
        await message.reply("✅ Ваша заявка отправлена. Ожидайте ответа.")
    except Exception as e:
        print(f"Ошибка при пересылке сообщения: {e}")
        await message.reply("❗ Ошибка при отправке. Попробуйте позже.")


# Ответ администратора на сообщение — пересылаем пользователю
@dp.message(F.from_user.id == ADMIN_ID)
async def handle_admin_reply(message: types.Message):
    if message.reply_to_message and message.reply_to_message.message_id in user_message_mapping:
        user_id = user_message_mapping[message.reply_to_message.message_id]
        try:
            await bot.send_message(user_id, f"💬 Ответ специалиста:\n{message.text}")
            await message.reply("✅ Ответ отправлен пользователю.")
        except Exception as e:
            await message.reply(f"❌ Не удалось отправить сообщение пользователю: {e}")
    else:
        await message.reply("❗ Ответьте на сообщение пользователя, чтобы бот понял, кому отправить сообщение.")

# Настройка веб-сервера
app = web.Application()
webhook_path = f"/bot/{API_TOKEN}"
handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
handler.register(app, path=webhook_path)

async def on_startup(app):  # ← нужно принять app
    webhook_url = "https://prav-ili-neprav.onrender.com" + webhook_path
    await bot.set_webhook(webhook_url)

if __name__ == "__main__":
    app.on_startup.append(on_startup)
    port = int(os.getenv("PORT", 10000))  # Render использует переменную PORT
    web.run_app(app, host="0.0.0.0", port=port)