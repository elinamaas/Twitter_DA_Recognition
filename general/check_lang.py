# -- coding: utf-8 --
__author__ = 'snownettle'
import cld
import langid


def check_german(tweet_text):

    if isinstance(tweet_text, unicode) is False:
        tweet_text = unicode(tweet_text, 'utf-8')
        tweet_text = tweet_text.encode('utf-8')
    tokens = tweet_text.split(' ')
    new_text = ''
    #delete @username
    for token in tokens:
        if '@' not in token:
            new_text += token + ' '
    new_text = new_text.lower()
    if isinstance(new_text, unicode) is False:
        text = unicode(new_text, 'utf-8')
        text = text.encode('utf-8')
    else:
        text = new_text.encode('utf-8')
    top_language_name = cld.detect(text)
    lang_form_langid = langid.classify(text)
    if new_text == '':
        return True
    #if text empty - german
    if top_language_name[0] == 'GERMAN' or lang_form_langid[0] == 'de':
        return True
    else:
        return False

# check_german('ich mache ein hause')


