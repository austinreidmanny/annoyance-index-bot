#!/usr/bin/env python3

# The Alex Goldman Annoyance Index Bot v1.0
# Austin R. Manny. June 15, 2017
# http://github.com/austinreidmanny

# Adapted from Molly White's 'bot.py' at https://github.com/molly/twitterbot_framework/
# Used within her MIT license granted at https://github.com/molly/twitterbot_framework/blob/master/LICENSE

# Before using, make sure that you have the module 'tweepy' installed
# Easiest way is via the UNIX utility 'pip'

import os
import tweepy
from secrets import *
from time import gmtime, strftime

from urllib import request
import re

def get_data():
    url = 'https://annoyanceindex.squarespace.com'
    with request.urlopen(url) as response:
        html = response.read().decode('utf-8')
    lines = html.split('\n')
    return lines

# Pare down the text to what I actually need from the website #
def cutdown():
    lines = get_data()
    for line in lines:
        if '594185d020099ed792309d97' in line:  # finds the code with the graph
            graph = line
    relevant = graph.split('594185d020099ed792309d97')[2] # skips to the relevant bit
    relevant = relevant.replace('&quot;', '')
    return relevant


# Retrieve the date of the most recent Annoyance Index score #
def current_date():
    relevant = cutdown()
    date_start = 'sampleLabels:'
    date_end = ']}'
    dates_str = (relevant[relevant.find(date_start):relevant.find(date_end)])[14:]

    dates = dates_str.split(',')
    most_recent_date = dates[-1]
    #print(dates)
    return most_recent_date


# Get all the Annoyance Index scores, and focus on the 2 most recent scores #
def scores():
    relevant = cutdown()
    val_start = '['
    val_end = ',seriesLabels'
    values = (relevant[relevant.find(val_start):relevant.find(val_end)])[1:]

    reg_start = '\['
    reg_end = '\]'
    scores = re.findall('%s([0-9].[0-9])%s' % (reg_start, reg_end), values)

    yester_score = scores[-2]
    today_score = scores[-1]
    return yester_score,today_score


# Compare the most recent score to the score before it to determine upward or downward trend #
# This will become the tweet #
def analysis():
    y_score, t_score = scores()

    if t_score > y_score:
        return ('As of %s, the @AGoldmun Annoyance Index is up! BUY BUY BUY!' % current_date() )
    elif t_score < y_score:
        return ('As of %s, the @AGoldmun Annoyance Index is down! SELL SELL SELL!' % current_date() )
    elif t_score == y_score:
        return ("As of %s, @AGoldmun Annoyance Index is holding steady. " \
               "That Alex is nothing if not consistent." % current_date() )


# Bot configuration #
bot_username = 'AnnoyanceIndex'
logfile_name = bot_username + '.log'


def create_tweet():
    # Put in my code from annoyance_index.py
    text = analysis()
    return text


def tweet(text):
    # Twitter authentication
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)

    # Send the tweet and log success of failure
    try:
        api.update_status(text)
    except tweepy.error.TweepError as e:
        log(e.message)
    else:
        log('Tweeted: %s' % text)


def log(message):
    # Revisit this to really understand how this logging implementation works
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime('%d %b %Y %H:%M:%S', gmtime())
        f.write('\n' + t + ' ' + message)


if __name__ == '__main__':
    tweet_text = create_tweet()
    tweet(tweet_text)
