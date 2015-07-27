# from postgres.postgres_queries import find_all_records, da_full_table

__author__ = 'snownettle'
from da_recognition import dialogue_acts_taxonomy
from postgres import postgres_queries, postgres_configuration
#we have three types of DIT++ schema. But the annotated data was only for


def match_reduced(da_name_full):
    if type(da_name_full) is not str:
        da_name_full = postgres_queries.find_da_by_id(da_name_full, 'dialogue_act_full')
    full_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_full()
    reduced_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_reduced()
    if reduced_taxonomy.contains(da_name_full):
        return da_name_full
    else:
        parent_name = full_taxonomy.parent(da_name_full)
        return match_reduced(parent_name.tag)


def match_min(da_name_full):
    if type(da_name_full) is not str:
        da_name_full = postgres_queries.find_da_by_id(da_name_full, 'dialogue_act_full')
    full_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_full()
    min_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_minimal()
    if min_taxonomy.contains(da_name_full):
        return da_name_full
    else:
        parent_name = full_taxonomy.parent(da_name_full)
        return match_min(parent_name.tag)


def merge_ontologies():
    results = postgres_queries.find_all_records(postgres_configuration.fullOntologyTable)
    merged_ontologies = dict()
    for record in results:
        da_full = record[1]
        da_id_full = record[0]
        da_reduced = match_reduced(da_id_full)
        da_minimal = match_min(da_id_full)
        merged_ontologies[da_full] = [da_reduced, da_minimal]
    return merged_ontologies

