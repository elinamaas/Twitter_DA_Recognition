__author__ = 'snownettle'
import csv
import xlsxwriter


# def write_to_file(list_of_tweets, file_name):
#     with open(file_name, 'wb') as csvfile:
#         spamwriter = csv.writer(csvfile, delimiter=';',)
#         spamwriter.writerow(['offset', 'token', 'variant 1', 'variant 2', 'variant 3', 'variant 4', 'dialogue act'])
#         for tweet in list_of_tweets:
#             spamwriter.writerow([])
#             spamwriter.writerow([])
#             text = tweet.get_text()
#             text = text.encode('utf')
#             # text = unicode(text)
#
#             spamwriter.writerow([text])
#             tokens = tweet.get_tags()
#             for offset, tags_list in tokens.iteritems():
#                 word = tweet.get_word(offset)
#                 word = word.encode('utf-8')
#                 # word = unicode(word)
#                 if len(tags_list) == 1:
#                     for tag_name, value in tags_list.iteritems():
#                         spamwriter.writerow([offset, word, '-', '-', '-', '-', tag_name])
#                 else:
#                     data = list()
#                     data.append(offset)
#                     data.append(word)
#                     for tag_name, value in tags_list.iteritems():
#                         data.append(tag_name)
#                     spamwriter.writerow(data)

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
    workbook.close()