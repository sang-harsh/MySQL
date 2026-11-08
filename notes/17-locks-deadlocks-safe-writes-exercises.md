# Locks, Deadlocks, And Safe Writes: Exercises

[Notes](17-locks-deadlocks-safe-writes.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 SQL/concurrency timelines, and 2 interview questions. Assume InnoDB. Timelines name session ordering and isolation level; outcomes depend on the stated order.

## 1. Reserve The Last Item

Stock is 1. Two requests each need 1. Recommend one atomic SQL update and how to interpret it.

**Expected result:** Exactly one update changes a row; the other changes zero after waiting if necessary.

<details><summary>Show answer</summary>

```sql
UPDATE inventory SET available=available-1
WHERE product_id=42 AND available>=1;
```
Check affected rows. InnoDB serializes conflicting updates on the row, so only one request can decrement the last unit successfully.
</details>

## 2. Read Then Update Safely

A workflow must inspect a row and then make a decision based on its current status. What read can reserve it until commit?

**Expected result:** SELECT FOR UPDATE inside a short transaction.

<details><summary>Show answer</summary>

```sql
START TRANSACTION;
SELECT status FROM jobs WHERE job_id=42 FOR UPDATE;
-- validate current status, update, then COMMIT
```
The locking read holds the row lock until the transaction ends. Use a selective indexed key and rollback if validation fails.
</details>

## 3. Add Optimistic Versioning

An API edits a document only if no other request changed it. Describe the version check.

**Expected result:** Update with ID and expected version, incrementing version; zero rows means conflict.

<details><summary>Show answer</summary>

```sql
UPDATE documents SET body='new text',version=version+1
WHERE document_id=42 AND version=7;
```
If no row changes, the document was removed or its version changed; return a conflict and let the caller reload.
</details>

## 4. Deadlock Timeline

Session A (REPEATABLE READ) updates row 1 then requests row 2. Session B at the same level updates row 2 then requests row 1. What can happen?

**Expected result:** A wait cycle forms; InnoDB detects the deadlock and rolls back one victim.

<details><summary>Show answer</summary>

A holds row 1 and waits for row 2; B holds row 2 and waits for row 1. InnoDB detects the cycle, chooses a victim, and returns a deadlock error. The application should retry the whole idempotent transaction with bounded backoff.
</details>

## 5. Reduce Deadlocks In Transfers

Transfers touch two account rows. What simple ordering rule can reduce deadlock risk?

**Expected result:** Lock/update account IDs in a consistent ascending order.

<details><summary>Show answer</summary>

Have every transfer acquire rows in a consistent key order, such as lower account ID then higher account ID, and keep the transaction short. This reduces cycles but deadlock handling is still required.
</details>

## 6. Choose SKIP LOCKED For Work

Two workers claim independent queue jobs. One job is locked by worker A. What does worker B gain from SKIP LOCKED, and what does it not guarantee?

**Expected result:** B can claim other unlocked work; skipped rows still exist and are omitted temporarily.

<details><summary>Show answer</summary>

A locking query with SKIP LOCKED can return other unlocked jobs without waiting. It does not provide a complete result set or guarantee when the skipped job will be retried; the queue needs recovery/lease rules.
</details>

## 7. Write A Conditional Stock Update

Decrease stock by 3 only if at least 3 are available.

**Expected result:** One update with a stock predicate and affected-row check.

<details><summary>Show answer</summary>

```sql
UPDATE inventory SET available=available-3
WHERE product_id=42 AND available>=3;
```
Check affected rows before inserting related order lines.
</details>

## 8. Write A Locking Read

Lock one account row before checking its balance in a transaction.

**Expected result:** SELECT FOR UPDATE by primary key after START TRANSACTION.

<details><summary>Show answer</summary>

```sql
START TRANSACTION;
SELECT balance FROM accounts WHERE account_id=10 FOR UPDATE;
```
Commit or roll back promptly after the dependent work.
</details>

## 9. Debug A Deadlock Retry

Why is retrying only the final UPDATE after InnoDB rolls back the transaction unsafe?

**Expected result:** The entire transaction may have been rolled back; repeat the full business unit safely.

<details><summary>Show answer</summary>

InnoDB rolls back a deadlock victim transaction, so earlier statements in that transaction are not committed. Retry the full transaction with idempotent external effects and bounded attempts.
</details>

## 10. Identify Lock Footprint Factors

Why can adding a missing selective index change contention?

**Expected result:** The plan may examine/lock fewer records or ranges, though exact locks depend on isolation and access path.

<details><summary>Show answer</summary>

A selective indexed predicate can reduce rows examined and the associated lock footprint. InnoDB's record/gap/next-key locks depend on index access and isolation, so inspect the actual plan and behavior rather than assuming a fixed lock count.
</details>

## 11. Interview: Pessimistic Or Optimistic?

Contrast FOR UPDATE with a version-column update.

**Expected result:** Cover early locks/waiting versus conflict detection on write.

<details><summary>Show answer</summary>

FOR UPDATE pessimistically locks rows while a transaction decides and writes, potentially making others wait. Optimistic version checks allow concurrent reads and detect a conflict when the update finds an unexpected version; the application then handles retry or user conflict.
</details>

## 12. Interview: Deadlock Handling

What should the application do after a deadlock error?

**Expected result:** Retry the whole safe transaction with a bounded policy; reduce causes but do not assume none recur.

<details><summary>Show answer</summary>

Treat the transaction as rolled back, then retry the complete operation with bounded attempts and backoff only if it is idempotent. Keep transactions short and acquire rows in consistent order to reduce recurrence.
</details>
