import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import os

# Configure Gemini API
def configure_gemini(api_key):
    """Configure Google Gemini API"""
    genai.configure(api_key=api_key)
    return True

@st.cache_resource
def get_gemini_llm(api_key, model="gemini-2.5-flash"):
    """Get Gemini LLM instance for LangChain"""
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )

def create_data_agent(df, api_key):
    """Create LangChain agent that can analyze the dataframe"""
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
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        full_prompt = f"""Você é um analista de dados especializado em e-commerce.
        
Contexto dos dados: {data_context if data_context else 'Dataset de vendas Amazon com 100k transações'}

{prompt}

Forneça uma análise profissional, concisa e acionável."""
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar insights: {str(e)}"

def generate_business_insights(df, metrics, api_key):
    """Generate comprehensive business insights using Gemini"""
    
    # Prepare data summary
    data_context = f"""
    Total de Vendas: ${metrics['total_revenue']:,.2f}
    Total de Pedidos: {metrics['total_orders']:,}
    Ticket Médio: ${metrics['avg_order_value']:.2f}
    Taxa de Conversão: {metrics['conversion_rate']:.1f}%
    Taxa de Cancelamento: {metrics['cancellation_rate']:.1f}%
    
    Top 3 Categorias:
    {df.groupby('Category')['TotalAmount'].sum().nlargest(3).to_string()}
    
    Top 3 Países:
    {df.groupby('Country')['TotalAmount'].sum().nlargest(3).to_string()}
    """
    
    prompt = """Baseado nos dados acima, forneça:

1. **3 Insights Principais**: Padrões importantes identificados nos dados
2. **3 Oportunidades**: Áreas com potencial de crescimento
3. **3 Recomendações Acionáveis**: Ações específicas para melhorar o desempenho

Seja específico e orientado a resultados de negócio."""
    
    return analyze_with_gemini(prompt, api_key, data_context)

def ask_data_question(df, question, api_key):
    """Use LangChain agent to answer questions about the data"""
    try:
        agent = create_data_agent(df, api_key)
        
        # Add context to question
        enhanced_question = f"""Analise os dados de vendas da Amazon e responda:

{question}

Forneça a resposta em português, com números específicos e insights acionáveis."""
        
        response = agent.run(enhanced_question)
        return response
    except Exception as e:
        return f"Erro ao processar pergunta: {str(e)}\n\nTente reformular a pergunta de forma mais específica."

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
    """Identify customers at risk of churning based on RFM"""
    
    # Define churn risk
    def calculate_churn_risk(row):
        # High recency (not bought recently) and low frequency = high churn risk
        if row['Recency'] > rfm_data['Recency'].quantile(0.75):
            if row['Frequency'] < rfm_data['Frequency'].quantile(0.25):
                return 'High Risk'
            else:
                return 'Medium Risk'
        elif row['Recency'] > rfm_data['Recency'].median():
            return 'Medium Risk'
        else:
            return 'Low Risk'
    
    rfm_data['Churn_Risk'] = rfm_data.apply(calculate_churn_risk, axis=1)
    
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
    Dados de vendas mensais:
    {monthly_sales.to_string()}
    
    Estatísticas:
    - Vendas médias mensais: ${monthly_sales['TotalAmount'].mean():,.2f}
    - Crescimento total: {((monthly_sales['TotalAmount'].iloc[-1] / monthly_sales['TotalAmount'].iloc[0] - 1) * 100):.1f}%
    - Mês com maior venda: {monthly_sales.loc[monthly_sales['TotalAmount'].idxmax(), 'OrderDate']}
    """
    
    prompt = """Analise as tendências de vendas e forneça:

1. Padrão de crescimento observado
2. Sazonalidade identificada
3. Previsão qualitativa para próximos meses
4. Recomendações estratégicas

Seja específico e orientado a ação."""
    
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
    Performance por categoria:
    {category_stats.to_string()}
    """
    
    prompt = """Analise o desempenho das categorias e forneça:

1. Categorias estrela (alto desempenho)
2. Categorias com oportunidade de crescimento
3. Insights sobre estratégia de desconto
4. Recomendações de mix de produtos

Seja específico com números."""
    
    return analyze_with_gemini(prompt, api_key, context)
