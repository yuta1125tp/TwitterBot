# -*-coding:utf-8 -*-
# 自動生成したつぶやきを後からいじくる
import re

def convert_dot2maru(sentence):
    # 1つのツイート中は。、か．，か統一する。
    sentence = re.sub(u"．",u"。", sentence)
    sentence = re.sub(u"，",u"、", sentence)
    return sentence

def convert_maru2dot(sentence):
    # 1つのツイート中は。、か．，か統一する。
    sentence = re.sub(u"。",u"．", sentence)
    sentence = re.sub(u"、",u"，", sentence)
    return sentence

    
def shorten_punctuate(sentence):
    # 。が複数続く場合1つにする。
    return re.sub(u'。+', u'。', sentence)
    
def multiple_punctuate(sentence):
    # 何かの理由で？複数の句読点が連続した場合はやめる。
    # ？。
    if bool(re.search(u'.*[。．！？]。$', sentence)):
        sentence = sentence[0:-1]
    return sentence
    
def punctuate_control(sentence_list):
    # 生成されたつぶやき候補がUnicode型でリストで入ってる
    return_list = []
    for sentence in list(sentence_list):
        sentence = shorten_punctuate(sentence)
        sentence = multiple_punctuate(sentence)
        sentence = convert_dot2maru(sentence)
        #if bool(re.search(u'.*。$', sentence)):
        #    print u"語尾が。"
        return_list.append(sentence)

    return return_list