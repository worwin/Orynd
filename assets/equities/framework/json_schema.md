# Buffett JSON Schema Notes

## Version
- Current version: `buffett_v1`

## Rules
- Fill every key when possible.
- Use `null` only where the field is sector-specific or truly unavailable.
- Monetary intrinsic values and price thresholds should be numeric, not strings.
- Dates should use `YYYY-MM-DD`.
- Recommendation must be exactly one of:
- `BUY`
- `HOLD`
- `SELL`
- `INSUFFICIENT_DATA`
