import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import streamlit as st
import os

# NOTE: the LLM imports (google.generativeai / langchain) are done lazily inside the
# functions that use them. This way, pages that only need the pure-ML functions
# (clustering, churn, anomalies) — such as Customer Insights — keep loading even when
# the optional AI packages are missing or have incompatible APIs (e.g.
# langchain.agents.agent_types was removed in newer versions).

# Configure Gemini API
def configure_gemini(api_key):
    """Configure Google Gemini API"""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    return True

@st.cache_resource
def get_gemini_llm(api_key, model="gemini-2.5-flash"):
    """Get Gemini LLM instance for LangChain"""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )

def create_data_agent(df, api_key):
    """Create LangChain agent that can analyze the dataframe"""
    from langchain_experimental.agents import create_pandas_dataframe_agent
    try:
        from langchain.agents.agent_types import AgentType
    except ImportError:
        # AgentType was moved in recent versions of langchain
        from langchain.agents import AgentType

    llm = get_gemini_llm(api_key)

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent

def analyze_with_gemini(prompt, api_key, data_context=None):
    """Use Gemini to analyze data and generate insights"""
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        full_prompt = f"""You are a data analyst specialized in e-commerce.

Data context: {data_context if data_context else 'Amazon sales dataset with 100k transactions'}

{prompt}

Provide a professional, concise and actionable analysis. Respond in English."""

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def generate_business_insights(df, metrics, api_key):
    """Generate comprehensive business insights using Gemini"""
    
    # Prepare data summary
    data_context = f"""
    Total Sales: ${metrics['total_revenue']:,.2f}
    Total Orders: {metrics['total_orders']:,}
    Average Order Value: ${metrics['avg_order_value']:.2f}
    Conversion Rate: {metrics['conversion_rate']:.1f}%
    Cancellation Rate: {metrics['cancellation_rate']:.1f}%

    Top 3 Categories:
    {df.groupby('Category')['TotalAmount'].sum().nlargest(3).to_string()}

    Top 3 Countries:
    {df.groupby('Country')['TotalAmount'].sum().nlargest(3).to_string()}
    """

    prompt = """Based on the data above, provide:

1. **3 Key Insights**: Important patterns identified in the data
2. **3 Opportunities**: Areas with growth potential
3. **3 Actionable Recommendations**: Specific actions to improve performance

Be specific and business-results oriented."""
    
    return analyze_with_gemini(prompt, api_key, data_context)

def ask_data_question(df, question, api_key):
    """Use LangChain agent to answer questions about the data"""
    try:
        agent = create_data_agent(df, api_key)
        
        # Add context to question
        enhanced_question = f"""Analyze the Amazon sales data and answer:

{question}

Provide the answer in English, with specific numbers and actionable insights."""

        response = agent.run(enhanced_question)
        return response
    except Exception as e:
        return f"Error processing question: {str(e)}\n\nTry rephrasing the question more specifically."

@st.cache_data
def perform_customer_clustering(df, n_clusters=4):
    """Perform K-means clustering on customer behavior"""
    
    # Aggregate customer features
    customer_features = df.groupby('CustomerID').agg({
        'TotalAmount': ['sum', 'mean', 'count'],
        'Quantity': 'sum',
        'Discount': 'mean',
        'ShippingCost': 'mean'
    }).reset_index()
    
    customer_features.columns = ['CustomerID', 'Total_Spent', 'Avg_Order_Value', 
                                  'Order_Count', 'Total_Items', 'Avg_Discount', 'Avg_Shipping']
    
    # Prepare features for clustering
    features = customer_features[['Total_Spent', 'Avg_Order_Value', 'Order_Count', 
                                   'Total_Items', 'Avg_Discount', 'Avg_Shipping']]
    
    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    customer_features['Cluster'] = kmeans.fit_predict(features_scaled)
    
    # Label clusters based on characteristics
    cluster_summary = customer_features.groupby('Cluster').agg({
        'Total_Spent': 'mean',
        'Order_Count': 'mean',
        'Avg_Order_Value': 'mean'
    }).round(2)
    
    # Assign meaningful names
    cluster_names = []
    for idx, row in cluster_summary.iterrows():
        if row['Total_Spent'] > cluster_summary['Total_Spent'].median() and \
           row['Order_Count'] > cluster_summary['Order_Count'].median():
            cluster_names.append('VIP Customers')
        elif row['Order_Count'] > cluster_summary['Order_Count'].median():
            cluster_names.append('Frequent Buyers')
        elif row['Avg_Order_Value'] > cluster_summary['Avg_Order_Value'].median():
            cluster_names.append('High-Value Buyers')
        else:
            cluster_names.append('Occasional Buyers')
    
    # Map cluster names
    cluster_map = dict(zip(cluster_summary.index, cluster_names))
    customer_features['Cluster_Name'] = customer_features['Cluster'].map(cluster_map)
    
    return customer_features, cluster_summary, cluster_map

