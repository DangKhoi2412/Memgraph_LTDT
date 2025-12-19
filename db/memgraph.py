# FILE: dangkhoi2412/memgraph_ltdt/Memgraph_LTDT-9204a059e3cbaedf5e3a36c0029fcffe185d10b6/db/memgraph.py

from neo4j import GraphDatabase
import os

class MemgraphClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemgraphClient, cls).__new__(cls)
            cls._instance.driver = None
            
            # Host: 'memgraph-db' trong Docker, 'localhost' ở ngoài
            host = os.getenv("MEMGRAPH_HOST", "memgraph-db")
            uri = f"bolt://{host}:7687"
            
            try:
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
        # Kiểm tra kỹ hơn thay vì chỉ check not None
        try:
            if self.driver:
                self.driver.verify_connectivity()
                return True
        except:
            pass
        return False

    def execute_query(self, query, params=None):
        if not self.driver: return [] # Check driver trực tiếp để tránh overhead verify_connectivity liên tục
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                return [record.data() for record in result]
        except Exception as e:
            print(f"Query Error: {e}")
            return []

    # --- BỔ SUNG HÀM NÀY ĐỂ FIX LỖI ---
    def execute_batch(self, operations):
        """
        Thực thi một danh sách các thao tác trong 1 Transaction duy nhất.
        operations: List of tuples (query, params)
        """
        if not self.driver: return False
        
        try:
            with self.driver.session() as session:
                # Dùng transaction explicit
                with session.begin_transaction() as tx:
                    for query, params in operations:
                        tx.run(query, params)
                    tx.commit() # Chỉ lưu khi TẤT CẢ lệnh đều thành công
            return True
        except Exception as e:
            print(f"❌ Batch Transaction Error: {e}")
            return False