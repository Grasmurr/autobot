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

from telegram_bot.service.api_methods import create_applicant, update_applicant_data, get_applicant


@dp.message(AdminStates.mailing_options, F.text == 'По ID')
async def mailing_menu(message: Message, state: FSMContext):
    await state.set_state(AdminStates.mailing_id_enter)
    markup = create_keyboard_buttons("Назад")
    await message.answer('Введите ID пользователя', reply_markup=markup)

@dp.message(AdminStates.mailing_id_enter, F.text == 'Назад')
async def back_from_mailing_menu(message: Message, state: FSMContext):
    await admin_menu(message, state)

@dp.message(AdminStates.mailing_id_enter)
async def mailing_id_enter(message: Message, state: FSMContext):
    if not message.text.isdigit():
        markup = create_keyboard_buttons("Назад")
        await message.answer('Кажется, вы прислали не ID — в нем могут быть только цифры. Попробуйте еще раз',
                             reply_markup=markup)
    else:
        user_id = message.text

        user_data = await get_applicant(user_id=user_id)
        username = user_data['data'][0]["telegram_name"]

        user_profile_link = f"<a href='tg://user?id={user_id}'>{username}</a>"
        markup = create_keyboard_buttons("Подтвердить",
                                         "Назад")
        await state.update_data(user_profile_link=user_profile_link, user_id=user_id)

        await message.answer(f"Вы собираетесь отправить сообщение пользователю <b>{user_profile_link}</b>. "
                             f"Подтвердить?\n\n"
                             f"Также вы можете отправить сообщение вручную, перейдя по ссылке на профиль пользователя",
                             reply_markup=markup)
        await state.set_state(AdminStates.mailing_id_confirm_user)

@dp.message(AdminStates.mailing_id_confirm_user, F.text == 'Назад')
async def back_from_mailing_id_enter(message: Message, state: FSMContext):
    await mailing_menu(message, state)


@dp.message(AdminStates.mailing_id_confirm_user, F.text == 'Подтвердить')
async def mailing_id_confirm_user(message: Message, state: FSMContext):
    markup = create_keyboard_buttons("Назад")
    await message.answer(f"Пожалуйста, пришлите текст сообщения",
                         reply_markup=markup)
    await state.set_state(AdminStates.mailing_id_enter_message_text)


@dp.message(AdminStates.mailing_id_confirm_user, F.text == 'Назад')
async def back_from_mailing_id_confirm_user(message: Message, state: FSMContext):
    await mailing_id_enter(message, state)


@dp.message(AdminStates.mailing_id_enter_message_text)
async def mailing_id_enter_message_text(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    markup = create_keyboard_buttons("Подтвердить",
                                     "Назад")
    user_profile_link = data['user_profile_link']

    await message.answer(f"Вы хотите отправить сообщение пользователю <b>{user_profile_link}</b>\n\n"
                         f"<b>Текст:</b>\n\n"
                         f"{text}\n\n"
                         f"Подтвердить?",
                         reply_markup=markup)
    await state.update_data(text=text)
    await state.set_state(AdminStates.mailing_id_сonfirm_message_text)


@dp.message(AdminStates.mailing_id_сonfirm_message_text, F.text == 'Назад')
async def back_from_mailing_id_сonfirm_message_text(message: Message, state: FSMContext):
    await mailing_id_confirm_user(message, state)

@dp.message(AdminStates.mailing_id_сonfirm_message_text, F.text == 'Подтвердить')
async def mailing_id_сonfirm_message_text(message: Message, state: FSMContext):
    data = await state.get_data()

    try:
        await bot.send_message(data['user_id'], data['text'])
        await message.answer("Сообщение успешно отправлено")
        await admin_menu(message, state)

    except:
        await message.answer("К сожалению, не удалось отправить. Попробуйте еще раз позже")
        await admin_menu(message, state)








