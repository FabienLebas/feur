import requests
import urllib.parse
import json
import psycopg2
import tweepy
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os

def getTweets(searchedWord, nbOfTweetsToSearch): #nbOfTweetsToSearch min = 10, max = 100
    url = "https://api.twitter.com/2/tweets/search/recent?query="
    query = searchedWord + " -is:retweet -is:reply lang:fr"
    encodedQuery = urllib.parse.quote(query)
    myBearer = os.environ.get('TWITTER_BEARER')
    headers = {'Authorization': 'Bearer ' + myBearer}
    payload = {'max_results': nbOfTweetsToSearch, 'tweet.fields' : 'text'}
    response = requests.get(url + encodedQuery, headers=headers, params=payload)
    tweets = response.json()
    return tweets['data']

def tweetsEligible(searchedWord, tweets):
    result = []
    for tweet in tweets:
        if tweet['text'].endswith(searchedWord) or tweet['text'].endswith(searchedWord + "?") or tweet['text'].endswith(searchedWord + " ?") or tweet['text'].endswith(searchedWord + "!") or tweet['text'].endswith(searchedWord + " !") or tweet['text'].endswith(searchedWord + "." or tweet['text'].endswith(searchedWord + " ")):
            result.append(tweet)
    return result

def alreadyAnsweredTweets(tweetIds):
    dbUser = os.environ.get('DB_USER')
    dbPassword = os.environ.get('DB_PASSWORD')
    dbHost = os.environ.get('DB_HOST')
    dbPort = os.environ.get('DB_PORT')
    dbDatabase = os.environ.get('DB_DATABASE')
    connection = psycopg2.connect(user=dbUser, password=dbPassword, host=dbHost, port=dbPort, database=dbDatabase)
    cursor = connection.cursor()
    sql = "SELECT id FROM answered_tweets WHERE id IN %s"
    cursor.execute(sql, (tweetIds,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def removeAlreadyAsnweredTweets(fetchedTweets):
    previousAnswers = alreadyAnsweredTweets()
    result = []
    for tweet in fetchedTweets:
        if previousAnswers.count(tweet.id) == 0:
            result.append(tweet)
        else:
            print('Found duplicate' + tweet['id'])
    return result

def postViaTweepy(tweetID, myAnswer): #TODO : 433 - The original Tweet author restricted who can reply to this Tweet.
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    answer = api.update_status(status = myAnswer, in_reply_to_status_id = tweetID , auto_populate_reply_metadata=True)
    return answer

def saveIAnswered(tweetID, textOfTheOriginalTweet, myAnswer):
    dbUser = os.environ.get('DB_USER')
    dbPassword = os.environ.get('DB_PASSWORD')
    dbHost = os.environ.get('DB_HOST')
    dbPort = os.environ.get('DB_PORT')
    dbDatabase = os.environ.get('DB_DATABASE')
    connection = psycopg2.connect(user=dbUser, password=dbPassword, host=dbHost, port=dbPort, database=dbDatabase)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO answered_tweets (id, answered_tweet, answer_text) VALUES (%s, %s, %s)", (tweetID, textOfTheOriginalTweet, myAnswer))    
    connection.commit()
    cursor.close()
    connection.close()

def oneBatchOfAnswers(searchedWord, nbOfTweetsToSearch, myAnswer):
    fetchedTweets = getTweets(searchedWord, nbOfTweetsToSearch)
    tweetsEndingOK = tweetsEligible(searchedWord, fetchedTweets) 
    print("I have found " + str(len(tweetsEndingOK)) + " potentials : " + str(tweetsEndingOK))
    ids = []
    for tweet in tweetsEndingOK:
        ids.append(tweet['id'])
    alreadyAnsweredFromMyList = alreadyAnsweredTweets(tuple(ids))
    tweetsToAnswer = []
    for tweet in tweetsEndingOK:
        if tweet['id'] not in str(alreadyAnsweredFromMyList):
            tweetsToAnswer.append(tweet)
    for tweet in tweetsToAnswer:
        postViaTweepy(tweet['id'], myAnswer)
        saveIAnswered(tweet['id'], tweet['text'], myAnswer)
    print('tweetsToAnswer : ' + str(len(tweetsToAnswer)))
    print(tweetsToAnswer)
    
oneBatchOfAnswers('pourquoi', '100', 'Feur')
oneBatchOfAnswers('quoi', '100', 'Feur')
