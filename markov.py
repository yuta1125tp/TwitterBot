# -*- coding: utf-8 -*-
import random
import MeCab
import codecs
import re

import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

import pickle

import sys

import time # sleep関数のため

import remove_tweet
import control_tweet

# sys.stdin  = codecs.getreader('utf-8')(sys.stdin)
# sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

appid = "dj0zaiZpPWNQYUtGT0phWWV6bCZzPWNvbnN1bWVyc2VjcmV0Jng9ODU-"  # 登録したアプリケーションID
pageurl = "http://jlp.yahooapis.jp/MAService/V1/parse"

"""
def wakati(text):
    t = MeCab.Tagger("-Owakati")
    m = t.parse(text.encode('utf-8'))
    # parseで分かち書きにされるのはスペースで区切られたstr
    # print 'print m'
    # print m #.encode('utf-8')
    # Unix系ならrstripするのは\nだけでいいけど、Windowsは\r\nを除いてあげなきゃいけない
    result = m.rstrip(" \r\n").split(" ")
    # そのstrからスペース+改行文字を除き、スペース毎に分割したものがlist構造で格納されてるresult
    # MeCabで処理した結果は文字列型なのでUnicode型にデコードしてやる
    for i in xrange(len(result)):
        result[i] = unicode(result[i], 'utf-8', 'ignore')    
    return result
"""

def wakati_MeCab(sentence, appid=appid, results="ma", filter="1|2|3|4|5|6|7|8|9|10|11|12|13"):
    # MeCabを利用してわかつ
    # 改行文字が除かれていないので注意。
    # 返すものはUnicode型の分かち書きされた言葉が入ったリスト
    t = MeCab.Tagger("-Owakati")
        
    if isinstance(sentence, list): # 引数がリストオブジェクト
        total_result = [[],[]]
        for i in xrange(len(sentence)):
            # parseで分かち書きにされるのはスペースで区切られたstr
            # print 'print m'
            # print m #.encode('utf-8')
            m = t.parse(sentence[i].encode("utf-8"))
            # Unix系ならrstripするのは\nだけでいいけど、Windowsは\r\nを除いてあげなきゃいけない
            result = m.rstrip(" \r\n").split(" ")
            # そのstrからスペース+改行文字を除き、スペース毎に分割したものがlist構造で格納されてるresult
            # MeCabで処理した結果は文字列型なのでUnicode型にデコードしてやる
            for j in xrange(len(result)):
                total_result[0].append(unicode(result[j], 'utf-8', errors='ignore'))
                total_result[1].append(j)
            # 1つづつのツイートの最後に改行文字を挟むことで複数ツイートが連続して繋がるのを防ぐ。
            total_result[0].append(u"\n")
            total_result[1].append(-1) # 改行文字のところのidxは-1にしておく？
        return total_result
    
    elif instance(sentence, unicode): # 引数がUnicode
        # 文章をURLエンコーディング
        total_result = []

        # parseで分かち書きにされるのはスペースで区切られたstr
        m = t.parse(sentence.encode("utf-8"))
        # Unix系ならrstripするのは\nだけでいいけど、Windowsは\r\nを除いてあげなきゃいけない
        result = m.rstrip(" \r\n").split(" ")
        # そのstrからスペース+改行文字を除き、スペース毎に分割したものがlist構造で格納されてるresult
        # MeCabで処理した結果は文字列型なのでUnicode型にデコードしてやる
        for i in xrange(len(result)):
            total_result.append(unicode(result[i], 'utf-8', 'ignore'))
        #total_result.append(unicode("\n", errors='utf-8'))
        return total_result
        
    else:
        print 'invalid argument'
        exit()

def wakati_Yahoo(sentence, appid=appid, results="ma", filter="1|2|3|4|5|6|7|8|9|10|11|12|13"):
    # Yahooのサービスを利用
    # 改行文字が除かれていないので注意。
    if isinstance(sentence, list):
        # 文章をURLエンコーディング
        result = []
        for i in xrange(len(sentence)):
            # print i
            sentence_encoded = urllib.quote_plus(sentence[i].encode("utf-8"))
            query = u"%s?appid=%s&results=%s&filter=%s&sentence=%s" % (pageurl, appid, results, filter, sentence_encoded)
            c = urllib2.urlopen(query)
            soup = BeautifulSoup(c.read())
            """
            return [(w.surface.string, w.reading.string, w.pos.string)
                    for w in soup.ma_result.word_list]
            """
            result_tuple = [(w.surface.string, w.reading.string, w.pos.string)
                      for w in soup.ma_result.word_list]
            for j in xrange(len(result_tuple)):
                # 長さ3のタプルだけど、こんな形式なので1つ目のみを使う(大学、だいがく、名詞)
                result.append(result_tuple[j][0])
        return result        
    elif instance(sentence, unicode): # 引数がUnicode
        # 文章をURLエンコーディング
        sentence = urllib.quote_plus(sentence.encode("utf-8"))
        query = u"%s?appid=%s&results=%s&filter=%s&sentence=%s" % (pageurl, appid, results, filter, sentence)
        c = urllib2.urlopen(query)
        soup = BeautifulSoup(c.read())
        """
        return [(w.surface.string, w.reading.string, w.pos.string)
                for w in soup.ma_result.word_list]
        """
        result_tuple = [(w.surface.string, w.reading.string, w.pos.string)
                  for w in soup.ma_result.word_list]
        result = []
        for i in xrange(len(result_tuple)):
            # 長さ3のタプルだけど、こんな形式なので1つ目のみを使う(大学、だいがく、名詞)
            result.append(result_tuple[i][0])   
        return result
    else:
        print 'sentence is invalid!'
        exit()
