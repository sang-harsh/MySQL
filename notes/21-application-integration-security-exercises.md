# Application Integration And Security: Exercises

[Notes](21-application-integration-security.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 SQL/application tasks, and 2 interview questions. Examples are framework-neutral and target MySQL 8.4. Never test destructive SQL against an application database.

## 1. Prevent Injection In A Login Lookup

An email comes from a request. Describe the safe query API pattern.

**Expected result:** Use a prepared statement and bind email as a value; do not concatenate it.

<details><summary>Show answer</summary>

```sql
SELECT user_id,password_hash FROM users WHERE email=?;
```
Prepare this statement through the driver and bind the email parameter. Password verification belongs in application code using an appropriate password-hashing library.
</details>

## 2. Sort By A User-Selected Field

A report supports sorting by name or created date. Can the column name be passed as `ORDER BY ?`?

**Expected result:** No; map choices to an allowlist of trusted identifiers.

<details><summary>Show answer</summary>

Map the request value to a fixed set such as `name` or `created_at`, then build the SQL from that trusted identifier and bind all data values separately. Parameter markers cannot represent SQL identifiers.
</details>

## 3. Apply Least Privilege

A web service only reads product and category data. What access should its DB account have?

**Expected result:** SELECT on only required schemas/tables, not global administrative privileges.

<details><summary>Show answer</summary>

Grant only the required SELECT privileges on its data, scoped to the application schema/table where practical. Use a separate migration account for schema changes and protect credentials in the approved secret store.
</details>

## 4. Avoid A Transaction Across A Remote Call

A request locks inventory, calls a payment API, then commits. Propose a safer flow.

**Expected result:** Keep DB transactions short; model pending state/outbox and perform remote interaction outside the held-lock interval.

<details><summary>Show answer</summary>

Use a short transaction to reserve or create a pending operation and durable outbox record, commit, call the provider outside the transaction, then record the result in another short idempotent transaction. Exact workflow depends on whether reservation or payment authorization comes first.
</details>

## 5. Reduce An N+1 Endpoint

The app loads 50 customers, then runs one orders query per customer. Suggest a bounded replacement.

**Expected result:** A batched query or join fetches related rows; preserve expected cardinality.

<details><summary>Show answer</summary>

Fetch orders for the 50 customer IDs in one batched `WHERE customer_id IN (...)` query, or use a join if the result grain is appropriate. Group child rows by customer in the application and avoid multiplying totals through additional joins.
</details>

## 6. Make A Payment Retry Safe

A client times out after the server may have committed the charge request. How should duplicate requests be handled?

**Expected result:** Unique idempotency key stored with operation and checked on retry.

<details><summary>Show answer</summary>

Require a client/request idempotency key, store it under a unique constraint with the operation result, and return the prior result for a duplicate key. This avoids applying the side effect twice after an ambiguous timeout.
</details>

## 7. Use A Prepared Value

Write a prepared query that selects an order by ID and status.

**Expected result:** Both user-supplied values use markers.

<details><summary>Show answer</summary>

```sql
SELECT order_id,amount FROM orders WHERE order_id=? AND status=?;
```
Bind both values through the driver. Do not interpolate them into the SQL text.
</details>

## 8. Insert Idempotently

An API records one webhook per provider event ID; duplicate IDs should not create a second row. Propose the database rule and behavior.

**Expected result:** UNIQUE provider/event ID and an explicit duplicate response/upsert policy.

<details><summary>Show answer</summary>

```sql
UNIQUE KEY uq_provider_event(provider_id,event_id)
```
On duplicate, return or inspect the existing record. Use ON DUPLICATE KEY UPDATE only if updating specified fields is the intended duplicate behavior; avoid changing unrelated state.
</details>

## 9. Diagnose A Pooled Connection Leak

The pool runs out of connections after exceptions. What cleanup must every path perform?

**Expected result:** Close/return the connection and commit or rollback transaction state in a finally/managed scope.

<details><summary>Show answer</summary>

Use the driver's context/transaction management so all success and error paths return the connection and resolve any open transaction. Reset session state when required by the pool/driver.
</details>

## 10. Check Upsert Semantics

What must be true before using `INSERT ... ON DUPLICATE KEY UPDATE` for a deduplicated record?

**Expected result:** A relevant PRIMARY/UNIQUE key must identify duplicates; update clause must preserve business rules.

<details><summary>Show answer</summary>

The table needs a primary/unique key whose conflict represents the duplicate business entity. The update clause must explicitly list intended fields and be safe on repeated requests; validate other constraints and side effects.
</details>

## 11. Interview: Prepared Statements

Explain how prepared statements reduce injection risk and their limitation.

**Expected result:** Separate values from SQL code, but identifiers need allowlisting.

<details><summary>Show answer</summary>

The SQL statement is parsed separately from bound values, so user data is treated as data rather than executable syntax. Parameters cannot bind identifiers or keywords; dynamic SQL structure must come from a strict allowlist.
</details>

## 12. Interview: N+1 Queries

Define the N+1 problem and one trade-off when fixing it with joins.

**Expected result:** Explain per-row extra query count and join cardinality concerns.

<details><summary>Show answer</summary>

N+1 is one query to load a collection plus one additional query for each of N records. A join or batch fetch can reduce round trips, but a one-to-many join repeats parent data and can inflate aggregates, so shape the result intentionally.
</details>
