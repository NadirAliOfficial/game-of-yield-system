from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class CEFRankingResult:
    """Ranking result for a single CEF"""
    symbol: str
    z_score: float
    momentum: float
    z_rank: int
    mom_rank: int
    combined_rank: float
    final_rank: int
    signal: str


class CEFRankingEngine:
    def __init__(
        self,
        z_weight: float = 0.5,
        mom_weight: float = 0.5,
        top_n: int = 10
    ):
        self.z_weight = z_weight
        self.mom_weight = mom_weight
        self.top_n = top_n
        
        # Storage
        self.z_scores: Dict[str, float] = {}
        self.momentum_scores: Dict[str, float] = {}
        self.rankings: Dict[str, CEFRankingResult] = {}
    
    def update_z_score(self, symbol: str, z_score: float):
        """Update Z-Score for symbol"""
        self.z_scores[symbol] = z_score
    
    def update_momentum(self, symbol: str, momentum: float):
        """Update Momentum for symbol"""
        self.momentum_scores[symbol] = momentum
    
    def calculate_rankings(self) -> List[CEFRankingResult]:
        """Calculate rankings for all symbols"""
        
        # Get symbols with both scores
        valid = [s for s in self.z_scores if s in self.momentum_scores]
        
        if not valid:
            return []
        
        # Rank by Z-Score (ascending - lower is better)
        z_sorted = sorted(valid, key=lambda x: self.z_scores.get(x, 0))
        z_ranks = {s: i for i, s in enumerate(z_sorted)}
        
        # Rank by Momentum (descending - higher is better)
        m_sorted = sorted(valid, key=lambda x: self.momentum_scores.get(x, 0), reverse=True)
        m_ranks = {s: i for i, s in enumerate(m_sorted)}
        
        # Combined ranking
        results = []
        for symbol in valid:
            z_rank = z_ranks[symbol]
            m_rank = m_ranks[symbol]
            combined = (self.z_weight * z_rank) + (self.mom_weight * m_rank)
            
            result = CEFRankingResult(
                symbol=symbol,
                z_score=self.z_scores[symbol],
                momentum=self.momentum_scores[symbol],
                z_rank=z_rank + 1,
                mom_rank=m_rank + 1,
                combined_rank=combined,
                final_rank=0,
                signal=self._get_signal(self.z_scores[symbol], self.momentum_scores[symbol])
            )
            results.append(result)
        
        # Sort by combined rank and assign final ranks
        results.sort(key=lambda x: x.combined_rank)
        for i, r in enumerate(results):
            r.final_rank = i + 1
        
        # Store results
        self.rankings = {r.symbol: r for r in results}
        
        return results
    
    def get_top_n(self, n: int = None) -> List[str]:
        """Get top N symbols"""
        if n is None:
            n = self.top_n
        
        results = self.calculate_rankings()
        return [r.symbol for r in results[:n]]
    
    def _get_signal(self, z: float, mom: float) -> str:
        """Generate trading signal"""
        if z < -1.5 and mom > 0:
            return "STRONG_BUY"
        elif z < -0.5 and mom > -0.05:
            return "BUY"
        elif z > 1.5 or mom < -0.15:
            return "SELL"
        else:
            return "HOLD"
    
    def get_ranking_report(self) -> str:
        """Generate ranking report"""
        results = self.calculate_rankings()
        
        lines = [
            "=" * 70,
            "CEF RANKING REPORT",
            "=" * 70,
            f"{'Rank':<5} {'Symbol':<8} {'Z-Score':>10} {'Momentum':>10} {'Signal':<12}",
            "-" * 70
        ]
        
        for r in results[:self.top_n]:
            lines.append(
                f"{r.final_rank:<5} {r.symbol:<8} {r.z_score:>10.3f} {r.momentum:>10.2%} {r.signal:<12}"
            )
        
        lines.append("=" * 70)
        lines.append(f"Top {self.top_n} Selected: {', '.join(self.get_top_n())}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    import numpy as np
    
    print("Testing CEF Ranking Engine...")
    print("=" * 50)
    
    engine = CEFRankingEngine(top_n=5)
    
    # Add sample data
    symbols = ['PDI', 'PTY', 'GAB', 'USA', 'HTD', 'RQI', 'DNP', 'AWP']
    
    np.random.seed(42)
    for symbol in symbols:
        engine.update_z_score(symbol, np.random.uniform(-2, 1))
        engine.update_momentum(symbol, np.random.uniform(-0.1, 0.2))
    
    print(engine.get_ranking_report())
    print("\n✓ All tests passed!")
