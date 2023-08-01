import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
from io import BytesIO

# Set up the Telegram bot
bot_token = '6084880964:AAFJfaQJYvXcUWotUXOCI5vQfFCzIGODY1A'
chat_id = '-1001944694630'
bot = telegram.Bot(token=bot_token)

# Set up the set to store the URLs
posted_urls = set()

# Scrape the NPR news page
url = 'https://www.npr.org/sections/news/'

async def scrape_npr_news():
    while True:
        try:
            # Scrape every 1 min
            """
            In this code, timeout=60 sets the timeout to 60 seconds. 
            This means that if the server does not respond within 60 seconds,
            the request will raise a Timeout exception.
            """
            response = requests.get(url, timeout=60)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the news article headlines, links, and images
            articles = soup.find_all('article', class_='item')
            for article in articles:
                Article_url = article.find('a')['href']
                headline = article.find('h2', class_='title').text.strip()
                image = article.find('img', class_='respArchListImg')
                detail = article.find('p',class_='teaser').text.strip()
                # Finding the image  and buffur the imag by pillow library
                if image:
                    image_url = image['src']
                    if not image_url.startswith('http'):
                        image_url = f"{url}{image_url}"
                    response = requests.get(image_url)
                    photo = BytesIO(response.content)
                else:
                    image_url = None
                    photo = None

                # Check if the article has already been posted
                if Article_url not in posted_urls:
                    caption = f"'{headline}'\n\n{detail}\n'Read more by the link down below'\n{Article_url}"
                    if photo:
                        await bot.send_photo(chat_id=chat_id, photo=photo.getvalue(), caption=caption)
                    else:
                        await bot.send_message(chat_id=chat_id, text=caption)

                    # Add the URL to the set of posted URLs
                    posted_urls.add(Article_url)

            # Sleep for 15 minutes
            '''
            function sleeps for 15 minutes after each scrape using asyncio.sleep(900)
            (900 seconds = 15 minutes).
            '''
            await asyncio.sleep(900)
        # Throw an error if the problem is network connection or url timedout 
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"HTTP request error: {e}")
            """
            blocks will now sleep for 1 minute (60 seconds) 
            before retrying after an HTTP or Telegram API error.
            """
            await asyncio.sleep(30)
        # Throw an error if the problem is telgram timed out 
        except telegram.error.TelegramError as e:
            print(f"Telegram API error: {e}")
            await asyncio.sleep(30)

if __name__ == '__main__':
    """
    asyncio is a Python module that provides infrastructure for writing single-threaded,
    asynchronous code using coroutines, event loops, and tasks.
    It allows you to write non-blocking, concurrent code that can handle many I/O-bound tasks efficiently.
    """
    asyncio.run(scrape_npr_news())
