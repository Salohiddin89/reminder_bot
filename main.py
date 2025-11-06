import asyncio
import os
import sqlite3
import dotenv
import re

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from keep_alive import keep_alive

dotenv.load_dotenv()
bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())


conn = sqlite3.connect("reminder.db")
cursor = conn.cursor()
conn.commit()

WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]

week_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Dushanba"),
            KeyboardButton(text="Seshanba"),
            KeyboardButton(text="Chorshanba"),
        ],
        [
            KeyboardButton(text="Payshanba"),
            KeyboardButton(text="Juma"),
            KeyboardButton(text="Shanba"),
        ],
    ],
    resize_keyboard=True,
)

finish_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Tugatish")]], resize_keyboard=True
)

confirm_keybord = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Tastiqlash"), KeyboardButton(text="Bekor qilish")]],
    resize_keyboard=True,
)

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/addlessons")],
        [KeyboardButton(text="/Dushanba"), KeyboardButton(text="/Seshanba")],
        [KeyboardButton(text="/Chorshanba"), KeyboardButton(text="/Payshanba")],
        [KeyboardButton(text="/Juma"), KeyboardButton(text="/Shanba")],
        [KeyboardButton(text="/9VDushanba"), KeyboardButton(text="/9VSeshanba")],
        [KeyboardButton(text="/9VChorshanba"), KeyboardButton(text="/9VPayshanba")],
        [KeyboardButton(text="/9VJuma"), KeyboardButton(text="/9VShanba")],
    ],
    resize_keyboard=True,
)


class WeekForm(StatesGroup):
    weekday = State()
    lessons = State()
    confirm = State()


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"👋 Salom {message.from_user.first_name}! Bu bot orqali siz kunlik Dars📚 javdalingizni saqlashingiz mumkin \n Javdal tuzish uchun /addlessons tering"
    )


@dp.message(Command("menu"))
async def menu_handler(message: Message):
    await message.answer(
        "📋 Quyidagi komandalarni tanlang yoki yozing:", reply_markup=menu_keyboard
    )


@dp.message(Command("addlessons"))
async def addlessons_handler(message: Message, state: FSMContext):
    await state.set_state(WeekForm.weekday)
    await message.answer("Hafta kunini tanlang", reply_markup=week_keyboard)


@dp.message(WeekForm.weekday)
async def weekday_handler(message: Message, state: FSMContext):
    if message.text not in WEEKDAYS:
        return await message.answer("Hafta kuni noto'g'ri kiritildi.")
    await state.set_data(data={"weekday": message.text, "lessons": []})
    await state.set_state(WeekForm.lessons)
    await message.answer(
        f"{message.text} kuni darslarini kiriting.", reply_markup=ReplyKeyboardRemove()
    )


@dp.message(WeekForm.lessons)
async def lessons_handler(message: Message, state: FSMContext):
    if message.text == "Tugatish":
        data = await state.get_data()
        await state.set_state(WeekForm.confirm)
        return await message.answer(
            f"""{data["weekday"]} jadvali:\n{"\n".join(f"{i + 1}. {lesson}" for i, lesson in enumerate(data["lessons"]))}""",
            reply_markup=confirm_keybord,
        )

    data = await state.get_data()
    raw_lessons = re.split(r"\n|,|;|\d+\.\s*", message.text)
    parsed_lessons = [item.strip() for item in raw_lessons if item.strip()]
    data["lessons"].extend(parsed_lessons)
    await state.update_data(data={"lessons": data["lessons"]})
    await message.answer(
        f"{data['weekday']} kuni darslarini kiriting.",
        reply_markup=finish_keyboard
        if len(data["lessons"]) > 0
        else ReplyKeyboardRemove(),
    )


@dp.message(WeekForm.confirm)
async def confirm_handler(message: Message, state: FSMContext):
    if message.text == "Bekor qilish":
        await state.clear()
        return await message.answer(
            "Ma'lumotlar bekor qilindi.", reply_markup=ReplyKeyboardRemove()
        )

    if message.text == "Tastiqlash":
        user_id = message.from_user.id
        data = await state.get_data()
        weekday = data["weekday"]
        lessons = data["lessons"]
        day = WEEKDAYS.index(weekday)
        cursor.execute(
            "DELETE FROM lessons WHERE day = ? AND user_id = ?", (day + 1, user_id)
        )
        for arrange, lesson in enumerate(lessons):
            cursor.execute(
                "INSERT INTO lessons (subject, day, arrange, user_id) VALUES (?, ?, ?, ?)",
                (lesson, day + 1, arrange + 1, user_id),
            )
        conn.commit()
        await state.clear()
        return await message.answer(
            "✅ Ma'lumotlar saqlandi.", reply_markup=ReplyKeyboardRemove()
        )

    await message.answer("⚠️ Xato tugma tanlandi.", reply_markup=ReplyKeyboardRemove())


# Hafta kunlari handlerlari (to‘g‘rilangan day qiymatlari)
@dp.message(Command("Dushanba"))
async def monday_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM lessons WHERE day = 1 AND user_id = ?", (user_id,))
    lessons = cursor.fetchall()
    answer = "*Dushanba* kunidagi darslar:\n\n"
    for lesson in lessons:
        subject = lesson[1]
        arrange = lesson[3]
        answer += f"_{arrange}_\\. {subject}\n"
    await message.answer(answer, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("Seshanba"))
