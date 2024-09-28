from neo4j import GraphDatabase


uri = "bolt://localhost:7687"
username = "neo4j"
password = "pranit1812"

def test_connection():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' AS message")
            record = result.single()
            print(record["message"])
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    test_connection()
