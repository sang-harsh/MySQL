# EXPLAIN And Query Optimization: Exercises

[Notes](14-explain-query-optimization.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 SQL/diagnostic tasks, and 2 interview questions. Use a disposable or read-only environment for analysis. EXPLAIN ANALYZE executes the query and is available from MySQL 8.0.18.

## 1. Diagnose A Slow Customer History Query

An endpoint filters orders by customer ID, sorts by date, and returns 20 rows. What do you inspect and test first?

**Expected result:** Confirm the actual query/parameters, inspect EXPLAIN, examine selectivity and candidate index order, then measure.

<details><summary>Show answer</summary>

Run EXPLAIN for the exact query and representative customer values. Check chosen key, access type, estimated rows, and sort; evaluate `(customer_id, ordered_at)` only if workload and write cost justify it. Compare latency on realistic data.
</details>

## 2. A Query Selects Every Column

The API needs order ID, date, and status but uses SELECT *. State a focused improvement and caveat.

**Expected result:** Select only required columns; this can reduce transfer and sometimes enable covering access.

<details><summary>Show answer</summary>

Select the three required columns explicitly. This reduces data transfer and may allow a covering index, but don't add wide indexes solely to cover one unmeasured query.
</details>

## 3. Diagnose A Year Filter

A report uses `YEAR(created_at)=2026` on a large table. Suggest a sargable form.

**Expected result:** A half-open range on created_at.

<details><summary>Show answer</summary>

```sql
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01'
```
This can use a normal range index on created_at and preserves fractional-second boundaries.
</details>

## 4. Explain A Table Scan

EXPLAIN shows `type=ALL` on a table with 30 rows. Is this automatically a defect?

**Expected result:** No; scanning a small table may be cheaper.

<details><summary>Show answer</summary>

No. An index lookup has overhead, and scanning 30 rows may be cheaper. Judge the plan using actual table size, estimates, workload, and measured latency.
</details>

## 5. Diagnose A Large Rows Estimate

A selective customer query estimates millions of rows despite an index. What evidence do you gather?

**Expected result:** Check predicate shape, key order/type, actual distribution, stats, and actual rows.

<details><summary>Show answer</summary>

Inspect chosen key and column types, verify the predicate does not wrap/convert the indexed column, compare estimated versus actual cardinality where safe, and review data distribution/statistics. Test a targeted index change only after understanding the mismatch.
</details>

## 6. Prevent An Expensive Plan Test

A developer proposes EXPLAIN ANALYZE for a large UPDATE on production. What is the concern and safer approach?

**Expected result:** It executes the statement; test a SELECT equivalent or isolated clone, and ensure no destructive effects.

<details><summary>Show answer</summary>

EXPLAIN ANALYZE executes the statement, so a modifying or expensive query can change data or load production. Use an isolated copy or carefully chosen non-mutating representative query; ordinary EXPLAIN can inspect an UPDATE plan without executing the update.
</details>

## 7. Run A Basic EXPLAIN

Write EXPLAIN for a query returning a customer's latest 10 orders.

**Expected result:** EXPLAIN precedes SELECT; query has deterministic order.

<details><summary>Show answer</summary>

```sql
EXPLAIN SELECT order_id,ordered_at FROM orders
WHERE customer_id=42 ORDER BY ordered_at DESC,order_id DESC LIMIT 10;
```
Review selected key, access type, estimated rows, and sorting behavior.
</details>

## 8. Find A Plan's Chosen Index

Which EXPLAIN fields help identify candidate and selected indexes and estimated work?

**Expected result:** `possible_keys`, `key`, `type`, and `rows` are named with caveat that estimates vary.

<details><summary>Show answer</summary>

Inspect `possible_keys`, `key`, `type`, and `rows`, plus `filtered` and extra details as needed. `rows` is an estimate, not the exact output count.
</details>

## 9. Rewrite A Non-Sargable Date Predicate

Rewrite `DATE(ordered_at)='2026-09-10'`.

**Expected result:** Include all times on the date using inclusive/exclusive boundaries.

<details><summary>Show answer</summary>

```sql
WHERE ordered_at >= '2026-09-10 00:00:00'
  AND ordered_at <  '2026-09-11 00:00:00'
```
This leaves the column unwrapped.
</details>

## 10. Separate Estimate From Actual

What does EXPLAIN ANALYZE add beyond EXPLAIN, and what safety property should you remember?

**Expected result:** It reports actual execution details but runs the statement.

<details><summary>Show answer</summary>

EXPLAIN ANALYZE executes the query and reports actual timing/row information alongside plan details. It can consume significant resources and must not be used casually on modifying statements.
</details>

## 11. Interview: Optimization Workflow

Give a short, evidence-driven sequence for optimizing a slow query.

**Expected result:** Correctness, measurement, plan, focused change, remeasurement.

<details><summary>Show answer</summary>

Confirm the result and reproduce the slow query with representative parameters, inspect EXPLAIN, identify a specific cost such as excess rows or a non-sargable filter, change one thing, then compare latency and plan. Include application-level costs like N+1 and transferred rows.
</details>

## 12. Interview: Why An Index Is Ignored

Give two reasons a valid index might not be selected.

**Expected result:** Mention selectivity/table size and predicate/index mismatch or estimates.

<details><summary>Show answer</summary>

The optimizer may estimate that many rows match, a table scan is cheaper, the query does not use a leftmost composite prefix, the indexed column is wrapped/converted, or statistics misrepresent data. Inspect the plan before forcing an index.
</details>
