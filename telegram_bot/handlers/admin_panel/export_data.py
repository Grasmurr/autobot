from telegram_bot.loader import dp, bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message

)
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.types.input_file import BufferedInputFile

from telegram_bot.loader import dp, bot
from telegram_bot.assets.config import ADMIN_ID
from telegram_bot.service.chat_backends import create_keyboard_buttons
from telegram_bot.states import AdminStates
from telegram_bot.handlers.user_panel.main_menu import main_menu
from telegram_bot.handlers.admin_panel.main_menu import admin_menu, mailing_menu

from telegram_bot.service.api_methods import create_applicant, update_applicant_data, get_applicant, get_all_applicants


import csv
import pandas as pd
import io
import tempfile, os

import openpyxl
from io import BytesIO
from aiogram.types import Message
from aiogram.utils.markdown import hcode


@dp.message(AdminStates.main, F.text == "Выгрузить данные")
async def choose_event_for_uploading_data(message: Message, state: FSMContext):
    markup = create_keyboard_buttons('.xlsx', '.csv', 'Назад')
    await state.set_state(AdminStates.upload_data)
    await message.answer(text='Выберите формат, в котором хотите выгрузить данные:',
                         reply_markup=markup)


@dp.message(AdminStates.upload_data, F.text == 'Назад')
async def back_from_choosing_event_for_uploading_data(message: Message, state: FSMContext):
    await choose_event_for_uploading_data(message, state)


def create_table(data, file_format):
    columns = {
        "telegram_name": "Имя в Telegram",
        "user_id": "ID пользователя",
        "name_from_user": "Имя пользователя",
        "telephone_number": "Телефонный номер",
        "urls": "Список ссылок",
        "request": "Был ли запрос"
    }

    df = pd.DataFrame.from_records(data)
    df = df.rename(columns=columns)

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    file_path = 'Пользователи' + file_format

    if file_format == ".xlsx":
        df.to_excel(file_path, index=False)
    elif file_format == ".csv":
        df.to_csv(file_path, index=False)
    else:
        print("Unsupported file format")
        return

    return file_path


@dp.message(AdminStates.upload_data, F.text.in_(['.xlsx', '.csv']))
async def export_event_data(message: Message, state: FSMContext):
    file_format = message.text

    data = await get_all_applicants()
    data = data['data']

    file_path = create_table(data, file_format)

    markup = create_keyboard_buttons('Выгрузить в другом формате',
                                                   'Вернуться в меню админа')
    caption = f"Вот ваш файл в формате {file_format}"
    with open(file_path, "rb") as file:
        await message.answer_document(document=BufferedInputFile(file.read(), filename=f'Пользователи{file_format}*'),
                                      caption=caption, reply_markup=markup)

    os.remove(file_path)

    await state.set_state(AdminStates.upload_data_in_format_final)


@dp.message(AdminStates.upload_data_in_format_final, F.text == 'Выгрузить в другом формате')
async def upload_data_in_another_format(message: Message, state: FSMContext):
    await choose_event_for_uploading_data(message, state)


@dp.message(AdminStates.upload_data_in_format_final, F.text == 'Вернуться в меню админа')
async def back_from_upload_data_in_format(message: Message, state: FSMContext):
    await admin_menu(message, state)