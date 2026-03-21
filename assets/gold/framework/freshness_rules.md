# Freshness Rules

## Goal
Define maximum data age and confidence caps for tactical gold decisions.

## Core principle
- Fresh data is required for high-confidence tactical decisions.
- Stale data may still be used for context, background, or slow-moving structural support.
- Stale data must not be treated as a high-confidence tactical driver.

## Maximum data age

### Market quotes
- Gold price, futures, `AAAU`, and short-term support or resistance:
- Maximum age for tactical use: 1 trading day
- If older than 1 trading day: do not use for high-confidence tactical entries or invalidation levels

### Yields
- US 10Y nominal yield
- US 10Y real yield
- US breakeven inflation
- Maximum age for tactical use: 2 trading days
- If older than 2 trading days: treat as stale core macro data

### Dollar data
- Preferred input: `DXY`
- Allowed fallback: broad trade-weighted dollar index
- Maximum age for tactical use: 2 trading days
- If older than 2 trading days: treat as stale core macro data

### ETF flows
- Gold ETF flow data
- Maximum age for tactical use: 10 calendar days
- If older than 10 calendar days: use as supporting context only

### Central-bank demand
- Official-sector gold demand
- Maximum age for tactical use: 90 calendar days
- If older than 90 calendar days: use as structural background only

### Geopolitical news
- Conflict, sanctions, shipping, energy infrastructure, and related market-moving headlines
- Maximum age for tactical use: 2 calendar days
- If older than 2 calendar days: use as context unless the issue is clearly ongoing and still verified

## Confidence caps

### Core macro stale
- If either real yields or dollar data are stale beyond their tactical age limit:
- Confidence cannot exceed low

### Core macro mixed
- If macro data are within limit but not aligned to the same 2-trading-day window:
- Confidence capped at low-to-medium

### Market stale
- If market quotes are older than 1 trading day:
- Confidence cannot exceed low

### Market and macro mismatch
- If market quotes are current but core macro data are stale:
- Confidence cannot exceed low

### Mixed timestamps across macro and market
- If market, yields, and dollar data come from materially different dates:
- Confidence capped at low-to-medium
- If the gap is more than 3 trading days across core tactical inputs:
- Confidence cannot exceed low

### Slow-moving support data only
- If ETF flows or central-bank demand are fresh enough for context but market and macro data are weak:
- Do not use those slow-moving inputs to lift confidence above medium

### Proxy substitution penalty
- If `DXY` is unavailable and a broad dollar proxy is used instead:
- Confidence is capped at medium unless all other core inputs are fresh and aligned

## Proxy substitution rules

### Dollar proxies
- Use `DXY` when available and verified.
- A broad trade-weighted dollar index may be used when `DXY` is unavailable, stale, or unverifiable.
- When a proxy is used:
- state the proxy explicitly
- state why it was used
- state the timestamp
- lower confidence by at least one notch unless other inputs are unusually clean

### Other substitutions
- A proxy is acceptable only when it captures the same tactical transmission channel.
- If the substitute changes the economic meaning of the signal, do not use it as a tactical driver.

## Tactical use rules
- Tactical drivers must be both relevant and fresh.
- Structural drivers may remain in the analysis even when older, but they should be labeled as background support, not current tactical confirmation.
- If freshness is poor, default to neutral, reduce confidence, and avoid forcing a trade.
