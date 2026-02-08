# Canadian Capitalist - CEF Dividend/DRIP Trading System

## Project Overview
This project aims to build an institutional-grade, automated trading and distribution ecosystem focused on NYSE-listed **Closed-End Funds (CEFs)**. The system utilizes a **Z-Score and Momentum-based** strategy to generate reliable income through disciplined dividend reinvestment (DRIP).

The mission is to achieve execution quality comparable to high-level manual trading, incorporating advanced order types and robust risk management. The product is branded as **"Pensionizer" (Pension-Advisor Ecosystem)**.

---

## Technical Strategy

### Core Assets
- NYSE-listed Closed-End Funds (CEFs)

### Primary Indicators
- **Z-Score (1-year lookback):** Based on NAV discount/premium
- **Momentum Composite:** Developer-optimized robust momentum indicators

### Selection Logic
- Scan CEF universe on dividend pay dates
- Rank by Z-Score + Momentum composite
- Reinvest dividends into the **Top 10** best-ranked CEFs (not 50)
- Equal weighting initially

### Trade Constraints
- **Minimum Trade Size:** $50,000 USD
- **Maximum Trade Size:** $500,000 USD
- DCA (Dollar-Cost Averaging) approach with low trade frequency

---

## Data Sources

### Primary Data Source: Barchart API
- **API Endpoint:** https://www.barchart.com/ondemand/api/getQuote
- Barchart account required for API access
- Watchlist sharing available via Barchart

### Secondary Data Source: CEF Connect
- **Website:** http://www.cefconnect.com/fund/AWP?view=fund
- Z-Score screen and watchlist data available
- **Note:** No official Nuveen/CEF Connect codebase exists
- Unofficial scraper available: `GitHub: daleholborow/parse.cefconnect`
  - Purpose: Quick-and-dirty scripts to pull closed-end fund data from CEF Connect's public endpoints
  - Saves parsed data to CSV
  - Author explicitly states no affiliation with CEF Connect

### Watchlists
- 2 separate watchlists maintained: one on Barchart, one on CEF Connect
- Z-score screen lives on CEF Connect

---

## Execution & Order Logic

### IBKR Integration
- **Order Types:**
  - Smart Day Limit Orders (preferred over market orders)
  - Level 2 / Iceberg orders for real money trades
  - Rules-based approximation acceptable if full L2 automation is difficult

### Execution Modes
- **Direct Users:** DRIP/DCA with fewer trades at same time
- **Institutional Licensees:** Must negotiate separately
- Consider ETF with embedded DRIP strategy as alternative

### Backtesting Parameters
- Ignore slippage and partial fills for initial backtesting
- Must pass stress tests:
  - **June 13, 2008** - Financial Crisis
  - **January 20, 2020** - COVID Crash
- Both had V-shape market price recovery
- Benchmark: ~7% monthly distribution sustained

---

## Distribution & Monetization Model

### Tier 1: QuantConnect Alpha Streams
- **Revenue Split:** 70% QC / 30% Quant
- Curated marketplace of vetted, live-tracked trading algorithms
- Institutional investors browse, evaluate, and license strategies
- Strategies run on QuantConnect's co-located, institutional-grade infrastructure
- Independent verification and clean performance data
- Funds can license alphas non-exclusively or exclusively depending on mandate and budget
- **Note:** Collective2 takes too much for white label and trading execution

### Tier 2: Native Platform (100% Ownership)
- **Watchlists without autotrade:** Signals-only subscription
- **Watchlists with autotrade:** IBKR direct execution
- Some through QC marketplace (70/30 split)
- Some 100% owned through native app with Stripe and PayPal

### Platform Options
- **AppMySite:** White-labeled agency platform
  - Custom screens/dashboards
  - Simple wrapper app vs full native app decision pending
- **Circle App:** Cheaper for similar platform functionality
- **WordPress Backend:** Using Divi Builder with:
  - AI-powered content creation tools
  - 2 animators and content manager
  - Email capture priority (not PayPal first)

### Subscription Pricing
- **45-Day Trial:** Test period for demo
- **After Trial:**
  - **$45 USD/month:** Without autotrade (signals only)
  - **$95 USD/month:** With autotrade enabled
- Waiting list for ETF based on same strategy
- Selling strategy and pre-launch BUZZ simultaneously

---

## User Segmentation

### User Types
1. **PRO Users:** Full access to autotrading and advanced features
2. **AM (Amateur) Users:**
   - Access to "Clinic" (educational content)
   - Access to "Practice Court" (paper trading simulation)

### Autotrade User Flow
- After 45-day trial, autotrading options:
  - Auto-disable until payment, OR
  - Continue with limited/capped size
- During trial: Paper only OR Live with capped size
- Kill switch for instant autotrade OFF

### Distribution Logic
- Alpha Streams and direct users may use same logic OR different parameters
- Licensing consideration: Whether redistribution of signals derived from Barchart/CEF Connect data is permitted
- Ops & control: Alerts reporting and who controls strategy changes once live

---

## Product Ecosystem Structure

### Pensionizer (Pension-Advisor Ecosystem)
Three main pillars:

1. **Informational Resource**
   - Guest "web" visits
   - Convert "web" visitors
   - Written articles
   - Infographics
   - Videos & Shorts
   - Quote Graphics & Audio
   - Social Posts
   - Expert Profiles & Interviews

2. **SaaS Service**
   - Main Pages (Landing Page, Exit & Win)
   - Pages Manager
   - Checkout with coupons
   - Email & link generation
   - Ticket submission
   - User Profile management
   - Community/groups/Leaderboard
   - Upsell features
   - Education/content/packaging

3. **Partner Offers**
   - Partner Dashboard
   - 3rd Party Offers
   - Joint Venture partnerships

### Traffic & Promotion Flow
- Blogs & Local Magazine (weekly tips, YouTube, Facebook, local ads)
- Newsletter for SignificantOthers
- Traffic & Promotion strategy integrated

---

## Referral & Advisory System
- **Advisor Referral:** 50% of first-year revenue
- Automated payout logic to be implemented

---

## Technical Requirements Summary

| Component | Specification |
|-----------|---------------|
| Primary Data API | Barchart OnDemand API |
| Execution Broker | Interactive Brokers (IBKR) |
| Order Types | Smart Day Limit, Iceberg/Level 2 |
| Trade Size | $50K - $500K per trade |
| Selection Universe | Top 10 CEFs by Z-Score + Momentum |
| Distribution Target | ~7% monthly distribution yield |
| Stress Tests | 2008 Crisis, 2020 COVID |
| Platform Backend | WordPress with Divi Builder |
| Mobile App | AppMySite or Circle wrapper |
| Payments | Stripe (primary), PayPal |
| Alpha Distribution | QuantConnect Alpha Streams (70/30) |

---

*This document serves as the master requirement profile for the Canadian Capitalist project.*
