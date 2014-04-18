# -*-coding:utf-8 -*-
# 自動生成したつぶやきを後からいじくる
import re

def bracket_control(sentence):
    bracket_list = [[u'「',u'」'],
                    [u'【',u'】'],
                    [u'（',u'）']]#,
    #                [u'\(',u'\)']] # 半角括弧の対応がむずい。 (でなく\(でなくてはいけない。
    for [left_bracket, right_bracket] in bracket_list:
        sentence = kagi_tozi(sentence, left_bracket, right_bracket)
        sentence = kagi_hazime(sentence, left_bracket, right_bracket)   
        sentence = check_nonsense_bracket(sentence, left_bracket+right_bracket)
    return sentence
 
def check_nonsense_bracket(sentence, brackets):
    # 内容がないカギ括弧では意味が無いので削除
    # 「」とか（）とか
    list_sentence = list(sentence)
    re_result = re.search(brackets, sentence)
    if re_result:
        list_sentence[re_result.start():re_result.end()]=[]
    sentence = u''
    for uni in list_sentence:
        sentence += uni    
    return sentence  
    
def kagi_tozi(sentence, left, right):
    kagi_stack = []
    for idx, uni in enumerate(sentence):
        if bool(re.search(left,uni)):
            kagi_stack.append(idx)
        if bool(re.search(right,uni)):
            if bool(len(kagi_stack)):
                kagi_stack.pop()
    for idx in kagi_stack:
        for i in xrange(len(sentence)-idx):
            if bool(re.search(u'。',sentence[idx+i])):
                sentence = sentence[:idx+i+1]+right+sentence[idx+i+1:]
                break
            if i == len(sentence)-idx-1:
                sentence = sentence + right
    return sentence
            
def kagi_hazime(sentence, left, right):
    list_sentence = list(sentence)
    list_sentence.reverse() # 逆順に
    kagi_stack = []
    for idx, uni in enumerate(list_sentence):
        if bool(re.search(right,uni)):
            kagi_stack.append(idx)
        if bool(re.search(left,uni)):
            if bool(len(kagi_stack)):
                kagi_stack.pop()
    for idx, kagi_idx in enumerate(kagi_stack):
        for i in xrange(idx,len(list_sentence)-kagi_idx):
            if bool(re.search(u'。',list_sentence[kagi_idx+i])):
                list_sentence.insert(kagi_idx+i, left)
                break
            if i == len(list_sentence)-kagi_idx-1:
                list_sentence.append(left)

    list_sentence.reverse()
    sentence = u''
    for uni in list_sentence:
        sentence += uni
    return sentence
        
    
"""        
def only_left_bracket(sentence):
    # 対応する右括弧を文末につける。
    #(
    #{
    #[
    #（
    #｛
    #「
    bracket_stack=[]
    for uni in sentence:
        if bool(re.search(u'（', uni)):
            bracket_stack.append(u'）')
        if bool(re.search(u'｛', uni)):
            bracket_stack.append(u'｝')
        if bool(re.search(u'「', uni)):
            bracket_stack.append(u'」')
        if bool(re.search(u'\(', uni)):
            bracket_stack.append(u')')
        if bool(re.search(u'{', uni)):
            bracket_stack.append(u'}')
        if bool(re.search(u'\[', uni)):
            bracket_stack.append(u']')

        #if bool(re.search(u'[）｝」\)}\]]', uni)):
        #    bracket_stack.pop()
        
        if bool(re.search(u'）', uni)):
            if u'）' in bracket_stack:
                bracket_stack.pop(bracket_stack.index(u'）'))
        if bool(re.search(u'｝', uni)):
            if u'｝' in bracket_stack:
                bracket_stack.pop(bracket_stack.index(u'｝'))
        if bool(re.search(u'」', uni)):
            if u'」' in bracket_stack:
                bracket_stack.pop(bracket_stack.index(u'」'))
        if bool(re.search(u'\)', uni)):
            if u')' in bracket_stack:
                bracket_stack.pop(bracket_stack.index(u')'))
        if bool(re.search(u'}', uni)):
            if u'}' in bracket_stack:
                bracket_stack.pop(bracket_stack.index(u'}'))
        if bool(re.search(u'\]', uni)):
            if u']' in bracket_stack:
                bracket_stack.pop(bracket_stack.index(u']'))
        
    bracket_stack.reverse()
    for bracket in bracket_stack:
        sentence += bracket
    return sentence
    
def only_right_bracket(sentence):
    # 対応する左括弧を文末につける。
    bracket_stack=[]
    # 逆順で見る
    print sentence
    rev_sentence = list(sentence)
    print rev_sentence
    rev_sentence.reverse()
    print rev_sentence
    for uni in rev_sentence:
        if bool(re.search(u'）', uni)):
            bracket_stack.append(u'（')
        if bool(re.search(u'｝', uni)):
            bracket_stack.append(u'｛')
        if bool(re.search(u'」', uni)):
            bracket_stack.append(u'「')
        if bool(re.search(u'\)', uni)):
            bracket_stack.append(u'(')
        if bool(re.search(u'}', uni)):
            bracket_stack.append(u'{')
        if bool(re.search(u'\]', uni)):
            bracket_stack.append(u'[')

        if bool(re.search(u'[（｛「\({\[]]', uni)):
            bracket_stack.pop()
        
        #if bool(re.search(u'）', uni)):
        #    bracket_stack.pop()
        #if bool(re.search(u'｝', uni)):
        #    bracket_stack.pop()
        #if bool(re.search(u'」', uni)):
        #    bracket_stack.pop()
        #if bool(re.search(u'\)', uni)):
        #    bracket_stack.pop()
        #if bool(re.search(u'}', uni)):
        #    bracket_stack.pop()
        #if bool(re.search(u'\]', uni)):
        #    bracket_stack.pop()
        
    bracket_stack.reverse()
    
    # 逆順にしていたのを元に戻す
    #sentence.reverse()

    for bracket in bracket_stack:
        sentence = bracket + sentence
    return sentence
"""
    
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
    if bool(re.search(u'.*[。．！？…]。$', sentence)):
        sentence = sentence[0:-1]
    return sentence
    
def add_punctuate(sentence):
    # 、が文中にある場合は文末に。を加える。
    pass
    
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

if __name__=="__main__":
    # uni = u"｛((「「｛私の名前は白川悠太」"
    uni = u"私の名前は白川悠太。」ほげ」"
    print uni
    uni = bracket_control(uni)
    print uni