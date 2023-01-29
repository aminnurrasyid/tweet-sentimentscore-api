import flask
from flask import Flask, request, jsonify
import tweepy
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def API():

    api_key = "uf5tDna15YxoCg3gMA0xUC2eP"
    api_key_secret = "AsOVMaORetoiawmvIOnRa4VuOmXFJ1HctpINtuMZr37WBepQjl"
    access_token = "4671014724-f60ozSGu70gOHA8RGRQ13lksXFCkzOVLwUSBS9g"
    access_token_secret = "3qrsEf6KS0QDz9FFW7iDttQBX6LurEQ9szpMSUB380EsR"

    # authentication
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    user_query = str(request.args['Query'])
    keywords = user_query + '-filter:retweets'
    limit = 200 

    public_tweets = tweepy.Cursor(api.search_tweets, count=limit, q=keywords, lang='en').items(limit)

    with open('negative.txt', 'r') as f:
        neg_words = f.read().split()
    with open('positive.txt', 'r') as f:
        pos_words = f.read().split()
    with open('negation.txt', 'r') as f:
        negation_words = f.read().split()
    with open('booster_inc.txt', 'r') as f:
        multinc_words = f.read().split()
    with open('booster_decr.txt', 'r') as f:
        multdec_words = f.read().split()

    lemma = WordNetLemmatizer()
    def text1_prep(x: str) -> list:
        corp = str(x).lower()
        corp = corp.strip('!"#$%&()*+,-./:;<=>?@[\\]^_{|}~')
        tokens = corp.split(' ')
        lemmatize = [lemma.lemmatize(w) for w in tokens]
        return lemmatize

    stop_words = stopwords.words('english')
    def text2_prep(x: str) -> list:
        corp = str(x).lower()
        corp = re.sub('[^a-zA-Z]+',' ', corp).strip()
        tokens = word_tokenize(corp)
        words = [t for t in tokens if t not in stop_words]
        lemmatize = [lemma.lemmatize(w) for w in words]
        return lemmatize

    def get_negated(magnitude, negation_bool):
        negated = magnitude*-1 if negation_bool else magnitude
        return negated

    def get_scalar1(negated, multi_low_bool):
        scalar1 = negated*0.5 if multi_low_bool else negated 
        return  scalar1 

    def get_scalar2(scalar1, multi_high_bool):
        scalar2 = scalar1*1.5 if multi_high_bool else scalar1 
        return scalar2 

    def get_sentiment(scalar2):
        sentiment = []
        for i in scalar2:
            if i>0:
                sentiment.append("Positive")
            elif i<0:
                sentiment.append("Negative")
            else:
                sentiment.append("Neutral")
        return sentiment

    def get_overallScore(score):
        n = len(score)
        return round(sum(score)/n,2)


    # create dataframe
    tweets = []
    for tweet in public_tweets:
        tweets.append((tweet.text).encode("utf-8"))

    df = pd.DataFrame(tweets, columns= ['tweet'])
    df['preprocess_txt1'] = df['tweet'].map(lambda x: text1_prep(x))
    df['preprocess_txt2'] = df['tweet'].map(lambda x: text2_prep(x))
    df['total_len'] = df['preprocess_txt2'].map(lambda x: len(x))
    df['positive_count'] = df['preprocess_txt2'].map(lambda x: len([i for i in x if i in pos_words]))
    df['negative_count'] = df['preprocess_txt2'].map(lambda x: len([i for i in x if i in neg_words]))
    df['negation_bool'] = df['preprocess_txt1'].map(lambda x: any([i for i in x if i in negation_words]))
    df['multi_low_bool'] = df['preprocess_txt1'].map(lambda x: any([i for i in x if i in multdec_words]))
    df['multi_high_bool'] = df['preprocess_txt1'].map(lambda x: any([i for i in x if i in multinc_words]))
    df['magnitude'] = df['positive_count']-df['negative_count']
    df['negated'] = df.apply(lambda x: get_negated(x.magnitude, x.negation_bool), axis=1)
    df['scalar1'] = df.apply(lambda x: get_scalar1(x.negated, x.multi_low_bool), axis=1)
    df['scalar2'] = df.apply(lambda x: get_scalar2(x.scalar1, x.multi_high_bool), axis=1)
    df['Sentiment'] = get_sentiment(df['scalar2'])
    df['Sentiment Score'] = round(df['scalar2']/df['total_len'],2)

    sentiment_score = get_overallScore(df['Sentiment Score'])
    str_tweets = df['tweet'].tolist() #str() wrap

    
    record_dictionary={}
    record_dictionary['Query']= user_query
    record_dictionary['tweets']= str_tweets
    record_dictionary['score']= sentiment_score
    json_record=[]
    json_record.append(record_dictionary)
    return jsonify(json_record)
