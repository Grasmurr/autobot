from telegram_bot.loader import dp, bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import \
    (Message,
     CallbackQuery,
     KeyboardButton,
     ReplyKeyboardMarkup,
     InlineKeyboardMarkup,
     InlineKeyboardButton,
     ReplyKeyboardRemove
     )
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F


from telegram_bot.service import api_methods
from telegram_bot.states import MainMenuStates


def create_keyboard_buttons(*args):
    builder = ReplyKeyboardBuilder()
    for i in args:
        builder.button(text=i)
    return builder.as_markup(resize_keyboard=True)


@dp.message(F.text == '/start')
async def main_menu(message: Message, state: FSMContext):
    buttons = create_keyboard_buttons('Узнать стоимость', 'Контакты')

    await message.answer(f'{message.from_user.full_name}, добро пожаловать в телегам-бот для '
                         f'расчета стоимости автомобиля!\n\nВыберите, что хотите сделать:',
                         reply_markup=buttons)


@dp.message(F.text == 'Контакты')
async def return_contacts(message: Message, state: FSMContext):
    await message.answer('Наши контакты:\n\nТелефон: +79..\nТелеграм: @username')


