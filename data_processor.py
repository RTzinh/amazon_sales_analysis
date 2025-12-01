import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

@st.cache_data
def load_data():
    """Load and cache the Amazon sales dataset"""
    try:
        df = pd.read_csv('Amazon.csv')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def preprocess_data(df):
    """Clean and preprocess the dataset"""
    df = df.copy()
    
    # Convert OrderDate to datetime
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # Create time-based features
    df['Year'] = df['OrderDate'].dt.year
    df['Month'] = df['OrderDate'].dt.month
    df['MonthName'] = df['OrderDate'].dt.strftime('%B')
    df['Quarter'] = df['OrderDate'].dt.quarter
    df['DayOfWeek'] = df['OrderDate'].dt.day_name()
    df['WeekOfYear'] = df['OrderDate'].dt.isocalendar().week
    
    # Create revenue features
    df['Revenue_Before_Discount'] = df['UnitPrice'] * df['Quantity']
    df['Discount_Amount'] = df['Revenue_Before_Discount'] * df['Discount']
    df['Net_Revenue'] = df['TotalAmount'] - df['Tax'] - df['ShippingCost']
    df['Profit_Margin'] = (df['Net_Revenue'] / df['TotalAmount']) * 100
    
    # Create order size category
    df['Order_Size'] = pd.cut(df['TotalAmount'], 
                               bins=[0, 100, 500, 1000, 5000],
                               labels=['Small', 'Medium', 'Large', 'Very Large'])
    
    return df

def get_summary_metrics(df):
    """Calculate key business metrics"""
    total_revenue = df['TotalAmount'].sum()
    total_orders = len(df)
    avg_order_value = df['TotalAmount'].mean()
    total_customers = df['CustomerID'].nunique()
    total_products = df['ProductID'].nunique()
    
    # Status breakdown
    delivered_orders = len(df[df['OrderStatus'] == 'Delivered'])
    cancelled_orders = len(df[df['OrderStatus'] == 'Cancelled'])
    returned_orders = len(df[df['OrderStatus'] == 'Returned'])
    
    # Revenue by status
    delivered_revenue = df[df['OrderStatus'] == 'Delivered']['TotalAmount'].sum()
    
    # Conversion rate (delivered / total)
    conversion_rate = (delivered_orders / total_orders) * 100
    
    # Cancellation rate
    cancellation_rate = (cancelled_orders / total_orders) * 100
    
    # Return rate
    return_rate = (returned_orders / total_orders) * 100
    
    metrics = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_customers': total_customers,
        'total_products': total_products,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'returned_orders': returned_orders,
        'delivered_revenue': delivered_revenue,
        'conversion_rate': conversion_rate,
        'cancellation_rate': cancellation_rate,
        'return_rate': return_rate
    }
    
    return metrics

def filter_data(df, date_range=None, categories=None, countries=None, status=None):
    """Filter dataframe based on user selections"""
    filtered_df = df.copy()
    
    if date_range:
        filtered_df = filtered_df[
            (filtered_df['OrderDate'] >= date_range[0]) & 
            (filtered_df['OrderDate'] <= date_range[1])
        ]
    
    if categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
    
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    
    if status:
        filtered_df = filtered_df[filtered_df['OrderStatus'].isin(status)]
    
    return filtered_df

def get_top_products(df, n=20, metric='revenue'):
    """Get top N products by specified metric"""
    if metric == 'revenue':
        top = df.groupby('ProductName')['TotalAmount'].sum().nlargest(n)
    elif metric == 'quantity':
        top = df.groupby('ProductName')['Quantity'].sum().nlargest(n)
    elif metric == 'orders':
        top = df.groupby('ProductName').size().nlargest(n)
    
    return top.reset_index()

def get_category_performance(df):
    """Analyze performance by category"""
    category_stats = df.groupby('Category').agg({
        'TotalAmount': 'sum',
        'Quantity': 'sum',
        'OrderID': 'count',
        'UnitPrice': 'mean',
        'Discount': 'mean',
        'Net_Revenue': 'sum',
        'Profit_Margin': 'mean'
    }).round(2)
    
    category_stats.columns = ['Revenue', 'Quantity', 'Orders', 'Avg_Price', 
                              'Avg_Discount', 'Net_Revenue', 'Avg_Margin']
    
    return category_stats.sort_values('Revenue', ascending=False)

def get_customer_segments_rfm(df):
    """Calculate RFM (Recency, Frequency, Monetary) segments"""
    # Calculate reference date (max date + 1 day)
    reference_date = df['OrderDate'].max() + pd.Timedelta(days=1)
    
    # Calculate RFM metrics
    rfm = df.groupby('CustomerID').agg({
        'OrderDate': lambda x: (reference_date - x.max()).days,  # Recency
        'OrderID': 'count',  # Frequency
        'TotalAmount': 'sum'  # Monetary
    })
    
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Create RFM scores (1-5, where 5 is best)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Convert to numeric
    rfm['R_Score'] = rfm['R_Score'].astype(int)
    rfm['F_Score'] = rfm['F_Score'].astype(int)
    rfm['M_Score'] = rfm['M_Score'].astype(int)
    
    # Calculate RFM score
    rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
    
    # Segment customers
    def segment_customer(row):
        if row['RFM_Score'] >= 13:
            return 'Champions'
        elif row['RFM_Score'] >= 10:
            return 'Loyal Customers'
        elif row['RFM_Score'] >= 7:
            return 'Potential Loyalists'
        elif row['RFM_Score'] >= 5 and row['R_Score'] >= 3:
            return 'At Risk'
        elif row['RFM_Score'] >= 5:
            return 'Needs Attention'
        else:
            return 'Lost'
    
    rfm['Segment'] = rfm.apply(segment_customer, axis=1)
    
    return rfm

def get_time_series_data(df, frequency='D'):
    """Aggregate data by time period"""
    time_series = df.set_index('OrderDate').resample(frequency).agg({
        'TotalAmount': 'sum',
        'OrderID': 'count',
        'Quantity': 'sum'
    }).reset_index()
    
    time_series.columns = ['Date', 'Revenue', 'Orders', 'Quantity']
    
    return time_series

def get_geographic_summary(df):
    """Summarize sales by geographic location"""
    country_stats = df.groupby('Country').agg({
        'TotalAmount': 'sum',
        'OrderID': 'count',
        'ShippingCost': 'mean'
    }).round(2)
    
    country_stats.columns = ['Revenue', 'Orders', 'Avg_Shipping_Cost']
    country_stats = country_stats.sort_values('Revenue', ascending=False)
    
    return country_stats
