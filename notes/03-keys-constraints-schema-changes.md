# Keys, Constraints, And Schema Changes

[Exercises](03-keys-constraints-schema-changes-exercises.md) | [Topic index](../start.md)

## Interview Answer

Keys identify rows and constraints make invalid states harder to store. A primary key is unique and non-NULL; a foreign key enforces a permitted relationship; a unique key prevents duplicate non-NULL key combinations. I choose constraints from the business rules and treat schema changes as production operations that need a reviewed migration, not ad hoc SQL.

## Key Points

- A single or composite primary key uniquely identifies a row. A composite key enforces uniqueness of the combination; column order matters to indexes and lookup patterns.
- A UNIQUE index allows multiple NULL values in MySQL because NULL is not equal to another NULL. Use NOT NULL if the business key is required.
- InnoDB foreign keys require compatible indexed columns and enforce referenced-row rules. Choose RESTRICT/CASCADE behavior deliberately; cascading deletes can affect many rows.
- `CHECK` constraints are enforced from MySQL 8.0.16. Defaults apply when a value is omitted (or DEFAULT is specified), not generally when NULL is explicitly inserted into a nullable column.
- AUTO_INCREMENT produces generated identifiers, not a gap-free sequence. Rollbacks, deletes, and allocation behavior can leave gaps.
- ALTER TABLE can rebuild or lock data depending on the operation, MySQL version, engine, and table shape. Test migration duration and application compatibility.
- DELETE removes selected rows; TRUNCATE removes all rows and resets AUTO_INCREMENT in typical InnoDB use; DROP removes the table. TRUNCATE and DROP are DDL and cause implicit commits; do not assume they can be rolled back like a DELETE.

## Minimal Example

```sql
CREATE TABLE account_memberships (
  account_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'member',
  PRIMARY KEY (account_id, user_id),
  CHECK (role IN ('owner', 'member'))
) ENGINE=InnoDB;
```

The composite primary key prevents the same user from being added to one account twice. Add foreign keys if the parent tables exist and their lifecycle rules are clear.

## Common Traps

- A unique constraint is not the same as NOT NULL; nullable unique columns can have multiple NULLs.
- A foreign key does not replace indexes for every query; it protects referential integrity.
- AUTO_INCREMENT values are identifiers, not business sequence numbers or evidence of missing rows.
- `TRUNCATE` is not a faster transactional DELETE substitute when row-level rollback or delete triggers matter.

## Likely Follow-Ups

**Primary versus unique key?** A table has one primary key, which is non-NULL; it may have multiple unique constraints, which can allow NULLs.

**When use a composite key?** When the combination is the natural identity, such as a membership pair. A surrogate key may still be useful, but preserve a UNIQUE constraint on the business pair.

**Can I roll back ALTER TABLE?** MySQL 8.0 supports atomic DDL for many operations, improving crash safety, but DDL causes implicit commits and is not generally undone by ROLLBACK. Use a forward migration or restore strategy.

## MySQL References

Examples target MySQL 8.4/InnoDB. See [CREATE TABLE constraints](https://dev.mysql.com/doc/refman/8.4/en/create-table.html), [CHECK constraints](https://dev.mysql.com/doc/refman/8.4/en/create-table-check-constraints.html), and [implicit commits](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html).
