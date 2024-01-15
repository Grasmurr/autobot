from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class MainMenuStates(StatesGroup):
    user_main_menu = State()
    report_choose = State()
    enter_name_for_request = State()
    enter_number_for_request = State()

class AdminStates(StatesGroup):
    main = State()

    mailing_options = State()

    mailing_id_enter = State()
    mailing_id_confirm_user = State()
    mailing_id_enter_message_text = State()
    mailing_id_сonfirm_message_text = State()

    begin_mailing = State()
    mailing_with_text = State()
    mailing_with_file = State()
    mailing_with_photo = State()

    upload_data = State()
    upload_data_in_format_final = State()




