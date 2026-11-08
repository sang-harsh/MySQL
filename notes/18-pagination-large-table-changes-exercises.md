# Pagination And Large-Table Changes: Exercises

[Notes](18-pagination-large-table-changes.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 SQL/operations tasks, and 2 interview questions. Use stable ordering and primary keys. Do not execute bulk changes against application data.

## 1. Paginate A Small Admin List

The admin needs numbered pages for 200 records. Which pagination approach is reasonable?

**Expected result:** LIMIT/OFFSET is reasonable with deterministic ordering for this modest list.

<details><summary>Show answer</summary>

```sql
SELECT item_id,name FROM items ORDER BY name,item_id LIMIT 20 OFFSET 40;
```
Use a unique tie-breaker. Offset pagination is acceptable for small/modest results and page-number navigation.
</details>

## 2. Improve A Deep Feed Page

A timeline loads its next page after `(created_at, event_id)` in descending order. Write the keyset predicate and ordering.

**Expected result:** Rows strictly after the cursor in descending lexicographic order, limited to 50.

<details><summary>Show answer</summary>

```sql
SELECT event_id,created_at FROM events
WHERE created_at<'2026-10-10 12:00:00'
   OR (created_at='2026-10-10 12:00:00' AND event_id<900)
ORDER BY created_at DESC,event_id DESC LIMIT 50;
```
The cursor values come from the final row of the previous page. Index ordering should match the access pattern.
</details>

## 3. Delete Old Events In Batches

A cleanup job must remove old event rows with limited lock duration. Describe a resumable batch pattern.

**Expected result:** Select/delete bounded IDs, commit each batch, and persist a cursor or progress state.

<details><summary>Show answer</summary>

```sql
DELETE FROM events WHERE event_id IN (
 SELECT event_id FROM (SELECT event_id FROM events
  WHERE created_at<'2025-01-01' ORDER BY event_id LIMIT 500) AS batch
);
```
Run each batch in a transaction, commit, monitor load, and continue until no rows remain. Use a durable checkpoint if the job must resume after interruption.
</details>

## 4. Avoid Reprocessing Rows

A batch update restarts after a crash. What should the job persist or use to resume safely?

**Expected result:** A deterministic cursor/checkpoint or an idempotent processed marker, committed consistently with the batch.

<details><summary>Show answer</summary>

Record the last processed primary key in the same transaction as the batch, or select rows by an idempotent status marker. On restart, continue after the committed cursor; ensure updates can be retried without duplicate side effects.
</details>

## 5. Choose Pagination For A Product Catalog

The product needs direct jump to page numbers and only a few thousand rows. Which approach and caveat?

**Expected result:** OFFSET can be simpler; use deterministic order and be aware of shifts.

<details><summary>Show answer</summary>

Use LIMIT/OFFSET with a stable unique order. Insertions between requests can shift pages; for much larger catalogs or next-only navigation, consider keyset pagination.
</details>

## 6. Review An Online Schema Change

A migration claims to be “online.” What operational risks remain?

**Expected result:** Resource use, metadata-lock waits, replication lag, and operation/version compatibility.

<details><summary>Show answer</summary>

Online DDL can still consume I/O/CPU, wait for metadata locks, and affect replicas; support depends on the exact operation and server version. Test on representative size and define monitoring/rollback or forward-fix steps.
</details>

## 7. Write The First Offset Page

Return the first 25 newest events, with a unique tie-breaker.

**Expected result:** Ordered newest timestamp first and event ID descending, limited to 25.

<details><summary>Show answer</summary>

```sql
SELECT event_id,created_at FROM events
ORDER BY created_at DESC,event_id DESC LIMIT 25 OFFSET 0;
```
Explicit ordering makes the page stable for a static dataset.
</details>

## 8. Add A Batch Limit

Write a SELECT to preview up to 100 eligible rows before processing, in ascending primary-key order.

**Expected result:** An explicitly ordered bounded selection.

<details><summary>Show answer</summary>

```sql
SELECT event_id FROM events WHERE archived=0 ORDER BY event_id LIMIT 100;
```
Preview the IDs and ensure the processing step uses the same eligibility condition.
</details>

## 9. Debug Non-Deterministic Pagination

Why can `ORDER BY created_at LIMIT 50 OFFSET 50` repeat/skip tied events across pages? Fix it.

**Expected result:** Timestamp ties need a unique tie-breaker.

<details><summary>Show answer</summary>

```sql
ORDER BY created_at,event_id LIMIT 50 OFFSET 50
```
If data changes between requests, offset pages may still shift; keyset pagination is preferable for a stable feed continuation.
</details>

## 10. Identify Keyset Limitation

Can keyset pagination jump directly to an arbitrary page number without locating a cursor?

**Expected result:** Not naturally; it is cursor-oriented.

<details><summary>Show answer</summary>

No. Keyset pagination efficiently continues from a known cursor but does not naturally map a page number to a position. It is best for sequential browsing, not arbitrary page jumps.
</details>

## 11. Interview: OFFSET Versus Keyset

Compare their main strengths and limitations.

**Expected result:** Cover page-number simplicity, deep offset work, cursor efficiency, and jumping limitation.

<details><summary>Show answer</summary>

OFFSET is straightforward and supports numbered pages but can require skipping many rows and pages can shift during concurrent changes. Keyset seeks from the last stable ordering key and suits large feeds, but does not naturally jump to arbitrary page numbers.
</details>

## 12. Interview: Why Batch Large Changes?

Why process a large update/delete in bounded batches?

**Expected result:** Mention lock duration, log/replication pressure, monitoring, and resumability.

<details><summary>Show answer</summary>

Bounded transactions limit lock duration and resource spikes, making progress easier to monitor and pause. A stable cursor/checkpoint lets the job resume safely, while idempotent updates make retries manageable.
</details>
