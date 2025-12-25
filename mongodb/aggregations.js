// ============================================
// MongoDB Aggregation Pipelines
// Reproducing Pandas Statistics
// ============================================

use final_project;

// 1. Total Sales (Sum of all amounts) - Equivalent to pandas: df["amount"].sum()
db.dataset.aggregate([
  {
    $group: {
      _id: null,
      total_sales: { $sum: "$amount" },
      count: { $sum: 1 }
    }
  }
])

// 2. Average Quantity - Equivalent to pandas: df["quantity"].mean()
db.dataset.aggregate([
  {
    $group: {
      _id: null,
      average_quantity: { $avg: "$quantity" },
      min_quantity: { $min: "$quantity" },
      max_quantity: { $max: "$quantity" }
    }
  }
])

// 3. Median Amount - Equivalent to pandas: df["amount"].median()
// Note: MongoDB doesn't have direct median, so we sort and get middle value
db.dataset.aggregate([
  { $sort: { amount: 1 } },
  {
    $group: {
      _id: null,
      amounts: { $push: "$amount" },
      count: { $sum: 1 }
    }
  },
  {
    $project: {
      median_index: { $floor: { $divide: ["$count", 2] } },
      amounts: 1,
      count: 1
    }
  }
])

// 4. Top Items by Total Amount - Equivalent to pandas: df.groupby("item")["amount"].sum().sort_values(ascending=False).head(10)
db.dataset.aggregate([
  {
    $group: {
      _id: "$item",
      total_amount: { $sum: "$amount" },
      total_quantity: { $sum: "$quantity" },
      invoice_count: { $sum: 1 }
    }
  },
  { $sort: { total_amount: -1 } },
  { $limit: 10 }
])

// 5. Category Frequencies (Invoice Types) - Equivalent to pandas: df["invoice_type"].value_counts()
db.dataset.aggregate([
  {
    $group: {
      _id: "$invoice_type",
      count: { $sum: 1 },
      total_amount: { $sum: "$amount" }
    }
  },
  { $sort: { count: -1 } }
])

// 6. Distribution Statistics - Equivalent to pandas describe()
db.dataset.aggregate([
  {
    $group: {
      _id: null,
      count: { $sum: 1 },
      avg_amount: { $avg: "$amount" },
      min_amount: { $min: "$amount" },
      max_amount: { $max: "$amount" },
      avg_quantity: { $avg: "$quantity" },
      avg_sales_price: { $avg: "$sales_price" }
    }
  }
])

// 7. Top Items by Quantity - Equivalent to pandas: df.groupby("item")["quantity"].sum().sort_values(ascending=False)
db.dataset.aggregate([
  {
    $group: {
      _id: "$item",
      totalQty: { $sum: "$quantity" },
      avgAmount: { $avg: "$amount" }
    }
  },
  { $sort: { totalQty: -1 } },
  { $limit: 10 }
])

// 8. Date-based Analysis (if date field exists)
db.dataset.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m", date: "$date" } },
      total_sales: { $sum: "$amount" },
      invoice_count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])
