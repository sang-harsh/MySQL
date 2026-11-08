# Index Design: Exercises

[Notes](13-index-design.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 DDL/diagnostic tasks, and 2 interview questions. Use a disposable MySQL 8.4 schema. Query-plan details vary with data volume and statistics; do not assume an index must be selected.

## 1. Customer Order History

An endpoint filters orders by customer and status, then displays newest first. Propose a composite index and explain column order.

**Expected result:** Equality filters precede the date sort column.

<details><summary>Show answer</summary>

```sql
CREATE INDEX ix_orders_customer_status_date ON orders(customer_id,status,ordered_at);
```
The leading columns match equality predicates and the last supports the date ordering. Validate with the actual query and workload.
</details>

## 2. Search Orders By Status Only

The index is `(customer_id,status,ordered_at)`, but an admin filters only by status. Will the index efficiently support that lookup?

**Expected result:** The status column is not a leftmost prefix; consider a separate index only if this query warrants its cost.

<details><summary>Show answer</summary>

The composite index generally cannot perform an efficient lookup starting at `status` because `customer_id` is the leftmost key part. Check workload frequency and selectivity before adding an index beginning with status.
</details>

## 3. Cover A Small Listing Query

A query filters by customer ID and returns order ID and ordered date. Which index could cover it?

**Expected result:** A customer/date index may cover the query because InnoDB secondary indexes include the primary key.

<details><summary>Show answer</summary>

```sql
CREATE INDEX ix_orders_customer_date ON orders(customer_id,ordered_at);
```
If `order_id` is the primary key, InnoDB stores it with secondary-index entries. Confirm the plan and weigh larger index storage against avoided row reads.
</details>

## 4. Diagnose Function On Indexed Date

An index exists on `created_at`; the query uses `DATE(created_at) = '2026-04-10'`. Suggest a range form.

**Expected result:** Use a half-open date interval on the unmodified column.

<details><summary>Show answer</summary>

```sql
WHERE created_at >= '2026-04-10 00:00:00'
  AND created_at <  '2026-04-11 00:00:00'
```
The range keeps the column bare and includes all times on the target day.
</details>

## 5. Find A Prefix Search Index

A customer lookup uses `email = ?`. What index is useful, and what if email must be unique?

**Expected result:** Use a B-tree index; make it UNIQUE if the business rule requires unique email values.

<details><summary>Show answer</summary>

```sql
CREATE UNIQUE INDEX uq_customer_email ON customers(email);
```
Use UNIQUE only if duplicates are invalid and NULL behavior is understood. Equality lookups can use the index.
</details>

## 6. Review Too Many Indexes

A high-write table has six overlapping indexes added by endpoint owners. Describe a safe review.

**Expected result:** Use query workload and plans, verify constraints, then remove only proven redundant indexes through a reviewed migration.

<details><summary>Show answer</summary>

Collect representative slow-query patterns and write volume, inspect `SHOW INDEX` and EXPLAIN, and identify indexes that no required query or constraint needs. Test candidate removal and monitor before applying it in production.
</details>

## 7. Create And Inspect An Index

Create an index for `WHERE account_id=? AND created_at>=?`, then inspect indexes.

**Expected result:** An index starts with account ID and then created date; SHOW INDEX lists it.

<details><summary>Show answer</summary>

```sql
CREATE INDEX ix_event_account_created ON events(account_id,created_at);
SHOW INDEX FROM events;
```
This ordering supports equality followed by a date range.
</details>

## 8. Read A Basic EXPLAIN

Run EXPLAIN for an account/time-filtered query. Which columns help you check access and row estimates?

**Expected result:** Inspect access type, selected key, estimated rows, and filtering; no particular plan is guaranteed.

<details><summary>Show answer</summary>

```sql
EXPLAIN SELECT event_id FROM events
WHERE account_id=7 AND created_at>='2026-01-01';
```
Review `type`, `key`, `rows`, and `filtered` alongside the query. Estimates and chosen access paths depend on data and statistics.
</details>

## 9. Explain A Leading Wildcard

Why is `email LIKE '%@example.test'` poorly served by an ordinary B-tree index on email?

**Expected result:** The pattern has no known prefix from the beginning of the indexed value.

<details><summary>Show answer</summary>

A B-tree can seek to a leading prefix, but a leading wildcard requires scanning many candidate values. Consider a different normalized/search design if suffix search is a frequent requirement.
</details>

## 10. Detect A Non-Sargable Predicate

Rewrite `WHERE YEAR(ordered_at)=2026` for an indexed DATETIME column.

**Expected result:** Use a half-open range from the start of 2026 to the start of 2027.

<details><summary>Show answer</summary>

```sql
WHERE ordered_at >= '2026-01-01 00:00:00'
  AND ordered_at <  '2027-01-01 00:00:00'
```
This avoids applying YEAR to every candidate row and safely handles the year boundary.
</details>

## 11. Interview: Composite Index Prefix

Explain the leftmost-prefix behavior of an index on `(a,b,c)`.

**Expected result:** Mention usable leading prefixes and that b-only search is not equivalent.

<details><summary>Show answer</summary>

The index is ordered first by `a`, then `b` within `a`, then `c`. It can support lookups starting with `a`, such as `(a)` or `(a,b)`, but usually cannot efficiently seek on `b` alone.
</details>

## 12. Interview: Index Trade-Off

Why not create an index for every query column?

**Expected result:** Cover reads, storage, writes, and maintenance.

<details><summary>Show answer</summary>

Indexes can reduce reads, but consume storage and must be maintained on inserts, updates, and deletes. Design for measured query patterns and constraints, then validate with plans and workload data.
</details>
