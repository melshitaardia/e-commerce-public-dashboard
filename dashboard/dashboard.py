# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the datasets
customers_df = pd.read_csv("../data/customers_dataset.csv")
orders_df = pd.read_csv("../data/orders_dataset.csv")
order_items_df = pd.read_csv("../data/order_items_dataset.csv")
order_reviews_df = pd.read_csv("../data/order_reviews_dataset.csv")
products_df = pd.read_csv("../data/products_dataset.csv")

# Convert date columns to datetime
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])

# Data Preparation
ecommerce_df = order_items_df.merge(products_df, on='product_id')
ecommerce_df = ecommerce_df.merge(orders_df, on='order_id')
ecommerce_df = ecommerce_df.merge(order_reviews_df, on='order_id')

# Calculate delivery time
ecommerce_df['delivery_time'] = (ecommerce_df['order_delivered_customer_date'] - ecommerce_df['order_purchase_timestamp']).dt.days

# Streamlit App Layout
st.title("E-Commerce Data Analysis Dashboard")

# Date Picker for filtering
st.sidebar.header("Filter by Date")
start_date = st.sidebar.date_input("Start Date", value=ecommerce_df['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input("End Date", value=ecommerce_df['order_purchase_timestamp'].max())

# Filter data based on selected date range
filtered_data = ecommerce_df[(ecommerce_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
                              (ecommerce_df['order_purchase_timestamp'] <= pd.to_datetime(end_date))]

# Sales Growth by Category
st.header("Sales Growth by Category")
monthly_category_df = filtered_data.resample(rule='M', on='order_purchase_timestamp').product_category_name.value_counts().unstack(fill_value=0)
monthly_category_df.index = monthly_category_df.index.strftime('%B %Y')
monthly_category_df = monthly_category_df.reset_index()

fig = go.Figure()
for category in monthly_category_df.columns[1:6]:  # Top 5 categories
    fig.add_trace(go.Scatter(x=monthly_category_df['order_purchase_timestamp'], 
                              y=monthly_category_df[category], 
                              mode='lines+markers', 
                              name=category))

fig.update_layout(title='Sales Trend of Top 5 Product Categories in 1 Year',
                  xaxis_title='Month',
                  yaxis_title='Number of Sales',
                  legend_title='Product Categories')
st.plotly_chart(fig)

# Delivery Time vs Review Score
st.header("Delivery Time vs Review Score")
fig2 = px.scatter(filtered_data, x='delivery_time', y='review_score', 
                  title='Delivery Time vs Review Score',
                  labels={'delivery_time': 'Delivery Time (days)', 'review_score': 'Review Score'},
                  trendline='ols')
st.plotly_chart(fig2)

# Customer Overview
st.header("Customer Overview")
customer_orders = filtered_data.groupby('customer_id').size().reset_index(name='order_count')
fig3 = px.histogram(customer_orders, x='order_count', 
                    title='Distribution of Orders per Customer',
                    labels={'order_count': 'Number of Orders'},
                    nbins=30)
st.plotly_chart(fig3)
