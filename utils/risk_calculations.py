"""
Risk Calculations Utilities for SANBI Ecosystem Risk Atlas
Risk threshold logic and performance comparison calculations
"""
import pandas as pd
from typing import Dict, Any, Optional, Union
from app.config import ECOSYSTEM_RISK_THRESHOLDS, THREAT_LEVELS, RISK_COLORS

def get_risk_level_by_threshold(risk_type: str, value: float) -> str:
    """
    Determine risk level based on value and threshold type
    
    Args:
        risk_type: Type of risk ('habitat_loss', 'annual_decline', 'transformation', 'protection_gap')
        value: The value to assess
        
    Returns:
        Risk level: 'critical', 'high', 'moderate', 'low', 'minimal'
    """
    thresholds = ECOSYSTEM_RISK_THRESHOLDS.get(risk_type, {})
    
    if not thresholds:
        return 'minimal'
    
    if value >= thresholds.get('critical', float('inf')):
        return 'critical'
    elif value >= thresholds.get('high', float('inf')):
        return 'high'
    elif value >= thresholds.get('moderate', float('inf')):
        return 'moderate'
    elif value >= thresholds.get('low', float('inf')):
        return 'low'
    else:
        return 'minimal'

def get_risk_color_by_threshold(risk_type: str, value: float) -> str:
    """
    Get color for risk value based on threshold
    
    Args:
        risk_type: Type of risk assessment
        value: The value to assess
        
    Returns:
        Hex color code for the risk level
    """
    risk_level = get_risk_level_by_threshold(risk_type, value)
    return RISK_COLORS.get(risk_level, '#cccccc')

def get_threat_level_info(threat_code: str) -> Dict[str, Any]:
    """
    Get complete information for IUCN threat level
    
    Args:
        threat_code: IUCN threat code (CR, EN, VU, NT, LC)
        
    Returns:
        Dictionary with name, color, priority, and description
    """
    base_info = THREAT_LEVELS.get(threat_code, THREAT_LEVELS.get('', {}))
    
    descriptions = {
        "CR": "Facing extremely high risk of extinction in the wild",
        "EN": "Facing very high risk of extinction in the wild", 
        "VU": "Facing high risk of extinction in the wild",
        "NT": "Close to qualifying for threatened category",
        "LC": "Widespread and abundant, lowest risk category"
    }
    
    return {
        **base_info,
        'description': descriptions.get(threat_code, "Classification pending or data deficient"),
        'code': threat_code
    }

def get_protection_level_info(protection_code: str) -> Dict[str, Any]:
    """
    Get information for protection level
    
    Args:
        protection_code: Protection code (WP, MP, PP, NP)
        
    Returns:
        Dictionary with name, color, and description
    """
    protection_info = {
        'WP': {
            'name': 'Well Protected',
            'color': '#2166ac',
            'description': 'Exceeds biodiversity conservation target',
            'status': 'success'
        },
        'MP': {
            'name': 'Moderately Protected', 
            'color': '#abdda4',
            'description': '50-99% of biodiversity target protected',
            'status': 'moderate'
        },
        'PP': {
            'name': 'Poorly Protected',
            'color': '#fdae61', 
            'description': '5-49% of biodiversity target protected',
            'status': 'warning'
        },
        'NP': {
            'name': 'Not Protected',
            'color': '#d73027',
            'description': 'Less than 5% of biodiversity target protected', 
            'status': 'critical'
        }
    }
    
    return protection_info.get(protection_code, {
        'name': 'Unknown',
        'color': '#cccccc', 
        'description': 'Protection status unknown',
        'status': 'unknown'
    })

def calculate_composite_risk_score(iucn_code: str, annual_decline: float, 
                                 transformation_pct: float) -> float:
    """
    Calculate composite risk score using SANBI methodology
    
    Args:
        iucn_code: IUCN threat level code
        annual_decline: Annual percentage decline rate
        transformation_pct: Current transformation percentage
        
    Returns:
        Composite risk score (0-100)
    """
    # IUCN threat score
    iucn_scores = {'CR': 50, 'EN': 30, 'VU': 15, 'NT': 5, 'LC': 0}
    iucn_score = iucn_scores.get(iucn_code, 0)
    
    # Annual decline score
    if annual_decline > 0.3:
        decline_score = 25
    elif annual_decline > 0.2:
        decline_score = 15
    elif annual_decline > 0.1:
        decline_score = 10
    elif annual_decline > 0.05:
        decline_score = 5
    else:
        decline_score = 0
    
    # Transformation score
    if transformation_pct > 50:
        transformation_score = 25
    elif transformation_pct > 25:
        transformation_score = 15
    elif transformation_pct > 15:
        transformation_score = 10
    else:
        transformation_score = 0
    
    return iucn_score + decline_score + transformation_score

