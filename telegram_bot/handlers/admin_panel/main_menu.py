from telegram_bot.loader import dp, bot
#
# @dp.message(F.text == '/admin', F.from_user.id == config.ADMIN_ID)
# async def admin_menu(message: Message, state: FSMContext):
#     markup = chat_backends.create_keyboard_buttons("Управление мероприятиями",
#                                                    "Оформить возврат",
#                                                    "Cделать выгрузку данных",
#                                                    "Рассылка",
#                                                    "Назад")
#     await state.set_state(AdminStates.main)
#     await message.answer('Добро пожаловать в админ-панель', reply_markup=markup)
#
#
# @dp.message(AdminStates.main, F.text == 'Назад')
# async def back_from_main_menu(message: Message, state: FSMContext):
#     await main_menu.promouter_menu(message, state)