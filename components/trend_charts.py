"""
Trend Charts Component for SANBI Ecosystem Risk Atlas
Temporal analysis visualization: 1990→2014→2040
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)

class TrendCharts:
    """Manages temporal trend analysis and visualization"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def create_trend_analysis_section(self, selections: Dict[str, str]) -> None:
        """
        Create temporal trend analysis section based on geographic selection
        
        Args:
            selections: Current geographic selections (biome, bioregion, ecosystem)
        """
        st.markdown("### Temporal Trend Analysis")
        
        try:
            if selections['ecosystem'] != "All Ecosystems":
                self._create_ecosystem_trend_analysis(selections)
            elif selections['biome'] != "All Biomes":
                self._create_biome_trend_analysis(selections['biome'])
            else:
                self._create_national_trend_analysis()
                
        except Exception as e:
            st.error(f"Could not load trend analysis: {e}")
            logger.error(f"Trend analysis error: {e}")
    
    def _create_biome_trend_analysis(self, biome: str) -> None:
        """Create trend analysis for specific biome"""
        habitat_data = self.cache_manager.get_habitat_transformation_data()
        biome_data = habitat_data[habitat_data['biome_18'] == biome]
        
        if biome_data.empty:
            st.warning(f"No trend data available for {biome}")
            return
        
        data = biome_data.iloc[0]
        
        # Create main habitat trend chart
        self._create_habitat_trend_chart(data, biome)
        
        # Create additional metrics
        col1, col2 = st.columns(2)
        
        with col1:
            self._create_loss_rate_metrics(data)
        
        with col2:
            self._create_projection_insights(data, biome)
    
    def _create_ecosystem_trend_analysis(self, selections: Dict[str, str]) -> None:
        """Create trend analysis for individual ecosystem"""
        ecosystem_details = self.cache_manager.get_ecosystem_details(
            biome=selections['biome'] if selections['biome'] != "All Biomes" else None,
            bioregion=selections['bioregion'] if selections['bioregion'] != "All Bioregions" else None,
            ecosystem=selections['ecosystem']
        )
        
        if ecosystem_details.empty:
            st.warning(f"No trend data available for {selections['ecosystem']}")
            return
        
        ecosystem_data = ecosystem_details.iloc[0]
        
        # Individual ecosystem trends
        self._create_individual_ecosystem_trends(ecosystem_data, selections['ecosystem'])
        
        # Ecosystem-specific insights
        self._create_ecosystem_trend_insights(ecosystem_data)
    
    def _create_national_trend_analysis(self) -> None:
        """Create national-level trend overview"""
        st.info("Select a specific biome or ecosystem to view detailed trend analysis")
        
        # Show aggregate national trends
        habitat_data = self.cache_manager.get_habitat_transformation_data()
        
        if not habitat_data.empty:
            # Calculate national averages
            national_trends = {
                '1990': habitat_data['avg_natural_1990'].mean(),
                '2014': habitat_data['avg_natural_2014'].mean(),
                '2040 (projected)': habitat_data['avg_natural_2040_projected'].mean()
            }
            
            # Create national trend overview
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(national_trends.keys()),
                y=list(national_trends.values()),
                mode='lines+markers',
                name='National Average',
                line=dict(color='#2E8B57', width=4),
                marker=dict(size=12)
            ))
            
            fig.update_layout(
                title="National Habitat Trends (All Biomes Average)",
                xaxis_title="Time Period",
                yaxis_title="Natural Habitat (%)",
                height=400,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _create_habitat_trend_chart(self, data: pd.Series, biome: str) -> None:
        """Create main habitat trend visualization"""
        # Prepare data
        years = ['1990', '2014', '2040 (projected)']
        natural_habitat = [
            data.get('avg_natural_1990', 0),
            data.get('avg_natural_2014', 0),
            data.get('avg_natural_2040_projected', 0)
        ]
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Main habitat trend line
        fig.add_trace(
            go.Scatter(
                x=years,
                y=natural_habitat,
                mode='lines+markers',
                name='Natural Habitat %',
                line=dict(color='#2E8B57', width=4),
                marker=dict(size=12, color='#2E8B57'),
                hovertemplate='<b>%{x}</b><br>Natural Habitat: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=False
        )
        
        # Add transformation percentage (inverse)
        transformation_pct = [100 - x for x in natural_habitat]
        fig.add_trace(
            go.Scatter(
                x=years,
                y=transformation_pct,
                mode='lines+markers',
                name='Transformed %',
                line=dict(color='#d73027', width=3, dash='dash'),
                marker=dict(size=10, color='#d73027'),
                hovertemplate='<b>%{x}</b><br>Transformed: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=True
        )
        
        # Add shaded areas for historical vs projected
        fig.add_vrect(
            x0=-0.5, x1=1.5,
            fillcolor="lightblue", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Historical", annotation_position="top left"
        )
        
        fig.add_vrect(
            x0=1.5, x1=2.5,
            fillcolor="lightyellow", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Projected", annotation_position="top right"
        )
        
        # Update layout
        fig.update_layout(
            title=f"Habitat Transformation Trend: {biome}",
            xaxis_title="Time Period",
            height=500,
            hovermode='x unified',
            legend=dict(x=0.02, y=0.98)
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Natural Habitat (%)", secondary_y=False, range=[0, 100])
        fig.update_yaxes(title_text="Transformed (%)", secondary_y=True, range=[0, 100])
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_loss_rate_metrics(self, data: pd.Series) -> None:
        """Create loss rate metrics panel"""
        st.markdown("#### Historical vs Projected Loss")
        
        # Calculate metrics
        historical_loss = data.get('avg_habitat_loss_24_years', 0)
        projected_loss = data.get('avg_projected_loss_26_years', 0)
        
        # Historical loss (1990-2014)
        st.metric(
            "Historical Loss (1990-2014)",
            f"{historical_loss:.2f}%",
            help="Actual habitat loss over 24-year period"
        )
        
        # Projected loss (2014-2040)
        st.metric(
            "Projected Loss (2014-2040)",
            f"{projected_loss:.2f}%",
            delta=f"{projected_loss - historical_loss:+.2f}% vs historical",
            delta_color="inverse",
            help="Projected habitat loss over 26-year period"
        )
        
        # Annual rates
        historical_annual = historical_loss / 24 if historical_loss else 0
        projected_annual = projected_loss / 26 if projected_loss else 0
        
        st.metric(
            "Rate Change",
            f"{projected_annual:.3f}% per year",
            delta=f"{projected_annual - historical_annual:+.3f}% vs historical rate",
            delta_color="inverse",
            help="Change in annual loss rate between periods"
        )
    
    def _create_projection_insights(self, data: pd.Series, biome: str) -> None:
        """Create projection insights and warnings"""
        st.markdown("#### Trend Insights")
        
        # Calculate key insights
        current_natural = data.get('avg_natural_2014', 0)
        projected_natural = data.get('avg_natural_2040_projected', 0)
        projected_loss = data.get('avg_projected_loss_26_years', 0)
        
        # Risk assessment based on projections
        if projected_natural < 30:
            st.error(f"""
            **High Risk Trajectory**  
            By 2040: Only {projected_natural:.1f}% natural habitat projected to remain
            """)
        elif projected_natural < 50:
            st.warning(f"""
            **Moderate Risk Trajectory**  
            By 2040: {projected_natural:.1f}% natural habitat projected to remain
            """)
        else:
            st.success(f"""
            **Stable Trajectory**  
            By 2040: {projected_natural:.1f}% natural habitat projected to remain
            """)
        
        # Time to critical thresholds
        if projected_loss > 0:
            years_to_50pct = self._calculate_years_to_threshold(current_natural, projected_loss, 50, 26)
            if years_to_50pct and years_to_50pct > 0:
                if years_to_50pct < 50:
                    st.info(f"**Time to 50% natural:** ~{years_to_50pct:.0f} years at current rate")
    
    def _create_individual_ecosystem_trends(self, ecosystem_data: pd.Series, ecosystem_name: str) -> None:
        """Create trend analysis for individual ecosystem"""
        # Individual ecosystems don't have the same temporal data structure
        # Focus on current metrics and decline rates
        
        current_natural = ecosystem_data.get('pcnat2014', 0)
        annual_decline = ecosystem_data.get('prcdelyear', 0)
        historical_loss = ecosystem_data.get('habitat_loss_24_years', 0)
        
        # Create projection based on current decline rate
        if annual_decline > 0:
            projected_26yr = current_natural * (1 - annual_decline/100)**26
            projected_natural_2040 = max(0, projected_26yr)
        else:
            projected_natural_2040 = current_natural
        
        # Estimate 1990 value from historical loss
        estimated_1990 = current_natural + historical_loss if historical_loss else current_natural
        
        # Create trend chart
        years = ['1990 (est)', '2014', '2040 (projected)']
        natural_habitat = [estimated_1990, current_natural, projected_natural_2040]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=natural_habitat,
            mode='lines+markers',
            name=f'{ecosystem_name}',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title=f"Individual Ecosystem Trend: {ecosystem_name}",
            xaxis_title="Time Period",
            yaxis_title="Natural Habitat (%)",
            height=400,
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_ecosystem_trend_insights(self, ecosystem_data: pd.Series) -> None:
        """Create insights for individual ecosystem trends"""
        annual_decline = ecosystem_data.get('prcdelyear', 0)
        current_natural = ecosystem_data.get('pcnat2014', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Current Natural Habitat",
                f"{current_natural:.1f}%"
            )
            
            st.metric(
                "Annual Decline Rate",
                f"{annual_decline:.3f}%",
                help="Current rate of vegetation decline per year"
            )
        
        with col2:
            # Calculate time to critical thresholds
            if annual_decline > 0:
                years_to_50pct = self._calculate_years_to_threshold_simple(current_natural, annual_decline, 50)
                years_to_30pct = self._calculate_years_to_threshold_simple(current_natural, annual_decline, 30)
                
                if years_to_50pct and years_to_50pct > 0:
                    st.metric(
                        "Years to 50% Natural",
                        f"{years_to_50pct:.0f} years",
                        help="Time to reach 50% natural habitat at current decline rate"
                    )
                
                if years_to_30pct and years_to_30pct > 0 and years_to_30pct < 100:
                    st.metric(
                        "Years to 30% Natural",
                        f"{years_to_30pct:.0f} years",
                        help="Time to reach critical 30% threshold"
                    )
    
    def _calculate_years_to_threshold(self, current_pct: float, loss_over_26_years: float, 
                                    threshold: float, period_years: int) -> Optional[float]:
        """Calculate years to reach a habitat threshold"""
        if loss_over_26_years <= 0 or current_pct <= threshold:
            return None
        
        annual_loss_rate = loss_over_26_years / period_years
        years_needed = (current_pct - threshold) / annual_loss_rate
        
        return years_needed if years_needed > 0 else None
    
    def _calculate_years_to_threshold_simple(self, current_pct: float, annual_decline_pct: float, 
                                           threshold: float) -> Optional[float]:
        """Calculate years to threshold using simple decline rate"""
        if annual_decline_pct <= 0 or current_pct <= threshold:
            return None
        
        # Using exponential decay: final = initial * (1 - rate)^years
        # Solving for years: years = log(final/initial) / log(1 - rate)
        import math
        
        try:
            decay_factor = 1 - (annual_decline_pct / 100)
            if decay_factor <= 0:
                return None
            
            years = math.log(threshold / current_pct) / math.log(decay_factor)
            return years if years > 0 else None
            
        except (ValueError, ZeroDivisionError):
            return None
    
    def create_comparative_trend_analysis(self, selections_list: List[Dict[str, str]]) -> None:
        """Create comparative trend analysis for multiple areas"""
        st.markdown("### Comparative Trend Analysis")
        
        if len(selections_list) < 2:
            st.info("Select multiple areas to compare trends")
            return
        
        fig = go.Figure()
        colors = ['#2E8B57', '#d73027', '#fdae61', '#abdda4', '#2166ac']
        
        try:
            for i, selections in enumerate(selections_list):
                if selections['biome'] != "All Biomes":
                    habitat_data = self.cache_manager.get_habitat_transformation_data()
                    biome_data = habitat_data[habitat_data['biome_18'] == selections['biome']]
                    
                    if not biome_data.empty:
                        data = biome_data.iloc[0]
                        
                        years = ['1990', '2014', '2040']
                        natural_habitat = [
                            data.get('avg_natural_1990', 0),
                            data.get('avg_natural_2014', 0),
                            data.get('avg_natural_2040_projected', 0)
                        ]
                        
                        fig.add_trace(go.Scatter(
                            x=years,
                            y=natural_habitat,
                            mode='lines+markers',
                            name=selections['biome'],
                            line=dict(color=colors[i % len(colors)], width=3),
                            marker=dict(size=8)
                        ))
            
            fig.update_layout(
                title="Comparative Biome Trends",
                xaxis_title="Time Period",
                yaxis_title="Natural Habitat (%)",
                height=500,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Could not create comparative analysis: {e}")


# Convenience functions for easy component usage
def create_trend_analysis(cache_manager, selections: Dict[str, str]) -> None:
    """
    Create trend analysis component
    
    Args:
        cache_manager: CacheManager instance
        selections: Current geographic selections
    """
    trend_charts = TrendCharts(cache_manager)
    trend_charts.create_trend_analysis_section(selections)

def create_comparative_trends(cache_manager, selections_list: List[Dict[str, str]]) -> None:
    """
    Create comparative trend analysis for multiple areas
    
    Args:
        cache_manager: CacheManager instance
        selections_list: List of geographic selections to compare
    """
    trend_charts = TrendCharts(cache_manager)
    trend_charts.create_comparative_trend_analysis(selections_list)