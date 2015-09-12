from postgres import postgres_configuration
from postgres.postgres_queries import find_all_records, find_da_by_name, find_da_by_id
from da_recognition import dialogue_acts_taxonomy

__author__ = 'snownettle'
#we have three types of DIT++ schema. But the annotated data was only for


def match_reduced(da_name_full, cursor):
    if type(da_name_full) is not str:
        da_name_full = find_da_by_id(da_name_full, 'dialogue_act_full', cursor)
    full_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_full()
    reduced_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_reduced()
    if reduced_taxonomy.contains(da_name_full):
        return da_name_full
    else:
        parent_name = full_taxonomy.parent(da_name_full)
        return match_reduced(parent_name.tag, cursor)


def match_min(da_name_full, cursor):
    if type(da_name_full) is not str:
        da_name_full = find_da_by_id(da_name_full, 'dialogue_act_full', cursor)
    full_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_full()
    min_taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_minimal()
    if min_taxonomy.contains(da_name_full):
        return da_name_full
    else:
        parent_name = full_taxonomy.parent(da_name_full)
        return match_min(parent_name.tag, cursor)


def merge_ontologies(cursor):
    results = find_all_records(postgres_configuration.fullOntologyTable, cursor)
    merged_ontologies = dict()
    for record in results:
        da_full = record[1]
        da_id_full = record[0]
        da_reduced = match_reduced(da_id_full)
        da_minimal = match_min(da_id_full)
        merged_ontologies[da_full] = [da_reduced, da_minimal]
    return merged_ontologies


def make_ontology_dict(cursor):
    ontology_dict = dict()
    da_full = find_all_records(postgres_configuration.fullOntologyTable, cursor)
    for da in da_full:
        da_full_name = da[1]
        da_id_full = da[0]
        da_reduced = match_reduced(da_id_full, cursor)
        da_id_reduced = find_da_by_name(da_reduced, 'dialogue_act_reduced', cursor)
        da_min = match_min(da_id_full, cursor)
        da_id_min = find_da_by_name(da_min, 'dialogue_act_minimal', cursor)
        ontology_dict[da_full_name] = [da_id_full, da_id_reduced, da_id_min]
    return ontology_dict
