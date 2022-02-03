import json
import sys, os
from neo4j import GraphDatabase

#python import_node.py <hetionet_data_file> ip


class import_data:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_nodes_connections(self, filename):
        with open(filename) as f:
            data = json.load(f)

            with self.driver.session() as session:
                node_type_set = set()
                with session.begin_transaction() as tx:

                    for i, node in enumerate(data):
                        node_type = node['kind']
                        node_name = node['name'].replace(r"'", r"\'")

                        if node_type + node_name not in node_type_set:
                            node_type_set.add(node_type + node_name)
                            query = f"MERGE (a:`{node_type}` " + "{"

                            for key, value in node.items():
                                if key != 'kind' and key != 'data':
                                    if isinstance(value, str):
                                        value = value.replace(r"'", r"\'")
                                    
                                    if isinstance(value, list):
                                        value = str(value).replace(r"'", r"\'")
                                    query += f"{key}: '{value}',"
                        
                            query = query[:-1] + "});"
                            #print (query)
                            #break
                            tx.run(query)
                    tx.commit()

                

import_json_file = sys.argv[1]
ip = sys.argv[2]
password = sys.argv[3]

connection = import_data(f"bolt://{ip}:7687", "neo4j", password)

connection.add_nodes_connections(import_json_file)

connection.close()
