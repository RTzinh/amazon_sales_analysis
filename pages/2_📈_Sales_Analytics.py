import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import load_data, preprocess_data, get_time_series_data
from utils import apply_custom_css, create_timeline_chart, display_insight_box
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sales Analytics", page_icon="📈", layout="wide")
apply_custom_css()

st.title("📈 Sales Analytics")
st.markdown("Análise temporal de vendas, tendências e padrões sazonais")

# Load data
with st.spinner("Carregando dados..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Erro ao carregar dados.")
        st.stop()
    df = preprocess_data(df_raw)

# Sidebar options
st.sidebar.header("⚙️ Configurações")

aggregation_level = st.sidebar.selectbox(
    "Nível de Agregação",
    ["Diário", "Semanal", "Mensal"],
    index=2
)

# Map to pandas frequency
freq_map = {"Diário": "D", "Semanal": "W", "Mensal": "M"}
freq = freq_map[aggregation_level]

# Get time series data
ts_data = get_time_series_data(df, freq)

# Main metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_revenue = ts_data['Revenue'].sum()
    st.metric("💰 Receita Total", f"${total_revenue:,.2f}")

with col2:
    total_orders = ts_data['Orders'].sum()
    st.metric("📦 Total de Pedidos", f"{total_orders:,}")

with col3:
    avg_daily_revenue = ts_data['Revenue'].mean()
    st.metric(f"📊 Média {aggregation_level}", f"${avg_daily_revenue:,.2f}")

st.markdown("---")

# Revenue trend
st.markdown(f"### 📈 Tendência de Vendas ({aggregation_level})")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=ts_data['Date'],
    y=ts_data['Revenue'],
    mode='lines+markers',
    name='Receita',
    line=dict(color='#8B5CF6', width=3),
    fill='tozeroy',
    fillcolor='rgba(139, 92, 246, 0.1)',
    marker=dict(size=6)
))

# Add trend line
z = np.polyfit(range(len(ts_data)), ts_data['Revenue'], 1)
p = np.poly1d(z)
trend_line = p(range(len(ts_data)))

fig.add_trace(go.Scatter(
    x=ts_data['Date'],
    y=trend_line,
    mode='lines',
    name='Tendência',
    line=dict(color='#EF4444', width=2, dash='dash')
))

fig.update_layout(
    xaxis_title='Data',
    yaxis_title='Receita ($)',
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font={'color': '#F1F5F9'},
    xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
    yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
    height=450,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Dual chart: Revenue and Orders
st.markdown("### 📊 Receita vs Pedidos")

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=ts_data['Date'],
        y=ts_data['Revenue'],
        name='Receita',
        marker_color='#8B5CF6',
        opacity=0.7
    ),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(
        x=ts_data['Date'],
        y=ts_data['Orders'],
        name='Pedidos',
        line=dict(color='#10B981', width=3),
        mode='lines+markers'
    ),
    secondary_y=True,
)

fig.update_xaxes(title_text="Data")
fig.update_yaxes(title_text="Receita ($)", secondary_y=False)
fig.update_yaxes(title_text="Número de Pedidos", secondary_y=True)

fig.update_layout(
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font={'color': '#F1F5F9'},
    height=450,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Monthly and Day of Week analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Vendas por Mês")
    
    monthly_sales = df.groupby('MonthName')['TotalAmount'].sum().reindex([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]).fillna(0)
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(range(1, 13)),
            y=monthly_sales.values,
            marker=dict(
                color=monthly_sales.values,
                colorscale='Purples',
                showscale=False
            ),
            text=[f'${v:,.0f}' for v in monthly_sales.values],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                     'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            showgrid=False
        ),
        yaxis=dict(title='Receita ($)', showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📆 Vendas por Dia da Semana")
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_sales = df.groupby('DayOfWeek')['TotalAmount'].sum().reindex(day_order)
    
    day_labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    
    fig = go.Figure(data=[
        go.Bar(
            x=day_labels,
            y=day_sales.values,
            marker=dict(
                color=['#8B5CF6' if i < 5 else '#3B82F6' for i in range(7)],
                opacity=0.8
            ),
            text=[f'${v:,.0f}' for v in day_sales.values],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        xaxis=dict(title='', showgrid=False),
        yaxis=dict(title='Receita ($)', showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Growth analysis
st.markdown("### 📊 Análise de Crescimento")

if freq == 'M':
    # Calculate month-over-month growth
    ts_data['Growth'] = ts_data['Revenue'].pct_change() * 100
    ts_data['Growth_Color'] = ts_data['Growth'].apply(lambda x: '#10B981' if x >= 0 else '#EF4444')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=ts_data['Date'][1:],
        y=ts_data['Growth'][1:],
        marker_color=ts_data['Growth_Color'][1:],
        text=[f'{v:.1f}%' for v in ts_data['Growth'][1:]],
        textposition='outside',
        name='Crescimento MoM'
    ))
    
    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Crescimento (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)', 'zeroline': True},
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Growth stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_growth = ts_data['Growth'].mean()
        st.metric("📈 Crescimento Médio MoM", f"{avg_growth:.1f}%")
    
    with col2:
        max_growth = ts_data['Growth'].max()
        st.metric("🚀 Maior Crescimento", f"{max_growth:.1f}%")
    
    with col3:
        min_growth = ts_data['Growth'].min()
        st.metric("📉 Maior Queda", f"{min_growth:.1f}%")

st.markdown("---")

# Insights
st.markdown("### 💡 Insights de Tendências")

col1, col2, col3 = st.columns(3)

with col1:
    best_month = monthly_sales.idxmax()
    best_month_value = monthly_sales.max()
    
    display_insight_box(
        "Melhor Mês",
        f"{best_month} teve o melhor desempenho com ${best_month_value:,.2f} em vendas.",
        "🏆"
    )

with col2:
    best_day = day_sales.idxmax()
    day_map = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
               'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    
    display_insight_box(
        "Melhor Dia",
        f"{day_map[best_day]} é o dia mais forte em vendas.",
        "📅"
    )

with col3:
    if z[0] > 0:
        trend_text = "crescimento"
        icon = "📈"
    else:
        trend_text = "queda"
        icon = "📉"
    
    display_insight_box(
        "Tendência Geral",
        f"As vendas apresentam tendência de {trend_text} ao longo do período.",
        icon
    )

from plotly.subplots import make_subplots
