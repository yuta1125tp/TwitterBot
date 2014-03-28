# -*- coding:utf-8 -*-

# twythonを使ったテストコード
import twython # pythonからtwitterをごちゃごちゃできるライブラリ
import codecs # 文字コードを指定してファイルの入出力をする場合に使う
import random # randint使うときに必要
import sys # 標準出力の文字コードを変更するために用いる

import re # 正規表現のマッチングかける時
import markov # 文書生成のためのマルコフ課程周りの関数が入ってる。

import pickle # つぶやきログがpickleで保存されてるのを読み込むため

import webapp2

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
    
def remove_at_tweet(tweet_dict):
    # 知らない人への@ツイートや#のハッシュタグをしてしまわないように
    index = []
    for follower_id in tweet_dict.keys():
        for i in xrange(len(tweet_dict[follower_id])):
            if bool(re.search(u'.*@.*', tweet_dict[follower_id][i])):
                index.append(i)
            elif bool(re.search(u'.*#.*', tweet_dict[follower_id][i])):
                index.append(i)
        for j in reversed(index):
            tweet_dict[follower_id].pop(j)
    
def remove_url_tweet(tweet_dict):
    # URLに繋がりそうなツイートは除く
    index = []
    url_keywords = [
        u'goo', u'pic.', u'.com', u'http', u'.ly', u',me']
    for follower_id in tweet_dict.keys():
        for i in xrange(len(tweet_dict[follower_id])):
            for key_word in url_keywords:
                if bool(re.search(u'.*' + key_word + u'.*', 
                                  tweet_dict[follower_id][i])):
                    index.append(i)
                    break
        for j in reversed(index):
            tweet_dict[follower_id].pop(j)

def remove_retweet(tweet_dict):
    # 引用やリツイートしないようにする
    # RT, QT
    # これを除く。
    index = []
    for follower_id in tweet_dict.keys():
        for i in xrange(len(tweet_dict[follower_id])):
            if bool(re.search(u'.*RT.*', tweet_dict[follower_id][i])):
                index.append(i)
            elif bool(re.search(u'.*QT.*', tweet_dict[follower_id][i])):
                index.append(i)
        for j in reversed(index):
            tweet_dict[follower_id].pop(j)
    
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
    
    remove_at_tweet(tweet_dict)
    remove_url_tweet(tweet_dict)
    remove_retweet(tweet_dict)
    # 辞書として持ってても仕方ないので辞書の解体
    # 全部合わせて1つのUnicode型変数にする。
    # 全部合わせて1つにするとURLエンコードした時にGAEから開けるURLの上限の長さを超えてしまう。
    # 1ツイート毎別々にYahooに問い合わせる方針に転換。
    tweet_unicode = u''
    tweet_unicode_list = [] # 1つのつぶやきが1つの要素なリスト
    for i in tweet_dict.keys(): # keys
        for j in xrange(len(tweet_dict[i])):
            tweet_unicode_list.append(tweet_dict[i][j])
            tweet_unicode += tweet_dict[i][j]

    f = open('tweet_log.pkl')
    l = pickle.load(f)
    f.close()

    tweet_unicode_list=tweet_unicode_list+l
    
    # print tweet_unicode
    # src = codecs.open("samples.txt", 'r', 'utf-8').read()

    import markov
    wordlist=[]
    # MeCabならURLを経由しないから全部まるっと投げてしまっていい。
    wordlist=markov.wakati_MeCab(tweet_unicode_list)
    # いっぺんに投げるとyahooに投げるURLが長くなりすぎてダメなので1ツイートごと細かく区切る
    """
    for tweet in tweet_unicode_list:
        # print tweet
        wordlist=wordlist+markov.wakati_MeCab([tweet])
        # wordlist=wordlist+markov.wakati_Yahoo([tweet])
    """
    """
    wordlist = markov.wakati_Yahoo(tweet_unicode_list) # ここで元となる文章が分かち書きに変換される
    """
    """
    f = open('wordlist.pkl','w')
    pickle.dump(wordlist,f)
    f.close()
    del wordlist
    
    f = open('wordlist.pkl','r')
    wordlist = pickle.load(f)
    f.close()   
    """
    mc_table = markov.make_MC_table2(wordlist)
    
    sentence = markov.generate_sentence2(mc_table, wordlist)
    sentence_list = re.split(u'。', sentence)
    tweet = u""
    tweet_index=0
    while(1):
        if sentence_list[tweet_index]!=u'':
            break
        tweet_index += 1
    
    try:
        api.update_status(status=sentence_list[tweet_index])
    except twython.TwythonError as e:
        print e    

class MainHandler(webapp2.RequestHandler):
    def get(self): 
        tweet_msg()
        self.response.write('Hello world!')
 
app = webapp2.WSGIApplication([
    ('/.*', MainHandler)
], debug=True)

if __name__=="__main__":
    tweet_msg()

