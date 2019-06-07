import tweepy
import pandas as pd
import json

# Getting credentials
with open("twitter_credentials.json", "r") as file:
    creds = json.load(file)
    
# Accessing the API
auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
api = tweepy.API(auth)

# Searching tweets
tweets = []
hashtags = []
varTimeline = api.home_timeline(count = 200, tweet_mode = 'extended')
for tweet in varTimeline:
    if(len(tweet.entities['hashtags']) > 0):
        hashtags.append(tweet.entities['hashtags'][0]['text'])
    tweets.append(tweet.full_text)
tweetFrame = pd.DataFrame(tweets)
tweetFrame.rename(index = str, columns = {0: 'Tweets'}, inplace = True)

# Function to convert contractions to its longer form
def decontracted(phrase):
    # specific
    phrase = re.sub(r"won\'t", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)

    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return phrase

# Cleaning tweets using regex
import re

clean_tweets = []
for index, row in tweetFrame.iterrows():
    clean_tweet = decontracted(row['Tweets'])
    regex = 'RT'
    clean_tweet = re.sub(regex, ' ', clean_tweet)
    regex = "(@_\w+)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"
    clean_tweet = re.sub(regex, ' ', clean_tweet)
    regex = 'https://t.co/Uuy0zOBCim'
    clean_tweet = re.sub(regex, '', clean_tweet)
    clean_tweet = re.sub('^\s*', '', clean_tweet)
    clean_tweets.append(clean_tweet)
    
cleanTweetFrame = pd.DataFrame(clean_tweets)
cleanTweetFrame.rename(index = str, columns = {0: 'Tweets'}, inplace = True)
    

# Analysing tweets  
from collections import Counter
counter_hashtags = Counter(hashtags)  
hashtag_count = pd.DataFrame(counter_hashtags.most_common(20))
hashtag_count.rename(index = str, columns = {0: 'Hashtag', 1: 'Frequency'}, inplace = True)
print(hashtag_count.to_string(index = False))
    
import matplotlib.pyplot as plt
from textblob import TextBlob
pos = 0
neg = 0    
neu = 0
sentiList = []
for index, row in cleanTweetFrame.iterrows():
    tweet = row['Tweets']
    analysis = TextBlob(tweet)
    sentiList.append(analysis.sentiment)
    if(analysis.sentiment[0] > 0):
        pos += 1
    elif(analysis.sentiment[0] < 0):
        neg += 1
    else:
        neu += 1
sentiFrame = pd.DataFrame(sentiList)
sentiFrame.hist(column = 'polarity')
print(f"Positive tweets: {pos} | Negative tweets: {neg} | Neutral Tweets: {neu}")
total = pos + neg + neu
print(f"Percentage of Positive tweets: {(pos/total)*100}%")
print(f"Percentage of Negative tweets: {(neg/total)*100}%")
print(f"Percentage of neutral tweets: {(neu/total)*100}%")
plt.pie([pos, neg, neu], labels = ['Positive', 'Negative', 'Neutral'], colors = ['Green', 'Red', 'Orange'], startangle=90, autopct='%.1f%%')
plt.show()