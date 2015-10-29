__author__ = 'snownettle'
from postgres import postgres_configuration
from analysing_GS import analysis
from prepare_gold_standard import rebuild_conversations


def stats_for_gold_standard():
    taxonomies = ['full', 'reduced', 'minimal']
    connection, cursor = postgres_configuration.make_connection()
    conversations_list = rebuild_conversations.build_conversation(cursor)
    analysis.deep_distribution(conversations_list)
    long_conversations_list, short_conversations_list = analysis.conversation_length_amount(conversations_list)
    analysis.overall_segments(cursor)
    analysis.segments_distribution(cursor)
    analysis.feature_distribution(cursor)
    for taxonomy in taxonomies:
        print taxonomy + ' taxonomy'
        analysis.da_unigrams(taxonomy, cursor)
        # print 'lengh distributation'
        # analysis.length_distribution_in_da(taxonomy, cursor)
        print 'bigrams'
        analysis.da_bigrams(conversations_list, taxonomy, cursor)
        # print 'bigram in long conversations'
        # analysis.da_bigrams(long_conversations_list, taxonomy, cursor)
        # print 'bigrams in short conversations'
        # analysis.da_bigrams(short_conversations_list, taxonomy, cursor)


stats_for_gold_standard()