async def seshanba_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM lessons WHERE day = 2 AND user_id = ?", (user_id,))
    lessons = cursor.fetchall()
    answer = "*Seshanba* kunidagi darslar:\n\n"
    for lesson in lessons:
        subject = lesson[1]
        arrange = lesson[3]
        answer += f"_{arrange}_\\. {subject}\n"
    await message.answer(answer, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("Chorshanba"))
async def chorshanba_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM lessons WHERE day = 3 AND user_id = ?", (user_id,))
    lessons = cursor.fetchall()
    answer = "*Chorshanba* kunidagi darslar:\n\n"
    for lesson in lessons:
        subject = lesson[1]
        arrange = lesson[3]
        answer += f"_{arrange}_\\. {subject}\n"
    await message.answer(answer, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("Payshanba"))
async def payshanba_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM lessons WHERE day = 4 AND user_id = ?", (user_id,))
    lessons = cursor.fetchall()
    answer = "*Payshanba* kunidagi darslar:\n\n"
    for lesson in lessons:
        subject = lesson[1]
        arrange = lesson[3]
        answer += f"_{arrange}_\\. {subject}\n"
    await message.answer(answer, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("Juma"))
async def juma_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM lessons WHERE day = 5 AND user_id = ?", (user_id,))
    lessons = cursor.fetchall()
    answer = "*Juma* kunidagi darslar:\n\n"
    for lesson in lessons:
        subject = lesson[1]
        arrange = lesson[3]
        answer += f"_{arrange}_\\. {subject}\n"
    await message.answer(answer, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("Shanba"))
async def shan_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM lessons WHERE day = 6 AND user_id = ?", (user_id,))
    lessons = cursor.fetchall()
    answer = "*Shanba* kunidagi darslar:\n\n"
    for lesson in lessons:
        subject = lesson[1]
        arrange = lesson[3]
        answer += f"_{arrange}_\\. {subject}\n"
    await message.answer(answer, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("9VDushanba"))
async def dushanba_handler(message: Message):
    await message.answer(
        "📘 *9V sinf Dushanba kungi darslar:*\n"
        "1\\. 🎯 Час будущегo\n"
        "2\\. 🇬🇧 английский язык\n"
        "3\\. 🇺🇿 Узбекский язык\n"
        "4\\. 🏠 Родной язык\n"
        "5\\. ➕ Алгебра\n"
        "6\\. 📐 Геометрия",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message(Command("9VSeshanba"))
async def Vseshanba_handler(message: Message):
    await message.answer(
        "📗 *9V sinf Seshanba kungi darslar:*\n"
        "1\\. 🏃‍♂️ физра\n"
        "2\\. 💻 информатика\n"
        "3\\. 🏛️ Основы гос и права\n"
        "4\\. ⚛️ Физика\n"
        "5\\. 🧬 Биология",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message(Command("9VChorshanba"))
async def Vchorshanba_handler(message: Message):
    await message.answer(
        "📙 *9V sinf Chorshanba kungi darslar:*\n"
        "1\\. 🏞️ История Узбекистана\n"
        "2\\. 🏠 Родной язык\n"
        "3\\. 📚 Литература\n"
        "4\\. ➕ Алгебра\n"
        "5\\. 📐 Геометрия\n"
        "6\\. 🇺🇿 Узбекский язык",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message(Command("9VPayshanba"))
async def Vpayshanba_handler(message: Message):
    await message.answer(
        "📒 *9V sinf Payshanba kungi darslar:*\n"
        "1\\. 🏃‍♂️ физра\n"
        "2\\. ✏️ Черчение\n"
        "3\\. 🇬🇧 английский язык\n"
        "4\\. 🌍 Всемирная история\n"
        "5\\. 💰 Экономика \\| 🗺️ география\n"
        "6\\. ⚗️ Химия",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message(Command("9VJuma"))
async def Vjuma_handler(message: Message):
    await message.answer(
        "📕 *9V sinf Juma kungi darslar:*\n"
        "1\\. ⚗️ Химия\n"
        "2\\. ➕ Алгебра\n"
        "3\\. 💻 информатика\n"
        "4\\. 🛠️ Технология\n"
        "5\\. 🏞️ История Узбекистана\n"
        "6\\. 🇺🇿 Узбекский язык",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message(Command("9VShanba"))
async def shanba_handler(message: Message):
    await message.answer(
        "📓 *9V sinf Shanba kungi darslar:*\n"
        "1\\. 🗺️ География\n"
        "2\\. 📚 Литература\n"
        "3\\. 🇬🇧 английский язык\n"
        "4\\. 🧬 биология\n"
        "5\\. ⚛️ физика\n"
        "6\\. ❤️ Воспитание",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def on_start():
    print("Bot has been started...")


async def main():
    dp.startup.register(on_start)
    await dp.start_polling(bot)

keep_alive()


if __name__ == "__main__":
    asyncio.run(main())
