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

    def add_nodes_connections(self, filename, nodetype_1, nodetype_2, relation_type):
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                
                df = pd.read_csv(filename, sep=',')
                
                for index, row in df.iterrows():
                    name_1 = row["from"].replace("'", "\\'")
                    name_2 = row["to"].replace("'", "\\'")

                    query = f"MATCH (s:`{nodetype_1}` " + "{" + f'name: "{name_1}"' + "}) "
                    query += f"MATCH (t:`{nodetype_2}` " + "{" + f'name: "{name_2}"' + "}) "
                    query += f"MERGE (s)-[r:`{relation_type}`]->(t);"

                    tx.run(query)

                    if index % 100 == 0:
                        tx.commit()
                        tx = session.begin_transaction()
                
                tx.commit()

                

import_csv_file = sys.argv[1]
ip = sys.argv[2]
password = sys.argv[3]
nodetype_1 = sys.argv[4]
nodetype_2 = sys.argv[5]
relation_type = sys.argv[6]

connection = import_data(f"bolt://{ip}:7687", "neo4j", password)

connection.add_nodes_connections(import_csv_file, nodetype_1, nodetype_2, relation_type)

connection.close()
