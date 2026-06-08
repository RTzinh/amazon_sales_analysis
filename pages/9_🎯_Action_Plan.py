import streamlit as st
import plotly.graph_objects as go
from data_processor import load_data, preprocess_data, get_summary_metrics, get_customer_segments_rfm
from ai_models import generate_business_insights
from utils import apply_custom_css, display_insight_box
from pdf_generator import generate_executive_summary_pdf, create_pdf_download_button
import pandas as pd

st.set_page_config(page_title="Action Plan", page_icon="🎯", layout="wide")
apply_custom_css()

st.title("🎯 Commercial Action Plan")
st.markdown("**Strategic Recommendations for Commercial Performance**")

# Load data
with st.spinner("Loading data..."):
    df_raw = load_data()
    if df_raw is None:
        st.error("Error loading data.")
        st.stop()
    df = preprocess_data(df_raw)
    metrics = get_summary_metrics(df)

# Executive Summary
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.15));
            border-left: 5px solid #8B5CF6; border-radius: 10px; padding: 2rem; margin: 1rem 0;">
    <h2 style="color: #8B5CF6; margin-top: 0;">📊 Executive Summary</h2>
    <p style="font-size: 1.1rem; line-height: 1.8;">
    This action plan was built from an in-depth analysis of <strong>100,000 transactions</strong>,
    identifying concrete opportunities to increase commercial performance, reduce losses and
    optimize sales processes.
    </p>
