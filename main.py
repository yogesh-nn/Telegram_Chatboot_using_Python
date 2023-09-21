import os
from dotenv import load_dotenv
import telegram
from telegram.ext import CommandHandler, MessageHandler, filters, Application
import openai
import g4f
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor()

load_dotenv()

# Set up openAI key from Environment Variables:
openai.api_key = os.getenv('OPENAI_KEY')

# Set up Telegram Bot Token from Environment Variables:
TOKEN = os.getenv("TG_BOT_TOKEN")



print(openai.api_key)
print(TOKEN)

def handle_message(message):
    response = g4f.ChatCompletion.create(
    model="gpt-3.5-turbo",
    provider=g4f.Provider.DeepAi,
    messages=[{"role": "user", "content": message}],
    )
    return response

async def start(update, context):
    first_name = update.message.chat.first_name

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Hello {}! Welcome to the AI Bot. How can I help you now ?".format(first_name)
    )

async def echo(update, context):
    message = update.message.text

    if os.getenv('OPENAI_KEY'):
        response = openai.Completion.create(
            engine = "text-davinci-002",
            promt = message,
            top_p = 1,
            frequency_penalty = 0,
            model="gpt-4",
            presence_penalty = 0,
            temperature=0,
            max_tokens=1000
        )

        if response:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = response.choices[0].text
            )
        else:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry! But please, share your Question one more time..."
            )

    else:
        response_future = executor.submit(handle_message, message)
        response = response_future.result()
        
        if response:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = response
            )

        else:
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Sorry! But please, share your Question one more time..."
            )


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("Start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Our AI Bot is running....")

    application.run_polling()

if __name__ == '__main__':
    main()