import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import load_data, preprocess_data
from utils import apply_custom_css, display_insight_box
import pandas as pd
import numpy as np

st.set_page_config(page_title="Commercial Efficiency", page_icon="⚡", layout="wide")
apply_custom_css()

st.title("⚡ Commercial Efficiency and Bottlenecks")
st.markdown("**Identifying improvement opportunities and process optimization**")

# Load data
with st.spinner("Loading data..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Error loading data.")
        st.stop()
    df = preprocess_data(df_raw)

# Calculate efficiency metrics
total_orders = len(df)
delivered = len(df[df['OrderStatus'] == 'Delivered'])
cancelled = len(df[df['OrderStatus'] == 'Cancelled'])
returned = len(df[df['OrderStatus'] == 'Returned'])
pending = len(df[df['OrderStatus'] == 'Pending'])

efficiency_rate = (delivered / total_orders) * 100
loss_rate = ((cancelled + returned) / total_orders) * 100

total_revenue = df['TotalAmount'].sum()
lost_revenue = df[df['OrderStatus'].isin(['Cancelled', 'Returned'])]['TotalAmount'].sum()

# Header metrics
st.markdown("### 🎯 Efficiency Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Efficiency Rate",
        f"{efficiency_rate:.1f}%",
        delta=f"+{efficiency_rate:.1f}%",
        help="Percentage of orders successfully delivered"
    )

with col2:
    st.metric(
        "Loss Rate",
        f"{loss_rate:.1f}%",
        delta=f"-{loss_rate:.1f}%",
        delta_color="inverse",
        help="Cancelled + returned orders"
    )

with col3:
    st.metric(
        "Lost Revenue",
        f"R$ {lost_revenue:,.2f}",
        delta=f"-{(lost_revenue/total_revenue)*100:.1f}%",
        delta_color="inverse",
        help="Total value in cancellations and returns"
    )

with col4:
    recovery_potential = lost_revenue * 0.3  # Assuming 30% recoverable
    st.metric(
        "Recovery Potential",
        f"R$ {recovery_potential:,.2f}",
        delta="+30% target",
        help="Estimated recoverable revenue with improvements"
    )

st.markdown("---")

# Cancellation analysis
st.markdown("### 🚫 Cancellation Analysis by Category")

cancelled_by_category = df[df['OrderStatus'] == 'Cancelled'].groupby('Category').agg({
    'OrderID': 'count',
    'TotalAmount': 'sum'
}).round(2)

cancelled_by_category.columns = ['Cancellations', 'Lost_Value']