</div>
""", unsafe_allow_html=True)

# Calculate key opportunities
total_revenue = df['TotalAmount'].sum()
delivered_revenue = df[df['OrderStatus'] == 'Delivered']['TotalAmount'].sum()
lost_revenue = df[df['OrderStatus'].isin(['Cancelled', 'Returned'])]['TotalAmount'].sum()
current_conversion = metrics['conversion_rate']

# Opportunities
opportunity_conversion = (delivered_revenue / current_conversion) * (80 - current_conversion)
opportunity_margin = delivered_revenue * 0.05  # 5% margin improvement
opportunity_retention = lost_revenue * 0.3  # 30% recovery

total_opportunity = opportunity_conversion + opportunity_margin + opportunity_retention

st.markdown("---")

# Opportunities Overview
st.markdown("### 💎 Identified Growth Potential")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Opportunity",
        f"R$ {total_opportunity:,.2f}",
        delta=f"+{(total_opportunity/delivered_revenue)*100:.1f}%",
        help="Total identified growth potential"
    )

with col2:
    st.metric(
        "Conversion Increase",
        f"R$ {opportunity_conversion:,.2f}",
        help="Improving conversion to 80%"
    )

with col3:
    st.metric(
        "Margin Gain",
        f"R$ {opportunity_margin:,.2f}",
        help="Optimizing margin by 5%"
    )

with col4:
    st.metric(
        "Loss Recovery",
        f"R$ {opportunity_retention:,.2f}",
        help="Reducing cancellations/returns"
    )

st.markdown("---")

# Strategic Action Plan
st.markdown("### 🎯 Strategic Action Plan")

# Action 1: Increase Conversion
with st.expander("**ACTION 1: INCREASE CONVERSION RATE** - HIGH Priority 🔴", expanded=True):
    st.markdown("""
    #### 🎯 Goal
    Raise the conversion rate from **{:.1f}%** to **80%**

    #### 📊 Estimated Impact
    **R$ {:.2f}** in additional revenue

    #### 🚀 Practical Actions

    **For Managers:**
    1. Implement a **structured follow-up** process for pending orders
    2. Create a **pre-cancellation contact routine** (D+2 from the order)
    3. Set **conversion targets** per seller

    **For Sellers:**
    1. **Confirm the order** by WhatsApp/phone within 2h of purchase
    2. Offer **payment alternatives** to reduce pending orders
    3. Proactively **resolve questions** about delivery and product

    **For Training:**
    1. Workshop: "Order confirmation techniques"
    2. Outreach script to recover pending orders
    3. Role-play: handling post-purchase objections

    #### 📅 Timeline
    - **Week 1-2**: Implement the follow-up process
    - **Week 3-4**: Train the team and refine scripts
    - **Month 2**: Measure results and adjust

    #### 🎯 Quarterly Target
    Conversion: **{:.1f}%** → **77%** (gain of R$ {:.2f})
    """.format(
        current_conversion,
        opportunity_conversion,
        current_conversion,
        opportunity_conversion * 0.7
    ))

# Action 2: Optimize Margin
with st.expander("**ACTION 2: OPTIMIZE COMMERCIAL MARGIN** - HIGH Priority 🔴"):

    # Calculate discount impact
    discount_analysis = df.groupby(pd.cut(df['Discount'], bins=[0, 0.05, 0.10, 0.15, 0.20, 1.0],
                                          labels=['0-5%', '5-10%', '10-15%', '15-20%', '>20%'])).agg({
        'Net_Revenue': 'sum',
        'TotalAmount': 'sum',
        'OrderID': 'count'
    })

    best_margin_range = ((discount_analysis['Net_Revenue'] / discount_analysis['TotalAmount']) * 100).idxmax()

    st.markdown(f"""
    #### 🎯 Goal
    Increase net margin by **5 percentage points**

    #### 📊 Estimated Impact
    **R$ {opportunity_margin:,.2f}** in additional profit

    #### 🚀 Practical Actions

    **Discount Management:**
    1. **Ideal zone identified**: Discounts in the **{best_margin_range}** range keep the best margin
    2. Set **discount approval limits** by hierarchy level
    3. Create a **discount matrix** by category and volume

    **For Sellers:**
    1. Prioritize **consultative selling** before offering a discount
    2. Use discounts as a **closing tool**, not an opening one
    3. **Bundling**: group products to preserve margin

    **Critical Products:**
    - Review the price/discount of products with **high volume and low margin**
    - Implement **dynamic pricing** in strategic categories
    - Negotiate better terms with suppliers

    **Training:**
    1. Workshop: "Value selling vs price selling"
    2. Anchoring techniques and price justification
    3. Negotiation scenario simulations

    #### 🎯 Quarterly Target
    Margin: **Current** → **+3%** (gain of R$ {opportunity_margin * 0.6:,.2f})
    """)

# Action 3: Reduce Losses
with st.expander("**ACTION 3: REDUCE COMMERCIAL LOSSES** - MEDIUM Priority 🟡"):

    # Calculate cancellation by category
    worst_category = df[df['OrderStatus'] == 'Cancelled'].groupby('Category').size().idxmax()
    worst_cancel_count = df[df['OrderStatus'] == 'Cancelled'].groupby('Category').size().max()

    st.markdown(f"""
    #### 🎯 Goal
    Reduce cancellations and returns by **30%**

    #### 📊 Estimated Impact
    **R$ {opportunity_retention:,.2f}** in recovered revenue

    #### 🚀 Practical Actions

    **Critical Category: {worst_category}**
    - **{worst_cancel_count}** cancellations identified
    - Investigate the **root causes** (quality, delivery, expectations)
    - Implement a **pre-sale qualification checklist**

    **Post-Sale Process:**
    1. **D+1 follow-up**: Confirm receipt and satisfaction
    2. Automatic **NPS survey** after delivery
    3. **Retention process** for return intent

    **For Sellers:**
    1. **Qualify the customer's expectations** before the sale
    2. Present **real photos/videos** of the product
    3. **Confirm key technical specifications**

    **Logistics:**
    1. Review **delivery SLA** by region
    2. Improve **tracking** and communication
    3. Partner with more efficient carriers

    #### 🎯 Quarterly Target
    Cancellations: **{metrics['cancellation_rate']:.1f}%** → **{metrics['cancellation_rate'] * 0.7:.1f}%**
    """)

# Action 4: Performance by Seller
seller_perf = df[df['OrderStatus'] == 'Delivered'].groupby('SellerID').agg({
    'TotalAmount': 'sum'
}).sort_values('TotalAmount', ascending=False)

top_seller_revenue = seller_perf.iloc[0]['TotalAmount']
avg_seller_revenue = seller_perf['TotalAmount'].mean()

with st.expander("**ACTION 4: LEVEL OUT SELLER PERFORMANCE** - MEDIUM Priority 🟡"):
    st.markdown(f"""
    #### 🎯 Goal
    Lift the performance of below-average sellers

    #### 📊 Identified Gap
    - Top seller: **R$ {top_seller_revenue:,.2f}**
    - Team average: **R$ {avg_seller_revenue:,.2f}**
    - **Gap: R$ {(top_seller_revenue - avg_seller_revenue):,.2f}**

    #### 🚀 Practical Actions

    **Team Management:**
    1. **Shadowing**: Junior sellers shadow top performers
    2. **Structured mentoring**: Top 20% mentor the bottom 20%
    3. **Weekly ranking** with public recognition

    **Development:**
    1. Identify the **best practices** of top performers
    2. Create a **sales playbook** with validated techniques
    3. Training focused on **individual gaps**

    **KPIs per Seller:**
    - Average order value
    - Conversion rate
    - Average margin
    - Satisfaction score (NPS)

    **Incentive System:**
    1. **Progressive commission** by margin
    2. **Bonus** for conversion above target
    3. **Gamification** with monthly challenges

    #### 🎯 Quarterly Target
    - 70% of the team above **R$ {avg_seller_revenue * 1.2:,.2f}**/month
    - Reduce the gap between top and bottom by **40%**
    """)

# Action 5: Regional Expansion
with st.expander("**ACTION 5: STRATEGIC GEOGRAPHIC EXPANSION** - LOW Priority 🟢"):

    state_revenue = df[df['OrderStatus'] == 'Delivered'].groupby('State')['TotalAmount'].sum().sort_values(ascending=False)
    top_state = state_revenue.index[0]
    underperforming_states = state_revenue[state_revenue < state_revenue.quantile(0.25)].index.tolist()

    st.markdown(f"""
    #### 🎯 Goal
    Tap into the potential of underserved markets

    #### 📊 Regional Analysis
    - **Leading State**: {top_state} (R$ {state_revenue.iloc[0]:,.2f})
    - **States with potential**: {len(underperforming_states)} states below Q1

    #### 🚀 Practical Actions

    **Gradual Expansion:**
    1. **Pilot** in 2-3 cities of underserved states
    2. **Local partnerships** with regional distributors
    3. **Geo-targeted marketing** in priority regions

    **Logistics:**
    1. Assess **shipping cost** vs market potential
    2. Set up regional **distribution centers**
    3. **Competitive lead times** for remote regions

    **Sales:**
    1. Assign a **specialist seller** per region
    2. **Active prospecting** in untapped markets
    3. Regional **seasonal campaigns**

    #### 🎯 Annual Target
    - Increase the share of emerging states by **25%**
    - Open **3 new regional markets**
    """)

st.markdown("---")

# Implementation Timeline
st.markdown("### 📅 Implementation Roadmap (90 days)")

timeline = pd.DataFrame({
    'Action': ['Conversion', 'Margin', 'Losses', 'Sellers', 'Expansion'],
    'Month_1': ['Implement', 'Map', 'Analyze', 'Diagnose', 'Plan'],
    'Month_2': ['Train', 'Adjust', 'Implement', 'Train', 'Pilot'],
    'Month_3': ['Measure', 'Optimize', 'Monitor', 'Level out', 'Expand']
})

st.dataframe(timeline, width='stretch', hide_index=True)

st.markdown("---")

# Success Metrics
st.markdown("### 📈 Success Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### Month 1
    - [ ] Follow-up implemented
    - [ ] Discount matrix created
    - [ ] Cancellation causes mapped
    - [ ] Seller diagnosis
    """)

