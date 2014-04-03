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

import webapp2

import os

# kawabottpへアクセスするための情報。
# ちなみに登録時に使用したメールアドレスはyuta1125tp+bot@gmail.com
consumerKey = 'XR9ImVofpaqa6zqcpeJlgQ'
consumerSecret = 'm9UAPDO6bFwuPip7kWT4MbJbMi6fY0POTDz92f9zpQ'
accessToken = '2221327394-qsHDtrC7TgEqATLijM3aM9S4UZyYWeRVjvmyGVw'
accessSecret = 'vXh3cYMbdKyOqUDeMKfCdBz9g4jn6wy66SNHWnUmjC64i'

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

def get_info(api, name="kawabottp"):
    # 夜中に叩く、api経由で情報を取得もしくは更新して、ローカルに保存する
    # get_sampleでは独自の辞書形式になおしているけどあんま効果ない気がする。
    # もちろん明らかに使わない情報を保存しておくのはナンセンスだけど、下手に加工しなくてもいい
    # 生のままpickleで保存
    # 保存用のディレクトリにユーザーID毎に保存
    # fout = codecs.open('samples.txt', 'w', 'utf-8')
    
    # 鍵アカウントの人は使えないので保存しててもダメだから捨ててしまっていい。
    ids = get_friends_id(api, name)
    remove_kagi_account(api, ids, name)
    
    num_tweet = 20
    abspath_to_script = os.path.abspath(os.path.dirname(__file__)) 
    if not os.path.exists(abspath_to_script+"/tweet_log"):
        os.mkdir(abspath_to_script+"/tweet_log")
    for i in xrange(len(ids)):
        #tweet_dict[ids[i]]=[] # ユーザIDをキーに1ユーザにつき1つのリストにツイートを保存
        # もしすでに該当するidのpicklefileがある場合は差分を追加する
        # 現状だと常に上書きしていて最近の20しか見れてない
        
        try:
            user_timeline = api.get_user_timeline(user_id = ids[i], 
                                                  count = num_tweet)
        except Exception as e:
            print e
        with open(abspath_to_script+"/tweet_log/"+str(ids[i])+".pkl", 'w') as fout:
            # HIGHEST_PROTOCOLを指定するとloadできなくなる！要検証
            pickle.dump(user_timeline, fout) #, pickle.HIGHEST_PROTOCOL)
        
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

"""
def get_samples(api, name='kawabottp'):
    # 指定したユーザーのフォロワーの最近のツイートを取得してtxtファイルに保存
    # ユーザをキーに辞書形式で保存する。無駄かもしれないけど…
    
    # fout = codecs.open('samples.txt', 'w', 'utf-8')
    
    ids = get_friends_id(api, name)
    remove_kagi_account(api, ids, name)
    
    num_tweet = 20
    
    tweet_dict = {}
    for i in xrange(len(ids)):
        tweet_dict[ids[i]]=[] # ユーザIDをキーに1ユーザにつき1つのリストにツイートを保存
        try:
            user_timeline = api.get_user_timeline(user_id = ids[i], 
                                                  count = num_tweet)
        except Exception as e:
            print e
        for j in xrange(len(user_timeline)):
            tweet_dict[ids[i]].append(user_timeline[j]['text'])


    # pbar.finish()
    return tweet_dict
"""
     
def get_friends_id(api, name):
    # 指定したユーザー"が"フォローしているユーザーのID一覧を返す
    try:
        users_friends_list = api.get_friends_ids(screen_name=name)
    except Exception as e:
        print e
    # print type(users_friends_list) # dict形式
    # print len(users_friends_list) # 要素が5つ
    # print users_friends_list['ids'] # followしているユーザのidのリストを返す 
    return users_friends_list['ids']
    
def get_follwers_id(api, name):
    # 指定したユーザー"を"フォローしているユーザーのID一覧を返す
    try:
        users_followers_list = api.get_followers_ids(screen_name=name)
    except Exception as e:
        print e
    # print type(users_friends_list) # dict形式
    # print len(users_friends_list) # 要素が5つ
    # print users_friends_list['ids'] # followしているユーザのidのリストを返す 
    return users_followers_list['ids']
    
def tweet_msg():
    
    #dictionary = load_dic('dictionary.txt')
    #save_dic(dictionary, 'dictionary2.txt')
    #random_tweet(dictionary)
    
    api = twython.Twython(app_key=consumerKey,
                  app_secret=consumerSecret,
                  oauth_token=accessToken,
                  oauth_token_secret=accessSecret)
    
    tweet_dict = get_samples(api)
    get_info(api)
    #remove_tweet.remove_at_tweet(tweet_dict)
    #remove_tweet.remove_url_tweet(tweet_dict)
    #remove_tweet.remove_retweet(tweet_dict)
    
    # 辞書として持ってても仕方ないので辞書の解体
    # 全部合わせて1つのUnicode型変数にする。
    # 全部合わせて1つにするとURLエンコードした時にGAEから開けるURLの上限の長さを超えてしまう。
    # 1ツイート毎別々にYahooに問い合わせる方針に転換。
    #tweet_unicode = u''
    
    """
    tweet_unicode_list = [] # 1つのつぶやきが1つの要素なリスト
    for i in tweet_dict.keys(): # keys
        for j in xrange(len(tweet_dict[i])):
            tweet_unicode_list.append(tweet_dict[i][j])
            #tweet_unicode += tweet_dict[i][j]
    """
    
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
    
    # print tweet_unicode
    # src = codecs.open("samples.txt", 'r', 'utf-8').read()

    import markov
    wordlist=[]
    # MeCabならURLを経由しないから全部まるっと投げてしまっていい。
    wordlist=markov.wakati_MeCab(tweet_unicode_list)

    mc_table = markov.make_MC_table2(wordlist)
    
    sentence = markov.generate_sentence2(mc_table, wordlist)
    sentence_list = re.split(u'\n', sentence)
    
    sentence_list = \
        control_tweet.punctuate_control(sentence_list)
    
    #tweet = u""
    tweet_index=0
    while(1):
        # 何もない文章が候補に上がる場合がある。
        if sentence_list[tweet_index]!=u'':
            break
        tweet_index += 1
    
    try:
        api.update_status(status=sentence_list[tweet_index])
    except twython.TwythonError as e:
        print e    

if __name__=="__main__":
    tweet_msg()

