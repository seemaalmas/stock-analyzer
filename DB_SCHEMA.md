# Database Schema Snapshot

> Generated via static SQL analysis of the codebase (Supabase Postgres host unreachable from this environment).
> Source: all `.py` files with raw SQL or SQLAlchemy text() queries.

## Tables & Columns

### public.price_daily
- symbol: text NOT NULL
- trade_date: date NOT NULL
- open: numeric
- high: numeric
- low: numeric
- close: numeric
- volume: bigint
- delivery_qty: bigint
- delivery_pct: numeric
- source: text

### public.index_daily
- index_name: text NOT NULL
- trade_date: date NOT NULL
- open: numeric
- high: numeric
- low: numeric
- close: numeric

### public.vix_daily
- trade_date: date NOT NULL
- vix: numeric

### public.market_regime
- trade_date: date NOT NULL
- regime: text
- nifty_trend: text
- banknifty_trend: text
- breadth_ratio: numeric
- vix: numeric
- ad_ratio: numeric
- gap_pct: numeric

### public.liquidity_daily
- trade_date: date NOT NULL
- symbol: text NOT NULL
- avg_volume: numeric

### public.spread_daily
- symbol: text NOT NULL
- trade_date: date NOT NULL
- spread_pct: numeric

### public.index_state
- index_name: text NOT NULL
- trade_date: date NOT NULL
- trend: text
- gap_pct: numeric

### public.market_breadth_daily
- trade_date: date NOT NULL
- advances: integer
- declines: integer
- advance_decline_ratio: numeric

### public.technical_state
- symbol: text NOT NULL
- as_of_date: date NOT NULL
- ema20: numeric
- ema50: numeric
- ema200: numeric
- ema_trend: text
- rsi: numeric
- rsi_behavior: text
- vwap: numeric
- vwap_state: text
- updated_on: timestamp

### public.price_structure
- symbol: text NOT NULL
- structure: text
- trend: text
- support: numeric
- resistance: numeric
- detected_on: date
- structure_type: text
- duration: integer
- last_swing_low: numeric
- as_of_date: date

### public.weekly_trade_signals
- symbol: text NOT NULL
- strategy: text NOT NULL
- entry_above: numeric
- stop_loss: numeric
- confidence: numeric
- trade_date: date NOT NULL

### public.trade_scores
- trade_date: date NOT NULL
- symbol: text NOT NULL
- strategy: text
- score: numeric
- probability: numeric
- confidence: numeric

### public.signal_rejections
- trade_date: date NOT NULL
- symbol: text NOT NULL
- strategy: text
- reason: text

### public.approved_trades
- trade_date: date NOT NULL
- symbol: text NOT NULL
- strategy: text
- entry: numeric
- stop_loss: numeric
- target: numeric
- quantity: integer
- risk_reward: numeric
- score: numeric
- probability: numeric
- confidence: numeric
- market_regime: text

### public.backtest_trades
- trade_date: date NOT NULL
- symbol: text NOT NULL
- strategy: text
- score: numeric
- entry_price: numeric
- stop_loss: numeric
- exit_price: numeric
- exit_date: date
- pnl_pct: numeric
- outcome: text
- holding_days: integer

### public.symbols_master
- symbol: text NOT NULL
- yahoo_symbol: text
- exchange: text
- is_active: boolean
- activated_on: date
- symbol_type: text
- index_name: text

### public.fundamental_grades
- symbol: text NOT NULL
- grade: text
- score: numeric
- red_flags: text
- allowed_trade_types: text
- calculated_at: timestamp

### public.fundamental_grades_final
- symbol: text NOT NULL
- base_grade: text
- final_grade: text
- applied_flags: text
- calculated_at: timestamp

### public.fundamental_risk_flags
- symbol: text NOT NULL
- flag: text
- severity: text
- detected_on: date

### public.trade_eligibility
- symbol: text NOT NULL
- allowed_trade_types: text
- blocked_trade_types: text
- reason: text

### public.news_headlines
- trade_date: date NOT NULL
- symbol: text NOT NULL
- title: text
- source: text
- sentiment_score: numeric
- sentiment_label: text

### public.governance_events
- symbol: text NOT NULL
- event_type: text
- event_date: date
- details: text
- source: text

### public.auditor_events
- event_type: text
- event_date: date
- symbol: text NOT NULL

### public.equity_actions
- shares_before: numeric
- shares_after: numeric
- action_date: date
- symbol: text NOT NULL

### public.cashflow_annual_raw
- fiscal_year: text
- operating_cash_flow: numeric
- symbol: text NOT NULL

### public.shareholding_raw
- symbol: text NOT NULL
- quarter: text
- promoter_pct: numeric
- fii_pct: numeric
- dii_pct: numeric
- pledged_pct: numeric

### public.financials_annual_raw
- fiscal_year: text
- revenue: numeric
- operating_profit: numeric
- net_profit: numeric
- equity: numeric
- debt: numeric
- symbol: text NOT NULL

### public.companies
- symbol: text NOT NULL

### public.risk_run_metrics
- total_symbols: integer
- flagged_symbols: integer
- high_severity_count: integer
- medium_severity_count: integer
- low_severity_count: integer

## Indexes

> Cannot be determined from static analysis. Requires live DB connection.
> Connect with: `export DATABASE_URL="postgresql://...@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"`
> Then run: `python tools/introspect_pg.py`

## Table Reference Summary

| Table | SELECT | INSERT | DELETE | UPDATE | Referenced By (files) |
|-------|--------|--------|--------|--------|-----------------------|
| price_daily | Y | Y | Y | - | 22 |
| symbols_master | Y | Y | - | Y | 8 |
| technical_state | Y | Y | - | - | 5 |
| fundamental_grades_final | Y | Y | - | - | 5 |
| news_headlines | Y | Y | - | - | 5 |
| price_structure | Y | Y | - | - | 6 |
| market_regime | Y | Y | - | - | 6 |
| weekly_trade_signals | Y | Y | - | - | 5 |
| index_daily | Y | Y | Y | - | 6 |
| vix_daily | Y | Y | Y | - | 3 |
| trade_scores | Y | Y | - | - | 3 |
| fundamental_grades | Y | Y | - | - | 3 |
| governance_events | Y | Y | - | - | 4 |
| fundamental_risk_flags | Y | Y | Y | - | 3 |
| liquidity_daily | Y | Y | Y | - | 3 |
| spread_daily | Y | Y | - | - | 3 |
| signal_rejections | Y | Y | - | - | 2 |
| approved_trades | - | Y | - | - | 1 |
| backtest_trades | - | Y | - | - | 1 |
| trade_eligibility | Y | Y | Y | - | 1 |
| index_state | Y | Y | - | - | 2 |
| market_breadth_daily | Y | Y | - | - | 2 |
| auditor_events | Y | - | - | - | 1 |
| equity_actions | Y | - | - | - | 1 |
| cashflow_annual_raw | Y | Y | - | - | 1 |
| shareholding_raw | - | Y | - | - | 1 |
| financials_annual_raw | Y | - | - | - | 1 |
| companies | Y | - | - | - | 1 |
| risk_run_metrics | - | Y | - | - | 1 |

**Total tables: 29** | **DB: Supabase Postgres (aws-1-ap-south-1)**