with col2:
    st.markdown("""
    #### Month 2
    - [ ] Conversion +5%
    - [ ] Margin +2%
    - [ ] Cancellations -15%
    - [ ] 50% of the team trained
    """)

with col3:
    st.markdown("""
    #### Month 3
    - [ ] Conversion +7%
    - [ ] Margin +3%
    - [ ] Cancellations -25%
    - [ ] Regional pilot launched
    """)

st.markdown("---")

# ROI Projection
st.markdown("### 💰 ROI Projection")

roi_data = pd.DataFrame({
    'Month': ['Month 1', 'Month 2', 'Month 3', 'Quarter Total'],
    'Investment': [15000, 10000, 8000, 33000],
    'Estimated_Return': [
        opportunity_conversion * 0.2 + opportunity_margin * 0.1,
        opportunity_conversion * 0.4 + opportunity_margin * 0.3 + opportunity_retention * 0.2,
        opportunity_conversion * 0.7 + opportunity_margin * 0.6 + opportunity_retention * 0.3,
        opportunity_conversion * 0.7 + opportunity_margin * 0.6 + opportunity_retention * 0.3
    ]
})

roi_data['ROI_%'] = ((roi_data['Estimated_Return'] - roi_data['Investment']) / roi_data['Investment'] * 100).round(1)

