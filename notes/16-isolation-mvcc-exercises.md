# Isolation Levels And MVCC: Exercises

[Notes](16-isolation-mvcc.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 transaction timelines/diagnostics, and 2 interview questions. Each timeline names sessions, statement order, isolation level, and expected result. Assume InnoDB and MySQL 8.4 unless stated.

## 1. Read A Consistent Snapshot

Session A at REPEATABLE READ begins and reads balance 100. Session B updates to 90 and commits. A performs an ordinary consistent SELECT again. What value does A generally see?

**Expected result:** A continues to see 100 in its transaction snapshot.

<details><summary>Show answer</summary>

A's ordinary consistent reads under InnoDB REPEATABLE READ generally share the same snapshot, so it sees 100 again. A locking read is not the same snapshot-read behavior.
</details>

## 2. Compare READ COMMITTED Reads

Session A at READ COMMITTED reads balance 100. Session B changes it to 90 and commits. A repeats an ordinary SELECT. What does A see?

**Expected result:** The second read sees 90 because it gets a fresh committed snapshot.

<details><summary>Show answer</summary>

At READ COMMITTED, each consistent read gets a fresh snapshot. After B commits, A's next read can see 90.
</details>

## 3. Avoid A Lost Update

Two requests read stock=1, each calculates 0, and both write 0. Recommend a safer operation.

**Expected result:** Atomic conditional update or locking/version check ensures only one succeeds.

<details><summary>Show answer</summary>

```sql
UPDATE inventory SET stock=stock-1 WHERE product_id=5 AND stock>=1;
```
Check affected rows. The update is atomic at the row and the predicate prevents decrementing below zero.
</details>

## 4. Lock Before Reserving Stock

Session A and B run under REPEATABLE READ. A starts a transaction and selects product 5 `FOR UPDATE`; B then selects the same row `FOR UPDATE`. What happens before A commits?

**Expected result:** B waits for A's row lock; after A commits, B proceeds and sees the current row.

<details><summary>Show answer</summary>

Session A's locking read locks the matching current row. Session B's locking read blocks until A commits/rolls back, then obtains the lock and sees the current value. Use a selective indexed predicate and keep the transaction short.
</details>

## 5. Choose Isolation For A Reporting Read

A dashboard can tolerate seeing a recent committed value on each separate query but not uncommitted changes. Which common level fits?

**Expected result:** READ COMMITTED is a typical fit, subject to cross-query consistency requirements.

<details><summary>Show answer</summary>

READ COMMITTED prevents dirty reads and gives each consistent read a fresh snapshot. If multiple statements must represent one stable point in time, use an appropriate transaction/isolation design and consider its trade-offs.
</details>

## 6. Explain A Phantom Conceptually

A transaction queries all orders with amount over 100. Another transaction inserts a qualifying order and commits. What is the standard phantom-read idea?

**Expected result:** A repeated predicate query may return a different set because a matching row was added.

<details><summary>Show answer</summary>

A phantom is a change in the set of rows matching a predicate between reads. Exact InnoDB behavior depends on isolation and whether reads are consistent or locking reads; REPEATABLE READ's snapshot and next-key locking behavior must be distinguished.
</details>

## 7. Set Session Isolation

Show SQL to set the next transaction's isolation level to READ COMMITTED for the current session.

**Expected result:** Use SET TRANSACTION ISOLATION LEVEL before starting the transaction.

<details><summary>Show answer</summary>

```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
START TRANSACTION;
```
Set it before the transaction begins and verify driver/session behavior.
</details>

## 8. Distinguish Consistent And Locking Reads

What is the key difference between ordinary SELECT and SELECT FOR UPDATE in an InnoDB transaction?

**Expected result:** Snapshot consistent read versus current locking read with locks.

<details><summary>Show answer</summary>

An ordinary consistent SELECT reads a snapshot using MVCC and generally does not lock the selected rows. SELECT FOR UPDATE is a current locking read that acquires locks to coordinate subsequent changes.
</details>

## 9. Debug An Isolation Claim

A candidate says “REPEATABLE READ always returns the latest committed row.” Correct the claim.

**Expected result:** Ordinary consistent reads may retain a transaction snapshot; locking reads differ.

<details><summary>Show answer</summary>

Under InnoDB REPEATABLE READ, ordinary consistent reads generally see the transaction's snapshot, not each latest commit. Locking reads such as FOR UPDATE are current reads and acquire locks.
</details>

## 10. Locate The Transaction Boundary

An app starts a transaction on pooled connection A and performs its second SELECT on connection B. Does A's snapshot govern B?

**Expected result:** No; each connection/session has independent transaction and snapshot state.

<details><summary>Show answer</summary>

No. The transaction and its snapshot are session-scoped. All related statements must use the same physical connection until commit or rollback.
</details>

## 11. Interview: Explain MVCC

Explain MVCC in practical application terms.

**Expected result:** Mention row versions/snapshots and concurrent reads/writes without claiming no locks.

<details><summary>Show answer</summary>

MVCC keeps versions of rows so a consistent reader can see a transaction snapshot while another transaction updates data. It reduces read/write blocking in many cases, but writes and locking reads can still block and create conflicts.
</details>

## 12. Interview: Isolation Does Not Replace What?

Why are constraints and atomic updates still important at a chosen isolation level?

**Expected result:** State that isolation does not encode every invariant or prevent every application race.

<details><summary>Show answer</summary>

Isolation governs visibility and concurrent interactions, but business invariants still need constraints and safe write patterns. Unique keys, conditional updates, and explicit locks can be required to prevent duplicate or invalid state.
</details>