# Calculate cancellation rate by category
total_by_category = df.groupby('Category')['OrderID'].count()
cancelled_by_category['Rate_%'] = ((cancelled_by_category['Cancellations'] / total_by_category) * 100).round(2)
cancelled_by_category = cancelled_by_category.sort_values('Lost_Value', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=cancelled_by_category.index,
        y=cancelled_by_category['Cancellations'],
        name='Cancellations',
        marker_color='#EF4444',
        text=cancelled_by_category['Cancellations'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Cancellations: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title='Cancellation Volume by Category',
        xaxis_title='Category',
        yaxis_title='Number of Cancellations',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False, 'tickangle': -45},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=cancelled_by_category.index,
        y=cancelled_by_category['Lost_Value'],
        name='Lost Value',
        marker_color='#F59E0B',
        text=cancelled_by_category['Lost_Value'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Value: R$ %{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Lost Value in Cancellations',
        xaxis_title='Category',
        yaxis_title='Lost Value (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False, 'tickangle': -45},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

# Cancellation rate table
st.dataframe(
    cancelled_by_category.style.background_gradient(cmap='Reds', subset=['Rate_%'])
                                .format({
                                    'Cancellations': '{:,.0f}',
                                    'Lost_Value': 'R$ {:,.2f}',
                                    'Rate_%': '{:.2f}%'
                                }),
    width='stretch'
)

st.markdown("---")

# Low-margin products analysis
st.markdown("### 💰 Products: High Volume vs Low Margin")

product_analysis = df[df['OrderStatus'] == 'Delivered'].groupby('ProductName').agg({
    'TotalAmount': 'sum',
    'Net_Revenue': 'sum',
    'OrderID': 'count',
    'Quantity': 'sum'
}).round(2)

product_analysis.columns = ['Revenue', 'Net_Margin', 'Sales', 'Quantity']
product_analysis['Margin_%'] = (product_analysis['Net_Margin'] / product_analysis['Revenue'] * 100).round(2)
product_analysis = product_analysis[product_analysis['Sales'] >= 10]  # Products with significant volume

# Identify problem products: high volume, low margin
low_margin_threshold = product_analysis['Margin_%'].quantile(0.25)
high_volume_threshold = product_analysis['Sales'].quantile(0.75)

problem_products = product_analysis[
    (product_analysis['Margin_%'] <= low_margin_threshold) &
    (product_analysis['Sales'] >= high_volume_threshold)
].sort_values('Revenue', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    # Scatter plot: Sales vs Margin
    fig = px.scatter(
        product_analysis.reset_index().head(100),
        x='Sales',
        y='Margin_%',
        size='Revenue',
        color='Margin_%',
        hover_name='ProductName',
        hover_data={'Revenue': ':R$ ,.2f', 'Sales': ':,', 'Margin_%': ':.1f'},
        color_continuous_scale='RdYlGn',
        title='Matrix: Sales Volume vs Margin (%)'
    )

    # Add quadrant lines
    median_sales = product_analysis['Sales'].median()
    median_margin = product_analysis['Margin_%'].median()
    
    fig.add_hline(y=median_margin, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=median_sales, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=500
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("#### ⚠️ Problem Products")
    st.markdown(f"**{len(problem_products)}** products with high volume but low margin")

    if len(problem_products) > 0:
        st.markdown("**Top 5 to review:**")
        for idx, (prod, row) in enumerate(problem_products.head(5).iterrows(), 1):
            st.markdown(f"""
            **{idx}. {prod[:40]}...**
            Margin: {row['Margin_%']:.1f}% | Sales: {row['Sales']:.0f}
            """)

        st.warning(f"💡 **Action**: Review the price/discount strategy for these products")

st.markdown("---")

# Payment methods analysis
st.markdown("### 💳 Efficiency by Payment Method")

payment_analysis = df.groupby(['PaymentMethod', 'OrderStatus']).size().unstack(fill_value=0)
payment_analysis['Total'] = payment_analysis.sum(axis=1)
payment_analysis['Delivery_Rate_%'] = (payment_analysis.get('Delivered', 0) / payment_analysis['Total'] * 100).round(2)
payment_analysis = payment_analysis.sort_values('Delivery_Rate_%', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()

    # Stacked bar for payment methods
    if 'Delivered' in payment_analysis.columns:
        fig.add_trace(go.Bar(
            x=payment_analysis.index,
            y=payment_analysis['Delivered'],
            name='Delivered',
            marker_color='#10B981'
        ))

    if 'Cancelled' in payment_analysis.columns:
        fig.add_trace(go.Bar(
            x=payment_analysis.index,
            y=payment_analysis['Cancelled'],
            name='Cancelled',
            marker_color='#EF4444'
        ))

    if 'Returned' in payment_analysis.columns:
        fig.add_trace(go.Bar(
            x=payment_analysis.index,
            y=payment_analysis['Returned'],
            name='Returned',
            marker_color='#F59E0B'
        ))

    fig.update_layout(
        title='Order Status by Payment Method',
        xaxis_title='Payment Method',
        yaxis_title='Number of Orders',
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False, 'tickangle': -45},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=payment_analysis.index,
        y=payment_analysis['Delivery_Rate_%'],
        marker_color='#8B5CF6',
        text=payment_analysis['Delivery_Rate_%'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Delivery Rate: %{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title='Delivery Rate by Payment Method',
        xaxis_title='Payment Method',
        yaxis_title='Delivery Rate (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False, 'tickangle': -45},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Quick Wins - fast-win opportunities
st.markdown("### 🚀 Quick Wins - Fast-Win Opportunities")

col1, col2, col3 = st.columns(3)

with col1:
    # Quick Win 1: Reduce cancellations in the worst category
    worst_category = cancelled_by_category['Rate_%'].idxmax()
    worst_rate = cancelled_by_category.loc[worst_category, 'Rate_%']
    category_revenue = df[df['Category'] == worst_category]['TotalAmount'].sum()
    potential_gain = category_revenue * (worst_rate / 100) * 0.5  # Reduce by 50%

    display_insight_box(
        f"Quick Win #1: {worst_category}",
        f"Cancellation rate: **{worst_rate:.1f}%**. Cutting it in half = **R$ {potential_gain:,.2f}**. Action: investigate the causes and train the team.",
        "🎯"
    )

with col2:
    # Quick Win 2: Focus on the best payment method
    best_payment = payment_analysis['Delivery_Rate_%'].idxmax()
    best_rate = payment_analysis.loc[best_payment, 'Delivery_Rate_%']

    display_insight_box(
        f"Quick Win #2: {best_payment}",
        f"Highest delivery rate: **{best_rate:.1f}%**. Encourage use of this method in campaigns and sales training.",
        "💳"
    )

with col3:
    # Quick Win 3: Fix high-turnover, low-margin products
    if len(problem_products) > 0:
        top_problem = problem_products.iloc[0]
        margin_impact = top_problem['Revenue'] * 0.05  # Increase margin by 5%

        display_insight_box(
            "Quick Win #3: Price Review",
            f"Adjusting the margin of the {len(problem_products)} critical products by +5% = **R$ {margin_impact * len(problem_products):,.2f}** in additional revenue.",
            "💰"
        )

st.markdown("---")

# Operational bottlenecks
st.markdown("### 🔍 Identified Operational Bottlenecks")

# Calculate operational bottlenecks
shipping_impact = (df['ShippingCost'].sum() / total_revenue) * 100
high_shipping = df[df['ShippingCost'] > df['ShippingCost'].quantile(0.90)]

tax_impact = (df['Tax'].sum() / total_revenue) * 100

discount_impact = (df['Discount_Amount'].sum() / total_revenue) * 100

col1, col2 = st.columns(2)

with col1:
    # Bottlenecks chart
    bottlenecks = pd.DataFrame({
        'Bottleneck': ['Cancellations', 'Returns', 'High Shipping', 'Discounts', 'Taxes'],
        'Impact_%': [
            (cancelled / total_orders) * 100,
            (returned / total_orders) * 100,
            shipping_impact,
            discount_impact,
            tax_impact
        ],
        'Type': ['Losses', 'Losses', 'Cost', 'Cost', 'Cost']
    })

    bottlenecks = bottlenecks.sort_values('Impact_%', ascending=True)

    fig = go.Figure()

    colors = ['#EF4444' if t == 'Losses' else '#F59E0B' for t in bottlenecks['Type']]

    fig.add_trace(go.Bar(
        y=bottlenecks['Bottleneck'],
        x=bottlenecks['Impact_%'],
        orientation='h',
        marker_color=colors,
        text=bottlenecks['Impact_%'].apply(lambda x: f'{x:.2f}%'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Impact: %{x:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title='Top Operational Bottlenecks',
        xaxis_title='Impact (%)',
        yaxis_title='',
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
    st.markdown("#### 📋 Action Prioritization")

    st.markdown("""
    **Priority 1 (Critical):**
    - ⚠️ Reduce cancellations in the highest-rate category
    - ⚠️ Review the discount strategy (high impact)

    **Priority 2 (Important):**
    - 🔍 Optimize shipping costs on high-value orders
    - 🔍 Investigate the reason for returns

    **Priority 3 (Improvement):**
    - 💡 Train the team on the most efficient payment method
    - 💡 Implement a post-sale follow-up process
    """)

    st.info("**Target**: Reducing bottlenecks by 20% next quarter = **R$ {:.2f}** in gains".format(lost_revenue * 0.2))