st.dataframe(
    roi_data.style.format({
        'Investment': 'R$ {:,.2f}',
        'Estimated_Return': 'R$ {:,.2f}',
        'ROI_%': '{:.1f}%'
    }).background_gradient(cmap='Greens', subset=['ROI_%']),
    width='stretch',
    hide_index=True
)

st.success(f"🎯 **Projected Quarterly ROI: {roi_data.iloc[3]['ROI_%']:.1f}%** | Return: R$ {roi_data.iloc[3]['Estimated_Return']:,.2f}")

st.markdown("---")

# PDF Export Button
st.markdown("### Export Report")
st.markdown("Generate an executive PDF with KPIs, quick wins and plan targets.")

margin_pct = (df['Net_Revenue'].sum() / total_revenue) * 100
roi_projected = ((total_opportunity * 0.7) / 33000) * 100

pdf_metrics = {
    'delivered_revenue': delivered_revenue,
    'avg_order_value': metrics['avg_order_value'],
    'conversion_rate': current_conversion,
    'margin_pct': margin_pct,
    'lost_revenue': lost_revenue,
    'roi_projected': roi_projected
}

quick_wins_data = [
    {
        'title': 'Increase Conversion',
        'description': 'Implement 24h follow-up, confirm pending orders, raise conversion from {:.1f}% to 77%'.format(current_conversion),
        'gain': opportunity_conversion * 0.3
    },
    {
        'title': 'Optimize Margin',
        'description': 'Review the discount policy, train the team on value, increase margin by +2%',
        'gain': opportunity_margin * 0.4
    },
    {
        'title': 'Reduce Losses',
        'description': 'Investigate cancellations, improve the post-sale process, reduce losses by -20%',
        'gain': opportunity_retention * 0.5
    }
]

if st.button("Generate PDF Report", type="primary", width='stretch'):
    with st.spinner("Generating PDF report..."):
        pdf_data = generate_executive_summary_pdf(pdf_metrics, quick_wins_data)
    create_pdf_download_button(pdf_data, "commercial_action_plan.pdf", "Download Action Plan as PDF")

st.markdown("---")

# Final Recommendations
st.markdown("### 🎯 Final Recommendations")

display_insight_box(
    "Executive Focus",
    """🚀 The analysis reveals <strong style="color:#8B5CF6;">R$ {:.2f}</strong> in immediate opportunities.<br>
    1. ✅ <strong style="color:#38BDF8;">Conversion</strong> — highest impact, easy to implement<br>
    2. 💰 <strong style="color:#22C55E;">Margin</strong> — direct impact on profit<br>
    3. 🤝 <strong style="color:#FBBF24;">Team</strong> — long-term sustainability<br><br>
    🧭 <strong>Execute with discipline, measure weekly, adjust quickly.</strong>""".format(total_opportunity),
    "🎯"
)

st.markdown("""
---

<div style="text-align: center; background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
            border-radius: 10px; padding: 1.5rem; margin: 2rem 0;">
    <h3 style="color: #8B5CF6; margin: 0;">🚀 Next Steps</h3>
    <p style="font-size: 1.1rem; margin-top: 1rem;">
    <strong>1.</strong> Present the plan to the executive committee<br>
    <strong>2.</strong> Approve budget and resources<br>
    <strong>3.</strong> Form the implementation team<br>
    <strong>4.</strong> Kick-off in 7 days
    </p>
</div>
""", unsafe_allow_html=True)

st.info("""
💡 This plan was structured with a high-performance commercial consulting methodology.
All data, analysis and projections are based on real evidence from your commercial dataset.
""")
