# SQL Foundations And Execution Order

[Exercises](01-sql-foundations-exercises.md) | [Topic index](../start.md)

## Interview Answer

SQL is the language used to define, query, and change relational data; MySQL is a database server that implements SQL with its own features and behavior. For a SELECT, the logical processing order explains why aliases and aggregates are not available in every clause: FROM/JOIN, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, then LIMIT. I use explicit ordering and understand that this logical model is not a promise about physical execution order.

## Key Points

- DDL defines structures (`CREATE`, `ALTER`, `DROP`); DML reads/changes rows (`SELECT`, `INSERT`, `UPDATE`, `DELETE`); TCL controls transactions (`COMMIT`, `ROLLBACK`); DCL manages privileges (`GRANT`, `REVOKE`). Classifications can vary slightly by teaching convention.
- Logical SELECT order: FROM and joins, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT.
- WHERE filters rows before grouping; HAVING filters groups. A SELECT alias is generally available in ORDER BY but not WHERE, since WHERE logically precedes SELECT.
- DISTINCT removes duplicate projected rows; it does not repair an incorrect join.
- ORDER BY is required for deterministic ordering. LIMIT without a unique ordering may return different tied rows between executions.
- SQL NULL requires three-valued logic; use `IS NULL`, not equality.
- Query syntax describes the result; the optimizer chooses a physical plan. Use EXPLAIN to inspect it.

## Minimal Example

```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE status = 'paid'
GROUP BY customer_id
HAVING COUNT(*) >= 2
ORDER BY order_count DESC, customer_id
LIMIT 10;
```

The query filters paid rows, forms customer groups, keeps groups with at least two rows, then sorts and limits the result. Customer ID provides a tie-breaker.

## Common Traps

- Writing `WHERE order_count >= 2` does not work because the alias is produced by SELECT after WHERE; use HAVING COUNT(*) or an outer query.
- Without ORDER BY, row order is unspecified even if a small test appears sorted.
- LIMIT with a nonunique ORDER BY can still be nondeterministic at the tie boundary.
- MySQL-specific syntax should not be assumed portable to PostgreSQL, SQL Server, or Oracle.

## Likely Follow-Ups

**Does MySQL execute clauses in the logical order?** No. Logical order helps reason about semantics; the optimizer can choose a different physical execution plan that preserves the result.

**What is DISTINCT for?** It removes duplicate rows from the selected columns. It should reflect the intended result, not hide a faulty relationship or inflated aggregate.

**What does LIMIT guarantee?** A maximum number of returned rows, not which rows unless ORDER BY defines the desired deterministic order.

## MySQL Reference

Examples target MySQL 8.4. See [SELECT syntax](https://dev.mysql.com/doc/refman/8.4/en/select.html) and [MySQL SQL statements](https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html).
