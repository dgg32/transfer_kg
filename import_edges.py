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

            with self.driver.session() as session:
                
                tx = session.begin_transaction()
                for i, edge in enumerate(data):
                    source_id = edge['source_id'][1]
                    source_type = edge['source_id'][0]
                    target_id = edge['target_id'][1]
                    target_type = edge['target_id'][0]

                    query = f"MATCH (s:`{source_type}` " + "{" + f'name: "{source_id}"' + "}) "
                    query += f"MATCH (t:`{target_type}` " + "{" + f'name: "{target_id}"' + "}) "
                    query += f"MERGE (s)-[r:`{edge['kind']}`]->(t);"

                    tx.run(query)

                    if i % 10000 == 0 and i != 0:
                        print(f'{i} edges processed')
                        tx.commit()
                        tx = session.begin_transaction()

                tx.commit()               

import_json_file = sys.argv[1]
ip = sys.argv[2]
password = sys.argv[3]

connection = import_data(f"bolt://{ip}:7687", "neo4j", password)


connection.add_nodes_connections(import_json_file)

        #break

connection.close()
