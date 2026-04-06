# Marketing Campaign Analytics

A full-stack data analytics project covering data cleaning, SQL analysis, and an interactive Streamlit dashboard for marketing campaign insights.


## Project Structure

```
Market_Analysis/
├── marketing.py                  # Streamlit dashboard app
├── Market.ipynb                  # Python notebook 
├── Cleaned_marketing_data.csv    # Cleaned dataset (required)
├── market.sql                    # SQL queries
├── requirements.txt              # Python dependencies
├── Project Report.pdf            # Project report
└── README.md                     # This file
```


##  Setup Instructions

### 1. Prerequisites

Make sure you have the following installed:

- **Python 3.9+** → [Download](https://www.python.org/downloads/)
- **pip** (comes with Python)

Check your versions:
```bash
python3 --version
pip --version
```

### 2. Install Dependencies

Run this in your project folder:

```bash
pip install streamlit pandas numpy plotly statsmodels
```

### 3. Prepare the Data

Make sure `Cleaned_marketing_data.csv` is in the **same folder** as `dashboard.py`:

The filename must match exactly: `Cleaned_marketing_data.csv`


##  Running the Dashboard

Open your terminal, navigate to the project folder, and run:

```bash
cd /path/to/Market_Analysis
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at:
```
http://localhost:8501
```

##  Running the SQL Queries

### Option A — MySQL

1. Open MySQL Workbench or your MySQL client
2. Run `market.sql` to create the database and execute all queries.

Or copy-paste individual queries from `market.sql` directly.

### Option B — Load CSV into MySQL with Python

```python
import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("Cleaned_marketing_data.csv")
engine = create_engine("mysql+mysqlconnector://user:password@localhost/market")
df.to_sql("market_data", con=engine, if_exists="replace", index=False)
print("Data loaded successfully!")
```

##  Dashboard Overview

The dashboard has **5 tabs**:

📈 Campaign Performance --> Acceptance rates per campaign, response rate by segment 
👥 Customer Segments    -->  Rule-based segments, demographics, complaint analysis 
🛍️ Spending Patterns    -->  Spend by product, age, income, country, education 
📦 Channel Analysis     -->  Web / Store / Catalog / Deals usage and preferences 
🏆 Top Customers        --> Top 10 spenders, heatmaps, target profile, recommendations 

### Sidebar Filters
- Country
- Education
- Age Group
- Income Group
- Marital Status


##  Common Errors & Fixes


`FileNotFoundError: Cleaned_marketing_data.csv`      -->  Place the CSV in the same folder as `dashboard.py` and run `streamlit run` from that folder 
`ModuleNotFoundError: No module named 'statsmodels'` -->  Run `pip install statsmodels` 
`ModuleNotFoundError: No module named 'plotly'`      -->  Run `pip install plotly` 
`ModuleNotFoundError: No module named 'streamlit'`   -->  Run `pip install streamlit`
 Port already in use                                 -->  Run `streamlit run dashboard.py --server.port 8502`


##  Key SQL Queries

The `market.sql` file contains 15 queries including:

1. Customers by education level
2. Average / min / max customer age
3. Overall response rate and revenue KPIs
4. Average spend per product
5. Spend by age group
6. Acceptance rate per campaign
7. Revenue per product
8. Most used purchase channel
9. Channel usage by age group
10. Top 10 highest-spending customers
11. Complainers vs non-complainers
12. Campaign acceptance frequency
13. Complaint rate
14. Customers by country
15. Education × Income Group cross-analysis


**Project:** Marketing Campaign Analysis  
**Domain:** Marketing / Customer Analytics  
**Tools:** Python, Pandas, NumPy, SQL, Streamlit, Plotly
