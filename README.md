# @TweetInspiredBy Twitter Bot



## Introduction
This project is designed to be a twitter bot that will reply to tweets with text automatically generated from models trained on user-specified datasets.
The datasets are pre-defined but specified by users when they tweet at the bot.



## How to interact with this bot
To use this bot, simply tweet "@TweetInspiredBy" followed by the name of one or more of the predefined datasets.
Dataset names are not case sensitive but should all be separated by spaces and must be spelled correctly and must include any underscores specified in the dataset names.



## Currently included datasets

#### shakespeare
Specifically, this dataset currently includes just the bulk of the text of Romeo and Juliet.
##### Source: http://shakespeare.mit.edu/

#### trump
Specifically, all of the tweets from the @RealDonaldTrump account.
The dataset only includes the text from the tweets sent out from this account and not any retweets.
The dataset has been cleaned to remove any urls.
##### Source: https://www.thetrumparchive.com/faq

#### poetry
A selection of some of the most iconic English poetry, taken from a subset of a list from the source website.
##### Source: https://lithub.com/the-32-most-iconic-poems-in-the-english-language/

#### inspirational_quotes
A list of 100 inspirational quotes from various famous individuals.
##### Source: https://www.forbes.com/sites/kevinkruse/2013/05/28/inspirational-quotes/?sh=4b2e57eb6c7a

#### birthday
The text from a website talking about birthdays.
Can be combined with other datasets to get interesting birthday messages for friends.
This was the original starting point for this project - to create some interesting birthday messages for a friend inspired by our facebook chat history and some inspirational quotes.



## How to set up your own bot
This codebase should work on a computer/server with git, python3, and pip3 installed. Steps:

1. Clone this repo via e.g. `git clone ...`
1. Best practice would be to create a virtual environment inside the repo's folder.
Use something like pyenv or virtualenv.
For virtualenv, install it via `pip3 install virtualenv` and then create a virtual environment by running `virtualenv venv`.
Finally, activate the new environment (in unix based systems) by running `source venv/bin/activate`.
1. Pip install all requirements (either in your virtual environment or on the machine itself) by running `pip3 install -r requirements.txt`.
This should install all packages specified in the requirements.txt file, which are the libraries required to run the code.
1. To connect to twitter, the code pulls the various twitter api keys from the current machine's environment variables.
Whilst best practice would probably store these in some sort of secret vault (e.g. AWS Secrets Manager) and pull them in
at runtime or as part of the infrastructure setup, for simplicity I have left them to be set manually as the deployment of this code is also manual.
A twitter development account will need to be created, along with a new project and the following four keys generated:
    - API key
    - API secret key
    - Access token
    - Access token secret

    These keys should be saved as environment variables with the following names by running (in unix based systems):
    ```
    export TWITTER_API_KEY=<API key>
    export TWITTER_API_SECRET_KEY=<API secret key>
    export TWITTER_ACCESS_TOKEN=<Access token>
    export TWITTER_ACCESS_TOKEN_SECRET=<Access token secret>
    ```
    Information about setting up twitter apps and getting access to twitter apis: https://developer.twitter.com/en/docs/apps/overview
    
    Authentication is via OAuth 1.0a: https://developer.twitter.com/en/docs/authentication/oauth-1-0a
1. Finally, run the program by executing `python3 main.py` or,
to run the application as a background task (e.g. if you are running the application on a remote server and want to be able to close the connection without killing the application) run `nohup python3 main.py &`.

##### Notes:
- On some machines `python3` may be aliased (and accessed) as `python`, and `pip3` as `pip`.
- You can run just the markov model code (without any twitter streaming) for development and testing locally by running the `text_generation_methods.py` file only.
- This bot is 


## Notes on best practice
As a fun project, there are places I have strayed from best practice.
Notably, I have included the data and also trained models in the git repo.

The data was included for others to be able to take and use straight away with the markovify NewlineText training method without the need to clean any data.
In this way I hope to make it easier for others to get started with similar projects.

The models were included in the repo for computational efficiency when deploying the code.
I run the twitter bot on an AWS EC2 instance, specifically the one available for 12 months for free (T2.micro).
As such, the compute power of this machine is limited.
I therefore utilise my personal laptop's higher processing capabilities to train the models faster, save the results, and then just load the models on the EC2.

I have added a limit to the size of training data to be included in each model because the EC2 server I deploy to only has 1GB of RAM and this quickly fills up when there are several datasets present.
Deploying the Twitter bot on a machine with more memory would allow more models trained on more data.



## Notable libraries
This project is built using several libraries, but two in particular form the backbone of this code.
- **markovify**: A very simple and easy to use library to train markov models and do text generation. https://github.com/jsvine/markovify
- **Tweepy**: A library that provides quick setup and use of the various twitter apis to stream, pull, and send tweets. https://www.tweepy.org/

