# Transactions And ACID: Exercises

[Notes](15-transactions-acid.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 SQL/transaction tasks, and 2 interview questions. Use isolated InnoDB tables. Concurrency tasks identify each session, isolation level, and statement order; do not execute against application data.

## 1. Place An Order And Reserve Stock

An order row and inventory decrement must succeed together. Describe the transaction and failure behavior.

**Expected result:** Reserve conditionally, verify one row changed, insert the order, then commit; otherwise rollback.

<details><summary>Show answer</summary>

```sql
START TRANSACTION;
UPDATE inventory SET available=available-1 WHERE product_id=42 AND available>0;
-- If ROW_COUNT() is not 1: ROLLBACK; otherwise insert order, then COMMIT.
```
The inventory check and order insert are atomic only when both execute on the same InnoDB connection and transaction.
</details>

## 2. Transfer Funds

Transfer 500.00 from account 1 to account 2. What must be atomic?

**Expected result:** Debit and credit commit together or neither does; insufficient balance must not produce a negative debit.

<details><summary>Show answer</summary>

Start a transaction, conditionally debit account 1 with `balance >= 500`, verify one row changed, credit account 2, then commit. Roll back on any failure. A ledger and idempotency key may be required for a real payment system.
</details>

## 3. Handle A Failed Insert

A transaction updates a row then violates a unique key on a later insert. What should the application do?

**Expected result:** Roll back the transaction and report/retry only under an explicit policy.

<details><summary>Show answer</summary>

Issue ROLLBACK on the same connection after the error unless the application's transaction framework already marks it rollback-only. Do not commit partial work; only retry when the operation is safe to repeat.
</details>

## 4. Keep A Transaction Short

A service calls a slow payment provider between START TRANSACTION and COMMIT. What is the risk and safer outline?

**Expected result:** Long-held locks increase contention; avoid external calls while the transaction is open.

<details><summary>Show answer</summary>

The network call lengthens lock duration and increases timeout/deadlock risk. Use an application workflow such as a pending state/outbox, make the external call outside the database transaction, then record its result in a short transaction with idempotent transitions.
</details>

## 5. Reuse A Pooled Connection

An application starts a transaction on one connection but runs the insert on another pooled connection. Is the work atomic?

**Expected result:** No; transaction state belongs to one session/connection.

<details><summary>Show answer</summary>

No. All statements must use the same physical database session until commit or rollback. The pool should return the connection only after transaction cleanup.
</details>

## 6. Deal With Unknown Commit Outcome

A network connection drops while COMMIT is being sent. Can the client assume rollback?

**Expected result:** No; commit may have succeeded. Check by idempotency key or authoritative state before retrying.

<details><summary>Show answer</summary>

The outcome is ambiguous to the client: the server may have committed before the connection failed. Make requests idempotent, then query the transaction/request record to determine state instead of blindly applying the operation again.
</details>

## 7. Use A Savepoint

Show SQL to roll back only the optional audit insert while keeping an earlier update eligible to commit.

**Expected result:** Roll back to a named savepoint and commit the remaining work.

<details><summary>Show answer</summary>

```sql
START TRANSACTION;
UPDATE accounts SET status='active' WHERE account_id=10;
SAVEPOINT before_audit;
INSERT INTO audit_log(account_id,event_name) VALUES(10,'activated');
ROLLBACK TO SAVEPOINT before_audit;
COMMIT;
```
This assumes the insert error handling permits continuing. Savepoints do not persist data until the outer COMMIT.
</details>

## 8. Check A Conditional Update

Write an atomic stock decrement that cannot take available below zero.

**Expected result:** The update affects one row only when enough stock remains.

<details><summary>Show answer</summary>

```sql
UPDATE inventory SET available=available-2
WHERE product_id=42 AND available>=2;
```
Check affected rows; zero means unavailable or missing. In application code, bind the product ID and validated positive quantity as prepared-statement parameters.
</details>

## 9. DDL Inside A Transaction

What happens to rollback expectations if `ALTER TABLE` is issued after `START TRANSACTION`?

**Expected result:** DDL generally causes implicit commits; a later ROLLBACK does not undo the schema change.

<details><summary>Show answer</summary>

MySQL DDL commonly causes an implicit commit before/after execution. Atomic DDL in supported MySQL 8.0+ operations is crash-safe behavior, not user transaction rollback. Separate migrations from business-data transactions.
</details>

## 10. Two-Session Inventory Race

Under InnoDB REPEATABLE READ, Session A and B both run `UPDATE inventory SET available=available-1 WHERE product_id=1 AND available>0` when available=1, in that order. What happens?

**Expected result:** A decrements to zero and commits; B waits for the row lock, re-evaluates the condition, and affects zero rows.

<details><summary>Show answer</summary>

Session A executes the conditional UPDATE and commits. Session B's UPDATE waits on the same row; after A commits, B checks the current row and its predicate is false, so it changes no row. The application must check affected rows. This assumes InnoDB and the stated statement ordering.
</details>

## 11. Interview: Explain ACID

Explain ACID with an order/payment example.

**Expected result:** Define all four properties and relate them to a practical write.

<details><summary>Show answer</summary>

Atomicity keeps required order and payment-state changes together. Consistency preserves constraints and business invariants. Isolation controls visibility/interference between concurrent work. Durability means a committed transaction survives supported failures.
</details>

## 12. Interview: Why Same Connection?

Why must a transaction's statements use the same connection?

**Expected result:** State that transaction state is session-scoped and pooled connections are independent.

<details><summary>Show answer</summary>

The server tracks an open transaction per session. A second connection has a separate transaction context and cannot see or commit the first session's uncommitted work, so all related statements must remain on one connection.
</details>
