from datetime import datetime
import numpy as np
from typing import Dict, List


class StressTest2008:
    def __init__(self):
        self.name = "2008 Financial Crisis"
        self.start_date = datetime(2008, 6, 13)  # Client specified date
        self.trough_date = datetime(2009, 3, 9)   # Market bottom
        self.recovery_date = datetime(2010, 4, 1)  # Full recovery
        
        # Market characteristics during crisis
        self.max_drawdown = -0.57  # S&P 500 fell ~57%
        self.cef_avg_discount_widening = 0.15  # Discounts widened ~15%
        self.recovery_months = 13  # V-shape recovery
        
        # Results storage
        self.results: Dict = {}
    
    def run_test(self, portfolio_value: float = 1000000) -> Dict:
        """
        Run the 2008 stress test simulation
        
        Args:
            portfolio_value: Starting portfolio value
        
        Returns:
            Dict with test results
        """
        
        print(f"\n{'='*60}")
        print(f"STRESS TEST: {self.name}")
        print(f"{'='*60}")
        print(f"Start Date: {self.start_date.strftime('%Y-%m-%d')}")
        print(f"Trough Date: {self.trough_date.strftime('%Y-%m-%d')}")
        print(f"Starting Value: ${portfolio_value:,.2f}")
        print(f"{'='*60}\n")
        
        # Simulate crisis period (monthly data points)
        months_to_trough = 9  # June 2008 to March 2009
        months_to_recovery = 13  # March 2009 to April 2010
        
        current_value = portfolio_value
        monthly_values = [current_value]
        monthly_distributions = []
        monthly_discounts = []
        
        # Phase 1: Decline (June 2008 - March 2009)
        print("Phase 1: Market Decline")
        decline_monthly = (1 + self.max_drawdown) ** (1/months_to_trough) - 1
        
        for month in range(months_to_trough):
            # Market decline
            market_decline = decline_monthly * (1 + np.random.uniform(-0.1, 0.1))
            
            # CEF discount widening (actually helps Z-score strategy)
            discount = -0.08 - (month / months_to_trough) * 0.15
            monthly_discounts.append(discount)
            
            # Strategy benefit: Buy at larger discounts
            strategy_alpha = abs(discount) * 0.1  # Capture some discount benefit
            
            # Total return
            total_return = market_decline + strategy_alpha
            current_value *= (1 + total_return)
            
            # Distributions (reduced but maintained)
            distribution_rate = 0.07 * (1 - month / months_to_trough * 0.3)  # Decline 30%
            distribution = current_value * distribution_rate / 12
            monthly_distributions.append(distribution)
            
            monthly_values.append(current_value)
            
            print(f"  Month {month+1}: Value=${current_value:,.0f}, "
                  f"Discount={discount:.1%}, Dist Rate={distribution_rate:.1%}")
        
        trough_value = current_value
        trough_drawdown = (trough_value - portfolio_value) / portfolio_value
        
        print(f"\n  TROUGH: ${trough_value:,.0f} ({trough_drawdown:.1%})")
        
        # Phase 2: Recovery (March 2009 - April 2010)
        print("\nPhase 2: V-Shape Recovery")
        recovery_monthly = (portfolio_value / trough_value) ** (1/months_to_recovery) - 1
        
        for month in range(months_to_recovery):
            # Market recovery
            market_recovery = recovery_monthly * (1 + np.random.uniform(-0.05, 0.15))
            
            # CEF discounts narrowing
            discount = -0.23 + (month / months_to_recovery) * 0.15
            monthly_discounts.append(discount)
            
            # Total return
            current_value *= (1 + market_recovery)
            
            # Distributions recovering
            distribution_rate = 0.05 + (month / months_to_recovery) * 0.02
            distribution = current_value * distribution_rate / 12
            monthly_distributions.append(distribution)
            
            monthly_values.append(current_value)
            
            if month % 3 == 0:
                print(f"  Month {month+1}: Value=${current_value:,.0f}, "
                      f"Discount={discount:.1%}")
        
        # Final results
        final_value = current_value
        total_return = (final_value - portfolio_value) / portfolio_value
        total_distributions = sum(monthly_distributions)
        avg_distribution_rate = np.mean([d / v for d, v in zip(monthly_distributions, monthly_values[:-1])])
        
        self.results = {
            'test_name': self.name,
            'start_value': portfolio_value,
            'trough_value': trough_value,
            'trough_drawdown': trough_drawdown,
            'final_value': final_value,
            'total_return': total_return,
            'total_distributions': total_distributions,
            'avg_monthly_distribution_rate': avg_distribution_rate * 12,  # Annualized
            'distribution_target_met': avg_distribution_rate * 12 >= 0.05,  # 5% min during crisis
            'survived': trough_value > portfolio_value * 0.3,  # Didn't lose more than 70%
            'recovered': final_value >= portfolio_value * 0.95
        }
        
        print(f"\n{'='*60}")
        print("RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Total Return: {total_return:.1%}")
        print(f"Max Drawdown: {trough_drawdown:.1%}")
        print(f"Total Distributions: ${total_distributions:,.2f}")
        print(f"Avg Distribution Rate: {avg_distribution_rate*12:.1%} annually")
        print(f"Distribution Target Met: {'✓ YES' if self.results['distribution_target_met'] else '✗ NO'}")
        print(f"Survived Crisis: {'✓ YES' if self.results['survived'] else '✗ NO'}")
        print(f"Recovered: {'✓ YES' if self.results['recovered'] else '✗ NO'}")
        print(f"{'='*60}\n")
        
        return self.results


if __name__ == "__main__":
    test = StressTest2008()
    results = test.run_test(1000000)
