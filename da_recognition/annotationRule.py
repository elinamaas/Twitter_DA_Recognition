__author__ = 'snownettle'
from postgres import postgres_queries, update_table

def assign_zero_da():
    # @username
    records = postgres_queries.find_all_records('segments_utterance')
    for record in records:
        utterance = record[2]
        start_offset = int(record[1].split(':')[0])
        end_offset = int(record[1].split(':')[1])
        if utterance.startswith('@') or start_offset - end_offset == 0:
            da_name = '0'
            da_id_full = postgres_queries.find_da_by_name(da_name, 'dialogue_act_full')
            da_id_reduced = postgres_queries.find_da_by_name(da_name, 'dialogue_act_reduced')
            da_id_min = postgres_queries.find_da_by_name(da_name, 'dialogue_act_minimal')
            update_table.update_segmentation_prediction_table(record[0], record[1], da_id_full,
                                                              da_id_reduced, da_id_min)

assign_zero_da()
