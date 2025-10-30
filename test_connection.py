from neo4j import GraphDatabase

def test_connection():
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "password123")
        )
        driver.verify_connectivity()
        print("✅ Connected to Neo4j successfully!")
        driver.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()