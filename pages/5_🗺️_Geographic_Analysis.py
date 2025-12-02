import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_processor import load_data, preprocess_data, get_geographic_summary
from utils import apply_custom_css, display_insight_box
import pandas as pd

st.set_page_config(page_title="Geographic Analysis", page_icon="🗺️", layout="wide")
apply_custom_css()

st.title("🗺️ Geographic Analysis")
st.markdown("Distribuição geográfica de vendas e análise regional")

# Load data
with st.spinner("Carregando dados..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Erro ao carregar dados.")
        st.stop()
    df = preprocess_data(df_raw)

# Geographic summary
geo_summary = get_geographic_summary(df)

# Country metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_countries = df['Country'].nunique()
    st.metric("🌍 Países Ativos", total_countries)

with col2:
    top_country = geo_summary.index[0]
    st.metric("🏆 País Líder", top_country)

with col3:
    top_country_revenue = geo_summary.iloc[0]['Revenue']
    st.metric("💰 Receita do Líder", f"${top_country_revenue:,.2f}")

with col4:
    total_cities = df['City'].nunique()
    st.metric("🏙️ Cidades Atendidas", total_cities)

st.markdown("---")

# World map
st.markdown("### 🌎 Mapa de Vendas por País")

country_data = df.groupby('Country').agg({
    'TotalAmount': 'sum',
    'OrderID': 'count'
}).reset_index()

country_data.columns = ['Country', 'Revenue', 'Orders']

# Map country names to ISO codes
country_iso_map = {
    'United States': 'USA',
    'India': 'IND',
    'Canada': 'CAN',
    'United Kingdom': 'GBR',
    'Australia': 'AUS'
}

country_data['iso_alpha'] = country_data['Country'].map(country_iso_map)

fig = px.choropleth(
    country_data,
    locations='iso_alpha',
    color='Revenue',
    hover_name='Country',
    hover_data={'Revenue': ':$,.2f', 'Orders': ':,', 'iso_alpha': False},
    color_continuous_scale='Purples',
    title=''
)

fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth',
        bgcolor='rgba(0,0,0,0)'
    ),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font={'color': '#F1F5F9'},
    height=500
)

