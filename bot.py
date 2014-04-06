# -*- coding:utf-8 -*-
# twython経由でTwitterのAPIを叩く

# twythonを使ったテストコード
import twython # pythonからtwitterをごちゃごちゃできるライブラリ
import codecs # 文字コードを指定してファイルの入出力をする場合に使う
import random # randint使うときに必要
import sys # 標準出力の文字コードを変更するために用いる

import re # 正規表現のマッチングかける時

import markov # 文書生成のためのマルコフ課程周りの関数が入ってる。
import remove_tweet # @や#を含むツイートを削除する
import control_tweet # 生成したつぶやきをいじくるモジュール

import pickle # つぶやきログがpickleで保存されてるのを読み込むため

# import webapp2

import os

import json

def load_dic(load_name):
    # 言葉を読み込んでくる。
    f = codecs.open(load_name, 'r', 'utf-8')
    data = f.read() # .txtの中身全部を読み込んでくる。
    dictionary = data.split('\n')
    # for word in dictionary:
    #     print word
    # print
    return dictionary

def save_dic(dictionary, save_name):
    # 言葉を保存する。
    f = codecs.open(save_name, 'w', 'utf-8')
    for word in dictionary:
        f.write(word+'\n')
        
def random_tweet(dictionary):
    # 保持している辞書からランダムに選んで表示する
    for i in xrange(10):
        print dictionary[random.randint(0,len(dictionary)-1)]

def remove_kagi_account(api, ids, name):
    # 鍵付きアカウントの内容をツイートしてしまってはまずいので
    # 鍵付きｱカウントのIDを削除する
    index = []
    list = api.get_followers_list(screen_name = name)
    for i in xrange(len(list[u'users'])):
        if list[u'users'][i][u'protected']:
            ids.remove(list[u'users'][i][u'id'])

def get_info(api, name):
    # 夜中に叩く、api経由で情報を取得もしくは更新して、ローカルに保存する
    # get_sampleでは独自の辞書形式になおしているけどあんま効果ない気がする。
    # もちろん明らかに使わない情報を保存しておくのはナンセンスだけど、下手に加工しなくてもいい
    # 生のままpickleで保存
    # 保存用のディレクトリにユーザーID毎に保存
    # fout = codecs.open('samples.txt', 'w', 'utf-8')
    
    # 差分を保存する。
    
    # 鍵アカウントの人は使えないので保存しててもダメだから捨ててしまっていい。
    ids = get_followers_id(api, name)
    remove_kagi_account(api, ids, name)
    
    num_tweet = 50
    abspath_to_script = os.path.abspath(os.path.dirname(__file__)) 
    
    if not os.path.exists(abspath_to_script+"/tweet_log"):
        os.mkdir(abspath_to_script+"/tweet_log")
    for i in xrange(len(ids)):
        # すでにログがある場合
        if os.path.exists(abspath_to_script+"/tweet_log/"+str(ids[i])+".pkl"):              
            with open(abspath_to_script+"/tweet_log/"+str(ids[i])+".pkl", 'r') as fin:
                tweet_log = pickle.load(fin)
                latest_id = tweet_log[0]['id']
            try:
                user_timeline = api.get_user_timeline(user_id = ids[i], 
                                                      count = num_tweet)
            except Exception as e:
                print e
            
            for idx, tweet in enumerate(user_timeline):
                if latest_id < tweet['id']: # 最後に保存した内容より新しい。
                    pass
                else:
                    break
            # 新しい分のつぶやきのリストを連結して保存する。
            tweet_log = user_timeline[0:idx] + tweet_log
            with open(abspath_to_script+"/tweet_log/"+str(ids[i])+".pkl", 'w+') as fout:
                pickle.dump(tweet_log, fout, pickle.HIGHEST_PROTOCOL)

        else:
            # ログがまだない場合
            try:
                user_timeline = api.get_user_timeline(user_id = ids[i], 
                                                      count = num_tweet)
            except Exception as e:
                print e
            
            with open(abspath_to_script+"/tweet_log/"+str(ids[i])+".pkl", 'a') as fout:
                pickle.dump(user_timeline, fout, pickle.HIGHEST_PROTOCOL)
        
def load_info():
    # ローカルに保存した情報を取得する
    # 現在の仕様だと結局つぶやき内容（Unicode型）のリストしか使ってないので
    # この関数の中でそれに直して返す
    abspath_to_script = os.path.abspath(os.path.dirname(__file__)) 
    unicode_list = []
    for pklfile in os.listdir(abspath_to_script+"/tweet_log"):
        with open(abspath_to_script+"/tweet_log/"+pklfile) as fin:
            user_timeline = pickle.load(fin)
            for tweet in user_timeline: 
                unicode_list.append(tweet['text'])
    return unicode_list

def get_friends_id(api, name):
    # 指定したユーザー"が"フォローしているユーザーのIDをリストで返す
    try:
        users_friends_list = api.get_friends_ids(screen_name=name)
    except Exception as e:
        print e
    # print type(users_friends_list) # dict形式
    # print len(users_friends_list) # 要素が5つ
    # print users_friends_list['ids'] # followしているユーザのidのリストを返す 
    return users_friends_list['ids']
    
