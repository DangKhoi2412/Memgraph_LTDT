from neo4j import GraphDatabase
import os

class MemgraphClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemgraphClient, cls).__new__(cls)
            cls._instance.driver = None
            
            # Host: Trong Docker là 'memgraph-db', Local là 'localhost'
            host = os.getenv("MEMGRAPH_HOST", "memgraph-db")
            uri = f"bolt://{host}:7687"
            
            try:
                # Memgraph mặc định không có user/pass
                driver = GraphDatabase.driver(uri, auth=("", ""))
                driver.verify_connectivity()
                cls._instance.driver = driver
                print(f"✅ Kết nối Memgraph thành công tại {uri}")
            except Exception as e:
                cls._instance.driver = None
                print(f"⚠️ Không thể kết nối DB: {e}")
                
        return cls._instance

    def close(self):
        if self.driver:
            self.driver.close()

    def is_connected(self):
        return self.driver is not None

    def execute_query(self, query, params=None):
        if not self.is_connected():
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                # Trả về list các record (dictionary)
                return [record.data() for record in result]
        except Exception as e:
            print(f"Query Error: {e}")
            return []