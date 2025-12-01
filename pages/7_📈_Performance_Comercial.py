import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import load_data, preprocess_data, get_summary_metrics
from utils import apply_custom_css, display_insight_box
import pandas as pd
import numpy as np

st.set_page_config(page_title="Performance Comercial", page_icon="📈", layout="wide")
apply_custom_css()

st.title("📈 Performance Comercial")
st.markdown("**Análise de KPIs Essenciais para Gestão Comercial**")

# Load data
with st.spinner("Carregando dados..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Erro ao carregar dados.")
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
st.markdown("### 💰 Indicadores de Performance")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Faturamento Real",
        f"R$ {delivered_revenue:,.2f}",
        delta=f"{metrics['conversion_rate']:.1f}% converte",
        help="Receita de pedidos entregues (excluindo cancelamentos)"
    )

with col2:
    st.metric(
        "Ticket Médio",
        f"R$ {metrics['avg_order_value']:.2f}",
        help="Valor médio por pedido"
    )

with col3:
    st.metric(
        "Margem Comercial",
        f"{gross_margin_pct:.1f}%",
        help="Margem líquida após impostos e frete"
    )

with col4:
    st.metric(
        "Perdas Comerciais",
        f"R$ {lost_revenue:,.2f}",
        delta=f"-{(lost_revenue/total_revenue)*100:.1f}%",
        delta_color="inverse",
        help="Receita perdida por cancelamentos e devoluções"
    )

with col5:
    st.metric(
        "Desconto Médio",
        f"{avg_discount:.1f}%",
        help="Desconto médio aplicado nas vendas"
    )

st.markdown("---")

# Funnel de conversão
st.markdown("### 🎯 Funil de Conversão Comercial")

col1, col2 = st.columns([2, 1])

with col1:
    stages = ['Pedidos Totais', 'Enviados', 'Entregues']
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
        title='Pipeline de Pedidos',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 🔍 Análise de Perdas")
    
    cancelled_rate = (metrics['cancelled_orders'] / metrics['total_orders']) * 100
    return_rate = metrics['return_rate']
    
    st.metric("Taxa de Cancelamento", f"{cancelled_rate:.2f}%", delta=f"-{cancelled_rate:.2f}%", delta_color="inverse")
    st.metric("Taxa de Devolução", f"{return_rate:.2f}%", delta=f"-{return_rate:.2f}%", delta_color="inverse")
    
    total_loss_rate = cancelled_rate + return_rate
    st.metric("Perda Total no Funil", f"{total_loss_rate:.2f}%", delta=f"-{total_loss_rate:.2f}%", delta_color="inverse")
    
    st.info(f"💡 **Quick Win**: Reduzir cancelamentos em 1% = R$ {(delivered_revenue * 0.01):,.2f}")

st.markdown("---")

# Performance por Vendedor
st.markdown("### 👥 Performance por Vendedor (Top 20)")

seller_perf = df[df['OrderStatus'] == 'Delivered'].groupby('SellerID').agg({
    'TotalAmount': ['sum', 'mean', 'count'],
    'Quantity': 'sum',
    'Discount': 'mean',
    'Net_Revenue': 'sum'
}).round(2)

