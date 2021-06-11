import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 10)
import matplotlib.pyplot as plt
import seaborn as sns
from operator import attrgetter
import matplotlib.colors as mcolors

df_ = pd.read_excel('/online_retail.xlsx',
                   dtype={'CustomerID': str,
                          'InvoiceID': str},
                   parse_dates=['InvoiceDate'])

df = df_.copy()
df.head()

# Dropping nulls.
df.dropna(subset=['CustomerID'], inplace=True)

# Dropping duplicated rows because because only shopping frequency is important for Retention Rate.
df = df[['CustomerID', 'InvoiceNo', 'InvoiceDate']].drop_duplicates()

# Calculating the number of unique orders for each customer.
n_orders = df.groupby(['CustomerID'])['InvoiceNo'].nunique()

# The percentage of customers who placed an order more than once in the entire dataset.
orders_perc = np.sum(n_orders > 1) / df['CustomerID'].nunique()

# Getting order months.
df['order_month'] = df['InvoiceDate'].dt.to_period('M')

# Creating the cohort variable.
df['cohort'] = df.groupby('CustomerID')['InvoiceDate'] \
    .transform('min') \
    .dt.to_period('M')

# Getting number of customers per month.
df_cohort = df.groupby(['cohort', 'order_month']) \
    .agg(n_customers=('CustomerID', 'nunique')) \
    .reset_index(drop=False)

# Getting periods.
df_cohort['period_number'] = (df_cohort.order_month - df_cohort.cohort).apply(attrgetter('n'))

# Creating cohort pivot table.
cohort_pivot = df_cohort.pivot_table(index='cohort',
                                     columns='period_number',
                                     values='n_customers')

cohort_size = cohort_pivot.iloc[:, 0]

# Creating Retention Matrix.
retention_matrix = cohort_pivot.divide(cohort_size, axis=0)

# Creating heat map of Retention Matrix.
sns.axes_style("white")
fig, ax = plt.subplots(1, 2,
                       figsize=(12, 8),
                       sharey=True,
                       gridspec_kw={'width_ratios': [1, 11]}
                       )

sns.heatmap(retention_matrix,
            annot=True,
            fmt='.0%',
            cmap='RdYlGn',  # colormap
            ax=ax[1])

ax[1].set_title('Monthly Cohorts: User Retention', fontsize=16)
ax[1].set(xlabel='# of periods', ylabel='')

cohort_size_df = pd.DataFrame(cohort_size).rename(columns={0: 'cohort_size'})
white_cmap = mcolors.ListedColormap(['white'])
sns.heatmap(cohort_size_df,
            annot=True,
            cbar=False,
            fmt='g',
            cmap=white_cmap,
            ax=ax[0])
fig.tight_layout()
plt.show()
