"""
Data layer for SANBI Ecosystem Risk Atlas
Provides unified access to database operations, queries, and caching
"""

from .database import DatabaseManager, get_database_manager, check_database_health
from .queries import EcosystemQueries
from .cache_manager import (
    CacheManager, 
    get_cache_manager,
    get_cached_biomes,
    get_cached_national_summary,
    get_cached_risk_analysis,
    clear_ecosystem_cache
)

__all__ = [
    # Database operations
    "DatabaseManager",
    "get_database_manager", 
    "check_database_health",
    
    # Query builder
    "EcosystemQueries",
    
    # Cache management
    "CacheManager",
    "get_cache_manager",
    "get_cached_biomes",
    "get_cached_national_summary", 
    "get_cached_risk_analysis",
    "clear_ecosystem_cache"
]

# Data layer health check
def verify_data_layer():
    """Verify that the data layer is properly configured and accessible"""
    health = check_database_health()
    
    status = {
        "database_connected": health["connection"],
        "table_exists": health["table_exists"],
        "data_available": health["data_available"],
        "spatial_data": health["spatial_data"],
        "cache_system": True,  # Cache system is always available
        "error_message": health.get("error_message")
    }
    
    return status

# Quick data access functions
def get_ecosystem_data():
    """Get all essential ecosystem data for the application"""
    try:
        cache_manager = get_cache_manager()
        
        return {
            "biomes": cache_manager.get_biomes(),
            "national_summary": cache_manager.get_national_summary(),
            "risk_analysis": cache_manager.get_comprehensive_risk_analysis(),
            "crisis_ecosystems": cache_manager.get_crisis_ecosystems()
        }
    except Exception as e:
        return {"error": str(e)}