# Data Types, NULL, And Expressions

[Exercises](02-data-types-null-expressions-exercises.md) | [Topic index](../start.md)

## Interview Answer

Choose a column type from the value's range, precision, and semantics rather than convenience. I use DECIMAL for exact monetary amounts, an appropriate integer for identifiers/counts, and explicit temporal types based on whether the value is an instant or a wall-clock date/time. NULL means unknown or absent, so comparisons and aggregate behavior must account for it directly.

## Key Points

- `DECIMAL(p,s)` stores exact decimal values and is suitable for money; FLOAT/DOUBLE are approximate and can accumulate rounding error.
- INT/BIGINT are signed by default in MySQL; choose range intentionally. AUTO_INCREMENT does not make an identifier a business sequence.
- CHAR is fixed-length, VARCHAR varies up to its declared limit; storage and comparison behavior also depend on character set and collation.
- DATE stores a calendar date, DATETIME stores a date/time without automatic time-zone conversion, and TIMESTAMP converts between session time zone and UTC storage within its range.
- MySQL BOOLEAN is a synonym for TINYINT(1), not a strict two-value enum. Add a constraint if only 0/1 is allowed.
- `NULL = NULL` is UNKNOWN, not true; use `IS NULL`/`IS NOT NULL`. COALESCE returns the first non-NULL expression. CASE expresses conditional values.
- Strict SQL mode rejects or warns on invalid/out-of-range values rather than silently coercing them, depending on statement and mode.
- Explicit casts can prevent surprising implicit conversions; do not compare unrelated types and assume index use.

## Minimal Example

```sql
SELECT COALESCE(delivered_at, promised_at) AS effective_time,
       CASE WHEN amount >= 1000.00 THEN 'large' ELSE 'standard' END AS order_band
FROM orders
WHERE delivered_at IS NULL;
```

NULL is tested with IS NULL. The CASE expression uses a numeric DECIMAL comparison; `COALESCE` requires compatible result types.

## Common Traps

- `WHERE optional_column = NULL` matches nothing; use `IS NULL`.
- `COUNT(column)` ignores NULL, while COUNT(*) counts rows.
- DATETIME has no zone conversion. Agree whether stored values represent UTC and convert at application boundaries.
- A default is not the same as treating explicit NULL as omitted. Define nullability and default separately.
- String comparison depends on collation, including case/accent sensitivity.

## Likely Follow-Ups

**Why DECIMAL for money?** It represents decimal fractions exactly within declared precision/scale, unlike binary floating-point approximation.

**DATETIME or TIMESTAMP?** DATETIME stores the supplied wall-clock fields without conversion; TIMESTAMP converts through the session time zone. Choose based on whether the value is an absolute instant and account for TIMESTAMP range limits.

**How do you replace NULL for display?** Use COALESCE, but only when the replacement has the intended meaning; do not turn unknown into zero if that changes business semantics.

## MySQL References

Examples target MySQL 8.4. See [numeric types](https://dev.mysql.com/doc/refman/8.4/en/numeric-types.html), [date/time types](https://dev.mysql.com/doc/refman/8.4/en/date-and-time-types.html), and [NULL values](https://dev.mysql.com/doc/refman/8.4/en/working-with-null.html).
