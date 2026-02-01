#!/usr/bin/env python3
"""
Discounted Cash Flow (DCF) Analysis for Commercial Real Estate
Calculates NPV, IRR, and related metrics for CRE investments
"""

import numpy as np
import numpy_financial as npf
from typing import List, Dict, Tuple, Optional


def calculate_noi(
    effective_gross_income: float,
    operating_expenses: float
) -> float:
    """Calculate Net Operating Income (NOI)"""
    return effective_gross_income - operating_expenses


def calculate_dscr(
    noi: float,
    annual_debt_service: float
) -> float:
    """Calculate Debt Service Coverage Ratio (DSCR)"""
    if annual_debt_service == 0:
        return float('inf')
    return noi / annual_debt_service


def calculate_cash_flow_before_tax(
    noi: float,
    debt_service: float,
    capital_expenditures: float = 0
) -> float:
    """Calculate Cash Flow Before Tax"""
    return noi - debt_service - capital_expenditures


def calculate_reversion_value(
    final_noi: float,
    exit_cap_rate: float,
    selling_costs_pct: float = 0.03
) -> float:
    """
    Calculate property reversion value at exit
    
    Args:
        final_noi: Projected NOI in terminal year
        exit_cap_rate: Expected exit capitalization rate
        selling_costs_pct: Selling costs as % of sale price (default 3%)
    """
    gross_sale_price = final_noi / exit_cap_rate
    selling_costs = gross_sale_price * selling_costs_pct
    net_sale_proceeds = gross_sale_price - selling_costs
    return net_sale_proceeds


def calculate_levered_irr(
    initial_equity: float,
    annual_cash_flows: List[float],
    reversion_value: float,
    loan_balance_at_exit: float
) -> float:
    """
    Calculate levered (equity) IRR
    
    Args:
        initial_equity: Initial equity investment
        annual_cash_flows: List of annual cash flows to equity
        reversion_value: Net sale proceeds at exit
        loan_balance_at_exit: Outstanding loan balance at sale
    """
    equity_at_exit = reversion_value - loan_balance_at_exit
    cash_flows = [-initial_equity] + annual_cash_flows + [equity_at_exit]
    return npf.irr(cash_flows)


def calculate_unlevered_irr(
    initial_investment: float,
    annual_noi: List[float],
    reversion_value: float
) -> float:
    """
    Calculate unlevered IRR (property-level returns)
    
    Args:
        initial_investment: Total acquisition cost
        annual_noi: List of annual NOI projections
        reversion_value: Gross sale price at exit
    """
    cash_flows = [-initial_investment] + annual_noi + [reversion_value]
    return npf.irr(cash_flows)


def calculate_npv(
    cash_flows: List[float],
    discount_rate: float
) -> float:
    """Calculate Net Present Value"""
    return npf.npv(discount_rate, cash_flows)


def calculate_equity_multiple(
    total_cash_distributions: float,
    initial_equity: float
) -> float:
    """Calculate total equity multiple"""
    return total_cash_distributions / initial_equity


def calculate_cash_on_cash_return(
    annual_cash_flow: float,
    initial_equity: float
) -> float:
    """Calculate annual cash-on-cash return"""
    return annual_cash_flow / initial_equity


def calculate_cap_rate(
    noi: float,
    purchase_price: float
) -> float:
    """Calculate capitalization rate"""
    return noi / purchase_price


def amortization_schedule(
    loan_amount: float,
    annual_rate: float,
    term_years: int,
    io_period_years: int = 0
) -> List[Dict[str, float]]:
    """
    Generate loan amortization schedule
    
    Args:
        loan_amount: Initial loan amount
        annual_rate: Annual interest rate (e.g., 0.05 for 5%)
        term_years: Loan term in years
        io_period_years: Interest-only period in years
    """
    monthly_rate = annual_rate / 12
    total_months = term_years * 12
    io_months = io_period_years * 12
    
    schedule = []
    balance = loan_amount
    
    # Interest-only period
    if io_months > 0:
        monthly_payment = loan_amount * monthly_rate
        for month in range(1, io_months + 1):
            interest = balance * monthly_rate
            schedule.append({
                'month': month,
                'payment': monthly_payment,
                'principal': 0,
                'interest': interest,
                'balance': balance
            })
    
    # Amortizing period
    amortizing_months = total_months - io_months
    if amortizing_months > 0:
        monthly_payment = npf.pmt(monthly_rate, amortizing_months, -balance)
        
        for month in range(io_months + 1, total_months + 1):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            balance -= principal
            
            schedule.append({
                'month': month,
                'payment': monthly_payment,
                'principal': principal,
                'interest': interest,
                'balance': max(0, balance)
            })
    
    return schedule


