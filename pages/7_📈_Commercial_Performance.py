import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import load_data, preprocess_data, get_summary_metrics
from utils import apply_custom_css, display_insight_box
import pandas as pd
import numpy as np

st.set_page_config(page_title="Commercial Performance", page_icon="📈", layout="wide")
apply_custom_css()

st.title("📈 Commercial Performance")
st.markdown("**Analysis of Essential KPIs for Sales Management**")

# Load data
with st.spinner("Loading data..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Error loading data.")
        st.stop()
    df = preprocess_data(df_raw)

# Calculate commercial KPIs
metrics = get_summary_metrics(df)

# Additional commercial metrics
total_revenue = df['TotalAmount'].sum()
delivered_revenue = df[df['OrderStatus'] == 'Delivered']['TotalAmount'].sum()
lost_revenue = df[df['OrderStatus'].isin(['Cancelled', 'Returned'])]['TotalAmount'].sum()
gross_margin_pct = (df['Net_Revenue'].sum() / total_revenue) * 100
avg_discount = df['Discount'].mean() * 100
total_shipping = df['ShippingCost'].sum()
shipping_impact = (total_shipping / total_revenue) * 100

# Header metrics
st.markdown("### 💰 Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Actual Revenue",
        f"R$ {delivered_revenue:,.2f}",
        delta=f"{metrics['conversion_rate']:.1f}% converts",
        help="Revenue from delivered orders (excluding cancellations)"
    )

with col2:
    st.metric(
        "Average Order Value",
        f"R$ {metrics['avg_order_value']:.2f}",
        help="Average value per order"
    )

with col3:
    st.metric(
        "Commercial Margin",
        f"{gross_margin_pct:.1f}%",
        help="Net margin after taxes and shipping"
    )

with col4:
    st.metric(
        "Commercial Losses",
        f"R$ {lost_revenue:,.2f}",
        delta=f"-{(lost_revenue/total_revenue)*100:.1f}%",
        delta_color="inverse",
        help="Revenue lost to cancellations and returns"
    )

with col5:
    st.metric(
        "Average Discount",
        f"{avg_discount:.1f}%",
        help="Average discount applied on sales"
    )

st.markdown("---")

# Conversion funnel
st.markdown("### 🎯 Commercial Conversion Funnel")

col1, col2 = st.columns([2, 1])

