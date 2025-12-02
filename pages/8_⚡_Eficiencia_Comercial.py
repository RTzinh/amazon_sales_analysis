import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import load_data, preprocess_data
from utils import apply_custom_css, display_insight_box
import pandas as pd
import numpy as np

st.set_page_config(page_title="Eficiência Comercial", page_icon="⚡", layout="wide")
apply_custom_css()

st.title("⚡ Eficiência e Gargalos Comerciais")
st.markdown("**Identificação de oportunidades de melhoria e otimização de processos**")

# Load data
with st.spinner("Carregando dados..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Erro ao carregar dados.")
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
st.markdown("### 🎯 Indicadores de Eficiência")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Taxa de Eficiência",
        f"{efficiency_rate:.1f}%",
        delta=f"+{efficiency_rate:.1f}%",
        help="Percentual de pedidos entregues com sucesso"
    )

with col2:
    st.metric(
        "Taxa de Perda",
        f"{loss_rate:.1f}%",
        delta=f"-{loss_rate:.1f}%",
        delta_color="inverse",
        help="Pedidos cancelados + devolvidos"
    )

with col3:
    st.metric(
        "Receita Perdida",
        f"R$ {lost_revenue:,.2f}",
        delta=f"-{(lost_revenue/total_revenue)*100:.1f}%",
        delta_color="inverse",
        help="Valor total em cancelamentos e devoluções"
    )

with col4:
    recovery_potential = lost_revenue * 0.3  # Assumindo 30% recuperável
    st.metric(
        "Potencial de Recuperação",
        f"R$ {recovery_potential:,.2f}",
        delta="+30% meta",
        help="Estimativa de receita recuperável com melhorias"
    )

st.markdown("---")

# Análise de Cancelamentos
st.markdown("### 🚫 Análise de Cancelamentos por Categoria")

cancelled_by_category = df[df['OrderStatus'] == 'Cancelled'].groupby('Category').agg({
    'OrderID': 'count',
    'TotalAmount': 'sum'
}).round(2)

cancelled_by_category.columns = ['Cancelamentos', 'Valor_Perdido']

