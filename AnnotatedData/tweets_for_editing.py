__author__ = 'snownettle'
import csv



def write_to_file(list_of_tweets):
    with open('tweet_to_edit.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';',)
        spamwriter.writerow(['offset', 'token', 'variant 1', 'variant 2', 'variant 3', 'variant 4', 'dialogue act'])
        for tweet in list_of_tweets:
            spamwriter.writerow([])
            spamwriter.writerow([])
            text = tweet.get_text()
            text = text.encode('utf-8')

            spamwriter.writerow([text])
            tokens = tweet.get_token()
            for offset, tags_list in tokens.iteritems():
                word = tweet.get_word(offset)
                word = word.encode('utf-8')
                if len(tags_list) == 1:
                    if 3 in tags_list[0].values():
                        for tag_name, value in tags_list[0].iteritems():
                            spamwriter.writerow([offset, word, '-', '-', '-', '-', tag_name])
                else:
                    data = list()
                    data.append(offset)
                    data.append(word)
                    for tag in tags_list:
                        for tag_name, value in tag.iteritems():
                            data.append(tag_name)
                    spamwriter.writerow(data)

