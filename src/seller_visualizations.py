import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

INPUT_FILE = Path("data/processed/seller_performance.csv")
OUTPUT_DIR = Path("reports/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load seller performance data
df = pd.read_csv(INPUT_FILE)

sns.set_theme(style="whitegrid")

# 1. Top 10 sellers by revenue
top_sellers = df.nlargest(10, "total_revenue").sort_values("total_revenue")

plt.figure(figsize=(10, 6))
sns.barplot(
    data=top_sellers,
    x="total_revenue",
    y="seller_city",
    hue="seller_city",
    legend=False
)
plt.title("Top 10 Sellers by Item Revenue")
plt.xlabel("Total Item Revenue")
plt.ylabel("Seller City")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top_10_sellers_revenue.png", dpi=300)
plt.close()

# 2. On-time delivery performance
top_delivery = (
    df.dropna(subset=["on_time_delivery_pct"])
    .nlargest(10, "on_time_delivery_pct")
    .sort_values("on_time_delivery_pct")
)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=top_delivery,
    x="on_time_delivery_pct",
    y="seller_city",
    hue="seller_city",
    legend=False
)
plt.title("Top 10 Sellers by Associated On-Time Delivery Rate")
plt.xlabel("On-Time Delivery (%)")
plt.ylabel("Seller City")
plt.xlim(0, 100)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "on_time_delivery.png", dpi=300)
plt.close()

# 3. Delivery performance vs review score
scatter_data = df.dropna(
    subset=["on_time_delivery_pct", "average_review_score"]
)

plt.figure(figsize=(9, 6))
sns.scatterplot(
    data=scatter_data,
    x="on_time_delivery_pct",
    y="average_review_score",
    alpha=0.6
)
plt.title("Delivery Performance vs Associated Order Review Score")
plt.xlabel("On-Time Delivery (%)")
plt.ylabel("Average Review Score")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "delivery_vs_reviews.png", dpi=300)
plt.close()

print("Visualisations created successfully:")
print("1. top_10_sellers_revenue.png")
print("2. on_time_delivery.png")
print("3. delivery_vs_reviews.png")
print("Saved in reports/figures/")