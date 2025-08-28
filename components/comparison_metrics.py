"""
Comparison Metrics Component for SANBI Ecosystem Risk Atlas
Performance comparison against national averages
"""
import streamlit as st
import pandas as pd
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ComparisonMetrics:
    """Manages performance comparison calculations and display"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def create_comparison_panel(self, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
        """
        Create comparison metrics panel vs national averages
        
        Args:
            selections: Current geographic selections
            national_summary: National-level summary statistics
        """
        st.markdown("### Performance Comparison")
        
        try:
            # Determine comparison level and get appropriate data
            if selections['ecosystem'] != "All Ecosystems":
                self._create_ecosystem_comparison(selections, national_summary)
            elif selections['biome'] != "All Biomes":
                self._create_biome_comparison(selections, national_summary)
            else:
                self._create_national_overview(national_summary)
                
        except Exception as e:
            st.error(f"Could not load comparison metrics: {e}")
            logger.error(f"Comparison metrics error: {e}")
    
    def _create_biome_comparison(self, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
        """Create biome vs national comparison"""
        biome_summary = self.cache_manager.get_biome_risk_summary(selections['biome'])
        
        if not biome_summary:
            st.info("No comparison data available for selected biome")
            return
        
        # Calculate key comparison metrics
        comparisons = self._calculate_biome_comparisons(biome_summary, national_summary)
        
        # Display comparison metrics
        for metric_name, comparison in comparisons.items():
            st.metric(
                metric_name,
                comparison['local_value'],
                delta=comparison['delta_formatted'],
                delta_color=comparison['delta_color'],
                help=comparison['help_text']
            )
    
    def _create_ecosystem_comparison(self, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
        """Create individual ecosystem vs national comparison"""
        ecosystem_details = self.cache_manager.get_ecosystem_details(
            biome=selections['biome'] if selections['biome'] != "All Biomes" else None,
            bioregion=selections['bioregion'] if selections['bioregion'] != "All Bioregions" else None,
            ecosystem=selections['ecosystem']
        )
        
        if ecosystem_details.empty:
            st.info("No comparison data available for selected ecosystem")
            return
        
        ecosystem_data = ecosystem_details.iloc[0]
        comparisons = self._calculate_ecosystem_comparisons(ecosystem_data, national_summary)
        
        # Display comparison metrics
        for metric_name, comparison in comparisons.items():
            st.metric(
                metric_name,
                comparison['local_value'],
                delta=comparison['delta_formatted'],
                delta_color=comparison['delta_color'],
                help=comparison['help_text']
            )
    
    def _create_national_overview(self, national_summary: Dict[str, Any]) -> None:
        """Display national-level overview without comparisons"""
        st.info("Select a biome or ecosystem to see comparison metrics")
        
        # Show key national statistics for reference
        st.markdown("#### National Reference Values")
        
        col1, col2 = st.columns(2)
        
        with col1:
            threat_pct = national_summary.get('high_threat_percentage', 0)
            st.metric("National Threat Level", f"{threat_pct:.1f}%")
        
        with col2:
            protection_gap = national_summary.get('inadequate_protection_percentage', 0)
            st.metric("National Protection Gap", f"{protection_gap:.1f}%")
    
    def _calculate_biome_comparisons(self, biome_summary: Dict[str, Any], national_summary: Dict[str, Any]) -> Dict[str, Dict]:
        """Calculate biome vs national comparisons"""
        comparisons = {}
        
        # Threat level comparison
        national_threat_pct = national_summary.get('high_threat_percentage', 0)
        biome_cr = biome_summary.get('critically_endangered', 0)
        biome_en = biome_summary.get('endangered', 0)
        biome_total = biome_summary.get('total_ecosystems', 1)
        biome_threat_pct = ((biome_cr + biome_en) / biome_total) * 100
        
        threat_delta = biome_threat_pct - national_threat_pct
        comparisons['Threat Level vs National'] = {
            'local_value': f"{biome_threat_pct:.1f}%",
            'delta_formatted': f"{threat_delta:+.1f}pp",
            'delta_color': "inverse",
            'help_text': f"Biome: {biome_threat_pct:.1f}% vs National: {national_threat_pct:.1f}%"
        }
        
        # Natural habitat comparison
        national_natural = national_summary.get('avg_natural_habitat', 0)
        biome_natural = biome_summary.get('avg_natural_habitat', 0)
        natural_delta = biome_natural - national_natural
        
        comparisons['Natural Habitat vs National'] = {
            'local_value': f"{biome_natural:.1f}%",
            'delta_formatted': f"{natural_delta:+.1f}pp",
            'delta_color': "normal",
            'help_text': f"Biome: {biome_natural:.1f}% vs National: {national_natural:.1f}%"
        }
        
        # Annual decline comparison
        national_decline = national_summary.get('avg_annual_decline', 0)
        biome_decline = biome_summary.get('avg_annual_decline', 0)
        decline_delta = biome_decline - national_decline
        
        comparisons['Annual Decline vs National'] = {
            'local_value': f"{biome_decline:.3f}%",
            'delta_formatted': f"{decline_delta:+.3f}pp",
            'delta_color': "inverse",
            'help_text': f"Biome: {biome_decline:.3f}% vs National: {national_decline:.3f}%"
        }
        
        return comparisons
    
    def _calculate_ecosystem_comparisons(self, ecosystem_data: pd.Series, national_summary: Dict[str, Any]) -> Dict[str, Dict]:
        """Calculate individual ecosystem vs national comparisons"""
        comparisons = {}
        
        # Natural habitat comparison
        national_natural = national_summary.get('avg_natural_habitat', 0)
        ecosystem_natural = ecosystem_data.get('pcnat2014', 0)
        natural_delta = ecosystem_natural - national_natural
        
        comparisons['Natural Habitat vs National'] = {
            'local_value': f"{ecosystem_natural:.1f}%",
            'delta_formatted': f"{natural_delta:+.1f}pp",
            'delta_color': "normal",
            'help_text': f"Ecosystem: {ecosystem_natural:.1f}% vs National: {national_natural:.1f}%"
        }
        
        # Annual decline comparison
        national_decline = national_summary.get('avg_annual_decline', 0)
        ecosystem_decline = ecosystem_data.get('prcdelyear', 0)
        decline_delta = ecosystem_decline - national_decline
        
        comparisons['Annual Decline vs National'] = {
            'local_value': f"{ecosystem_decline:.3f}%",
            'delta_formatted': f"{decline_delta:+.3f}pp",
            'delta_color': "inverse",
            'help_text': f"Ecosystem: {ecosystem_decline:.3f}% vs National: {national_decline:.3f}%"
        }
        
        # Transformation comparison
        national_transformation = national_summary.get('avg_transformation', 0)
        ecosystem_transformation = ecosystem_data.get('current_transformation_percentage', 0)
        transformation_delta = ecosystem_transformation - national_transformation
        
        comparisons['Transformation vs National'] = {
            'local_value': f"{ecosystem_transformation:.1f}%",
            'delta_formatted': f"{transformation_delta:+.1f}pp",
            'delta_color': "inverse",
            'help_text': f"Ecosystem: {ecosystem_transformation:.1f}% vs National: {national_transformation:.1f}%"
        }
        
        return comparisons
    
    def calculate_performance_category(self, local_value: float, national_value: float, metric_type: str = "default") -> Dict[str, str]:
        """
        Categorize performance relative to national average
        
        Args:
            local_value: Local metric value
            national_value: National average value
            metric_type: Type of metric ("threat", "protection", "habitat", "decline")
            
        Returns:
            Dictionary with performance category and color
        """
        if national_value == 0:
            return {"category": "No Comparison", "color": "#cccccc"}
        
        ratio = local_value / national_value
        
        if metric_type in ["threat", "decline", "transformation"]:
            # Lower is better for threat metrics
            if ratio <= 0.7:
                return {"category": "Much Better", "color": "#2166ac"}
            elif ratio <= 0.9:
                return {"category": "Better", "color": "#abdda4"}
            elif ratio <= 1.1:
                return {"category": "Similar", "color": "#ffffbf"}
            elif ratio <= 1.3:
                return {"category": "Worse", "color": "#fdae61"}
            else:
                return {"category": "Much Worse", "color": "#d73027"}
        
        else:
            # Higher is better for habitat/protection metrics
            if ratio >= 1.3:
                return {"category": "Much Better", "color": "#2166ac"}
            elif ratio >= 1.1:
                return {"category": "Better", "color": "#abdda4"}
            elif ratio >= 0.9:
                return {"category": "Similar", "color": "#ffffbf"}
            elif ratio >= 0.7:
                return {"category": "Worse", "color": "#fdae61"}
            else:
                return {"category": "Much Worse", "color": "#d73027"}
    
    def create_performance_summary(self, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
        """Create a visual performance summary with color-coded indicators"""
        st.markdown("#### Performance Overview")
        
        try:
            if selections['biome'] == "All Biomes":
                st.info("Select a specific area to see performance summary")
                return
            
            # Get comparison data
            if selections['biome'] != "All Biomes":
                biome_summary = self.cache_manager.get_biome_risk_summary(selections['biome'])
                if not biome_summary:
                    return
                
                # Calculate performance categories
                biome_cr = biome_summary.get('critically_endangered', 0)
                biome_en = biome_summary.get('endangered', 0)
                biome_total = biome_summary.get('total_ecosystems', 1)
                biome_threat_pct = ((biome_cr + biome_en) / biome_total) * 100
                
                national_threat_pct = national_summary.get('high_threat_percentage', 0)
                threat_performance = self.calculate_performance_category(
                    biome_threat_pct, national_threat_pct, "threat"
                )
                
                biome_natural = biome_summary.get('avg_natural_habitat', 0)
                national_natural = national_summary.get('avg_natural_habitat', 0)
                habitat_performance = self.calculate_performance_category(
                    biome_natural, national_natural, "habitat"
                )
                
                # Display performance indicators
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="
                        background-color: {threat_performance['color']}20;
                        border-left: 4px solid {threat_performance['color']};
                        padding: 10px;
                        margin: 5px 0;
                    ">
                        <strong>Threat Level:</strong> {threat_performance['category']}<br>
                        <small>{biome_threat_pct:.1f}% vs {national_threat_pct:.1f}% national</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="
                        background-color: {habitat_performance['color']}20;
                        border-left: 4px solid {habitat_performance['color']};
                        padding: 10px;
                        margin: 5px 0;
                    ">
                        <strong>Natural Habitat:</strong> {habitat_performance['category']}<br>
                        <small>{biome_natural:.1f}% vs {national_natural:.1f}% national</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Could not create performance summary: {e}")


# Convenience functions for easy component usage
def create_comparison_metrics(cache_manager, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
    """
    Create comparison metrics component
    
    Args:
        cache_manager: CacheManager instance
        selections: Current geographic selections
        national_summary: National-level summary statistics
    """
    comparison_metrics = ComparisonMetrics(cache_manager)
    comparison_metrics.create_comparison_panel(selections, national_summary)

def create_performance_summary(cache_manager, selections: Dict[str, str], national_summary: Dict[str, Any]) -> None:
    """
    Create performance summary with visual indicators
    
    Args:
        cache_manager: CacheManager instance  
        selections: Current geographic selections
        national_summary: National-level summary statistics
    """
    comparison_metrics = ComparisonMetrics(cache_manager)
    comparison_metrics.create_performance_summary(selections, national_summary)