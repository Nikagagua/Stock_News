import requests
from twilio.rest import Client
from dotenv import load_dotenv
import datetime as dt
import os

STOCK: str = "TSLA"
COMPANY_NAME: str = "Tesla Inc"

load_dotenv('.env')

alpha_api_key: str = os.getenv('ALPHA_API_KEY')

alpha_url = 'https://www.alphavantage.co/query'
alpha_params = {
    'function': 'TIME_SERIES_INTRADAY',
    'symbol': 'IBM',
    'interval': '60min',
    'apikey': alpha_api_key,
}

alpha_response = requests.get(url=alpha_url, params=alpha_params)
alpha_data = alpha_response.json()

today = dt.datetime.today()
day_of_today = today.day

stock_date: list = []
stock_close: list = []
for key, value in alpha_data.items():
    for k, v in value.items():
        stock_date.append(k)
        stock_close.append(v)

close_data_list: list = stock_close[6:]
data_close: list = []

for i in range(len(close_data_list)):
    data = close_data_list[i]['4. close']
    data_close.append(data)

yesterday = today - dt.timedelta(days=1)
day_before_yesterday = today - dt.timedelta(days=2)

yesterday_close = None
day_before_y_close = None

for i, data_str in enumerate(stock_date[6:]):
    date = dt.datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
    if date.date() == yesterday.date():
        yesterday_close = float(data_close[i])
    elif date.date() == day_before_yesterday.date():
        day_before_y_close = float(data_close[i])

difference: float = abs(yesterday_close - day_before_y_close)
percentage_change: float = round(difference / day_before_y_close * 100 if day_before_y_close else None, 2)
print(percentage_change)

news_url = 'https://newsapi.org/v2/everything'
news_api_key: str = os.getenv('NEWS_API_KEY')
news_params = {
    'q': COMPANY_NAME,
    'apiKey': news_api_key,
    'language': 'en',
    'from': day_before_yesterday.strftime('%Y-%m-%d'),
    'to': today.strftime('%Y-%m-%d'),
    'sortBy': 'relevancy',
    'title': STOCK,
    'description': STOCK,
}

news_response = requests.get(url=news_url, params=news_params)
news_data = news_response.json()

sliced_news_data: list = news_data['articles'][:3]

new_data_title = []
new_data_desc = []

if percentage_change <= 5:
    for i in range(len(sliced_news_data)):
        new_data_title.append(sliced_news_data[i]['title'])
        new_data_desc.append(sliced_news_data[i]['description'])

twilio_auth_token: str = os.getenv('AUTH_TOKEN')
account_ssid: str = os.getenv('ACCOUNT_SSID')
twilio_phone_number: str = os.getenv('PHONE_NUMBER')
my_phone_number: str = os.getenv('MY_PHONE_NUMBER')

if percentage_change >= 0:
    client = Client(account_ssid, twilio_auth_token)
    message = client.messages \
        .create(
        body=f"TSLA: 🔺{percentage_change}\n"
             f"Headline: {new_data_title[0]}\n"
             f"Brief: {new_data_desc[0]}",
        from_=twilio_phone_number,
        to=my_phone_number,
    )
elif percentage_change <= 5:
    client = Client(account_ssid, twilio_auth_token)
    message = client.messages \
        .create(
        body=f"TSLA: 🔻{percentage_change}\n"
             f"Headline: {new_data_title[0]}\n"
             f"Brief: {new_data_desc[0]}",
        from_=twilio_phone_number,
        to=my_phone_number,
    )