def assess_risk_trajectory(current_natural: float, annual_decline: float, 
                          protection_level: str) -> Dict[str, Any]:
    """
    Assess ecosystem risk trajectory and provide recommendations
    
    Args:
        current_natural: Current natural habitat percentage
        annual_decline: Annual decline rate
        protection_level: Protection level code
        
    Returns:
        Dictionary with trajectory assessment and recommendations
    """
    trajectory = {'level': 'stable', 'color': '#abdda4', 'urgency': 'low'}
    recommendations = []
    
    # Assess current status
    if current_natural < 30:
        trajectory.update({'level': 'critical', 'color': '#d73027', 'urgency': 'immediate'})
        recommendations.append("Immediate intervention required")
        recommendations.append("Emergency conservation measures needed")
    elif current_natural < 50:
        trajectory.update({'level': 'high_risk', 'color': '#f46d43', 'urgency': 'high'})
        recommendations.append("Urgent conservation action required")
    elif current_natural < 70:
        trajectory.update({'level': 'moderate_risk', 'color': '#fdae61', 'urgency': 'moderate'})
        recommendations.append("Active monitoring and management needed")
    
    # Assess decline rate
    if annual_decline > 0.2:
        if trajectory['urgency'] != 'immediate':
            trajectory.update({'urgency': 'high'})
        recommendations.append("Address rapid decline causes")
    elif annual_decline > 0.1:
        recommendations.append("Monitor decline trends closely")
    
    # Assess protection status
    protection_info = get_protection_level_info(protection_level)
    if protection_info['status'] in ['critical', 'warning']:
        recommendations.append("Improve protection coverage")
        if trajectory['urgency'] == 'low':
            trajectory.update({'urgency': 'moderate'})
    
    return {
        'trajectory': trajectory,
        'recommendations': recommendations,
        'protection_status': protection_info
    }

def calculate_performance_vs_national(local_value: float, national_value: float, 
                                    metric_type: str = "default") -> Dict[str, Any]:
    """
    Calculate performance comparison against national average
    
    Args:
        local_value: Local area value
        national_value: National average value  
        metric_type: Type of metric for proper comparison direction
        
    Returns:
        Dictionary with performance category, delta, and formatting
    """
    if national_value == 0:
        return {
            'category': 'No Comparison',
            'color': '#cccccc',
            'delta': 0,
            'delta_formatted': 'N/A',
            'performance_ratio': 1.0
        }
    
    delta = local_value - national_value
    ratio = local_value / national_value
    
    # Determine if higher or lower values are better
    better_when_higher = metric_type in ["habitat", "protection", "natural"]
    better_when_lower = metric_type in ["threat", "decline", "transformation", "loss"]
    
    # Calculate performance category
    if better_when_lower:
        if ratio <= 0.7:
            category, color = "Much Better", "#2166ac"
        elif ratio <= 0.9:
            category, color = "Better", "#abdda4"
        elif ratio <= 1.1:
            category, color = "Similar", "#ffffbf"
        elif ratio <= 1.3:
            category, color = "Worse", "#fdae61"
        else:
            category, color = "Much Worse", "#d73027"
    elif better_when_higher:
        if ratio >= 1.3:
            category, color = "Much Better", "#2166ac"
        elif ratio >= 1.1:
            category, color = "Better", "#abdda4"
        elif ratio >= 0.9:
            category, color = "Similar", "#ffffbf"
        elif ratio >= 0.7:
            category, color = "Worse", "#fdae61"
        else:
            category, color = "Much Worse", "#d73027"
    else:
        # Default: closer to national average is better
        if abs(ratio - 1) <= 0.1:
            category, color = "Similar", "#ffffbf"
        elif abs(ratio - 1) <= 0.3:
            category, color = "Moderate Difference", "#fdae61"
        else:
            category, color = "Large Difference", "#d73027"
    
    # Format delta
    delta_sign = "+" if delta > 0 else ""
    if abs(delta) >= 1:
        delta_formatted = f"{delta_sign}{delta:.1f}pp"
    else:
        delta_formatted = f"{delta_sign}{delta:.2f}pp"
    
    return {
        'category': category,
        'color': color,
        'delta': delta,
        'delta_formatted': delta_formatted, 
        'performance_ratio': ratio,
        'local_value': local_value,
        'national_value': national_value
    }

