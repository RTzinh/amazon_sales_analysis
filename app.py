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
    <h2 style="color: #8B5CF6; margin-top: 0;">Welcome to the Sales Analytics Platform 🚀</h2>
    <p style="font-size: 1.1rem; line-height: 1.8; color: #E2E8F0;">
        This application delivers advanced analytics on Amazon sales data with <strong>100,000 transactions</strong>,
        leveraging <strong>artificial intelligence</strong> and <strong>machine learning</strong> to generate actionable insights.
    </p>
</div>
""", unsafe_allow_html=True)

# Features grid
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Core Features

    - **Interactive Dashboard**: Dynamic visualizations and real-time filters
    - **Sales Analysis**: Time trends, seasonality and forecasting
    - **Product Performance**: Top products, categories and margin analysis
    - **Customer Insights**: RFM segmentation and behavioral clustering
    """)

with col2:
    st.markdown("""
    ### 🤖 AI Features

    - **Google Gemini AI**: Automatic generation of business insights
    - **LangChain Agents**: Natural-language queries over your data
    - **ML Clustering**: Smart customer segmentation
    - **Anomaly Detection**: Identification of unusual patterns
    """)

st.markdown("---")

# Navigation guide
st.markdown("""
### 🧭 Navigation

Use the sidebar menu to access:

1. **📊 Overview** - High-level view of KPIs and key metrics
2. **📈 Sales Analytics** - Time-based sales analysis and trends
3. **🛍️ Product Performance** - Product and category performance
4. **👥 Customer Insights** - Customer segmentation and analysis
5. **🗺️ Geographic Analysis** - Geographic sales distribution
6. **🤖 AI Insights** - Artificial-intelligence-powered analysis

""")

# Setup instructions
with st.expander("⚙️ Google Gemini API Setup"):
    st.markdown("""
    To use the AI features, you need to configure your Google Gemini API key:

    1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Create a new API Key
    3. Paste the key on the **🤖 AI Insights** page

    **Note**: The key is stored only in your local session and is never saved.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; padding: 2rem;">
    <p>Built with ❤️ using Streamlit, Plotly, Google Gemini AI and LangChain</p>
    <p style="font-size: 0.9rem;">© 2025 Amazon Sales Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)