@st.cache_data
def detect_anomalies(df, contamination=0.05):
    """Detect anomalous transactions using Isolation Forest"""
    
    # Select features for anomaly detection
    features = df[['TotalAmount', 'Quantity', 'UnitPrice', 'Discount', 
                    'ShippingCost', 'Tax']].copy()
    
    # Train Isolation Forest
    iso_forest = IsolationForest(contamination=contamination, random_state=42)
    df_copy = df.copy()
    df_copy['Anomaly'] = iso_forest.fit_predict(features)
    
    # -1 indicates anomaly, 1 indicates normal
    anomalies = df_copy[df_copy['Anomaly'] == -1].copy()
    
    return anomalies

def predict_customer_churn(rfm_data):
    """Identify customers at risk of churning based on RFM.

    Vectorized: the thresholds (quantiles/median) are computed ONCE over the whole
    columns, instead of being recomputed for each row inside an apply. This avoids
    ~159s of processing on ~43k customers (the old row-by-row apply version made the
    app freeze on the "Computing RFM segments..." screen). The result is identical to
    the original logic.
    """
    recency = rfm_data['Recency']
    frequency = rfm_data['Frequency']

    # Thresholds computed only once
    rec_q75 = recency.quantile(0.75)
    rec_median = recency.median()
    freq_q25 = frequency.quantile(0.25)

    # High recency (not bought recently) and low frequency = high churn risk
    high_recency = recency > rec_q75
    low_frequency = frequency < freq_q25

    # Default: Low Risk; apply the rules in the same order as the original logic
    churn = pd.Series('Low Risk', index=rfm_data.index)
    # For recency above the median (but not in the top 25%) -> Medium Risk
    churn[recency > rec_median] = 'Medium Risk'
    # For recency in the top 25%: Medium Risk by default, High Risk if frequency is low
    churn[high_recency] = 'Medium Risk'
    churn[high_recency & low_frequency] = 'High Risk'

    rfm_data['Churn_Risk'] = churn

    return rfm_data

def generate_product_recommendations(df, customer_id=None, top_n=5):
    """Generate product recommendations based on purchase patterns"""
    
    if customer_id:
        # Get customer's purchase history
        customer_products = df[df['CustomerID'] == customer_id]['ProductID'].unique()
        
        # Find similar customers (who bought same products)
        similar_customers = df[df['ProductID'].isin(customer_products)]['CustomerID'].unique()
        
        # Get products bought by similar customers
        recommended_products = df[
            (df['CustomerID'].isin(similar_customers)) & 
            (~df['ProductID'].isin(customer_products))
        ].groupby('ProductName')['TotalAmount'].sum().nlargest(top_n)
        
        return recommended_products.reset_index()
    else:
        # Return top selling products as default
        top_products = df.groupby('ProductName')['TotalAmount'].sum().nlargest(top_n)
        return top_products.reset_index()

def analyze_sales_trends(df, api_key):
    """Use Gemini to analyze sales trends"""
    
    # Prepare trend data
    monthly_sales = df.groupby(df['OrderDate'].dt.to_period('M')).agg({
        'TotalAmount': 'sum',
        'OrderID': 'count'
    }).reset_index()
    
    monthly_sales['OrderDate'] = monthly_sales['OrderDate'].astype(str)
    
    trend_context = f"""
    Monthly sales data:
    {monthly_sales.to_string()}

    Statistics:
    - Average monthly sales: ${monthly_sales['TotalAmount'].mean():,.2f}
    - Total growth: {((monthly_sales['TotalAmount'].iloc[-1] / monthly_sales['TotalAmount'].iloc[0] - 1) * 100):.1f}%
    - Highest-selling month: {monthly_sales.loc[monthly_sales['TotalAmount'].idxmax(), 'OrderDate']}
    """

    prompt = """Analyze the sales trends and provide:

1. Observed growth pattern
2. Identified seasonality
3. Qualitative forecast for the coming months
4. Strategic recommendations

Be specific and action oriented."""
    
    return analyze_with_gemini(prompt, api_key, trend_context)

def analyze_category_performance(df, api_key):
    """Use Gemini to analyze category performance"""
    
    category_stats = df.groupby('Category').agg({
        'TotalAmount': ['sum', 'mean'],
        'OrderID': 'count',
        'Discount': 'mean'
    }).round(2)
    
    category_stats.columns = ['Total_Revenue', 'Avg_Order', 'Total_Orders', 'Avg_Discount']
    category_stats = category_stats.sort_values('Total_Revenue', ascending=False)
    
    context = f"""
    Performance by category:
    {category_stats.to_string()}
    """

    prompt = """Analyze the category performance and provide:

1. Star categories (high performance)
2. Categories with growth opportunity
3. Insights on discount strategy
4. Product-mix recommendations

Be specific with numbers."""
    
    return analyze_with_gemini(prompt, api_key, context)