def get_risk_summary_stats(ecosystem_data: Union[pd.DataFrame, pd.Series]) -> Dict[str, Any]:
    """
    Calculate comprehensive risk summary statistics
    
    Args:
        ecosystem_data: DataFrame with ecosystem data or Series for single ecosystem
        
    Returns:
        Dictionary with calculated risk statistics
    """
    if isinstance(ecosystem_data, pd.Series):
        # Single ecosystem
        return {
            'total_ecosystems': 1,
            'threat_distribution': {ecosystem_data.get('rlev5', 'LC'): 1},
            'avg_natural_habitat': ecosystem_data.get('pcnat2014', 0),
            'avg_annual_decline': ecosystem_data.get('prcdelyear', 0),
            'avg_transformation': ecosystem_data.get('current_transformation_percentage', 0),
            'composite_risk_score': calculate_composite_risk_score(
                ecosystem_data.get('rlev5', 'LC'),
                ecosystem_data.get('prcdelyear', 0), 
                ecosystem_data.get('current_transformation_percentage', 0)
            )
        }
    
    else:
        # Multiple ecosystems
        threat_counts = ecosystem_data['rlev5'].value_counts().to_dict()
        
        return {
            'total_ecosystems': len(ecosystem_data),
            'threat_distribution': threat_counts,
            'critically_endangered': threat_counts.get('CR', 0),
            'endangered': threat_counts.get('EN', 0),
            'vulnerable': threat_counts.get('VU', 0),
            'high_threat_count': threat_counts.get('CR', 0) + threat_counts.get('EN', 0),
            'high_threat_percentage': ((threat_counts.get('CR', 0) + threat_counts.get('EN', 0)) / len(ecosystem_data) * 100) if len(ecosystem_data) > 0 else 0,
            'avg_natural_habitat': ecosystem_data['pcnat2014'].mean(),
            'avg_annual_decline': ecosystem_data['prcdelyear'].mean(),
            'avg_transformation': ecosystem_data.get('current_transformation_percentage', pd.Series([0])).mean(),
            'max_decline_rate': ecosystem_data['prcdelyear'].max(),
            'min_natural_habitat': ecosystem_data['pcnat2014'].min()
        }

def categorize_ecosystem_urgency(iucn_code: str, annual_decline: float, 
                               current_natural: float, protection_level: str) -> Dict[str, Any]:
    """
    Categorize ecosystem conservation urgency
    
    Args:
        iucn_code: IUCN threat level
        annual_decline: Annual decline percentage
        current_natural: Current natural habitat percentage
        protection_level: Protection level code
        
    Returns:
        Dictionary with urgency category and action recommendations
    """
    urgency_score = 0
    
    # IUCN contribution
    iucn_urgency = {'CR': 4, 'EN': 3, 'VU': 2, 'NT': 1, 'LC': 0}
    urgency_score += iucn_urgency.get(iucn_code, 0)
    
    # Decline rate contribution
    if annual_decline > 0.3:
        urgency_score += 3
    elif annual_decline > 0.1:
        urgency_score += 2
    elif annual_decline > 0.05:
        urgency_score += 1
    
    # Current habitat contribution
    if current_natural < 30:
        urgency_score += 3
    elif current_natural < 50:
        urgency_score += 2
    elif current_natural < 70:
        urgency_score += 1
    
    # Protection contribution
    protection_urgency = {'NP': 2, 'PP': 1, 'MP': 0, 'WP': -1}
    urgency_score += protection_urgency.get(protection_level, 0)
    
    # Categorize urgency
    if urgency_score >= 8:
        category = "Emergency"
        color = "#8B0000"
        timeframe = "Immediate (0-1 years)"
        actions = ["Emergency intervention", "Immediate threat mitigation", "Expert assessment"]
    elif urgency_score >= 6:
        category = "Critical"
        color = "#d73027" 
        timeframe = "Urgent (1-3 years)"
        actions = ["Priority conservation", "Threat assessment", "Management plan"]
    elif urgency_score >= 4:
        category = "High"
        color = "#f46d43"
        timeframe = "High priority (3-5 years)" 
        actions = ["Active management", "Monitoring program", "Threat reduction"]
    elif urgency_score >= 2:
        category = "Moderate"
        color = "#fdae61"
        timeframe = "Regular monitoring (5-10 years)"
        actions = ["Regular monitoring", "Preventive measures", "Research needs"]
    else:
        category = "Low"
        color = "#abdda4" 
        timeframe = "Stable management"
        actions = ["Maintain current protection", "Periodic assessment"]
    
    return {
        'category': category,
        'color': color,
        'urgency_score': urgency_score,
        'timeframe': timeframe,
        'recommended_actions': actions
    }