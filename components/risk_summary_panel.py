"""
Risk Summary Panel Component for SANBI Ecosystem Risk Atlas
5-category risk display with color-coded risk metric cards
"""
import streamlit as st
import pandas as pd
from typing import Dict, Optional, Any
import logging

from utils.risk_calculations import (
    get_risk_color_by_threshold,
    get_threat_level_info, 
    get_protection_level_info,
    calculate_composite_risk_score,
    assess_risk_trajectory,
    get_risk_summary_stats,
    categorize_ecosystem_urgency
)

logger = logging.getLogger(__name__)

class RiskSummaryPanel:
    """Manages 5-category risk display panels"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def create_risk_profile_section(self, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
        """
        Create risk profile section based on geographic selection
        
        Args:
            selections: Current geographic selections
            national_summary: National summary statistics
        """
        st.markdown("### Risk Profile Analysis")
        
        try:
            if selections['ecosystem'] != "All Ecosystems":
                self._display_individual_ecosystem_risk(selections)
            elif selections['biome'] != "All Biomes":
                self._display_biome_risk_profile(selections, national_summary)
            else:
                self._display_national_risk_profile(national_summary)
                
        except Exception as e:
            st.error(f"Could not load risk profile: {e}")
            logger.error(f"Risk profile error: {e}")
    
    def _display_individual_ecosystem_risk(self, selections: Dict[str, str]) -> None:
        """Display detailed risk analysis for individual ecosystem"""
        ecosystem_details = self.cache_manager.get_ecosystem_details(
            biome=selections['biome'] if selections['biome'] != "All Biomes" else None,
            bioregion=selections['bioregion'] if selections['bioregion'] != "All Bioregions" else None,
            ecosystem=selections['ecosystem']
        )
        
        if ecosystem_details.empty:
            st.warning("No detailed data available for selected ecosystem")
            return
        
        data = ecosystem_details.iloc[0]
        ecosystem_name = data.get('name_18', 'Unknown Ecosystem')
        
        st.markdown(f"#### {ecosystem_name}")
        
        # Create 5-category risk display
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            self._create_threat_level_card(data)
        
        with col2:
            self._create_transformation_card(data)
        
        with col3:
            self._create_decline_rate_card(data)
        
        with col4:
            self._create_habitat_loss_card(data)
        
        with col5:
            self._create_protection_card(data)
        
        # Risk assessment summary
        st.markdown("---")
        self._create_ecosystem_urgency_assessment(data)
    
    def _display_biome_risk_profile(self, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
        """Display biome-level risk summary"""
        biome_name = selections['biome']
        biome_summary = self.cache_manager.get_biome_risk_summary(biome_name)
        
        if not biome_summary:
            st.warning("No summary data available for selected biome")
            return
        
        st.markdown(f"#### {biome_name} Risk Summary")
        
        # Biome-level metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_ecosystems = biome_summary.get('total_ecosystems', 0)
            st.metric("Total Ecosystems", f"{int(total_ecosystems)}")
        
        with col2:
            critically_endangered = biome_summary.get('critically_endangered', 0)
            endangered = biome_summary.get('endangered', 0)
            high_threat = critically_endangered + endangered
            st.metric("High Threat", f"{int(high_threat)}", 
                     delta=f"CR: {int(critically_endangered)}, EN: {int(endangered)}")
        
        with col3:
            avg_natural = biome_summary.get('avg_natural_habitat', 0)
            st.metric("Natural Habitat", f"{avg_natural:.1f}%", 
                     help="Average percentage of natural habitat remaining")
        
        with col4:
            avg_decline = biome_summary.get('avg_annual_decline', 0)
            st.metric("Annual Decline", f"{avg_decline:.3f}%",
                     help="Average annual vegetation decline rate")
        
        # Most threatened ecosystem highlight
        if biome_summary.get('most_threatened_ecosystem'):
            threatened = biome_summary['most_threatened_ecosystem']
            threat_info = get_threat_level_info(threatened['threat_level'])
            
            st.markdown("#### Most Critical Ecosystem")
            st.markdown(f"""
            <div style="border-left: 4px solid {threat_info['color']}; padding: 10px; background-color: #f8f9fa;">
                <strong>{threatened['name']}</strong><br>
                <small>Status: {threat_info['name']} | Annual Decline: {threatened['decline_rate']:.3f}%</small>
            </div>
            """, unsafe_allow_html=True)
    
    def _display_national_risk_profile(self, national_summary: Dict[str, Any]) -> None:
        """Display national-level risk overview"""
        st.markdown("#### National Risk Overview")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total = national_summary.get('total_ecosystems', 0)
            st.metric("Total Ecosystems", f"{int(total)}")
        
        with col2:
            cr = national_summary.get('critically_endangered', 0)
            st.metric("Critically Endangered", f"{int(cr)}")
        
        with col3:
            en = national_summary.get('endangered', 0)
            st.metric("Endangered", f"{int(en)}")
        
        with col4:
            threat_pct = national_summary.get('high_threat_percentage', 0)
            st.metric("High Threat %", f"{threat_pct:.1f}%")
        
        with col5:
            protection_gap = national_summary.get('inadequate_protection_percentage', 0)
            st.metric("Protection Gap", f"{protection_gap:.1f}%")
    
    def _create_threat_level_card(self, data: pd.Series) -> None:
        """Create IUCN threat level card"""
        threat_level = data.get('rlev5', 'DD')
        threat_info = get_threat_level_info(threat_level)
        
        st.markdown(f"""
        <div style="
            border: 2px solid {threat_info['color']}; 
            border-radius: 8px; 
            padding: 12px; 
            background-color: {threat_info['color']}15;
            text-align: center;
        ">
            <h4 style="margin: 0; color: {threat_info['color']};">IUCN Status</h4>
            <h2 style="margin: 5px 0; color: {threat_info['color']};">{threat_level}</h2>
            <small style="color: #666;">{threat_info['name']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    def _create_transformation_card(self, data: pd.Series) -> None:
        """Create habitat transformation card"""
        natural_habitat = data.get('pcnat2014', 0)
        transformation_pct = 100 - natural_habitat
        color = get_risk_color_by_threshold('transformation', transformation_pct)
        
        st.markdown(f"""
        <div style="
            border: 2px solid {color}; 
            border-radius: 8px; 
            padding: 12px; 
            background-color: {color}15;
            text-align: center;
        ">
            <h4 style="margin: 0; color: {color};">Transformation</h4>
            <h2 style="margin: 5px 0; color: {color};">{transformation_pct:.1f}%</h2>
            <small style="color: #666;">Habitat Transformed</small>
        </div>
        """, unsafe_allow_html=True)
    
    def _create_decline_rate_card(self, data: pd.Series) -> None:
        """Create annual decline rate card"""
        annual_decline = data.get('prcdelyear', 0)
        color = get_risk_color_by_threshold('annual_decline', annual_decline)
        
        st.markdown(f"""
        <div style="
            border: 2px solid {color}; 
            border-radius: 8px; 
            padding: 12px; 
            background-color: {color}15;
            text-align: center;
        ">
            <h4 style="margin: 0; color: {color};">Annual Decline</h4>
            <h2 style="margin: 5px 0; color: {color};">{annual_decline:.3f}%</h2>
            <small style="color: #666;">Per Year</small>
        </div>
        """, unsafe_allow_html=True)
    
    def _create_habitat_loss_card(self, data: pd.Series) -> None:
        """Create habitat loss card"""
        habitat_loss = data.get('habitat_loss_24_years', 0)
        color = get_risk_color_by_threshold('habitat_loss', habitat_loss)
        
        st.markdown(f"""
        <div style="
            border: 2px solid {color}; 
            border-radius: 8px; 
            padding: 12px; 
            background-color: {color}15;
            text-align: center;
        ">
            <h4 style="margin: 0; color: {color};">Habitat Loss</h4>
            <h2 style="margin: 5px 0; color: {color};">{habitat_loss:.1f}%</h2>
            <small style="color: #666;">24-Year Period</small>
        </div>
        """, unsafe_allow_html=True)
    
    def _create_protection_card(self, data: pd.Series) -> None:
        """Create protection level card"""
        protection_level = data.get('pl_2018', 'Unknown')
        protection_info = get_protection_level_info(protection_level)
        
        st.markdown(f"""
        <div style="
            border: 2px solid {protection_info['color']}; 
            border-radius: 8px; 
            padding: 12px; 
            background-color: {protection_info['color']}15;
            text-align: center;
        ">
            <h4 style="margin: 0; color: {protection_info['color']};">Protection</h4>
            <h2 style="margin: 5px 0; color: {protection_info['color']};">{protection_level}</h2>
            <small style="color: #666;">{protection_info['name']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    def _create_ecosystem_urgency_assessment(self, data: pd.Series) -> None:
        """Create urgency assessment for ecosystem"""
        iucn_code = data.get('rlev5', 'LC')
        annual_decline = data.get('prcdelyear', 0)
        current_natural = data.get('pcnat2014', 0)
        protection_level = data.get('pl_2018', 'Unknown')
        
        urgency = categorize_ecosystem_urgency(iucn_code, annual_decline, current_natural, protection_level)
        composite_score = calculate_composite_risk_score(iucn_code, annual_decline, 100 - current_natural)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            #### Conservation Urgency
            <div style="
                border: 2px solid {urgency['color']}; 
                border-radius: 8px; 
                padding: 15px; 
                background-color: {urgency['color']}15;
            ">
                <h3 style="margin: 0; color: {urgency['color']};">{urgency['category']}</h3>
                <p style="margin: 5px 0;"><strong>Timeframe:</strong> {urgency['timeframe']}</p>
                <p style="margin: 5px 0;"><strong>Risk Score:</strong> {composite_score}/100</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Recommended Actions")
            for action in urgency['recommended_actions']:
                st.markdown(f"• {action}")
    
    def create_multi_ecosystem_risk_grid(self, ecosystems_data: pd.DataFrame, title: str = "Ecosystem Risk Grid") -> None:
        """
        Create a grid view of multiple ecosystems with risk indicators
        
        Args:
            ecosystems_data: DataFrame with ecosystem data
            title: Title for the risk grid
        """
        st.markdown(f"### {title}")
        
        if ecosystems_data.empty:
            st.warning("No ecosystem data available for risk grid")
            return
        
        # Sort by risk level
        threat_order = {'CR': 1, 'EN': 2, 'VU': 3, 'NT': 4, 'LC': 5}
        ecosystems_data['threat_priority'] = ecosystems_data['rlev5'].map(threat_order).fillna(6)
        ecosystems_sorted = ecosystems_data.sort_values(['threat_priority', 'prcdelyear'], ascending=[True, False])
        
        # Create grid layout
        cols_per_row = 3
        
        for i in range(0, len(ecosystems_sorted), cols_per_row):
            row_ecosystems = ecosystems_sorted.iloc[i:i+cols_per_row]
            cols = st.columns(cols_per_row)
            
            for j, (idx, ecosystem) in enumerate(row_ecosystems.iterrows()):
                if j < len(cols):
                    with cols[j]:
                        self._create_ecosystem_risk_card(ecosystem)
    
    def _create_ecosystem_risk_card(self, ecosystem: pd.Series) -> None:
        """Create individual ecosystem risk card for grid view"""
        threat_info = get_threat_level_info(ecosystem.get('rlev5', 'LC'))
        transformation_pct = ecosystem.get('current_transformation_percentage', 0)
        annual_decline = ecosystem.get('prcdelyear', 0)
        
        st.markdown(f"""
        <div style="
            border: 2px solid {threat_info['color']}; 
            border-radius: 8px; 
            padding: 10px; 
            margin: 5px 0;
            background-color: {threat_info['color']}10;
        ">
            <h5 style="margin: 0; color: {threat_info['color']};">{ecosystem.get('name_18', 'Unknown')}</h5>
            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                <small><strong>{ecosystem.get('rlev5', 'LC')}</strong></small>
                <small>{transformation_pct:.1f}% transformed</small>
            </div>
            <div style="text-align: center; margin-top: 5px;">
                <small>{annual_decline:.3f}% annual decline</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def create_risk_heatmap(self, biome_risk_data: pd.DataFrame) -> None:
        """
        Create risk heatmap for biomes
        
        Args:
            biome_risk_data: DataFrame with biome risk metrics
        """
        st.markdown("### Risk Intensity Heatmap")
        
        if biome_risk_data.empty:
            st.warning("No data available for risk heatmap")
            return
        
        try:
            import plotly.graph_objects as go
            
            # Prepare data for heatmap
            metrics = ['high_threat_percentage', 'avg_habitat_loss_24_years', 'avg_annual_decline', 'inadequate_protection_percentage']
            metric_names = ['Threat Level %', 'Habitat Loss %', 'Annual Decline %', 'Protection Gap %']
            
            z_data = []
            for metric in metrics:
                if metric in biome_risk_data.columns:
                    z_data.append(biome_risk_data[metric].values)
                else:
                    z_data.append([0] * len(biome_risk_data))
            
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=biome_risk_data['biome_18'].values if 'biome_18' in biome_risk_data.columns else list(biome_risk_data.index),
                y=metric_names,
                colorscale='Reds',
                hoverongaps=False,
                hovertemplate='<b>%{x}</b><br>%{y}: %{z:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Biome Risk Metrics Heatmap",
                xaxis_title="Biomes",
                yaxis_title="Risk Metrics",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except ImportError:
            st.error("Plotly required for heatmap visualization")
        except Exception as e:
            st.error(f"Could not create risk heatmap: {e}")


# Convenience functions for easy component usage
def create_risk_profile_section(cache_manager, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
    """
    Create risk profile section component
    
    Args:
        cache_manager: CacheManager instance
        selections: Current geographic selections
        national_summary: National-level summary statistics
    """
    risk_panel = RiskSummaryPanel(cache_manager)
    risk_panel.create_risk_profile_section(selections, national_summary)

def create_ecosystem_risk_grid(cache_manager, ecosystems_data: pd.DataFrame, title: str = "Ecosystem Risk Grid") -> None:
    """
    Create ecosystem risk grid component
    
    Args:
        cache_manager: CacheManager instance
        ecosystems_data: DataFrame with ecosystem data
        title: Title for the risk grid
    """
    risk_panel = RiskSummaryPanel(cache_manager)
    risk_panel.create_multi_ecosystem_risk_grid(ecosystems_data, title)

def create_risk_heatmap(cache_manager, biome_risk_data: pd.DataFrame) -> None:
    """
    Create risk heatmap component
    
    Args:
        cache_manager: CacheManager instance
        biome_risk_data: DataFrame with biome risk metrics
    """
    risk_panel = RiskSummaryPanel(cache_manager)
    risk_panel.create_risk_heatmap(biome_risk_data)