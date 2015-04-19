# -- coding: utf-8 --
__author__ = 'snownettle'
import cld
import langid
import pandas


def check_german(tweet_text):
    emoji_key = pandas.read_csv('DATA/emoji_table.txt', encoding='utf-8', index_col=0)
    emoji_key['count'] = 0
    emoji_dict = emoji_key['count'].to_dict()
    emoji_dict = emoji_key['count'].to_dict()
    emoji_dict_total = emoji_key['count'].to_dict()
    emoji_list = emoji_dict.keys()


    tweet_text = unicode(tweet_text, 'utf-8')
    tweet_text = tweet_text.encode('utf-8')
    tokens = tweet_text.split(' ')
    new_text = ''
    #delete @username
    for token in tokens:
        if '@' not in token:
            new_text += token + ' '
    new_text = new_text.lower()
    text = unicode(new_text, 'utf-8')
    text = text.encode('utf-8')
    top_language_name = cld.detect(text)
    lang_form_langid = langid.classify(text)
    if new_text == '':
        return True
    #if text emty - german
    if top_language_name[0] == 'GERMAN' or lang_form_langid[0] == 'de':
        return True
    else:
        return False


