from telegram_bot.loader import dp, bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,

)
from aiogram import F

from telegram_bot.states import MainMenuStates
from telegram_bot.service.chat_backends import fetch_url

from bs4 import BeautifulSoup
import re


@dp.message(F.text == '/start')
async def load_url(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, укажите URL.")
    await state.set_state(MainMenuStates.report_choose)


def check_entered_url(url: str):
    if not url.startswith('http') or not url.startswith('https'):
        return 'Кажется, вы прислали не ссылку! Пожалуйста, пришлите ссылку, которая начинается на http или https'

    return 0


@dp.message(MainMenuStates.report_choose)
async def try_2(message: Message, state: FSMContext):
    url = message.text

    is_valid = check_entered_url(url)
    if is_valid != 0:
        await message.answer(is_valid)
        return

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

    characteristcs = ''
    keys = [i for i in car_data]
    values = [i for i in car_data.values()]
    for i in range(len(keys)):
        characteristcs += f'{keys[i]} {values[i]}\n'
    car_name = soup.title.string.split(' в городе ')[0]
    await message.answer(f'{car_name}')

    price_text = soup.find(text=re.compile("Брутто"))

    if price_text:
        price_match = re.search(r'(\d+\s*\d*\s*\d*)\s*€\s*\(*Брутто\)*', price_text)
        if price_match:
            price = price_match.group(1)
            print(f"Цена: {price} €")
    await message.answer(f'Название: {car_name}\n\nСтоимость: {price}€\n\n{characteristcs}')

