import mysql.connector as sql
import pandas as pd
import tweepy
from datetime import datetime

f = open("logs.txt", "a")
f.write(str(datetime.now()))
f.close()
db_connection = sql.connect(host='localhost', database='tweetwoot', user='root', password='426480ua')
c = db_connection.cursor()
ds = pd.read_sql("SELECT * FROM super_users", db_connection)
df = pd.read_sql("SELECT * FROM twitter_users", db_connection)
def runTime(df, ds):
    CONSUMER_KEY = 'foPgt4FTfPNPffEIDULlNdN45'
    CONSUMER_SECRET = 'xCO7Lcjh22ORCF7E1i8X602gwzc8peun203iDUO4HBKLKxNBnT'
    users = []
    super = []
    supertweet = []
    recenttweet = []
    for index, row in df.iterrows():
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(row['access_token'], row['access_secret'])
        user = tweepy.API(auth)
        users.append(user)
        recenttweet.append(row['lasttweet'])

    for index, row in ds.iterrows():
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(row['access_token'], row['access_secret'])
        user = tweepy.API(auth)
        super.append(user)
        supertweet.append(row['lasttweet'])
    i = 0;
    for x in users:
        try:    
            mostrecenttweet = x.user_timeline()[0]
            print(mostrecenttweet.text)
            xyz = mostrecenttweet.text
            if mostrecenttweet.id != recenttweet[i] and "RT" not in xyz:
                try:
                    name = x.auth.get_username()
                    c.execute("UPDATE twitter_users SET lasttweet=%s WHERE displayName='%s' " % (mostrecenttweet.id, name))
                    db_connection.commit()
                except tweepy.TweepError, e:
                    print(e)          
                print("ticl")
                for y in users:
                    if y != x:
                        try:
                            y.retweet(mostrecenttweet.id)
                        except tweepy.TweepError, e:
                            print(e)
    # updates lasttweet to the most recent tweet
            recenttweet[i] = mostrecenttweet.id
        except tweepy.TweepError, e:
            print(e)
        i = i + 1
    i = 0
    for x in super:
        try:    
            mostrecenttweet = x.user_timeline()[0] 
            print(mostrecenttweet.text)
            xyz = mostrecenttweet.text
            if mostrecenttweet.id != supertweet[i] and "RT" not in xyz:
                try:
                    name = x.auth.get_username()
                    c.execute("UPDATE super_users SET lasttweet=%s WHERE displayName='%s' " % (mostrecenttweet.id, name))
                    db_connection.commit()
                except tweepy.TweepError, e:
                    print(e)
                print("ticl")
                for y in users:
                    print("Rt")
                    try:
                        y.retweet(mostrecenttweet.id)
                    except tweepy.TweepError, e:
                        print(e)
            supertweet[i] = mostrecenttweet.id
        except tweepy.TweepError, e:
            print(e)
        i = i + 1
		
    return 1
runTime(df, ds)