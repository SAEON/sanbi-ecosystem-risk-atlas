"""
Cache management for SANBI Ecosystem Risk Atlas
Optimized caching strategies for database queries and computed results
"""
import streamlit as st
import pandas as pd
import geopandas as gpd
from typing import Dict, Any, Optional, Union
import hashlib
import json
from functools import wraps
import logging

from app.config import CACHE_CONFIG, DatabaseConfig
from data.database import get_database_manager
from data.queries import EcosystemQueries

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching for ecosystem risk data"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.queries = EcosystemQueries(DatabaseConfig())
    
    @staticmethod
    def create_cache_key(prefix: str, **kwargs) -> str:
        """Create a consistent cache key from parameters"""
        # Sort parameters for consistent hashing
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        hash_obj = hashlib.md5(params_str.encode())
        return f"{prefix}_{hash_obj.hexdigest()[:8]}"
    
    # =============================================================================
    # GEOGRAPHIC DATA CACHING
    # =============================================================================
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"], show_spinner=CACHE_CONFIG["show_spinner"])
    def get_biomes(_self) -> pd.DataFrame:
        """Get cached list of all biomes"""
        return _self.db_manager.execute_query(_self.queries.get_biomes())
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_bioregions(_self, biome: Optional[str] = None) -> pd.DataFrame:
        """Get cached list of bioregions"""
        return _self.db_manager.execute_query(_self.queries.get_bioregions(biome))
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_ecosystems(_self, biome: Optional[str] = None, bioregion: Optional[str] = None) -> pd.DataFrame:
        """Get cached list of ecosystems"""
        return _self.db_manager.execute_query(_self.queries.get_ecosystems(biome, bioregion))
    
    # =============================================================================
    # RISK ANALYSIS CACHING
    # =============================================================================
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_habitat_transformation_data(_self) -> pd.DataFrame:
        """Get cached habitat transformation analysis by biome"""
        return _self.db_manager.execute_query(_self.queries.get_habitat_transformation_by_biome())
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_threat_levels_data(_self) -> pd.DataFrame:
        """Get cached threat level analysis by biome"""
        return _self.db_manager.execute_query(_self.queries.get_threat_levels_by_biome())
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_vegetation_vulnerability_data(_self) -> pd.DataFrame:
        """Get cached vegetation vulnerability analysis by biome"""
        return _self.db_manager.execute_query(_self.queries.get_vegetation_vulnerability_by_biome())
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_protection_gaps_data(_self) -> pd.DataFrame:
        """Get cached protection gap analysis by biome"""
        return _self.db_manager.execute_query(_self.queries.get_protection_gaps_by_biome())
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_national_summary(_self) -> Dict[str, Any]:
        """Get cached national summary statistics"""
        result = _self.db_manager.execute_query(_self.queries.get_national_summary())
        return result.iloc[0].to_dict() if not result.empty else {}
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_crisis_ecosystems(_self, limit: int = 10) -> pd.DataFrame:
        """Get cached list of crisis ecosystems"""
        return _self.db_manager.execute_query(_self.queries.get_crisis_ecosystems(limit))
    
    # =============================================================================
    # DETAILED ECOSYSTEM DATA
    # =============================================================================
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_ecosystem_details(_self, biome: Optional[str] = None, 
                            bioregion: Optional[str] = None,
                            ecosystem: Optional[str] = None) -> pd.DataFrame:
        """Get cached detailed ecosystem information"""
        return _self.db_manager.execute_query(
            _self.queries.get_ecosystem_details(biome, bioregion, ecosystem)
        )
    
    # =============================================================================
    # SPATIAL DATA CACHING
    # =============================================================================
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_ecosystem_geometries(_self, biome: Optional[str] = None) -> gpd.GeoDataFrame:
        """Get cached ecosystem geometries for mapping"""
        return _self.db_manager.execute_spatial_query(
            _self.queries.get_ecosystem_geometries(biome)
        )
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_biome_boundaries(_self) -> gpd.GeoDataFrame:
        """Get cached biome boundaries for overview mapping"""
        return _self.db_manager.execute_spatial_query(_self.queries.get_biome_boundaries())
    


    # Need to add these methods to CacheManager class:

    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_ecosystems_by_bioregion(_self, bioregion: str) -> pd.DataFrame:
        """Get ecosystems filtered by bioregion"""
        return _self.db_manager.execute_query(_self.queries.get_ecosystems(bioregion=bioregion))

    @st.cache_data(ttl=CACHE_CONFIG["ttl"]) 
    def get_individual_ecosystem(_self, ecosystem_name: str) -> pd.DataFrame:
        """Get detailed data for a single ecosystem"""
        return _self.db_manager.execute_query(_self.queries.get_ecosystem_details(ecosystem=ecosystem_name))
    
    

    # =============================================================================
    # COMPUTED METRICS CACHING
    # =============================================================================
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_comprehensive_risk_analysis(_self) -> Dict[str, pd.DataFrame]:
        """Get all risk analyses in one cached call"""
        return {
            "habitat_transformation": _self.get_habitat_transformation_data(),
            "threat_levels": _self.get_threat_levels_data(),
            "vegetation_vulnerability": _self.get_vegetation_vulnerability_data(),
            "protection_gaps": _self.get_protection_gaps_data()
        }
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def get_biome_risk_summary(_self, biome: str) -> Dict[str, Any]:
        """Get comprehensive risk summary for a specific biome"""
        # Get detailed data for the biome
        ecosystem_details = _self.get_ecosystem_details(biome=biome)
        
        if ecosystem_details.empty:
            return {}
        
        # Calculate aggregated metrics
        summary = {
            "biome_name": biome,
            "total_ecosystems": len(ecosystem_details),
            "critically_endangered": len(ecosystem_details[ecosystem_details["rlev5"] == "CR"]),
            "endangered": len(ecosystem_details[ecosystem_details["rlev5"] == "EN"]),
            "vulnerable": len(ecosystem_details[ecosystem_details["rlev5"] == "VU"]),
            "avg_natural_habitat": ecosystem_details["pcnat2014"].mean(),
            "avg_annual_decline": ecosystem_details["prcdelyear"].mean(),
            "avg_transformation": ecosystem_details["current_transformation_percentage"].mean(),
            "max_decline_rate": ecosystem_details["prcdelyear"].max(),
            "most_threatened_ecosystem": None,
            "fastest_declining_ecosystem": None
        }
        
        # Find most threatened and fastest declining ecosystems
        if not ecosystem_details.empty:
            threatened_ecosystems = ecosystem_details[ecosystem_details["rlev5"].isin(["CR", "EN"])]
            if not threatened_ecosystems.empty:
                most_threatened = threatened_ecosystems.iloc[0]
                summary["most_threatened_ecosystem"] = {
                    "name": most_threatened["name_18"],
                    "threat_level": most_threatened["rlev5"],
                    "decline_rate": most_threatened["prcdelyear"]
                }
            
            fastest_declining = ecosystem_details.loc[ecosystem_details["prcdelyear"].idxmax()]
            summary["fastest_declining_ecosystem"] = {
                "name": fastest_declining["name_18"],
                "decline_rate": fastest_declining["prcdelyear"],
                "threat_level": fastest_declining["rlev5"]
            }
        
        return summary
    
    # =============================================================================
    # CACHE MANAGEMENT UTILITIES
    # =============================================================================
    
    def clear_all_cache(self):
        """Clear all Streamlit cache"""
        st.cache_data.clear()
        st.cache_resource.clear()
        logger.info("All cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about current cache status"""
        # This is a simplified cache info - Streamlit doesn't expose detailed cache metrics
        return {
            "cache_ttl": CACHE_CONFIG["ttl"],
            "max_entries": CACHE_CONFIG["max_entries"],
            "show_spinner": CACHE_CONFIG["show_spinner"],
            "status": "Cache system active"
        }
    
    def warm_up_cache(self):
        """Pre-load essential data into cache"""
        try:
            # Load critical data that will be used across the application
            logger.info("Starting cache warm-up...")
            
            # Load geographic data
            self.get_biomes()
            self.get_bioregions()
            
            # Load risk analysis data
            self.get_national_summary()
            self.get_comprehensive_risk_analysis()
            self.get_crisis_ecosystems()
            
            # Load spatial boundaries for mapping
            self.get_biome_boundaries()
            
            logger.info("Cache warm-up completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Cache warm-up failed: {e}")
            return False

# Global cache manager instance
@st.cache_resource
def get_cache_manager() -> CacheManager:
    """Get cached instance of CacheManager"""
    return CacheManager()

# Convenience functions for common cache operations
def get_cached_biomes() -> pd.DataFrame:
    """Quick access to cached biomes list"""
    cache_manager = get_cache_manager()
    return cache_manager.get_biomes()

def get_cached_national_summary() -> Dict[str, Any]:
    """Quick access to cached national summary"""
    cache_manager = get_cache_manager()
    return cache_manager.get_national_summary()

def get_cached_risk_analysis() -> Dict[str, pd.DataFrame]:
    """Quick access to cached comprehensive risk analysis"""
    cache_manager = get_cache_manager()
    return cache_manager.get_comprehensive_risk_analysis()

def clear_ecosystem_cache():
    """Clear ecosystem-related cache"""
    cache_manager = get_cache_manager()
    cache_manager.clear_all_cache()
    st.success("Cache cleared successfully!")