def get_followers_id(api, name):
    # 指定したユーザー"を"フォローしているユーザーのIDをリストで返す
    try:
        users_followers_list = api.get_followers_ids(screen_name=name)
    except Exception as e:
        print e
    # print type(users_friends_list) # dict形式
    # print len(users_friends_list) # 要素が5つ
    # print users_friends_list['ids'] # followしているユーザのidのリストを返す 
    return users_followers_list['ids']
    
def create_friendship(api, ids):
    # 指定したidをフォローする
    # 過去にフォローのリクエストを送った人物に返事が来る前に再度送ろうとすると怒られる。
    # あと、リクエストが拒否された人に何度もリクエストを送るのも頭良くない。
    # 「リクエスト送ったけど承認されてないidリスト」をローカルに保存しておく。
    # 承認された時 このリストからidを抜くとちょうどいい？
    abspath_to_script = os.path.abspath(os.path.dirname(__file__)) 
    if os.path.exists(abspath_to_script + "/waiting_ids.pkl"):
        with open(abspath_to_script + "/waiting_ids.pkl", 'r') as fin:
            waiting_ids = pickle.load(fin)
        
    else:
        waiting_ids = []
    for id in ids:
        if id in waiting_ids: 
            pass
        else:
            api.create_friendship(user_id=id)
    
    # 了承待ちのidの保存
    waiting_ids = list(set(ids) - set(waiting_ids)) + waiting_ids
    with open(abspath_to_script + "/waiting_ids.pkl", 'w') as fout:
        pickle.dump(waiting_ids, fout, pickle.HIGHEST_PROTOCOL)
        
def remove_friendship(api, ids):
    # 指定したidをリムーブする
    for id in ids:
        api.destroy_friendship(user_id=id)

def update_waiting_ids():
    # waiting_ids.pklを更新する
    pass

def load_account_info(filename):
    abspath_to_script = os.path.abspath(os.path.dirname(__file__)) 
    info_list = json.load(open(abspath_to_script + '/' + filename))
    
    username = info_list['username']
    consumerKey = info_list['consumerKey']
    consumerSecret = info_list['consumerSecret']
    accessToken = info_list['accessToken']
    accessSecret = info_list['accessSecret']
    
    return username,\
           consumerKey,\
           consumerSecret,\
           accessToken,\
           accessSecret

def update_info():
    # 一日一回ぐらい叩いてフォローの関係を更新、
    # フォロワーのつぶやきを見てローカルに保存し直す
    
    username,\
    consumerKey,\
    consumerSecret,\
    accessToken,\
    accessSecret = load_account_info('kawa1125bot.json')
    
    api = twython.Twython(app_key=consumerKey,
                  app_secret=consumerSecret,
                  oauth_token=accessToken,
                  oauth_token_secret=accessSecret)
    
    followers_id = get_followers_id(api, username)
    friends_id = get_friends_id(api, username)
    
    # 集合の差をとる
    follower_only = list(set(followers_id) - set(friends_id))
    follow_only = list(set(friends_id) - set(followers_id))
    
    create_friendship(api, follower_only)
    remove_friendship(api, follow_only)
    
    get_info(api, username)
          
def tweet_msg():
        
    username,\
    consumerKey,\
    consumerSecret,\
    accessToken,\
    accessSecret = load_account_info('kawa1125bot.json')
    
    api = twython.Twython(app_key=consumerKey,
                  app_secret=consumerSecret,
                  oauth_token=accessToken,
                  oauth_token_secret=accessSecret)
    
    #get_info(api,username)
    
    tweet_unicode_list = load_info()
    
    # cronで呼び出すと相対パスの始まりがずれるみたい。
    import os
    abspath_to_script = os.path.abspath(os.path.dirname(__file__)) 
    f = open(abspath_to_script+'/tweet_log.pkl')
    l = pickle.load(f)
    f.close()

    # twitte apiで取ってきた分ともともと保持していた自分のつぶやき履歴を連結する
    tweet_unicode_list=tweet_unicode_list+l 
    
    # よろしくないツイートを除く
    remove_tweet.remove_retweet(tweet_unicode_list)
    remove_tweet.remove_at_tweet(tweet_unicode_list)
    remove_tweet.remove_url_tweet(tweet_unicode_list)
    
    import markov
    wordlist=[]
    # MeCabならURLを経由しないから全部まるっと投げてしまっていい。
    wordlist=markov.wakati_MeCab(tweet_unicode_list)

    mc_table = markov.make_MC_table2(wordlist)
    
    sentence = markov.generate_sentence2(mc_table, wordlist)
    sentence_list = re.split(u'\n', sentence)
    
    # 句読点周りを整形 
    sentence_list = control_tweet.punctuate_control(sentence_list)
    
    tweet_index=0
    while(1):
        # 何もない文章が候補に上がる場合がある？
        if sentence_list[tweet_index]!=u'':
            break
        tweet_index += 1
    try:
        api.update_status(status=sentence_list[tweet_index])
    except twython.TwythonError as e:
        print e    

if __name__=="__main__":
    update_info()
    #tweet_msg()

