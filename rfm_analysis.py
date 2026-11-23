"""
E-Commerce Customer Segmentation using RFM Analysis

Reads the UCI Online Retail dataset, builds Recency / Frequency / Monetary
values for every customer, scores them, names the segments, and also runs
K-Means as a cross-check. Everything is saved in the outputs/ folder.

Usage:
    python rfm_analysis.py
    python rfm_analysis.py --file data/online_retail.csv
"""

import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

OUT_DIR = "outputs"


def find_data_file(path):
    if path and os.path.exists(path):
        return path
    for name in ["data/Online Retail.xlsx", "data/online_retail.xlsx",
                 "data/Online Retail.csv", "data/online_retail.csv",
                 "data/data.csv"]:
        if os.path.exists(name):
            return name
    sys.exit("Dataset not found. Put the UCI Online Retail file inside the data/ folder "
             "or pass it with --file.")


def load_data(path):
    if path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        # the Kaggle csv version is not utf-8
        df = pd.read_csv(path, encoding="ISO-8859-1")
    df.columns = [c.strip() for c in df.columns]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df


def clean_data(df):
    start = len(df)
    df = df.dropna(subset=["CustomerID"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]  # cancellations
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df = df.drop_duplicates()
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    print(f"Rows before cleaning: {start:,} | after: {len(df):,}")
    return df


def build_rfm(df):
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("TotalPrice", "sum"),
    ).reset_index()
    print(f"Customers: {len(rfm):,} | snapshot date: {snapshot.date()}")
    return rfm


def score_rfm(rfm):
    rfm["R_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    # rank first because many customers share the same frequency value
    rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5,
                             labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"].astype(str) + rfm["F_score"].astype(str) + rfm["M_score"].astype(str)
    return rfm


def name_segments(rfm):
    r, f = rfm["R_score"], rfm["F_score"]
    conditions = [
        (r >= 4) & (f >= 4),
        (r >= 3) & (f >= 3),
        (r >= 3) & (f <= 2),
        (r <= 2) & (f >= 4),
        (r <= 2) & (f == 3),
        (r == 2) & (f <= 2),
        (r == 1) & (f <= 2),
    ]
    names = ["Champions", "Loyal Customers", "New / Promising", "Can't Lose Them",
             "At Risk", "Hibernating", "Lost"]
    rfm["Segment"] = np.select(conditions, names, default="Other")
    return rfm


def summarise(rfm):
    summary = rfm.groupby("Segment").agg(
        Customers=("CustomerID", "count"),
        Avg_Recency_days=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Monetary=("Monetary", "mean"),
        Total_Revenue=("Monetary", "sum"),
    ).round(1)
    summary["Pct_of_Customers"] = (summary["Customers"] / summary["Customers"].sum() * 100).round(1)
    summary["Pct_of_Revenue"] = (summary["Total_Revenue"] / summary["Total_Revenue"].sum() * 100).round(1)
    return summary.sort_values("Total_Revenue", ascending=False)


def run_kmeans(rfm):
    # RFM is heavily right skewed, so log transform before scaling
    X = np.log1p(rfm[["Recency", "Frequency", "Monetary"]])
    X = StandardScaler().fit_transform(X)

    inertia, sil = [], []
    ks = range(2, 9)
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
        inertia.append(km.inertia_)
        sample = min(len(X), 4000)
        sil.append(silhouette_score(X, km.labels_, sample_size=sample, random_state=42))

    best_k = list(ks)[int(np.argmax(sil))]
    print(f"Silhouette is highest at k={best_k} ({max(sil):.3f})")
    # silhouette often prefers k=2 on RFM data, which is too coarse for marketing,
    # so the final model uses k=4 (see the elbow/silhouette chart for the trade-off)
    final_k = 4
    print(f"Using k={final_k} for the final clusters")

    rfm["Cluster"] = KMeans(n_clusters=final_k, n_init=10, random_state=42).fit_predict(X)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(list(ks), inertia, marker="o")
    ax[0].set_title("Elbow curve")
    ax[0].set_xlabel("k")
    ax[0].set_ylabel("Inertia")
    ax[1].plot(list(ks), sil, marker="o", color="darkorange")
    ax[1].set_title("Silhouette score")
    ax[1].set_xlabel("k")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/kmeans_elbow_silhouette.png", dpi=150)
    plt.close()

    profile = rfm.groupby("Cluster").agg(
        Customers=("CustomerID", "count"),
        Avg_Recency=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Monetary=("Monetary", "mean"),
    ).round(1)
    return rfm, profile


def make_charts(rfm, summary):
    order = summary.sort_values("Customers", ascending=True)
    plt.figure(figsize=(8, 5))
    plt.barh(order.index, order["Customers"], color="#1f3a8a")
    plt.title("Customers per segment")
    plt.xlabel("Number of customers")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/segment_sizes.png", dpi=150)
    plt.close()

    order = summary.sort_values("Pct_of_Revenue", ascending=True)
    plt.figure(figsize=(8, 5))
    plt.barh(order.index, order["Pct_of_Revenue"], color="#f97316")
    plt.title("Share of revenue per segment (%)")
    plt.xlabel("% of total revenue")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/segment_revenue_share.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 6))
    for seg, g in rfm.groupby("Segment"):
        plt.scatter(g["Frequency"], g["Monetary"], s=10, alpha=0.5, label=seg)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Frequency (orders, log)")
    plt.ylabel("Monetary (log)")
    plt.title("Customers by Frequency and Monetary value")
    plt.legend(fontsize=8, markerscale=2)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/segments_scatter.png", dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=None, help="path to the dataset")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    df = clean_data(load_data(find_data_file(args.file)))
    rfm = name_segments(score_rfm(build_rfm(df)))
    summary = summarise(rfm)
    rfm, cluster_profile = run_kmeans(rfm)
    make_charts(rfm, summary)

    rfm.to_csv(f"{OUT_DIR}/rfm_scores.csv", index=False)
    summary.to_csv(f"{OUT_DIR}/segment_summary.csv")
    cluster_profile.to_csv(f"{OUT_DIR}/kmeans_cluster_profile.csv")
    try:
        with pd.ExcelWriter(f"{OUT_DIR}/rfm_results.xlsx") as xw:
            rfm.to_excel(xw, sheet_name="RFM scores", index=False)
            summary.to_excel(xw, sheet_name="Segment summary")
            cluster_profile.to_excel(xw, sheet_name="KMeans profile")
    except ImportError:
        print("openpyxl not installed, skipped the Excel file (csv files are saved).")

    print("\nSegment summary")
    print(summary.to_string())
    print("\nK-Means cluster profile")
    print(cluster_profile.to_string())
    print(f"\nAll files saved in {OUT_DIR}/")


if __name__ == "__main__":
    main()