def make_MC_table2(wordlist):
    # Create table of Markov Chain
    markov = {}
    w1 = u""
    w2 = u""
    # wordlistにどんどん事例を保存していく。
    # 事例: (w1, w2) -> w3
    # 直前の2単語？をキーに次につづく単語を予測
    for i in xrange(len(wordlist[0])):
        word = wordlist[0][i]
        idx = wordlist[1][i]
        if w1 and w2: # u""はFalse扱い
            if (w1, w2) not in markov:
                markov[(w1, w2)] = [] # 初めて見る単語の連続だった場合はキーに登録
            markov[(w1, w2)].append((word,idx)) # そのキーの後に続く単語を登録(リスト)
        w1, w2 = w2, word # 次の単語に写る
    return markov
    
def make_MC_table1(wordlist):
    # Create table of Markov Chain
    markov = {}
    w1 = u""
    # wordlistにどんどん事例を保存していく。
    # 事例: (w1) -> w3
    # 直前の1単語？をキーに次につづく単語を予測
    for word in wordlist:
        if w1:
            if w1 not in markov:
                markov[w1] = [] # 初めて見る単語の連続だった場合はキーに登録
            markov[w1].append(word) # そのキーの後に単語を登録(リスト)
        w1 = word # 次の単語に写る
    return markov
    
def generate_sentence2(MCtable, wordlist):
    # Generate Sentence
    # 前の単語1つに注目
    count = 0
    sentence = u""
    # 生成する文章のはじめの2単語はランダムに選ぶ
    """
    for w1,w2 in MCtable.keys():
        #print type(MCtable[(w1,w2)])
        #print MCtable
        #for i in xrange(len(MCtable[(w1,w2)])):
        #    print MCtable[(w1,w2)][i][0],
    """
    
    while(1):
        w1,w2 = random.choice(MCtable.keys())
        if MCtable.has_key((w1, w2)):
            if MCtable[(w1,w2)][0][1]==2: # w3相当のidx=2
                break
    sentence += w1
    sentence += w2
    while count < len(wordlist[0]):
        # 直前の2単語をもとにその後ろにくる単語を事例ベースで予測。
        # 事例が複数ある場合はランダムに選ぶ

        # w1,w2に存在しないキーの組み合わせが起きるとエラーで落ちる。
        # 最後のツイートの後に言葉が続かないので、キーがなくなる。
        # キーがない場合はもう一度キーを取り直す。
        # 学習用の文章が十分多かったらそんなことなくなるんだろうけど。。。
        if not MCtable.has_key((w1, w2)):
            w1, w2  = random.choice(MCtable.keys())
        tmp = random.choice(MCtable[(w1, w2)])
        # print tmp
        sentence += tmp[0]
        w1, w2 = w2, tmp[0]
        count += 1
    return sentence
    
def generate_sentence1(MCtable, wordlist):
    # Generate Sentence
    count = 0
    sentence = u""
    # 生成する文章のはじめの1単語はランダムに選ぶ 
    w1 = random.choice(MCtable.keys())
    while count < len(wordlist):
        # 直前の2単語をもとにその後ろにくる単語を事例ベースで予測。
        # 事例が複数ある場合はランダムに選ぶ
        tmp = random.choice(MCtable[w1])
        # print tmp
        sentence += tmp
        w1 = tmp
        count += 1
    return sentence
 
if __name__ == "__main__":
    # fout = open('out.txt', 'w')
    
    f = open('tweet_log.pkl')
    
    # 保存されているのはツイートがリスト形式で保存されている
    tweet_log = pickle.load(f)
    
    for i in xrange(10):
        print i,',',tweet_log[i]
    print 
    time.sleep(1)

    # 不要なツイートはリストから削除する
    remove_tweet.remove_retweet(tweet_log)
    remove_tweet.remove_at_tweet(tweet_log)
    remove_tweet.remove_url_tweet(tweet_log)
    
    for i in xrange(10):
        print i,',',tweet_log[i]
    print 
    time.sleep(1)
    
    wordlist = wakati_MeCab(tweet_log[0:10]) 
    
    for i in xrange(len(wordlist[0])):
        print i,',',wordlist[0][i],',',wordlist[1][i]

    print 
    time.sleep(1)
    
    markov = make_MC_table2(wordlist)
    
    sentence = generate_sentence2(markov, wordlist)
    
    print sentence
    
    splited_sentence = re.split(u'\n', sentence)
    
    splited_sentence = \
        control_tweet.punctuate_control(splited_sentence)
    
    # Unicode型はprint関数で出力すると日本語で表示される
    for i in xrange(len(splited_sentence)):
        print i,',',splited_sentence[i]
        
        
    # 保存する際はUnicode型から文字列型にエンコードする
    # fout.write(sentence.encode('utf-8'))
    # print sentence.encode('utf-8')