seller_perf.columns = ['Faturamento', 'Ticket_Medio', 'Vendas', 'Itens', 'Desc_Medio', 'Margem_Liquida']
seller_perf['Margem_%'] = (seller_perf['Margem_Liquida'] / seller_perf['Faturamento'] * 100).round(1)
seller_perf = seller_perf.sort_values('Faturamento', ascending=False).head(20)

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=seller_perf.index,
        y=seller_perf['Faturamento'],
        name='Faturamento',
        marker_color='#8B5CF6',
        text=seller_perf['Faturamento'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Ranking de Faturamento por Vendedor',
        xaxis_title='Vendedor',
        yaxis_title='Faturamento (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False, 'tickangle': -45},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=450,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 🏆 Destaques")
    
    best_seller = seller_perf.index[0]
    best_revenue = seller_perf.iloc[0]['Faturamento']
    
    st.metric("Top Vendedor", best_seller, f"R$ {best_revenue:,.0f}")
    
    best_ticket = seller_perf['Ticket_Medio'].idxmax()
    ticket_value = seller_perf.loc[best_ticket, 'Ticket_Medio']
    
    st.metric("Maior Ticket Médio", best_ticket, f"R$ {ticket_value:,.2f}")
    
    best_margin = seller_perf['Margem_%'].idxmax()
    margin_value = seller_perf.loc[best_margin, 'Margem_%']
    
    st.metric("Melhor Margem", best_margin, f"{margin_value:.1f}%")

# Detailed seller table
st.markdown("#### 📊 Tabela Detalhada de Performance")

st.dataframe(
    seller_perf.style.background_gradient(cmap='Purples', subset=['Faturamento', 'Margem_Liquida'])
                     .format({
                         'Faturamento': 'R$ {:,.2f}',
                         'Ticket_Medio': 'R$ {:,.2f}',
                         'Vendas': '{:,.0f}',
                         'Itens': '{:,.0f}',
                         'Desc_Medio': '{:.1%}',
                         'Margem_Liquida': 'R$ {:,.2f}',
                         'Margem_%': '{:.1f}%'
                     }),
    use_container_width=True,
    height=400
)

st.markdown("---")

# Análise de Desconto vs Margem
st.markdown("### 💸 Impacto do Desconto no Resultado Comercial")

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
    
    discount_analysis.columns = ['Faturamento', 'Ticket_Medio', 'Vendas', 'Margem']
    discount_analysis['Margem_%'] = (discount_analysis['Margem'] / discount_analysis['Faturamento'] * 100).round(1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=discount_analysis.index.astype(str),
        y=discount_analysis['Faturamento'],
        name='Faturamento',
        marker_color='#8B5CF6',
        text=discount_analysis['Faturamento'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Faturamento por Faixa de Desconto',
        xaxis_title='Faixa de Desconto',
        yaxis_title='Faturamento (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=discount_analysis.index.astype(str),
        y=discount_analysis['Margem_%'],
        mode='lines+markers',
        name='Margem %',
        line=dict(color='#EF4444', width=3),
        marker=dict(size=12),
        text=discount_analysis['Margem_%'].apply(lambda x: f'{x:.1f}%'),
        textposition='top center'
    ))
    
    fig.update_layout(
        title='Margem (%) por Faixa de Desconto',
        xaxis_title='Faixa de Desconto',
        yaxis_title='Margem (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)', 'range': [0, max(discount_analysis['Margem_%']) * 1.2]},
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Regional Performance
st.markdown("### 🗺️ Performance Regional (Top 10 Estados)")

state_perf = df[df['OrderStatus'] == 'Delivered'].groupby('State').agg({
    'TotalAmount': 'sum',
    'OrderID': 'count',
    'CustomerID': 'nunique'
}).round(2)

state_perf.columns = ['Faturamento', 'Vendas', 'Clientes']
state_perf['Ticket_Medio'] = (state_perf['Faturamento'] / state_perf['Vendas']).round(2)
state_perf = state_perf.sort_values('Faturamento', ascending=False).head(10)

col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=state_perf.index[::-1],
        x=state_perf['Faturamento'][::-1],
        orientation='h',
        marker=dict(
            color=state_perf['Faturamento'][::-1],
            colorscale='Viridis',
            showscale=False
        ),
        text=state_perf['Faturamento'][::-1].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Top 10 Estados por Faturamento',
        xaxis_title='Faturamento (R$)',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': False},
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(
        state_perf.style.format({
            'Faturamento': 'R$ {:,.2f}',
            'Vendas': '{:,.0f}',
            'Clientes': '{:,.0f}',
            'Ticket_Medio': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        height=450
    )

st.markdown("---")

# Insights Comerciais
st.markdown("### 💡 Insights Comerciais Estratégicos")

col1, col2, col3 = st.columns(3)

with col1:
    # Calculate opportunity
    current_conversion = metrics['conversion_rate']
    target_conversion = 80.0
    revenue_opportunity = (delivered_revenue / current_conversion) * (target_conversion - current_conversion)
    
    display_insight_box(
        "Oportunidade de Conversão",
        f"Aumentar conversão de {current_conversion:.1f}% para {target_conversion:.0f}% = **R$ {revenue_opportunity:,.2f}** adicionais.",
        "🎯"
    )

with col2:
    # Best discount range
    best_discount_range = discount_analysis['Margem_%'].idxmax()
    best_margin = discount_analysis.loc[best_discount_range, 'Margem_%']
    
    display_insight_box(
        "Zona Ideal de Desconto",
        f"Desconto na faixa **{best_discount_range}** mantém melhor margem ({best_margin:.1f}%). Orientar vendedores.",
        "💰"
    )

with col3:
    # Top performer insight
    avg_seller_revenue = seller_perf['Faturamento'].mean()
    top_seller_revenue = seller_perf.iloc[0]['Faturamento']
    gap = top_seller_revenue - avg_seller_revenue
    
    display_insight_box(
        "Gap de Performance",
        f"Top vendedor fatura R$ {gap:,.2f} acima da média. **Replicar práticas** do {best_seller}.",
        "🏆"
    )
