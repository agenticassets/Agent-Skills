#!/usr/bin/env python3
"""
Sensitivity and Scenario Analysis for Commercial Real Estate
Monte Carlo simulation and stress testing capabilities
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable
from scipy import stats


def two_way_sensitivity_table(
    base_inputs: Dict,
    var1_name: str,
    var1_range: List[float],
    var2_name: str,
    var2_range: List[float],
    metric_func: Callable,
    format_pct: bool = True
) -> pd.DataFrame:
    """
    Create a two-way sensitivity table (e.g., IRR sensitivity to exit cap and rent growth)
    
    Args:
        base_inputs: Dictionary of base case inputs
        var1_name: Name of first variable (rows)
        var1_range: List of values for first variable
        var2_name: Name of second variable (columns)
        var2_range: List of values for second variable
        metric_func: Function that calculates metric from inputs dict
        format_pct: Whether to format output as percentages
    
    Returns:
        Pandas DataFrame with sensitivity results
    """
    results = []
    
    for val1 in var1_range:
        row = []
        for val2 in var2_range:
            inputs = base_inputs.copy()
            inputs[var1_name] = val1
            inputs[var2_name] = val2
            metric_value = metric_func(inputs)
            row.append(metric_value * 100 if format_pct else metric_value)
        results.append(row)
    
    # Create DataFrame
    if format_pct:
        col_labels = [f"{val*100:.1f}%" for val in var2_range]
        row_labels = [f"{val*100:.1f}%" for val in var1_range]
    else:
        col_labels = [f"{val:.3f}" for val in var2_range]
        row_labels = [f"{val:.3f}" for val in var1_range]
    
    df = pd.DataFrame(results, index=row_labels, columns=col_labels)
    df.index.name = var1_name
    df.columns.name = var2_name
    
    return df


def scenario_analysis(
    scenarios: Dict[str, Dict],
    metric_func: Callable,
    metric_name: str = "IRR"
) -> pd.DataFrame:
    """
    Perform scenario analysis (Base, Downside, Upside)
    
    Args:
        scenarios: Dict of scenario names to input dicts
        metric_func: Function that calculates metric from inputs
        metric_name: Name of the metric being calculated
    
    Returns:
        DataFrame with scenario results
    """
    results = {}
    
    for scenario_name, inputs in scenarios.items():
        metric_value = metric_func(inputs)
        results[scenario_name] = metric_value
    
    df = pd.DataFrame.from_dict(results, orient='index', columns=[metric_name])
    df.index.name = 'Scenario'
    
    return df


def monte_carlo_simulation(
    base_inputs: Dict,
    variable_distributions: Dict[str, Tuple[str, tuple]],
    metric_func: Callable,
    n_simulations: int = 10000,
    random_seed: int = 42
) -> Tuple[np.ndarray, Dict]:
    """
    Run Monte Carlo simulation for risk analysis
    
    Args:
        base_inputs: Dictionary of base case inputs
        variable_distributions: Dict mapping variable names to (distribution_type, parameters)
            Example: {'rent_growth': ('normal', (0.03, 0.01)),
                     'exit_cap': ('uniform', (0.045, 0.065))}
        metric_func: Function that calculates metric from inputs
        n_simulations: Number of Monte Carlo iterations
        random_seed: Random seed for reproducibility
    
    Returns:
        Tuple of (array of metric values, dict of statistics)
    """
    np.random.seed(random_seed)
    results = []
    
    for _ in range(n_simulations):
        inputs = base_inputs.copy()
        
        # Sample from distributions
        for var_name, (dist_type, params) in variable_distributions.items():
            if dist_type == 'normal':
                inputs[var_name] = np.random.normal(*params)
            elif dist_type == 'uniform':
                inputs[var_name] = np.random.uniform(*params)
            elif dist_type == 'triangular':
                inputs[var_name] = np.random.triangular(*params)
            elif dist_type == 'lognormal':
                inputs[var_name] = np.random.lognormal(*params)
        
        # Calculate metric
        metric_value = metric_func(inputs)
        results.append(metric_value)
    
    results = np.array(results)
    
    # Calculate statistics
    stats_dict = {
        'mean': np.mean(results),
        'median': np.median(results),
        'std': np.std(results),
        'min': np.min(results),
        'max': np.max(results),
        'p10': np.percentile(results, 10),
        'p25': np.percentile(results, 25),
        'p75': np.percentile(results, 75),
        'p90': np.percentile(results, 90),
        'prob_negative': np.mean(results < 0),
        'prob_below_hurdle': lambda hurdle: np.mean(results < hurdle)
    }
    
    return results, stats_dict


def stress_test(
    base_inputs: Dict,
    stress_scenarios: Dict[str, Dict],
    metric_func: Callable
) -> pd.DataFrame:
    """
    Perform stress testing with extreme scenarios
    
    Args:
        base_inputs: Base case input parameters
        stress_scenarios: Dict of stress scenario names to parameter changes
            Example: {'Recession': {'rent_growth': -0.05, 'vacancy_rate': 0.15}}
        metric_func: Function to calculate metric
    
    Returns:
        DataFrame with stress test results
    """
    results = {'Base Case': metric_func(base_inputs)}
    
    for scenario_name, changes in stress_scenarios.items():
        stress_inputs = base_inputs.copy()
        stress_inputs.update(changes)
        results[scenario_name] = metric_func(stress_inputs)
    
    df = pd.DataFrame.from_dict(results, orient='index', columns=['Metric'])
    df.index.name = 'Scenario'
    
    # Add % change from base
    base_value = df.loc['Base Case', 'Metric']
    df['Change from Base'] = (df['Metric'] - base_value) / base_value * 100
    
    return df


def breakeven_analysis(
    base_inputs: Dict,
    variable_name: str,
    target_metric_value: float,
    metric_func: Callable,
    search_range: Tuple[float, float] = None,
    tolerance: float = 0.0001
) -> float:
    """
    Find the breakeven value of a variable for a target metric
    
    Args:
        base_inputs: Base case inputs
        variable_name: Name of variable to solve for
        target_metric_value: Target value for the metric
        metric_func: Function that calculates metric
        search_range: (min, max) range to search
        tolerance: Convergence tolerance
    
    Returns:
        Breakeven value of the variable
    """
    def objective(x):
        inputs = base_inputs.copy()
        inputs[variable_name] = x
        return metric_func(inputs) - target_metric_value
    
    if search_range is None:
        search_range = (0, 1)
    
    from scipy.optimize import brentq
    
    try:
        breakeven_value = brentq(objective, *search_range, xtol=tolerance)
        return breakeven_value
    except ValueError:
        return None


def tornado_chart_data(
    base_inputs: Dict,
    variables_to_test: Dict[str, Tuple[float, float]],
    metric_func: Callable
) -> pd.DataFrame:
    """
    Generate data for tornado chart (sensitivity ranking)
    
    Args:
        base_inputs: Base case inputs
        variables_to_test: Dict of variable names to (low_value, high_value) tuples
        metric_func: Function to calculate metric
    
    Returns:
        DataFrame sorted by impact magnitude
    """
    base_metric = metric_func(base_inputs)
    impacts = []
    
    for var_name, (low_val, high_val) in variables_to_test.items():
        # Calculate low scenario
        low_inputs = base_inputs.copy()
        low_inputs[var_name] = low_val
        low_metric = metric_func(low_inputs)
        
        # Calculate high scenario
        high_inputs = base_inputs.copy()
        high_inputs[var_name] = high_val
        high_metric = metric_func(high_inputs)
        
        # Calculate impacts
        low_impact = low_metric - base_metric
        high_impact = high_metric - base_metric
        total_swing = abs(high_impact - low_impact)
        
        impacts.append({
            'Variable': var_name,
            'Base': base_metric,
            'Low Value': low_val,
            'Low Metric': low_metric,
            'Low Impact': low_impact,
            'High Value': high_val,
            'High Metric': high_metric,
            'High Impact': high_impact,
            'Total Swing': total_swing
        })
    
    df = pd.DataFrame(impacts)
    df = df.sort_values('Total Swing', ascending=False)
    
    return df


# Example usage
if __name__ == "__main__":
    print("=== CRE Sensitivity Analysis Example ===\n")
    
    # Define a simple metric function for demonstration
    def simple_irr_calc(inputs):
        """Simplified IRR calculation for demonstration"""
        noi = inputs['year_1_noi']
        growth = inputs['rent_growth']
        exit_cap = inputs['exit_cap']
        hold = inputs['hold_period']
        
        # Project NOI
        terminal_noi = noi * ((1 + growth) ** hold)
        exit_value = terminal_noi / exit_cap
        
        # Simplified IRR estimate
        purchase_price = inputs['purchase_price']
        total_return = (exit_value - purchase_price) / purchase_price
        annualized_return = (1 + total_return) ** (1/hold) - 1
        
        return annualized_return
    
    # Base case inputs
    base_case = {
        'purchase_price': 10_000_000,
        'year_1_noi': 550_000,
        'rent_growth': 0.03,
        'exit_cap': 0.055,
        'hold_period': 7
    }
    
    # Two-way sensitivity: IRR vs Exit Cap and Rent Growth
    print("1. Two-Way Sensitivity Table (IRR vs Exit Cap & Rent Growth)")
    rent_growth_range = [0.01, 0.02, 0.03, 0.04, 0.05]
    exit_cap_range = [0.045, 0.050, 0.055, 0.060, 0.065]
    
    sensitivity_table = two_way_sensitivity_table(
        base_case,
        'rent_growth',
        rent_growth_range,
        'exit_cap',
        exit_cap_range,
        simple_irr_calc
    )
    print(sensitivity_table)
    
    # Scenario analysis
    print("\n\n2. Scenario Analysis")
    scenarios = {
        'Downside': {**base_case, 'rent_growth': 0.01, 'exit_cap': 0.065},
        'Base': base_case,
        'Upside': {**base_case, 'rent_growth': 0.05, 'exit_cap': 0.045}
    }
    scenario_results = scenario_analysis(scenarios, simple_irr_calc, 'IRR')
    print(scenario_results * 100)  # Convert to percentage
    
    # Tornado chart
    print("\n\n3. Tornado Chart Data (Impact Ranking)")
    variables = {
        'rent_growth': (0.01, 0.05),
        'exit_cap': (0.045, 0.065),
        'year_1_noi': (500_000, 600_000)
    }
    tornado_data = tornado_chart_data(base_case, variables, simple_irr_calc)
    print(tornado_data[['Variable', 'Total Swing']].to_string(index=False))
