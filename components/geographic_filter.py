"""
Geographic Filter Component for SANBI Ecosystem Risk Atlas
Three-level filtering: Biome → Bioregion → Ecosystem
"""
import streamlit as st
import pandas as pd
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class GeographicFilter:
    """Manages three-level geographic filtering hierarchy"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def create_filter_sidebar(self) -> Dict[str, str]:
        """
        Create the complete geographic filtering interface in sidebar
        
        Returns:
            Dict containing selected biome, bioregion, and ecosystem
        """
        st.sidebar.markdown("### Geographic Selection")
        
        # Initialize selection state
        if 'geo_selections' not in st.session_state:
            st.session_state.geo_selections = {
                'biome': 'All Biomes',
                'bioregion': 'All Bioregions', 
                'ecosystem': 'All Ecosystems'
            }
        
        # Step 1: Biome selection
        selected_biome = self._create_biome_selector()
        
        # Step 2: Bioregion selection (conditional on biome)
        selected_bioregion = self._create_bioregion_selector(selected_biome)
        
        # Step 3: Ecosystem selection (conditional on biome and bioregion)
        selected_ecosystem = self._create_ecosystem_selector(selected_biome, selected_bioregion)
        
        # Update session state
        st.session_state.geo_selections.update({
            'biome': selected_biome,
            'bioregion': selected_bioregion,
            'ecosystem': selected_ecosystem
        })
        
        # Display selection summary
        self._display_selection_summary(selected_biome, selected_bioregion, selected_ecosystem)
        
        return {
            'biome': selected_biome,
            'bioregion': selected_bioregion, 
            'ecosystem': selected_ecosystem
        }
    
    def _create_biome_selector(self) -> str:
        """Create biome selection dropdown"""
        try:
            biomes = self.cache_manager.get_biomes()
            
            if biomes.empty:
                st.sidebar.error("No biome data available")
                return "All Biomes"
            
            biome_options = ["All Biomes"] + sorted(biomes['biome_18'].tolist())
            
            selected_biome = st.sidebar.selectbox(
                "Select Biome:",
                options=biome_options,
                index=biome_options.index(st.session_state.geo_selections['biome']) 
                      if st.session_state.geo_selections['biome'] in biome_options else 0,
                help="Choose a biome to explore its bioregions and ecosystems",
                key="biome_selector"
            )
            
            # Reset dependent selections if biome changed
            if selected_biome != st.session_state.geo_selections.get('biome'):
                st.session_state.geo_selections['bioregion'] = 'All Bioregions'
                st.session_state.geo_selections['ecosystem'] = 'All Ecosystems'
            
            return selected_biome
            
        except Exception as e:
            st.sidebar.error(f"Error loading biomes: {e}")
            logger.error(f"Biome selector error: {e}")
            return "All Biomes"
    
    def _create_bioregion_selector(self, selected_biome: str) -> str:
        """Create bioregion selection dropdown based on selected biome"""
        if selected_biome == "All Biomes":
            return "All Bioregions"
        
        try:
            bioregions = self.cache_manager.get_bioregions(biome=selected_biome)
            
            if bioregions.empty:
                st.sidebar.info(f"No bioregions available for {selected_biome}")
                return "All Bioregions"
            
            bioregion_options = ["All Bioregions"] + sorted(bioregions['bioregion_'].tolist())
            
            selected_bioregion = st.sidebar.selectbox(
                "Select Bioregion:",
                options=bioregion_options,
                index=bioregion_options.index(st.session_state.geo_selections['bioregion']) 
                      if st.session_state.geo_selections['bioregion'] in bioregion_options else 0,
                help="Choose a specific bioregion within the selected biome",
                key="bioregion_selector"
            )
            
            # Reset ecosystem selection if bioregion changed
            if selected_bioregion != st.session_state.geo_selections.get('bioregion'):
                st.session_state.geo_selections['ecosystem'] = 'All Ecosystems'
            
            return selected_bioregion
            
        except Exception as e:
            st.sidebar.error(f"Error loading bioregions: {e}")
            logger.error(f"Bioregion selector error: {e}")
            return "All Bioregions"
    
    def _create_ecosystem_selector(self, selected_biome: str, selected_bioregion: str) -> str:
        """Create ecosystem selection dropdown based on biome and bioregion"""
        if selected_biome == "All Biomes":
            return "All Ecosystems"
        
        try:
            # Build ecosystem filters
            ecosystem_filters = {'biome': selected_biome}
            if selected_bioregion != "All Bioregions":
                ecosystem_filters['bioregion'] = selected_bioregion
            
            ecosystems = self.cache_manager.get_ecosystems(**ecosystem_filters)
            
            if ecosystems.empty:
                selection_text = f"{selected_biome}"
                if selected_bioregion != "All Bioregions":
                    selection_text += f" → {selected_bioregion}"
                st.sidebar.info(f"No ecosystems available for {selection_text}")
                return "All Ecosystems"
            
            ecosystem_options = ["All Ecosystems"] + sorted(ecosystems['name_18'].tolist())
            
            selected_ecosystem = st.sidebar.selectbox(
                "Select Ecosystem:",
                options=ecosystem_options,
                index=ecosystem_options.index(st.session_state.geo_selections['ecosystem']) 
                      if st.session_state.geo_selections['ecosystem'] in ecosystem_options else 0,
                help="Choose a specific ecosystem type for detailed analysis",
                key="ecosystem_selector"
            )
            
            return selected_ecosystem
            
        except Exception as e:
            st.sidebar.error(f"Error loading ecosystems: {e}")
            logger.error(f"Ecosystem selector error: {e}")
            return "All Ecosystems"
    
    def _display_selection_summary(self, biome: str, bioregion: str, ecosystem: str):
        """Display current geographic selection summary"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Current Selection:**")
        
        # Biome
        st.sidebar.markdown(f"**Biome:** {biome}")
        
        # Bioregion (only if not "All")
        if bioregion != "All Bioregions":
            st.sidebar.markdown(f"**Bioregion:** {bioregion}")
        
        # Ecosystem (only if not "All")
        if ecosystem != "All Ecosystems":
            st.sidebar.markdown(f"**Ecosystem:** {ecosystem}")
        
        # Show selection path
        path_parts = [biome]
        if bioregion != "All Bioregions":
            path_parts.append(bioregion)
        if ecosystem != "All Ecosystems":
            path_parts.append(ecosystem)
        
        if len(path_parts) > 1:
            selection_path = " → ".join(path_parts)
            st.sidebar.markdown(f"*Path: {selection_path}*")
    
    def get_selection_level(self, selections: Dict[str, str]) -> str:
        """
        Determine the current selection level for appropriate data display
        
        Returns:
            'national', 'biome', 'bioregion', or 'ecosystem'
        """
        if selections['ecosystem'] != "All Ecosystems":
            return 'ecosystem'
        elif selections['bioregion'] != "All Bioregions":
            return 'bioregion'
        elif selections['biome'] != "All Biomes":
            return 'biome'
        else:
            return 'national'
    
    def get_ecosystem_count_info(self, selections: Dict[str, str]) -> Dict[str, int]:
        """
        Get count information for current selection
        
        Returns:
            Dictionary with counts for current selection level
        """
        try:
            if selections['biome'] == "All Biomes":
                # National level - get biome counts
                biomes = self.cache_manager.get_biomes()
                return {
                    'total_biomes': len(biomes),
                    'total_ecosystems': biomes['ecosystem_count'].sum() if not biomes.empty else 0
                }
            
            elif selections['bioregion'] == "All Bioregions":
                # Biome level - get bioregion and ecosystem counts
                bioregions = self.cache_manager.get_bioregions(biome=selections['biome'])
                ecosystems = self.cache_manager.get_ecosystems(biome=selections['biome'])
                return {
                    'total_bioregions': len(bioregions),
                    'total_ecosystems': len(ecosystems)
                }
            
            elif selections['ecosystem'] == "All Ecosystems":
                # Bioregion level - get ecosystem count
                ecosystems = self.cache_manager.get_ecosystems(
                    biome=selections['biome'],
                    bioregion=selections['bioregion']
                )
                return {
                    'total_ecosystems': len(ecosystems)
                }
            
            else:
                # Individual ecosystem level
                return {'individual_ecosystem': True}
                
        except Exception as e:
            logger.error(f"Error getting count info: {e}")
            return {}
    
    def create_breadcrumb_navigation(self, selections: Dict[str, str]) -> None:
        """Create breadcrumb-style navigation showing selection hierarchy"""
        breadcrumbs = []
        
        if selections['biome'] == "All Biomes":
            breadcrumbs.append("** South Africa **")
        else:
            breadcrumbs.append("South Africa")
            
            # Add biome level
            if selections['bioregion'] == "All Bioregions":
                breadcrumbs.append(f"** {selections['biome']}**")
            else:
                breadcrumbs.append(f" {selections['biome']}")
                
                # Add bioregion level
                if selections['ecosystem'] == "All Ecosystems":
                    breadcrumbs.append(f"**🗺️ {selections['bioregion']}**")
                else:
                    breadcrumbs.append(f"🗺️ {selections['bioregion']}")
                    
                    # Add ecosystem level
                    breadcrumbs.append(f"**🏞️ {selections['ecosystem']}**")
        
        st.markdown(" → ".join(breadcrumbs))


def create_geographic_filter(cache_manager) -> Dict[str, str]:
    """
    Create geographic filter component and return selections
    
    Args:
        cache_manager: CacheManager instance
        
    Returns:
        Dictionary with selected biome, bioregion, and ecosystem
    """
    geo_filter = GeographicFilter(cache_manager)
    return geo_filter.create_filter_sidebar()

def get_selection_level(selections: Dict[str, str]) -> str:
    """Get the current selection level"""
    geo_filter = GeographicFilter(None) 
    return geo_filter.get_selection_level(selections)

def create_breadcrumb_navigation(selections: Dict[str, str]) -> None:
    """Create breadcrumb navigation for current selection"""
    geo_filter = GeographicFilter(None)
    geo_filter.create_breadcrumb_navigation(selections)