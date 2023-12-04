from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class MainMenuStates(StatesGroup):
    report_choose = State()