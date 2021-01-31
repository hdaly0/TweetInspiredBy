"""
Ocean HD
Jan 2020

Methods to deal with connecting to twitter, retrieving tweets, getting relevant info from tweets, and replying to tweets
"""
# Imports
import os
from text_generation_methods import generate_text_from_specified_datasets
from custom_exceptions import NoMatchingDatasetsException
import tweepy
import time
import re

import logging
logger = logging.getLogger("TweetLogger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/twitter.log", "w", "utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s: %(message)s"))
logger.addHandler(handler)

# Pull config from environment variables
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Authenticate to twitter
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Get API
api = tweepy.API(auth)

# Define regex to only match standard characters and underscore
regex_matching_pattern = "[^a-zA-Z0-9_ ]"
regular_character_matcher = re.compile(regex_matching_pattern)

# Define max length of text to generate based on tweet length limits
MAX_TWEET_LENGTH = 280
MAX_USERNAME_LENGTH = 15
EXTRA_CHARACTERS_REQUIRED = 2 # @ and a space
MAX_GENERATED_TEXT_LENGTH = MAX_TWEET_LENGTH - MAX_USERNAME_LENGTH - EXTRA_CHARACTERS_REQUIRED

# For the method pulling "mentions" define time to wait between each poll
TIME_TO_WAIT_BEFORE_PULLING_NEW_TWEETS = 15


def remove_non_standard_characters_regex(text):
    return regular_character_matcher.sub("", text).lower()


def manage_inbound_tweet(status):
    status_id = status.id
    text = status.text
    screen_name = status.user.screen_name

    clean_text = remove_non_standard_characters_regex(text)
    try:
        response_text = generate_text_from_specified_datasets(clean_text, MAX_GENERATED_TEXT_LENGTH)
    except NoMatchingDatasetsException:
        response_text = "No matching datasets found"

    response_text = f"@{screen_name} {response_text}"

    logger.info({"tweet_in_id": status_id,
                 "tweet_in_text": text,
                 "cleaned_tweet_in_text": clean_text,
                 "tweet_in_user": screen_name,
                 "response_out": response_text})

    original_tweet_url = f"https://twitter.com/{screen_name}/status/{status_id}"
    api.update_status(status=response_text, attachment_url=original_tweet_url)


def pull_new_inbound_tweets():
    latest_id = 1
    while True:
        mentions = api.mentions_timeline(since_id=latest_id)
        # TODO: parallelise
        for status in mentions:
            print(status)
            manage_inbound_tweet(status)
            latest_id = status.id
        time.sleep(TIME_TO_WAIT_BEFORE_PULLING_NEW_TWEETS)


def stream_incoming_tweets():
    class botStreamListener(tweepy.StreamListener):
        def on_status(self, status):
            manage_inbound_tweet(status)

        def on_error(self, status_code):
            if status_code == 420:
                # returning False in on_error disconnects the stream
                return False

    stream_listener = botStreamListener()
    inbound_stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    # TODO: This has a BUG because it replies to it's own posts... gets into a loop
    inbound_stream.filter(track=["@TweetInspiredBy"])

# Test connection
# api.update_status("test tweet")
