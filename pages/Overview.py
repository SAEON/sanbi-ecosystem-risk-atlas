"""
SANBI Ecosystem Risk Atlas - Overview Dashboard
National-level ecosystem risk summary and key insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import (
    initialize_streamlit_config, 
    AppConfig, 
    THREAT_LEVELS, 
    RISK_COLORS,
    BIOME_INFO,
    ECOSYSTEM_RISK_THRESHOLDS
)
from data import get_cache_manager, check_database_health

def main():
    """Main overview dashboard function"""
    
    # Initialize Streamlit config
    initialize_streamlit_config()
    app_config = AppConfig()
    
    # Page header
    st.title("National Ecosystem Risk Overview")
    st.markdown("Assessment of South Africa's ecosystem health and biodiversity threats from SANBI 2018 Report")
    
    # Check database health
    health = check_database_health()
    if not (health["connection"] and health["data_available"]):
        st.error("Database connection failed. Please check your configuration.")
        st.stop()
    
    # Load data
    cache_manager = get_cache_manager()
    
    try:
        national_summary = cache_manager.get_national_summary()
        risk_analysis = cache_manager.get_comprehensive_risk_analysis()
        crisis_ecosystems = cache_manager.get_crisis_ecosystems(limit=10)
        
        if not national_summary:
            st.error("No national summary data available")
            st.stop()
            
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()
    
    create_overview_dashboard(national_summary, risk_analysis, crisis_ecosystems)


def create_overview_dashboard(national_summary, risk_analysis, crisis_ecosystems):
    """Create the main overview dashboard layout"""
    
    # Key metrics row
    create_key_metrics_section(national_summary)
    
    st.markdown("---")
    
    # Main content in columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        create_threat_level_analysis(national_summary, risk_analysis)
        st.markdown("### Biome Risk Overview")
        create_biome_risk_charts(risk_analysis)
    
    with col2:
        create_crisis_alerts_panel(crisis_ecosystems)
        create_quick_insights_panel(risk_analysis)
    
    # Full-width sections
    st.markdown("---")
    create_detailed_biome_analysis(risk_analysis)
    
    # Methodology section at bottom
    st.markdown("---")
    create_methodology_section()


def create_key_metrics_section(national_summary):
    """Create key national metrics cards"""
    st.markdown("### National Ecosystem Status")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_ecosystems = int(national_summary.get('total_ecosystems', 0))
        st.metric(
            "Total Ecosystems", 
            f"{total_ecosystems:,}",
            help="Total number of ecosystem types assessed in South Africa"
        )
    
    with col2:
        cr_count = int(national_summary.get('critically_endangered', 0))
        st.metric(
            "Critically Endangered",
            f"{cr_count}",
            help="Ecosystems facing immediate extinction risk",
            delta=f"-{cr_count} at risk" if cr_count > 0 else None,
            delta_color="inverse"
        )
    
    with col3:
        en_count = int(national_summary.get('endangered', 0))
        st.metric(
            "Endangered",
            f"{en_count}",
            help="Ecosystems at high risk of extinction",
            delta=f"-{en_count} at risk" if en_count > 0 else None,
            delta_color="inverse"
        )
    
    with col4:
        threat_pct = national_summary.get('high_threat_percentage', 0)
        st.metric(
            "High Threat %",
            f"{threat_pct:.1f}%",
            help="Percentage of ecosystems that are Critically Endangered or Endangered",
            delta=f"{threat_pct:.1f}% threatened" if threat_pct > 0 else None,
            delta_color="inverse"
        )
    
    with col5:
        protection_gap = national_summary.get('inadequate_protection_percentage', 0)
        st.metric(
            "Protection Gap",
            f"{protection_gap:.1f}%",
            help="Percentage of ecosystems inadequately protected",
            delta=f"{protection_gap:.1f}% gap" if protection_gap > 0 else None,
            delta_color="inverse"
        )

def create_threat_level_analysis(national_summary, risk_analysis):
    """Create threat level distribution charts"""
    st.markdown("### Biodiversity Threat Assessment")
    
    # Threat level pie chart
    threat_data = {
        'Critically Endangered': national_summary.get('critically_endangered', 0),
        'Endangered': national_summary.get('endangered', 0),
        'Vulnerable': national_summary.get('vulnerable', 0),
        'Least Concern': national_summary.get('least_concern', 0)
    }
    
    # Create pie chart
    fig_pie = px.pie(
        values=list(threat_data.values()),
        names=list(threat_data.keys()),
        title="IUCN Red List Status Distribution",
        color_discrete_map={
            'Critically Endangered': THREAT_LEVELS['CR']['color'],
            'Endangered': THREAT_LEVELS['EN']['color'], 
            'Vulnerable': THREAT_LEVELS['VU']['color'],
            'Least Concern': THREAT_LEVELS['LC']['color']
        }
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

def create_biome_risk_charts(risk_analysis):
    """Create biome-level risk analysis charts"""
    
    # Get biome data
    habitat_data = risk_analysis.get('habitat_transformation', pd.DataFrame())
    threat_data = risk_analysis.get('threat_levels', pd.DataFrame())
    
    if habitat_data.empty or threat_data.empty:
        st.warning("Biome risk data not available")
        return
    
    # Merge data for combined analysis
    biome_risk = pd.merge(
        habitat_data[['biome_18', 'avg_habitat_loss_24_years']],
        threat_data[['biome_18', 'high_threat_percentage']],
        on='biome_18',
        how='inner'
    )
    
    # Create scatter plot
    fig_scatter = px.scatter(
        biome_risk,
        x='avg_habitat_loss_24_years',
        y='high_threat_percentage',
        size='high_threat_percentage',
        color='high_threat_percentage',
        hover_name='biome_18',
        title="Biome Risk Assessment: Habitat Loss vs Threat Levels",
        labels={
            'avg_habitat_loss_24_years': 'Habitat Loss (24 years) %',
            'high_threat_percentage': 'High Threat Ecosystems %'
        },
        color_continuous_scale='Reds'
    )
    
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

def create_crisis_alerts_panel(crisis_ecosystems):
    """Create crisis ecosystems alert panel"""
    st.markdown("### Crisis Alerts")
    st.markdown("Ecosystems requiring immediate conservation action")
    
    if crisis_ecosystems.empty:
        st.warning("No crisis ecosystem data available")
        return
    
    # Show top 5 crisis ecosystems
    for idx, ecosystem in crisis_ecosystems.head(5).iterrows():
        threat_color = THREAT_LEVELS.get(ecosystem['rlev5'], {}).get('color', '#cccccc')
        
        with st.container():
            st.markdown(f"""
            <div style="border-left: 4px solid {threat_color}; padding: 10px; margin: 5px 0; background-color: #f8f9fa;">
                <strong>{ecosystem['name_18']}</strong><br>
                <small>{ecosystem['biome_18']}</small><br>
                {ecosystem['rlev5']} | 
                {ecosystem['prcdelyear']:.2f}% annual decline |
                {ecosystem['transformation_percentage']:.1f}% transformed
            </div>
            """, unsafe_allow_html=True)

def create_quick_insights_panel(risk_analysis):
    """Create quick insights panel"""
    st.markdown("### Quick Insights")
    
    habitat_data = risk_analysis.get('habitat_transformation', pd.DataFrame())
    vulnerability_data = risk_analysis.get('vegetation_vulnerability', pd.DataFrame())
    
    if not habitat_data.empty:
        # Most at-risk biome
        most_at_risk = habitat_data.iloc[0]
        st.info(f"""
        **Most Habitat Loss**: {most_at_risk['biome_18']}  
        Lost {most_at_risk['avg_habitat_loss_24_years']:.1f}% over 24 years
        """)
    
    if not vulnerability_data.empty:
        # Fastest declining biome
        fastest_decline = vulnerability_data.iloc[0]
        st.warning(f"""
        **Fastest Decline**: {fastest_decline['biome_18']}  
        Declining at {fastest_decline['avg_annual_decline']:.2f}% per year
        """)
    
    # Conservation success
    st.success("""
    **Conservation Success**: Forests  
    0% inadequately protected (model biome)
    """)

def create_detailed_biome_analysis(risk_analysis):
    """Create detailed biome comparison table"""
    st.markdown("### Detailed Biome Risk Analysis")
    
    # Get all risk data
    habitat_data = risk_analysis.get('habitat_transformation', pd.DataFrame())
    threat_data = risk_analysis.get('threat_levels', pd.DataFrame())
    vulnerability_data = risk_analysis.get('vegetation_vulnerability', pd.DataFrame())
    protection_data = risk_analysis.get('protection_gaps', pd.DataFrame())
    
    # Merge all data
    if not any([df.empty for df in [habitat_data, threat_data, vulnerability_data, protection_data]]):
        detailed_analysis = habitat_data[['biome_18', 'ecosystem_count', 'avg_habitat_loss_24_years']].copy()
        detailed_analysis = pd.merge(detailed_analysis, threat_data[['biome_18', 'high_threat_percentage']], on='biome_18')
        detailed_analysis = pd.merge(detailed_analysis, vulnerability_data[['biome_18', 'avg_annual_decline']], on='biome_18')
        detailed_analysis = pd.merge(detailed_analysis, protection_data[['biome_18', 'inadequate_protection_percentage']], on='biome_18')
        
        # Rename columns for display
        detailed_analysis.columns = [
            'Biome', 'Ecosystems', 'Habitat Loss (24yr) %', 
            'High Threat %', 'Annual Decline %', 'Protection Gap %'
        ]
        
        # Format numbers
        detailed_analysis['Habitat Loss (24yr) %'] = detailed_analysis['Habitat Loss (24yr) %'].round(2)
        detailed_analysis['High Threat %'] = detailed_analysis['High Threat %'].round(1)
        detailed_analysis['Annual Decline %'] = detailed_analysis['Annual Decline %'].round(3)
        detailed_analysis['Protection Gap %'] = detailed_analysis['Protection Gap %'].round(1)
        
        # Display sortable table
        st.dataframe(
            detailed_analysis,
            use_container_width=True,
            height=400
        )
    else:
        st.warning("Detailed biome analysis data not available")

def create_methodology_section():
    """Create methodology and thresholds reference section"""
    st.markdown("## Risk Assessment Methodology & Thresholds")
    st.markdown("Reference guide for understanding ecosystem risk calculations and benchmarking")
    
    # Create tabs for different methodology sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Crisis Scoring", 
        "IUCN Threat Levels", 
        "Risk Thresholds", 
        "Data Sources"
    ])
    
    with tab1:
        st.markdown("### Crisis Ecosystem Scoring Methodology")
        st.markdown("**Composite Risk Score = IUCN Threat Score + Annual Decline Score + Transformation Score**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### IUCN Threat Level Points")
            threat_scores = {
                "CR (Critically Endangered)": 50,
                "EN (Endangered)": 30, 
                "VU (Vulnerable)": 15,
                "NT (Near Threatened)": 5,
                "LC (Least Concern)": 0
            }
            
            for level, points in threat_scores.items():
                threat_code = level.split()[0]
                color = THREAT_LEVELS.get(threat_code, {}).get('color', '#cccccc')
                st.markdown(f"""
                <div style="border-left: 4px solid {color}; padding: 5px; margin: 3px 0;">
                    <strong>{level}:</strong> {points} points
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Annual Decline Rate Points")
            decline_scores = [
                (">0.3% annual decline", 25),
                (">0.2% annual decline", 15),
                (">0.1% annual decline", 10),
                (">0.05% annual decline", 5),
                ("≤0.05% annual decline", 0)
            ]
            
            for description, points in decline_scores:
                st.markdown(f"**{description}:** {points} points")
        
        with col3:
            st.markdown("#### Habitat Transformation Points")
            transformation_scores = [
                (">50% transformed", 25),
                (">25% transformed", 15),
                (">15% transformed", 10),
                ("≤15% transformed", 0)
            ]
            
            for description, points in transformation_scores:
                st.markdown(f"**{description}:** {points} points")
        
        st.markdown("---")
        
        st.markdown("#### Crisis Level Interpretation")
        st.info("""
        **Maximum Score:** 100 points (50 + 25 + 25)  
        **High Crisis:** 70+ points (typically CR/EN + high decline + significant transformation)  
        **Moderate Crisis:** 40-69 points  
        **Lower Priority:** <40 points
        """)
    
    with tab2:
        st.markdown("### IUCN Red List Threat Categories")
        st.markdown("International Union for Conservation of Nature threat level classifications")
        
        # Create visual threat level guide
        for code, info in THREAT_LEVELS.items():
            if code:  # Skip empty key
                st.markdown(f"""
                <div style="
                    border: 2px solid {info['color']}; 
                    border-radius: 8px; 
                    padding: 12px; 
                    margin: 8px 0; 
                    background-color: {info['color']}15;
                ">
                    <h4 style="color: {info['color']}; margin: 0;">
                        {code} - {info['name']} (Priority: {info['priority']})
                    </h4>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">
                        {get_threat_description(code)}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Risk Assessment Thresholds")
        st.markdown("Benchmarks used to categorize ecosystem risk levels")
        
        # Display each risk threshold category
        for risk_type, thresholds in ECOSYSTEM_RISK_THRESHOLDS.items():
            st.markdown(f"#### {format_risk_type_name(risk_type)}")
            
            # Create threshold bars
            cols = st.columns(len(thresholds))
            threshold_items = list(thresholds.items())
            
            for i, (level, value) in enumerate(threshold_items):
                with cols[i]:
                    color = RISK_COLORS.get(level, '#cccccc')
                    
                    st.markdown(f"""
                    <div style="
                        background-color: {color}; 
                        color: white; 
                        padding: 10px; 
                        border-radius: 5px; 
                        text-align: center;
                        margin: 2px;
                    ">
                        <strong>{level.upper()}</strong><br>
                        {format_threshold_value(value, risk_type)}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
    
    with tab4:
        st.markdown("### Data Sources & Technical Notes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Primary Data Source")
            st.markdown("""
            **SANBI National Biodiversity Assessment 2018**
            - South African National Biodiversity Institute
            - Comprehensive ecosystem risk assessment
            - IUCN Red List methodology applied to ecosystems
            - Habitat transformation analysis (1990-2040)
            - Conservation status evaluation
            """)
            
            st.markdown("#### Key Indicators")
            indicators = {
                "rlev5": "IUCN Red List threat level",
                "prcnat1990": "% natural habitat (1990 baseline)",
                "pcnat2014": "% natural habitat remaining (2014)",
                "pcnat2040a": "% natural habitat projected (2040)",
                "prcdelyear": "Annual percentage decline rate", 
                "pl_2018": "Protection level classification",
                "cnsrv_trgt": "Conservation target percentage"
            }
            
            for code, description in indicators.items():
                st.markdown(f"**{code}:** {description}")
        
        with col2:
            st.markdown("#### Spatial Coverage") 
            st.markdown("""
            **Geographic Scope:** South Africa  
            **Resolution:** Ecosystem-level mapping  
            **Biomes Covered:** All major South African biomes  
            **Total Ecosystems:** ~440 ecosystem types assessed
            """)
            
            st.markdown("#### Temporal Analysis Framework")
            st.markdown("""
            **Historical Baseline (1990):** Starting reference point for habitat extent  
            **Current Assessment (2014):** Most recent comprehensive habitat mapping  
            **Future Projection (2040):** Modeled habitat extent under current trends  
            
            **Key Derived Metrics:**
            - **24-year Loss (1990-2014):** Historical habitat transformation rate
            - **26-year Projected Loss (2014-2040):** Expected future habitat loss under current pressures
            - **Total Projection Period:** 50-year trend analysis (1990-2040)
            """)
            
            st.markdown("#### Methodology References")
            st.markdown("""
            - **IUCN Red List of Ecosystems:** Keith, D.A., et al. (2013) Scientific Foundations for an IUCN Red List of Ecosystems. PLOS ONE 8(5): e62111
            - **NBA 2018 Methods:** Skowno, A.L., et al. (2019) National Biodiversity Assessment 2018: The status of South Africa's ecosystems and biodiversity. SANBI
            - **Protection Analysis:** South African Protected Areas Database (SAPAD), SANBI
            - **Data Platform:** SANBI Biodiversity GIS (BGIS) spatial datasets
            """)

def get_threat_description(code: str) -> str:
    """Get description for IUCN threat level"""
    descriptions = {
        "CR": "Facing extremely high risk of extinction in the wild",
        "EN": "Facing very high risk of extinction in the wild", 
        "VU": "Facing high risk of extinction in the wild",
        "NT": "Close to qualifying for threatened category",
        "LC": "Widespread and abundant, lowest risk category"
    }
    return descriptions.get(code, "Classification pending or data deficient")

def format_risk_type_name(risk_type: str) -> str:
    """Format risk type names for display"""
    names = {
        "habitat_loss": "Habitat Loss (24-year period)",
        "annual_decline": "Annual Vegetation Decline Rate", 
        "transformation": "Current Landscape Transformation",
        "protection_gap": "Protection Gap Assessment"
    }
    return names.get(risk_type, risk_type.replace('_', ' ').title())

def format_threshold_value(value: float, risk_type: str) -> str:
    """Format threshold values for display"""
    if risk_type == "annual_decline":
        return f">{value}%" if value > 0.01 else f"<{value}%"
    else:
        return f">{value}%" if value > 1 else f"<{value}%"


if __name__ == "__main__":
    main()