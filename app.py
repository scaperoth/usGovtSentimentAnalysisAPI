# app.py
# Import necessary packages
from base import TwitterGovtSentiment
from flask import Flask
from flask_restful import Resource, reqparse, Api
from flask_caching import Cache
import os

# Instantiate a flask object
app = Flask(__name__)

# set up cache for routes and api fetch
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache_timeout = 300
if 'GOVE_SENT_CACHE_TIMEOUT' in os.environ:
	cache_timeout = os.environ['GOVE_SENT_CACHE_TIMEOUT']

# Instantiate Api object
api = Api(app)

twitterAnalysis = TwitterGovtSentiment(cache_timeout)

class CurrentSentiment(Resource):

    # Creating the get method
    @cache.cached(timeout=cache_timeout)
    def get(self):
        try:
            tweets = twitterAnalysis.get_tweets(query=os.environ['GOV_SENT_SEARCH'], count=100)
            # picking positive tweets from tweets
            ptweets = [tweet for tweet in tweets if tweet['analysis'].sentiment == 'positive']
            ntweets = [tweet for tweet in tweets if tweet['analysis'].sentiment == 'negative']

            tweet_subjectivity = 0
            for tweet in tweets:
                tweet_subjectivity += tweet['analysis'].subjectivity

            output = {}
            output['pos_perc'] = 100 * len(ptweets) / len(tweets)
            output['neg_perc'] = 100 * len(ntweets) / len(tweets)
            output['neu_perc'] = 100 * (len(tweets) - len(ntweets) - len(ptweets)) / len(tweets)
            output['subjectivity'] = tweet_subjectivity/len(tweets)
            return output
        except ValueError:
           return {'message': 'Sentiment not calculated', 'error': ValueError}


# Adding the URIs to the api
api.add_resource(CurrentSentiment, '/sentiment')

if __name__ == '__main__':
    # Run the applications
    app.run()
