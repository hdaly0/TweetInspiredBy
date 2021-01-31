"""
Ocean HD
Jan 2020

Main method to run on server to load/train models and start twitter stream to reply to incoming tweets.
"""
from twitter_methods import pull_new_inbound_tweets


def main():
    """
    Main method to run in order to run the twitter bot
    :return: void
    """
    # Use the method to poll "mentions" of the associated twitter account as the streaming method has a bug
    pull_new_inbound_tweets()


if __name__ == "__main__":
    main()
