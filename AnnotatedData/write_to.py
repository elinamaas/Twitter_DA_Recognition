__author__ = 'snownettle'
import xlsxwriter
import re


def write_to_xlsx_file(list_of_tweets, file_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    row = 1
    col = 0
    worksheet.write(0, 0, 'offset')
    worksheet.write(0, 1, 'token')
    worksheet.write(0, 2, 'variant 1')
    worksheet.write(0, 3, 'variant 2')
    worksheet.write(0, 4, 'variant 3')
    worksheet.write(0, 5, 'variant 4')
    worksheet.write(0, 6, 'dialogue act')
    for tweet in list_of_tweets:
            text = tweet.get_text()
            tweet_text = re.split('user=', text)[1]
            tweet_text = tweet_text.partition(' ')[2]
            if tweet_text != '':
                worksheet.write(row, col, text)
                row += 1
                tokens = tweet.get_tags()
                for offset, tags_list in tokens.iteritems():
                    word = tweet.get_word(offset)
                    if len(tags_list) == 1:
                        for tag_name, value in tags_list.iteritems():
                            worksheet.write(row, col, offset)
                            worksheet.write(row, col+1, word)
                            worksheet.write(row, col+6, tag_name)
                    else:
                        data = list()
                        data.append(offset)
                        data.append(word)
                        for tag_name, value in tags_list.iteritems():
                            data.append(tag_name)
                        number_of_tags = len(data)
                        for i in range(0, number_of_tags, 1):
                            worksheet.write(row, col + i, data[i])
                    row += 1
                row += 1
            else:
                print tweet.get_text()
    workbook.close()


def write_to_xlsx_file_final(list_of_tweets, file_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    row = 1
    col = 0
    worksheet.write(0, 0, 'offset')
    worksheet.write(0, 1, 'token')
    worksheet.write(0, 2, 'dialogue act')
    for tweet in list_of_tweets:
        text = tweet.get_text()
        worksheet.write(row, col, text)
        row += 1
        tokens = tweet.get_tokens()
        for i in range(4, len(tokens) + 4, 1):
            token_da = tokens[str(i)]
            for token, da in token_da.iteritems():
                worksheet.write(row, col, str(i))
                worksheet.write(row, col+1, token)
                worksheet.write(row, col+2, da)
                row += 1
        row += 1
    workbook.close()