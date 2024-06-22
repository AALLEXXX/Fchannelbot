from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_menu_keyboard_builder() -> InlineKeyboardBuilder:
    key_builder = InlineKeyboardBuilder()
    key_builder.button(text="Получить доступ в закрытый чат", callback_data="get_closed_chat")

    key_builder.adjust(1)
    return key_builder