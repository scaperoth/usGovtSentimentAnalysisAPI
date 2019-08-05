# base.py
import re
import os
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

class TweetAnalysis(object):
	sentiment = 'neutral'
	subjectivity = 0

	def __init__(self, sentiment, subjectivity):
		self.sentiment = sentiment
		self.subjectivity = subjectivity

class TwitterGovtSentiment(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = os.environ['GOV_SENT_TWITTER_CONS_KEY']
        consumer_secret = os.environ['GOV_SENT_TWITTER_CONS_SECRET']

        # attempt authentication

        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)

            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A - Za - z0 - 9] +)|([^0-9A-Za-z \t]) | (\w + : \/\/\S+)", " ", tweet).split())

    def get_tweet_analysis(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))

        sentiment = 'neutral'
        subjectivity = analysis.sentiment.subjectivity

        # set sentiment
        if analysis.sentiment.polarity > 0:
            sentiment = 'positive'
        elif analysis.sentiment.polarity < 0:
            sentiment = 'negative'

        return TweetAnalysis(sentiment, subjectivity)

    def get_tweets(self, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count, show_user=False)
            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['analysis'] = self.get_tweet_analysis(
                    tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))
