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

from telegram_bot.loader import dp, bot
from telegram_bot.assets.config import ADMIN_ID
from telegram_bot.service.chat_backends import create_keyboard_buttons
from telegram_bot.states import AdminStates
from telegram_bot.handlers.user_panel.main_menu import main_menu
from telegram_bot.handlers.admin_panel.main_menu import admin_menu, mailing_menu

from telegram_bot.service.api_methods import create_applicant, update_applicant_data, get_applicant, get_all_applicants



@dp.message(AdminStates.mailing_options, F.text == "Всем пользователям")
async def start_mailing(message: Message, state: FSMContext):
    buttons = create_keyboard_buttons('Текст', 'Фото', 'Файл', 'Назад')
    await message.answer('Хорошо! Выберите в каком формате вы хотите отправить рассылку:', reply_markup=buttons)
    await state.set_state(AdminStates.begin_mailing)


@dp.message(AdminStates.begin_mailing, F.text == 'Назад')
async def back_to_mailing_menu(message: Message, state: FSMContext):
    await mailing_menu(message, state)


@dp.message(AdminStates.begin_mailing)
async def back_to_admin_menu(message: Message, state: FSMContext):
    type_to_mail = message.text
    if type_to_mail not in ['Текст', 'Фото', 'Файл']:
        buttons = create_keyboard_buttons('Текст', 'Фото', 'Файл', 'Назад')
        await message.answer('Кажется, вы выбрали что-то не из кнопок. Пожалуйста, воспользуйтесь кнопкой ниже:',
                             reply_markup=buttons)
        return
    buttons = create_keyboard_buttons('Назад')
    if type_to_mail == 'Текст':
        await state.set_state(AdminStates.mailing_with_text)
        await message.answer('Хорошо! Отправьте текст, который вы собираетесь отправить:',
                             reply_markup=buttons)
    elif type_to_mail == 'Фото':
        await state.set_state(AdminStates.mailing_with_photo)
        await message.answer('Хорошо! Отправьте фото, которое вы собираетесь отправить (с подписью):',
                             reply_markup=buttons)
    else:
        await state.set_state(AdminStates.mailing_with_file)
        await message.answer('Хорошо! Отправьте файл, который вы собираетесь отправить (с подписью):',
                             reply_markup=buttons)


@dp.message(AdminStates.mailing_with_photo, F.text == 'Назад')
async def back_to_start_mailing(message: Message, state: FSMContext):
    await start_mailing(message, state)


@dp.message(AdminStates.mailing_with_text, F.text == 'Назад')
async def back_to_start_mailing(message: Message, state: FSMContext):
    await start_mailing(message, state)


@dp.message(AdminStates.mailing_with_file, F.text == 'Назад')
async def back_to_start_mailing(message: Message, state: FSMContext):
    await start_mailing(message, state)


@dp.message(AdminStates.mailing_with_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    caption = message.caption
    await state.update_data(mailing_type='Фото', photo_id=photo_id, caption=caption)
    buttons = create_keyboard_buttons('Подтвердить', 'Назад')
    await message.answer('Вы хотите разослать такое фото с такой подписью?', reply_markup=buttons)
    await message.answer_photo(photo=photo_id, caption=caption)


@dp.message(AdminStates.mailing_with_file, F.document)
async def handle_photo(message: Message, state: FSMContext):
    file_id = message.document.file_id
    caption = message.caption
    await state.update_data(mailing_type='Файл', file_id=file_id, caption=caption)
    buttons = create_keyboard_buttons('Подтвердить', 'Назад')
    await message.answer('Вы хотите разослать такой файл с такой подписью?', reply_markup=buttons)
    await message.answer_document(document=file_id, caption=caption)

@dp.message(AdminStates.mailing_with_text)
async def handle_text(message: Message, state: FSMContext):
    ans = message.text
    await state.update_data(mailing_type='Текст', text_to_mail=ans)
    buttons = create_keyboard_buttons('Подтвердить', 'Назад')
    await message.answer('Вы хотите разослать такой текст?', reply_markup=buttons)
    await message.answer(ans)

@dp.message(AdminStates.mailing_with_text, F.text == 'Подтвердить')
async def handle_text(message: Message, state: FSMContext):
    await mail_promouters(state)
    await admin_menu(message, state)


@dp.message(AdminStates.mailing_with_file, F.text == 'Подтвердить')
async def start_file_mailing(message: Message, state: FSMContext):
    await mail_promouters(state)
    await admin_menu(message, state)


@dp.message(AdminStates.mailing_with_photo, F.text == 'Подтвердить')
async def start_photo_mailing(message: Message, state: FSMContext):
    await mail_promouters(state)
    await admin_menu(message, state)


async def mail_promouters(state: FSMContext):
    ids = await get_all_applicants()
    data = await state.get_data()
    mailing_type = data['mailing_type']
    if mailing_type == 'Текст':
        content = data['text_to_mail']
    elif mailing_type == 'Фото':
        content = [data['photo_id'], data['caption']]
    else:
        content = [data['file_id'], data['caption']]
    for i in ids['data']:
        user_id = i['user_id']
        try:
            if mailing_type == 'Текст':
                await bot.send_message(chat_id=user_id, text=content)
            elif mailing_type == 'Фото':
                photo_id, caption = content
                await bot.send_photo(chat_id=user_id, photo=photo_id, caption=caption)
            elif mailing_type == 'Файл':
                file_id, caption = content
                await bot.send_document(chat_id=user_id, document=file_id, caption=caption)
        except:
            user_data = await get_applicant(user_id=user_id)
            username = user_data['data'][0]["telegram_name"]

            user_profile_link = f"<a href='tg://user?id={user_id}'>{username}</a>"
            await bot.send_message(chat_id=ADMIN_ID, text=f'Не получилось отправить пользователю '
                                                          f'<b>{user_profile_link}</b>', ParseMode=ParseMode.HTML)







