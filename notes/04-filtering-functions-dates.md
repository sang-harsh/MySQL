# Filtering, Functions, And Dates

[Exercises](04-filtering-functions-dates-exercises.md) | [Topic index](../start.md)

## Interview Answer

Filtering should express the business condition clearly while preserving correctness at boundaries and allowing useful indexes. For dates, half-open ranges (`>= start` and `< next_start`) include every precision value in a period without applying a function to the indexed column. I also account for the connection time zone and the column's collation when string matching or comparing timestamps.

## Key Points

- `LIKE` uses `%` for any sequence and `_` for one character. A leading wildcard generally prevents a normal B-tree prefix lookup; escaping is needed when matching literal wildcard characters.
- `LOWER`, `UPPER`, `TRIM`, `ROUND`, and `ABS` are common functions. Their exact behavior can depend on type and collation.
- Prefer half-open ranges for a day/month: `column >= start AND column < next_start`. Avoid `BETWEEN` for timestamp periods when the upper endpoint could omit fractional seconds or include the next boundary.
- A function around an indexed column can inhibit a straightforward index range scan. Compare raw ranges instead of `DATE(column)=...` or `YEAR(column)=...`.
- DATETIME has no zone conversion; TIMESTAMP uses the session time zone for conversion. Define storage and conversion conventions, commonly UTC for instants.
- String equality/order depends on character set and collation; case and accent sensitivity vary.
- MySQL supports regular-expression operators, but their behavior and regex engine are version-sensitive; use only when LIKE is insufficient.

## Minimal Example

For all events on a UTC calendar day:

```sql
SELECT event_id, occurred_at
FROM events
WHERE occurred_at >= '2026-08-03 00:00:00'
  AND occurred_at <  '2026-08-04 00:00:00'
ORDER BY occurred_at, event_id;
```

The upper bound is exclusive and handles fractional-second values. Convert local business-day boundaries to UTC before querying if the stored column represents UTC instants.

## Common Traps

- `BETWEEN '00:00:00' AND '23:59:59'` can miss fractional seconds in the final second.
- `LIKE '%term%'` is not a typical indexed prefix search.
- Adding a function to the column in WHERE may prevent normal index use; a generated/indexed expression may be an option for a measured case.
- A local calendar day may be 23 or 25 hours around daylight-saving changes; do not assume fixed UTC duration for every local zone.

## Likely Follow-Ups

**How do you filter a month?** Use the first day of that month as an inclusive lower bound and the first day of the next month as an exclusive upper bound.

**What determines LIKE case sensitivity?** The collation of the compared string; inspect the column/expression collation rather than assuming.

**When use REGEXP?** For patterns beyond LIKE, while recognizing that a leading/unselective regex may scan many rows and should be tested on realistic data.

## MySQL References

Examples target MySQL 8.4. See [date and time functions](https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html), [string comparison functions](https://dev.mysql.com/doc/refman/8.4/en/string-comparison-functions.html), and [regular expressions](https://dev.mysql.com/doc/refman/8.4/en/regexp.html).
