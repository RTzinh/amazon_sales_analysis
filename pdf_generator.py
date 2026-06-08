from fpdf import FPDF
from datetime import datetime
import pandas as pd

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
    def header(self):
        """Header with title and logo"""
        self.set_font('Arial', 'B', 20)
        self.set_text_color(139, 92, 246)
        self.cell(0, 15, 'Commercial Performance Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, f'Generated on: {datetime.now().strftime("%m/%d/%Y %H:%M")}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        """Footer with page number"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_executive_summary_pdf(metrics, quick_wins):
    """Generate executive summary PDF report"""
    pdf = ReportPDF()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, 'Executive Summary', 0, 1)
    pdf.ln(5)

    # KPIs Section
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Key Indicators', 0, 1)
    pdf.ln(2)

    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(51, 65, 85)

    kpis = [
        ('Actual Revenue', f"R$ {metrics['delivered_revenue']:,.2f}"),
        ('Average Order Value', f"R$ {metrics['avg_order_value']:,.2f}"),
        ('Conversion Rate', f"{metrics['conversion_rate']:.1f}%"),
        ('Net Margin', f"{metrics['margin_pct']:.1f}%"),
        ('Commercial Losses', f"R$ {metrics['lost_revenue']:,.2f}"),
        ('Projected ROI (90 days)', f"{metrics['roi_projected']:.0f}%"),
    ]
    
    for label, value in kpis:
        pdf.cell(80, 7, f'  {label}:', 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(100, 7, value, 0, 1)
        pdf.set_font('Arial', '', 11)
    
    pdf.ln(5)
    
    # Quick Wins Section
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Quick Wins - Priority Actions', 0, 1)
    pdf.ln(2)

    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(51, 65, 85)
    available_width = pdf.w - pdf.l_margin - pdf.r_margin

    for i, win in enumerate(quick_wins, 1):
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(139, 92, 246)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(available_width, 7, f'Quick Win #{i}: {win["title"]}')

        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(available_width, 5, f'- {win["description"]}')

        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(16, 185, 129)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(available_width, 6, f'Estimated Gain: R$ {win["gain"]:,.2f}')
        pdf.ln(4)

    pdf.ln(5)

    # Footer note
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 5, 'This report was generated automatically based on the analysis of 100,000 transactions. '
                         'For full details, see the interactive dashboards.')
    
    # FPDF2 output can be str/bytes/bytearray depending on version/config.
    data = pdf.output(dest='S')
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    return str(data).encode('latin-1', errors='replace')

def generate_performance_pdf(seller_data, metrics):
    """Generate performance report PDF"""
    pdf = ReportPDF()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, 'Performance Report by Seller', 0, 1)
    pdf.ln(5)

    # Top 10 Sellers Table
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Top 10 Sellers', 0, 1)
    pdf.ln(2)

    # Table header
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(139, 92, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 7, 'Seller', 1, 0, 'C', True)
    pdf.cell(40, 7, 'Revenue', 1, 0, 'C', True)
    pdf.cell(30, 7, 'Avg Order Value', 1, 0, 'C', True)
    pdf.cell(25, 7, 'Sales', 1, 0, 'C', True)
    pdf.cell(25, 7, 'Margin %', 1, 1, 'C', True)
    
    # Table data
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0, 0, 0)
    
    for idx, row in seller_data.head(10).iterrows():
        pdf.cell(30, 6, str(idx)[:10], 1, 0, 'L')
        pdf.cell(40, 6, f"R$ {row['Revenue']:,.0f}", 1, 0, 'R')
        pdf.cell(30, 6, f"R$ {row['Avg_Order_Value']:,.0f}", 1, 0, 'R')
        pdf.cell(25, 6, f"{row['Sales']:.0f}", 1, 0, 'C')
        pdf.cell(25, 6, f"{row['Margin_%']:.1f}%", 1, 1, 'C')
    
    pdf.ln(5)
    
    # Key Insights
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Key Insights', 0, 1)
    pdf.ln(2)

    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"- Top seller earned R$ {seller_data.iloc[0]['Revenue']:,.2f}\n"
                         f"- Team average order value: R$ {seller_data['Avg_Order_Value'].mean():,.2f}\n"
                         f"- Average margin: {seller_data['Margin_%'].mean():.1f}%\n"
                         f"- Performance gap: {((seller_data.iloc[0]['Revenue'] / seller_data['Revenue'].mean() - 1) * 100):.1f}%")
    
    data = pdf.output(dest='S')
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    return str(data).encode('latin-1', errors='replace')

def create_pdf_download_button(pdf_data, filename, button_text="📥 Download PDF Report"):
    """Create a styled download button for PDF"""
    import streamlit as st
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label=button_text,
            data=pdf_data,
            file_name=filename,
            mime="application/pdf",
            width='stretch',
            type="secondary"
        )
