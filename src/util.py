from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, BotCommand, MenuButtonCommands, BotCommandScopeChat
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


# Converts a user object to a string
def dialog_user_info_to_str(user) -> str:
    result = ""
    map = {"name": "Имя", "sex": "Пол", "age": "Возраст", "city": "Город", "occupation": "Профессия", "hobby": "Хобби", "goals": "Цели знакомства",
           "handsome": "Красота, привлекательность в баллах (максимум 10 баллов)", "wealth": "Доход, богатство", "annoys": "В людях раздражает"}
    for key, name in map.items():
        if key in user:
            result += name + ": " + user[key] + "\n"
    return result


# Sends a text message to the chat
async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


# Sends a text message to the chat and adds buttons to it
async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: dict) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


# Sends a photo to the chat
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> Message:
    with open('../resources/images/' + name + ".jpg", 'rb') as photo:
        return await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)


# Displays the command and main menu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, language_code="en", scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)


# Loads a message from the ../resources/messages/ folder
def load_message(name):
    with open("../resources/messages/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()


# Loads a prompt from the ../resources/prompts/ folder
def load_prompt(name):
    with open("../resources/prompts/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()


class Dialog:
    pass
