import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def apply_custom_css():
    """Apply custom CSS for beautiful UI"""
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Metric cards */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 1rem;
        }
        
        /* Cards with glassmorphism effect */
        .metric-card {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(139, 92, 246, 0.2);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            margin: 1rem 0;
        }
        
        /* Headers */
        h1 {
            background: linear-gradient(120deg, #8B5CF6, #3B82F6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        h2, h3 {
            color: #8B5CF6;
            font-weight: 600;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #8B5CF6, #3B82F6);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(139, 92, 246, 0.4);
        }
        
        /* Info boxes */
        .stAlert {
            border-radius: 10px;
            border-left: 5px solid #8B5CF6;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
            border-radius: 10px;
            font-weight: 600;
        }
        
        /* Dataframes */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, prefix="", suffix=""):
    """Create a beautiful metric card"""
    delta_html = f'<p style="color: {"#10b981" if delta and delta > 0 else "#ef4444"}; font-size: 0.9rem; margin: 0;">{"↑" if delta and delta > 0 else "↓"} {abs(delta) if delta else 0:.1f}%</p>' if delta is not None else ""
    
    html = f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 0.9rem; margin: 0; text-transform: uppercase; letter-spacing: 1px;">{title}</p>
        <h2 style="margin: 0.5rem 0; font-size: 2rem; font-weight: 700;">{prefix}{value:,.2f}{suffix}</h2>
        {delta_html}
    </div>
    """
    return html

def format_currency(value):
    """Format value as currency"""
    return f"${value:,.2f}"

def format_number(value):
    """Format large numbers with K/M suffix"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:.0f}"

def create_gauge_chart(value, max_value, title):
    """Create a gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "#8B5CF6"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value*0.33], 'color': '#fee2e2'},
                {'range': [max_value*0.33, max_value*0.66], 'color': '#fef3c7'},
                {'range': [max_value*0.66, max_value], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'}
    )
    
    return fig

def create_timeline_chart(df, x_col, y_col, title, color='#8B5CF6'):
    """Create interactive timeline chart"""
    fig = px.line(df, x=x_col, y=y_col, title=title)
    
    fig.update_traces(
        line_color=color,
        line_width=3,
        fill='tozeroy',
        fillcolor=f'rgba(139, 92, 246, 0.1)'
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        title={'font': {'size': 20, 'color': '#8B5CF6'}},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=400
    )
    
    return fig

def create_bar_chart(df, x_col, y_col, title, orientation='v', color='#8B5CF6'):
    """Create interactive bar chart"""
    if orientation == 'h':
        fig = px.bar(df, x=y_col, y=x_col, orientation='h', title=title)
    else:
        fig = px.bar(df, x=x_col, y=y_col, title=title)
    
    fig.update_traces(
        marker_color=color,
        marker_line_color='#8B5CF6',
        marker_line_width=1.5,
        opacity=0.8
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        title={'font': {'size': 20, 'color': '#8B5CF6'}},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=500,
        hovermode='closest'
    )
    
    return fig

def create_pie_chart(values, names, title):
    """Create interactive pie chart"""
    fig = px.pie(
        values=values,
        names=names,
        title=title,
        color_discrete_sequence=px.colors.sequential.Purples_r
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+value+percent'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        title={'font': {'size': 20, 'color': '#8B5CF6'}},
        height=500
    )
    
    return fig

def create_scatter_plot(df, x_col, y_col, color_col=None, title=''):
    """Create scatter plot with optional color dimension"""
    if color_col:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title,
                        color_continuous_scale='Purples')
    else:
        fig = px.scatter(df, x=x_col, y=y_col, title=title)
        fig.update_traces(marker={'color': '#8B5CF6', 'size': 8})
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        title={'font': {'size': 20, 'color': '#8B5CF6'}},
        xaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        yaxis={'showgrid': True, 'gridcolor': 'rgba(148, 163, 184, 0.1)'},
        height=500
    )
    
    return fig

def create_heatmap(data, x_labels, y_labels, title):
    """Create correlation heatmap"""
    fig = px.imshow(
        data,
        x=x_labels,
        y=y_labels,
        title=title,
        color_continuous_scale='Purples',
        aspect='auto'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        title={'font': {'size': 20, 'color': '#8B5CF6'}},
        height=500
    )
    
    return fig

def create_3d_scatter(df, x_col, y_col, z_col, color_col, title):
    """Create 3D scatter plot for clustering visualization"""
    fig = px.scatter_3d(
        df, 
        x=x_col, 
        y=y_col, 
        z=z_col, 
        color=color_col,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_layout(
        scene=dict(
            bgcolor='rgba(0,0,0,0)',
            xaxis={'backgroundcolor': 'rgba(0,0,0,0)', 'gridcolor': 'rgba(148, 163, 184, 0.2)'},
            yaxis={'backgroundcolor': 'rgba(0,0,0,0)', 'gridcolor': 'rgba(148, 163, 184, 0.2)'},
            zaxis={'backgroundcolor': 'rgba(0,0,0,0)', 'gridcolor': 'rgba(148, 163, 184, 0.2)'}
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        title={'font': {'size': 20, 'color': '#8B5CF6'}},
        height=600
    )
    
    return fig

def create_funnel_chart(stages, values, title):
    """Create funnel chart for conversion analysis"""
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ['#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6']}
    ))
    
    fig.update_layout(
        title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F1F5F9'},
        title_font={'size': 20, 'color': '#8B5CF6'},
        height=400
    )
    
    return fig

def display_insight_box(title, content, icon="💡"):
    """Display an insight box with icon"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.15));
        border-left: 5px solid #8B5CF6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <h3 style="margin: 0 0 0.5rem 0; color: #8B5CF6;">{icon} {title}</h3>
        <p style="margin: 0; color: #E2E8F0; line-height: 1.6;">{content}</p>
    </div>
    """, unsafe_allow_html=True)
