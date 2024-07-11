import os
from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHATGPT_API_TOKEN = os.getenv("CHATGPT_API_TOKEN")


async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await show_main_menu(update, context, {
        "start": "main manu",
        "profile ": " Tinder-profile generation 😎",
        "opener ": "message for dating 🥰",
        "message": "correspondence on your behalf 😈",
        "date ": "correspondence with the stars 🔥",
        "gpt": "Talk with Gpt 🧠"
    })


async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)


async def gpt_dialogue(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)

    await send_text(update, context, answer)


async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_grande": "Ариана Гранде",
        "date_robbie": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том Харди ",
    })


async def date_dialogue(update, context):
    text = update.message.text

    my_message = await send_text(update, context, "Typing...")

    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)


async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(update, context, "congratulations, great choice")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def message(update, context):
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next": "Next message",
        "message_date": "Invite to date"
    })
    dialog.list.clear()


async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update, context, "ChatGPT is thinking...")

    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)


async def message_dialogue(update, context):
    text = update.message.text
    dialog.list.append(text)


async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "How old are you")


async def profile_dialogue(update, context):
    dialog.count += 1
    text = update.message.text

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "who do you work for?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "do you have hobby?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "what you don't like? in people?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "purpose of dating?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "GPT is thinking...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def opener(update, context):
    dialog.mode = "opener"

    text = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "his/her name?")


async def opener_dialogue(update, context):
    dialog.count += 1
    text = update.message.text

    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "his/her age?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "rate his/her appearance: 1-10")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "What is his/her job?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "his/her purpose of dating?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "GPT is thinking...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def hello(update, context):
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
        await send_text(update, context, "Your message " + update.message.text)

        await send_photo(update, context, "avatar_main")
        await send_text_buttons(update, context, "start process?", {
            "start": "START",
            "stop": "STOP"
        })


dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}


async def hello_buttons(update, context):
    query = update.callback_query.data
    if query == "start":
        await send_text(update, context, "Process Started")
    else:
        await send_text(update, context, "Process Stopped")

chatgpt = ChatGptService(token=CHATGPT_API_TOKEN)
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
