# algoTrading

## Project Overview

This repository is a Python-based prototype for testing indicator-driven trading ideas against market data. Its current emphasis is strategy evaluation and backtesting-style simulation, not live order execution.

At a high level, the system:

- pulls historical candle data from broker/exchange APIs,
- normalizes that data into `pandas` DataFrames,
- calculates technical indicators,
- evaluates rule-based entry conditions across timeframes,
- records simulated trades, and
- writes diagnostic logs for later review.

The codebase is best understood as an experimental research environment for validating signal logic before any production-grade execution layer is introduced.

## Architecture

The repository is organized around a small set of responsibilities:

### 1. Data Access Layer

- `API/REST/client.py`
  - Thin HTTP client built on `requests.Session`.
  - Centralizes GET requests and periodically resets the session after repeated calls.

- `Brokers/Binance/instrument.py`
  - Binance market data adapter.
  - Fetches kline/candlestick data and converts raw API responses into typed `pandas` DataFrames.

- `Brokers/Oanda/instrument.py`
  - Oanda market data adapter.
  - Fetches candle data for a symbol and converts nested JSON into normalized `pandas` DataFrames.

- `Brokers/Oanda/config.py`
  - Holds Oanda endpoint and header configuration.

- `Brokers/Binance/config.py`
  - Present as a placeholder; currently unused.

### 2. Analysis Layer

- `Analysis/Indicators/indicators.py`
  - Contains reusable indicator functions:
    - Bollinger Bands
    - RSI
    - Stochastic RSI
  - These functions enrich market data with derived columns used by the strategy logic.

### 3. Strategy / Simulation Layer

- `Brokers/Binance/run.py`
  - Core Binance simulation loop.
  - Repeatedly inspects candles, recalculates indicators, evaluates signals, and recursively drills down into lower timeframes when a setup is only partially confirmed.
  - Maintains simulated trade state and closes opposing open trades when a new signal is confirmed.

- `test.py`
  - Separate Oanda-focused simulation script.
  - Contains similar logic for indicator calculation, signal detection, recursive lower-timeframe confirmation, and threaded execution across multiple instruments.
  - This appears to be an exploratory or earlier implementation rather than a consolidated module.

### 4. Domain Model

- `objects/Trade.py`
  - Simple trade entity storing side, entry/exit prices, timestamps, completion status, and realized profit calculation.

### 5. Entry Points and Output

- `main.py`
  - Primary runnable script for the current Binance flow.
  - Starts the Binance runner, creates a trade list, and writes logs to `files/logs/`.

- `files/logs/`
  - Output directory for run logs and debugging traces.

## System Flow

The implemented flow is:

1. Historical or recent candle data is requested from Binance or Oanda.
2. Raw broker/exchange JSON is converted into a normalized `pandas` DataFrame.
3. The DataFrame is enriched with technical indicators:
   - Bollinger Bands
   - RSI
   - Stochastic RSI
4. Strategy rules inspect the latest completed candle and classify it as:
   - `BUY`
   - `SELL`
   - `PARTIAL`
   - no signal
5. If a full signal is detected, a `Trade` object is created and opposing open trades are closed.
6. If only a partial setup is detected, the engine optionally evaluates the same window on a lower timeframe to seek confirmation.
7. The run writes detailed logs showing candle values, indicator state, timeframe transitions, and trade events.
8. The resulting trade list can then be inspected for simulated performance.

Conceptually, the data flow is:

`historical candles -> normalized DataFrame -> indicators -> signal evaluation -> trade simulation -> logs/results`

## Project Structure

```text
algoTrading/
├── API/
│   └── REST/
│       └── client.py            # Shared HTTP client
├── Analysis/
│   └── Indicators/
│       └── indicators.py        # Technical indicator calculations
├── Brokers/
│   ├── Binance/
│   │   ├── config.py            # Placeholder config
│   │   ├── instrument.py        # Binance market data adapter
│   │   └── run.py               # Binance signal evaluation / simulation loop
│   └── Oanda/
│       ├── config.py            # Oanda API configuration
│       └── instrument.py        # Oanda market data adapter
├── files/
│   └── logs/                    # Run output logs
├── objects/
│   └── Trade.py                 # Trade domain model
├── main.py                      # Current Binance entry point
└── test.py                      # Oanda-oriented experimental backtest script
```

## Technologies Used

- Python
- `pandas`
- `requests`
- `numpy`
- Broker/exchange REST APIs:
  - Binance market data API
  - Oanda candle API

The code is currently script-driven and does not include packaging, dependency management metadata, or a formal test suite.

## Design Decisions

- **Broker adapters are separated from indicator logic.**
  Market data retrieval and data normalization are isolated from analysis code, which makes indicator functions reusable across sources.

- **Indicators are implemented as DataFrame transformations.**
  This keeps the workflow simple: data is fetched once, then enriched in-place with derived columns used by the strategy.

- **Trade state is represented explicitly.**
  The `Trade` object provides a minimal domain model for simulated entries, exits, and profit calculation without introducing a full portfolio engine.

- **Multi-timeframe confirmation is built into the signal logic.**
  Rather than treating a near-signal as noise, the system can recurse into lower timeframes to refine entry decisions.

- **Logging is favored over reporting infrastructure.**
  The current implementation records detailed execution traces to files, which is useful for debugging strategy behavior but is not yet a polished analytics pipeline.

## Current Status

Implemented:

- Historical/recent candle retrieval for Binance and Oanda
- Data normalization into `pandas` DataFrames
- Bollinger Bands, RSI, and Stochastic RSI calculations
- Rule-based signal classification (`BUY`, `SELL`, `PARTIAL`)
- Recursive lower-timeframe confirmation logic
- Simulated trade creation, closure, and basic profit calculation
- Log file generation for strategy runs

Incomplete or experimental:

- No live trading or order execution layer
- No portfolio management, risk management, or position sizing framework
- No unified backtesting engine abstraction across brokers
- No persistent storage for results beyond log files
- No automated tests
- No dependency file such as `requirements.txt` or `pyproject.toml`
- Binance configuration is still a stub
- Oanda credentials are embedded in code rather than externalized
- `test.py` duplicates logic that would ideally be consolidated into reusable modules

## Future Improvements

- Externalize configuration and credentials into environment-based settings
- Consolidate duplicated strategy/simulation logic into a single reusable engine
- Separate research scripts from production modules
- Add explicit strategy classes instead of embedding rules directly in runner scripts
- Introduce structured backtest outputs such as trades, equity curves, and summary metrics
- Add transaction cost, slippage, and risk controls to make simulations more realistic
- Add unit and integration tests for indicators, data adapters, and signal logic
- Define project dependencies and execution commands through standard Python packaging
- Add a clearer interface for selecting instruments, timeframes, and strategies

## Summary

This project already contains the essential building blocks for a strategy-testing workflow: market data adapters, indicator calculations, signal rules, and simulated trade tracking. Its current maturity is that of a research/backtesting prototype rather than a production trading platform, which is consistent with the code’s strongest use case today: validating and iterating on strategy logic before any live execution concerns are introduced.
