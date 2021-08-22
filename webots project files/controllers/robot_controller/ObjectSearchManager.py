import re
import nltk
import pandas as dp
from gensim.models import Word2Vec, KeyedVectors

#load w2v model
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary = True, limit = 100000)

def find_object_on_table(table, query_object):
    
    query_object = query_object.lower()
    found = False
    for object in table:
        if object == query_object:
            found = True
    
    return found

def get_list_of_best_match_tables(query_object, table_containers):

    unordered_table_containers = table_containers.copy()

    ordered_table_containers = []

    while len(unordered_table_containers) != 0:

        table, table_index = get_best_match_table_with_table_index(query_object, unordered_table_containers)
        if(table == None and table_index == None):
            ordered_table_containers = ordered_table_containers + unordered_table_containers
            unordered_table_containers.clear()
        else :
            ordered_table_containers.append(table)
            unordered_table_containers.pop(table_index)
    
    return ordered_table_containers


def get_best_match_table(query_object, table_containers):
    """
    finds the table with the object most similar to the query object. similarity check using word2vec

    :param query_object       : object to find
    :param table_containers   : a list of tables, each table is a dictionay with object name and thier global coordinate
    
    :return: the best table and its positon
    """ 

    
    bestSimilarity = None
    best_table_index = None
    table_index = 1

    for table in table_containers:
        for object in list(table.keys())[1:]:
            try:
                similarity = model.similarity(object, query_object)
                
                if (bestSimilarity is None or similarity > bestSimilarity):
                    bestSimilarity = similarity
                    best_table_index = table_index
     
            except Exception:
                continue
        table_index = table_index + 1  

    if best_table_index != None:
            best_table = table_containers[(best_table_index-1)]
    else: 
        best_table = None  

    return best_table

def get_best_match_table_with_table_index(query_object, table_containers):
    """
    finds the table with the object most similar to the query object. similarity check using word2vec

    :param query_object       : object to find
    :param table_containers   : a list of tables, each table is a dictionay with object name and thier global coordinate
    
    :return: the best table and its positon
    """ 

    
    bestSimilarity = None
    best_table_index = None
    table_index = 0

    for table in table_containers:
        for object in list(table.keys())[1:]:
            try:
                similarity = model.similarity(object, query_object)
                
                if (bestSimilarity is None or similarity > bestSimilarity):
                    bestSimilarity = similarity
                    best_table_index = table_index
     
            except Exception:
                continue
        table_index = table_index + 1  

    if best_table_index != None:
            best_table = table_containers[(best_table_index)]
    else: 
        best_table = None  

    return best_table, best_table_index


def tokenize(text):   
    DELIM = '\s|(?<!\d)[,.](?!\d)'  
    return re.split(DELIM, text.lower())