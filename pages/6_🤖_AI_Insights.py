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

def _load_gemini_key_from_secrets():
    """Return GEMINI_API_KEY from .streamlit/secrets.toml if available."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None
    return None

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")
apply_custom_css()

st.title("🤖 AI-Powered Insights")
st.markdown("Advanced analytics with Google Gemini AI and LangChain")

# API Key configuration
st.sidebar.header("⚙️ Settings")

secret_api_key = _load_gemini_key_from_secrets()

api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    value=secret_api_key or "",
    type="password",
    help="Get your key at https://makersuite.google.com/app/apikey"
)

if secret_api_key:
    st.sidebar.info("Key loaded from .streamlit/secrets.toml or Streamlit Cloud Secrets.")

if not api_key:
    st.warning("⚠️ Please enter your Google Gemini API key in the sidebar to use the AI features.")

    st.markdown("""
    ### How to get your API Key:

    1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Sign in with your Google account
    3. Click "Create API Key"
    4. Copy the key and paste it in the field on the left

    **Note**: The key is stored only in your session and is never saved permanently.
    """)

    st.info("💡 **Available AI Features:**\n\n"
            "- 🧠 Automatic business insights\n"
            "- 💬 Chat with your data using natural language\n"
            "- 📈 AI-powered trend analysis\n"
            "- 🎯 Category performance analysis\n"
            "- 🚨 Anomaly detection")

    st.stop()

# Configure Gemini
try:
    configure_gemini(api_key)
    st.sidebar.success("✅ API configured successfully!")
except Exception as e:
    st.sidebar.error(f"❌ Error configuring API: {str(e)}")
    st.stop()

# Load data
with st.spinner("Loading data..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Error loading data.")
        st.stop()
    df = preprocess_data(df_raw)
    metrics = get_summary_metrics(df)

st.markdown("---")

# Tab navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧠 Automated Insights",
    "💬 Chat with Data",
    "📈 Trend Analysis",
    "🎯 Category Performance",
    "🚨 Anomaly Detection"
])

# Tab 1: Automated Business Insights
with tab1:
    st.markdown("### 🧠 AI-Generated Business Insights")
    st.markdown("The AI analyzes your data and generates actionable recommendations automatically.")

    if st.button("🔄 Generate Insights", type="primary", width='stretch'):
        with st.spinner("🤖 Gemini is analyzing your data..."):
            try:
                insights = generate_business_insights(df, metrics, api_key)

                st.markdown("---")
                st.markdown("### 📊 Full Analysis")

                st.markdown(insights)

                st.success("✅ Analysis complete!")

            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")

    # Quick stats for context
    st.markdown("---")
    st.markdown("#### 📈 Data Context")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Total Revenue", f"${metrics['total_revenue']:,.2f}")

    with col2:
        st.metric("📦 Total Orders", f"{metrics['total_orders']:,}")

    with col3:
        st.metric("👥 Customers", f"{metrics['total_customers']:,}")

    with col4:
        st.metric("✅ Conversion Rate", f"{metrics['conversion_rate']:.1f}%")

# Tab 2: Interactive Chat
with tab2:
    st.markdown("### 💬 Ask Questions About Your Data")
    st.markdown("Use natural language to query your data. The LangChain agent will analyze and answer.")

    # Example questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What is the best-selling product?
        - How much revenue did we make in Electronics?
        - Which country has the highest average order value?
        - How many customers placed more than 3 orders?
        - Which category has the lowest profit margin?
        - What are the 5 products with the highest discount?
        - Which day of the week has the most sales?
        - What is the average shipping cost by country?
        """)

    # Chat interface
    question = st.text_area(
        "Your question:",
        placeholder="e.g. What are the 10 best-selling products by value?",
        height=100
    )

    if st.button("🤖 Ask the Agent", type="primary", width='stretch'):
        if question:
            with st.spinner("🤖 The LangChain agent is processing your question..."):
                try:
                    answer = ask_data_question(df, question, api_key)

                    st.markdown("---")
                    st.markdown("### 🎯 Answer")
                    st.markdown(answer)

                except Exception as e:
                    st.error(f"Error processing question: {str(e)}\n\nTry rephrasing your question more specifically.")
        else:
            st.warning("Please type a question.")
    
    # Conversation history (simulated)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

# Tab 3: Sales Trends Analysis
with tab3:
    st.markdown("### 📈 AI-Powered Trend Analysis")
    st.markdown("Gemini analyzes time patterns and provides qualitative forecasts.")

    if st.button("📊 Analyze Trends", type="primary", width='stretch'):
        with st.spinner("🤖 Analyzing sales trends..."):
            try:
                trend_analysis = analyze_sales_trends(df, api_key)

                st.markdown("---")
                st.markdown(trend_analysis)

                # Show trend chart
                st.markdown("### 📈 Trend Chart")
                
                monthly_sales = df.groupby(df['OrderDate'].dt.to_period('M')).agg({
                    'TotalAmount': 'sum'
                }).reset_index()
                
                monthly_sales['OrderDate'] = monthly_sales['OrderDate'].astype(str)
                
                fig = px.line(
                    monthly_sales,
                    x='OrderDate',
                    y='TotalAmount',
                    title='Monthly Sales Evolution',
                    markers=True
                )

                fig.update_traces(line_color='#8B5CF6', line_width=3)

                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Revenue ($)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F1F5F9'},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    height=400
                )
                
                st.plotly_chart(fig, width='stretch')

            except Exception as e:
                st.error(f"Analysis error: {str(e)}")

