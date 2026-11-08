# Schema Design And Normalization: Exercises

[Notes](11-schema-design-normalization.md) | [Topic index](../start.md)

12 questions: 6 production design scenarios, 4 schema/diagnostic tasks, and 2 interview questions. Target MySQL 8.4 with InnoDB. Treat every schema as a design exercise; use a fresh schema for DDL.

## 1. Model Customers And Orders

A customer may place many orders; each order belongs to at most one customer. Propose the relationship.

**Expected result:** A nullable or required customer_id foreign key on orders according to guest-order rules.

<details><summary>Show answer</summary>

```sql
CREATE TABLE orders (
 order_id BIGINT PRIMARY KEY,
 customer_id BIGINT NULL,
 FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB;
```
Use NOT NULL if guests are forbidden. Decide retention/deletion behavior explicitly.
</details>

## 2. Model Products In An Order

An order contains many products and a product can occur in many orders. Store quantity and the sale-time price.

**Expected result:** Use an order_items junction table with both keys and relationship attributes.

<details><summary>Show answer</summary>

```sql
CREATE TABLE order_items (
 order_id BIGINT NOT NULL,
 product_id BIGINT NOT NULL,
 quantity INT NOT NULL,
 unit_price DECIMAL(10,2) NOT NULL,
 PRIMARY KEY(order_id,product_id)
) ENGINE=InnoDB;
```
Add foreign keys to both parent tables. Preserve unit_price as the transaction-time value.
</details>

## 3. Avoid Repeating Addresses In Every Order

A customer can update their profile address, but each order must retain the delivery address used at checkout. What belongs where?

**Expected result:** Keep the current address with customer data and snapshot the delivery address on each order.

<details><summary>Show answer</summary>

Store normalized current address fields on the customer/address entity and copy the confirmed delivery address into the order's historical snapshot. This duplication is intentional because the order describes a past transaction.
</details>

## 4. Remove Comma-Separated Product IDs

A column stores values like `12,18,24`. Propose a relational replacement.

**Expected result:** One row per association in a junction table.

<details><summary>Show answer</summary>

Create a child table with a parent foreign key and one product ID per row, plus a composite uniqueness constraint if duplicates are invalid. This makes joins, constraints, and indexes usable.
</details>

## 5. Decide Whether To Store A Customer Total

The application needs a customer lifetime total. Should it calculate each time or store a cached total?

**Expected result:** Begin with calculation; denormalize only if measurement justifies it and consistency is defined.

<details><summary>Show answer</summary>

Start by calculating from authoritative order/payment facts. If measured latency justifies a stored summary, define transactional update rules, idempotency, reconciliation, and rebuild behavior so the total cannot silently drift.
</details>

## 6. Model Multiple Phone Numbers

A user can have multiple phone numbers, each with a type and verification status. How should the schema represent them?

**Expected result:** A user_phone child table with one phone per row and a foreign key.

<details><summary>Show answer</summary>

Use a separate user_phone table with phone ID or a suitable composite key, user_id, phone number, type, and verified status. Add uniqueness rules only if the business requires global or per-user uniqueness.
</details>

## 7. Create A Junction Table

Write a basic table definition for course enrollment, one enrollment per student/course pair.

**Expected result:** Both references are non-NULL and the pair is unique.

<details><summary>Show answer</summary>

```sql
CREATE TABLE enrollments (
 student_id BIGINT NOT NULL,
 course_id BIGINT NOT NULL,
 enrolled_at DATETIME NOT NULL,
 PRIMARY KEY(student_id,course_id),
 FOREIGN KEY(student_id) REFERENCES students(student_id),
 FOREIGN KEY(course_id) REFERENCES courses(course_id)
) ENGINE=InnoDB;
```
The composite primary key prevents duplicate enrollment pairs.
</details>

## 8. Identify A Partial Dependency

A table has composite key `(order_id, product_id)`, plus `order_date` and `quantity`. Why might `order_date` violate 2NF?

**Expected result:** order_date depends on order_id alone, not the whole composite key.

<details><summary>Show answer</summary>

If order_date is determined by order_id alone, it depends on only part of the composite key. Store it on orders; keep quantity on order_items because it depends on the order/product line.
</details>

## 9. Identify A Transitive Dependency

In an employee table, `employee_id -> department_id -> department_name`. What is the 3NF concern?

**Expected result:** Department name depends transitively on employee ID through department ID.

<details><summary>Show answer</summary>

Store department_name in a departments table keyed by department_id and reference that ID from employees. This gives department facts one authoritative location and avoids inconsistent copies.
</details>

## 10. Preserve Natural-Key Uniqueness

A table has a surrogate `user_id`, but email must be unique. What constraint is still needed?

**Expected result:** A UNIQUE constraint on email, with a clear nullable/required rule.

<details><summary>Show answer</summary>

```sql
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE(email);
```
Use NOT NULL if every user must have email; otherwise MySQL permits multiple NULLs under a unique index.
</details>

## 11. Interview: Explain 1NF, 2NF, And 3NF

Give concise practical definitions of the first three normal forms.

**Expected result:** Cover atomic/domain values, whole composite key, and non-key dependency.

<details><summary>Show answer</summary>

1NF avoids repeating groups and stores one value per intended cell. 2NF removes attributes dependent on only part of a composite candidate key. 3NF removes transitive dependencies so non-key attributes depend on the key, the whole key, and nothing but the key.
</details>

## 12. Interview: Why Denormalize?

Give one valid reason to denormalize and one operational requirement it creates.

**Expected result:** Explain measured read benefit and consistency/refresh responsibility.

<details><summary>Show answer</summary>

Denormalization can reduce expensive repeated reads when measurement shows a real bottleneck. It creates duplicated state, so updates, stale-data tolerance, reconciliation, and rebuild ownership must be defined.
</details>
