import math

def assign_list_of_objects_to_tables(table_containers, objects):
    """
    assigns object to the tables

    
    :param table_containers   : a list of tables, each table is a dictionary.
    :param objects            : dictionary containing objects
    
    :return: None
    """
 
    for object in objects:
           
        shortest = 1500
        shortest_table = None
        for table in table_containers:

            distance = math.sqrt((object[1][0] - table["table_pos"][0])**2 + (object[1][1] - table["table_pos"][1])**2)
    
            if distance < shortest:
                shortest = distance
                shortest_table = table
                
        if(shortest != 1500 and shortest_table != None):
            shortest_table[object[0]] = object[1]
   