# Tab 4: Category Performance
with tab4:
    st.markdown("### 🎯 AI-Powered Category Performance Analysis")
    st.markdown("Deep insights into the performance of each product category.")

    if st.button("🔍 Analyze Categories", type="primary", width='stretch'):
        with st.spinner("🤖 Analyzing category performance..."):
            try:
                category_analysis = analyze_category_performance(df, api_key)

                st.markdown("---")
                st.markdown(category_analysis)

                # Category comparison chart
                st.markdown("### 📊 Visual Comparison")
                
                category_perf = df.groupby('Category').agg({
                    'TotalAmount': 'sum',
                    'OrderID': 'count',
                    'Discount': 'mean'
                }).round(2)
                
                category_perf.columns = ['Revenue', 'Orders', 'Average Discount']
                category_perf = category_perf.sort_values('Revenue', ascending=True)

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    y=category_perf.index,
                    x=category_perf['Revenue'],
                    name='Revenue',
                    orientation='h',
                    marker=dict(color='#8B5CF6')
                ))

                fig.update_layout(
                    title='Revenue by Category',
                    xaxis_title='Revenue ($)',
                    yaxis_title='',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F1F5F9'},
                    height=400
                )
                
                st.plotly_chart(fig, width='stretch')

            except Exception as e:
                st.error(f"Analysis error: {str(e)}")

# Tab 5: Anomaly Detection
with tab5:
    st.markdown("### 🚨 Anomaly Detection")
    st.markdown("Identifies unusual transactions using Isolation Forest (Machine Learning)")

    contamination = st.slider(
        "Sensitivity (% of expected anomalies)",
        min_value=1,
        max_value=10,
        value=5,
        help="Percentage of data that will be considered anomalous"
    ) / 100

    if st.button("🔍 Detect Anomalies", type="primary", width='stretch'):
        with st.spinner("🤖 Running anomaly detection..."):
            try:
                anomalies = detect_anomalies(df, contamination)

                st.success(f"✅ Detected {len(anomalies):,} anomalous transactions!")

                col1, col2, col3 = st.columns(3)

                with col1:
                    anomaly_revenue = anomalies['TotalAmount'].sum()
                    st.metric("💰 Revenue in Anomalies", f"${anomaly_revenue:,.2f}")

                with col2:
                    avg_anomaly_value = anomalies['TotalAmount'].mean()
                    st.metric("📊 Average Value", f"${avg_anomaly_value:,.2f}")

                with col3:
                    anomaly_rate = (len(anomalies) / len(df)) * 100
                    st.metric("📈 Anomaly Rate", f"{anomaly_rate:.2f}%")

                st.markdown("---")

                # Anomaly scatter plot
                st.markdown("### 📊 Anomaly Visualization")

                plot_data = df.copy()
                plot_data['Type'] = 'Normal'
                plot_data.loc[anomalies.index, 'Type'] = 'Anomaly'
                
                # Sample for performance
                plot_sample = plot_data.sample(min(5000, len(plot_data)))
                
                fig = px.scatter(
                    plot_sample,
                    x='UnitPrice',
                    y='Quantity',
                    color='Type',
                    size='TotalAmount',
                    hover_data=['ProductName', 'TotalAmount', 'Category'],
                    color_discrete_map={'Normal': '#8B5CF6', 'Anomaly': '#EF4444'},
                    title='Anomalies: Price vs Quantity'
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#F1F5F9'},
                    xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
                    height=500
                )
                
                st.plotly_chart(fig, width='stretch')
                
                # Anomaly table
                st.markdown("### 📋 Top 20 Anomalies")
                
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
                    width='stretch',
                    height=400
                )
                
                # Insights about anomalies
                st.markdown("### 💡 Insights on Anomalies")

                col1, col2, col3 = st.columns(3)

                with col1:
                    anomaly_by_status = anomalies['OrderStatus'].value_counts()
                    most_common_status = anomaly_by_status.index[0]

                    display_insight_box(
                        "Predominant Status",
                        f"{most_common_status} is the most common status among anomalies ({anomaly_by_status.iloc[0]} cases).",
                        "📊"
                    )

                with col2:
                    anomaly_by_category = anomalies['Category'].value_counts()
                    most_anomalous_cat = anomaly_by_category.index[0]

                    display_insight_box(
                        "Category with Most Anomalies",
                        f"{most_anomalous_cat} has {anomaly_by_category.iloc[0]} anomalous transactions.",
                        "🎯"
                    )

                with col3:
                    high_value_anomalies = len(anomalies[anomalies['TotalAmount'] > df['TotalAmount'].quantile(0.95)])

                    display_insight_box(
                        "High-Value Anomalies",
                        f"{high_value_anomalies} anomalies are very high-value transactions.",
                        "💎"
                    )

            except Exception as e:
                st.error(f"Detection error: {str(e)}")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #94a3b8; padding: 1rem;">
    <p>Powered by Google Gemini AI 🤖 & LangChain 🦜</p>
</div>
""", unsafe_allow_html=True)
