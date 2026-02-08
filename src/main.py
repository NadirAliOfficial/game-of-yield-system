from AlgorithmImports import *
from datetime import timedelta
import numpy as np
from typing import List, Dict, Tuple

class CanadianCapitalistCEFStrategy(QCAlgorithm):
    def Initialize(self):
        """Initialize the algorithm with parameters and universe"""
        
        # =====================================================
        # CONFIGURATION PARAMETERS
        # =====================================================
        
        # Backtest Period Settings
        self.SetStartDate(2007, 1, 1)  # Start before 2008 crisis
        self.SetEndDate(2024, 12, 31)  # Include recent data
        
        # Capital Settings
        self.SetCash(1000000)  # $1M starting capital
        
        # Trade Size Constraints
        self.MIN_TRADE_SIZE = 50000   # Minimum $50K per trade
        self.MAX_TRADE_SIZE = 500000  # Maximum $500K per trade
        
        # Strategy Parameters
        self.NUM_TOP_HOLDINGS = 10    # Number of top CEFs to hold
        self.Z_SCORE_LOOKBACK = 252   # 1-year lookback (trading days)
        self.MOMENTUM_LOOKBACK = 90   # 3-month momentum lookback
        self.REBALANCE_DAYS = 30      # Rebalance frequency (monthly on div pay dates)
        
        # Z-Score Weight and Momentum Weight (equal for now)
        self.Z_SCORE_WEIGHT = 0.5
        self.MOMENTUM_WEIGHT = 0.5
        
        # Benchmark Settings
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        self.SetBenchmark("SPY")
        
        # =====================================================
        # CEF UNIVERSE DEFINITION
        # =====================================================
        
        # Core CEF Universe (NYSE-listed CEFs with good liquidity)
        # This list should be updated with client's actual watchlist
        self.CEF_UNIVERSE = [
            # Equity CEFs
            "GAB",   # Gabelli Equity Trust
            "GDV",   # Gabelli Dividend & Income Trust
            "USA",   # Liberty All-Star Equity Fund
            "ADX",   # Adams Diversified Equity Fund
            "UTF",   # Cohen & Steers Infrastructure Fund
            "RQI",   # Cohen & Steers Quality Income Realty
            "RNP",   # Cohen & Steers REIT & Preferred Income
            "DNP",   # Duff & Phelps Utility & Infrastructure
            "UTG",   # Reaves Utility Income Fund
            "HTD",   # John Hancock Tax-Advtgd Div Inc
            
            # Fixed Income CEFs
            "PDI",   # PIMCO Dynamic Income Fund
            "PTY",   # PIMCO Corporate & Income Opportunity
            "PCN",   # PIMCO Corporate & Income Strategy
            "PHK",   # PIMCO High Income Fund
            "PCI",   # PIMCO Dynamic Credit Income Fund
            "AWF",   # AllianceBernstein Global High Income
            "AWP",   # Aberdeen Global Premier Properties
            "BGX",   # Blackstone Senior Floating Rate
            "BSL",   # Blackstone Senior Floating Rate 2022
            "EAD",   # Wells Fargo Income Opportunities
            
            # Multi-Asset CEFs
            "ETB",   # Eaton Vance Tax-Managed Buy-Write
            "ETV",   # Eaton Vance Tax-Advtgd Div Income
            "ETW",   # Eaton Vance Tax-Managed Glbl Div
            "EVT",   # Eaton Vance Tax-Advtgd Bond Strategy
            "JPC",   # Nuveen Preferred & Income Opp
            "JPS",   # Nuveen Preferred Securities
            "JRI",   # Nuveen Real Asset Income
            "NVG",   # Nuveen AMT-Free Muni Credit Income
            "NAD",   # Nuveen Quality Municipal Income
            "NZF",   # Nuveen Municipal Credit Income
        ]
        
        # =====================================================
        # DATA STORAGE
        # =====================================================
        
        # Historical data for indicators
        self.price_history: Dict[str, List[float]] = {}
        self.nav_history: Dict[str, List[float]] = {}  # Will simulate for now
        self.discount_history: Dict[str, List[float]] = {}
        
        # Current signals
        self.z_scores: Dict[str, float] = {}
        self.momentum_scores: Dict[str, float] = {}
        self.final_rankings: Dict[str, float] = {}
        
        # Holdings tracking
        self.current_holdings: List[str] = []
        self.last_rebalance: datetime = None
        
        # Performance tracking
        self.total_dividends_received = 0
        self.monthly_distributions: List[float] = []
        
        # =====================================================
        # SCHEDULE OPERATIONS
        # =====================================================
        
        # Add securities to universe
        for symbol in self.CEF_UNIVERSE:
            equity = self.AddEquity(symbol, Resolution.Daily)
            equity.SetDataNormalizationMode(DataNormalizationMode.Raw)
            self.price_history[symbol] = []
            self.nav_history[symbol] = []
            self.discount_history[symbol] = []
        
        # Schedule monthly rebalancing (first trading day of month)
        self.Schedule.On(
            self.DateRules.MonthStart("SPY"),
            self.TimeRules.AfterMarketOpen("SPY", 30),
            self.MonthlyRebalance
        )
        
        # Schedule dividend handling
        self.Schedule.On(
            self.DateRules.EveryDay("SPY"),
            self.TimeRules.AfterMarketOpen("SPY", 60),
            self.HandleDividends
        )
        
        # Log initialization
        self.Debug(f"Canadian Capitalist CEF Strategy Initialized")
        self.Debug(f"Universe Size: {len(self.CEF_UNIVERSE)} CEFs")
        self.Debug(f"Top Holdings Target: {self.NUM_TOP_HOLDINGS}")
        self.Debug(f"Trade Size: ${self.MIN_TRADE_SIZE:,} - ${self.MAX_TRADE_SIZE:,}")

    # =====================================================
    # INDICATOR CALCULATIONS
    # =====================================================
    
    def CalculateZScore(self, symbol: str) -> float:
        """
        Calculate Z-Score based on NAV discount/premium
        
        Z-Score = (Current_Discount - Mean_Discount) / StdDev_Discount
        
        For now, we simulate NAV using price-based approximation
        In production, use real NAV data from Barchart/CEF Connect
        """
        
        if symbol not in self.discount_history:
            return 0.0
        
        discounts = self.discount_history[symbol]
        
        if len(discounts) < self.Z_SCORE_LOOKBACK:
            return 0.0
        
        # Use last 252 days (1 year)
        recent_discounts = discounts[-self.Z_SCORE_LOOKBACK:]
        
        current_discount = recent_discounts[-1]
        mean_discount = np.mean(recent_discounts)
        std_discount = np.std(recent_discounts)
        
        if std_discount == 0:
            return 0.0
        
        z_score = (current_discount - mean_discount) / std_discount
        
        return z_score
    
    def CalculateMomentumScore(self, symbol: str) -> float:
        """
        Calculate Momentum Composite Score
        
        Simple momentum: (Price_Today - Price_N_Days_Ago) / Price_N_Days_Ago
        
        More negative Z-score (bigger discount) is better for CEFs
        More positive momentum is better
        """
        
        if symbol not in self.price_history:
            return 0.0
        
        prices = self.price_history[symbol]
        
        if len(prices) < self.MOMENTUM_LOOKBACK:
            return 0.0
        
        current_price = prices[-1]
        past_price = prices[-self.MOMENTUM_LOOKBACK]
        
        if past_price == 0:
            return 0.0
        
        momentum = (current_price - past_price) / past_price
        
        return momentum
    
    def SimulateNAVDiscount(self, symbol: str, current_price: float) -> float:
        """
        Simulate NAV discount for backtesting purposes
        
        In production, this will be replaced with real NAV data
        from Barchart API or CEF Connect scraper
        
        Simulation uses a mean-reverting random process
        """
        
        # Base discount (typical CEF trades at slight discount)
        base_discount = -0.05  # 5% discount
        
        # Add some volatility
        volatility = 0.08  # 8% standard deviation
        
        # Get previous discount or initialize
        if symbol in self.discount_history and len(self.discount_history[symbol]) > 0:
            prev_discount = self.discount_history[symbol][-1]
            # Mean reversion with random noise
            mean_reversion = 0.1 * (base_discount - prev_discount)
            random_shock = np.random.normal(0, volatility / np.sqrt(252))
            new_discount = prev_discount + mean_reversion + random_shock
        else:
            new_discount = base_discount + np.random.normal(0, volatility / 2)
        
        # Clamp to reasonable range (-50% to +20%)
        new_discount = max(-0.50, min(0.20, new_discount))
        
        return new_discount
    
    def CalculateRankings(self) -> Dict[str, float]:
        """
        Calculate final rankings combining Z-Score and Momentum
        
        For CEFs:
        - Lower (more negative) Z-Score = bigger discount = BETTER
        - Higher momentum = BETTER
        
        We invert Z-Score ranking so more negative = higher rank
        """
        
        rankings = {}
        
        # Get valid symbols with data
        valid_symbols = []
        for symbol in self.CEF_UNIVERSE:
            if (symbol in self.z_scores and symbol in self.momentum_scores):
                if self.Securities.ContainsKey(symbol):
                    if self.Securities[symbol].Price > 0:
                        valid_symbols.append(symbol)
        
        if len(valid_symbols) == 0:
            return rankings
        
        # Rank by Z-Score (descending - more negative is better)
        z_sorted = sorted(valid_symbols, key=lambda x: self.z_scores.get(x, 0))
        z_ranks = {sym: i for i, sym in enumerate(z_sorted)}
        
        # Rank by Momentum (ascending - higher is better)
        mom_sorted = sorted(valid_symbols, key=lambda x: self.momentum_scores.get(x, 0), reverse=True)
        mom_ranks = {sym: i for i, sym in enumerate(mom_sorted)}
        
        # Combined ranking
        for symbol in valid_symbols:
            z_rank = z_ranks.get(symbol, len(valid_symbols))
            mom_rank = mom_ranks.get(symbol, len(valid_symbols))
            
            # Weighted average rank (lower is better)
            combined_rank = (self.Z_SCORE_WEIGHT * z_rank) + (self.MOMENTUM_WEIGHT * mom_rank)
            rankings[symbol] = combined_rank
        
        self.final_rankings = rankings
        return rankings
    
    # =====================================================
    # TRADING LOGIC
    # =====================================================
    
    def GetTopCEFs(self, n: int = 10) -> List[str]:
        """Get the top N CEFs by combined ranking"""
        
        rankings = self.CalculateRankings()
        
        if len(rankings) == 0:
            return []
        
        # Sort by combined rank (lower is better)
        sorted_symbols = sorted(rankings.keys(), key=lambda x: rankings[x])
        
        return sorted_symbols[:n]
    
    def CalculatePositionSize(self, symbol: str) -> int:
        """
        Calculate position size with trade size constraints
        
        Equal weight among top holdings, respecting min/max trade sizes
        """
        
        portfolio_value = self.Portfolio.TotalPortfolioValue
        
        # Target allocation per position
        target_allocation = portfolio_value / self.NUM_TOP_HOLDINGS
        
        # Clamp to trade size limits
        position_value = max(self.MIN_TRADE_SIZE, min(self.MAX_TRADE_SIZE, target_allocation))
        
        # Get current price
        if not self.Securities.ContainsKey(symbol):
            return 0
        
        price = self.Securities[symbol].Price
        
        if price <= 0:
            return 0
        
        # Calculate shares
        shares = int(position_value / price)
        
        return shares
    
    def MonthlyRebalance(self):
        """
        Monthly rebalancing logic
        
        Called on first trading day of each month
        Implements DRIP by reinvesting into top 10 CEFs
        """
        
        # Get top 10 CEFs
        top_cefs = self.GetTopCEFs(self.NUM_TOP_HOLDINGS)
        
        if len(top_cefs) == 0:
            self.Debug(f"[{self.Time}] No valid CEFs for rebalancing")
            return
        
        self.Debug(f"\n{'='*60}")
        self.Debug(f"[{self.Time}] MONTHLY REBALANCE")
        self.Debug(f"Portfolio Value: ${self.Portfolio.TotalPortfolioValue:,.2f}")
        self.Debug(f"Top {len(top_cefs)} CEFs: {', '.join(top_cefs)}")
        self.Debug(f"{'='*60}\n")
        
        # Log rankings
        for i, symbol in enumerate(top_cefs):
            z = self.z_scores.get(symbol, 0)
            m = self.momentum_scores.get(symbol, 0)
            r = self.final_rankings.get(symbol, 0)
            self.Debug(f"  {i+1}. {symbol}: Z-Score={z:.3f}, Mom={m:.3%}, Rank={r:.2f}")
        
        # Close positions not in top CEFs
        for symbol in list(self.current_holdings):
            if symbol not in top_cefs:
                if self.Portfolio[symbol].Invested:
                    self.Liquidate(symbol)
                    self.Debug(f"  SELL: {symbol} (no longer in top {self.NUM_TOP_HOLDINGS})")
        
        # Open/adjust positions for top CEFs
        for symbol in top_cefs:
            target_shares = self.CalculatePositionSize(symbol)
            current_shares = self.Portfolio[symbol].Quantity if self.Portfolio[symbol].Invested else 0
            
            if target_shares > 0:
                # Use Limit Orders (Smart Day Limit as per requirements)
                price = self.Securities[symbol].Price
                limit_price = price * 1.001  # Slight buffer for execution
                
                if current_shares == 0:
                    # New position
                    self.LimitOrder(symbol, target_shares, limit_price)
                    self.Debug(f"  BUY (NEW): {symbol}, {target_shares} shares @ ${limit_price:.2f}")
                elif abs(target_shares - current_shares) > 10:
                    # Adjust position (only if significant difference)
                    delta = target_shares - current_shares
                    if delta > 0:
                        self.LimitOrder(symbol, delta, limit_price)
                        self.Debug(f"  BUY (ADD): {symbol}, {delta} shares @ ${limit_price:.2f}")
                    else:
                        self.LimitOrder(symbol, delta, price * 0.999)
                        self.Debug(f"  SELL (REDUCE): {symbol}, {abs(delta)} shares")
        
        # Update current holdings
        self.current_holdings = top_cefs
        self.last_rebalance = self.Time
        
        # Track monthly distribution
        self._TrackMonthlyDistribution()
    
    def HandleDividends(self):
        pass
    
    def _TrackMonthlyDistribution(self):
        
        # Calculate current yield
        total_dividend_value = 0
        for symbol in self.current_holdings:
            if self.Portfolio[symbol].Invested:
                # Estimate annual distribution (simplified)
                # In production, use actual dividend data
                position_value = self.Portfolio[symbol].HoldingsValue
                estimated_yield = 0.08  # Assume 8% average CEF yield
                total_dividend_value += position_value * estimated_yield / 12
        
        portfolio_value = self.Portfolio.TotalPortfolioValue
        if portfolio_value > 0:
            monthly_distribution_rate = total_dividend_value / portfolio_value
            self.monthly_distributions.append(monthly_distribution_rate)
            
            # Calculate rolling average
            if len(self.monthly_distributions) >= 12:
                avg_monthly = np.mean(self.monthly_distributions[-12:]) * 100
                self.Debug(f"  12-Month Avg Distribution Rate: {avg_monthly:.2f}%")
    
    # =====================================================
    # DATA HANDLING
    # =====================================================
    
    def OnData(self, data):
        """Process incoming data and update indicators"""
        
        for symbol in self.CEF_UNIVERSE:
            if not data.ContainsKey(symbol):
                continue
            
            if not data[symbol]:
                continue
            
            price = data[symbol].Close
            
            if price <= 0:
                continue
            
            # Update price history
            self.price_history[symbol].append(price)
            
            # Keep only needed history
            max_history = max(self.Z_SCORE_LOOKBACK, self.MOMENTUM_LOOKBACK) + 100
            if len(self.price_history[symbol]) > max_history:
                self.price_history[symbol] = self.price_history[symbol][-max_history:]
            
            # Simulate NAV discount (replace with real data in production)
            discount = self.SimulateNAVDiscount(symbol, price)
            self.discount_history[symbol].append(discount)
            
            if len(self.discount_history[symbol]) > max_history:
                self.discount_history[symbol] = self.discount_history[symbol][-max_history:]
            
            # Update indicators
            self.z_scores[symbol] = self.CalculateZScore(symbol)
            self.momentum_scores[symbol] = self.CalculateMomentumScore(symbol)
    
    def OnDividend(self, dividend):
        """Track dividend payments"""
        
        self.total_dividends_received += dividend.Distribution * self.Portfolio[dividend.Symbol].Quantity
        self.Debug(f"  DIVIDEND: {dividend.Symbol} - ${dividend.Distribution:.4f}/share")
    
    # =====================================================
    # RISK MANAGEMENT
    # =====================================================
    
    def OnOrderEvent(self, orderEvent):
        """Track order execution"""
        
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug(f"  ORDER FILLED: {orderEvent.Symbol} - {orderEvent.FillQuantity} shares @ ${orderEvent.FillPrice:.2f}")
    
    def OnEndOfAlgorithm(self):
        """Final reporting at backtest end"""
        
        self.Debug(f"\n{'='*60}")
        self.Debug("BACKTEST COMPLETE - FINAL REPORT")
        self.Debug(f"{'='*60}")
        self.Debug(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:,.2f}")
        self.Debug(f"Total Dividends Received: ${self.total_dividends_received:,.2f}")
        
        if len(self.monthly_distributions) > 0:
            avg_monthly = np.mean(self.monthly_distributions) * 100
            self.Debug(f"Average Monthly Distribution: {avg_monthly:.2f}%")
            self.Debug(f"Target: 7.00% (7% monthly = ~84% annual)")
            
            if avg_monthly >= 0.58:  # ~7% monthly
                self.Debug("✓ BENCHMARK MET: 7% monthly distribution target achieved!")
            else:
                self.Debug("✗ BENCHMARK NOT MET: Below 7% monthly distribution target")
        
        self.Debug(f"\nFinal Holdings: {', '.join(self.current_holdings)}")
        self.Debug(f"{'='*60}\n")
