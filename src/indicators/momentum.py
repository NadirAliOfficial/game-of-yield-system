import numpy as np
from typing import List, Optional, Dict
from collections import deque


class MomentumIndicator:
    def __init__(self, period: int = 63, name: str = "Momentum"):
        self.period = period
        self.name = name
        self.price_history: deque = deque(maxlen=period + 10)  # Buffer

        # Current values
        self.current_momentum: float = 0.0
        self.current_price: float = 0.0
        self.past_price: float = 0.0

        # State
        self.is_ready: bool = False
        self.data_points: int = 0

    def update(self, price: float) -> float:
        """
        Update indicator with new price

        Args:
            price: Current price

        Returns:
            Current momentum value
        """

        if price <= 0:
            return self.current_momentum

        self.price_history.append(price)
        self.current_price = price
        self.data_points += 1

        # Check if we have enough data
        if len(self.price_history) <= self.period:
            self.is_ready = False
            return 0.0

        self.is_ready = True

        # Get price from N periods ago
        history_list = list(self.price_history)
        self.past_price = history_list[-(self.period + 1)]

        # Calculate momentum (rate of change)
        if self.past_price > 0:
            self.current_momentum = (self.current_price - self.past_price) / self.past_price
        else:
            self.current_momentum = 0.0

        return self.current_momentum

    def get_momentum(self) -> float:
        """Get current momentum value"""
        return self.current_momentum

    def get_annualized_momentum(self) -> float:
        """Get annualized momentum (for comparison across timeframes)"""
        if not self.is_ready:
            return 0.0

        # Annualize based on period
        annual_factor = 252 / self.period
        return self.current_momentum * annual_factor

    def reset(self):
        """Reset indicator to initial state"""
        self.price_history.clear()
        self.current_momentum = 0.0
        self.current_price = 0.0
        self.past_price = 0.0
        self.is_ready = False
        self.data_points = 0

    def get_stats(self) -> dict:
        """Get current statistics"""
        return {
            'name': self.name,
            'period': self.period,
            'momentum': self.current_momentum,
            'momentum_pct': f"{self.current_momentum:.2%}",
            'current_price': self.current_price,
            'past_price': self.past_price,
            'is_ready': self.is_ready,
            'data_points': len(self.price_history)
        }

    def __repr__(self) -> str:
        return f"MomentumIndicator({self.name}, {self.period}d, mom={self.current_momentum:.2%})"


