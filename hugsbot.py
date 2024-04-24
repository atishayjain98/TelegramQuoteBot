import os
import requests
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TOKEN = os.getenv("BOT_TOKEN")

# Base URL for the Telegram API
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Dictionary to store quotes
quotes = {}


# Function to send messages to Telegram
def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.post(url, params=params)
    return response.json()


# Command handler for /addq <person> <quote>
def add_quote(chat_id, args):
    if len(args) >= 2:
        person = args[0]
        quote = ' '.join(args[1:])
        if person.lower() in quotes:
            quotes[person.lower()].append(quote)
        else:
            quotes[person.lower()] = [quote]
        send_message(chat_id, "Quote added successfully!")
    else:
        send_message(chat_id, "Please provide both person and quote.")


# Command handler for /quote
def random_quote(chat_id):
    if not quotes:
        send_message(chat_id, "No quotes available.")
    else:
        person = random.choice(list(quotes.keys()))
        quote = random.choice(quotes[person])
        send_message(chat_id, f"{person}: {quote}")


# Command handler for /quote <person>
def specific_quote(chat_id, args):
    person = ' '.join(args).lower()  # Convert to lowercase
    if person in quotes:
        quote = random.choice(quotes[person])
        send_message(chat_id, f"{person}: {quote}")
    else:
        send_message(chat_id, "No quotes available for this person.")


# Function to handle incoming messages
def handle_message(update):
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]

        # Convert command to lowercase
        text_lower = text.lower()

        if text_lower.startswith("/addq"):
            add_quote(chat_id, text_lower.split()[1:])
        elif text_lower.startswith("/quote"):
            args = text_lower.split()[1:]
            if args:
                specific_quote(chat_id, args)
            else:
                random_quote(chat_id)


# Main function to listen for updates
def main():
    offset = None
    while True:
        url = BASE_URL + "getUpdates"
        params = {"offset": offset, "timeout": 60}
        response = requests.get(url, params=params)
        updates = response.json().get("result", [])

        if updates:
            for update in updates:
                handle_message(update)
                offset = update["update_id"] + 1


if __name__ == '__main__':
    main()
