from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class MainMenuStates(StatesGroup):
    user_main_menu = State()
    report_choose = State()
    enter_name_for_request = State()
    enter_number_for_request = State()