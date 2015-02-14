__author__ = 'snownettle'
# coding=utf-8

#
# def replace_german_letters(text):
#     german_letters =['ö', 'Ö', 'ä', 'Ä', 'ü', 'Ü', 'ß']
#     text = text.replace('’', '_')
#     text = text.replace('‘', '_')
#     text = text.replace('"', '')
#     text = text.replace('.', '_')
#     text = text.replace('…', '_')
#     text = text.replace('²', '2')
#     text = text.replace('≠', '<>')
#     text = text.replace('€', 'Euro')
#     text = text.replace('͡°', '->')
#     text = text.replace('͜͜ʖ', '?')
#     text = text.replace('ʖ', '?')
#     text = text.replace('͜?', '?')
#     text = text.replace('͡o', '?')
#     text = text.replace('Wo', 'Wo')
#     text = text.replace('?', '?')
#     for letter in german_letters:
#         if letter in text:
#             text = text.replace('ö', 'oe').replace('Ö', 'Oe')
#             text = text.replace('ä', 'ae').replace('Ä', 'Ae')
#             text = text.replace('ü', 'ue').replace('Ü', 'Ue')
#             text = text.replace('ß', 'ss')
#     return text
