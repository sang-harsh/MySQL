# Data Types, NULL, And Expressions: Exercises

[Notes](02-data-types-null-expressions.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 SQL/type tasks, and 2 interview questions. Use MySQL 8.4 defaults unless the question names a session setting. Monetary values are INR; UTC handling is explicit.

## 1. Store Product Prices

Choose a type for product prices with at most two fractional digits and a maximum below 100 million.

**Expected result:** An exact DECIMAL with sufficient precision and scale.

<details><summary>Show answer</summary>

```sql
price DECIMAL(10,2) NOT NULL
```
DECIMAL(10,2) allows eight integer digits and two fractional digits. Choose precision from actual business limits.
</details>

## 2. Store An Event Instant

An audit event is an absolute instant and the application consistently exchanges UTC. Choose between DATETIME and TIMESTAMP and state the handling rule.

**Expected result:** Either can be made correct with a consistent rule; TIMESTAMP performs session-zone conversion and has a range limit.

<details><summary>Show answer</summary>

Use TIMESTAMP when its supported range is sufficient and session time zones are controlled, or use DATETIME with an explicit UTC convention. Always configure connections and test conversions at boundaries.
</details>

## 3. Find Rows Missing A Delivery Time

Write a query that returns undelivered order IDs.

**Expected result:** Rows whose delivered_at is NULL.

<details><summary>Show answer</summary>

```sql
SELECT order_id FROM orders WHERE delivered_at IS NULL ORDER BY order_id;
```
NULL must be checked with IS NULL, not equality.
</details>

## 4. Show A Fallback Time

Return delivered_at when known, otherwise promised_at.

**Expected result:** The first non-NULL timestamp per row.

<details><summary>Show answer</summary>

```sql
SELECT order_id,COALESCE(delivered_at,promised_at) AS effective_time FROM orders;
```
COALESCE returns the first non-NULL expression; compatible temporal types are expected.
</details>

## 5. Count Known Emails

A table has 10 users, 2 with NULL email. Give counts for all users and known emails.

**Expected result:** COUNT(*) is 10 and COUNT(email) is 8.

<details><summary>Show answer</summary>

```sql
SELECT COUNT(*) AS all_users,COUNT(email) AS known_emails FROM users;
```
COUNT(column) excludes NULL values.
</details>

## 6. Restrict A Boolean Flag

A flag must be exactly 0 or 1. Define a MySQL column rule.

**Expected result:** TINYINT with NOT NULL and an enforced CHECK constraint on MySQL 8.0.16+.

<details><summary>Show answer</summary>

```sql
is_active TINYINT NOT NULL CHECK(is_active IN (0,1))
```
MySQL's BOOLEAN alias alone does not enforce only two values. CHECK constraints are enforced from 8.0.16.
</details>

## 7. Classify Amounts

Return order ID and `high` for amounts at least 1000.00, otherwise `regular`.

**Expected result:** Each row receives exactly one label based on its amount.

<details><summary>Show answer</summary>

```sql
SELECT order_id,
 CASE WHEN amount>=1000.00 THEN 'high' ELSE 'regular' END AS band
FROM orders ORDER BY order_id;
```
Use DECIMAL for exact monetary comparisons.
</details>

## 8. Debug NULL Equality

Why does `WHERE cancelled_at = NULL` return no rows? Correct it.

**Expected result:** Use IS NULL.

<details><summary>Show answer</summary>

```sql
WHERE cancelled_at IS NULL
```
Ordinary comparisons with NULL produce UNKNOWN, which WHERE does not retain.
</details>

## 9. Debug Floating-Point Money

A report accumulates thousands of FLOAT prices and shows tiny unexpected differences. Recommend a type and caveat.

**Expected result:** Use DECIMAL for exact stored monetary values and define rounding rules.

<details><summary>Show answer</summary>

Use DECIMAL with precision/scale sized for the business range, and define when rounding occurs (line, tax, or invoice total). DECIMAL does not choose the correct accounting policy by itself.
</details>

## 10. Compare A Half-Open Time Range

Write a predicate for all UTC events on 2026-07-14, assuming the column stores UTC DATETIME values.

**Expected result:** Include midnight on July 14 and exclude midnight July 15.

<details><summary>Show answer</summary>

```sql
WHERE event_time >= '2026-07-14 00:00:00'
  AND event_time <  '2026-07-15 00:00:00'
```
The half-open range avoids fractional-second boundary errors and leaves the column unwrapped.
</details>

## 11. Interview: NULL Semantics

What does `NULL = NULL` evaluate to, and how should NULL be tested?

**Expected result:** State UNKNOWN and use IS NULL/IS NOT NULL.

<details><summary>Show answer</summary>

`NULL = NULL` evaluates to UNKNOWN because NULL represents an absent/unknown value. Use `IS NULL` or `IS NOT NULL`; COALESCE is for intentional fallback values, not comparison.
</details>

## 12. Interview: DATETIME Versus TIMESTAMP

Explain their practical difference in MySQL.

**Expected result:** Cover automatic session time-zone conversion and explicit application conventions.

<details><summary>Show answer</summary>

DATETIME stores the supplied date/time fields without automatic time-zone conversion. TIMESTAMP converts from the session time zone to UTC for storage and back on retrieval, with a more limited range. Use a consistent UTC/session policy for absolute instants.
</details>
