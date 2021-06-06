"""
Ocean HD
Jan 2020

Main method to run on server to load/train models and start twitter stream to reply to incoming tweets.
"""
import logging
import time


from twitter_methods import setup_tweepy_api, stream_incoming_tweets


# Setup logging
logger = logging.getLogger("MainLogger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/main.log", "w", "utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s: %(message)s"))
logger.addHandler(handler)


# Config
TIME_TO_WAIT_BEFORE_RETRY_ATTEMPT_AFTER_ERROR = 15


def main():
    """
    Main method to run in order to run the twitter bot
    :return: void
    """
    logger.info({
        "message": "Starting main program"
    })
    # Use the method to poll "mentions" of the associated twitter account as the streaming method has a bug
    # pull_new_inbound_tweets()

    # Run commands in a loop to retry if an error occurs
    while True:
        logger.info({"message": "Inside the continuous while loop"})
        try:
            # Set up a tweepy api
            api = setup_tweepy_api()
            # Use streaming method to wait and reply to relevant tweets
            stream_incoming_tweets(api)
        except Exception as e:
            logger.exception({
                "message": "An Exception was raised during the continuous running of the program",
                "exception": str(e)
            })
            # Wait specified amount of time before trying to reconnect to twitter
            logger.info({"message": f"Waiting {TIME_TO_WAIT_BEFORE_RETRY_ATTEMPT_AFTER_ERROR}s before retrying to setup new tweepy api and message stream"})
            time.sleep(TIME_TO_WAIT_BEFORE_RETRY_ATTEMPT_AFTER_ERROR)


if __name__ == "__main__":
    main()
