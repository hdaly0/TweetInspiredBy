"""
Ocean HD
Jan 2020

Main method to run on server to load/train models and start twitter stream to reply to incoming tweets.
"""
import logging
logger = logging.getLogger("MainLogger")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("logs/main.log", "w", "utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s: %(message)s"))
logger.addHandler(handler)


from twitter_methods import stream_incoming_tweets


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
            # Use streaming method to wait and reply to relevant tweets
            stream_incoming_tweets()
        except Exception as e:
            logger.exception({
                "message": "An Exception was raised during the continuous running of the program",
                "exception": str(e)
            })


if __name__ == "__main__":
    main()
