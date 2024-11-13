import praw
import requests
from bs4 import BeautifulSoup
import random
import os
import time
import logging
from dotenv import load_dotenv
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO)

# Reddit bot account 
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="FetchItBot/1.0 by u/FetchItForYou (Purpose: Fetch an image)",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

# Upload to Imgur
def upload_to_imgur(image_url):
    try:
        client_id = os.getenv("IMGUR_CLIENT_ID")
        headers = {"Authorization": f"Client-ID {client_id}"}
        image_data = requests.get(image_url).content
        response = requests.post(
            "https://api.imgur.com/3/upload",
            headers=headers,
            files={"image": image_data}
        )
        response.raise_for_status()
        data = response.json()
        return data['data']['link']
    except RequestException as e:
        logging.error(f"Error uploading image to Imgur: {e}")
        return None

# Get random image
def fetch_random_image(query):
    try:
        sanitized_query = ''.join(e for e in query if e.isalnum() or e.isspace())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={sanitized_query}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        img_tags = soup.find_all("img")
        img_urls = [img['src'] for img in img_tags[1:]]
        return random.choice(img_urls)
    except RequestException as e:
        logging.error(f"Error fetching random image for '{query}': {e}")
        return None

# Main
subreddit = reddit.subreddit("all")
for comment in subreddit.stream.comments(skip_existing=True):
    if f"u/{reddit.user.me()}" in comment.body.lower():
        request = comment.body.lower().split(f"u/{reddit.user.me()}")[1].strip()
        if "fetch me" in request:
            search_term = request.split("fetch me")[-1].strip()
            image_url = fetch_random_image(search_term)
            disclaimer = "\n\n---\n\nI am a bot. This action was performed automatically."
            if image_url:
                imgur_url = upload_to_imgur(image_url)
                if imgur_url:
                    comment.reply(f"Here’s a random image of {search_term}: ![Image]({imgur_url}){disclaimer}")
                    logging.info(f"Successfully posted image for: {search_term}")
                else:
                    comment.reply(f"Sorry, sI couldn't fetch an image of {search_term} at the moment.{disclaimer}")
                    logging.error(f"Failed to upload image for: {search_term}")
            else:
                comment.reply(f"Sorry, I couldn't fetch an image of {search_term} at the moment.{disclaimer}")
                logging.error(f"Failed to fetch image for: {search_term}")
            time.sleep(60)
