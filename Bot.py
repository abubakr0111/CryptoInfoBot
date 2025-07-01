import telebot
from telebot import types
import feedparser
import requests
import xml.etree.ElementTree as ET

bot = telebot.TeleBot("7605831800:AAGBDlrFVzwMJIbShXxl5M2lzaIbxnuneUk")

# Источники новостей
decrypt_feed_url = "https://decrypt.co/feed"
us_news_feed_url = "https://www.npr.org/rss/rss.php?id=1014"

def parse_rss(url, limit=5):
    feed = feedparser.parse(url)
    entries = feed.entries[:limit]
    news = ""
    for entry in entries:
        news += f"• [{entry.title}]({entry.link})\n"
    return news if news else "Новостей не найдено."

def get_usd_to_rub():
    try:
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = requests.get(url)
        root = ET.fromstring(response.content)

        usd_rate = None
        for valute in root.findall('Valute'):
            if valute.find('CharCode').text == 'USD':
                value = valute.find('Value').text
                nominal = valute.find('Nominal').text
                usd_rate = float(value.replace(',', '.')) / float(nominal)
                break
        if usd_rate:
            return f"💵 Курс USD к RUB: {usd_rate:.4f} ₽"
        else:
            return "Ошибка: курс доллара не найден."
    except Exception as e:
        print("Ошибка при получении курса USD к RUB:", e)
        return "Ошибка при получении курса доллара."

def get_usd_to_tjs():
    try:
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = requests.get(url)
        root = ET.fromstring(response.content)

        usd_rate = None
        tjs_rate = None
        for valute in root.findall('Valute'):
            code = valute.find('CharCode').text
            if code == 'USD':
                value = valute.find('Value').text
                nominal = valute.find('Nominal').text
                usd_rate = float(value.replace(',', '.')) / float(nominal)
            elif code == 'TJS':
                value = valute.find('Value').text
                nominal = valute.find('Nominal').text
                tjs_rate = float(value.replace(',', '.')) / float(nominal)

        if usd_rate and tjs_rate:
            usd_to_tjs = usd_rate / tjs_rate
            return f"💵 Курс USD к TJS (сомони): {usd_to_tjs:.4f}"
        else:
            return "Ошибка: не удалось получить курс USD или TJS."
    except Exception as e:
        print("Ошибка при получении курса USD к TJS:", e)
        return "Ошибка при получении курса USD к TJS."

def get_memecoin_top():
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        response = requests.get(url)
        data = response.json()
        coins = data.get("coins", [])
        news = "🐒 Топ мемкоинов сейчас:\n"
        for coin in coins[:5]:
            item = coin.get("item", {})
            name = item.get("name", "Unknown")
            symbol = item.get("symbol", "")
            news += f"• {name} ({symbol})\n"
        return news if coins else "Нет данных по мемкоинам."
    except Exception:
        return "Ошибка при получении данных мемкоинов."

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('/crypto'),
               types.KeyboardButton('/dollar'),
               types.KeyboardButton('/memecoin'),
               types.KeyboardButton('/usnews'),
               types.KeyboardButton('/help'))
    bot.send_message(message.chat.id,
                     "Привет, Абубакр! Выбери тему новостей или данные:",
                     reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_message(message):
    text = ("Используй кнопки или команды:\n"
            "/crypto — последние новости криптовалют\n"
            "/dollar — курсы USD к RUB и USD к TJS\n"
            "/memecoin — топ мемкоинов\n"
            "/usnews — новости правительства США\n"
            "/help — помощь")
    bot.reply_to(message, text)

@bot.message_handler(commands=['crypto'])
def crypto_news(message):
    news = parse_rss(decrypt_feed_url)
    bot.send_message(message.chat.id, "📰 Свежие новости крипто:\n\n" + news, parse_mode="Markdown")

@bot.message_handler(commands=['dollar'])
def dollar_news(message):
    rate_usd_rub = get_usd_to_rub()
    rate_usd_tjs = get_usd_to_tjs()
    bot.send_message(message.chat.id, f"{rate_usd_rub}\n{rate_usd_tjs}")

@bot.message_handler(commands=['memecoin'])
def memecoin_news(message):
    news = get_memecoin_top()
    bot.send_message(message.chat.id, news)

@bot.message_handler(commands=['usnews'])
def us_news(message):
    news = parse_rss(us_news_feed_url)
    bot.send_message(message.chat.id, "🏛 Новости правительства США:\n\n" + news, parse_mode="Markdown")

bot.polling()