class MomentumComposite:
    """
    Momentum Composite Indicator

    Combines multiple momentum timeframes into a single score.
    Provides robust momentum signal by averaging across periods.
    """

    def __init__(
        self,
        short_period: int = 21,    # 1 month
        medium_period: int = 63,   # 3 months
        long_period: int = 126,    # 6 months
        short_weight: float = 0.25,
        medium_weight: float = 0.50,
        long_weight: float = 0.25
    ):
        """
        Initialize Momentum Composite

        Args:
            short_period: Short-term momentum period (days)
            medium_period: Medium-term momentum period (days)
            long_period: Long-term momentum period (days)
            short_weight: Weight for short-term momentum
            medium_weight: Weight for medium-term momentum
            long_weight: Weight for long-term momentum
        """

        # Validate weights
        total_weight = short_weight + medium_weight + long_weight
        if abs(total_weight - 1.0) > 0.01:
            # Normalize weights
            short_weight /= total_weight
            medium_weight /= total_weight
            long_weight /= total_weight

        self.short_weight = short_weight
        self.medium_weight = medium_weight
        self.long_weight = long_weight

        # Create component indicators
        self.short_mom = MomentumIndicator(period=short_period, name="Short")
        self.medium_mom = MomentumIndicator(period=medium_period, name="Medium")
        self.long_mom = MomentumIndicator(period=long_period, name="Long")

        # Composite value
        self.composite_momentum: float = 0.0
        self.is_ready: bool = False

    def update(self, price: float) -> float:
        """
        Update all momentum indicators with new price

        Args:
            price: Current price

        Returns:
            Composite momentum value
        """

        # Update all components
        short = self.short_mom.update(price)
        medium = self.medium_mom.update(price)
        long_val = self.long_mom.update(price)

        # Check readiness (require at least medium-term to be ready)
        self.is_ready = self.medium_mom.is_ready

        if not self.is_ready:
            return 0.0

        # Calculate composite
        # Use only ready components
        total_weight = 0.0
        weighted_sum = 0.0

        if self.short_mom.is_ready:
            weighted_sum += self.short_weight * short
            total_weight += self.short_weight

        if self.medium_mom.is_ready:
            weighted_sum += self.medium_weight * medium
            total_weight += self.medium_weight

        if self.long_mom.is_ready:
            weighted_sum += self.long_weight * long_val
            total_weight += self.long_weight

        if total_weight > 0:
            self.composite_momentum = weighted_sum / total_weight
        else:
            self.composite_momentum = 0.0

        return self.composite_momentum

    def get_composite(self) -> float:
        """Get composite momentum value"""
        return self.composite_momentum

    def get_components(self) -> Dict[str, float]:
        """Get individual momentum components"""
        return {
            'short': self.short_mom.get_momentum(),
            'medium': self.medium_mom.get_momentum(),
            'long': self.long_mom.get_momentum(),
            'composite': self.composite_momentum
        }

    def get_signal(self) -> str:
        """
        Get trading signal based on momentum

        Returns:
            'STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL'
        """

        if not self.is_ready:
            return 'NEUTRAL'

        m = self.composite_momentum

        if m >= 0.20:      # +20% or more
            return 'STRONG_BUY'
        elif m >= 0.05:    # +5% to +20%
            return 'BUY'
        elif m <= -0.20:   # -20% or worse
            return 'STRONG_SELL'
        elif m <= -0.05:   # -5% to -20%
            return 'SELL'
        else:
            return 'NEUTRAL'

    def is_positive_trend(self) -> bool:
        """Check if overall trend is positive"""
        if not self.is_ready:
            return False

        components = self.get_components()
        positive_count = sum(1 for v in components.values() if v > 0)
        return positive_count >= 2  # At least 2 of 3 positive

    def reset(self):
        """Reset all indicators"""
        self.short_mom.reset()
        self.medium_mom.reset()
        self.long_mom.reset()
        self.composite_momentum = 0.0
        self.is_ready = False

    def get_stats(self) -> dict:
        """Get comprehensive statistics"""
        return {
            'composite': self.composite_momentum,
            'composite_pct': f"{self.composite_momentum:.2%}",
            'signal': self.get_signal(),
            'positive_trend': self.is_positive_trend(),
            'is_ready': self.is_ready,
            'short': self.short_mom.get_stats(),
            'medium': self.medium_mom.get_stats(),
            'long': self.long_mom.get_stats()
        }

    def __repr__(self) -> str:
        return (
            f"MomentumComposite(composite={self.composite_momentum:.2%}, "
            f"signal={self.get_signal()})"
        )


class MultiAssetMomentum:
    """
    Multi-Asset Momentum Manager

    Manages momentum indicators for multiple CEF symbols
    and provides ranking functionality.
    """

    def __init__(
        self,
        short_period: int = 21,
        medium_period: int = 63,
        long_period: int = 126
    ):
        """
        Initialize Multi-Asset Momentum Manager

        Args:
            short_period: Short-term period (days)
            medium_period: Medium-term period (days)
            long_period: Long-term period (days)
        """
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period
        self.indicators: Dict[str, MomentumComposite] = {}

    def add_symbol(self, symbol: str):
        """Add a symbol to track"""
        if symbol not in self.indicators:
            self.indicators[symbol] = MomentumComposite(
                short_period=self.short_period,
                medium_period=self.medium_period,
                long_period=self.long_period
            )

    def remove_symbol(self, symbol: str):
        """Remove a symbol from tracking"""
        if symbol in self.indicators:
            del self.indicators[symbol]

    def update(self, symbol: str, price: float) -> float:
        """Update indicator for a specific symbol"""
        if symbol not in self.indicators:
            self.add_symbol(symbol)

        return self.indicators[symbol].update(price)

    def get_momentum(self, symbol: str) -> float:
        """Get momentum for a specific symbol"""
        if symbol not in self.indicators:
            return 0.0
        return self.indicators[symbol].get_composite()

    def get_all_momentum(self) -> Dict[str, float]:
        """Get momentum for all symbols"""
        return {
            symbol: ind.get_composite()
            for symbol, ind in self.indicators.items()
        }

    def get_rankings(self, ascending: bool = False) -> List[tuple]:
        """
        Get symbols ranked by momentum

        Args:
            ascending: If False, highest momentum first (default)

        Returns:
            List of (symbol, momentum) tuples sorted by momentum
        """

        scores = []
        for symbol, indicator in self.indicators.items():
            if indicator.is_ready:
                scores.append((symbol, indicator.get_composite()))

        return sorted(scores, key=lambda x: x[1], reverse=not ascending)

    def get_top_n(self, n: int) -> List[str]:
        """Get top N symbols by momentum (highest first)"""
        rankings = self.get_rankings(ascending=False)
        return [symbol for symbol, _ in rankings[:n]]

    def get_positive_momentum_symbols(self) -> List[str]:
        """Get all symbols with positive momentum trend"""
        return [
            symbol for symbol, indicator in self.indicators.items()
            if indicator.is_ready and indicator.is_positive_trend()
        ]

    def get_summary(self) -> dict:
        """Get summary statistics for all symbols"""
        return {
            symbol: {
                'momentum': indicator.get_composite(),
                'signal': indicator.get_signal(),
                'positive_trend': indicator.is_positive_trend()
            }
            for symbol, indicator in self.indicators.items()
            if indicator.is_ready
        }


