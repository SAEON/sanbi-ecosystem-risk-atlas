"""
SANBI Ecosystem Risk Atlas - Core Configuration
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import streamlit as st


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "ecosystem_risk_db")
    username: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    schema: str = os.getenv("DB_SCHEMA", "sdgs")
    table: str = os.getenv("DB_TABLE", "environmental_risk")

@dataclass
class AppConfig:
    """Application configuration"""
    title: str = "SANBI Ecosystem Risk Profiler"
    subtitle: str = "South African Ecosystem Risk Assessment and Vulnerability Profiler"
    description: str = """
    This atlas provides ecosystem-level risk assessment based on the 2018 National 
    Biodiversity Assessment (NBA) data from SANBI. Analyze ecosystem threat status, 
    habitat transformation risk, and biodiversity vulnerability across South African biomes.
    """
    version: str = "1.0.0"
    page_icon: str = "🌿"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"

# Risk Assessment Thresholds
ECOSYSTEM_RISK_THRESHOLDS = {
    # 🌿 Habitat Transformation Risk (% habitat loss over 24 years)
    "habitat_loss": {
        "critical": 4.0,    # >4% loss (Indian Ocean Coastal Belt level)
        "high": 2.0,        # 2-4% loss (Grassland, Forests, Savanna, Fynbos)
        "moderate": 1.0,    # 1-2% loss (Azonal, Albany Thicket)
        "low": 0.5,         # 0.5-1% loss
        "minimal": 0.1      # <0.5% loss (Karoo, Desert)
    },
    
    # 🌱 Vegetation Vulnerability (annual decline %)
    "annual_decline": {
        "critical": 0.4,    # >0.4% annual decline
        "high": 0.2,        # 0.2-0.4% annual decline
        "moderate": 0.1,    # 0.1-0.2% annual decline
        "low": 0.05,        # 0.05-0.1% annual decline
        "minimal": 0.01     # <0.05% annual decline
    },
    
    # 🏞️ Landscape Transformation (% currently transformed)
    "transformation": {
        "critical": 50.0,   # >50% transformed
        "high": 25.0,       # 25-50% transformed
        "moderate": 15.0,   # 15-25% transformed
        "low": 10.0,        # 10-15% transformed
        "minimal": 5.0      # <10% transformed
    },
    
    # 🛡️ Protection Gap (% inadequately protected)
    "protection_gap": {
        "critical": 80.0,   # >80% inadequately protected
        "high": 60.0,       # 60-80% inadequately protected
        "moderate": 40.0,   # 40-60% inadequately protected
        "low": 20.0,        # 20-40% inadequately protected
        "minimal": 10.0     # <20% inadequately protected
    }
}

# IUCN Red List Threat Levels
THREAT_LEVELS = {
    "CR": {"name": "Critically Endangered", "color": "#d73027", "priority": 5},
    "EN": {"name": "Endangered", "color": "#f46d43", "priority": 4},
    "VU": {"name": "Vulnerable", "color": "#fdae61", "priority": 3},
    "NT": {"name": "Near Threatened", "color": "#fee08b", "priority": 2},
    "LC": {"name": "Least Concern", "color": "#abdda4", "priority": 1},
    "": {"name": "Data Deficient", "color": "#cccccc", "priority": 0}
}

# Risk Level Color Scheme
RISK_COLORS = {
    "critical": "#d73027",    # Deep red
    "high": "#f46d43",        # Orange-red  
    "moderate": "#fdae61",    # Orange
    "low": "#fee08b",         # Light orange
    "minimal": "#abdda4",     # Light green
    "success": "#2166ac"      # Blue for success stories
}

# Biome Information
BIOME_INFO = {
    "Fynbos": {
        "description": "Mediterranean-climate shrublands, global biodiversity hotspot",
        "key_threats": ["Urban expansion", "Invasive species", "Fire regime changes"],
        "conservation_priority": "Critical"
    },
    "Grassland": {
        "description": "Temperate grasslands supporting agriculture and endemic species",
        "key_threats": ["Agricultural conversion", "Overgrazing", "Mining"],
        "conservation_priority": "High"
    },
    "Savanna": {
        "description": "Mixed tree-grass ecosystems supporting wildlife and communities",
        "key_threats": ["Bush encroachment", "Overgrazing", "Infrastructure development"],
        "conservation_priority": "Moderate"
    },
    "Indian Ocean Coastal Belt": {
        "description": "Narrow coastal ecosystems with high endemism",
        "key_threats": ["Coastal development", "Sea level rise", "Tourism pressure"],
        "conservation_priority": "Critical"
    },
    "Succulent Karoo": {
        "description": "Arid succulent shrublands, global biodiversity hotspot",
        "key_threats": ["Overgrazing", "Mining", "Climate change"],
        "conservation_priority": "Moderate"
    },
    "Nama-Karoo": {
        "description": "Semi-arid shrublands with adapted fauna",
        "key_threats": ["Overgrazing", "Desertification", "Infrastructure"],
        "conservation_priority": "Low"
    },
    "Albany Thicket": {
        "description": "Dense, drought-resistant shrublands",
        "key_threats": ["Overgrazing", "Browsing pressure", "Fragmentation"],
        "conservation_priority": "Moderate"
    },
    "Forests": {
        "description": "Temperate and afromontane forest patches",
        "key_threats": ["Fragmentation", "Edge effects", "Invasive species"],
        "conservation_priority": "High"
    },
    "Azonal Vegetation": {
        "description": "Specialized vegetation in unique habitats",
        "key_threats": ["Water abstraction", "Development", "Pollution"],
        "conservation_priority": "High"
    },
    "Desert": {
        "description": "Arid ecosystems with specialized adaptations",
        "key_threats": ["Mining", "Off-road vehicles", "Infrastructure"],
        "conservation_priority": "Low"
    }
}

# Dashboard Navigation
PAGES = {
    "🎯 Overview": {
        "title": "National Ecosystem Risk Overview",
        "description": "High-level summary of ecosystem risks across South Africa"
    },
    "🔍 Biome Explorer": {
        "title": "Interactive Biome Risk Explorer", 
        "description": "Detailed risk analysis by biome, bioregion, and ecosystem"
    },
    "🚨 Crisis Alerts": {
        "title": "Priority Conservation Actions",
        "description": "Ecosystems requiring immediate intervention"
    },
    "📊 Risk Categories": {
        "title": "Risk Category Deep Dive",
        "description": "Detailed analysis of each risk factor"
    },
    "🎖️ Success Stories": {
        "title": "Conservation Success Models",
        "description": "Well-protected ecosystems and best practices"
    }
}

# Map Configuration
MAP_CONFIG = {
    "default_zoom": 5,
    "center_lat": -28.5,
    "center_lon": 24.5,
    "max_zoom": 12,
    "min_zoom": 4,
    "tile_layer": "OpenStreetMap"
}

# Performance Settings
CACHE_CONFIG = {
    "ttl": 3600,  # 1 hour cache
    "max_entries": 1000,
    "show_spinner": True
}

def get_database_url() -> str:
    """Construct database connection URL"""
    db_config = DatabaseConfig()
    return f"postgresql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"

def initialize_streamlit_config():
    """Initialize Streamlit page configuration"""
    app_config = AppConfig()
    
    st.set_page_config(
        page_title=app_config.title,
        page_icon=app_config.page_icon,
        layout=app_config.layout,
        initial_sidebar_state=app_config.initial_sidebar_state
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .risk-critical { color: #d73027; font-weight: bold; }
    .risk-high { color: #f46d43; font-weight: bold; }
    .risk-moderate { color: #fdae61; font-weight: bold; }
    .risk-low { color: #fee08b; font-weight: bold; }
    .risk-minimal { color: #abdda4; font-weight: bold; }
    .metric-container { 
        background-color: #f0f2f6; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        margin: 0.5rem 0; 
    }
    </style>
    """, unsafe_allow_html=True)