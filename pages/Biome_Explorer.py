"""
SANBI Ecosystem Risk Atlas - Biome Explorer (Refactored)
Interactive exploration of ecosystem risk by biome, bioregion, and individual ecosystem
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import (
    initialize_streamlit_config, 
    AppConfig, 
    BIOME_INFO
)
from data import get_cache_manager, check_database_health
from components.geographic_filter import create_geographic_filter, create_breadcrumb_navigation
from components.comparison_metrics import create_comparison_metrics, create_performance_summary
from components.trend_charts import create_trend_analysis
from components.risk_summary_panel import create_risk_profile_section

def main():
    """Main biome explorer function"""
    
    # Initialize Streamlit config
    initialize_streamlit_config()
    app_config = AppConfig()
    
    # Page header
    st.title("Interactive Biome Risk Explorer")
    st.markdown("**Explore ecosystem risk patterns across South Africa's biomes, bioregions, and individual ecosystems**")
    
    # Check database health
    health = check_database_health()
    if not (health["connection"] and health["data_available"]):
        st.error("Database connection failed. Please check your configuration.")
        st.stop()
    
    # Load data and create geographic filter component
    cache_manager = get_cache_manager()
    
    try:
        # Use the geographic filter component
        selections = create_geographic_filter(cache_manager)
        
        # Get additional data
        national_summary = cache_manager.get_national_summary()
        risk_analysis = cache_manager.get_comprehensive_risk_analysis()
        
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()
    
    # Main content area with breadcrumb navigation
    create_breadcrumb_navigation(selections)
    st.markdown("---")
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        create_risk_profile_section(cache_manager, selections, national_summary)
        st.markdown("---")
        create_trend_analysis(cache_manager, selections)
    
    with col2:
        create_comparison_metrics(cache_manager, selections, national_summary)
        create_performance_summary(cache_manager, selections, national_summary)
        create_biome_info_panel(selections['biome'])
    
    # Full-width ecosystem details section
    st.markdown("---")
    create_ecosystem_list_section(cache_manager, selections)


def create_biome_info_panel(selected_biome):
    """Display biome information and context"""
    st.markdown("### Biome Information")
    
    if selected_biome in BIOME_INFO:
        info = BIOME_INFO[selected_biome]
        
        st.markdown(f"**{selected_biome}**")
        st.markdown(info['description'])
        
        st.markdown("**Key Threats:**")
        for threat in info['key_threats']:
            st.markdown(f"• {threat}")
        
        priority = info['conservation_priority']
        priority_color = {
            'Critical': '#d73027',
            'High': '#f46d43', 
            'Moderate': '#fdae61',
            'Low': '#abdda4'
        }.get(priority, '#cccccc')
        
        st.markdown(f"""
        **Conservation Priority:** 
        <span style="color: {priority_color}; font-weight: bold;">{priority}</span>
        """, unsafe_allow_html=True)
    
    elif selected_biome != "All Biomes":
        st.info(f"No detailed information available for {selected_biome}")


def create_ecosystem_list_section(cache_manager, selections):
    """Create ecosystem list and details for selected geographic area"""
    st.markdown("### Ecosystem Details")
    
    try:
        # Get ecosystems based on selection
        ecosystem_filters = {}
        if selections['biome'] != "All Biomes":
            ecosystem_filters['biome'] = selections['biome']
        if selections['bioregion'] != "All Bioregions":
            ecosystem_filters['bioregion'] = selections['bioregion']
        if selections['ecosystem'] != "All Ecosystems":
            ecosystem_filters['ecosystem'] = selections['ecosystem']
            
        ecosystems = cache_manager.get_ecosystem_details(**ecosystem_filters)
        
        if not ecosystems.empty:
            # Sort by threat level and decline rate
            threat_order = {'CR': 1, 'EN': 2, 'VU': 3, 'NT': 4, 'LC': 5}
            ecosystems['threat_priority'] = ecosystems['rlev5'].map(threat_order).fillna(6)
            ecosystems_sorted = ecosystems.sort_values(['threat_priority', 'prcdelyear'], ascending=[True, False])
            
            # Display ecosystem table with key metrics
            display_columns = {
                'name_18': 'Ecosystem',
                'rlev5': 'Threat',
                'pcnat2014': 'Natural %',
                'prcdelyear': 'Annual Decline %',
                'current_transformation_percentage': 'Transformed %',
                'pl_2018': 'Protection'
            }
            
            display_data = ecosystems_sorted[list(display_columns.keys())].copy()
            display_data.columns = list(display_columns.values())
            
            # Format numeric columns
            display_data['Natural %'] = display_data['Natural %'].round(1)
            display_data['Annual Decline %'] = display_data['Annual Decline %'].round(3)
            display_data['Transformed %'] = display_data['Transformed %'].round(1)
            
            st.dataframe(
                display_data,
                use_container_width=True,
                height=400,
                column_config={
                    "Threat": st.column_config.TextColumn(
                        help="IUCN Red List Status"
                    ),
                    "Natural %": st.column_config.ProgressColumn(
                        min_value=0,
                        max_value=100,
                        format="%.1f%%"
                    ),
                    "Transformed %": st.column_config.ProgressColumn(
                        min_value=0,
                        max_value=100,
                        format="%.1f%%"
                    )
                }
            )
            
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_ecosystems = len(ecosystems_sorted)
                st.metric("Total Ecosystems", total_ecosystems)
            
            with col2:
                threatened = len(ecosystems_sorted[ecosystems_sorted['rlev5'].isin(['CR', 'EN'])])
                threat_pct = (threatened / total_ecosystems * 100) if total_ecosystems > 0 else 0
                st.metric("High Threat", f"{threatened}", delta=f"{threat_pct:.1f}%")
            
            with col3:
                avg_natural = ecosystems_sorted['pcnat2014'].mean()
                st.metric("Avg Natural Habitat", f"{avg_natural:.1f}%")
            
            with col4:
                avg_decline = ecosystems_sorted['prcdelyear'].mean()
                st.metric("Avg Annual Decline", f"{avg_decline:.3f}%")
                
        else:
            st.warning("No ecosystem data available for current selection")
            
    except Exception as e:
        st.error(f"Could not load ecosystem details: {e}")


if __name__ == "__main__":
    main()