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

from telegram_bot.service.api_methods import create_applicant, update_applicant_data, get_applicant

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
    try:
        await message.answer("Скоро вернемся! Расчет стоимости может занять до минуты")

        telegram_name = message.from_user.username
        if telegram_name is None:
            telegram_name = "Отсутствует"

        user_id = message.from_user.id

        url = message.text

        await state.update_data(url=url, telegram_name=telegram_name, user_id=user_id)

        global registration_year, mileage
        url = message.text
        await state.update_data(message=message)

        is_valid = check_entered_url(url)
        if is_valid != 0:
            await message.answer(is_valid)
            return

        url = message.text

        is_valid = check_entered_url(url)
        if is_valid != 0:
            await message.answer(is_valid)
            return

        response = await fetch_url(url)
        soup = BeautifulSoup(response, 'html.parser')

        car_data = {}

        lang = soup.html.get('lang')

        if lang == 'ru':
            car_name = soup.title.string

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

            registration_date = car_data.get('Первая регистрация', '')
            if registration_date and not check_car_age(registration_date):
                await message.answer('Машина старше пяти лет! На машины старше пяти лет высокая пошлина '
                                     'и их ввозить не выгодно.')
                await main_menu(message, state)


            netto_price = soup.find(class_="netto-price").text

            registration_year = datetime.strptime(car_data['Первая регистрация'], '%m/%Y').year if car_data['Первая регистрация'] else 'Отсутствует'
            mileage = car_data['Пробег'] if mileage else 'Отсутствует'
            registration_date = car_data['Первая регистрация']
            engine_volume = car_data['Объем двигателя']

            builder = InlineKeyboardBuilder()
            builder.button(text='Отправить заявку', callback_data=f'send_request')
            markup = builder.as_markup()

            await message.answer(
                f'<b>{car_name}</b>\n\n'
                f'<b>Год регистрации:</b> {registration_year}\n'
                f'<b>Пробег:</b> {mileage}\n\n'
                f'<b>Рассчитанная стоимость:</b> {netto_price}€',
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )

        else:
            car_name = soup.find('title').get_text()
            scripts = soup.find_all("script")
            kilometerstand = None
            for script in scripts:
                if script.string and '"mileage":' in script.string:
                    match = re.search(r'"mileage":\s*"([^"]+)"', script.string)
                    if match:
                        kilometerstand = match.group(1)
                        break

            netto_price_element = soup.find(attrs={"data-testid": "sec-price"})
            if netto_price_element:
                netto_price = netto_price_element.text
                print("Netto Price found with data-testid:", netto_price)
            else:
                scripts = soup.find_all("script")
                netto_price = None
                for script in scripts:
                    if script.string and '"price":' in script.string:
                        match = re.search(r'"price":\s*([0-9.]+)', script.string)
                        if match:
                            netto_price = match.group(1)
                            break

            kilometerstand = soup.find('div', id='mileage-v').get_text(strip=True) if soup.find('div', id='mileage-v') else "Отсутствует"
            erstzulassung_element = soup.find('div', id='firstRegistration-v')
            erstzulassung = datetime.strptime(erstzulassung_element.get_text(strip=True), '%m/%Y').year if erstzulassung_element else "Отсутствует"

            if erstzulassung != 'Отсутствует' and not check_car_age(erstzulassung):
                await message.answer('Машина старше пяти лет! На машины старше пяти лет высокая пошлина '
                                     'и их ввозить не выгодно.')
                await main_menu(message, state)

            builder = InlineKeyboardBuilder()
            builder.button(text='Отправить заявку', callback_data=f'send_request')
            markup = builder.as_markup()

            await message.answer(
                f'<b>{car_name}</b>\n\n'
                f'<b>Год регистрации:</b> {erstzulassung}\n'
                f'<b>Пробег:</b> {kilometerstand}\n\n'
                f'<b>Рассчитанная стоимость:</b> {netto_price}€',
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )

        await state.update_data(car_name=car_name, price=netto_price)
        data = await state.get_data()

        is_exist = await get_applicant(user_id=data['user_id'])

        if not is_exist or not is_exist['data']:
            await create_applicant(telegram_name=data['telegram_name'],
                                   user_id=data['user_id'],
                                   urls=[data['url']],
                                   name_from_user=None,
                                   telephone_number=None,
                                   request=False)
    except Exception as E:
        await message.answer('Кажется, что-то пошло не так! Попробуйте еще раз!')
        await bot.send_message(chat_id=305378717, text=f'Ссылка: {url}\n\nОшибка: {E}')


@dp.callback_query(lambda call: call.data == 'send_request', MainMenuStates.report_choose)
async def send_request_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_exist = await get_applicant(user_id=data['user_id'])

    request_value = is_exist['data'][0]["request"]

    print("ВНИМАНИЕ", request_value)
    if request_value:
        name = is_exist['data'][0]['name_from_user']
        telephone_number = is_exist['data'][0]['telephone_number']

        user_profile_link = f"<a href='tg://user?id={data['user_id']}'>{name}</a>"

        admin_id = ADMIN_ID
        await bot.send_message(admin_id, f"Новая заявка от пользователя <b>{user_profile_link}</b>!\n\n"
                                         f"<b>Контактный номер телефона:</b> {telephone_number}\n\n"
                                         f"<b>Модель:</b> {data['car_name']}\n\n"
                                         f"<b>Рассчитанная стоимость:</b> {data['price']} €\n\n"
                                         f"<a href='{data['url']}'>Ссылка</a>\n",
                               parse_mode=ParseMode.HTML)

        await state.get_data()

        urls = is_exist['data'][0]['urls']
        print(urls)
        urls.append(data['url'])
        print(urls)

        await update_applicant_data(
            user_id=data['user_id'],
            name_from_user=name,
            telephone_number=telephone_number,
            urls=urls,
            request=True
            )

        await callback.message.answer("Спасибо за заявку! Мы свяжемся с вами в ближайшее время")
        await state.clear()
        message = data['message']
        await main_menu(message, state)
    else:
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
                                   parse_mode=ParseMode.HTML, disable_web_page_preview=True)

            await state.update_data(request=True)
            await state.get_data()

            await update_applicant_data(
                                       user_id=data['user_id'],
                                       name_from_user=data['name'],
                                       telephone_number=data['telephone_number'],
                                       urls=[data['url']],
                                       request=True)

            await message.answer("Спасибо за заявку! Мы свяжемся с вами в ближайшее время")
            await main_menu(message, state)
