from neo4j import GraphDatabase, basic_auth
import pandas as pd
from typing import List, Dict, Any

class Neo4jHelper:
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=basic_auth(self.username, self.password)
            )
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def test_connection(self):
        """Test database connection"""
        try:
            if not self.driver:
                self.connect()
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, cypher_query: str, parameters: Dict = None) -> Dict[str, Any]:
        """Execute a Cypher query and return JSON-safe results"""
        try:
            if not self.driver:
                self.connect()

            with self.driver.session() as session:
                result = session.run(cypher_query, parameters or {})
                data = []
                for record in result:
                    row = {}
                    for key, value in record.items():
                        if isinstance(value, list):
                            row[key] = [dict(v._properties) if hasattr(v, "_properties") else v for v in value]
                        elif hasattr(value, "_properties"):
                            row[key] = dict(value._properties)
                        else:
                            row[key] = value
                    data.append(row)

                return {"success": True, "data": data, "count": len(data)}

        except Exception as e:
            return {"success": False, "error": str(e), "data": [], "count": 0}
        
        def get_database_summary(self) -> Dict[str, int]:
            """Get summary of nodes in database"""
            query = """
            MATCH (n)
            RETURN labels(n)[0] as label, count(n) as count
            ORDER BY label
            """
            
            result = self.execute_query(query)
            if result["success"]:
                return {item["label"]: item["count"] for item in result["data"]}
            return {}
    
    def get_sample_employees(self, limit: int = 5) -> List[Dict]:
        """Get sample employee data"""
        query = """
        MATCH (e:Employee)
        RETURN e.emp_id as emp_id, e.name as name, e.designation as designation
        LIMIT $limit
        """
        
        result = self.execute_query(query, {"limit": limit})
        return result["data"] if result["success"] else []
    
    def get_schema_info(self) -> Dict[str, List]:
        """Get database schema information"""
        nodes_query = "CALL db.labels() YIELD label RETURN collect(label) as labels"
        rels_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as relationships"
        
        nodes_result = self.execute_query(nodes_query)
        rels_result = self.execute_query(rels_query)
        
        return {
            "nodes": nodes_result["data"][0]["labels"] if nodes_result["success"] else [],
            "relationships": rels_result["data"][0]["relationships"] if rels_result["success"] else []
        }
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()