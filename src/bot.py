import os
from typing import Dict

from dotenv import load_dotenv
from telegram import Message, Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler, ContextTypes

from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_photo, send_text_buttons, show_main_menu, \
    dialog_user_info_to_str

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHATGPT_API_TOKEN = os.getenv("CHATGPT_API_TOKEN")


class Dialog:
    def __init__(self):
        self.mode: str = ""
        self.list: list[str] = []
        self.count: int = 0
        self.user: Dict[str, str] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dialog.mode = "main"
    text: str = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await show_main_menu(update, context, {
        "start": "main menu",
        "profile": "Tinder-profile generation 😎",
        "opener": "Message for dating 🥰",
        "message": "Correspondence on your behalf 😈",
        "date": "Correspondence with the stars 🔥",
        "gpt": "Talk with GPT 🧠"
    })


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    dialog.mode = "gpt"
    text: str = load_message("gpt")
    await send_photo(update, context, "gpt")
    return await send_text(update, context, text)


async def gpt_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    text: str = update.message.text
    prompt: str = load_prompt("gpt")
    answer: str = await chatgpt.send_question(prompt, text)
    return await send_text(update, context, answer)


async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    dialog.mode = "date"
    text: str = load_message("date")
    await send_photo(update, context, "date")
    return await send_text_buttons(update, context, text, {
        "date_grande": "Ariana Grande",
        "date_robbie": "Margot Robbie",
        "date_zendaya": "Zendaya",
        "date_gosling": "Ryan Gosling",
        "date_hardy": "Tom Hardy",
    })


async def date_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    text: str = update.message.text
    my_message: Message = await send_text(update, context, "Typing...")
    answer: str = await chatgpt.add_message(text)
    return await my_message.edit_text(answer)


async def date_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query: str = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, "Congratulations, great choice")
    prompt: str = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dialog.mode = "message"
    text: str = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next": "Next message",
        "message_date": "Invite to date"
    })
    dialog.list.clear()


async def message_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query: str = update.callback_query.data
    await update.callback_query.answer()
    prompt: str = load_prompt(query)
    user_chat_history: str = "\n\n".join(dialog.list)
    my_message: Message = await send_text(update, context, "ChatGPT is thinking...")
    answer: str = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


async def message_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text: str = update.message.text
    dialog.list.append(text)


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dialog.mode = "profile"
    text: str = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "How old are you")


async def profile_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    dialog.count += 1
    text: str = update.message.text

    if dialog.count == 1:
        dialog.user["age"] = text
        return await send_text(update, context, "Who do you work for?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        return await send_text(update, context, "Do you have a hobby?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        return await send_text(update, context, "What don't you like in people?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        return await send_text(update, context, "Purpose of dating?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt: str = load_prompt("profile")
        user_info: str = dialog_user_info_to_str(dialog.user)
        my_message: Message = await send_text(update, context, "GPT is thinking...")
        answer: str = await chatgpt.send_question(prompt, user_info)
        return await my_message.edit_text(answer)


async def opener(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dialog.mode = "opener"
    text: str = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "His/her name?")


async def opener_dialogue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    dialog.count += 1
    text: str = update.message.text

    if dialog.count == 1:
        dialog.user["name"] = text
        return await send_text(update, context, "His/her age?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        return await send_text(update, context, "Rate his/her appearance: 1-10")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        return await send_text(update, context, "What is his/her job?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        return await send_text(update, context, "His/her purpose of dating?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt: str = load_prompt("opener")
        user_info: str = dialog_user_info_to_str(dialog.user)
        my_message: Message = await send_text(update, context, "GPT is thinking...")
        answer: str = await chatgpt.send_question(prompt, user_info)
        return await my_message.edit_text(answer)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if dialog.mode == "gpt":
        await gpt_dialogue(update, context)
    elif dialog.mode == "date":
        await date_dialogue(update, context)
    elif dialog.mode == "message":
        await date_dialogue(update, context)
    elif dialog.mode == "profile":
        await profile_dialogue(update, context)
    elif dialog.mode == "opener":
        await opener_dialogue(update, context)
    else:
        await send_text(update, context, "*Hi*")
        await send_text(update, context, "_Hi_")
        await send_text(update, context, "Your message: " + update.message.text)
        await send_photo(update, context, "avatar_main")
        await send_text_buttons(update, context, "Start process?", {
            "start": "START",
            "stop": "STOP"
        })


async def hello_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query: str = update.callback_query.data
    if query == "start":
        await send_text(update, context, "Process Started")
    else:
        await send_text(update, context, "Process Stopped")


dialog = Dialog()
chatgpt = ChatGptService(token=CHATGPT_API_TOKEN)


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gpt", gpt))
    app.add_handler(CommandHandler("date", date))
    app.add_handler(CommandHandler("message", message))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("opener", opener))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

    app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
    app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
    app.add_handler(CallbackQueryHandler(hello_buttons))

    app.run_polling()


if __name__ == "__main__":
    main()
