import streamlit as st
from utils import apply_custom_css

# Page configuration
st.set_page_config(
    page_title="Amazon Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Main page content
st.title("🛍️ Amazon Sales Analytics Dashboard")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
            border-radius: 15px; padding: 2rem; margin: 2rem 0;">
    <h2 style="color: #8B5CF6; margin-top: 0;">Bem-vindo à Plataforma de Análise de Vendas 🚀</h2>
    <p style="font-size: 1.1rem; line-height: 1.8; color: #E2E8F0;">
        Esta aplicação oferece análises avançadas de vendas da Amazon com <strong>100.000 transações</strong>,
        utilizando <strong>inteligência artificial</strong> e <strong>machine learning</strong> para gerar insights acionáveis.
    </p>
</div>
""", unsafe_allow_html=True)

# Features grid
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Recursos Principais
    
    - **Dashboard Interativo**: Visualizações dinâmicas e filtros em tempo real
    - **Análise de Vendas**: Tendências temporais, sazonalidade e forecasting
    - **Performance de Produtos**: Top produtos, categorias e análise de margem
    - **Insights de Clientes**: Segmentação RFM e clustering comportamental
    """)
    
with col2:
    st.markdown("""
    ### 🤖 Recursos de IA
    
    - **Google Gemini AI**: Geração automática de insights de negócio
    - **LangChain Agents**: Consultas em linguagem natural aos dados
    - **Clustering ML**: Segmentação inteligente de clientes
    - **Detecção de Anomalias**: Identificação de padrões incomuns
    """)

st.markdown("---")

# Navigation guide
st.markdown("""
### 🧭 Navegação

Use o menu lateral para acessar:

1. **📊 Overview** - Visão geral dos KPIs e métricas principais
2. **📈 Sales Analytics** - Análise temporal de vendas e tendências
3. **🛍️ Product Performance** - Desempenho de produtos e categorias
4. **👥 Customer Insights** - Segmentação e análise de clientes
5. **🗺️ Geographic Analysis** - Distribuição geográfica de vendas
6. **🤖 AI Insights** - Análises com inteligência artificial

""")

# Setup instructions
with st.expander("⚙️ Configuração da API do Google Gemini"):
    st.markdown("""
    Para utilizar os recursos de IA, você precisa configurar sua chave da API do Google Gemini:
    
    1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Crie uma nova API Key
    3. Cole a chave na página **🤖 AI Insights**
    
    **Nota**: A chave será armazenada apenas na sua sessão local e não será salva.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; padding: 2rem;">
    <p>Desenvolvido com ❤️ usando Streamlit, Plotly, Google Gemini AI e LangChain</p>
    <p style="font-size: 0.9rem;">© 2025 Amazon Sales Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)
