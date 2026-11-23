# E-Commerce Customer Segmentation (RFM Analysis)

Project 2 of my Data Analytics internship at Veda Technology.

The goal was simple: take a real e-commerce transactions dataset, split the customers into groups using RFM (Recency, Frequency, Monetary value), and then turn those groups into an actual marketing decision, not just a bunch of clusters.

## What is RFM?

- **Recency**: how many days ago the customer last bought something
- **Frequency**: how many separate orders they placed
- **Monetary**: how much money they spent in total

Customers who bought recently, buy often and spend a lot are the best ones. Customers who haven't bought for months are drifting away. Marketing teams use this to decide who gets a loyalty reward and who gets a win-back offer.

## Dataset

[UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail): transactions from a UK-based online retailer between December 2010 and December 2011 (about 540,000 rows). It is also available on Kaggle as `data.csv`.

The dataset is not uploaded here because of its size. Download it and put it in a folder called `data/`.

## Approach

1. **Cleaning**: removed rows with no CustomerID, cancelled invoices (InvoiceNo starting with "C"), zero or negative quantity and price, and duplicate rows.
2. **RFM table**: used one day after the last invoice date as the reference date, then calculated R, F and M for each customer.
3. **Scoring**: gave each of R, F and M a score from 1 to 5 using quintiles. For recency a lower number of days gets a higher score. Frequency is ranked before splitting because a lot of customers have the same order count.
4. **Segment names**: mapped the R and F scores to 7 segments a marketing manager can understand: Champions, Loyal Customers, New / Promising, Can't Lose Them, At Risk, Hibernating, Lost.
5. **K-Means cross-check**: log-transformed and scaled the RFM values (they are very right skewed), tried k from 2 to 8 and looked at the elbow and silhouette score. Silhouette alone prefers a very small k, so I used k = 4 for the final clusters to keep them useful for marketing, and compared them with the rule-based segments.
6. **Recommendation**: wrote a one-page plan on which segment to target first, with which campaign and why. See [recommendation.md](recommendation.md).

## Tools used

Python (Pandas, NumPy, Scikit-learn, Matplotlib), Excel for checking the output, Power BI for the dashboard (load `outputs/rfm_scores.csv`).

## Project structure

```
ecommerce-rfm-customer-segmentation/
├── rfm_analysis.py        # full pipeline: clean, RFM, score, segment, K-Means, charts
├── rfm_analysis.ipynb     # same pipeline, ready to run in Google Colab
├── recommendation.md      # which segment to target and how
├── requirements.txt
├── data/                  # put the dataset here (not uploaded)
└── outputs/
    ├── rfm_scores.csv             # RFM score table for all customers
    ├── segment_summary.csv        # size, spend and revenue share of each segment
    ├── kmeans_cluster_profile.csv
    ├── rfm_results.xlsx           # same tables in one Excel file
    ├── segment_sizes.png
    ├── segment_revenue_share.png
    ├── segments_scatter.png
    └── kmeans_elbow_silhouette.png
```

## How to run

```bash
git clone https://github.com/RathodHarshvardhansinh/ecommerce-rfm-customer-segmentation.git
cd ecommerce-rfm-customer-segmentation
pip install -r requirements.txt
# download the dataset into data/ first
python rfm_analysis.py
```

If your file has a different name, use `python rfm_analysis.py --file path/to/file.csv`. All results are saved in the `outputs/` folder.

### Run on Google Colab (no setup)

Open `rfm_analysis.ipynb` in [Google Colab](https://colab.research.google.com), upload `rfm_analysis.py` in the files panel and run all cells. It downloads the dataset, runs the pipeline, shows the segment table and charts, and gives you `outputs.zip` to download.

## Outcome

Every customer gets an RFM score and a segment name, and the segment summary shows how many customers each segment has and how much revenue it brings. Based on that, the recommendation is to go after the **Can't Lose Them** segment first with a personal win-back offer, then **At Risk** as the second wave, while keeping Champions happy with rewards instead of discounts. The reasoning is in [recommendation.md](recommendation.md).

## Limitations

- The data is from one retailer, mostly wholesale customers, so results may not match a regular consumer store.
- RFM only looks at buying behavior, not product type, returns or marketing channel.
- Segment cut-offs are quintiles, so they are relative to this customer base.

## What I learned

- Naming segments in plain business words matters more than the clustering itself.
- Real transaction data needs a lot of cleaning (cancellations, missing customer IDs) before any analysis makes sense.
- K-Means metrics and business usefulness don't always agree, so the final choice has to make sense for the people using it.

## Author

Harshvardhansinh Rathod
B.Tech Information Technology, Sankalchand Patel College of Engineering
GitHub: [RathodHarshvardhansinh](https://github.com/RathodHarshvardhansinh)
