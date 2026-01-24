"""
Database Connection Pool Manager
Implements connection pooling for PostgreSQL to improve performance
"""
import psycopg2.pool
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class DatabaseManager:
    """
    Singleton pattern para manejar el pool de conexiones de PostgreSQL
    """
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Inicializar el pool de conexiones"""
        try:
            # Configuración del pool
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,  # Mínimo de conexiones
                maxconn=10,  # Máximo de conexiones
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'chatapp'),
                password=os.getenv('DB_PASSWORD', 'chatapp123'),
                database=os.getenv('DB_NAME', 'chatapp'),
                port=int(os.getenv('DB_PORT', 5432))
            )
            logger.info("✅ Connection pool initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing connection pool: {e}")
            raise
    
    def get_connection(self):
        """Obtener una conexión del pool"""
        try:
            connection = self._pool.getconn()
            logger.debug("📡 Connection retrieved from pool")
            return connection
        except Exception as e:
            logger.error(f"❌ Error getting connection from pool: {e}")
            raise
    
    def return_connection(self, connection):
        """Devolver una conexión al pool"""
        try:
            self._pool.putconn(connection)
            logger.debug("📡 Connection returned to pool")
        except Exception as e:
            logger.error(f"❌ Error returning connection to pool: {e}")
    
    def close_all_connections(self):
        """Cerrar todas las conexiones del pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("🔒 All connections closed")

# Instancia global del manager
db_manager = DatabaseManager()
