import json
import sys, os
from neo4j import GraphDatabase
import pandas as pd
#python import_node.py <hetionet_data_file> ip


class import_data:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_nodes_connections(self, filename, node_type):
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                
                df = pd.read_csv(filename, sep=',')
                
                for index, row in df.iterrows():
                    name = row["name"].replace("'", "\\'")

                    properties = {}
                    for k in df.columns:
                        if k != "name":
                            v = row[k]
                            
                            if isinstance(v, str):
                                v = v.replace("'", "\\'")

                            if isinstance(v, list):
                                v = str(v).replace(r"'", r"\'")

                            properties[k] = v
                    
                    query = f"MERGE (a:`{node_type}` " + "{" + "name: " + f"'{name}'" + "}) "
                    query += f"ON CREATE SET "
                    
                    for k in properties:
                        query += f"a.{k} = '{properties[k]}', "
                    
                    query = query[:-2]
                    query += "ON MATCH SET "
                    for k in properties:
                        query += f"a.{k} = '{properties[k]}', "

                    query = query[:-2] 
                    query += ";"
                    #print ("query:", query)
                    tx.run(query)

                    if index % 100 == 0:
                        tx.commit()
                        tx = session.begin_transaction()
                
                tx.commit()

                

import_csv_file = sys.argv[1]
ip = sys.argv[2]
password = sys.argv[3]
node_type = sys.argv[4]

connection = import_data(f"bolt://{ip}:7687", "neo4j", password)

connection.add_nodes_connections(import_csv_file, node_type)

connection.close()
