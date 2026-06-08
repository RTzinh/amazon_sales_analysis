import streamlit as st
import plotly.graph_objects as go
from data_processor import load_data, preprocess_data, get_summary_metrics
from utils import apply_custom_css, display_insight_box
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
apply_custom_css()

# Load data
with st.spinner("Loading data..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Error loading data.")
        st.stop()
    df = preprocess_data(df_raw)
    metrics = get_summary_metrics(df)

# Header with logo and title
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <h1 style="font-size: 3rem; font-weight: 700; 
                background: linear-gradient(135deg, #8B5CF6, #3B82F6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;">
        📊 Executive Dashboard
    </h1>
    <p style="font-size: 1.2rem; color: #94A3B8; margin-top: 0.5rem;">
        Strategic View of Commercial Performance
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Calculate key metrics
total_revenue = df['TotalAmount'].sum()
delivered_revenue = df[df['OrderStatus'] == 'Delivered']['TotalAmount'].sum()
lost_revenue = df[df['OrderStatus'].isin(['Cancelled', 'Returned'])]['TotalAmount'].sum()
conversion_rate = metrics['conversion_rate']
cancellation_rate = metrics['cancellation_rate']
avg_ticket = metrics['avg_order_value']

# Opportunities
opportunity_conversion = (delivered_revenue / conversion_rate) * (80 - conversion_rate)
opportunity_margin = delivered_revenue * 0.05
opportunity_retention = lost_revenue * 0.3
total_opportunity = opportunity_conversion + opportunity_margin + opportunity_retention

# === 6 KEY KPIs ===
st.markdown("### 💎 Key KPIs")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.15));
                border-left: 5px solid #10B981;
                border-radius: 15px;
                padding: 1.5rem;
                text-align: center;">
        <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">💰 ACTUAL REVENUE</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #10B981; margin: 0.5rem 0;">
            R$ {delivered_revenue:,.0f}
        </div>
        <div style="font-size: 0.85rem; color: #10B981;">
            ✓ {conversion_rate:.1f}% conversion
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(124, 58, 237, 0.15));
                border-left: 5px solid #8B5CF6;
                border-radius: 15px;
                padding: 1.5rem;
                text-align: center;">
        <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">🎯 AVERAGE ORDER VALUE</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #8B5CF6; margin: 0.5rem 0;">
            R$ {avg_ticket:,.2f}
        </div>
        <div style="font-size: 0.85rem; color: #8B5CF6;">
            {metrics['total_orders']:,} orders
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    margin_pct = (df['Net_Revenue'].sum() / total_revenue) * 100
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.15));
                border-left: 5px solid #3B82F6;
                border-radius: 15px;
                padding: 1.5rem;
                text-align: center;">
        <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">📈 NET MARGIN</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #3B82F6; margin: 0.5rem 0;">
            {margin_pct:.1f}%
        </div>
        <div style="font-size: 0.85rem; color: #3B82F6;">
            R$ {df['Net_Revenue'].sum():,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.15));
                border-left: 5px solid #EF4444;
                border-radius: 15px;
                padding: 1.5rem;
                text-align: center;">
        <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">⚠️ COMMERCIAL LOSSES</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #EF4444; margin: 0.5rem 0;">
            R$ {lost_revenue:,.0f}
        </div>
        <div style="font-size: 0.85rem; color: #EF4444;">
            {cancellation_rate:.1f}% cancellation
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.15));
                border-left: 5px solid #F59E0B;
                border-radius: 15px;
                padding: 1.5rem;
                text-align: center;">
        <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">💡 TOTAL OPPORTUNITY</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #F59E0B; margin: 0.5rem 0;">
            R$ {total_opportunity:,.0f}
        </div>
        <div style="font-size: 0.85rem; color: #F59E0B;">
            +{(total_opportunity/delivered_revenue)*100:.1f}% potential
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    roi_projected = ((total_opportunity * 0.7) / 33000) * 100
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.15));
                border-left: 5px solid #10B981;
                border-radius: 15px;
                padding: 1.5rem;
                text-align: center;">
        <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">🚀 PROJECTED ROI</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: #10B981; margin: 0.5rem 0;">
            {roi_projected:,.0f}%
        </div>
        <div style="font-size: 0.85rem; color: #10B981;">
            in 90 days
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === TREND CHART ===
st.markdown("### 📈 Revenue Trend")

# Monthly revenue
monthly_revenue = df[df['OrderStatus'] == 'Delivered'].groupby(
    df['OrderDate'].dt.to_period('M')
)['TotalAmount'].sum().reset_index()
monthly_revenue['OrderDate'] = monthly_revenue['OrderDate'].astype(str)

fig = go.Figure()

# Area chart
fig.add_trace(go.Scatter(
    x=monthly_revenue['OrderDate'],
    y=monthly_revenue['TotalAmount'],
    fill='tozeroy',
    fillcolor='rgba(139, 92, 246, 0.2)',
    line=dict(color='#8B5CF6', width=4),
    mode='lines+markers',
    marker=dict(size=10, color='#8B5CF6', symbol='circle'),
    hovertemplate='<b>%{x}</b><br>Revenue: R$ %{y:,.2f}<extra></extra>'
))

