
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load datasets
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
sellers = pd.read_csv(DATA_DIR / "olist_sellers_dataset.csv")
reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")

# Convert date columns
date_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_columns:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

# Aggregate reviews at order level
order_reviews = (
    reviews.groupby("order_id")
    .agg(review_score=("review_score", "mean"))
    .reset_index()
)

# Aggregate items at seller-order level
seller_orders = (
    items.groupby(["seller_id", "order_id"])
    .agg(
        order_revenue=("price", "sum"),
        item_count=("order_item_id", "count")
    )
    .reset_index()
)

# Attach order information
seller_orders = seller_orders.merge(
    orders,
    on="order_id",
    how="left"
)

seller_orders = seller_orders.merge(
    order_reviews,
    on="order_id",
    how="left"
)

# Delivery delay in days:
# Negative = early, zero = on time, positive = late
seller_orders["delivery_delay_days"] = (
    seller_orders["order_delivered_customer_date"]
    - seller_orders["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

# Calculate seller-level KPIs
def calculate_seller_metrics(group):
    delivered = group[group["order_status"] == "delivered"]

    valid_delivery = delivered[
        delivered["delivery_delay_days"].notna()
    ]

    return pd.Series({
        "total_revenue": group["order_revenue"].sum(),
        "delivered_revenue": delivered["order_revenue"].sum(),
        "total_orders": group["order_id"].nunique(),
        "delivered_orders": delivered["order_id"].nunique(),
        "cancelled_orders": (
            group.loc[
                group["order_status"] == "canceled",
                "order_id"
            ].nunique()
        ),
        "on_time_delivery_pct": (
            (valid_delivery["delivery_delay_days"] <= 0).mean() * 100
            if len(valid_delivery) else None
        ),
        "average_review_score": group["review_score"].mean()
    })

performance = (
    seller_orders.groupby("seller_id")
    .apply(calculate_seller_metrics, include_groups=False)
    .reset_index()
)

# Cancellation rate
performance["cancellation_rate_pct"] = (
    performance["cancelled_orders"]
    / performance["total_orders"] * 100
)

# Add seller information
performance = performance.merge(
    sellers,
    on="seller_id",
    how="left"
)

# Save output
performance.to_csv(
    OUTPUT_DIR / "seller_performance.csv",
    index=False
)

# Display results
print("\nSELLER PERFORMANCE SUMMARY")
print("=" * 55)

print("Total sellers:", len(performance))
print("Total item revenue:",
      round(performance["total_revenue"].sum(), 2))
print("Delivered revenue:",
      round(performance["delivered_revenue"].sum(), 2))

print("\nTOP 10 SELLERS BY REVENUE")

print(
    performance.nlargest(10, "total_revenue")[
        ["seller_id", "seller_city", "total_revenue",
         "total_orders", "on_time_delivery_pct",
         "average_review_score"]
    ].to_string(index=False)
)

print("\nSaved seller_performance.csv successfully.")
