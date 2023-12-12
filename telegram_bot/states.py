from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class MainMenuStates(StatesGroup):
    user_main_menu = State()
    report_choose = State()
