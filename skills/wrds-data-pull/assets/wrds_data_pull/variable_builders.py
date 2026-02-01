"""
Financial Variable Construction Module
======================================

Standard financial ratios and metrics with academic citations.
"""

import pandas as pd
import numpy as np


class FinancialRatios:
    """
    Calculate standard financial ratios from Compustat variables.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset with Compustat variables

    Examples
    --------
    >>> ratios = FinancialRatios(df)
    >>> df['tobins_q'] = ratios.tobins_q()
    >>> df['leverage'] = ratios.leverage()
    """

    def __init__(self, df):
        self.df = df

    def tobins_q(self):
        """
        Tobin's Q = (Market Value of Assets) / (Book Value of Assets)

        Formula: (Market Equity + Total Debt - Cash) / Total Assets

        References:
        - Kaplan & Zingales (1997, QJE)
        - Chung & Pruitt (1994, FAJ) - simplified version
        """
        # Get appropriate variables (quarterly or annual)
        at = self._get_var(['atq', 'at'])  # Total assets
        csho = self._get_var(['cshoq', 'csho'])  # Shares outstanding
        prcc = self._get_var(['prccq', 'prcc_f'])  # Stock price
        dltt = self._get_var(['dlttq', 'dltt'])  # Long-term debt
        dlc = self._get_var(['dlcq', 'dlc'])  # Current debt
        che = self._get_var(['cheq', 'che'])  # Cash

        market_equity = abs(prcc) * csho  # abs() for negative prices (bid/ask avg)
        total_debt = dltt.fillna(0) + dlc.fillna(0)
        market_value_assets = market_equity + total_debt - che.fillna(0)

        return market_value_assets / at

    def leverage(self, method='book'):
        """
        Leverage = Total Debt / Assets (or Equity)

        Parameters
        ----------
        method : str
            'book' (debt/assets) or 'market' (debt/market_equity)

        References:
        - Rajan & Zingales (1995, JF)
        - Frank & Goyal (2009, JFE)
        """
        dltt = self._get_var(['dlttq', 'dltt'])
        dlc = self._get_var(['dlcq', 'dlc'])
        total_debt = dltt.fillna(0) + dlc.fillna(0)

        if method == 'book':
            at = self._get_var(['atq', 'at'])
            return total_debt / at
        elif method == 'market':
            csho = self._get_var(['cshoq', 'csho'])
            prcc = self._get_var(['prccq', 'prcc_f'])
            market_equity = abs(prcc) * csho
            return total_debt / market_equity
        else:
            raise ValueError("method must be 'book' or 'market'")

    def roa(self):
        """
        Return on Assets = Net Income / Total Assets

        References:
        - DuPont decomposition
        - Standard accounting metric
        """
        ni = self._get_var(['niq', 'ni'])
        at = self._get_var(['atq', 'at'])
        return ni / at

    def roe(self):
        """
        Return on Equity = Net Income / Book Equity

        References:
        - Standard accounting metric
        """
        ni = self._get_var(['niq', 'ni'])
        seq = self._get_var(['seqq', 'seq'])
        return ni / seq

    def book_to_market(self):
        """
        Book-to-Market Ratio = Book Equity / Market Equity

        References:
        - Fama & French (1992, JF)
        - Davis, Fama & French (2000, JF) - definition
        """
        seq = self._get_var(['seqq', 'seq'])
        csho = self._get_var(['cshoq', 'csho'])
        prcc = self._get_var(['prccq', 'prcc_f'])
        market_equity = abs(prcc) * csho
        return seq / market_equity

    def market_cap(self):
        """
        Market Capitalization = Price × Shares Outstanding

        Returns market cap in millions (if csho in millions, prcc in dollars)
        """
        csho = self._get_var(['cshoq', 'csho'])
        prcc = self._get_var(['prccq', 'prcc_f'])
        return abs(prcc) * csho

    def _get_var(self, var_names):
        """Helper to get variable with quarterly or annual naming."""
        for var in var_names:
            if var in self.df.columns:
                return self.df[var]
        raise KeyError(f"None of {var_names} found in DataFrame")


class REITMetrics:
    """
    REIT-specific financial metrics.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset with REIT variables
    """

    def __init__(self, df):
        self.df = df

    def ffo(self, method='nareit'):
        """
        Funds From Operations (FFO)

        Parameters
        ----------
        method : str
            'nareit' (standard definition) or 'simple' (NI + DA)

        References:
        - NAREIT definition: https://www.reit.com/data-research/reit-indexes
        - Geltner et al. (2007) - Commercial Real Estate Analysis
        """
        ni = self._get_var(['niq', 'ni'])
        dp = self._get_var(['dpq', 'dp'])  # Depreciation

        if method == 'simple':
            return ni + dp
        elif method == 'nareit':
            # NAREIT: FFO = NI + DA - Gains on Sales
            # Approximation (gains not always available)
            return ni + dp
        else:
            raise ValueError("method must be 'simple' or 'nareit'")

    def ffo_per_share(self):
        """FFO / Shares Outstanding"""
        ffo = self.ffo()
        csho = self._get_var(['cshoq', 'csho'])
        return ffo / csho

    def nav_discount(self):
        """
        NAV Discount/Premium = (Price - NAV per share) / NAV per share

        Approximation: Use book value as proxy for NAV
        """
        seq = self._get_var(['seqq', 'seq'])
        csho = self._get_var(['cshoq', 'csho'])
        prcc = self._get_var(['prccq', 'prcc_f'])

        nav_per_share = seq / csho
        price = abs(prcc)

        return (price - nav_per_share) / nav_per_share

    def _get_var(self, var_names):
        """Helper to get variable with quarterly or annual naming."""
        for var in var_names:
            if var in self.df.columns:
                return self.df[var]
        raise KeyError(f"None of {var_names} found in DataFrame")


def construct_financial_ratios(df, ratios=None):
    """
    Convenience function to add multiple financial ratios to DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset
    ratios : list of str, optional
        Ratios to calculate. If None, calculates all.
        Options: 'tobins_q', 'leverage', 'roa', 'roe', 'btm', 'market_cap'

    Returns
    -------
    pandas.DataFrame
        DataFrame with added ratio columns

    Examples
    --------
    >>> df = construct_financial_ratios(df, ratios=['leverage', 'roa'])
    """
    fin = FinancialRatios(df)
    df = df.copy()

    if ratios is None:
        ratios = ['tobins_q', 'leverage', 'roa', 'roe', 'btm', 'market_cap']

    for ratio in ratios:
        if ratio == 'tobins_q':
            df['tobins_q'] = fin.tobins_q()
        elif ratio == 'leverage':
            df['leverage'] = fin.leverage()
        elif ratio == 'roa':
            df['roa'] = fin.roa()
        elif ratio == 'roe':
            df['roe'] = fin.roe()
        elif ratio == 'btm':
            df['book_to_market'] = fin.book_to_market()
        elif ratio == 'market_cap':
            df['market_cap'] = fin.market_cap()
        else:
            raise ValueError(f"Unknown ratio: {ratio}")

    return df
