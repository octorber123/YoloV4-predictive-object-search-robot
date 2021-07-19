import re
import nltk
import pandas as dp
from gensim.models import Word2Vec, KeyedVectors

#load w2v model
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary = True, limit = 100000)

def find_object_on_table(table, query_object):
    
    query_object = query_object.lower()
    print(query_object)
    found = False
    for object in table:
        if object == query_object:
            found = True
    
    return found
            

def get_best_match_table3(query_object, table_containers):
    """
    finds the table with the object most similar to the query object. similarity check using word2vec

    :param query_object       : object to find
    :param table_containers   : a list of tables, each table is a dictionay with object name and thier global coordinate
    
    :return: the best similarity and best table
    """ 

    
    bestSimilarity = None

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
        
    if(bestSimilarity == None):
        bestSimilarity = None
        best_table_index = None
        
        
    best_table = "table " + str(best_table_index)
    

    return [bestSimilarity, best_table]


def get_best_match_table_position(query_object, table_containers):
    """
    finds the table with the object most similar to the query object. similarity check using word2vec

    :param query_object       : object to find
    :param table_containers   : a list of tables, each table is a dictionay with object name and thier global coordinate
    
    :return: the best similarity and best table
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
            best_table = best_table["table_pos"]
    else: 
        best_table = None


    print(best_table)
    

    return best_table

def get_best_match_table(query_object, table_containers):
    """
    finds the table with the object most similar to the query object. similarity check using word2vec

    :param query_object       : object to find
    :param table_containers   : a list of tables, each table is a dictionay with object name and thier global coordinate
    
    :return: the best similarity and best table
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


    print(best_table)
    

    return best_table
def find_table_wtih_best_match_ordered_list(query_object, table_containers):

    table_containers = table_containers
    best_tables_list = []
    master_index = 1
    while master_index != len(table_containers):

        print(master_index)
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
            best_tables_list.append(best_table)
            print("remove " , best_table_index-1)
            table_containers.remove(best_table_index-1)

        master_index = master_index + 1

    return best_tables_list

def tokenize(text):   
    DELIM = '\s|(?<!\d)[,.](?!\d)'  
    return re.split(DELIM, text.lower())