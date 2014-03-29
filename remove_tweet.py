# -*-coding:utf-8 -*-
# つぶやくと問題がありそうな候補を予め消しておく。
# ハッシュタグ
# @ツイート
# URL

import re

def remove_at_tweet(tweet_dict):
    # 知らない人への@ツイートや#のハッシュタグをしてしまわないように
    if isinstance(tweet_dict,dict):
        index = []
        for follower_id in tweet_dict.keys():
            for i in xrange(len(tweet_dict[follower_id])):
                if bool(re.search(u'.*@.*', tweet_dict[follower_id][i])):
                    index.append(i)
                elif bool(re.search(u'.*#.*', tweet_dict[follower_id][i])):
                    index.append(i)
            for j in reversed(index):
                tweet_dict[follower_id].pop(j)

    elif isinstance(tweet_dict, list):
        for tweet in list(tweet_dict):
            if bool(re.search(u'.*@.*', tweet)):
                tweet_dict.remove(tweet)
            elif bool(re.search(u'.*#.*', tweet)):
                tweet_dict.remove(tweet)
                
def remove_url_tweet(tweet_dict):
    # URLに繋がりそうなキーワードを含むツイートは除く
    url_keywords = [
        u'www.', u'pic.', u'.com', u'http',
        u'.ly', u',me', u't.co', u'//',
        u'.jp']
    if isinstance(tweet_dict,dict):
        index = []
        for follower_id in tweet_dict.keys():
            for i in xrange(len(tweet_dict[follower_id])):
                for key_word in url_keywords:
                    if bool(re.search(u'.*' + key_word + u'.*', 
                                      tweet_dict[follower_id][i])):
                        index.append(i)
                        break
            for j in reversed(index):
                tweet_dict[follower_id].pop(j)
                
    elif isinstance(tweet_dict, list):
        for tweet in list(tweet_dict):
            for key_word in url_keywords:
                if bool(re.search(u'.*' + key_word + u'.*', tweet)):
                    tweet_dict.remove(tweet)
                    break
                    
def remove_retweet(tweet_dict):
    # 引用やリツイートしないようにする
    # RT, QT
    # これらを除く。
    
    # 引数にはAPIで取ってきたばかりのdictが来る場合と、
    # ツイートのUnicode型のリストの場合がある。
    if isinstance(tweet_dict,dict):
        index = []
        for follower_id in tweet_dict.keys():
            for i in xrange(len(tweet_dict[follower_id])):
                if bool(re.search(u'.*RT.*', tweet_dict[follower_id][i])):
                    index.append(i)
                elif bool(re.search(u'.*QT.*', tweet_dict[follower_id][i])):
                    index.append(i)
            for j in reversed(index):
                tweet_dict[follower_id].pop(j)
    elif isinstance(tweet_dict, list):
        for tweet in list(tweet_dict):
            if bool(re.search(u'.*RT.*', tweet)):
                tweet_dict.remove(tweet)
            elif bool(re.search(u'.*QT.*', tweet)):
                tweet_dict.remove(tweet)
