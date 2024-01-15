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

from telegram_bot.service import api_methods
from telegram_bot.states import MainMenuStates

from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

import asyncio, time

from selenium.webdriver.chrome.options import Options


def create_keyboard_buttons(*args):
    builder = ReplyKeyboardBuilder()
    for i in args:
        builder.button(text=i)
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


def get_page_source(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

    driver = webdriver.Remote(
        command_executor='http://selenium-chromium:4444/wd/hub',
        options=chrome_options
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    time.sleep(5)

    html = driver.page_source
    driver.quit()
    return html


async def fetch_url(url):
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        html = await loop.run_in_executor(executor, get_page_source, url)
        return html