# Add trend line
from sklearn.linear_model import LinearRegression
import numpy as np

X = np.arange(len(monthly_revenue)).reshape(-1, 1)
y = monthly_revenue['TotalAmount'].values
model = LinearRegression().fit(X, y)
trend = model.predict(X)

fig.add_trace(go.Scatter(
    x=monthly_revenue['OrderDate'],
    y=trend,
    mode='lines',
    line=dict(color='#3B82F6', width=3, dash='dash'),
    name='Trend',
    hovertemplate='Trend: R$ %{y:,.2f}<extra></extra>'
))

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font={'color': '#F1F5F9', 'size': 13},
    xaxis={
        'showgrid': False,
        'title': '',
        'tickfont': {'size': 12}
    },
    yaxis={
        'showgrid': True,
        'gridcolor': 'rgba(148, 163, 184, 0.1)',
        'title': '',
        'tickformat': 'R$ ,.0f',
        'tickfont': {'size': 12}
    },
    height=400,
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, width='stretch')

st.markdown("---")

# === 3 QUICK WINS ===
st.markdown("### 🎯 Quick Wins - Priority Actions")

col1, col2, col3 = st.columns(3)

with col1:
    gain1 = opportunity_conversion * 0.3
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.1));
                border: 2px solid #8B5CF6;
                border-radius: 15px;
                padding: 1.5rem;">
        <div style="text-align: center; font-size: 3rem; margin-bottom: 0.5rem;">🎯</div>
        <h3 style="color: #8B5CF6; margin: 0.5rem 0; text-align: center;">Quick Win #1</h3>
        <h4 style="color: #F1F5F9; text-align: center; margin: 0.5rem 0;">Increase Conversion</h4>
        <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.6;">
            • Implement 24h follow-up<br>
            • Confirm pending orders<br>
            • Raise from {conversion_rate:.1f}% → 77%
        </p>
        <div style="background: rgba(139, 92, 246, 0.2); 
                    border-radius: 10px; 
                    padding: 1rem; 
                    text-align: center;
                    margin-top: 1rem;">
            <div style="font-size: 0.85rem; color: #94A3B8;">Estimated Gain</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #8B5CF6;">
                R$ {gain1:,.0f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    gain2 = opportunity_margin * 0.4
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
                border: 2px solid #3B82F6;
                border-radius: 15px;
                padding: 1.5rem;">
        <div style="text-align: center; font-size: 3rem; margin-bottom: 0.5rem;">💰</div>
        <h3 style="color: #3B82F6; margin: 0.5rem 0; text-align: center;">Quick Win #2</h3>
        <h4 style="color: #F1F5F9; text-align: center; margin: 0.5rem 0;">Optimize Margin</h4>
        <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.6;">
            • Review discount policy<br>
            • Train the team on value selling<br>
            • Increase margin by +2%
        </p>
        <div style="background: rgba(59, 130, 246, 0.2); 
                    border-radius: 10px; 
                    padding: 1rem; 
                    text-align: center;
                    margin-top: 1rem;">
            <div style="font-size: 0.85rem; color: #94A3B8;">Estimated Gain</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #3B82F6;">
                R$ {gain2:,.0f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    gain3 = opportunity_retention * 0.5
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
                border: 2px solid #10B981;
                border-radius: 15px;
                padding: 1.5rem;">
        <div style="text-align: center; font-size: 3rem; margin-bottom: 0.5rem;">⚡</div>
        <h3 style="color: #10B981; margin: 0.5rem 0; text-align: center;">Quick Win #3</h3>
        <h4 style="color: #F1F5F9; text-align: center; margin: 0.5rem 0;">Reduce Losses</h4>
        <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.6;">
            • Investigate cancellations<br>
            • Improve the post-sale process<br>
            • Reduce losses by -20%
        </p>
        <div style="background: rgba(16, 185, 129, 0.2); 
                    border-radius: 10px; 
                    padding: 1rem; 
                    text-align: center;
                    margin-top: 1rem;">
            <div style="font-size: 0.85rem; color: #94A3B8;">Estimated Gain</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #10B981;">
                R$ {gain3:,.0f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === VIEW FULL PLAN BUTTON ===
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <p style="font-size: 1.1rem; color: #94A3B8; margin-bottom: 1.5rem;">
        See the full action plan with detailed ROI and a 90-day timeline
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎯 VIEW FULL ACTION PLAN", width='stretch', type="primary"):
        st.switch_page("pages/9_🎯_Action_Plan.py")

st.markdown("<br>", unsafe_allow_html=True)

# === FOOTER ===
st.markdown("""
<div style="text-align: center; 
            padding: 2rem 1rem 1rem 1rem; 
            border-top: 1px solid rgba(148, 163, 184, 0.2);
            margin-top: 2rem;">
    <p style="color: #64748B; font-size: 0.9rem;">
        📊 Executive Dashboard | Commercial Performance Analysis<br>
        <span style="font-size: 0.85rem;">Built with a professional consulting methodology</span>
    </p>
</div>
""", unsafe_allow_html=True)
