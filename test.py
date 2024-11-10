import praw
from dotenv import load_dotenv
import os

load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="FetchItBot v1.0 (by u/FetchItForYou)",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

try:
    print(f"Logged in as: {reddit.user.me()}")
except Exception as e:
    print(f"Error: {e}")