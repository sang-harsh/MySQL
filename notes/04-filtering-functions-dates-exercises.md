# Filtering, Functions, And Dates: Exercises

[Notes](04-filtering-functions-dates.md) | [Topic index](../start.md)

12 questions: 7 filter/query tasks, 3 debugging/edge cases, and 2 interview questions. Dates in the fixture are UTC DATETIME values. Order outputs explicitly; all comparisons are case-insensitive under the sample default collation unless specified otherwise.

## Setup

```sql
CREATE TABLE filter_events (
 event_id INT PRIMARY KEY,
 title VARCHAR(60) NOT NULL,
 amount DECIMAL(8,2) NOT NULL,
 occurred_at DATETIME NOT NULL
);
INSERT INTO filter_events VALUES
 (1,'Blue Sale',10,'2026-08-03 00:00:00.000000'),
 (2,'blue sale',20,'2026-08-03 23:59:59.500000'),
 (3,'Launch_1',30,'2026-08-04 00:00:00.000000');
```

## 1. Find Titles Starting With Blue

Return events whose title starts with `Blue`, ordered by event ID.

**Expected result:** Events 1 and 2 under the fixture's case-insensitive collation.

<details><summary>Show answer</summary>

```sql
SELECT event_id,title FROM filter_events WHERE title LIKE 'Blue%' ORDER BY event_id;
```
The trailing wildcard allows a prefix pattern; case behavior comes from collation.
</details>

## 2. Find A Literal Underscore

Return titles containing a literal underscore.

**Expected result:** Event 3 only.

<details><summary>Show answer</summary>

```sql
SELECT event_id,title FROM filter_events WHERE title LIKE '%!_%' ESCAPE '!' ORDER BY event_id;
```
`_` is a one-character wildcard unless escaped.
</details>

## 3. Filter One UTC Day

Return all events on August 3, 2026.

**Expected result:** Events 1 and 2, including the fractional-second event.

<details><summary>Show answer</summary>

```sql
SELECT event_id FROM filter_events
WHERE occurred_at>='2026-08-03 00:00:00' AND occurred_at<'2026-08-04 00:00:00'
ORDER BY event_id;
```
The half-open range includes every time on the day.
</details>

## 4. Filter A Calendar Month

Return events in August 2026.

**Expected result:** Events 1, 2, and 3.

<details><summary>Show answer</summary>

```sql
SELECT event_id FROM filter_events
WHERE occurred_at>='2026-08-01' AND occurred_at<'2026-09-01'
ORDER BY event_id;
```
The exclusive next-month boundary avoids precision issues.
</details>

## 5. Round Amounts For Display

Return each event amount rounded to the nearest whole unit.

**Expected result:** 10, 20, and 30.

<details><summary>Show answer</summary>

```sql
SELECT event_id,ROUND(amount,0) AS rounded_amount FROM filter_events ORDER BY event_id;
```
Display rounding should not replace the exact stored amount.
</details>

## 6. Find Titles Containing “sale”

Return title matches containing `sale` anywhere.

**Expected result:** Events 1 and 2 under the fixture collation.

<details><summary>Show answer</summary>

```sql
SELECT event_id FROM filter_events WHERE title LIKE '%sale%' ORDER BY event_id;
```
The leading wildcard may require scanning; use it for correctness, then evaluate search needs separately.
</details>

## 7. Return Events Above The Average

Return events whose amount is strictly greater than the average amount.

**Expected result:** Event 3 only.

<details><summary>Show answer</summary>

```sql
SELECT event_id,amount FROM filter_events
WHERE amount>(SELECT AVG(amount) FROM filter_events) ORDER BY event_id;
```
The average is 20.00, so only 30 is strictly greater.
</details>

## 8. Debug An Inclusive Upper Boundary

Why might `BETWEEN '2026-08-03 00:00:00' AND '2026-08-03 23:59:59'` miss an event at 23:59:59.5? Correct it.

**Expected result:** Use an exclusive next-day boundary; include event 2.

<details><summary>Show answer</summary>

```sql
WHERE occurred_at>='2026-08-03 00:00:00' AND occurred_at<'2026-08-04 00:00:00'
```
Fractional-second values can be later than 23:59:59 but still belong to that date.
</details>

## 9. Debug YEAR On An Indexed Column

Rewrite `WHERE YEAR(occurred_at)=2026` as a range.

**Expected result:** Include all 2026 events and leave the column unwrapped.

<details><summary>Show answer</summary>

```sql
WHERE occurred_at>='2026-01-01 00:00:00' AND occurred_at<'2027-01-01 00:00:00'
```
A plain range is more amenable to an index range scan.
</details>

## 10. Explain A Leading Wildcard

Does `title LIKE '%sale'` normally use a B-tree index as a prefix search?

**Expected result:** No; the first character is unknown, so a normal index cannot seek by a fixed prefix.

<details><summary>Show answer</summary>

A B-tree prefix lookup needs a known beginning of the value. A leading wildcard usually requires examining many entries; consider full-text or another search design only if workload warrants it.
</details>

## 11. Interview: Half-Open Date Ranges

Explain why `>= start AND < next_start` is useful for date filters.

**Expected result:** Cover precision, boundaries, and index-friendly predicate form.

<details><summary>Show answer</summary>

A half-open range includes every instant from the period start but excludes the next period exactly, so fractional seconds are handled without guessing a final timestamp. It also keeps the indexed column unwrapped.
</details>

## 12. Interview: Time Zones And Business Days

How should an application query a local business day when timestamps are stored in UTC?

**Expected result:** Convert the local period boundaries to UTC, respecting the named zone and DST.

<details><summary>Show answer</summary>

Calculate the start of the requested calendar day and the next day in the business time zone, convert both instants to UTC, then query the half-open UTC range. Do not assume every local day is exactly 24 hours around daylight-saving transitions.
</details>