def project_operating_pro_forma(
    year_1_gross_income: float,
    year_1_vacancy_rate: float,
    year_1_operating_expenses: float,
    rent_growth_rate: float,
    expense_growth_rate: float,
    projection_years: int = 10
) -> List[Dict[str, float]]:
    """
    Project operating pro forma for multiple years
    
    Returns list of dicts with keys: year, pgi, vacancy, egi, opex, noi
    """
    pro_forma = []
    
    for year in range(1, projection_years + 1):
        # Project income with growth
        pgi = year_1_gross_income * ((1 + rent_growth_rate) ** (year - 1))
        vacancy = pgi * (year_1_vacancy_rate + 0.002 * (year - 1))  # Slight vacancy increase over time
        egi = pgi - vacancy
        
        # Project expenses with growth
        opex = year_1_operating_expenses * ((1 + expense_growth_rate) ** (year - 1))
        
        # Calculate NOI
        noi = egi - opex
        
        pro_forma.append({
            'year': year,
            'pgi': pgi,
            'vacancy': vacancy,
            'egi': egi,
            'opex': opex,
            'noi': noi
        })
    
    return pro_forma


def sensitivity_analysis_2d(
    base_case_inputs: Dict,
    variable1: str,
    variable1_range: List[float],
    variable2: str,
    variable2_range: List[float],
    metric_function: callable
) -> np.ndarray:
    """
    Perform 2-dimensional sensitivity analysis
    
    Args:
        base_case_inputs: Dict of base case input parameters
        variable1: Name of first variable to vary
        variable1_range: List of values for first variable
        variable2: Name of second variable to vary
        variable2_range: List of values for second variable
        metric_function: Function that takes inputs dict and returns metric value
    
    Returns:
        2D numpy array of metric values
    """
    results = np.zeros((len(variable1_range), len(variable2_range)))
    
    for i, val1 in enumerate(variable1_range):
        for j, val2 in enumerate(variable2_range):
            inputs = base_case_inputs.copy()
            inputs[variable1] = val1
            inputs[variable2] = val2
            results[i, j] = metric_function(inputs)
    
    return results


# Example usage
if __name__ == "__main__":
    # Example acquisition analysis
    print("=== Commercial Real Estate DCF Example ===\n")
    
    # Property parameters
    purchase_price = 10_000_000
    acquisition_costs = 300_000
    total_investment = purchase_price + acquisition_costs
    
    # Year 1 operating assumptions
    year_1_gross_income = 850_000
    vacancy_rate = 0.05
    operating_expenses = 340_000
    
    # Growth assumptions
    rent_growth = 0.03
    expense_growth = 0.025
    
    # Financing
    loan_amount = 7_000_000
    equity = total_investment - loan_amount
    interest_rate = 0.055
    loan_term_years = 30
    io_period = 5
    
    # Exit assumptions
    hold_period = 7
    exit_cap_rate = 0.055
    
    # Generate pro forma
    pro_forma = project_operating_pro_forma(
        year_1_gross_income,
        vacancy_rate,
        operating_expenses,
        rent_growth,
        expense_growth,
        hold_period
    )
    
    print("Operating Pro Forma:")
    print(f"{'Year':<6}{'PGI':>12}{'Vacancy':>12}{'EGI':>12}{'OpEx':>12}{'NOI':>12}")
    print("-" * 66)
    for year in pro_forma:
        print(f"{year['year']:<6}{year['pgi']:>12,.0f}{year['vacancy']:>12,.0f}"
              f"{year['egi']:>12,.0f}{year['opex']:>12,.0f}{year['noi']:>12,.0f}")
    
    # Calculate debt service
    amort = amortization_schedule(loan_amount, interest_rate, loan_term_years, io_period)
    annual_debt_service = sum(amort[i]['payment'] for i in range(12))
    
    print(f"\n\nDebt Service:")
    print(f"Annual Debt Service: ${annual_debt_service:,.2f}")
    print(f"Year 1 DSCR: {calculate_dscr(pro_forma[0]['noi'], annual_debt_service):.2f}x")
    
    # Calculate cash flows
    annual_cash_flows = []
    for year in pro_forma[:-1]:  # Exclude terminal year
        cf = calculate_cash_flow_before_tax(year['noi'], annual_debt_service)
        annual_cash_flows.append(cf)
    
    # Calculate reversion
    final_noi = pro_forma[-1]['noi']
    reversion = calculate_reversion_value(final_noi, exit_cap_rate)
    
    # Get loan balance at exit
    loan_balance_at_exit = amort[hold_period * 12 - 1]['balance']
    
    # Calculate returns
    levered_irr = calculate_levered_irr(equity, annual_cash_flows, reversion, loan_balance_at_exit)
    
    total_distributions = sum(annual_cash_flows) + (reversion - loan_balance_at_exit)
    equity_multiple = calculate_equity_multiple(total_distributions, equity)
    
    year_1_coc = calculate_cash_on_cash_return(annual_cash_flows[0], equity)
    entry_cap = calculate_cap_rate(pro_forma[0]['noi'], purchase_price)
    
    print(f"\n\nInvestment Returns:")
    print(f"Levered IRR: {levered_irr * 100:.2f}%")
    print(f"Equity Multiple: {equity_multiple:.2f}x")
    print(f"Year 1 Cash-on-Cash: {year_1_coc * 100:.2f}%")
    print(f"Entry Cap Rate: {entry_cap * 100:.2f}%")
    print(f"Exit Cap Rate: {exit_cap_rate * 100:.2f}%")
    print(f"Exit NOI: ${final_noi:,.0f}")
    print(f"Gross Sale Price: ${reversion / 0.97:,.0f}")
    print(f"Net Sale Proceeds: ${reversion:,.0f}")
