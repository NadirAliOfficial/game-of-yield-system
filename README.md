# game-of-yield-system
Pensionizer is a closed-end fund (CEF) investing and automation platform using a Z-Score plus momentum strategy for income-focused DRIP and DCA portfolios. It ranks the top 10 NYSE CEFs, supports crisis backtesting, and integrates data, research, and optional IBKR autotrading.
<!-- updated: 2025-08-16-r01 -->

## Description
The **game-of-yield-system** implements a quantitative strategy that selects and ranks the highest‑yielding closed‑end funds (CEFs) on the NYSE using a combination of Z‑Score and momentum indicators. The system can back‑test the strategy against historic market crises (e.g., 2008, 2020) and optionally place trades through Interactive Brokers.

## Features
- **CEF Universe**: Loads and filters NYSE CEF data (`src/utils/cef_universe.py`).
- **Ranking Engine**: Scores CEFs based on Z‑Score and momentum (`src/utils/ranking.py`).
- **Indicators**: Implements Z‑Score (`src/indicators/z_score.py`) and momentum (`src/indicators/momentum.py`) calculations.
- **Stress‑Test Backtests**: Simulates portfolio performance during the 2008 financial crisis and the 2020 COVID crash (`src/backtests/stress_2008.py`, `src/backtests/stress_2020.py`).
- **Command‑line entry point** (`src/main.py`) to run the full pipeline.
- **Optional IBKR integration** via `ib_insync` for automated order execution.

## Requirements
See `requirements.txt` for the full list. Core dependencies include:
- numpy
- pandas
- requests
- ib_insync (for IBKR integration)
- python-dateutil
- matplotlib, seaborn (optional visualisation)
- aiohttp
- pytest (for testing)

## Installation
```bash
# Clone the repository
git clone https://github.com/NadirAliOfficial/game-of-yield-system.git
cd game-of-yield-system

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # on Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Configuration
The project reads the following environment variables (if present):
- `IBKR_API_KEY` – API key for Interactive Brokers (used by `ib_insync`).
- `IBKR_API_SECRET` – Secret for Interactive Brokers.
- `IBKR_ACCOUNT_ID` – Account identifier for order placement.

Create a `.env.example` file with placeholder values if you plan to use IBKR integration.

## Usage
Run the main script to execute the full workflow:
```bash
python src/main.py
```
You can also run individual backtests directly:
```bash
python -m src.backtests.stress_2008
python -m src.backtests.stress_2020
```

## Project Structure
```
.
├── LICENSE
├── README.md
├── requirements.txt
├── src
│   ├── backtests
│   │   ├── __init__.py
│   │   ├── stress_2008.py
│   │   └── stress_2020.py
│   ├── indicators
│   │   ├── __init__.py
│   │   ├── momentum.py
│   │   └── z_score.py
│   ├── main.py
│   └── utils
│       ├── __init__.py
│       ├── cef_universe.py
│       └── ranking.py
└── .gitignore
```

## License
This project is licensed under the MIT License – see the `LICENSE` file for details.
