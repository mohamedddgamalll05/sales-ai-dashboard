// ============================================
// MongoDB CRUD Queries
// Demonstrating Insert, Read, Update, Delete
// ============================================

use sales_db;

// ============================================
// CREATE (Insert) Operations
// ============================================

// Insert a new user (Signup)
db.users.insertOne({
  name: "John Doe",
  email: "john.doe@example.com",
  password_hash: "hashed_password_here",
  created_at: new Date()
});

// Insert a prediction
db.predictions.insertOne({
  user_id: "USER_ID_HERE",
  input_data: {
    quantity: 100,
    sales_price: 50.0
  },
  prediction: 1,
  model_version: "1.0",
  created_at: new Date()
});

// Insert multiple dataset records
db.dataset.insertMany([
  {
    invoice_type: "Sales",
    date: new Date(),
    item: "Product A",
    quantity: 10,
    sales_price: 25.0,
    amount: 250.0,
    balance: 0
  },
  {
    invoice_type: "Sales",
    date: new Date(),
    item: "Product B",
    quantity: 5,
    sales_price: 50.0,
    amount: 250.0,
    balance: 0
  }
]);

// ============================================
// READ Operations
// ============================================

// Read all users
db.users.find();

// Read user by email (for login)
db.users.find({ email: "john.doe@example.com" });

// Read dataset with limit (for dashboard)
db.dataset.find().limit(5);

// Read all predictions
db.predictions.find();

// Read predictions by user_id
db.predictions.find({ user_id: "USER_ID_HERE" });

// Read predictions sorted by date
db.predictions.find().sort({ created_at: -1 }).limit(10);

// Read dataset with filters
db.dataset.find({ amount: { $gt: 1000 } });

// Read dataset grouped by item
db.dataset.find({ item: "Product A" });

// ============================================
// UPDATE Operations (Optional - for forgot password)
// ============================================

// Update user password
db.users.updateOne(
  { email: "john.doe@example.com" },
  { $set: { password_hash: "new_hashed_password" } }
);

// Update user name
db.users.updateOne(
  { email: "john.doe@example.com" },
  { $set: { name: "John Updated" } }
);

// Increment prediction count (if stats collection exists)
// db.user_stats.updateOne(
//   { user_id: "USER_ID_HERE" },
//   { $inc: { prediction_count: 1 } },
//   { upsert: true }
// );

// ============================================
// DELETE Operations
// ============================================

// Delete a user (used in delete account - see transactions.js for atomic version)
db.users.deleteOne({ email: "john.doe@example.com" });

// Delete predictions by user_id
db.predictions.deleteMany({ user_id: "USER_ID_HERE" });

// Delete a specific prediction
db.predictions.deleteOne({ _id: ObjectId("PREDICTION_ID_HERE") });

// ============================================
// Complex Queries
// ============================================

// Find users created in the last 7 days
db.users.find({
  created_at: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
});

// Find high-value invoices
db.dataset.find({ amount: { $gt: 1000 } }).sort({ amount: -1 });

// Count predictions by model version
db.predictions.aggregate([
  {
    $group: {
      _id: "$model_version",
      count: { $sum: 1 }
    }
  }
]);

// Find users with most predictions
db.predictions.aggregate([
  {
    $group: {
      _id: "$user_id",
      prediction_count: { $sum: 1 }
    }
  },
  { $sort: { prediction_count: -1 } },
  { $limit: 10 }
]);
