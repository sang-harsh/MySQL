# Schema Design And Normalization

[Exercises](11-schema-design-normalization-exercises.md) | [Topic index](../start.md)

## Interview Answer

A relational schema represents entities and their relationships while protecting data consistency. Normalization separates facts so each fact is stored in the appropriate place, reducing update, insert, and delete anomalies. I start with entities and cardinality, use junction tables for many-to-many relationships, and denormalize only for a measured read or reporting need with a clear consistency strategy.

## Key Points

- One-to-many: store the parent's key as a foreign key on the many-side, such as `orders.customer_id`.
- Many-to-many: use a junction table with foreign keys to both sides, usually a composite unique/primary key on that pair. Put relationship attributes (such as quantity) on the junction row.
- 1NF: columns hold values from the intended domain rather than repeating lists/groups. Store product lines as rows, not comma-separated IDs.
- 2NF: non-key attributes depend on the whole candidate key, not part of a composite key. It matters when a key has multiple columns.
- 3NF: non-key attributes depend on the key, the whole key, and nothing but the key; avoid transitive dependencies between non-key columns.
- Normalization avoids conflicting copies, but some values (for example a historical order-item price) are intentionally snapshotted because they describe a past event.
- Denormalization adds duplicated or derived state. Define who updates it, how it is rebuilt, and what stale data is acceptable.

## Minimal Example

```sql
CREATE TABLE order_items (
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (order_id, product_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;
```

The pair identifies a product line in an order; quantity and the historical unit price belong to that relationship. If the same product can appear in separate lines, use a line ID or include a line number in the key.

## Common Traps

- A comma-separated list in a column makes validation, joins, and indexing difficult; model repeated values as child rows.
- Do not overwrite historical order price when the current product price changes; snapshot transaction facts where business history requires it.
- Normalization is not an absolute ban on duplication. A cache or summary table needs explicit refresh and consistency rules.
- A surrogate ID does not remove the need for a UNIQUE constraint on a natural business key.

## Likely Follow-Ups

**What anomaly does normalization prevent?** A change to a duplicated fact can update one row but miss another, creating inconsistent values. Separating the fact gives it one authoritative location.

**When denormalize?** When measurement shows a read bottleneck and the team can maintain the duplicated data reliably. Document freshness and repair/rebuild behavior.

**What is BCNF?** A stronger normal form requiring every determinant to be a candidate key. For typical application interviews, explain it briefly and focus on recognizing when a dependency violates it.

## Reference

Examples target MySQL 8.4/InnoDB for constraints; normalization principles are relational concepts rather than MySQL-specific behavior. See [foreign key constraints](https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html).
