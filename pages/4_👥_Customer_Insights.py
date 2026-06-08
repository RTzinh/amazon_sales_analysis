import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_processor import load_data, preprocess_data, get_customer_segments_rfm
from ai_models import perform_customer_clustering, predict_customer_churn
from utils import apply_custom_css, create_3d_scatter, display_insight_box
import pandas as pd

st.set_page_config(page_title="Customer Insights", page_icon="👥", layout="wide")
apply_custom_css()

st.title("👥 Customer Insights")
st.markdown("Customer segmentation and behavioral analysis")

# Load data
with st.spinner("Loading data..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Error loading data.")
        st.stop()
    df = preprocess_data(df_raw)

# Customer overview metrics
total_customers = df['CustomerID'].nunique()
total_orders = len(df)
avg_orders_per_customer = total_orders / total_customers
total_revenue = df['TotalAmount'].sum()
avg_customer_value = total_revenue / total_customers

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Total Customers", f"{total_customers:,}")

with col2:
    st.metric("🛒 Avg Orders/Customer", f"{avg_orders_per_customer:.1f}")

with col3:
    st.metric("💰 Average Customer Value", f"${avg_customer_value:,.2f}")

with col4:
    repeat_customers = df.groupby('CustomerID').size()
    repeat_rate = (repeat_customers[repeat_customers > 1].count() / total_customers) * 100
    st.metric("🔁 Repeat Rate", f"{repeat_rate:.1f}%")

st.markdown("---")

# RFM Analysis
st.markdown("### 📊 RFM Segmentation (Recency, Frequency, Monetary)")

with st.spinner("Computing RFM segments..."):
    rfm_data = get_customer_segments_rfm(df)
    rfm_with_churn = predict_customer_churn(rfm_data)

# Segment distribution
col1, col2 = st.columns([2, 1])

with col1:
    segment_counts = rfm_with_churn['Segment'].value_counts()
    
    fig = px.bar(
        x=segment_counts.values,
        y=segment_counts.index,
        orientation='h',
        title='RFM Segment Distribution',
        labels={'x': 'Number of Customers', 'y': 'Segment'},
        color=segment_counts.values,
        color_continuous_scale='Purples'
    )
    
    fig.update_traces(text=segment_counts.values, textposition='outside')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': False},
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("#### 📋 Segments")
    
    segment_revenue = df.merge(
        rfm_with_churn[['Segment']],
        left_on='CustomerID',
        right_index=True
    ).groupby('Segment')['TotalAmount'].sum().sort_values(ascending=False)
    
    for segment in segment_revenue.index:
        revenue = segment_revenue[segment]
        count = segment_counts[segment]
        
        st.markdown(f"""
        **{segment}**
        {count:,} customers | ${revenue:,.0f}
        """)

st.markdown("---")

# RFM Scores visualization
st.markdown("### 💎 RFM Matrix")

col1, col2 = st.columns(2)

