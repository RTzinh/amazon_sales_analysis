import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_processor import load_data, preprocess_data, get_summary_metrics
from ai_models import (
    configure_gemini, 
    generate_business_insights,
    ask_data_question,
    analyze_sales_trends,
    analyze_category_performance,
    detect_anomalies
)
from utils import apply_custom_css, display_insight_box
import pandas as pd

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")
apply_custom_css()

st.title("🤖 AI-Powered Insights")
st.markdown("Análises avançadas com Google Gemini AI e LangChain")

# API Key configuration
st.sidebar.header("⚙️ Configuração")

api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    type="password",
    help="Obtenha sua chave em https://makersuite.google.com/app/apikey"
)

if not api_key:
    st.warning("⚠️ Por favor, insira sua chave da API do Google Gemini na barra lateral para usar os recursos de IA.")
    
    st.markdown("""
    ### Como obter sua API Key:
    
    1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Faça login com sua conta Google
    3. Clique em "Create API Key"
    4. Copie a chave e cole no campo à esquerda
    
    **Nota**: A chave é armazenada apenas na sua sessão e não é salva permanentemente.
    """)
    
    st.info("💡 **Funcionalidades de IA Disponíveis:**\n\n"
            "- 🧠 Insights automáticos de negócio\n"
            "- 💬 Chat com seus dados usando linguagem natural\n"
            "- 📈 Análise de tendências com IA\n"
            "- 🎯 Análise de performance de categorias\n"
            "- 🚨 Detecção de anomalias")
    
    st.stop()

# Configure Gemini
try:
    configure_gemini(api_key)
    st.sidebar.success("✅ API configurada com sucesso!")
except Exception as e:
    st.sidebar.error(f"❌ Erro ao configurar API: {str(e)}")
    st.stop()

# Load data
with st.spinner("Carregando dados..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Erro ao carregar dados.")
        st.stop()
    df = preprocess_data(df_raw)
    metrics = get_summary_metrics(df)

st.markdown("---")

# Tab navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧠 Insights Automáticos",
    "💬 Chat com Dados",
    "📈 Análise de Tendências",
    "🎯 Performance de Categorias",
    "🚨 Detecção de Anomalias"
])

# Tab 1: Automated Business Insights
with tab1:
    st.markdown("### 🧠 Insights de Negócio Gerados por IA")
    st.markdown("A IA analisa seus dados e gera recomendações acionáveis automaticamente.")
    
    if st.button("🔄 Gerar Insights", type="primary", use_container_width=True):
        with st.spinner("🤖 Gemini está analisando seus dados..."):
            try:
                insights = generate_business_insights(df, metrics, api_key)
                
                st.markdown("---")
                st.markdown("### 📊 Análise Completa")
                
                st.markdown(insights)
                
                st.success("✅ Análise concluída!")
                
            except Exception as e:
                st.error(f"Erro ao gerar insights: {str(e)}")
    
    # Quick stats for context
    st.markdown("---")
    st.markdown("#### 📈 Contexto dos Dados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Receita Total", f"${metrics['total_revenue']:,.2f}")
    
    with col2:
        st.metric("📦 Total de Pedidos", f"{metrics['total_orders']:,}")
    
    with col3:
        st.metric("👥 Clientes", f"{metrics['total_customers']:,}")
    
    with col4:
        st.metric("✅ Taxa de Conversão", f"{metrics['conversion_rate']:.1f}%")

