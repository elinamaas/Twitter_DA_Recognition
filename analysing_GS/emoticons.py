# encoding: utf-8
from postgres import postgres_configuration, postgres_queries
__author__ = 'snownettle'


def emoticons_lib():
    emoticons_string = '(。＞0＜。) XD :-) :) :D :o) :] :3 :c) :> =] 8) =) :} :^) :っ) :-D 8-D 8D x-D xD X-D XD =-D =D =-3 =3 B^D ' \
                       ':-)) >:[ :-( :( :-c :c :-< :っC :< :-[ :[ :{ ;( :-|| :@ >:( :\'-( :\'( :\'-) :\') D:< D: D8 ' \
                       'D; D= DX v.v D-\': >:O :-O :O :-o :o 8-0 O_O o-o O_o o_O o_o O-O :* :^* ( \'}{\' ) ;-) ;) *-) ' \
                       '*) ;-] ;] ;D ;^) :-, >:P :-P :P X-P x-p xp XP :-p :p =p :-Þ :Þ :þ :-þ :-b :b d: >:\ >:/ :-/ ' \
                       ':-. :/ :\ =/ =\ :L =L :S >.< :| :-| :$ :-X :X :-# :# O:-) 0:-3 0:3 0:-) 0:) 0;^) >:) >;) >:-) ' \
                       '}:-) }:) 3:-) 3:) o/\o ^5 >_>^ ^<_< |;-) |-O :-J :-& :& #-) %-) %) Drunk,[8] :-###.. :###.. ' \
                       '<:-| ಠ_ಠ <*)))-{ ><(((*> ><> \o/ *\\0/* @}-;-\'--- @>-->-- ~(_8^(I) 5:-) ~:-\ //0-0\\\\ *<|:-) ' \
                       '=:o] ,:-) 7:^] <3 </3 ;-) ;) :/ ;)) ;))) xD ;-D *Lach* *Cool* XD (。＞0＜。)'

    emoticons_list = emoticons_string.split(' ')
    return emoticons_list


# def count_emoticons():
#     conn, cur = postgres_configuration.make_connection()
#     emoticons_list = emoticons_lib()
#     records = postgres_queries.find_all_records('segments_utterance', cur)
#     f = 0
#     nf = 0
#     print len(records)
#     for record in records:
#         # if 'http:' not in record[3]:
#         #     a = any(emoticon in emoticons_list for emoticon in record[3])
#         # if a is True:
#         #     print record[3]
#         #     f += 1
#         # else:
#         #     nf += 1
#         for emoticon in emoticons_list:
#             if emoticon in record[3] and 'http:' not in record[3]:
#                 print record[3]
#                 f += 1
#                 break
#
#     print 'true ' + str(f)
#     print 'false ' + str(nf)
#     postgres_configuration.close_connection(conn)
#
# count_emoticons()