"""
Test script for SANBI Ecosystem Risk Atlas database layer
Run this to validate database connectivity and data integrity
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from typing import Dict, Any
import traceback

# Import our data layer
from data import (
    check_database_health,
    get_database_manager,
    get_cache_manager,
    verify_data_layer
)
from app.config import DatabaseConfig

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def test_database_connectivity():
    """Test basic database connectivity"""
    print_section("DATABASE CONNECTIVITY TEST")
    
    try:
        # Test database health
        health = check_database_health()
        
        print("Database Health Check Results:")
        for key, value in health.items():
            status = "✅ PASS" if value else "❌ FAIL"
            if key == "error_message" and value:
                status = f"❌ ERROR: {value}"
            print(f"  {key}: {status}")
        
        # Test database manager
        db_manager = get_database_manager()
        connection_info = db_manager.get_connection_info()
        
        print("\nDatabase Connection Info:")
        for key, value in connection_info.items():
            print(f"  {key}: {value}")
        
        # Test table info
        if health["table_exists"]:
            table_info = db_manager.get_table_info()
            print("\nTable Information:")
            for key, value in table_info.items():
                print(f"  {key}: {value}")
        
        return health["connection"] and health["table_exists"] and health["data_available"]
        
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        traceback.print_exc()
        return False

def test_geographic_queries():
    """Test geographic filtering queries"""
    print_section("GEOGRAPHIC QUERIES TEST")
    
    try:
        cache_manager = get_cache_manager()
        
        # Test biomes query
        print_subsection("Biomes Query")
        biomes = cache_manager.get_biomes()
        print(f"Total biomes found: {len(biomes)}")
        print("Biomes available:")
        for _, biome in biomes.iterrows():
            print(f"  - {biome['biome_18']}: {biome['ecosystem_count']} ecosystems")
        
        # Test bioregions query
        print_subsection("Bioregions Query")
        bioregions = cache_manager.get_bioregions()
        print(f"Total bioregions found: {len(bioregions)}")
        print("First 5 bioregions:")
        for _, bioregion in bioregions.head().iterrows():
            print(f"  - {bioregion['bioregion_']} ({bioregion['biome_18']})")
        
        # Test ecosystems query for Fynbos
        print_subsection("Ecosystems Query (Fynbos)")
        fynbos_ecosystems = cache_manager.get_ecosystems(biome="Fynbos")
        print(f"Fynbos ecosystems found: {len(fynbos_ecosystems)}")
        print("First 5 Fynbos ecosystems:")
        for _, ecosystem in fynbos_ecosystems.head().iterrows():
            print(f"  - {ecosystem['name_18']} ({ecosystem['rlev5']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Geographic queries test failed: {e}")
        traceback.print_exc()
        return False

def test_risk_analysis_queries():
    """Test risk analysis queries"""
    print_section("RISK ANALYSIS QUERIES TEST")
    
    try:
        cache_manager = get_cache_manager()
        
        # Test habitat transformation
        print_subsection("🌿 Habitat Transformation Analysis")
        habitat_data = cache_manager.get_habitat_transformation_data()
        print(f"Biomes analyzed: {len(habitat_data)}")
        print("Top 3 biomes by habitat loss:")
        top_habitat_loss = habitat_data.head(3)
        for _, biome in top_habitat_loss.iterrows():
            print(f"  - {biome['biome_18']}: {biome['avg_habitat_loss_24_years']:.2f}% loss")
        
        # Test threat levels
        print_subsection("🦎 Biodiversity Threat Analysis")
        threat_data = cache_manager.get_threat_levels_data()
        print(f"Biomes analyzed: {len(threat_data)}")
        print("Top 3 biomes by threat percentage:")
        top_threats = threat_data.head(3)
        for _, biome in top_threats.iterrows():
            print(f"  - {biome['biome_18']}: {biome['high_threat_percentage']:.1f}% threatened")
        
        # Test vegetation vulnerability
        print_subsection("🌱 Vegetation Vulnerability Analysis")
        vulnerability_data = cache_manager.get_vegetation_vulnerability_data()
        print(f"Biomes analyzed: {len(vulnerability_data)}")
        print("Top 3 biomes by annual decline:")
        top_decline = vulnerability_data.head(3)
        for _, biome in top_decline.iterrows():
            print(f"  - {biome['biome_18']}: {biome['avg_annual_decline']:.3f}% annual decline")
        
        # Test protection gaps
        print_subsection("🛡️ Protection Gap Analysis")
        protection_data = cache_manager.get_protection_gaps_data()
        print(f"Biomes analyzed: {len(protection_data)}")
        print("Top 3 biomes by protection gap:")
        top_gaps = protection_data.head(3)
        for _, biome in top_gaps.iterrows():
            print(f"  - {biome['biome_18']}: {biome['inadequate_protection_percentage']:.1f}% inadequately protected")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk analysis queries test failed: {e}")
        traceback.print_exc()
        return False

def test_summary_queries():
    """Test summary and crisis detection queries"""
    print_section("SUMMARY & CRISIS QUERIES TEST")
    
    try:
        cache_manager = get_cache_manager()
        
        # Test national summary
        print_subsection("National Summary")
        national_summary = cache_manager.get_national_summary()
        print("National Statistics:")
        key_stats = [
            'total_ecosystems', 'total_biomes', 'critically_endangered', 
            'endangered', 'high_threat_percentage', 'inadequate_protection_percentage'
        ]
        for stat in key_stats:
            if stat in national_summary:
                print(f"  {stat}: {national_summary[stat]}")
        
        # Test crisis ecosystems
        print_subsection("Crisis Ecosystems")
        crisis_ecosystems = cache_manager.get_crisis_ecosystems(limit=5)
        print(f"Top 5 crisis ecosystems:")
        for _, ecosystem in crisis_ecosystems.iterrows():
            print(f"  - {ecosystem['name_18']} ({ecosystem['biome_18']})")
            print(f"    Threat: {ecosystem['rlev5']}, Risk Score: {ecosystem['composite_risk_score']}")
        
        # Test biome risk summary for Fynbos
        print_subsection("Biome Risk Summary (Fynbos)")
        fynbos_summary = cache_manager.get_biome_risk_summary("Fynbos")
        if fynbos_summary:
            print("Fynbos Risk Summary:")
            summary_keys = [
                'total_ecosystems', 'critically_endangered', 'endangered', 
                'avg_natural_habitat', 'avg_annual_decline'
            ]
            for key in summary_keys:
                if key in fynbos_summary:
                    print(f"  {key}: {fynbos_summary[key]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Summary queries test failed: {e}")
        traceback.print_exc()
        return False

def test_spatial_queries():
    """Test spatial data queries"""
    print_section("SPATIAL QUERIES TEST")
    
    try:
        cache_manager = get_cache_manager()
        
        # Test biome boundaries
        print_subsection("Biome Boundaries")
        biome_boundaries = cache_manager.get_biome_boundaries()
        print(f"Biome boundaries loaded: {len(biome_boundaries)}")
        print("Biomes with spatial data:")
        for _, biome in biome_boundaries.iterrows():
            print(f"  - {biome['biome_18']}: {biome['ecosystem_count']} ecosystems")
        
        # Test ecosystem geometries for Fynbos
        print_subsection("Ecosystem Geometries (Fynbos sample)")
        fynbos_geometries = cache_manager.get_ecosystem_geometries(biome="Fynbos")
        print(f"Fynbos geometries loaded: {len(fynbos_geometries)}")
        if len(fynbos_geometries) > 0:
            print("Sample Fynbos ecosystems with geometry:")
            for _, ecosystem in fynbos_geometries.head(3).iterrows():
                print(f"  - {ecosystem['name_18']}: {ecosystem['rlev5']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Spatial queries test failed: {e}")
        traceback.print_exc()
        return False

def test_cache_performance():
    """Test cache performance and functionality"""
    print_section("CACHE PERFORMANCE TEST")
    
    try:
        cache_manager = get_cache_manager()
        
        # Get cache info
        cache_info = cache_manager.get_cache_info()
        print("Cache Configuration:")
        for key, value in cache_info.items():
            print(f"  {key}: {value}")
        
        # Test cache warm-up
        print_subsection("Cache Warm-up Test")
        warmup_success = cache_manager.warm_up_cache()
        print(f"Cache warm-up: {'✅ SUCCESS' if warmup_success else '❌ FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache performance test failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all database layer tests"""
    print_section("SANBI ECOSYSTEM RISK ATLAS - DATABASE LAYER TEST")
    print("Testing database connectivity, queries, and cache performance...")
    
    test_results = {}
    
    # Run all tests
    test_results["connectivity"] = test_database_connectivity()
    test_results["geographic_queries"] = test_geographic_queries()
    test_results["risk_analysis"] = test_risk_analysis_queries()
    test_results["summary_queries"] = test_summary_queries()
    test_results["spatial_queries"] = test_spatial_queries()
    test_results["cache_performance"] = test_cache_performance()
    
    # Print final results
    print_section("TEST RESULTS SUMMARY")
    
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! Database layer is ready for use.")
    else:
        print("⚠️  SOME TESTS FAILED. Check the errors above.")
    print(f"{'='*60}")
    
    return all_passed

if __name__ == "__main__":
    # Load environment variables if .env file exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Environment variables loaded from .env file")
    except ImportError:
        print("python-dotenv not installed. Using system environment variables.")
    except Exception as e:
        print(f"Could not load .env file: {e}")
    
    # Run the comprehensive test
    success = run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)