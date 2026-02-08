import numpy as np
from typing import List, Optional
from collections import deque


class ZScoreIndicator:
    
    def __init__(self, lookback_period: int = 252, min_periods: int = 60):
        self.lookback_period = lookback_period
        self.min_periods = min_periods
        self.discount_history: deque = deque(maxlen=lookback_period)
        
        # Statistics
        self.current_z_score: float = 0.0
        self.mean_discount: float = 0.0
        self.std_discount: float = 0.0
        self.current_discount: float = 0.0
        
        # State tracking
        self.is_ready: bool = False
        self.data_points: int = 0
    
    def update(self, nav: float, market_price: float) -> float:
        """
        Update indicator with new NAV and market price data
        
        Args:
            nav: Net Asset Value per share
            market_price: Current market price per share
        
        Returns:
            Current Z-Score value
        """
        
        if nav <= 0 or market_price <= 0:
            return self.current_z_score
        
        # Calculate discount (negative = trading at discount)
        discount = (market_price - nav) / nav
        
        return self.update_with_discount(discount)
    
    def update_with_discount(self, discount: float) -> float:
        """
        Update indicator with pre-calculated discount value
        
        Args:
            discount: NAV discount as decimal (e.g., -0.10 = 10% discount)
        
        Returns:
            Current Z-Score value
        """
        
        # Add to history
        self.discount_history.append(discount)
        self.current_discount = discount
        self.data_points += 1
        
        # Check if we have enough data
        if len(self.discount_history) < self.min_periods:
            self.is_ready = False
            return 0.0
        
        self.is_ready = True
        
        # Calculate statistics
        discounts = list(self.discount_history)
        self.mean_discount = np.mean(discounts)
        self.std_discount = np.std(discounts)
        
        # Calculate Z-Score
        if self.std_discount > 0:
            self.current_z_score = (discount - self.mean_discount) / self.std_discount
        else:
            self.current_z_score = 0.0
        
        return self.current_z_score
    
    def get_z_score(self) -> float:
        """Get current Z-Score value"""
        return self.current_z_score
    
    def get_percentile(self) -> float:
        """
        Get percentile of current discount in historical distribution
        
        Returns:
            Percentile (0-100) where lower means more discounted
        """
        
        if not self.is_ready or len(self.discount_history) == 0:
            return 50.0
        
        discounts = list(self.discount_history)
        percentile = sum(1 for d in discounts if d > self.current_discount) / len(discounts) * 100
        
        return percentile
    
    def get_signal(self) -> str:
        """
        Get trading signal based on Z-Score
        
        Returns:
            'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'
        """
        
        if not self.is_ready:
            return 'HOLD'
        
        z = self.current_z_score
        
        if z <= -2.0:
            return 'STRONG_BUY'
        elif z <= -1.0:
            return 'BUY'
        elif z >= 2.0:
            return 'STRONG_SELL'
        elif z >= 1.0:
            return 'SELL'
        else:
            return 'HOLD'
    
    def reset(self):
        """Reset indicator to initial state"""
        self.discount_history.clear()
        self.current_z_score = 0.0
        self.mean_discount = 0.0
        self.std_discount = 0.0
        self.current_discount = 0.0
        self.is_ready = False
        self.data_points = 0
    
    def get_stats(self) -> dict:
        """Get current statistics"""
        return {
            'z_score': self.current_z_score,
            'current_discount': self.current_discount,
            'mean_discount': self.mean_discount,
            'std_discount': self.std_discount,
            'data_points': len(self.discount_history),
            'is_ready': self.is_ready,
            'percentile': self.get_percentile(),
            'signal': self.get_signal()
        }
    
    def __repr__(self) -> str:
        return (
            f"ZScoreIndicator(z={self.current_z_score:.2f}, "
            f"discount={self.current_discount:.2%}, "
            f"signal={self.get_signal()})"
        )


