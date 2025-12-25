// ============================================
// MongoDB Indexes
// Demonstrating Performance Improvements
// ============================================

use final_project;

// ============================================
// CREATE INDEXES
// ============================================

// Index 1: Email index on users collection (for fast login lookups)
db.users.createIndex({ email: 1 }, { name: "email_index" });
print("✅ Created index on users.email");

// Index 2: User ID index on predictions collection (for fast user prediction queries)
db.predictions.createIndex({ user_id: 1 }, { name: "user_id_index" });
print("✅ Created index on predictions.user_id");

// Index 3: Created_at index on predictions (for time-based queries)
db.predictions.createIndex({ created_at: -1 }, { name: "created_at_index" });
print("✅ Created index on predictions.created_at");

// Index 4: Amount index on dataset (for analytics queries)
db.dataset.createIndex({ amount: -1 }, { name: "amount_index" });
print("✅ Created index on dataset.amount");

// Index 5: Item index on dataset (for grouping queries)
db.dataset.createIndex({ item: 1 }, { name: "item_index" });
print("✅ Created index on dataset.item");

// ============================================
// EXPLAIN QUERIES - BEFORE INDEX (or without using index)
// ============================================

print("\n=== QUERY 1: Find user by email (WITHOUT INDEX) ===");
db.users.find({ email: "test@test.com" }).explain("executionStats");

print("\n=== QUERY 2: Find predictions by user_id (WITHOUT INDEX) ===");
db.predictions.find({ user_id: "some_user_id" }).explain("executionStats");

// ============================================
// EXPLAIN QUERIES - AFTER INDEX (showing performance improvement)
// ============================================

print("\n=== QUERY 1: Find user by email (WITH INDEX) ===");
// This should show "IXSCAN" (index scan) instead of "COLLSCAN" (collection scan)
const explain1 = db.users.find({ email: "test@test.com" }).explain("executionStats");
print(`Execution Time: ${explain1.executionStats.executionTimeMillis}ms`);
print(`Index Used: ${explain1.executionStats.executionStages.indexName || "COLLSCAN"}`);
print(`Documents Examined: ${explain1.executionStats.executionStages.documentsExamined}`);
print(`Documents Returned: ${explain1.executionStats.nReturned}`);

print("\n=== QUERY 2: Find predictions by user_id (WITH INDEX) ===");
const explain2 = db.predictions.find({ user_id: "some_user_id" }).explain("executionStats");
print(`Execution Time: ${explain2.executionStats.executionTimeMillis}ms`);
print(`Index Used: ${explain2.executionStats.executionStages.indexName || "COLLSCAN"}`);
print(`Documents Examined: ${explain2.executionStats.executionStages.documentsExamined}`);
print(`Documents Returned: ${explain2.executionStats.nReturned}`);

print("\n=== QUERY 3: Top items by amount (WITH INDEX) ===");
const explain3 = db.dataset.find({ amount: { $gt: 1000 } }).sort({ amount: -1 }).limit(10).explain("executionStats");
print(`Execution Time: ${explain3.executionStats.executionTimeMillis}ms`);
print(`Index Used: ${explain3.executionStats.executionStages.indexName || "COLLSCAN"}`);

// ============================================
// LIST ALL INDEXES
// ============================================

print("\n=== INDEXES ON users COLLECTION ===");
db.users.getIndexes();

print("\n=== INDEXES ON predictions COLLECTION ===");
db.predictions.getIndexes();

print("\n=== INDEXES ON dataset COLLECTION ===");
db.dataset.getIndexes();
