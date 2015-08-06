__author__ = 'snownettle'
from postgres import postgres_queries, insert_to_table
from da_recognition import matching_schema

# annotate all segments as inform

def assign_inform_da():
    records = postgres_queries.find_all_records('Segmentation')
    da_id_full = postgres_queries.find_da_by_name('IT_IP_Inform', 'dialogue_act_full')
    da_reduced = matching_schema.match_reduced(da_id_full)
    da_id_reduced = postgres_queries.find_da_by_name(da_reduced, 'dialogue_act_reduced')
    da_min = matching_schema.match_min(da_id_full)
    da_id_min = postgres_queries.find_da_by_name(da_min, 'dialogue_act_minimal')
    for record in records:
        tweet_id = record[0]
        # segments_offset = record[1]
        start_offset = record[1]
        end_offset = record[2]
        insert_to_table.insert_into_segmantation_prediction_table(tweet_id, start_offset, end_offset, da_id_full,
                                                                  da_id_reduced, da_id_min)


# assign_inform_da()


