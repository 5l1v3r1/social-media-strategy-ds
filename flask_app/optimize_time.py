import json 
import os
import tweepy

from datetime import date
import calendar

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Helper functions
def todays_date():
    """Returns today's date in UTC"""
    today = date.today()
    day = today.strftime("%b-%d-%Y").replace('-', ' ')
    my_date = date.today()
    return calendar.day_name[my_date.weekday()][:3] + ' ' + day

def min_bin (mins):
    """Bins the minutes of when our followers engage into 00 and 30"""
    l = []
    for _min in mins:
        if _min < 30:
            l.append('00')
        else:
            l.append('30')
    return l

class data_wrangling:
    
    # Definining api as a class variable (shared among all instances of the class) 
    api = tweepy.API(auth, wait_on_rate_limit=True)    
    
    def __init__(self, user_id, follower_count=10):
        # instance variables (unique for each instance of the class)
        self.user_id = user_id
        self.follower_count = follower_count
        
    def followers_ids(self):
        """Returns the first 10 ids of the user's followers"""
        followers_ids = api.followers_ids(self.user_id)
        return followers_ids
    
    def get_follower_data(self, followers_ids):
        
        times = []
        text = []

        # Loop through the follower_count (int) defined in instance
        for followers in followers_ids[:self.follower_count]:

            # Try and excepts statement to bipass an error that arises when we call a protected user's information
            try:

                favorited_tweets = api.favorites(id=f'{followers}')

                # Add each tweet that the current follower engaged with to the list  
                for tweet in range(len(favorited_tweets)):

                    status = favorited_tweets[tweet]

                    #convert to string
                    json_str = json.dumps(status._json)

                    #deserialise string into python object
                    parsed = json.loads(json_str)
                    
                    # gets the created_at (time) and the text from the tweets the followers engaged with
                    times.append(parsed.get('created_at'))
                    text.append(parsed.get('text'))

            except tweepy.TweepError:

                pass

        # Seperates hours, mins into lists to be put into a df (leave hours as str to keep in military time for put request to backend)
        hours, mins = [i[11:13] for i in times], [int(i[14:16]) for i in times]
        
        _min_bin = min_bin(mins)
         
        # Creates df with times and text
        df = pd.DataFrame(data={'hours':hours, 'mins':mins, 'min_bin':_min_bin, 'text':text})
        
        df['time'] = df['hours'].astype(str) + ':' + df['min_bin'].astype(str)
        
        return df
    
    def optimal_time(self, df):
        today = date.today()
        day = today.strftime("%b-%d-%Y").replace('-', ' ')
        day_and_date = calendar.day_name[today.weekday()][:3] + ' ' + day
        optimal_time = df['time'].value_counts().idxmax()
        return day_and_date + ' ' + optimal_time + ':00 UTC+0000'
