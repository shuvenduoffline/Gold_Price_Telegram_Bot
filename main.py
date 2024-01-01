import requests
import re
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Constants
API_KEY = 'YOUR_API_KEY'

BOT_USER_NAME = 'paper_gold_rate_bot'


def get_html_content(url):
    """Retrieves the HTML content of a given webpage.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str: The raw HTML content of the webpage, or None if an error occurs.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for error status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML content: {e}")
        return None


def get_divs_by_class(html_content, class_name):
    """Retrieves all div elements with the specified class name from the HTML content.

    Args:
        html_content (str): The raw HTML content of the webpage.
        class_name (str): The name of the class to search for.

    Returns:
        list: A list of BeautifulSoup Tag objects representing the div elements with the class name.
    """

    soup = BeautifulSoup(html_content, "html.parser")
    return soup.find_all("div", class_=class_name)

def get_first_table_in_div(html_content, div_class_name):
    """Retrieves the first table element within a div with the specified class name.

    Args:
        html_content (str): The raw HTML content of the webpage.
        div_class_name (str): The name of the class to search for in the div.

    Returns:
        BeautifulSoup Tag object: The first table element found within a matching div, or None if not found.
    """

    soup = BeautifulSoup(html_content, "html.parser")
    target_div = soup.find("div", class_=div_class_name)

    if target_div:
        first_table = target_div.find("table")
        return first_table
    else:
        return None

def get_todays_gold_rate():
    # Example usage:
    url = "https://www.anandabazar.com/business/today-gold-price-in-kolkata"  # Replace with the actual URL you want to fetch
    html_content = get_html_content(url)

    table = get_first_table_in_div(html_content, "tpricetable01")

    # print(table)  # Print the text content of each div

    # Access the last td element:
    last_td = table.find_all("tr")[-1].find_all("td")[-1];

    # Access the text content of the last td:
    last_td_text = last_td.text.strip()

    match = re.search(r"(.*?)₹", last_td_text)
    if match:
        todays_gold_rate = match.group(1).strip()
        return todays_gold_rate
    else:
        print("No ₹ symbol found in the text.")
    return "Unable to find rate"



async def start_command(update : Update, context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, Welcome to Gold Paper rate tracking bot')

async def help_command(update : Update, context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Simple to use price checking bot')

async def todays_price_command(update : Update, context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Todays Anadabazar Kolkata 22k Gold Rate is ' +  get_todays_gold_rate() + " inr.")

# Responses
def handle_response(text):
    processed = text.lower();
    if 'gold rate' in processed:
        return "Todays Anadabazar Kolkata 22k Gold Rate is " + get_todays_gold_rate() + " inr.";
    return 'I do not understand what you saying...'

async def handle_message(update : Update, context : ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type} : "{text}"')

    if message_type == 'group':
        if BOT_USER_NAME in text:
            response = handle_response(text)
        else:
            return
    else:
        response = handle_response(text)
    
    print('Bot : ', response)
    await update.message.reply_text(response)

async def error(update : Update, context : ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(API_KEY).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('todays_gold_rate', todays_price_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)