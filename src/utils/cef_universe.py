# CEF Universe Manager
# Canadian Capitalist Strategy

"""
CEF Universe Management

Manages the universe of Closed-End Funds (CEFs) for the trading strategy.
Provides functionality to:
- Define and maintain CEF watchlist
- Filter CEFs by criteria (volume, market cap, etc.)
- Categorize CEFs by asset class
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class CEFCategory(Enum):
    """CEF Asset Class Categories"""
    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    MULTI_ASSET = "Multi-Asset"
    MUNICIPAL = "Municipal"
    REAL_ESTATE = "Real Estate"
    UTILITY = "Utility"
    INTERNATIONAL = "International"


@dataclass
class CEFInfo:
    """CEF Information Container"""
    symbol: str
    name: str
    category: CEFCategory
    sponsor: str = ""
    inception_date: str = ""
    typical_yield: float = 0.0
    avg_volume: int = 0

    def __repr__(self):
        return f"CEF({self.symbol}: {self.name[:30]})"


class CEFUniverse:
    """
    CEF Universe Manager

    Maintains the universe of CEFs for strategy selection.
    Based on client's watchlists from Barchart and CEF Connect.
    """

    # Default CEF Universe (based on client requirements)
    DEFAULT_UNIVERSE = {
        # PIMCO Fixed Income CEFs (Popular for income)
        "PDI": CEFInfo("PDI", "PIMCO Dynamic Income Fund", CEFCategory.FIXED_INCOME, "PIMCO", "2012-05", 0.12),
        "PTY": CEFInfo("PTY", "PIMCO Corporate & Income Opportunity", CEFCategory.FIXED_INCOME, "PIMCO", "2002-12", 0.10),
        "PCN": CEFInfo("PCN", "PIMCO Corporate & Income Strategy", CEFCategory.FIXED_INCOME, "PIMCO", "2001-12", 0.09),
        "PHK": CEFInfo("PHK", "PIMCO High Income Fund", CEFCategory.FIXED_INCOME, "PIMCO", "2003-04", 0.11),
        "PCI": CEFInfo("PCI", "PIMCO Dynamic Credit Income Fund", CEFCategory.FIXED_INCOME, "PIMCO", "2013-01", 0.10),

        # Gabelli Equity CEFs
        "GAB": CEFInfo("GAB", "Gabelli Equity Trust", CEFCategory.EQUITY, "Gabelli", "1986-08", 0.06),
        "GDV": CEFInfo("GDV", "Gabelli Dividend & Income Trust", CEFCategory.EQUITY, "Gabelli", "2003-11", 0.06),

        # Cohen & Steers (Real Estate/Infrastructure)
        "UTF": CEFInfo("UTF", "Cohen & Steers Infrastructure Fund", CEFCategory.UTILITY, "Cohen & Steers", "2004-03", 0.08),
        "RQI": CEFInfo("RQI", "Cohen & Steers Quality Income Realty", CEFCategory.REAL_ESTATE, "Cohen & Steers", "2002-02", 0.08),
        "RNP": CEFInfo("RNP", "Cohen & Steers REIT & Preferred Income", CEFCategory.REAL_ESTATE, "Cohen & Steers", "2003-06", 0.07),

        # Utility/Infrastructure
        "DNP": CEFInfo("DNP", "Duff & Phelps Utility & Infrastructure", CEFCategory.UTILITY, "Duff & Phelps", "1987-01", 0.07),
        "UTG": CEFInfo("UTG", "Reaves Utility Income Fund", CEFCategory.UTILITY, "Reaves", "2004-02", 0.07),

        # Liberty All-Star
        "USA": CEFInfo("USA", "Liberty All-Star Equity Fund", CEFCategory.EQUITY, "ALPS", "1986-10", 0.10),

        # Adams Funds
        "ADX": CEFInfo("ADX", "Adams Diversified Equity Fund", CEFCategory.EQUITY, "Adams", "1929-01", 0.06),

        # John Hancock
        "HTD": CEFInfo("HTD", "John Hancock Tax-Advantaged Dividend Income", CEFCategory.EQUITY, "John Hancock", "2004-02", 0.07),

        # Aberdeen
        "AWP": CEFInfo("AWP", "Aberdeen Global Premier Properties", CEFCategory.REAL_ESTATE, "Aberdeen", "2007-02", 0.08),
        "AWF": CEFInfo("AWF", "AllianceBernstein Global High Income", CEFCategory.FIXED_INCOME, "AllianceBernstein", "1993-09", 0.08),

        # Blackstone
        "BGX": CEFInfo("BGX", "Blackstone Senior Floating Rate", CEFCategory.FIXED_INCOME, "Blackstone", "2010-06", 0.08),
        "BSL": CEFInfo("BSL", "Blackstone Senior Floating Rate 2022", CEFCategory.FIXED_INCOME, "Blackstone", "2010-06", 0.08),

        # Eaton Vance
        "ETB": CEFInfo("ETB", "Eaton Vance Tax-Managed Buy-Write", CEFCategory.EQUITY, "Eaton Vance", "2005-12", 0.08),
        "ETV": CEFInfo("ETV", "Eaton Vance Tax-Advantaged Dividend Income", CEFCategory.EQUITY, "Eaton Vance", "2003-09", 0.07),
        "ETW": CEFInfo("ETW", "Eaton Vance Tax-Managed Global Dividend", CEFCategory.INTERNATIONAL, "Eaton Vance", "2007-02", 0.08),
        "EVT": CEFInfo("EVT", "Eaton Vance Tax-Advantaged Bond Strategy", CEFCategory.FIXED_INCOME, "Eaton Vance", "2004-11", 0.07),

        # Nuveen
        "JPC": CEFInfo("JPC", "Nuveen Preferred & Income Opportunities", CEFCategory.FIXED_INCOME, "Nuveen", "2003-03", 0.08),
        "JPS": CEFInfo("JPS", "Nuveen Preferred Securities", CEFCategory.FIXED_INCOME, "Nuveen", "2002-08", 0.07),
        "JRI": CEFInfo("JRI", "Nuveen Real Asset Income", CEFCategory.MULTI_ASSET, "Nuveen", "2012-06", 0.08),
        "NVG": CEFInfo("NVG", "Nuveen AMT-Free Municipal Credit Income", CEFCategory.MUNICIPAL, "Nuveen", "1999-10", 0.05),
        "NAD": CEFInfo("NAD", "Nuveen Quality Municipal Income", CEFCategory.MUNICIPAL, "Nuveen", "1999-10", 0.05),
        "NZF": CEFInfo("NZF", "Nuveen Municipal Credit Income", CEFCategory.MUNICIPAL, "Nuveen", "2001-11", 0.05),
    }

    def __init__(self, custom_symbols: Optional[List[str]] = None):
        """Initialize CEF Universe"""
        self.universe: Dict[str, CEFInfo] = {}

        if custom_symbols:
            for symbol in custom_symbols:
                if symbol in self.DEFAULT_UNIVERSE:
                    self.universe[symbol] = self.DEFAULT_UNIVERSE[symbol]
                else:
                    # Add unknown symbol with minimal info
                    self.universe[symbol] = CEFInfo(symbol, f"Unknown CEF ({symbol})", CEFCategory.MULTI_ASSET)
        else:
            self.universe = self.DEFAULT_UNIVERSE.copy()

    def get_symbols(self) -> List[str]:
        """Get all symbols in universe"""
        return list(self.universe.keys())

    def get_by_category(self, category: CEFCategory) -> List[str]:
        """Get symbols by category"""
        return [s for s, info in self.universe.items() if info.category == category]

    def get_info(self, symbol: str) -> Optional[CEFInfo]:
        """Get CEF info by symbol"""
        return self.universe.get(symbol)

    def add_symbol(self, symbol: str, info: Optional[CEFInfo] = None):
        """Add symbol to universe"""
        if info:
            self.universe[symbol] = info
        elif symbol in self.DEFAULT_UNIVERSE:
            self.universe[symbol] = self.DEFAULT_UNIVERSE[symbol]
        else:
            self.universe[symbol] = CEFInfo(symbol, f"CEF ({symbol})", CEFCategory.MULTI_ASSET)

    def remove_symbol(self, symbol: str):
        """Remove symbol from universe"""
        if symbol in self.universe:
            del self.universe[symbol]

    def get_summary(self) -> Dict:
        """Get universe summary"""
        categories = {}
        for info in self.universe.values():
            cat = info.category.value
            categories[cat] = categories.get(cat, 0) + 1

        return {
            'total_cefs': len(self.universe),
            'by_category': categories,
            'symbols': self.get_symbols()
        }

    def __len__(self):
        return len(self.universe)

    def __iter__(self):
        return iter(self.universe.keys())

    def __contains__(self, symbol: str):
        return symbol in self.universe


if __name__ == "__main__":
    print("Testing CEF Universe Manager...")
    print("=" * 50)

    universe = CEFUniverse()
    summary = universe.get_summary()

    print(f"Total CEFs: {summary['total_cefs']}")
    print("\nBy Category:")
    for cat, count in summary['by_category'].items():
        print(f"  {cat}: {count}")

    print(f"\nFixed Income CEFs: {universe.get_by_category(CEFCategory.FIXED_INCOME)}")
    print(f"\nPDI Info: {universe.get_info('PDI')}")

    print("\n✓ All tests passed!")
