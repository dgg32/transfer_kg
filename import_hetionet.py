import json
import sys, os
from neo4j import GraphDatabase

class import_data:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_nodes_connections(self, filename):
        with open(filename) as f:
            data = json.load(f)

            # nodes = data["nodes"]

            # with self.driver.session() as session:
            #     node_type_set = set()
            #     with session.begin_transaction() as tx:
            #         for i, node in enumerate(nodes):
            #             node_type = node['kind']
            #             node_name = node['name']

            #             if node_type + node_name not in node_type_set:
            #                 node_type_set.add(node_type + node_name)
            #                 query = f"MERGE (a:`{node_type}` " + "{"

            #                 for key, value in node.items():
            #                     if key != 'kind' and key != 'data':
            #                         if isinstance(value, str):
            #                             value = value.replace(r"'", r"\'")
            #                         query += f"{key}: '{value}',"
                        
            #                 query = query[:-1] + "});"
            #                 #print (query)
            #                 #break
            #                 tx.run(query)
            #         tx.commit()

            
            edges = data["edges"]

            with self.driver.session() as session:
                
                with session.begin_transaction() as tx:
                    for i, edge in enumerate(edges):
                        source_id = edge['source_id'][1]
                        source_type = edge['source_id'][0]
                        target_id = edge['target_id'][1]
                        target_type = edge['target_id'][0]

                        query = f"MERGE (s:`{source_type}` " + "{" + f'name: "{source_id}"' + "}) "
                        query += f"MERGE (t:`{target_type}` " + "{" + f'name: "{target_id}"' + "}) "
                        query += f"MERGE (s)-[r:`{edge['kind']}`]->(t);"
                        # for key, value in edge.items():
                        #     if key != 'kind' and key != 'data':
                        #         if isinstance(value, str):
                        #             value = value.replace(r"'", r"\'")
                        #         query += f"{key}: '{value}',"
                    
                        #query = query[:-1] + "});"
                        #print (query)
                        #break
                        tx.run(query)
                    tx.commit()
                

import_json_file = "data/new_hetionet.json"

connection = import_data("bolt://localhost:7687", "neo4j", "3344264")


connection.add_nodes_connections(import_json_file)

        #break

connection.close()
