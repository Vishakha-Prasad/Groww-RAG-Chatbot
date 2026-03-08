from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, List


SchemeType = Literal["etf", "mutual_fund"]


@dataclass(frozen=True)
class SchemeConfig:
    """Configuration for a single scheme page on Groww."""

    id: str
    name: str
    url: str
    scheme_type: SchemeType


SCHEMES: List[SchemeConfig] = [
    SchemeConfig(
        id="hdfc_nifty_1d_rate_liquid_etf",
        name="HDFC Nifty 1D Rate Liquid ETF - Growth",
        url="https://groww.in/etfs/hdfc-nifty-d-rate-liquid-etf",
        scheme_type="etf",
    ),
    SchemeConfig(
        id="hdfc_small_cap_fund_direct_growth",
        name="HDFC Small Cap Fund Direct Growth",
        url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        scheme_type="mutual_fund",
    ),
    SchemeConfig(
        id="hdfc_nifty_50_index_fund_direct_growth",
        name="HDFC NIFTY 50 Index Fund Direct Growth",
        url="https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
        scheme_type="mutual_fund",
    ),
    SchemeConfig(
        id="hdfc_retirement_savings_fund_equity_plan_direct_growth",
        name="HDFC Retirement Savings Fund Equity Plan Direct Growth",
        url="https://groww.in/mutual-funds/hdfc-retirement-savings-fund-equity-plan-direct-growth",
        scheme_type="mutual_fund",
    ),
    SchemeConfig(
        id="hdfc_multi_asset_allocation_fund_direct_growth",
        name="HDFC Multi Asset Allocation Fund Direct Growth",
        url="https://groww.in/mutual-funds/hdfc-multi-asset-allocation-fund-direct-growth",
        scheme_type="mutual_fund",
    ),
]


__all__ = ["SchemeConfig", "SchemeType", "SCHEMES"]

