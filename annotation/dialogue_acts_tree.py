__author__ = 'snownettle'


from treelib import Tree


def build_da_taxonomy():
    da_taxonomy = Tree()
    da_taxonomy.create_node('DIT++ Taxonomy', 'DIT++ Taxonomy')

    da_taxonomy.create_node('ADF', 'ADF', parent='DIT++ Taxonomy')

    da_taxonomy.create_node('ADF_Commissive', 'ADF_Commissive', parent='ADF')
    da_taxonomy.create_node('ADF_Commissive_Offer', 'ADF_Commissive_Offer', parent='ADF_Commissive')
    da_taxonomy.create_node('ADF_Commissive_Offer_Promise', 'ADF_Commissive_Offer_Promise',
                            parent='ADF_Commissive_Offer')
    da_taxonomy.create_node('ADF_Commissive_Offer_Threat', 'ADF_Commissive_Offer_Threat',
                            parent='ADF_Commissive_Offer')
    da_taxonomy.create_node('ADF_Commissive_Offer_AddressRequestSuggestion',
                            'ADF_Commissive_Offer_AddressRequestSuggestion',
                            parent='ADF_Commissive_Offer')
    da_taxonomy.create_node('ADF_Commissive_Offer_AddressRequestSuggestion_Accept',
                            'ADF_Commissive_Offer_AddressRequestSuggestion_Accept',
                            parent='ADF_Commissive_Offer_AddressRequestSuggestion')
    da_taxonomy.create_node('ADF_Commissive_Offer_AddressRequestSuggestion_Decline',
                            'ADF_Commissive_Offer_AddressRequestSuggestion_Decline',
                            parent='ADF_Commissive_Offer_AddressRequestSuggestion')

    da_taxonomy.create_node('ADF_Directive', 'ADF_Directive', parent='ADF')
    da_taxonomy.create_node('ADF_Directive_Request', 'ADF_Directive_Request', parent='ADF_Directive')
    da_taxonomy.create_node('ADF_Directive_Suggestion', 'ADF_Directive_Suggestion', parent='ADF_Directive')
    da_taxonomy.create_node('ADF_Directive_AddressOffer', 'ADF_Directive_AddressOffer', parent='ADF_Directive')
    da_taxonomy.create_node('ADF_Directive_AddressOffer_Accept', 'ADF_Directive_AddressOffer_Accept',
                            parent='ADF_Directive_AddressOffer')
    da_taxonomy.create_node('ADF_Directive_AddressOffer_Decline', 'ADF_Directive_AddressOffer_Decline',
                            parent='ADF_Directive_AddressOffer')


    da_taxonomy.create_node('IT', 'IT', parent='DIT++ Taxonomy')
    da_taxonomy.create_node('IT_IP', 'IT_IP', parent='IT')
    da_taxonomy.create_node('IT_IP_Inform', 'IT_IP_Inform', parent='IT_IP')
    da_taxonomy.create_node('IT_IP_Inform_Answer', 'IT_IP_Inform_Answer', parent='IT_IP_Inform')
    da_taxonomy.create_node('IT_IP_Inform_Agreement', 'IT_IP_Inform_Agreement', parent='IT_IP_Inform')
    da_taxonomy.create_node('IT_IP_Inform_Disagreement', 'IT_IP_Inform_Disagreement', parent='IT_IP_Inform')
    da_taxonomy.create_node('IT_IP_Inform_Disagreement_Correction', 'IT_IP_Inform_Disagreement_Correction',
                            parent='IT_IP_Inform_Disagreement')

    da_taxonomy.create_node('IT_IS', 'IT_IS', parent='IT')
    da_taxonomy.create_node('IT_IS_Q', 'IT_IS_Q', parent='IT_IS')
    da_taxonomy.create_node('IT_IS_Q_ChoiceQuestion', 'IT_IS_Q_ChoiceQuestion', parent='IT_IS_Q')
    da_taxonomy.create_node('IT_IS_Q_SetQuestion', 'IT_IS_Q_SetQuestion', parent='IT_IS_Q')
    da_taxonomy.create_node('IT_IS_Q_PropQuestion', 'IT_IS_Q_PropQuestion', parent='IT_IS_Q')
    da_taxonomy.create_node('IT_IS_Q_PropQuestion_CheckQ', 'IT_IS_Q_PropQuestion_CheckQ', parent='IT_IS_Q_PropQuestion')

    da_taxonomy.create_node('DSM', 'DSM', parent='DIT++ Taxonomy')
    da_taxonomy.create_node('DSM_Open', 'DSM_Open', parent='DSM')
    da_taxonomy.create_node('DSM_TopicIntroduction', 'DSM_TopicIntroduction', parent='DSM')
    da_taxonomy.create_node('DSM_TopicShift', 'DSM_TopicShift', parent='DSM')

    da_taxonomy.create_node('OCM', 'OCM', parent='DIT++ Taxonomy')
    da_taxonomy.create_node('OCM_Error', 'OCM_Error', parent='OCM')
    da_taxonomy.create_node('OCM_Retraction', 'OCM_Retraction', parent='OCM')
    da_taxonomy.create_node('OCM_SelfCorrection', 'OCM_SelfCorrection', parent='OCM')

    da_taxonomy.create_node('PCM', 'PCM', parent='DIT++ Taxonomy')
    da_taxonomy.create_node('PCM_Completion', 'PCM_Completion', parent='PCM')
    da_taxonomy.create_node('PCM_Correct', 'PCM_Correct', parent='PCM')


    da_taxonomy.create_node('SOCIAL', 'SOCIAL', parent='DIT++ Taxonomy')

    da_taxonomy.create_node('SOCIAL_Apologize', 'SOCIAL_Apologize', parent='SOCIAL')
    da_taxonomy.create_node('SOCIAL_Apologize_Apology', 'SOCIAL_Apologize_Apology', parent='SOCIAL_Apologize')
    da_taxonomy.create_node('SOCIAL_Apologize_ApologyDownplay', 'SOCIAL_Apologize_ApologyDownplay',
                            parent='SOCIAL_Apologize')

    da_taxonomy.create_node('SOCIAL_Bye', 'SOCIAL_Bye', parent='SOCIAL')
    da_taxonomy.create_node('SOCIAL_Bye_Initial', 'SOCIAL_Bye_Initial', parent='SOCIAL_Bye')
    da_taxonomy.create_node('SOCIAL_Bye_Return', 'SOCIAL_Bye_Return', parent='SOCIAL_Bye')

    da_taxonomy.create_node('SOCIAL_Gratitude', 'SOCIAL_Gratitude', parent='SOCIAL')
    da_taxonomy.create_node('SOCIAL_Gratitude_Thank', 'SOCIAL_Gratitude_Thank', parent='SOCIAL_Gratitude')
    da_taxonomy.create_node('SOCIAL_Gratitude_ThankDownplay', 'SOCIAL_Gratitude_ThankDownplay', parent='SOCIAL_Gratitude')

    da_taxonomy.create_node('SOCIAL_Introduce', 'SOCIAL_Introduce', parent='SOCIAL')
    da_taxonomy.create_node('SOCIAL_Introduce_Initial', 'SOCIAL_Introduce_Initial', parent='SOCIAL_Introduce')
    da_taxonomy.create_node('SOCIAL_Introduce_Return', 'SOCIAL_Introduce_Return', parent='SOCIAL_Introduce')

    da_taxonomy.create_node('SOCIAL_Salutation', 'SOCIAL_Salutation', parent='SOCIAL')
    da_taxonomy.create_node('SOCIAL_Salutation_Greet', 'SOCIAL_Salutation_Greet', parent='SOCIAL_Salutation')
    da_taxonomy.create_node('SOCIAL_Salutation_ReturnGreet', 'SOCIAL_Salutation_ReturnGreet', parent='SOCIAL_Salutation')

    da_taxonomy.create_node('OTHER', 'OTHER', parent='DIT++ Taxonomy')

    da_taxonomy.create_node('0', '0', parent='DIT++ Taxonomy')

    #da_taxonomy.show()
    #print da_taxonomy.depth()
    # print da_taxonomy.is_branch('DIT++ Taxonomy')
    return da_taxonomy


def find_common_parent(taxonomy, tag1, tag2):
    parent1 = taxonomy.parent(tag1).tag
    parent2 = taxonomy.parent(tag2).tag
    if parent1 == parent2:
        return parent1
    else:
        return None


def check_related_tags(taxonomy, tag1, tag2):
    parent1 = taxonomy.parent(tag1).tag
    parent2 = taxonomy.parent(tag2).tag
    if parent1 == tag2:
        return parent1
    elif parent2 == tag1:
        return parent2
    else:
        return None


# tree = build_da_taxonomy()
# root = tree.root
# children =  tree.children(root)
# for child in children:
#     print child.tag
# print type(root)
# print len(tree.all_nodes())





