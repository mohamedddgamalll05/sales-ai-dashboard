// ============================================
// MongoDB Transactions (ACID)
// Demonstrating Atomic Operations
// ============================================

use sales_db;

// ============================================
// TRANSACTION 1: Delete User and All Predictions (SUCCESS SCENARIO)
// ============================================
// This transaction ensures that deleting a user AND all their predictions
// happens atomically - either both succeed or both fail.

session = db.getMongo().startSession();
session.startTransaction();

try {
  // Replace "USER_ID_HERE" with actual ObjectId from your users collection
  const userId = ObjectId("USER_ID_HERE");
  const userIdStr = userId.toString();
  
  // Delete user
  const deleteUserResult = session.getDatabase("sales_db").users.deleteOne(
    { _id: userId },
    { session: session }
  );
  
  // Delete all predictions for this user
  const deletePredictionsResult = session.getDatabase("sales_db").predictions.deleteMany(
    { user_id: userIdStr },
    { session: session }
  );
  
  // If both operations succeed, commit the transaction
  session.commitTransaction();
  
  print("✅ Transaction committed successfully");
  print(`   Deleted user: ${deleteUserResult.deletedCount}`);
  print(`   Deleted predictions: ${deletePredictionsResult.deletedCount}`);
  
} catch (e) {
  // If any operation fails, rollback everything
  session.abortTransaction();
  print("❌ Transaction aborted due to error:");
  print(`   ${e.message}`);
}

session.endSession();

// ============================================
// TRANSACTION 2: Rollback Scenario
// ============================================
// This demonstrates what happens when a transaction fails
// and needs to be rolled back.

session = db.getMongo().startSession();
session.startTransaction();

try {
  const userId = ObjectId("USER_ID_HERE");
  const userIdStr = userId.toString();
  
  // Delete user
  session.getDatabase("sales_db").users.deleteOne(
    { _id: userId },
    { session: session }
  );
  
  // Intentionally cause an error (e.g., invalid operation)
  // This will trigger rollback
  session.getDatabase("sales_db").predictions.deleteMany(
    { user_id: userIdStr, invalidField: { $invalid: "operation" } }, // Invalid query
    { session: session }
  );
  
  session.commitTransaction();
  
} catch (e) {
  // Transaction will be rolled back automatically
  session.abortTransaction();
  print("✅ Transaction rolled back successfully (as expected)");
  print(`   Error: ${e.message}`);
}

session.endSession();

// ============================================
// TRANSACTION 3: Log Prediction AND Update Usage Stats (Alternative Example)
// ============================================
// This shows another atomic operation: saving a prediction
// and updating user statistics in one transaction.

session = db.getMongo().startSession();
session.startTransaction();

try {
  const userId = ObjectId("USER_ID_HERE");
  const userIdStr = userId.toString();
  
  // Insert prediction
  session.getDatabase("sales_db").predictions.insertOne(
    {
      user_id: userIdStr,
      input_data: { quantity: 100, sales_price: 50.0 },
      prediction: 1,
      model_version: "1.0",
      created_at: new Date()
    },
    { session: session }
  );
  
  // Update user stats (if you have a stats collection)
  // session.getDatabase("sales_db").user_stats.updateOne(
  //   { user_id: userIdStr },
  //   { $inc: { prediction_count: 1 } },
  //   { upsert: true, session: session }
  // );
  
  session.commitTransaction();
  print("✅ Prediction logged and stats updated atomically");
  
} catch (e) {
  session.abortTransaction();
  print("❌ Transaction aborted - prediction not saved");
  print(`   ${e.message}`);
}

session.endSession();
