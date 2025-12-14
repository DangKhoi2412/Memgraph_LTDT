from neo4j import GraphDatabase
import streamlit as st
import os

class MemgraphClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemgraphClient, cls).__new__(cls)
            cls._instance.driver = None
            
            # Lấy host từ Docker Compose
            host = os.getenv("MEMGRAPH_HOST", "127.0.0.1")
            uri = f"bolt://{host}:7687"
            
            try:
                # Kết nối dùng Neo4j driver (Tương thích 100% với Memgraph)
                driver = GraphDatabase.driver(uri, auth=("", ""))
                driver.verify_connectivity()
                cls._instance.driver = driver
                print(f"✅ Kết nối Memgraph (qua Neo4j Driver) thành công tại {uri}!")
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
                # Chuyển kết quả Neo4j thành List các Dictionary (Python chuẩn)
                return [record.data() for record in result]
        except Exception as e:
            st.error(f"Lỗi truy vấn: {e}")
            return []