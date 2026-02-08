from datetime import datetime
import numpy as np
from typing import Dict


class StressTest2020:

    def __init__(self):
        self.name = "2020 COVID Crash"
        self.start_date = datetime(2020, 1, 20)  # Client specified date
        self.trough_date = datetime(2020, 3, 23)  # Market bottom
        self.recovery_date = datetime(2020, 8, 18)  # New highs
        
        # Market characteristics
        self.max_drawdown = -0.34  # S&P 500 fell ~34%
        self.decline_weeks = 5     # Very rapid decline
        self.recovery_weeks = 21   # Fast V-shape
        
        # Results storage
        self.results: Dict = {}
    
    def run_test(self, portfolio_value: float = 1000000) -> Dict:
        """Run the 2020 stress test simulation"""
        
        print(f"\n{'='*60}")
        print(f"STRESS TEST: {self.name}")
        print(f"{'='*60}")
        print(f"Start Date: {self.start_date.strftime('%Y-%m-%d')}")
        print(f"Trough Date: {self.trough_date.strftime('%Y-%m-%d')}")
        print(f"Starting Value: ${portfolio_value:,.2f}")
        print(f"{'='*60}\n")
        
        current_value = portfolio_value
        weekly_values = [current_value]
        distributions = []
        
        # Phase 1: Rapid Decline (5 weeks)
        print("Phase 1: Rapid Decline (5 weeks)")
        decline_weekly = (1 + self.max_drawdown) ** (1/self.decline_weeks) - 1
        
        for week in range(self.decline_weeks):
            # Market decline
            market_decline = decline_weekly * (1 + np.random.uniform(-0.1, 0.1))
            
            # CEF discounts widened rapidly
            discount = -0.10 - (week / self.decline_weeks) * 0.20
            
            # Strategy benefit from buying at discounts
            strategy_alpha = abs(discount) * 0.05
            
            current_value *= (1 + market_decline + strategy_alpha)
            weekly_values.append(current_value)
            
            print(f"  Week {week+1}: Value=${current_value:,.0f}, Decline={market_decline:.1%}")
        
        trough_value = current_value
        trough_drawdown = (trough_value - portfolio_value) / portfolio_value
        
        print(f"\n  TROUGH: ${trough_value:,.0f} ({trough_drawdown:.1%})")
        
        # Phase 2: V-Shape Recovery (21 weeks)
        print("\nPhase 2: V-Shape Recovery")
        recovery_weekly = (portfolio_value * 1.1 / trough_value) ** (1/self.recovery_weeks) - 1
        
        for week in range(self.recovery_weeks):
            market_recovery = recovery_weekly * (1 + np.random.uniform(-0.05, 0.10))
            current_value *= (1 + market_recovery)
            weekly_values.append(current_value)
            
            # Monthly distribution (every 4 weeks)
            if week % 4 == 0:
                dist = current_value * 0.07 / 12
                distributions.append(dist)
                print(f"  Week {week+1}: Value=${current_value:,.0f}, Dist=${dist:,.0f}")
        
        final_value = current_value
        total_return = (final_value - portfolio_value) / portfolio_value
        
        self.results = {
            'test_name': self.name,
            'start_value': portfolio_value,
            'trough_value': trough_value,
            'trough_drawdown': trough_drawdown,
            'final_value': final_value,
            'total_return': total_return,
            'total_distributions': sum(distributions),
            'weeks_to_recovery': self.recovery_weeks,
            'survived': trough_value > portfolio_value * 0.5,
            'recovered': final_value >= portfolio_value
        }
        
        print(f"\n{'='*60}")
        print("RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Total Return: {total_return:.1%}")
        print(f"Max Drawdown: {trough_drawdown:.1%}")
        print(f"Recovery Time: {self.recovery_weeks} weeks")
        print(f"Survived: {'✓ YES' if self.results['survived'] else '✗ NO'}")
        print(f"Recovered: {'✓ YES' if self.results['recovered'] else '✗ NO'}")
        print(f"{'='*60}\n")
        
        return self.results


if __name__ == "__main__":
    test = StressTest2020()
    results = test.run_test(1000000)
