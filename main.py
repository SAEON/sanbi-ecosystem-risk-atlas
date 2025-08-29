"""
SANBI Ecosystem Risk Atlas - Main Application Entry Point
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import (
    initialize_streamlit_config, 
    AppConfig, 
    PAGES,
    THREAT_LEVELS 
)
from data import check_database_health, get_cache_manager

def Main():
    """Main application entry point"""
    
    # Initialize Streamlit configuration
    initialize_streamlit_config()
    app_config = AppConfig()
    
    # Main header
    st.title(app_config.title)
    st.markdown(f"### {app_config.subtitle}")
    
    # Database health check in sidebar
    with st.sidebar:
        
        health = check_database_health()
        
        if health["connection"] and health["data_available"]:
            try:
                cache_manager = get_cache_manager()
                national_summary = cache_manager.get_national_summary()
                
                if national_summary:
                    st.metric(
                        "Total Ecosystems", 
                        f"{int(national_summary.get('total_ecosystems', 0)):,}" 
                    )
                    st.metric(
                        "Biomes", 
                        f"{int(national_summary.get('total_biomes', 0))}"
                    )
                    st.metric(
                        "Threatened", 
                         f"{national_summary.get('high_threat_percentage', 0):.1f}%"
                    )
            except Exception as e:
                st.warning(f"Data summary unavailable: {e}")
                
        else:
            st.error("Issues with database connection")
            st.error(f"Error: {health.get('error_message', 'Unknown error')}")
            
    
    # Main content area
    if health["connection"] and health["data_available"]:
        # App is ready - show navigation
        st.markdown("---")
        
        # Navigation menu
        st.markdown("## Ecosystem Risk Atlas Navigation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(" **Overview Dashboard**", use_container_width=True):
                st.switch_page("pages/Overview.py")
            
            if st.button(" **Biome Explorer**", use_container_width=True):
                st.switch_page("pages/Biome_Explorer.py")
                
            #if st.button(" **Crisis Alerts**", use_container_width=True):
            #    st.switch_page("pages/03_🚨_Crisis_Alerts.py")
        
        with col2:
            if st.button(" **Risk Categories**", use_container_width=True):
                st.switch_page("pages/Risk_Categories.py")
                
            #if st.button(" **Success Stories**", use_container_width=True):
            #    st.switch_page("pages/05_🎖️_Success_Stories.py")
        
        # App description
        st.markdown("---")
        st.markdown("### About This Atlas")
        st.markdown(app_config.description)
        
        # Quick stats preview
        try:
            cache_manager = get_cache_manager()
            national_summary = cache_manager.get_national_summary()
            crisis_ecosystems = cache_manager.get_crisis_ecosystems(limit=3)
            
            if national_summary:
                st.markdown("### Quick National Overview")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Ecosystems",
                        f"{int(national_summary.get('total_ecosystems', 0)):,}",
                        help="Total number of ecosystem types assessed"
                    )
                
                with col2:
                    st.metric(
                        "Critically Endangered", 
                        f"{int(national_summary.get('critically_endangered', 0))}",
                        help="Ecosystems facing immediate extinction risk"
                    )
                
                with col3:
                    st.metric(
                        "Endangered",
                        f"{int(national_summary.get('endangered', 0))}",
                        help="Ecosystems at high risk of extinction"
                    )
                
                with col4:
                    threat_pct = national_summary.get('high_threat_percentage', 0)
                    st.metric(
                        "High Threat %",
                        f"{threat_pct:.1f}%",
                        help="Percentage of ecosystems that are CR or EN"
                    )
            
            if not crisis_ecosystems.empty:
                st.markdown("###  Top Crisis Ecosystems")
                st.markdown("*Ecosystems requiring immediate conservation attention*")
                
                for idx, ecosystem in crisis_ecosystems.head(3).iterrows():
                    threat_code = ecosystem['rlev5']
                    threat_info = THREAT_LEVELS.get(threat_code, {})
                    threat_name = threat_info.get('name', threat_code) 
                    threat_color = threat_info.get('color', '#cccccc')

                    with st.expander(f"🔴 {ecosystem['name_18']} ({ecosystem['biome_18']})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Threat Level:** {threat_name}")
                            st.markdown(f"**Biome:** {ecosystem['biome_18']}")
                        
                        with col2:
                            st.markdown(f"**Natural Habitat:** {ecosystem['pcnat2014']:.1f}%")
                            st.markdown(f"**Annual Decline:** {ecosystem['prcdelyear']:.2f}%")
                        
                        with col3:
                            st.markdown(f"**Transformed:** {ecosystem['transformation_percentage']:.1f}%")
                            st.markdown(f"**Risk Score:** {ecosystem['composite_risk_score']:.0f}")
                            
        except Exception as e:
            st.warning(f"Could not load preview data: {e}")
    
    else:
        # Database connection failed - show setup instructions
        st.error("## ⚠️ Database Connection Required")
        st.markdown("""
        The Ecosystem Risk Atlas requires a connection to the PostgreSQL database 
        containing the NBA 2018 ecosystem data.
        
        ### Setup Steps:
        1. **Check your `.env` file** with database credentials
        2. **Verify PostgreSQL is running** and accessible
        3. **Confirm the `environmental_risk_data` table exists** in the `sdgs` schema
        4. **Test the connection** using the database test script
        
        ### Database Configuration:
        ```bash
        DB_HOST=localhost
        DB_PORT=5432
        DB_NAME=your_database_name
        DB_USER=postgres
        DB_PASSWORD=your_password
        DB_SCHEMA=sdgs
        DB_TABLE=environmental_risk_data
        ```
        """)
        
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**SANBI** - South African National Biodiversity Institute")
    with col2:
        st.markdown("**SAEON** - South African Environmental Observation Network")
    with col3:
        st.markdown(f"**Version:** {app_config.version}")

if __name__ == "__main__":
    Main()