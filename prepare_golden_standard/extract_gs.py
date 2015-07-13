__author__ = 'snownettle'
from mongoDB import mongoDB_configuration
from readData import rawAnnotatedData_read
import annotated_tweets_final



# firstly insert to postgres ontologies!
#insert to mongo
#recalculate depending on ontology

database_name = mongoDB_configuration.db_name
collectionNameAllAnnotations = mongoDB_configuration.collectionNameAllAnnotations

annotatedData_path = mongoDB_configuration.pathToAnnotatedData
annotatedDataRAW_path = mongoDB_configuration.pathAnnotatedDataRAW

# make connection to mongodb
collectionAllAnnotation = mongoDB_configuration.get_collection(database_name, collectionNameAllAnnotations)


if mongoDB_configuration.check_tweets_amount(collectionAllAnnotation) == 0:
    print 'Start inserting to mongoDB...'
    rawAnnotatedData_read.import_annotated_docs(annotatedData_path, collectionAllAnnotation)
    print 'Collection ' + collectionNameAllAnnotations + ' is already existed and has ' \
          + str(mongoDB_configuration.check_tweets_amount(collectionAllAnnotation)) + ' records'
else:
    print 'Collection ' + collectionNameAllAnnotations + ' is already existed and has ' \
          + str(mongoDB_configuration.check_tweets_amount(collectionAllAnnotation)) + ' records'

print '\n' + '\033[1m' + 'Full ontology'
print '\033[0m'
agreed, tweets_to_edit = annotated_tweets_final.iaa_ontologies(collectionAllAnnotation, ontology='full')
print '\n' + '\033[1m' + 'Reduced ontology'
print '\033[0m'
annotated_tweets_final.iaa_ontologies(collectionAllAnnotation, ontology='reduced')
print '\n' + '\033[1m' + 'Minimal ontology'
print '\033[0m'
annotated_tweets_final.iaa_ontologies(collectionAllAnnotation, ontology='minimal')
# merging
# annotated_tweets_final.merging(agreed, tweets_to_edit)