with col1:
    stages = ['Total Orders', 'Shipped', 'Delivered']
    values = [
        metrics['total_orders'],
        metrics['total_orders'] - df[df['OrderStatus'] == 'Pending'].shape[0],
        metrics['delivered_orders']
    ]
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ['#8B5CF6', '#7C3AED', '#10B981']},
        connector={"line": {"color": "#8B5CF6", "width": 2}}
    ))
    
    fig.update_layout(
        title='Order Pipeline',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        height=350
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("#### 🔍 Loss Analysis")

    cancelled_rate = (metrics['cancelled_orders'] / metrics['total_orders']) * 100
    return_rate = metrics['return_rate']

    st.metric("Cancellation Rate", f"{cancelled_rate:.2f}%", delta=f"-{cancelled_rate:.2f}%", delta_color="inverse")
    st.metric("Return Rate", f"{return_rate:.2f}%", delta=f"-{return_rate:.2f}%", delta_color="inverse")

    total_loss_rate = cancelled_rate + return_rate
    st.metric("Total Funnel Loss", f"{total_loss_rate:.2f}%", delta=f"-{total_loss_rate:.2f}%", delta_color="inverse")

    st.info(f"💡 **Quick Win**: Reducing cancellations by 1% = R$ {(delivered_revenue * 0.01):,.2f}")

st.markdown("---")

# Performance by Seller
st.markdown("### 👥 Performance by Seller (Top 20)")

seller_perf = df[df['OrderStatus'] == 'Delivered'].groupby('SellerID').agg({
    'TotalAmount': ['sum', 'mean', 'count'],
    'Quantity': 'sum',
    'Discount': 'mean',
    'Net_Revenue': 'sum'
}).round(2)

seller_perf.columns = ['Revenue', 'Avg_Order_Value', 'Sales', 'Items', 'Avg_Discount', 'Net_Margin']
seller_perf['Margin_%'] = (seller_perf['Net_Margin'] / seller_perf['Revenue'] * 100).round(1)
seller_perf = seller_perf.sort_values('Revenue', ascending=False).head(20)

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=seller_perf.index,
        y=seller_perf['Revenue'],
        name='Revenue',
        marker_color='#8B5CF6',
        text=seller_perf['Revenue'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Revenue: R$ %{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Revenue Ranking by Seller',
        xaxis_title='Seller',
        yaxis_title='Revenue (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False, 'tickangle': -45},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=450,
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("#### 🏆 Highlights")

    best_seller = seller_perf.index[0]
    best_revenue = seller_perf.iloc[0]['Revenue']

    st.metric("Top Seller", best_seller, f"R$ {best_revenue:,.0f}")

    best_ticket = seller_perf['Avg_Order_Value'].idxmax()
    ticket_value = seller_perf.loc[best_ticket, 'Avg_Order_Value']

    st.metric("Highest Average Order Value", best_ticket, f"R$ {ticket_value:,.2f}")

    best_margin = seller_perf['Margin_%'].idxmax()
    margin_value = seller_perf.loc[best_margin, 'Margin_%']

    st.metric("Best Margin", best_margin, f"{margin_value:.1f}%")

# Detailed seller table
st.markdown("#### 📊 Detailed Performance Table")

st.dataframe(
    seller_perf.style.background_gradient(cmap='Purples', subset=['Revenue', 'Net_Margin'])
                     .format({
                         'Revenue': 'R$ {:,.2f}',
                         'Avg_Order_Value': 'R$ {:,.2f}',
                         'Sales': '{:,.0f}',
                         'Items': '{:,.0f}',
                         'Avg_Discount': '{:.1%}',
                         'Net_Margin': 'R$ {:,.2f}',
                         'Margin_%': '{:.1f}%'
                     }),
    width='stretch',
    height=400
)

st.markdown("---")

# Discount vs Margin analysis
st.markdown("### 💸 Discount Impact on Commercial Results")

col1, col2 = st.columns(2)

with col1:
    # Create discount ranges
    df['Discount_Range'] = pd.cut(df['Discount'], 
                                   bins=[0, 0.05, 0.10, 0.15, 0.20, 1.0],
                                   labels=['0-5%', '5-10%', '10-15%', '15-20%', '>20%'])
    
    discount_analysis = df.groupby('Discount_Range').agg({
        'TotalAmount': ['sum', 'mean', 'count'],
        'Net_Revenue': 'sum'
    }).round(2)
    
    discount_analysis.columns = ['Revenue', 'Avg_Order_Value', 'Sales', 'Margin']
    discount_analysis['Margin_%'] = (discount_analysis['Margin'] / discount_analysis['Revenue'] * 100).round(1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=discount_analysis.index.astype(str),
        y=discount_analysis['Revenue'],
        name='Revenue',
        marker_color='#8B5CF6',
        text=discount_analysis['Revenue'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))

    fig.update_layout(
        title='Revenue by Discount Range',
        xaxis_title='Discount Range',
        yaxis_title='Revenue (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=discount_analysis.index.astype(str),
        y=discount_analysis['Margin_%'],
        mode='lines+markers',
        name='Margin %',
        line=dict(color='#EF4444', width=3),
        marker=dict(size=12),
        text=discount_analysis['Margin_%'].apply(lambda x: f'{x:.1f}%'),
        textposition='top center'
    ))

    fig.update_layout(
        title='Margin (%) by Discount Range',
        xaxis_title='Discount Range',
        yaxis_title='Margin (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)', 'range': [0, max(discount_analysis['Margin_%']) * 1.2]},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Regional Performance
st.markdown("### 🗺️ Regional Performance (Top 10 States)")

state_perf = df[df['OrderStatus'] == 'Delivered'].groupby('State').agg({
    'TotalAmount': 'sum',
    'OrderID': 'count',
    'CustomerID': 'nunique'
}).round(2)

state_perf.columns = ['Revenue', 'Sales', 'Customers']
state_perf['Avg_Order_Value'] = (state_perf['Revenue'] / state_perf['Sales']).round(2)
state_perf = state_perf.sort_values('Revenue', ascending=False).head(10)

col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=state_perf.index[::-1],
        x=state_perf['Revenue'][::-1],
        orientation='h',
        marker=dict(
            color=state_perf['Revenue'][::-1],
            colorscale='Viridis',
            showscale=False
        ),
        text=state_perf['Revenue'][::-1].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Revenue: R$ %{x:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Top 10 States by Revenue',
        xaxis_title='Revenue (R$)',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': False},
        height=450
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.dataframe(
        state_perf.style.format({
            'Revenue': 'R$ {:,.2f}',
            'Sales': '{:,.0f}',
            'Customers': '{:,.0f}',
            'Avg_Order_Value': 'R$ {:,.2f}'
        }),
        width='stretch',
        height=450
    )

st.markdown("---")

# Insights Comerciais
st.markdown("### 💡 Strategic Commercial Insights")

col1, col2, col3 = st.columns(3)

with col1:
    # Calculate opportunity
    current_conversion = metrics['conversion_rate']
    target_conversion = 80.0
    revenue_opportunity = (delivered_revenue / current_conversion) * (target_conversion - current_conversion)

    display_insight_box(
        "Conversion Opportunity",
        f"Raising conversion from {current_conversion:.1f}% to {target_conversion:.0f}% = **R$ {revenue_opportunity:,.2f}** in additional revenue.",
        "🎯"
    )

with col2:
    # Best discount range
    best_discount_range = discount_analysis['Margin_%'].idxmax()
    best_margin = discount_analysis.loc[best_discount_range, 'Margin_%']

    display_insight_box(
        "Ideal Discount Zone",
        f"Discounts in the **{best_discount_range}** range keep the best margin ({best_margin:.1f}%). Guide your sellers.",
        "💰"
    )

with col3:
    # Top performer insight
    avg_seller_revenue = seller_perf['Revenue'].mean()
    top_seller_revenue = seller_perf.iloc[0]['Revenue']
    gap = top_seller_revenue - avg_seller_revenue

    display_insight_box(
        "Performance Gap",
        f"The top seller earns R$ {gap:,.2f} above the average. **Replicate the practices** of {best_seller}.",
        "🏆"
    )