# Tab 2: Interactive Chat
with tab2:
    st.markdown("### 💬 Faça Perguntas aos Seus Dados")
    st.markdown("Use linguagem natural para consultar seus dados. O agente LangChain irá analisar e responder.")
    
    # Example questions
    with st.expander("💡 Exemplos de Perguntas"):
        st.markdown("""
        - Qual é o produto mais vendido?
        - Quanto faturamos em Electronics?
        - Qual país tem o maior ticket médio?
        - Quantos clientes fizeram mais de 3 pedidos?
        - Qual categoria tem a menor margem de lucro?
        - Quais são os 5 produtos com maior desconto?
        - Qual dia da semana tem mais vendas?
        - Qual é o valor médio de frete por país?
        """)
    
    # Chat interface
    question = st.text_area(
        "Sua pergunta:",
        placeholder="Ex: Quais são os 10 produtos mais vendidos em valor?",
        height=100
    )
    
    if st.button("🤖 Perguntar ao Agente", type="primary", use_container_width=True):
        if question:
            with st.spinner("🤖 Agente LangChain está processando sua pergunta..."):
                try:
                    answer = ask_data_question(df, question, api_key)
                    
                    st.markdown("---")
                    st.markdown("### 🎯 Resposta")
                    st.markdown(answer)
                    
                except Exception as e:
                    st.error(f"Erro ao processar pergunta: {str(e)}\n\nTente reformular sua pergunta de forma mais específica.")
        else:
            st.warning("Por favor, digite uma pergunta.")
    
    # Conversation history (simulated)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

# Tab 3: Sales Trends Analysis
with tab3:
    st.markdown("### 📈 Análise de Tendências com IA")
    st.markdown("O Gemini analisa padrões temporais e fornece previsões qualitativas.")
    
    if st.button("📊 Analisar Tendências", type="primary", use_container_width=True):
        with st.spinner("🤖 Analisando tendências de vendas..."):
            try:
                trend_analysis = analyze_sales_trends(df, api_key)
                
                st.markdown("---")
                st.markdown(trend_analysis)
                
                # Show trend chart
                st.markdown("### 📈 Gráfico de Tendência")
                
                monthly_sales = df.groupby(df['OrderDate'].dt.to_period('M')).agg({
                    'TotalAmount': 'sum'
                }).reset_index()
                
                monthly_sales['OrderDate'] = monthly_sales['OrderDate'].astype(str)
                
                fig = px.line(
                    monthly_sales,
                    x='OrderDate',
                    y='TotalAmount',
                    title='Evolução Mensal de Vendas',
                    markers=True
                )
                
                fig.update_traces(line_color='#8B5CF6', line_width=3)
                
                fig.update_layout(
                    xaxis_title='Mês',
                    yaxis_title='Receita ($)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F1F5F9'},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro na análise: {str(e)}")

