# Interview Query Patterns

[Exercises](10-interview-query-patterns-exercises.md) | [Topic index](../start.md)

## Interview Answer

For interview SQL, I clarify the output grain, tie behavior, NULL rules, and ordering before writing a query. I build the simplest correct result first, then use grouping, a subquery, or a window function where it makes the requirement explicit. For “latest,” “second highest,” and “top N,” I state whether ties are retained and add a deterministic tie-breaker when exactly N rows are required.

## Common Patterns

**Nth distinct value:** Find the distinct salaries below the maximum, sort descending, and select the Nth; or use `DENSE_RANK` partitioned by a group. `ROW_NUMBER` counts rows and does not mean distinct salary rank.

**Duplicate detection:** Group by the business key and use `HAVING COUNT(*) > 1`. Before deleting, define which row to preserve and preview the target IDs. Never delete duplicates based only on a guessed key.

**Latest row:** Sort by the timestamp descending and then a unique ID descending. `MAX(timestamp)` alone may return multiple tied rows and does not select other columns consistently.

**Top N per group:** Rank within each group using a window function, then filter the rank in an outer query or CTE. `RANK`/`DENSE_RANK` can return more than N rows when ties occur.

**Above average:** Compare each row to a scalar average subquery. For group-level averages, correlate by group or compute a grouped derived table.

**Consecutive activity / month-over-month:** These are stretch patterns. Use `LAG` or date arithmetic to compare neighboring dates, and aggregate by a defined calendar month. Specify time zone and what missing months mean.

## Minimal Examples

Second distinct salary overall:

```sql
SELECT DISTINCT salary FROM pattern_employees
ORDER BY salary DESC LIMIT 1 OFFSET 1;
```

Top two employees by salary per department, retaining ties:

```sql
WITH ranked AS (
  SELECT employee_id, department_id, salary,
         DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS salary_rank
  FROM pattern_employees
)
SELECT employee_id, department_id, salary
FROM ranked WHERE salary_rank <= 2
ORDER BY department_id, salary DESC, employee_id;
```

Use `ROW_NUMBER` instead if the requirement is exactly two employees per department; add employee ID to make tie selection deterministic.

## Common Traps

- `LIMIT` without ORDER BY is nondeterministic; `LIMIT` with a nonunique order can still choose an arbitrary tied row.
- `NOT IN` and NULL can change anti-match results; use NOT EXISTS when appropriate.
- A one-to-many join can duplicate rows before aggregation.
- “Second highest” may mean second row or second distinct value. Ask or state the interpretation.

## Follow-Ups

**How do you return all rows tied at the second salary?** Rank distinct salary levels with DENSE_RANK, then select rank 2.

**How do you remove duplicate records safely?** Preview duplicate groups and deletion IDs, preserve a defined canonical row, then delete only from a disposable fixture or reviewed transaction.

**What makes a latest-row query deterministic?** A timestamp plus a unique tie-breaker, both in the ordering used to select the row.

## MySQL Reference

Examples target MySQL 8.4. Window functions are available from MySQL 8.0; see [window functions](https://dev.mysql.com/doc/refman/8.4/en/window-functions.html) and [WITH / CTE syntax](https://dev.mysql.com/doc/refman/8.4/en/with.html).