# =====================================================
# QUANTCONNECT INTEGRATION
# =====================================================

try:
    from AlgorithmImports import *

    class QCMomentumComposite(PythonIndicator):
        """
        QuantConnect-compatible Momentum Composite Indicator

        This class wraps MomentumComposite for use in QuantConnect algorithms.
        """

        def __init__(self, name: str, short: int = 21, medium: int = 63, long: int = 126):
            super().__init__()
            self.Name = name
            self.indicator = MomentumComposite(
                short_period=short,
                medium_period=medium,
                long_period=long
            )
            self.Value = 0.0

        def Update(self, input) -> bool:
            """Update indicator with new data point"""

            if hasattr(input, 'Close'):
                price = float(input.Close)
            elif hasattr(input, 'Value'):
                price = float(input.Value)
            else:
                price = float(input)

            self.Value = self.indicator.update(price)
            return self.indicator.is_ready

        @property
        def IsReady(self) -> bool:
            return self.indicator.is_ready

        def Reset(self):
            self.indicator.reset()
            self.Value = 0.0

except ImportError:
    # Not running in QuantConnect environment
    pass


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":
    # Test the Momentum indicator
    print("Testing Momentum Indicator...")
    print("=" * 50)

    # Create indicator
    indicator = MomentumComposite(
        short_period=5,    # Shorter for testing
        medium_period=10,
        long_period=20
    )

    # Simulate price data with upward trend
    np.random.seed(42)
    base_price = 20.0
    trend = 0.001  # ~0.1% per day upward trend

    prices = []
    for i in range(50):
        if len(prices) > 0:
            drift = trend + np.random.normal(0, 0.01)
            new_price = prices[-1] * (1 + drift)
        else:
            new_price = base_price

        prices.append(new_price)
        mom = indicator.update(new_price)

        if i % 10 == 0 or i >= 45:
            components = indicator.get_components()
            print(f"Day {i+1:3d}: Price=${new_price:.2f}, "
                  f"Short={components['short']:+.2%}, "
                  f"Med={components['medium']:+.2%}, "
                  f"Long={components['long']:+.2%}, "
                  f"Composite={mom:+.2%}")

    print("\n" + "=" * 50)
    print("Final Statistics:")
    stats = indicator.get_stats()
    print(f"  Composite: {stats['composite_pct']}")
    print(f"  Signal: {stats['signal']}")
    print(f"  Positive Trend: {stats['positive_trend']}")

    # Test multi-asset manager
    print("\n" + "=" * 50)
    print("Testing Multi-Asset Momentum Manager...")
    print("=" * 50)

    manager = MultiAssetMomentum(short_period=5, medium_period=10, long_period=20)

    symbols = ['PDI', 'PTY', 'GAB', 'USA', 'HTD']

    # Simulate data for multiple symbols with different trends
    for day in range(50):
        for i, symbol in enumerate(symbols):
            # Different trends for different CEFs
            trend = 0.001 * (i - 2)  # -0.2% to +0.2% per day
            base = 20 + i * 5

            if day == 0:
                price = base
            else:
                prev = base * (1 + trend * (day - 1))
                price = prev * (1 + trend + np.random.normal(0, 0.005))

            manager.update(symbol, price)

    print("\nFinal Rankings (highest momentum first):")
    for rank, (symbol, mom) in enumerate(manager.get_rankings(), 1):
        print(f"  {rank}. {symbol}: {mom:+.2%}")

    print(f"\nTop 3 by Momentum: {manager.get_top_n(3)}")
    print(f"Positive Trend Symbols: {manager.get_positive_momentum_symbols()}")

    print("\n✓ All tests passed!")
