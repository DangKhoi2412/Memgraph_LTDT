from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("", ""))

def run():
    with driver.session() as session:
        result = session.run("MATCH (n:PersistenceCheck) RETURN n")
        nodes = [r['n'] for r in result]
        print(f"Found {len(nodes)} PersistenceCheck nodes.")
        for n in nodes:
            print(n)

try:
    run()
except Exception as e:
    print(e)
finally:
    driver.close()
