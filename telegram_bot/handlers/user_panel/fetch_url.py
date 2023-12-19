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


from telegram_bot.states import MainMenuStates
from telegram_bot.service.chat_backends import fetch_url, create_keyboard_buttons

from telegram_bot.handlers.user_panel.main_menu import main_menu
from telegram_bot.assets.config import ADMIN_ID

from bs4 import BeautifulSoup
import re
from datetime import datetime


@dp.message(MainMenuStates.user_main_menu, F.text == 'Узнать стоимость')
async def load_url(message: Message, state: FSMContext):
    markup = create_keyboard_buttons("Назад")
    await message.answer("Пожалуйста, пришлите ссылку на интересующую вас модель",
                         reply_markup=markup)
    await state.set_state(MainMenuStates.report_choose)


@dp.message(MainMenuStates.report_choose, F.text == 'Назад')
async def back_from_load_url(message: Message, state: FSMContext):
    await main_menu(message, state)

def check_entered_url(url: str):
    if not url.startswith('http') or not url.startswith('https'):
        return ('Кажется, вы прислали не ссылку! Пожалуйста, пришлите ссылку, '
                'которая начинается на http или https')

    return 0


def check_car_age(registration_date):
    registration_datetime = datetime.strptime(registration_date, "%m/%Y")
    current_datetime = datetime.now()
    years_difference = current_datetime.year - registration_datetime.year

    if current_datetime.month < registration_datetime.month or (
            current_datetime.month == registration_datetime.month and current_datetime.day < registration_datetime.day):
        years_difference -= 1

    if years_difference > 5:
        return False
    else:
        return True

@dp.message(MainMenuStates.report_choose)
async def try_2(message: Message, state: FSMContext):
    url = message.text

    is_valid = check_entered_url(url)
    if is_valid != 0:
        await message.answer(is_valid)
        return

    await message.answer("Скоро вернемся! Расчет стоимости может занять до 10 минут")

    await state.update_data(url=url)

    response = await fetch_url(url)
    await message.reply(f"Размер HTML: {len(response)} символов.")
    soup = BeautifulSoup(response, 'html.parser')
    print(soup)

    car_data = {}

    attribute_blocks = soup.find_all("div", class_="g-row")

    for block in attribute_blocks:
        spans = block.find_all('span')
        if len(spans) >= 2:
            key = spans[0].get_text(strip=True)
            value = spans[1].get_text(strip=True)
            car_data[key] = value

        p_tags = block.find_all('p', class_='bullet-point-text')
        for p in p_tags:
            feature = p.get_text(strip=True)
            car_data[feature] = "Да"

    print (car_data['Первая регистрация'])

    registration_date = car_data.get('Первая регистрация', '')
    if not check_car_age(registration_date):
        await message.answer('Машина старше пяти лет! На машины старше пяти лет высокая пошлина '
                             'и их ввозить не выгодно.')
        await main_menu(message, state)
    else:
        characteristcs = ''
        keys = [i for i in car_data]
        values = [i for i in car_data.values()]
        for i in range(len(keys)):
            characteristcs += f'{keys[i]} {values[i]}\n'
        car_name = soup.title.string.split(' в городе ')[0]
        await message.answer(f'{car_name}')

        price_text = soup.find(text=re.compile("Брутто"))
        print (characteristcs)

        if price_text:
            price_match = re.search(r'(\d+\s*\d*\s*\d*)\s*€\s*\(*Брутто\)*', price_text)
            if price_match:
                price = price_match.group(1)
                print(f"Цена: {price} €")

        builder = InlineKeyboardBuilder()
        builder.button(text='Отправить заявку', callback_data=f'send_request')
        markup = builder.as_markup()

        await state.update_data(car_name=car_name, price=price)

        await message.answer(
            f'Название: {car_name}\n\nСтоимость: {price}€\n\n{characteristcs}',
            reply_markup=markup
        )


@dp.callback_query(lambda call: call.data == 'send_request', MainMenuStates.report_choose)
async def send_request_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MainMenuStates.enter_name_for_request)
    await callback.message.answer("Пожалуйста, введите ваше имя")

@dp.message(MainMenuStates.enter_name_for_request)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(MainMenuStates.enter_number_for_request)
    markup = create_keyboard_buttons("Назад")
    await message.answer(f"Спасибо, {message.text}! Теперь введите ваш контактный номер телефона",
                         reply_markup=markup)


def check_phone_number(telephone_number):
    input_string = re.sub(r'\D', '', telephone_number)
    if len(input_string) == 11:
        return True
    else:
        return False


@dp.message(MainMenuStates.enter_number_for_request)
async def process_phone(message: Message, state: FSMContext):

    user_id = message.from_user.id
    await state.update_data(user_id=user_id)

    telephone_number = message.text

    if telephone_number == "Назад":
        await load_url(message, state)

    else:
        if not check_phone_number(telephone_number):
            await message.answer("Кажется, вы отправили не номер телефона! "
                                 "Проверьте, пожалуйста, количество цифр")
            return

        else:
            telephone_number = re.sub(r'\D', '', telephone_number)
            await state.update_data(telephone_number=telephone_number)
            data = await state.get_data()

            user_profile_link = f"<a href='tg://user?id={user_id}'>{data['name']}</a>"

            admin_id = ADMIN_ID
            await bot.send_message(admin_id, f"Новая заявка от пользователя <b>{user_profile_link}</b>!\n\n"
                                             f"<b>Контактный номер телефона:</b> {data['telephone_number']}\n\n"
                                             f"<b>Модель:</b> {data['car_name']}\n\n"
                                             f"<b>Рассчитанная стоимость:</b> {data['price']} €\n\n"
                                             f"<a href='{data['url']}'>Ссылка</a>\n",
                                   parse_mode=ParseMode.HTML)

            await message.answer("Спасибо за заявку! Мы свяжемся с вами в ближайшее время")
            await main_menu(message, state)
