"""
SQL Queries for SANBI Ecosystem Risk Atlas
All queries for ecosystem risk analysis and geographic filtering
"""
from typing import Dict, List, Optional, Any
import pandas as pd
import geopandas as gpd
from app.config import DatabaseConfig

class EcosystemQueries:
    """SQL queries for ecosystem risk analysis"""
    
    def __init__(self, db_config: DatabaseConfig):
        self.schema = db_config.schema
        self.table = db_config.table
        self.full_table = f"{self.schema}.{self.table}"
    
    # =============================================================================
    # GEOGRAPHIC FILTERING QUERIES
    # =============================================================================
    
    def get_biomes(self) -> str:
        """Get all available biomes"""
        return f"""
        SELECT DISTINCT 
            biome_18,
            COUNT(*) as ecosystem_count
        FROM {self.full_table}
        WHERE biome_18 IS NOT NULL 
        AND biome_18 != ' ' 
        AND biome_18 != '<Null>'
        GROUP BY biome_18
        ORDER BY biome_18
        """
    
    def get_bioregions(self, biome: Optional[str] = None) -> str:
        """Get bioregions, optionally filtered by biome"""
        where_clause = "WHERE bioregion_ IS NOT NULL AND bioregion_ != ''"
        if biome:
            where_clause += f" AND biome_18 = '{biome}'"
        
        return f"""
        SELECT DISTINCT 
            bioregion_,
            biome_18,
            COUNT(*) as ecosystem_count
        FROM {self.full_table}
        {where_clause}
        GROUP BY bioregion_, biome_18
        ORDER BY bioregion_
        """
    
    def get_ecosystems(self, biome: Optional[str] = None, bioregion: Optional[str] = None) -> str:
        """Get individual ecosystems, optionally filtered"""
        where_conditions = ["name_18 IS NOT NULL", "name_18 != ''"]
        
        if biome:
            where_conditions.append(f"biome_18 = '{biome}'")
        if bioregion:
            where_conditions.append(f"bioregion_ = '{bioregion}'")
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        return f"""
        SELECT 
            name_18,
            mapcode18,
            biome_18,
            bioregion_,
            rlev5,
            pcnat2014,
            prcdelyear,
            cnsrv_trgt,
            pl_2018
        FROM {self.full_table}
        {where_clause}
        ORDER BY name_18
        """
    
    # =============================================================================
    # RISK ANALYSIS QUERIES
    # =============================================================================
    
    def get_habitat_transformation_by_biome(self) -> str:
        """🌿 Ecosystem degradation risk - habitat transformation by biome"""
        return f"""
        SELECT 
            biome_18,
            COUNT(*) as ecosystem_count,
            AVG(prcnat1990) as avg_natural_1990,
            AVG(pcnat2014) as avg_natural_2014,
            AVG(pcnat2040a) as avg_natural_2040_projected,
            AVG(prcnat1990 - pcnat2014) as avg_habitat_loss_24_years,
            AVG(pcnat2014 - pcnat2040a) as avg_projected_loss_26_years,
            AVG(100 - pcnat2014) as avg_transformation_percentage
        FROM {self.full_table}
        WHERE biome_18 IS NOT NULL 
        AND biome_18 NOT IN ('', '<Null>', ' ')
        AND prcnat1990 IS NOT NULL 
        AND pcnat2014 IS NOT NULL
        GROUP BY biome_18
        ORDER BY avg_habitat_loss_24_years DESC
        """
    
    def get_threat_levels_by_biome(self) -> str:
        """🦎 Biodiversity threat distribution by biome"""
        return f"""
        SELECT 
            biome_18,
            COUNT(*) as total_ecosystems,
            COUNT(CASE WHEN rlev5 = 'CR' THEN 1 END) as critically_endangered,
            COUNT(CASE WHEN rlev5 = 'EN' THEN 1 END) as endangered,
            COUNT(CASE WHEN rlev5 = 'VU' THEN 1 END) as vulnerable,
            COUNT(CASE WHEN rlev5 = 'NT' THEN 1 END) as near_threatened,
            COUNT(CASE WHEN rlev5 = 'LC' THEN 1 END) as least_concern,
            COUNT(CASE WHEN rlev5 IN ('CR', 'EN') THEN 1 END) as high_threat_total,
            ROUND(COUNT(CASE WHEN rlev5 IN ('CR', 'EN') THEN 1 END) * 100.0 / COUNT(*), 2) as high_threat_percentage
        FROM {self.full_table}
        WHERE biome_18 IS NOT NULL 
        AND biome_18 NOT IN ('', '<Null>', ' ')
        AND rlev5 IS NOT NULL
        GROUP BY biome_18
        ORDER BY high_threat_percentage DESC
        """
    
    def get_vegetation_vulnerability_by_biome(self) -> str:
        """🌱 Vegetation vulnerability - decline rates by biome"""
        return f"""
        SELECT 
            biome_18,
            COUNT(*) as ecosystem_count,
            AVG(prcdelyear) as avg_annual_decline,
            AVG(degrext) as avg_degradation_extent,
            MAX(prcdelyear) as max_annual_decline,
            COUNT(CASE WHEN prcdelyear > 0.2 THEN 1 END) as high_decline_ecosystems
        FROM {self.full_table}
        WHERE biome_18 IS NOT NULL 
        AND biome_18 NOT IN ('', '<Null>', ' ')
        AND prcdelyear IS NOT NULL
        GROUP BY biome_18
        ORDER BY avg_annual_decline DESC
        """
    
    def get_protection_gaps_by_biome(self) -> str:
        """🛡️ Conservation gap analysis by biome"""
        return f"""
        SELECT 
            biome_18,
            COUNT(*) as ecosystem_count,
            AVG(cnsrv_trgt) as avg_conservation_target,
            COUNT(CASE WHEN pl_2018 = 'NP' THEN 1 END) as not_protected,
            COUNT(CASE WHEN pl_2018 = 'PP' THEN 1 END) as poorly_protected,
            COUNT(CASE WHEN pl_2018 = 'MP' THEN 1 END) as moderately_protected,
            COUNT(CASE WHEN pl_2018 = 'WP' THEN 1 END) as well_protected,
            ROUND(COUNT(CASE WHEN pl_2018 IN ('NP', 'PP') THEN 1 END) * 100.0 / COUNT(*), 2) as inadequate_protection_percentage
        FROM {self.full_table}
        WHERE biome_18 IS NOT NULL 
        AND biome_18 NOT IN ('', '<Null>', ' ')
        AND cnsrv_trgt IS NOT NULL
        GROUP BY biome_18
        ORDER BY inadequate_protection_percentage DESC
        """
    
    # =============================================================================
    # DETAILED ECOSYSTEM QUERIES
    # =============================================================================
    
    def get_ecosystem_details(self, biome: Optional[str] = None, 
                            bioregion: Optional[str] = None,
                            ecosystem: Optional[str] = None) -> str:
        """Get detailed information for specific ecosystem(s)"""
        where_conditions = [
            "name_18 IS NOT NULL",
            "biome_18 NOT IN ('', '<Null>', ' ')"
        ]
        
        if biome:
            where_conditions.append(f"biome_18 = '{biome}'")
        if bioregion:
            where_conditions.append(f"bioregion_ = '{bioregion}'")
        if ecosystem:
            where_conditions.append(f"name_18 = '{ecosystem}'")
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        return f"""
        SELECT 
            name_18,
            mapcode18,
            biome_18,
            bioregion_,
            rlev5,
            cnsrv_trgt,
            prcnat1990,
            pcnat2014,
            pcnat2040a,
            prcdelyear,
            degrext,
            pl_2018,
            endemic,
            eoo,
            aoo,
            ytc,
            ytc_class,
            -- Calculate derived risk metrics
            (prcnat1990 - pcnat2014) as habitat_loss_24_years,
            (pcnat2014 - pcnat2040a) as projected_loss_26_years,
            (100 - pcnat2014) as current_transformation_percentage,
            -- Risk categorization
            CASE 
                WHEN rlev5 = 'CR' THEN 5
                WHEN rlev5 = 'EN' THEN 4
                WHEN rlev5 = 'VU' THEN 3
                WHEN rlev5 = 'NT' THEN 2
                WHEN rlev5 = 'LC' THEN 1
                ELSE 0
            END as threat_score
        FROM {self.full_table}
        {where_clause}
        ORDER BY 
            CASE 
                WHEN rlev5 = 'CR' THEN 1
                WHEN rlev5 = 'EN' THEN 2
                WHEN rlev5 = 'VU' THEN 3
                WHEN rlev5 = 'NT' THEN 4
                WHEN rlev5 = 'LC' THEN 5
                ELSE 6
            END,
            prcdelyear DESC,
            name_18
        """
    
    # =============================================================================
    # SPATIAL QUERIES
    # =============================================================================
    
    def get_ecosystem_geometries(self, biome: Optional[str] = None) -> str:
        """Get ecosystem geometries for mapping"""
        where_conditions = [
            "geometry IS NOT NULL",
            "biome_18 NOT IN ('', '<Null>', ' ')"
        ]
        
        if biome:
            where_conditions.append(f"biome_18 = '{biome}'")
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        return f"""
        SELECT 
            name_18,
            mapcode18,
            biome_18,
            bioregion_,
            rlev5,
            pcnat2014,
            prcdelyear,
            (100 - pcnat2014) as transformation_percentage
        FROM {self.full_table}
        {where_clause}
        ORDER BY name_18
        """
    
    def get_biome_boundaries(self) -> str:
        """Get dissolved biome boundaries for overview mapping"""
        return f"""
        SELECT 
            biome_18,
            COUNT(*) as ecosystem_count,
            AVG(pcnat2014) as avg_natural_habitat,
            AVG(prcdelyear) as avg_decline_rate,
            COUNT(CASE WHEN rlev5 IN ('CR', 'EN') THEN 1 END) as threatened_ecosystems
        FROM {self.full_table}
        WHERE biome_18 NOT IN ('', '<Null>', ' ')
        GROUP BY biome_18
        ORDER BY biome_18
        """
    
    # =============================================================================
    # SUMMARY STATISTICS
    # =============================================================================
    
    def get_national_summary(self) -> str:
        """Get national-level ecosystem risk summary"""
        return f"""
        SELECT 
            COUNT(*) as total_ecosystems,
            COUNT(DISTINCT biome_18) as total_biomes,
            COUNT(DISTINCT bioregion_) as total_bioregions,
            
            -- Threat level summary
            COUNT(CASE WHEN rlev5 = 'CR' THEN 1 END) as critically_endangered,
            COUNT(CASE WHEN rlev5 = 'EN' THEN 1 END) as endangered,
            COUNT(CASE WHEN rlev5 = 'VU' THEN 1 END) as vulnerable,
            COUNT(CASE WHEN rlev5 = 'LC' THEN 1 END) as least_concern,
            
            -- Habitat metrics
            AVG(pcnat2014) as avg_natural_habitat,
            AVG(prcdelyear) as avg_annual_decline,
            AVG(100 - pcnat2014) as avg_transformation,
            
            -- Protection metrics
            AVG(cnsrv_trgt) as avg_conservation_target,
            COUNT(CASE WHEN pl_2018 IN ('NP', 'PP') THEN 1 END) as inadequately_protected,
            
            -- Risk calculations
            ROUND(COUNT(CASE WHEN rlev5 IN ('CR', 'EN') THEN 1 END) * 100.0 / COUNT(*), 2) as high_threat_percentage,
            ROUND(COUNT(CASE WHEN pl_2018 IN ('NP', 'PP') THEN 1 END) * 100.0 / COUNT(*), 2) as inadequate_protection_percentage
        FROM {self.full_table}
        WHERE biome_18 NOT IN ('', '<Null>', ' ')
        """
    
    def get_crisis_ecosystems(self, limit: int = 10) -> str:
        """Get top crisis ecosystems requiring immediate attention"""
        return f"""
        SELECT 
            name_18,
            biome_18,
            bioregion_,
            rlev5,
            pcnat2014,
            prcdelyear,
            (100 - pcnat2014) as transformation_percentage,
            pl_2018,
            cnsrv_trgt,
            -- Calculate composite risk score
            (CASE 
                WHEN rlev5 = 'CR' THEN 50
                WHEN rlev5 = 'EN' THEN 30
                WHEN rlev5 = 'VU' THEN 15
                WHEN rlev5 = 'NT' THEN 5
                ELSE 0
            END +
            CASE 
                WHEN prcdelyear > 0.3 THEN 25
                WHEN prcdelyear > 0.2 THEN 15
                WHEN prcdelyear > 0.1 THEN 10
                WHEN prcdelyear > 0.05 THEN 5
                ELSE 0
            END +
            CASE 
                WHEN (100 - pcnat2014) > 50 THEN 25
                WHEN (100 - pcnat2014) > 25 THEN 15
                WHEN (100 - pcnat2014) > 15 THEN 10
                ELSE 0
            END) as composite_risk_score
        FROM {self.full_table}
        WHERE biome_18 NOT IN ('', '<Null>', ' ')
        AND name_18 IS NOT NULL
        ORDER BY composite_risk_score DESC, prcdelyear DESC
        LIMIT {limit}
        """