####################################
# Customer Segmentation using RFM
#####################################

# An e-commerce company wants to segment its customers and determine marketing strategies according to these segments.
# The company believes that marketing activities specific to customer segments that exhibit common behaviors will
# increase revenue.

# For example, it is desired to organize different campaigns for new customers and different campaigns in order to
# retain customers that are very profitable for the company.

# Dataset resource : https://archive.ics.uci.edu/ml/datasets/Online+Retail
# InvoiceNo – Fatura Numarası (Eğer bu kod C ile başlıyorsa işlemin iptal edildiğini ifade eder.)
# StockCode – Ürün kodu (Her bir ürün için eşsiz numara.)
# Description – Ürün ismi
# InvoiceDate – Fatura tarihi
# UnitPrice – Fatura fiyatı (Sterlin)
# CustomerID – Eşsiz müşteri numarası
# Country – Ülke ismi

# Import Libraries
import pandas as pd
import datetime as dt
from pandas.core.common import SettingWithCopyWarning
import warnings
import matplotlib.pyplot as plt

# Some display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

# Read the 2010-2011 data in the Online Retail II excel.
sales = pd.read_excel(r"/Users/naltay/Library/Mobile Documents/com~apple~CloudDocs/DATA SCIENCE/DSMLBC/data/online_retail_II.xlsx", sheet_name="Year 2010-2011")

##########################
# Understanding and Preparing Data
##########################

# Examine the descriptive statistics of the data set.
print('{:,} rows; {:,} columns'.format(sales.shape[0], sales.shape[1]))
print(sales.describe())

print(sales.isnull().sum().sort_values(ascending=False))

# Remove the missing observations from the data set. Use the 'inplace=True' parameter for subtraction.
sales.dropna(axis=0, inplace=True)

# How many of each product are there?
sales["Description"].value_counts().sort_values(ascending=False).head()
# WHITE HANGING HEART T-LIGHT HOLDER    2070
# REGENCY CAKESTAND 3 TIER              1905
# JUMBO BAG RED RETROSPOT               1662
# ASSORTED COLOUR BIRD ORNAMENT         1418
# PARTY BUNTING                         1416

# The 'C' in the invoices shows the canceled transactions. Remove the canceled transactions from the dataset.
df = sales[~sales["Invoice"].str.contains("C", na=False)]

# Create a variable named 'TotalPrice' that represents the total earnings per invoice.
df["TotalPrice"] = df["Price"] * df["Quantity"]
df.dropna(axis=0, inplace=True)

##########################
# Calculation RFM Metrics
##########################

df["InvoiceDate"].max()
# Timestamp('2011-12-09 12:50:00')

today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda invoicedate: (today_date - invoicedate.max()).days,
                                     'Invoice': lambda invoice: invoice.nunique(),
                                     'TotalPrice': lambda totalprice: totalprice.sum()})

rfm.columns = ["recency", "frequency", "monetary"]
rfm = rfm[(rfm['monetary'] > 0)]
print(rfm.describe().T)

##########################
# Calculation of RFM Scores and turning into one variable
##########################

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
# We did not consider manutery in this problem due to the correlation relationship with frequency.
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

##########################
# Defining RFM scores as segments
##########################

# The RFM scores give us 53 = 125 segments. Which is not easy to work with.
# We are going to work with 10 segments based on the R and F scores. Here is the description of the segments:

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.reset_index(inplace=True)
print(rfm.head())
rfm.to_excel("rfm_segments.xlsx")

# In general, the frequency values are quite low. At this point, it may be advisable to organize promotions and
# high discount campaigns. We need to give our priority to our customers who are present but whose loyalty
# may decrease day by day.

# It is seen that customers with cant_loose segment have a high frequency value in the general average,
# but they have recently withdrawn from the system themselves. This segment has high earning potential
# if the right strategies are applied for the company. A significant discount is recommended for quick recovery.
# A recovery campaign that appeals to emotion can be created.

# The at_Risk segment includes our customers who are familiar with the system and have a significant shopping
# experience. It should be in the first place in the segments that need to be focused, its recovery will provide high
# returns to the company. Here, promotional campaigns can be organized for the product groups they have shopped for
# the target audience. There may be a mass that withdraws itself from the system by purchasing a stocked product.
# Product-based campaigns can be recommended for them.

# plot the distribution of customers over R and F
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))

for i, p in enumerate(['R', 'F']):
    parameters = {'R': 'Recency', 'F': 'Frequency'}
    y = rfm[p].value_counts().sort_index()
    x = y.index
    ax = axes[i]
    bars = ax.bar(x, y, color='silver')
    ax.set_frame_on(False)
    ax.tick_params(left=False, labelleft=False, bottom=False)
    ax.set_title('Distribution of {}'.format(parameters[p]), fontsize=14)
    for bar in bars:
        value = bar.get_height()
        if value == y.max():
            bar.set_color('firebrick')
        ax.text(bar.get_x() + bar.get_width() / 2,
                value - 5,
                '{}\n({}%)'.format(int(value), int(value * 100 / y.sum())), ha='center', va='top', color='w')

plt.show()

# plot the distribution of M for RF score
fig, axes = plt.subplots(nrows=5, ncols=5, sharex=False, sharey=True, figsize=(10, 10))

r_range = range(1, 6)
f_range = range(1, 6)
for r in r_range:
    for f in f_range:
        y = rfm[(rfm['R'] == r) & (rfm['F'] == f)]['M'].value_counts().sort_index()
        x = y.index
        ax = axes[r - 1, f - 1]
        bars = ax.bar(x, y, color='silver')
        if r == 5:
            if f == 3:
                ax.set_xlabel('{}\nF'.format(f), va='top')
            else:
                ax.set_xlabel('{}\n'.format(f), va='top')
        if f == 1:
            if r == 3:
                ax.set_ylabel('R\n{}'.format(r))
            else:
                ax.set_ylabel(r)
        ax.set_frame_on(False)
        ax.tick_params(left=False, labelleft=False, bottom=False)
        ax.set_xticks(x)
        ax.set_xticklabels(x, fontsize=8)

        for bar in bars:
            value = bar.get_height()
            if value == y.max():
                bar.set_color('firebrick')
            ax.text(bar.get_x() + bar.get_width() / 2,
                    value,
                    int(value),
                    ha='center',
                    va='bottom',
                    color='k')
fig.suptitle('Distribution of M for each F and R',
             fontsize=14)
plt.tight_layout()
plt.show()
