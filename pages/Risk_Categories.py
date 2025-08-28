"""
SANBI Ecosystem Risk Atlas - Risk Categories Deep Dive
Detailed analysis of each risk factor category
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
    ECOSYSTEM_RISK_THRESHOLDS
)
from data import get_cache_manager, check_database_health
from components.geographic_filter import create_geographic_filter, create_breadcrumb_navigation
from components.comparison_metrics import create_comparison_metrics
from utils.risk_calculations import get_risk_level_by_threshold, get_risk_color_by_threshold

def main():
    """Main risk categories function"""
    
    # Initialize Streamlit config
    initialize_streamlit_config()
    app_config = AppConfig()
    
    # Page header
    st.title("Risk Categories Deep Dive")
    st.markdown("Detailed analysis of ecosystem risk factors across South Africa's biomes")
    
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
        
        # Load comprehensive risk data
        risk_analysis = cache_manager.get_comprehensive_risk_analysis()
        national_summary = cache_manager.get_national_summary()
        
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()
    
    # Main content with breadcrumb navigation
    create_breadcrumb_navigation(selections)
    st.markdown("---")
    
    create_risk_categories_layout(cache_manager, selections, risk_analysis, national_summary)


def create_risk_categories_layout(cache_manager, selections, risk_analysis, national_summary):
    """Create the main risk categories layout"""
    
    # Risk category selector
    st.markdown("### Select Risk Category for Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_category = st.selectbox(
            "Choose Risk Category:",
            options=[
                "Habitat Transformation",
                "Biodiversity Threat Status", 
                "Vegetation Vulnerability",
                "Protection Gaps",
                "Comprehensive Overview"
            ],
            help="Select a risk category to explore in detail"
        )
    
    with col2:
        show_comparison = st.toggle(
            "Show vs National",
            value=True,
            help="Show comparison with national averages"
        )
    
    # Display selected risk category analysis
    st.markdown("---")
    
    if selected_category == "Habitat Transformation":
        create_habitat_transformation_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary)
    elif selected_category == "Biodiversity Threat Status":
        create_threat_status_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary)
    elif selected_category == "Vegetation Vulnerability":
        create_vegetation_vulnerability_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary)
    elif selected_category == "Protection Gaps":
        create_protection_gaps_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary)
    else:
        create_comprehensive_risk_overview(risk_analysis, selections, national_summary)


def create_habitat_transformation_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary):
    """Create detailed habitat transformation analysis"""
    st.markdown("## Habitat Transformation Analysis")
    st.markdown("Historical and projected habitat loss across biomes")
    
    habitat_data = risk_analysis.get('habitat_transformation', pd.DataFrame())
    
    if habitat_data.empty:
        st.warning("No habitat transformation data available")
        return
    
    # Filter data if specific biome selected
    filtered_data = habitat_data.copy()
    if selections['biome'] != "All Biomes":
        filtered_data = habitat_data[habitat_data['biome_18'] == selections['biome']]
    
    # Key insights panel
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_loss = filtered_data['avg_habitat_loss_24_years'].mean()
        st.metric("Average Historical Loss", f"{avg_loss:.2f}%", help="Average habitat loss 1990-2014")
    
    with col2:
        avg_projected = filtered_data['avg_projected_loss_26_years'].mean()
        st.metric("Average Projected Loss", f"{avg_projected:.2f}%", help="Expected loss 2014-2040")
    
    with col3:
        if not filtered_data.empty:
            worst_biome = filtered_data.loc[filtered_data['avg_habitat_loss_24_years'].idxmax()]
            st.metric("Most Impacted Biome", worst_biome['biome_18'], 
                     delta=f"{worst_biome['avg_habitat_loss_24_years']:.2f}% loss")
    
    with col4:
        avg_transformation = filtered_data['avg_transformation_percentage'].mean()
        st.metric("Average Transformed", f"{avg_transformation:.1f}%", 
                 help="Current transformation across selected area")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        create_habitat_loss_timeline_chart(filtered_data)
    
    with col2:
        create_transformation_risk_levels_chart(filtered_data)
    
    # Show comparison metrics if enabled
    if show_comparison and selections['biome'] != "All Biomes":
        create_comparison_metrics(cache_manager, selections, national_summary)
    
    # Detailed data table
    st.markdown("#### Detailed Habitat Transformation Data")
    display_habitat_data = filtered_data[[
        'biome_18', 'ecosystem_count', 'avg_natural_1990', 'avg_natural_2014', 
        'avg_natural_2040_projected', 'avg_habitat_loss_24_years', 'avg_projected_loss_26_years'
    ]].copy()
    
    display_habitat_data.columns = [
        'Biome', 'Ecosystems', 'Natural 1990 (%)', 'Natural 2014 (%)',
        'Projected 2040 (%)', 'Historical Loss (%)', 'Projected Loss (%)'
    ]
    
    # Round numeric columns
    numeric_columns = display_habitat_data.select_dtypes(include=['float64']).columns
    display_habitat_data[numeric_columns] = display_habitat_data[numeric_columns].round(2)
    
    st.dataframe(display_habitat_data, use_container_width=True, height=400)


def create_threat_status_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary):
    """Create detailed biodiversity threat analysis"""
    st.markdown("## Biodiversity Threat Status Analysis")
    st.markdown("IUCN Red List status distribution and trends")
    
    threat_data = risk_analysis.get('threat_levels', pd.DataFrame())
    
    if threat_data.empty:
        st.warning("No threat level data available")
        return
    
    # Filter data if specific biome selected
    filtered_data = threat_data.copy()
    if selections['biome'] != "All Biomes":
        filtered_data = threat_data[threat_data['biome_18'] == selections['biome']]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cr = filtered_data['critically_endangered'].sum()
        st.metric("Critically Endangered", f"{int(total_cr)}", help="Ecosystems facing immediate extinction risk")
    
    with col2:
        total_en = filtered_data['endangered'].sum()
        st.metric("Endangered", f"{int(total_en)}", help="Ecosystems at high extinction risk")
    
    with col3:
        high_threat_avg = filtered_data['high_threat_percentage'].mean()
        st.metric("Average High Threat", f"{high_threat_avg:.1f}%", 
                 help="Average percentage of CR+EN ecosystems")
    
    with col4:
        if not filtered_data.empty:
            worst_threat_biome = filtered_data.loc[filtered_data['high_threat_percentage'].idxmax()]
            st.metric("Highest Threat Biome", worst_threat_biome['biome_18'],
                     delta=f"{worst_threat_biome['high_threat_percentage']:.1f}% threatened")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        create_threat_distribution_chart(filtered_data)
    
    with col2:
        create_threat_heatmap_chart(filtered_data)
    
    # Show comparison metrics if enabled
    if show_comparison and selections['biome'] != "All Biomes":
        create_comparison_metrics(cache_manager, selections, national_summary)
    
    # Detailed data table
    st.markdown("#### Detailed Threat Status Data")
    display_threat_data = filtered_data[[
        'biome_18', 'total_ecosystems', 'critically_endangered', 'endangered',
        'vulnerable', 'least_concern', 'high_threat_percentage'
    ]].copy()
    
    display_threat_data.columns = [
        'Biome', 'Total', 'CR', 'EN', 'VU', 'LC', 'High Threat (%)'
    ]
    
    st.dataframe(display_threat_data, use_container_width=True, height=400)


def create_vegetation_vulnerability_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary):
    """Create vegetation vulnerability analysis"""
    st.markdown("## Vegetation Vulnerability Analysis")
    st.markdown("Annual decline rates and degradation patterns")
    
    vulnerability_data = risk_analysis.get('vegetation_vulnerability', pd.DataFrame())
    
    if vulnerability_data.empty:
        st.warning("No vegetation vulnerability data available")
        return
    
    # Filter data if specific biome selected
    filtered_data = vulnerability_data.copy()
    if selections['biome'] != "All Biomes":
        filtered_data = vulnerability_data[vulnerability_data['biome_18'] == selections['biome']]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_decline = filtered_data['avg_annual_decline'].mean()
        st.metric("Average Annual Decline", f"{avg_decline:.3f}%", help="Mean vegetation decline rate per year")
    
    with col2:
        max_decline = filtered_data['max_annual_decline'].max()
        st.metric("Maximum Decline Rate", f"{max_decline:.3f}%", help="Highest recorded annual decline")
    
    with col3:
        high_decline_total = filtered_data['high_decline_ecosystems'].sum()
        st.metric("High Decline Ecosystems", f"{int(high_decline_total)}", 
                 help="Ecosystems with >0.2% annual decline")
    
    with col4:
        if not filtered_data.empty:
            fastest_declining = filtered_data.loc[filtered_data['avg_annual_decline'].idxmax()]
            st.metric("Fastest Declining Biome", fastest_declining['biome_18'],
                     delta=f"{fastest_declining['avg_annual_decline']:.3f}%/year")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        create_decline_rate_chart(filtered_data)
    
    with col2:
        create_vulnerability_assessment_chart(filtered_data)
    
    # Show comparison metrics if enabled
    if show_comparison and selections['biome'] != "All Biomes":
        create_comparison_metrics(cache_manager, selections, national_summary)
    
    # Detailed data table
    st.markdown("#### Detailed Vulnerability Data")
    display_vulnerability_data = filtered_data[[
        'biome_18', 'ecosystem_count', 'avg_annual_decline', 
        'max_annual_decline', 'high_decline_ecosystems'
    ]].copy()
    
    display_vulnerability_data.columns = [
        'Biome', 'Ecosystems', 'Avg Decline (%/year)', 
        'Max Decline (%/year)', 'High Decline Count'
    ]
    
    # Round numeric columns
    display_vulnerability_data['Avg Decline (%/year)'] = display_vulnerability_data['Avg Decline (%/year)'].round(4)
    display_vulnerability_data['Max Decline (%/year)'] = display_vulnerability_data['Max Decline (%/year)'].round(4)
    
    st.dataframe(display_vulnerability_data, use_container_width=True, height=400)


def create_protection_gaps_analysis(cache_manager, risk_analysis, selections, show_comparison, national_summary):
    """Create protection gaps analysis"""
    st.markdown("## Protection Gaps Analysis")
    st.markdown("Conservation target achievement and protection adequacy")
    
    protection_data = risk_analysis.get('protection_gaps', pd.DataFrame())
    
    if protection_data.empty:
        st.warning("No protection gap data available")
        return
    
    # Filter data if specific biome selected
    filtered_data = protection_data.copy()
    if selections['biome'] != "All Biomes":
        filtered_data = protection_data[protection_data['biome_18'] == selections['biome']]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_target = filtered_data['avg_conservation_target'].mean()
        st.metric("Average Conservation Target", f"{avg_target:.1f}%", help="Average conservation target percentage")
    
    with col2:
        well_protected = filtered_data['well_protected'].sum()
        st.metric("Well Protected Ecosystems", f"{int(well_protected)}", help="Ecosystems meeting protection targets")
    
    with col3:
        inadequate_avg = filtered_data['inadequate_protection_percentage'].mean()
        st.metric("Average Protection Gap", f"{inadequate_avg:.1f}%", 
                 help="Average percentage inadequately protected")
    
    with col4:
        if not filtered_data.empty:
            worst_protection = filtered_data.loc[filtered_data['inadequate_protection_percentage'].idxmax()]
            st.metric("Highest Protection Gap", worst_protection['biome_18'],
                     delta=f"{worst_protection['inadequate_protection_percentage']:.1f}% gap")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        create_protection_status_chart(filtered_data)
    
    with col2:
        create_conservation_achievement_chart(filtered_data)
    
    # Show comparison metrics if enabled
    if show_comparison and selections['biome'] != "All Biomes":
        create_comparison_metrics(cache_manager, selections, national_summary)
    
    # Detailed data table
    st.markdown("#### Detailed Protection Data")
    display_protection_data = filtered_data[[
        'biome_18', 'ecosystem_count', 'avg_conservation_target',
        'well_protected', 'poorly_protected', 'inadequate_protection_percentage'
    ]].copy()
    
    display_protection_data.columns = [
        'Biome', 'Ecosystems', 'Avg Target (%)', 
        'Well Protected', 'Poorly Protected', 'Protection Gap (%)'
    ]
    
    st.dataframe(display_protection_data, use_container_width=True, height=400)


def create_comprehensive_risk_overview(risk_analysis, selections, national_summary):
    """Create comprehensive overview of all risk categories"""
    st.markdown("## Comprehensive Risk Overview")
    st.markdown("Multi-factor risk assessment across all categories")
    
    # Get all risk data
    habitat_data = risk_analysis.get('habitat_transformation', pd.DataFrame())
    threat_data = risk_analysis.get('threat_levels', pd.DataFrame())
    vulnerability_data = risk_analysis.get('vegetation_vulnerability', pd.DataFrame())
    protection_data = risk_analysis.get('protection_gaps', pd.DataFrame())
    
    if any([df.empty for df in [habitat_data, threat_data, vulnerability_data, protection_data]]):
        st.warning("Incomplete risk data for comprehensive analysis")
        return
    
    # Create comprehensive analysis
    create_multi_factor_correlation_analysis(habitat_data, threat_data, vulnerability_data, protection_data)
    
    # Priority ranking
    create_biome_priority_ranking(habitat_data, threat_data, vulnerability_data, protection_data)


# Chart creation functions
def create_habitat_loss_timeline_chart(habitat_data):
    """Create habitat loss timeline chart"""
    st.markdown("#### Historical vs Projected Loss")
    
    if habitat_data.empty:
        st.warning("No data for timeline chart")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=habitat_data['biome_18'],
        y=habitat_data['avg_habitat_loss_24_years'],
        name='Historical Loss (1990-2014)',
        marker_color='#d73027'
    ))
    
    fig.add_trace(go.Bar(
        x=habitat_data['biome_18'],
        y=habitat_data['avg_projected_loss_26_years'],
        name='Projected Loss (2014-2040)',
        marker_color='#f46d43'
    ))
    
    fig.update_layout(
        title="Habitat Loss Timeline by Biome",
        xaxis_title="Biome",
        yaxis_title="Habitat Loss (%)",
        height=400,
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_transformation_risk_levels_chart(habitat_data):
    """Create transformation risk levels chart"""
    st.markdown("#### Transformation Risk Levels")
    
    if habitat_data.empty:
        st.warning("No data for risk levels chart")
        return
    
    # Categorize biomes by risk level
    risk_categories = []
    colors = []
    for _, biome in habitat_data.iterrows():
        transformation_pct = biome['avg_transformation_percentage']
        risk_level = get_risk_level_by_threshold('transformation', transformation_pct)
        risk_categories.append(risk_level)
        colors.append(get_risk_color_by_threshold('transformation', transformation_pct))
    
    fig = px.scatter(
        x=habitat_data['biome_18'],
        y=habitat_data['avg_transformation_percentage'],
        color=risk_categories,
        size=habitat_data['avg_transformation_percentage'],
        title="Transformation Risk Assessment by Biome",
        labels={'x': 'Biome', 'y': 'Transformation (%)'},
        color_discrete_map={
            'critical': RISK_COLORS['critical'],
            'high': RISK_COLORS['high'],
            'moderate': RISK_COLORS['moderate'],
            'low': RISK_COLORS['low'],
            'minimal': RISK_COLORS['minimal']
        }
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_threat_distribution_chart(threat_data):
    """Create threat level distribution chart"""
    st.markdown("#### Threat Level Distribution")
    
    if threat_data.empty:
        st.warning("No data for threat distribution")
        return
    
    # Aggregate threat counts
    total_cr = threat_data['critically_endangered'].sum()
    total_en = threat_data['endangered'].sum()
    total_vu = threat_data['vulnerable'].sum()
    total_lc = threat_data['least_concern'].sum()
    
    fig = px.pie(
        values=[total_cr, total_en, total_vu, total_lc],
        names=['Critically Endangered', 'Endangered', 'Vulnerable', 'Least Concern'],
        title="Ecosystem Threat Distribution",
        color_discrete_map={
            'Critically Endangered': THREAT_LEVELS['CR']['color'],
            'Endangered': THREAT_LEVELS['EN']['color'],
            'Vulnerable': THREAT_LEVELS['VU']['color'],
            'Least Concern': THREAT_LEVELS['LC']['color']
        }
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_threat_heatmap_chart(threat_data):
    """Create threat severity heatmap"""
    st.markdown("#### Threat Severity by Biome")
    
    if threat_data.empty or len(threat_data) == 0:
        st.warning("No data for threat heatmap")
        return
    
    fig = go.Figure(data=go.Heatmap(
        z=[threat_data['high_threat_percentage'].values],
        x=threat_data['biome_18'].values,
        y=['High Threat Percentage'],
        colorscale='Reds',
        hoverongaps=False,
        hovertemplate='<b>%{x}</b><br>High Threat: %{z:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="High Threat Percentage by Biome",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_decline_rate_chart(vulnerability_data):
    """Create decline rate distribution chart"""
    st.markdown("#### Annual Decline Rate Distribution")
    
    if vulnerability_data.empty:
        st.warning("No data for decline rate chart")
        return
    
    fig = px.bar(
        vulnerability_data,
        x='biome_18',
        y='avg_annual_decline',
        title="Average Annual Decline Rate by Biome",
        labels={'avg_annual_decline': 'Annual Decline Rate (%)', 'biome_18': 'Biome'},
        color='avg_annual_decline',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_vulnerability_assessment_chart(vulnerability_data):
    """Create vulnerability risk assessment chart"""
    st.markdown("#### Vulnerability Risk Categories")
    
    if vulnerability_data.empty:
        st.warning("No data for vulnerability assessment")
        return
    
    # Categorize by risk level
    risk_counts = {'critical': 0, 'high': 0, 'moderate': 0, 'low': 0, 'minimal': 0}
    
    for _, biome in vulnerability_data.iterrows():
        decline_rate = biome['avg_annual_decline']
        risk_level = get_risk_level_by_threshold('annual_decline', decline_rate)
        risk_counts[risk_level] += 1
    
    fig = px.pie(
        values=list(risk_counts.values()),
        names=list(risk_counts.keys()),
        title="Vulnerability Risk Categories",
        color_discrete_map=RISK_COLORS
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_protection_status_chart(protection_data):
    """Create protection status chart"""
    st.markdown("#### Protection Status Distribution")
    
    if protection_data.empty:
        st.warning("No data for protection status chart")
        return
    
    well_protected = protection_data['well_protected'].sum()
    moderately_protected = protection_data['moderately_protected'].sum() if 'moderately_protected' in protection_data.columns else 0
    poorly_protected = protection_data['poorly_protected'].sum()
    not_protected = protection_data['not_protected'].sum()
    
    fig = px.bar(
        x=['Well Protected', 'Moderately Protected', 'Poorly Protected', 'Not Protected'],
        y=[well_protected, moderately_protected, poorly_protected, not_protected],
        title="Ecosystem Protection Status",
        color=[well_protected, moderately_protected, poorly_protected, not_protected],
        color_continuous_scale='RdYlGn_r'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_conservation_achievement_chart(protection_data):
    """Create conservation target achievement chart"""
    st.markdown("#### Conservation Target Achievement")
    
    if protection_data.empty:
        st.warning("No data for conservation achievement chart")
        return
    
    # Calculate achievement percentage (well protected / total)
    protection_data_copy = protection_data.copy()
    protection_data_copy['achievement_percentage'] = (
        protection_data_copy['well_protected'] / protection_data_copy['ecosystem_count'] * 100
    )
    
    fig = px.bar(
        protection_data_copy,
        x='biome_18',
        y='achievement_percentage',
        title="Conservation Target Achievement by Biome",
        labels={'achievement_percentage': 'Achievement (%)', 'biome_18': 'Biome'},
        color='achievement_percentage',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_multi_factor_correlation_analysis(habitat_data, threat_data, vulnerability_data, protection_data):
    """Create risk factor correlation analysis"""
    st.markdown("### Risk Factor Correlations")
    
    try:
        # Merge all data for correlation analysis
        merged_data = habitat_data[['biome_18', 'avg_habitat_loss_24_years']].copy()
        merged_data = merged_data.merge(threat_data[['biome_18', 'high_threat_percentage']], on='biome_18', how='inner')
        merged_data = merged_data.merge(vulnerability_data[['biome_18', 'avg_annual_decline']], on='biome_18', how='inner') 
        merged_data = merged_data.merge(protection_data[['biome_18', 'inadequate_protection_percentage']], on='biome_18', how='inner')
        
        if merged_data.empty:
            st.warning("Insufficient data for correlation analysis")
            return
        
        # Calculate correlation matrix
        correlation_data = merged_data[[
            'avg_habitat_loss_24_years', 'high_threat_percentage', 
            'avg_annual_decline', 'inadequate_protection_percentage'
        ]].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_data.values,
            x=['Habitat Loss', 'High Threat', 'Annual Decline', 'Protection Gap'],
            y=['Habitat Loss', 'High Threat', 'Annual Decline', 'Protection Gap'],
            colorscale='RdBu',
            zmid=0,
            hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Risk Factor Correlation Matrix",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        st.markdown("#### Correlation Insights")
        st.markdown("""
        - **Strong positive correlations** (red) indicate risk factors that tend to occur together
        - **Strong negative correlations** (blue) indicate inverse relationships
        - **Values near 0** (white) indicate little correlation between factors
        """)
        
    except Exception as e:
        st.error(f"Could not create correlation analysis: {e}")


def create_biome_priority_ranking(habitat_data, threat_data, vulnerability_data, protection_data):
    """Create priority ranking based on multiple risk factors"""
    st.markdown("### Biome Priority Ranking")
    
    try:
        # Merge key risk indicators
        priority_data = habitat_data[['biome_18', 'avg_habitat_loss_24_years', 'avg_transformation_percentage']].copy()
        priority_data = priority_data.merge(threat_data[['biome_18', 'high_threat_percentage']], on='biome_18', how='inner')
        priority_data = priority_data.merge(vulnerability_data[['biome_18', 'avg_annual_decline']], on='biome_18', how='inner')
        priority_data = priority_data.merge(protection_data[['biome_18', 'inadequate_protection_percentage']], on='biome_18', how='inner')
        
        if priority_data.empty:
            st.warning("Insufficient data for priority ranking")
            return
        
        # Calculate composite priority score (0-100)
        priority_data['priority_score'] = (
            priority_data['high_threat_percentage'] * 0.3 +
            priority_data['avg_transformation_percentage'] * 0.25 +
            priority_data['avg_annual_decline'] * 50 * 0.2 +  # Scale up annual decline
            priority_data['inadequate_protection_percentage'] * 0.15 +
            priority_data['avg_habitat_loss_24_years'] * 2 * 0.1  # Scale up habitat loss
        )
        
        # Sort by priority score
        priority_data_sorted = priority_data.sort_values('priority_score', ascending=False)
        
        # Create priority ranking chart
        fig = px.bar(
            priority_data_sorted,
            x='biome_18',
            y='priority_score',
            title="Biome Conservation Priority Ranking",
            labels={'priority_score': 'Priority Score', 'biome_18': 'Biome'},
            color='priority_score',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Priority interpretation
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top Priority Biomes")
            top_3 = priority_data_sorted.head(3)
            for _, biome in top_3.iterrows():
                st.markdown(f"**{biome['biome_18']}** - Score: {biome['priority_score']:.1f}")
        
        with col2:
            st.markdown("#### Priority Factors")
            st.markdown("""
            **Weighting:**
            - Threat Level: 30%
            - Transformation: 25% 
            - Annual Decline: 20%
            - Protection Gap: 15%
            - Historical Loss: 10%
            """)
        
    except Exception as e:
        st.error(f"Could not create priority ranking: {e}")


if __name__ == "__main__":
    main()