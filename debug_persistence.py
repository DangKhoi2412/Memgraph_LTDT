from neo4j import GraphDatabase
import time

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("", ""))

def run():
    with driver.session() as session:
        # Create Data
        session.run("CREATE (:PersistenceCheck {timestamp: $t})", t=time.time())
        print("created node")
        
        # Snapshot
        session.run("CREATE SNAPSHOT")
        print("snapshot created")

try:
    run()
except Exception as e:
    print(e)
finally:
    driver.close()