st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Country comparison
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💵 Receita por País")
    
    fig = go.Figure(data=[
        go.Bar(
            y=geo_summary.index,
            x=geo_summary['Revenue'],
            orientation='h',
            marker=dict(
                color=geo_summary['Revenue'],
                colorscale='Purples',
                showscale=False
            ),
            text=[f'${v:,.0f}' for v in geo_summary['Revenue']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        xaxis_title='Receita ($)',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': False},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("### 📦 Pedidos por País")
    
    country_orders = df['Country'].value_counts()
    
    fig = px.pie(
        values=country_orders.values,
        names=country_orders.index,
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Purples_r
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Pedidos: %{value:,}<br>Percentual: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# State Analysis (for countries with state data)
st.markdown("### 📍 Análise por Estado/Região")

state_revenue = df.groupby(['Country', 'State']).agg({
    'TotalAmount': 'sum',
    'OrderID': 'count'
}).reset_index()

state_revenue.columns = ['País', 'Estado', 'Receita', 'Pedidos']
state_revenue = state_revenue.sort_values('Receita', ascending=False)

# Show top 20 states
st.dataframe(
    state_revenue.head(20).style.background_gradient(cmap='Purples', subset=['Receita'])
                                .format({
                                    'Receita': '${:,.2f}',
                                    'Pedidos': '{:,.0f}'
                                }),
    width='stretch',
    height=400
)

st.markdown("---")

# City Analysis
st.markdown("### 🏙️ Top 15 Cidades")

city_data = df.groupby('City').agg({
    'TotalAmount': 'sum',
    'OrderID': 'count',
    'Country': 'first'
}).reset_index()

city_data.columns = ['Cidade', 'Receita', 'Pedidos', 'País']
city_data = city_data.sort_values('Receita', ascending=False).head(15)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=city_data['Cidade'],
    y=city_data['Receita'],
    marker=dict(
        color=city_data['Receita'],
        colorscale='Viridis',
        showscale=False
    ),
    text=[f'${v:,.0f}' for v in city_data['Receita']],
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Receita: $%{y:,.2f}<extra></extra>'
))

fig.update_layout(
    xaxis_title='',
    yaxis_title='Receita ($)',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font={'color': '#F1F5F9'},
    xaxis={'showgrid': False, 'tickangle': -45},
    yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
    height=450
)

st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Shipping Cost Analysis
st.markdown("### 🚚 Análise de Custos de Frete")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Custo Médio de Frete por País")
    
    fig = go.Figure(data=[
        go.Bar(
            y=geo_summary.index,
            x=geo_summary['Avg_Shipping_Cost'],
            orientation='h',
            marker=dict(
                color=geo_summary['Avg_Shipping_Cost'],
                colorscale='Reds',
                showscale=False
            ),
            text=[f'${v:.2f}' for v in geo_summary['Avg_Shipping_Cost']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        xaxis_title='Custo Médio ($)',
        yaxis_title='',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': False},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("#### Custo de Frete vs Valor do Pedido")
    
    # Sample for better visualization
    sample_df = df.sample(min(5000, len(df)))
    
    fig = px.scatter(
        sample_df,
        x='TotalAmount',
        y='ShippingCost',
        color='Country',
        opacity=0.6,
        trendline='ols'
    )
    
    fig.update_layout(
        xaxis_title='Valor do Pedido ($)',
        yaxis_title='Custo de Frete ($)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Regional Performance Metrics
st.markdown("### 📊 Métricas Regionais Detalhadas")

regional_metrics = df.groupby('Country').agg({
    'TotalAmount': ['sum', 'mean'],
    'OrderID': 'count',
    'Quantity': 'sum',
    'ShippingCost': 'mean',
    'Discount': 'mean',
    'CustomerID': 'nunique'
}).round(2)

regional_metrics.columns = ['Receita Total', 'Ticket Médio', 'Pedidos', 
                            'Itens Vendidos', 'Frete Médio', 'Desconto Médio', 'Clientes']

regional_metrics = regional_metrics.sort_values('Receita Total', ascending=False)

st.dataframe(
    regional_metrics.style.background_gradient(cmap='Purples', subset=['Receita Total', 'Pedidos'])
                          .format({
                              'Receita Total': '${:,.2f}',
                              'Ticket Médio': '${:,.2f}',
                              'Pedidos': '{:,.0f}',
                              'Itens Vendidos': '{:,.0f}',
                              'Frete Médio': '${:,.2f}',
                              'Desconto Médio': '{:.1%}',
                              'Clientes': '{:,.0f}'
                          }),
    width='stretch'
)

st.markdown("---")

# Insights
st.markdown("### 💡 Insights Geográficos")

col1, col2, col3 = st.columns(3)

with col1:
    us_revenue_pct = (geo_summary.loc['United States', 'Revenue'] / df['TotalAmount'].sum()) * 100
    
    display_insight_box(
        "Concentração nos EUA",
        f"Estados Unidos representa {us_revenue_pct:.1f}% de toda a receita.",
        "🇺🇸"
    )

with col2:
    highest_shipping = geo_summary['Avg_Shipping_Cost'].idxmax()
    highest_shipping_cost = geo_summary.loc[highest_shipping, 'Avg_Shipping_Cost']
    
    display_insight_box(
        "Frete Mais Caro",
        f"{highest_shipping} tem o custo médio de frete mais alto: ${highest_shipping_cost:.2f}.",
        "💸"
    )

with col3:
    top_city = city_data.iloc[0]
    
    display_insight_box(
        "Cidade Campeã",
        f"{top_city['Cidade']} ({top_city['País']}) lidera com ${top_city['Receita']:,.2f}.",
        "🏆"
    )