# Calculate cancellation rate by category
total_by_category = df.groupby('Category')['OrderID'].count()
cancelled_by_category['Taxa_%'] = ((cancelled_by_category['Cancelamentos'] / total_by_category) * 100).round(2)
cancelled_by_category = cancelled_by_category.sort_values('Valor_Perdido', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=cancelled_by_category.index,
        y=cancelled_by_category['Cancelamentos'],
        name='Cancelamentos',
        marker_color='#EF4444',
        text=cancelled_by_category['Cancelamentos'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Cancelamentos: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Volume de Cancelamentos por Categoria',
        xaxis_title='Categoria',
        yaxis_title='Número de Cancelamentos',
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
        y=cancelled_by_category['Valor_Perdido'],
        name='Valor Perdido',
        marker_color='#F59E0B',
        text=cancelled_by_category['Valor_Perdido'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Valor Perdido em Cancelamentos',
        xaxis_title='Categoria',
        yaxis_title='Valor Perdido (R$)',
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
    cancelled_by_category.style.background_gradient(cmap='Reds', subset=['Taxa_%'])
                                .format({
                                    'Cancelamentos': '{:,.0f}',
                                    'Valor_Perdido': 'R$ {:,.2f}',
                                    'Taxa_%': '{:.2f}%'
                                }),
    width='stretch'
)

st.markdown("---")

# Análise de Produtos de Baixa Margem
st.markdown("### 💰 Produtos: Alto Volume vs Baixa Margem")

product_analysis = df[df['OrderStatus'] == 'Delivered'].groupby('ProductName').agg({
    'TotalAmount': 'sum',
    'Net_Revenue': 'sum',
    'OrderID': 'count',
    'Quantity': 'sum'
}).round(2)

product_analysis.columns = ['Faturamento', 'Margem_Liquida', 'Vendas', 'Quantidade']
product_analysis['Margem_%'] = (product_analysis['Margem_Liquida'] / product_analysis['Faturamento'] * 100).round(2)
product_analysis = product_analysis[product_analysis['Vendas'] >= 10]  # Produtos com volume significativo

# Identify problem products: high volume, low margin
low_margin_threshold = product_analysis['Margem_%'].quantile(0.25)
high_volume_threshold = product_analysis['Vendas'].quantile(0.75)

problem_products = product_analysis[
    (product_analysis['Margem_%'] <= low_margin_threshold) &
    (product_analysis['Vendas'] >= high_volume_threshold)
].sort_values('Faturamento', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    # Scatter plot: Sales vs Margin
    fig = px.scatter(
        product_analysis.reset_index().head(100),
        x='Vendas',
        y='Margem_%',
        size='Faturamento',
        color='Margem_%',
        hover_name='ProductName',
        hover_data={'Faturamento': ':R$ ,.2f', 'Vendas': ':,', 'Margem_%': ':.1f'},
        color_continuous_scale='RdYlGn',
        title='Matriz: Volume de Vendas vs Margem (%)'
    )
    
    # Add quadrant lines
    median_sales = product_analysis['Vendas'].median()
    median_margin = product_analysis['Margem_%'].median()
    
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
    st.markdown("#### ⚠️ Produtos Problemáticos")
    st.markdown(f"**{len(problem_products)}** produtos com alto volume mas baixa margem")
    
    if len(problem_products) > 0:
        st.markdown("**Top 5 para revisar:**")
        for idx, (prod, row) in enumerate(problem_products.head(5).iterrows(), 1):
            st.markdown(f"""
            **{idx}. {prod[:40]}...**  
            Margem: {row['Margem_%']:.1f}% | Vendas: {row['Vendas']:.0f}
            """)
        
        st.warning(f"💡 **Ação**: Revisar estratégia de preço/desconto nestes produtos")

st.markdown("---")

# Análise de Métodos de Pagamento
st.markdown("### 💳 Eficiência por Método de Pagamento")

payment_analysis = df.groupby(['PaymentMethod', 'OrderStatus']).size().unstack(fill_value=0)
payment_analysis['Total'] = payment_analysis.sum(axis=1)
payment_analysis['Taxa_Entrega_%'] = (payment_analysis.get('Delivered', 0) / payment_analysis['Total'] * 100).round(2)
payment_analysis = payment_analysis.sort_values('Taxa_Entrega_%', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    
    # Stacked bar for payment methods
    if 'Delivered' in payment_analysis.columns:
        fig.add_trace(go.Bar(
            x=payment_analysis.index,
            y=payment_analysis['Delivered'],
            name='Entregue',
            marker_color='#10B981'
        ))
    
    if 'Cancelled' in payment_analysis.columns:
        fig.add_trace(go.Bar(
            x=payment_analysis.index,
            y=payment_analysis['Cancelled'],
            name='Cancelado',
            marker_color='#EF4444'
        ))
    
    if 'Returned' in payment_analysis.columns:
        fig.add_trace(go.Bar(
            x=payment_analysis.index,
            y=payment_analysis['Returned'],
            name='Devolvido',
            marker_color='#F59E0B'
        ))
    
    fig.update_layout(
        title='Status de Pedidos por Método de Pagamento',
        xaxis_title='Método de Pagamento',
        yaxis_title='Número de Pedidos',
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
        y=payment_analysis['Taxa_Entrega_%'],
        marker_color='#8B5CF6',
        text=payment_analysis['Taxa_Entrega_%'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Taxa de Entrega: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Taxa de Entrega por Método de Pagamento',
        xaxis_title='Método de Pagamento',
        yaxis_title='Taxa de Entrega (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': False, 'tickangle': -45},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Quick Wins - Oportunidades Rápidas
st.markdown("### 🚀 Quick Wins - Oportunidades de Ganho Rápido")

col1, col2, col3 = st.columns(3)

with col1:
    # Quick Win 1: Reduzir cancelamentos na pior categoria
    worst_category = cancelled_by_category['Taxa_%'].idxmax()
    worst_rate = cancelled_by_category.loc[worst_category, 'Taxa_%']
    category_revenue = df[df['Category'] == worst_category]['TotalAmount'].sum()
    potential_gain = category_revenue * (worst_rate / 100) * 0.5  # Reduzir 50%
    
    display_insight_box(
        f"Quick Win #1: {worst_category}",
        f"Taxa de cancelamento: **{worst_rate:.1f}%**. Reduzir pela metade = **R$ {potential_gain:,.2f}**. Ação: investigar motivos e treinar equipe.",
        "🎯"
    )

with col2:
    # Quick Win 2: Focar no melhor método de pagamento
    best_payment = payment_analysis['Taxa_Entrega_%'].idxmax()
    best_rate = payment_analysis.loc[best_payment, 'Taxa_Entrega_%']
    
    display_insight_box(
        f"Quick Win #2: {best_payment}",
        f"Maior taxa de entrega: **{best_rate:.1f}%**. Incentivar uso deste método em campanhas e treinamentos de vendas.",
        "💳"
    )

with col3:
    # Quick Win 3: Corrigir produtos de alta rotação e baixa margem
    if len(problem_products) > 0:
        top_problem = problem_products.iloc[0]
        margin_impact = top_problem['Faturamento'] * 0.05  # Aumentar margem 5%
        
        display_insight_box(
            "Quick Win #3: Revisão de Preços",
            f"Ajustar margem dos {len(problem_products)} produtos críticos em +5% = **R$ {margin_impact * len(problem_products):,.2f}** adicionais.",
            "💰"
        )

st.markdown("---")

# Gargalos Operacionais
st.markdown("### 🔍 Gargalos Operacionais Identificados")

# Calculate operational bottlenecks
shipping_impact = (df['ShippingCost'].sum() / total_revenue) * 100
high_shipping = df[df['ShippingCost'] > df['ShippingCost'].quantile(0.90)]

tax_impact = (df['Tax'].sum() / total_revenue) * 100

discount_impact = (df['Discount_Amount'].sum() / total_revenue) * 100

col1, col2 = st.columns(2)

with col1:
    # Bottlenecks chart
    bottlenecks = pd.DataFrame({
        'Gargalo': ['Cancelamentos', 'Devoluções', 'Frete Alto', 'Descontos', 'Impostos'],
        'Impacto_%': [
            (cancelled / total_orders) * 100,
            (returned / total_orders) * 100,
            shipping_impact,
            discount_impact,
            tax_impact
        ],
        'Tipo': ['Perdas', 'Perdas', 'Custo', 'Custo', 'Custo']
    })
    
    bottlenecks = bottlenecks.sort_values('Impacto_%', ascending=True)
    
    fig = go.Figure()
    
    colors = ['#EF4444' if t == 'Perdas' else '#F59E0B' for t in bottlenecks['Tipo']]
    
    fig.add_trace(go.Bar(
        y=bottlenecks['Gargalo'],
        x=bottlenecks['Impacto_%'],
        orientation='h',
        marker_color=colors,
        text=bottlenecks['Impacto_%'].apply(lambda x: f'{x:.2f}%'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Impacto: %{x:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Principais Gargalos Operacionais',
        xaxis_title='Impacto (%)',
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
    st.markdown("#### 📋 Priorização de Ações")
    
    st.markdown("""
    **Prioridade 1 (Crítico):**
    - ⚠️ Reduzir cancelamentos na categoria com maior taxa
    - ⚠️ Revisar estratégia de desconto (impacto alto)
    
    **Prioridade 2 (Importante):**
    - 🔍 Otimizar custos de frete em pedidos de alto valor
    - 🔍 Investigar motivo de devoluções
    
    **Prioridade 3 (Melhoria):**
    - 💡 Treinar equipe no método de pagamento mais eficiente
    - 💡 Implementar processo de follow-up pós-venda
    """)
    
    st.info("**Meta**: Reduzir gargalos em 20% no próximo trimestre = **R$ {:.2f}** em ganhos".format(lost_revenue * 0.2))