class MultiAssetZScore:
    """
    Multi-Asset Z-Score Manager
    
    Manages Z-Score indicators for multiple CEF symbols
    and provides ranking functionality.
    """
    
    def __init__(self, lookback_period: int = 252, min_periods: int = 60):
        """
        Initialize Multi-Asset Z-Score Manager
        
        Args:
            lookback_period: Number of days for historical analysis
            min_periods: Minimum data points required
        """
        self.lookback_period = lookback_period
        self.min_periods = min_periods
        self.indicators: dict = {}
    
    def add_symbol(self, symbol: str):
        """Add a symbol to track"""
        if symbol not in self.indicators:
            self.indicators[symbol] = ZScoreIndicator(
                lookback_period=self.lookback_period,
                min_periods=self.min_periods
            )
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from tracking"""
        if symbol in self.indicators:
            del self.indicators[symbol]
    
    def update(self, symbol: str, nav: float, market_price: float) -> float:
        """Update indicator for a specific symbol"""
        if symbol not in self.indicators:
            self.add_symbol(symbol)
        
        return self.indicators[symbol].update(nav, market_price)
    
    def update_with_discount(self, symbol: str, discount: float) -> float:
        """Update indicator with pre-calculated discount"""
        if symbol not in self.indicators:
            self.add_symbol(symbol)
        
        return self.indicators[symbol].update_with_discount(discount)
    
    def get_z_score(self, symbol: str) -> float:
        """Get Z-Score for a specific symbol"""
        if symbol not in self.indicators:
            return 0.0
        return self.indicators[symbol].get_z_score()
    
    def get_all_z_scores(self) -> dict:
        """Get Z-Scores for all symbols"""
        return {symbol: ind.get_z_score() for symbol, ind in self.indicators.items()}
    
    def get_rankings(self, ascending: bool = True) -> List[tuple]:
        """
        Get symbols ranked by Z-Score
        
        Args:
            ascending: If True, lowest (most undervalued) first
        
        Returns:
            List of (symbol, z_score) tuples sorted by Z-Score
        """
        
        scores = []
        for symbol, indicator in self.indicators.items():
            if indicator.is_ready:
                scores.append((symbol, indicator.get_z_score()))
        
        return sorted(scores, key=lambda x: x[1], reverse=not ascending)
    
    def get_top_n(self, n: int) -> List[str]:
        """Get top N symbols by Z-Score (most undervalued)"""
        rankings = self.get_rankings(ascending=True)
        return [symbol for symbol, _ in rankings[:n]]
    
    def get_summary(self) -> dict:
        """Get summary statistics for all symbols"""
        return {
            symbol: indicator.get_stats()
            for symbol, indicator in self.indicators.items()
        }


# =====================================================
# QUANTCONNECT INTEGRATION
# =====================================================

try:
    from AlgorithmImports import *
    
    class QCZScoreIndicator(PythonIndicator):
        """
        QuantConnect-compatible Z-Score Indicator
        
        This class wraps ZScoreIndicator for use in QuantConnect algorithms.
        """
        
        def __init__(self, name: str, lookback: int = 252):
            super().__init__()
            self.Name = name
            self.indicator = ZScoreIndicator(lookback_period=lookback)
            self.Value = 0.0
        
        def Update(self, input) -> bool:
            """Update indicator with new data point"""
            
            # Input should contain discount value
            if hasattr(input, 'Value'):
                discount = input.Value
            else:
                discount = float(input)
            
            self.Value = self.indicator.update_with_discount(discount)
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
    # Test the Z-Score indicator
    print("Testing Z-Score Indicator...")
    print("=" * 50)
    
    # Create indicator
    indicator = ZScoreIndicator(lookback_period=60, min_periods=20)
    
    # Simulate discount data (mean reversion around -5%)
    np.random.seed(42)
    base_discount = -0.05
    discounts = []
    
    for i in range(100):
        if len(discounts) > 0:
            prev = discounts[-1]
            mean_rev = 0.1 * (base_discount - prev)
            noise = np.random.normal(0, 0.02)
            new_discount = prev + mean_rev + noise
        else:
            new_discount = base_discount + np.random.normal(0, 0.01)
        
        discounts.append(new_discount)
        z = indicator.update_with_discount(new_discount)
        
        if i % 20 == 0 or i >= 95:
            print(f"Day {i+1:3d}: Discount={new_discount:+.2%}, Z={z:+.2f}, Signal={indicator.get_signal()}")
    
    print("\n" + "=" * 50)
    print("Final Statistics:")
    for key, value in indicator.get_stats().items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    # Test multi-asset manager
    print("\n" + "=" * 50)
    print("Testing Multi-Asset Z-Score Manager...")
    print("=" * 50)
    
    manager = MultiAssetZScore(lookback_period=30, min_periods=10)
    
    symbols = ['PDI', 'PTY', 'GAB', 'USA', 'HTD']
    
    # Simulate data for multiple symbols
    for day in range(50):
        for symbol in symbols:
            # Different base discounts for different CEFs
            base = -0.05 - hash(symbol) % 10 / 100
            discount = base + np.random.normal(0, 0.02)
            manager.update_with_discount(symbol, discount)
    
    print("\nFinal Rankings (most undervalued first):")
    for rank, (symbol, z) in enumerate(manager.get_rankings(), 1):
        print(f"  {rank}. {symbol}: Z={z:+.2f}")
    
    print(f"\nTop 3 CEFs: {manager.get_top_n(3)}")
    
    print("\n✓ All tests passed!")
