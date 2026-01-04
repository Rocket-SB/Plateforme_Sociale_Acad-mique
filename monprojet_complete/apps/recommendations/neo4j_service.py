from neo4j import GraphDatabase
from django.conf import settings
from functools import lru_cache

class Neo4jDriver:
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_driver()
        return cls._instance

    def _init_driver(self):
        """Initialize Neo4j driver"""
        neo4j_uri = settings.NEO4J_URI
        auth = (
            settings.NEO4J_SETTINGS['username'],
            settings.NEO4J_SETTINGS['password']
        )
        try:
            self._driver = GraphDatabase.driver(neo4j_uri, auth=auth)
            # Test connection
            with self._driver.session(database=settings.NEO4J_SETTINGS['database']) as session:
                session.run("RETURN 1")
            print("✓ Neo4j connected successfully")
        except Exception as e:
            print(f"✗ Neo4j connection failed: {e}")
            self._driver = None

    def get_session(self):
        """Get a Neo4j session"""
        if self._driver is None:
            self._init_driver()
        if self._driver is None:
            return None
        return self._driver.session(database=settings.NEO4J_SETTINGS['database'])

    def close(self):
        """Close driver"""
        if self._driver:
            self._driver.close()


def get_neo4j_driver():
    """Get or create Neo4j driver instance"""
    return Neo4jDriver()
