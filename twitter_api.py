from datetime import datetime, timezone
import tweepy
import re
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def clean_text(text):
    """Removes all mentions (@username) and links in text"""
    text = re.sub(r'(@[A-Za-z0-9_]+)', '', text)
    text = re.sub('http://\S+|https://\S+', '', text)
    text = text.lstrip()
    return text

def get_sentiment(account_balance, doge_balance):
    """
    Returns the sentiment of a crypto related tweet (negative, neutral, positive) by performing sentiment 
    analysis on Elon Musk's 5 most recent tweets on his timeline
    """

    if account_balance > 0 or doge_balance > 0:
        # get Twitter API access keys and tokens
        with open("api_keys.txt", "r") as f:
            lines = f.read().splitlines()
            twitter_public_key, twitter_private_key = lines[2], lines[3]
            access_token, access_token_secret = lines[5], lines[6]
        
        authenticator = tweepy.OAuthHandler(twitter_public_key, twitter_private_key)
        authenticator.set_access_token(access_token, access_token_secret)
        api = tweepy.API(authenticator, wait_on_rate_limit=True)

        # sentiment analyzer
        sid = SentimentIntensityAnalyzer()

        # get current time in UTC
        now_utc = datetime.now(timezone.utc)

        # get the 5 latest tweets from Elon Musk's Twitter timeline
        tweets = api.user_timeline(screen_name="elonmusk", tweet_mode="extended", count=5)
        for tweet in tweets:
            text = clean_text(tweet.full_text)
            scores = sid.polarity_scores(text)["compound"]
            if scores != 0:
                delta_minutes = (now_utc - tweet.created_at).seconds // 60
                text = text.lower()
                if delta_minutes < 30 and ("crypto" in text or "stock" in text or "doge" in text or "bitcoin" in text):
                    return scores

    return 0