# Tab 4: Category Performance
with tab4:
    st.markdown("### 🎯 Análise de Performance de Categorias com IA")
    st.markdown("Insights profundos sobre o desempenho de cada categoria de produto.")
    
    if st.button("🔍 Analisar Categorias", type="primary", use_container_width=True):
        with st.spinner("🤖 Analisando performance das categorias..."):
            try:
                category_analysis = analyze_category_performance(df, api_key)
                
                st.markdown("---")
                st.markdown(category_analysis)
                
                # Category comparison chart
                st.markdown("### 📊 Comparação Visual")
                
                category_perf = df.groupby('Category').agg({
                    'TotalAmount': 'sum',
                    'OrderID': 'count',
                    'Discount': 'mean'
                }).round(2)
                
                category_perf.columns = ['Receita', 'Pedidos', 'Desconto Médio']
                category_perf = category_perf.sort_values('Receita', ascending=True)
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    y=category_perf.index,
                    x=category_perf['Receita'],
                    name='Receita',
                    orientation='h',
                    marker=dict(color='#8B5CF6')
                ))
                
                fig.update_layout(
                    title='Receita por Categoria',
                    xaxis_title='Receita ($)',
                    yaxis_title='',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F1F5F9'},
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro na análise: {str(e)}")

# Tab 5: Anomaly Detection
with tab5:
    st.markdown("### 🚨 Detecção de Anomalias")
    st.markdown("Identifica transações incomuns usando Isolation Forest (Machine Learning)")
    
    contamination = st.slider(
        "Sensibilidade (% de anomalias esperadas)",
        min_value=1,
        max_value=10,
        value=5,
        help="Porcentagem de dados que serão considerados anômalos"
    ) / 100
    
    if st.button("🔍 Detectar Anomalias", type="primary", use_container_width=True):
        with st.spinner("🤖 Executando detecção de anomalias..."):
            try:
                anomalies = detect_anomalies(df, contamination)
                
                st.success(f"✅ Detectadas {len(anomalies):,} transações anômalas!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    anomaly_revenue = anomalies['TotalAmount'].sum()
                    st.metric("💰 Receita em Anomalias", f"${anomaly_revenue:,.2f}")
                
                with col2:
                    avg_anomaly_value = anomalies['TotalAmount'].mean()
                    st.metric("📊 Valor Médio", f"${avg_anomaly_value:,.2f}")
                
                with col3:
                    anomaly_rate = (len(anomalies) / len(df)) * 100
                    st.metric("📈 Taxa de Anomalia", f"{anomaly_rate:.2f}%")
                
                st.markdown("---")
                
                # Anomaly scatter plot
                st.markdown("### 📊 Visualização de Anomalias")
                
                plot_data = df.copy()
                plot_data['Tipo'] = 'Normal'
                plot_data.loc[anomalies.index, 'Tipo'] = 'Anomalia'
                
                # Sample for performance
                plot_sample = plot_data.sample(min(5000, len(plot_data)))
                
                fig = px.scatter(
                    plot_sample,
                    x='UnitPrice',
                    y='Quantity',
                    color='Tipo',
                    size='TotalAmount',
                    hover_data=['ProductName', 'TotalAmount', 'Category'],
                    color_discrete_map={'Normal': '#8B5CF6', 'Anomalia': '#EF4444'},
                    title='Anomalias: Preço vs Quantidade'
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F1F5F9'},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Anomaly table
                st.markdown("### 📋 Top 20 Anomalias")
                
                anomaly_display = anomalies[[
                    'OrderID', 'ProductName', 'Category', 'TotalAmount', 
                    'Quantity', 'UnitPrice', 'Discount', 'OrderStatus'
                ]].sort_values('TotalAmount', ascending=False).head(20)
                
                st.dataframe(
                    anomaly_display.style.format({
                        'TotalAmount': '${:,.2f}',
                        'UnitPrice': '${:,.2f}',
                        'Discount': '{:.1%}'
                    }),
                    use_container_width=True,
                    height=400
                )
                
                # Insights about anomalies
                st.markdown("### 💡 Insights sobre Anomalias")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    anomaly_by_status = anomalies['OrderStatus'].value_counts()
                    most_common_status = anomaly_by_status.index[0]
                    
                    display_insight_box(
                        "Status Predominante",
                        f"{most_common_status} é o status mais comum em anomalias ({anomaly_by_status.iloc[0]} casos).",
                        "📊"
                    )
                
                with col2:
                    anomaly_by_category = anomalies['Category'].value_counts()
                    most_anomalous_cat = anomaly_by_category.index[0]
                    
                    display_insight_box(
                        "Categoria com Mais Anomalias",
                        f"{most_anomalous_cat} tem {anomaly_by_category.iloc[0]} transações anômalas.",
                        "🎯"
                    )
                
                with col3:
                    high_value_anomalies = len(anomalies[anomalies['TotalAmount'] > df['TotalAmount'].quantile(0.95)])
                    
                    display_insight_box(
                        "Anomalias de Alto Valor",
                        f"{high_value_anomalies} anomalias são transações de valor muito alto.",
                        "💎"
                    )
                
            except Exception as e:
                st.error(f"Erro na detecção: {str(e)}")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #94a3b8; padding: 1rem;">
    <p>Powered by Google Gemini AI 🤖 & LangChain 🦜</p>
</div>
""", unsafe_allow_html=True)
