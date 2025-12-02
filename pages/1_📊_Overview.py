import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_processor import load_data, preprocess_data, get_summary_metrics, filter_data
from utils import apply_custom_css, create_metric_card, format_currency, create_timeline_chart, create_pie_chart, display_insight_box
import pandas as pd

st.set_page_config(page_title="Overview Dashboard", page_icon="📊", layout="wide")
apply_custom_css()

st.title("📊 Overview Dashboard")
st.markdown("Visão geral dos principais indicadores de desempenho")

# Load and process data
with st.spinner("Carregando dados..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Erro ao carregar dados. Verifique se o arquivo Amazon.csv está presente.")
        st.stop()
    
    df = preprocess_data(df_raw)

# Sidebar filters
st.sidebar.header("🎛️ Filtros")

# Date range filter
min_date = df['OrderDate'].min().date()
max_date = df['OrderDate'].max().date()

date_range = st.sidebar.date_input(
    "Período",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Convert to datetime
if len(date_range) == 2:
    date_filter = (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
else:
    date_filter = None

# Category filter
categories = st.sidebar.multiselect(
    "Categorias",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Country filter
countries = st.sidebar.multiselect(
    "Países",
    options=df['Country'].unique(),
    default=df['Country'].unique()
)

# Order status filter
statuses = st.sidebar.multiselect(
    "Status do Pedido",
    options=df['OrderStatus'].unique(),
    default=df['OrderStatus'].unique()
)

# Apply filters
df_filtered = filter_data(df, date_filter, categories, countries, statuses)

# Calculate metrics
metrics = get_summary_metrics(df_filtered)

# Display key metrics
st.markdown("### 💰 Principais Métricas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        create_metric_card(
            "Receita Total",
            metrics['total_revenue'],
            delta=None,
            prefix="$"
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        create_metric_card(
            "Total de Pedidos",
            metrics['total_orders'],
            delta=None
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        create_metric_card(
            "Ticket Médio",
            metrics['avg_order_value'],
            delta=None,
            prefix="$"
        ),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        create_metric_card(
            "Taxa de Conversão",
            metrics['conversion_rate'],
            delta=None,
            suffix="%"
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

# Second row of metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Clientes Únicos",
        f"{metrics['total_customers']:,}",
        help="Número total de clientes únicos"
    )

with col2:
    st.metric(
        "📦 Produtos Únicos",
        f"{metrics['total_products']:,}",
        help="Número total de produtos vendidos"
    )

with col3:
    st.metric(
        "🚫 Taxa de Cancelamento",
        f"{metrics['cancellation_rate']:.1f}%",
        delta=f"-{metrics['cancellation_rate']:.1f}%",
        delta_color="inverse",
        help="Porcentagem de pedidos cancelados"
    )

with col4:
    st.metric(
        "↩️ Taxa de Retorno",
        f"{metrics['return_rate']:.1f}%",
        delta=f"-{metrics['return_rate']:.1f}%",
        delta_color="inverse",
        help="Porcentagem de pedidos retornados"
    )

st.markdown("---")

# Revenue trend and status breakdown
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Tendência de Vendas")
    
    # Daily revenue trend
    daily_revenue = df_filtered.groupby(df_filtered['OrderDate'].dt.date)['TotalAmount'].sum().reset_index()
    daily_revenue.columns = ['Date', 'Revenue']
    
    fig = create_timeline_chart(daily_revenue, 'Date', 'Revenue', 'Receita Diária')
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("### 📊 Status dos Pedidos")
    
    status_counts = df_filtered['OrderStatus'].value_counts()
    fig = create_pie_chart(
        status_counts.values,
        status_counts.index,
        ''
    )
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Category and Payment analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛍️ Receita por Categoria")
    
    category_revenue = df_filtered.groupby('Category')['TotalAmount'].sum().sort_values(ascending=True)
    
    fig = go.Figure(go.Bar(
        x=category_revenue.values,
        y=category_revenue.index,
        orientation='h',
        marker=dict(
            color=category_revenue.values,
            colorscale='Purples',
            showscale=False
        ),
        text=[f'${v:,.0f}' for v in category_revenue.values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='',
        xaxis_title='Receita ($)',
        yaxis_title='',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': False}
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("### 💳 Métodos de Pagamento")
    
    payment_counts = df_filtered['PaymentMethod'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=payment_counts.index,
        values=payment_counts.values,
        hole=0.4,
        marker=dict(colors=px.colors.sequential.Purples_r),
        textposition='inside',
        textinfo='percent+label'
    )])
    
    fig.update_layout(
        title='',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Quick Insights
st.markdown("### 💡 Insights Rápidos")

col1, col2, col3 = st.columns(3)

with col1:
    top_category = df_filtered.groupby('Category')['TotalAmount'].sum().idxmax()
    top_category_revenue = df_filtered.groupby('Category')['TotalAmount'].sum().max()
    
    display_insight_box(
        "Categoria Líder",
        f"{top_category} é a categoria mais lucrativa com {format_currency(top_category_revenue)} em vendas.",
        "🏆"
    )

with col2:
    top_country = df_filtered.groupby('Country')['TotalAmount'].sum().idxmax()
    country_pct = (df_filtered[df_filtered['Country'] == top_country]['TotalAmount'].sum() / metrics['total_revenue']) * 100
    
    display_insight_box(
        "Mercado Principal",
        f"{top_country} representa {country_pct:.1f}% da receita total.",
        "🌍"
    )

with col3:
    avg_items = df_filtered['Quantity'].mean()
    
    display_insight_box(
        "Comportamento de Compra",
        f"Em média, clientes compram {avg_items:.1f} itens por pedido.",
        "🛒"
    )

# Data summary
with st.expander("📋 Ver Resumo dos Dados"):
    st.dataframe(
        df_filtered.describe(),
        width='stretch'
    )
