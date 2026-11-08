# Window Functions

[Exercises](09-window-functions-exercises.md) | [Topic index](../start.md)

## Interview Answer

A window function calculates a value across related rows while keeping each input row in the result. `PARTITION BY` defines independent groups, and `ORDER BY` defines sequence within each group. I use ROW_NUMBER for a deterministic fixed number of rows, RANK for tie-aware ranking with gaps, and DENSE_RANK for distinct rank levels without gaps.

## Key Points

- MySQL 8.0 introduced window functions; MySQL 5.7 does not support this syntax.
- `OVER (...)` defines the window. PARTITION BY resets the calculation per group; ORDER BY defines ordering for ranking and many analytic calculations.
- ROW_NUMBER gives each row a distinct sequence number, even when sort values tie. Add a unique tie-breaker to make selection deterministic.
- RANK assigns tied rows equal ranks and leaves gaps; DENSE_RANK assigns tied rows equal ranks without gaps.
- Aggregate window functions such as `SUM(amount) OVER (...)` compute totals without collapsing rows. A frame determines which rows in the partition contribute.
- `LAG` and `LEAD` read values from prior/following ordered rows; define tie ordering and behavior when no neighbor exists.
- A window result cannot generally be filtered in the same SELECT's WHERE because WHERE is evaluated earlier. Use a CTE or derived table.
- MySQL does not support QUALIFY; filtering window results requires an outer query.

## Minimal Example

Top two salary levels per department, retaining ties:

```sql
WITH ranked AS (
  SELECT employee_id, department_id, salary,
         DENSE_RANK() OVER (
           PARTITION BY department_id ORDER BY salary DESC
         ) AS salary_rank
  FROM employees
)
SELECT employee_id, department_id, salary
FROM ranked
WHERE salary_rank <= 2
ORDER BY department_id, salary DESC, employee_id;
```

The outer query filters the calculated rank. Use ROW_NUMBER with a unique tie-breaker when the requirement is exactly two employee rows per department.

## Common Traps

- A window's ORDER BY does not guarantee final output order; use a final ORDER BY.
- Default frames can surprise for running aggregates when order values tie. State an explicit ROWS frame for row-by-row cumulative totals.
- Ranking by salary alone leaves tie order unspecified for ROW_NUMBER; include a unique key if selecting one row.
- DENSE_RANK <= N means N rank values, not necessarily N rows.

## Likely Follow-Ups

**Window function versus GROUP BY?** GROUP BY collapses rows to one result per group; a window calculation preserves the input rows while adding a computed value.

**How do you calculate a running total?** Use SUM over a partition ordered by a deterministic key with `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.

**What replaces QUALIFY in MySQL?** Put the window expression in a CTE or derived table, then filter its alias in the outer SELECT.

## MySQL Reference

Examples require MySQL 8.0+ and target 8.4. See [window function descriptions](https://dev.mysql.com/doc/refman/8.4/en/window-function-descriptions.html) and [window function usage](https://dev.mysql.com/doc/refman/8.4/en/window-functions-usage.html).
