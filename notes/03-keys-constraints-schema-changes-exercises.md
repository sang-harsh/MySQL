# Keys, Constraints, And Schema Changes: Exercises

[Notes](03-keys-constraints-schema-changes.md) | [Topic index](../start.md)

12 questions: 6 production scenarios, 4 SQL/DDL tasks, and 2 interview questions. Examples target MySQL 8.4 with InnoDB. Run DDL only in a fresh practice schema.

## 1. Enforce Unique Membership

An account can contain each user only once, and each user must belong to an existing account and user record. What key/constraints should the membership table use?

**Expected result:** Duplicate account-user pairs are rejected and missing parent rows are rejected.

<details><summary>Show answer</summary>

```sql
CREATE TABLE memberships (
 account_id BIGINT NOT NULL,
 user_id BIGINT NOT NULL,
 PRIMARY KEY(account_id,user_id),
 FOREIGN KEY(account_id) REFERENCES accounts(account_id),
 FOREIGN KEY(user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
```
The composite key enforces pair uniqueness; the foreign keys enforce both relationships. Parent tables must already exist with compatible indexed key types.
</details>

## 2. Optional External Reference

A vendor reference may be absent, but when present it must not be duplicated. Define the column constraint and explain NULL behavior.

**Expected result:** Multiple rows may omit the reference; non-NULL duplicate references are rejected.

<details><summary>Show answer</summary>

```sql
vendor_reference VARCHAR(80) NULL UNIQUE
```
MySQL unique indexes permit multiple NULL values. Add NOT NULL only if every row must have a reference.
</details>

## 3. Restrict Payment Statuses

Create a payment table with a required status limited to pending, captured, or refunded.

**Expected result:** Invalid values are rejected on MySQL 8.0.16 and later.

<details><summary>Show answer</summary>

```sql
CREATE TABLE payments (
 payment_id BIGINT PRIMARY KEY AUTO_INCREMENT,
 status VARCHAR(16) NOT NULL,
 CHECK(status IN ('pending','captured','refunded'))
) ENGINE=InnoDB;
```
MySQL began enforcing CHECK constraints in 8.0.16; older releases parsed but did not enforce them.
</details>

## 4. Add A Required Column Safely

A populated table needs a non-NULL `created_at` value. Describe a cautious migration sequence.

**Expected result:** Existing rows remain valid and application versions can coexist during deployment.

<details><summary>Show answer</summary>

Add a nullable column or a supported default first, backfill in bounded batches if needed, deploy code that writes it, verify no NULLs, then apply NOT NULL. Exact online behavior depends on table and server version; test on a production-like copy.
</details>

## 5. Delete An Account With Children

Orders reference customers. The business requires orders to remain for audit, so how should customer deletion behave?

**Expected result:** The database must not silently delete the orders.

<details><summary>Show answer</summary>

Use the default restrictive foreign-key behavior (or explicitly `ON DELETE RESTRICT`) and reject customer deletion while orders reference it. Use a separate soft-delete/archival policy if the customer must be hidden but history retained.
</details>

## 6. Choose Delete, Truncate, Or Drop

You need to remove old test rows matching a date, empty a disposable staging table, or remove that table entirely. Match each operation.

**Expected result:** Selective rows use DELETE; all rows use TRUNCATE; table removal uses DROP.

<details><summary>Show answer</summary>

```sql
DELETE FROM staging_events WHERE created_at < '2026-01-01';
TRUNCATE TABLE disposable_stage;
DROP TABLE disposable_stage;
```
Only run the last two against the intended disposable object. TRUNCATE and DROP cause implicit commits and are not ordinary rollback-able row deletes.
</details>

## 7. Make An Idempotency Key Unique

An API request has a required idempotency key unique within a client. Define the relevant table key.

**Expected result:** The same key may be used by different clients but not twice by one client.

<details><summary>Show answer</summary>

```sql
CREATE TABLE request_log (
 request_id BIGINT PRIMARY KEY AUTO_INCREMENT,
 client_id BIGINT NOT NULL,
 idempotency_key VARCHAR(100) NOT NULL,
 UNIQUE KEY uq_client_request(client_id,idempotency_key)
) ENGINE=InnoDB;
```
The composite unique key matches the business scope; both columns are NOT NULL to avoid NULL uniqueness surprises.
</details>

## 8. Diagnose AUTO_INCREMENT Gaps

After a failed insert and a deleted row, IDs are 10, 12, and 15. Is the table corrupt, and should IDs be renumbered?

**Expected result:** No; gaps are normal and identifiers should not be renumbered for presentation.

<details><summary>Show answer</summary>

No. AUTO_INCREMENT is designed to provide generated identifiers, not a gap-free business sequence. Use a separate controlled sequence if regulations require gap accounting.
</details>

## 9. Debug A Nullable Unique Column

Why does a UNIQUE constraint allow two rows with NULL in the constrained column?

**Expected result:** Explain NULL uniqueness and how to require exactly one non-NULL value.

<details><summary>Show answer</summary>

MySQL treats NULL values as distinct for UNIQUE-index purposes, so multiple NULL entries are allowed. Declare the column NOT NULL as well as UNIQUE when every record must have a value.
</details>

## 10. Review A Cascading Delete

A team proposes `ON DELETE CASCADE` from customers to orders. What must be checked before approval?

**Expected result:** Address business retention, deletion scope, and testability.

<details><summary>Show answer</summary>

Confirm that deleting a customer is truly allowed to erase all dependent order history, estimate the number of affected rows, and test transaction/runtime behavior. If history must remain, RESTRICT or soft deletion is safer.
</details>

## 11. Interview: Primary And Foreign Keys

Explain the distinct jobs of primary and foreign keys.

**Expected result:** Cover row identity, uniqueness/non-NULL, and referential integrity.

<details><summary>Show answer</summary>

A primary key uniquely identifies each row and cannot be NULL. A foreign key constrains a child value to reference an existing parent key, protecting relationships from orphan records.
</details>

## 12. Interview: DDL And Rollback

Can you wrap TRUNCATE or ALTER TABLE in a transaction and roll it back?

**Expected result:** Explain implicit commit and atomic DDL distinction.

<details><summary>Show answer</summary>

No, do not rely on transaction rollback to undo these DDL statements because they cause implicit commits. MySQL 8.0 atomic DDL protects supported operations against partial crash effects, but it does not make the DDL a user-rollback-able transaction.
</details>
