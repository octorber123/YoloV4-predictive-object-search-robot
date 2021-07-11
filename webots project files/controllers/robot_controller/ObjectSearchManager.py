import nltk
import pandas as dp
from gensim.models import Word2Vec, KeyedVectors

#load w2v model
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary = True, limit = 100000)


def find_table_wtih_best_match(query_object, table_containers):
    """
    finds the table with the object most similar to the query object. similarity check using word2vec

    :param query_object       : object to find
    :param table_containers   : a list of tables, each table is a dictionay with object name and thier global coordinate
    
    :return: the best similarity and best table
    """ 

    
    bestSimilarity = None

    table_index = 1
    for table in table_containers:
        for object in table:
            try:
            
                similarity = model.similarity(object, query_object)
                
                if bestSimilarity is None:
                    bestSimilarity = similarity
                    best_table_index = table_index
                    
                elif similarity > bestSimilarity:
                    bestSimilarity = similarity
                    best_table_index = table_index
                          
            except Exception:
                continue
        table_index = table_index + 1    
        
    if(bestSimilarity == None):
        bestSimilarity = None
        best_table_index = None
        
    best_table = "table " + str(best_table_index)
    
    return [bestSimilarity, best_table]
