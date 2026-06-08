import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_processor import load_data, preprocess_data, get_top_products, get_category_performance
from utils import apply_custom_css, create_bar_chart, create_scatter_plot, display_insight_box
import pandas as pd

st.set_page_config(page_title="Product Performance", page_icon="🛍️", layout="wide")
apply_custom_css()

st.title("🛍️ Product Performance")
st.markdown("Detailed analysis of products, categories and brands")

# Load data
with st.spinner("Loading data..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Error loading data.")
        st.stop()
    df = preprocess_data(df_raw)

# Sidebar options
st.sidebar.header("⚙️ Options")

top_n = st.sidebar.slider("Number of Top Products", 5, 50, 20)

metric_choice = st.sidebar.radio(
    "Primary Metric",
    ["Revenue", "Quantity", "Orders"]
)

metric_map = {"Revenue": "revenue", "Quantity": "quantity", "Orders": "orders"}

# Category Performance Overview
st.markdown("### 📊 Performance by Category")

category_stats = get_category_performance(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    best_category = category_stats['Revenue'].idxmax()
    st.metric(
        "🏆 Leading Category",
        best_category,
        f"${category_stats.loc[best_category, 'Revenue']:,.0f}"
    )

with col2:
    total_categories = len(category_stats)
    st.metric("📦 Total Categories", total_categories)

with col3:
    avg_margin = category_stats['Avg_Margin'].mean()
    st.metric("💰 Average Margin", f"{avg_margin:.1f}%")

with col4:
    high_discount_cat = category_stats['Avg_Discount'].idxmax()
    st.metric(
        "🏷️ Highest Average Discount",
        high_discount_cat,
        f"{category_stats.loc[high_discount_cat, 'Avg_Discount']*100:.1f}%"
    )

# Category comparison table
st.markdown("#### 📋 Category Comparison")

st.dataframe(
    category_stats.style.background_gradient(cmap='Purples', subset=['Revenue', 'Net_Revenue'])
                        .format({
                            'Revenue': '${:,.2f}',
                            'Quantity': '{:,.0f}',
                            'Orders': '{:,.0f}',
                            'Avg_Price': '${:,.2f}',
                            'Avg_Discount': '{:.1%}',
                            'Net_Revenue': '${:,.2f}',
                            'Avg_Margin': '{:.1f}%'
                        }),
    width='stretch',
    height=300
)

st.markdown("---")

# Category visualizations
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💵 Revenue by Category")

    fig = px.bar(
        category_stats.reset_index(),
        x='Category',
        y='Revenue',
        color='Revenue',
        color_continuous_scale='Purples',
        text='Revenue'
    )

    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Revenue ($)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=450,
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("### 📈 Margin vs Discount by Category")
    
    fig = px.scatter(
        category_stats.reset_index(),
        x='Avg_Discount',
        y='Avg_Margin',
        size='Revenue',
        color='Category',
        hover_data=['Revenue', 'Orders'],
        text='Category'
    )
    
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        xaxis_title='Average Discount (%)',
        yaxis_title='Average Margin (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=450,
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Top Products
st.markdown(f"### 🏆 Top {top_n} Products - {metric_choice}")

top_products_data = get_top_products(df, top_n, metric_map[metric_choice])

if metric_choice == "Revenue":
    col_name = 'TotalAmount'
    prefix = '$'
elif metric_choice == "Quantity":
    col_name = 'Quantity'
    prefix = ''
else:
    col_name = 'ProductName'
    prefix = ''

fig = go.Figure()

colors = px.colors.sequential.Purples_r[:len(top_products_data)]

if metric_choice == "Revenue":
    values = top_products_data[col_name]
    text = [f'${v:,.0f}' for v in values]
elif metric_choice == "Quantity":
    values = top_products_data[col_name]
    text = [f'{v:,.0f}' for v in values]
else:
    values = top_products_data.iloc[:, 1]
    text = [f'{v:,}' for v in values]

fig.add_trace(go.Bar(
    y=top_products_data['ProductName'][::-1],
    x=values[::-1],
    orientation='h',
    marker=dict(
        color=values[::-1],
        colorscale='Purples',
        showscale=False
    ),
    text=text[::-1],
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>' + metric_choice + ': %{x:,.0f}<extra></extra>'
))

fig.update_layout(
    xaxis_title=metric_choice,
    yaxis_title='',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font={'color': '#F1F5F9'},
    xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
    yaxis={'showgrid': False},
    height=max(400, top_n * 20),
    margin=dict(l=200)
)

st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Brand Analysis
st.markdown("### 🏷️ Brand Analysis")

col1, col2 = st.columns([2, 1])

with col1:
    brand_revenue = df.groupby('Brand')['TotalAmount'].sum().nlargest(15).sort_values()
    
    fig = go.Figure(go.Bar(
        x=brand_revenue.values,
        y=brand_revenue.index,
        orientation='h',
        marker=dict(
            color=brand_revenue.values,
            colorscale='Viridis',
            showscale=False
        ),
        text=[f'${v:,.0f}' for v in brand_revenue.values],
        textposition='outside'
    ))
    
    fig.update_layout(
        xaxis_title='Revenue ($)',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': False},
        height=500,
        title='Top 15 Brands by Revenue'
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    top_brand = df.groupby('Brand')['TotalAmount'].sum().idxmax()
    top_brand_revenue = df.groupby('Brand')['TotalAmount'].sum().max()
    
    st.metric(
        "🥇 Brand #1",
        top_brand,
        f"${top_brand_revenue:,.0f}"
    )

    total_brands = df['Brand'].nunique()
    st.metric("🏷️ Total Brands", total_brands)
    
    # Market share
    total_revenue = df['TotalAmount'].sum()
    top_brand_share = (top_brand_revenue / total_revenue) * 100
    st.metric("📊 Market Share", f"{top_brand_share:.1f}%")

st.markdown("---")

# Price vs Quantity Analysis
st.markdown("### 💰 Price vs Quantity Analysis")

product_summary = df.groupby('ProductName').agg({
    'UnitPrice': 'mean',
    'Quantity': 'sum',
    'TotalAmount': 'sum',
    'Category': 'first'
}).reset_index()

product_summary = product_summary.nlargest(100, 'TotalAmount')

fig = px.scatter(
    product_summary,
    x='UnitPrice',
    y='Quantity',
    size='TotalAmount',
    color='Category',
    hover_name='ProductName',
    log_x=True,
    title='Relationship between Unit Price and Quantity Sold'
)

fig.update_layout(
    xaxis_title='Unit Price ($) - Log Scale',
    yaxis_title='Total Quantity Sold',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font={'color': '#F1F5F9'},
    xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
    yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
    height=500
)

st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Insights
st.markdown("### 💡 Product Insights")

col1, col2, col3 = st.columns(3)

with col1:
    top_product = df.groupby('ProductName')['TotalAmount'].sum().idxmax()
    top_product_revenue = df.groupby('ProductName')['TotalAmount'].sum().max()
    
    display_insight_box(
        "Top Product",
        f"{top_product[:40]}... generated ${top_product_revenue:,.2f} in revenue.",
        "🏆"
    )

with col2:
    most_profitable_cat = category_stats['Avg_Margin'].idxmax()
    margin = category_stats.loc[most_profitable_cat, 'Avg_Margin']
    
    display_insight_box(
        "Most Profitable Category",
        f"{most_profitable_cat} has an average margin of {margin:.1f}%.",
        "💰"
    )

with col3:
    total_products = df['ProductID'].nunique()
    avg_product_revenue = df.groupby('ProductID')['TotalAmount'].sum().mean()
    
    display_insight_box(
        "Diversification",
        f"{total_products} unique products with an average revenue of ${avg_product_revenue:,.2f}.",
        "📦"
    )
