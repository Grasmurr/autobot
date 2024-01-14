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


@dp.message(F.text == '/admin', F.from_user.id == ADMIN_ID)
async def admin_menu(message: Message, state: FSMContext):
    markup = create_keyboard_buttons("Отправить сообщение пользователям",
                                      "Выгрузить таблицу пользователей",
                                      "На панель юзера")
    await state.set_state(AdminStates.main)
    await message.answer('Добро пожаловать в админ-панель', reply_markup=markup)


@dp.message(AdminStates.main, F.text == 'На панель юзера')
async def back_from_main_menu(message: Message, state: FSMContext):
    await main_menu(message, state)

@dp.message(AdminStates.main, F.text == 'Отправить сообщение пользователям')
async def mailing_menu(message: Message, state: FSMContext):
    markup = create_keyboard_buttons("По ID",
                                     "Зарегистрированным пользователям",
                                     "Назад")
    await state.set_state(AdminStates.mailing_options)
    await message.answer('Как вы хотите отправить сообщение?', reply_markup=markup)

@dp.message(AdminStates.mailing_options, F.text == 'Назад')
async def back_from_mailing_options(message: Message, state: FSMContext):
    await admin_menu(message, state)
