import os
import logging
from typing import List, Tuple, Dict, Any, Optional
from neo4j import GraphDatabase, Driver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GraphRepository:
    """
    Singleton Repository for Memgraph Database interactions.
    Handles connection management, query execution, and data synchronization.
    """
    _instance = None
    driver: Optional[Driver] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphRepository, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize database connection securely."""
        self.driver = None
        host = os.getenv("MEMGRAPH_HOST", "memgraph-db")
        uri = f"bolt://{host}:7687"
        
        try:
            # Memgraph CE (Community Edition) typically doesn't use auth by default in this setup
            self.driver = GraphDatabase.driver(uri, auth=("", ""))
            self.driver.verify_connectivity()
            logger.info(f"✅ Connected to Memgraph at {uri}")
        except Exception as e:
            logger.error(f"⚠️ Connection Failed: {e}")
            self.driver = None

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    @property
    def is_connected(self) -> bool:
        """Check if driver is active and connected."""
        try:
            if self.driver:
                self.driver.verify_connectivity()
                return True
        except Exception:
            pass
        return False

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return dictionary results."""
        if not self.driver:
            raise ConnectionError("Database driver is not initialized.")
            
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def get_all_nodes_and_edges(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Retrieve existing graph structure from database.
        Returns: (List of Node Names, List of Edge Dictionaries)
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to Memgraph")

        # 1. Fetch Nodes
        # Using list comprehension for speed
        raw_nodes = self.execute_query("MATCH (n:Node) RETURN n.name as name")
        nodes = [str(r['name']) for r in raw_nodes if r.get('name')]

        # 2. Fetch Edges
        # Always assume directed for this application
        q_edges = """
        MATCH (u:Node)-[r:LINK]->(v:Node) 
        RETURN u.name as source, v.name as target, r.weight as weight
        """
        raw_edges = self.execute_query(q_edges)
        
        edges = []
        for r in raw_edges:
            src = r.get('source')
            tgt = r.get('target')
            
            # Safe integer conversion for weight
            try:
                w = int(r.get('weight', 1))
            except (ValueError, TypeError):
                w = 1

            if src and tgt:
                edges.append({
                    "source": str(src), 
                    "target": str(tgt), 
                    "weight": w 
                })
        
        logger.info(f"📥 Loaded {len(nodes)} nodes, {len(edges)} edges.")
        return nodes, edges

    def sync_graph(self, nodes: List[str], edges: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Synchronize in-memory graph state to the database securely.
        Implements: Indexing -> Transactional Write -> Snapshot -> Verification.
        """
        if not self.is_connected:
             return False, "Not connected to Memgraph"

        try:
            with self.driver.session() as session:
                # 1. Optimization: Ensure Index exists
                try:
                    session.run("CREATE INDEX ON :Node(name)")
                except Exception: 
                    pass # Ignore if index already exists or syntax differs by version

                # 2. Atomic Transaction: Write Data
                with session.begin_transaction() as tx:
                    # Merge Nodes
                    if nodes:
                        q_nodes = "UNWIND $batch as name MERGE (:Node {name: name})"
                        # Sanitize strings
                        node_data = [str(n).strip() for n in nodes]
                        tx.run(q_nodes, {"batch": node_data})

                    # Delete ALL existing edges to prevent staleness
                    tx.run("MATCH ()-[r:LINK]->() DELETE r")

                    # Create New Edges
                    # Uses CREATE instead of MERGE to bypass "edge property disabled" restrictions
                    if edges:
                        q_edges = """
                        UNWIND $batch as e
                        MATCH (u:Node {name: e.source})
                        MATCH (v:Node {name: e.target})
                        CREATE (u)-[:LINK {weight: e.weight}]->(v)
                        """
                        edge_data = []
                        for e in edges:
                            s = str(e.get('source', '')).strip()
                            t = str(e.get('target', '')).strip()
                            w_raw = e.get('weight', 1)
                            try: w = int(w_raw) 
                            except: w = 1
                            
                            if s and t:
                                edge_data.append({"source": s, "target": t, "weight": w})
                        
                        if edge_data:
                            tx.run(q_edges, {"batch": edge_data})
                            
                    tx.commit()
            
            # 3. Persistence: Force Snapshot to Disk
            try:
                with self.driver.session() as session:
                    session.run("CREATE SNAPSHOT")
            except Exception as e:
                logger.warning(f"Snapshot Failed (Data might be volatile): {e}")

            # 4. Integrity Check: Verify Data was Written
            if edges:
                check_q = "MATCH ()-[r:LINK]->() RETURN count(r) as c"
                count_res = self.execute_query(check_q)
                count = count_res[0]['c'] if count_res else 0
                
                if count == 0:
                    return False, "Sync failed: Database confirmed 0 edges after write."
                
                verify_msg = f"(Verified: {count})"
            else:
                verify_msg = "(Empty Graph)"

            msg = f"Saved {len(nodes)} nodes, {len(edges)} edges. {verify_msg}"
            logger.info(f"✅ {msg}")
            return True, msg
            
        except Exception as e:
            logger.error(f"Sync Error: {e}")
            return False, str(e)

    def clear_database(self) -> None:
        """Dangerous: Wipes entire database."""
        if not self.is_connected: return
        try:
            self.execute_query("MATCH (n) DETACH DELETE n")
            logger.warning("Database Wiped.")
        except Exception as e:
            logger.error(f"Clear DB Error: {e}")