with col1:
    # Recency vs Frequency
    fig = px.scatter(
        rfm_with_churn.reset_index(),
        x='Recency',
        y='Frequency',
        size='Monetary',
        color='Segment',
        hover_data=['CustomerID', 'RFM_Score'],
        title='Recency vs Frequency (size = Monetary)'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=450
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    # Frequency vs Monetary
    fig = px.scatter(
        rfm_with_churn.reset_index(),
        x='Frequency',
        y='Monetary',
        color='Segment',
        size='Monetary',
        hover_data=['CustomerID', 'Recency'],
        title='Frequency vs Monetary Value'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=450
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Customer Clustering
st.markdown("### 🎯 Customer Clustering (Machine Learning)")

n_clusters = st.slider("Number of Clusters", 3, 6, 4)

with st.spinner("Running clustering analysis..."):
    customer_clusters, cluster_summary, cluster_map = perform_customer_clustering(df, n_clusters)

col1, col2 = st.columns([2, 1])

with col1:
    # 3D visualization
    fig = create_3d_scatter(
        customer_clusters,
        'Total_Spent',
        'Order_Count',
        'Avg_Order_Value',
        'Cluster_Name',
        'Customer Clusters (3D)'
    )

    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("#### 📊 Cluster Profile")

    st.dataframe(
        cluster_summary.rename(columns={
            'Total_Spent': 'Avg Spend',
            'Order_Count': 'Avg Orders',
            'Avg_Order_Value': 'Avg Order Value'
        }).style.format({
            'Avg Spend': '${:,.2f}',
            'Avg Orders': '{:.1f}',
            'Avg Order Value': '${:,.2f}'
        }),
        width='stretch'
    )

    for cluster_id, cluster_name in cluster_map.items():
        count = len(customer_clusters[customer_clusters['Cluster'] == cluster_id])
        st.markdown(f"**{cluster_name}**: {count:,} customers")

st.markdown("---")

# Churn Risk Analysis
st.markdown("### ⚠️ Churn Risk Analysis")

churn_distribution = rfm_with_churn['Churn_Risk'].value_counts()

col1, col2 = st.columns([2, 1])

with col1:
    risk_colors = {'High Risk': '#EF4444', 'Medium Risk': '#F59E0B', 'Low Risk': '#10B981'}
    
    fig = go.Figure(data=[go.Pie(
        labels=churn_distribution.index,
        values=churn_distribution.values,
        marker=dict(colors=[risk_colors[risk] for risk in churn_distribution.index]),
        hole=0.4,
        textinfo='percent+label+value'
    )])
    
    fig.update_layout(
        title='Churn Risk Distribution',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    high_risk_customers = rfm_with_churn[rfm_with_churn['Churn_Risk'] == 'High Risk']
    
    st.metric(
        "🚨 High-Risk Customers",
        len(high_risk_customers),
        f"{(len(high_risk_customers)/len(rfm_with_churn)*100):.1f}%"
    )

    high_risk_revenue = df[df['CustomerID'].isin(high_risk_customers.index)]['TotalAmount'].sum()

    st.metric(
        "💰 Revenue at Risk",
        f"${high_risk_revenue:,.2f}",
        help="Total revenue from high-risk customers"
    )

# Top customers
st.markdown("---")
st.markdown("### 🏆 Top 20 Customers")

top_customers = df.groupby(['CustomerID', 'CustomerName']).agg({
    'TotalAmount': 'sum',
    'OrderID': 'count',
    'Quantity': 'sum'
}).reset_index()

top_customers.columns = ['CustomerID', 'Name', 'Total Revenue', 'Orders', 'Items Purchased']
top_customers = top_customers.sort_values('Total Revenue', ascending=False).head(20)

# Add RFM segment
top_customers = top_customers.merge(
    rfm_with_churn[['Segment', 'Churn_Risk']],
    left_on='CustomerID',
    right_index=True,
    how='left'
)

st.dataframe(
    top_customers.style.background_gradient(cmap='Purples', subset=['Total Revenue'])
                       .format({
                           'Total Revenue': '${:,.2f}',
                           'Orders': '{:,.0f}',
                           'Items Purchased': '{:,.0f}'
                       }),
    width='stretch',
    height=500
)

st.markdown("---")

# Insights
st.markdown("### 💡 Customer Insights")

col1, col2, col3 = st.columns(3)

with col1:
    champions = len(rfm_with_churn[rfm_with_churn['Segment'] == 'Champions'])
    champions_pct = (champions / total_customers) * 100
    
    display_insight_box(
        "Champions Customers",
        f"{champions:,} customers ({champions_pct:.1f}%) are Champions - the best customers!",
        "🏆"
    )

with col2:
    at_risk = len(rfm_with_churn[rfm_with_churn['Churn_Risk'] == 'High Risk'])

    display_insight_box(
        "Action Required",
        f"{at_risk:,} high-risk customers need immediate attention for retention.",
        "⚠️"
    )

with col3:
    vip_cluster = customer_clusters[customer_clusters['Cluster_Name'] == 'VIP Customers']
    vip_revenue = vip_cluster['Total_Spent'].sum()

    display_insight_box(
        "VIP Customers",
        f"The VIP cluster generated ${vip_revenue:,.2f} in total revenue.",
        "💎"
    )
