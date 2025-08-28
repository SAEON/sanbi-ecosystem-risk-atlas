"""
Database connection and session management for SANBI Ecosystem Risk Atlas
"""
import os
import logging
from typing import Dict, Any, Optional
import streamlit as st
import psycopg2
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from app.config import DatabaseConfig, get_database_url, CACHE_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and queries for the ecosystem risk atlas"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self._engine = None
    
    @property
    def engine(self):
        """Lazy initialization of database engine"""
        if self._engine is None:
            try:
                database_url = get_database_url()
                self._engine = create_engine(
                    database_url,
                    poolclass=NullPool,  # Disable connection pooling for Streamlit
                    echo=False
                )
                logger.info("Database engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize database engine: {e}")
                st.error(f"Database connection failed: {e}")
                raise
        return self._engine
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"], show_spinner=CACHE_CONFIG["show_spinner"])
    def execute_query(_self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame
        Note: _self parameter prevents Streamlit from hashing the DatabaseManager instance
        """
        try:
            with _self.engine.connect() as conn:
                if params:
                    result = pd.read_sql(text(query), conn, params=params)
                else:
                    result = pd.read_sql(text(query), conn)
                logger.info(f"Query executed successfully. Returned {len(result)} rows")
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            st.error(f"Database query failed: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def execute_spatial_query(_self, query: str, params: Optional[Dict[str, Any]] = None) -> gpd.GeoDataFrame:
        """
        Execute spatial SQL query and return results as GeoDataFrame
        """
        try:
            with _self.engine.connect() as conn:
                if params:
                    result = gpd.read_postgis(text(query), conn, params=params, geom_col='geometry')
                else:
                    result = gpd.read_postgis(text(query), conn, geom_col='geometry')
                logger.info(f"Spatial query executed successfully. Returned {len(result)} features")
                return result
        except Exception as e:
            logger.error(f"Spatial query execution failed: {e}")
            st.error(f"Spatial query failed: {e}")
            return gpd.GeoDataFrame()
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get basic information about the ecosystem risk table"""
        query = f"""
        SELECT 
            COUNT(*) as total_ecosystems,
            COUNT(DISTINCT biome_18) as total_biomes,
            COUNT(DISTINCT bioregion_) as total_bioregions,
            MIN(pcnat2014) as min_natural_habitat,
            MAX(pcnat2014) as max_natural_habitat,
            AVG(pcnat2014) as avg_natural_habitat
        FROM {self.config.schema}.{self.config.table}
        WHERE pcnat2014 IS NOT NULL
        """
        result = self.execute_query(query)
        return result.iloc[0].to_dict() if not result.empty else {}
    
    def get_connection_info(self) -> Dict[str, str]:
        """Get database connection information for debugging"""
        return {
            "host": self.config.host,
            "port": str(self.config.port),
            "database": self.config.database,
            "schema": self.config.schema,
            "table": self.config.table,
            "connected": str(self.test_connection())
        }

# Global database manager instance
@st.cache_resource
def get_database_manager() -> DatabaseManager:
    """Get cached database manager instance"""
    return DatabaseManager()

def check_database_health() -> Dict[str, Any]:
    """Comprehensive database health check"""
    db_manager = get_database_manager()
    
    health_status = {
        "connection": False,
        "table_exists": False,
        "data_available": False,
        "spatial_data": False,
        "error_message": None
    }
    
    try:
        # Test basic connection
        health_status["connection"] = db_manager.test_connection()
        
        if health_status["connection"]:
            # Check if table exists
            table_check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{db_manager.config.schema}' 
                AND table_name = '{db_manager.config.table}'
            )
            """
            result = db_manager.execute_query(table_check_query)
            health_status["table_exists"] = result.iloc[0, 0] if not result.empty else False
            
            if health_status["table_exists"]:
                # Check if data is available
                count_query = f"SELECT COUNT(*) FROM {db_manager.config.schema}.{db_manager.config.table}"
                result = db_manager.execute_query(count_query)
                count = result.iloc[0, 0] if not result.empty else 0
                health_status["data_available"] = count > 0
                
                # Check spatial data
                spatial_query = f"""
                SELECT COUNT(*) FROM {db_manager.config.schema}.{db_manager.config.table} 
                WHERE geometry IS NOT NULL
                """
                result = db_manager.execute_query(spatial_query)
                spatial_count = result.iloc[0, 0] if not result.empty else 0
                health_status["spatial_data"] = spatial_count > 0
                
    except Exception as e:
        health_status["error_message"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_status