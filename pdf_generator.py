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
        self.cell(0, 15, 'Relatorio de Performance Comercial', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """Footer with page number"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generate_executive_summary_pdf(metrics, quick_wins):
    """Generate executive summary PDF report"""
    pdf = ReportPDF()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, 'Sumario Executivo', 0, 1)
    pdf.ln(5)
    
    # KPIs Section
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Indicadores Principais', 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(51, 65, 85)
    
    kpis = [
        ('Faturamento Real', f"R$ {metrics['delivered_revenue']:,.2f}"),
        ('Ticket Medio', f"R$ {metrics['avg_order_value']:,.2f}"),
        ('Taxa de Conversao', f"{metrics['conversion_rate']:.1f}%"),
        ('Margem Liquida', f"{metrics['margin_pct']:.1f}%"),
        ('Perdas Comerciais', f"R$ {metrics['lost_revenue']:,.2f}"),
        ('ROI Projetado (90 dias)', f"{metrics['roi_projected']:.0f}%"),
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
    pdf.cell(0, 8, 'Quick Wins - Acoes Prioritarias', 0, 1)
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
        pdf.multi_cell(available_width, 6, f'Ganho Estimado: R$ {win["gain"]:,.2f}')
        pdf.ln(4)
    
    pdf.ln(5)
    
    # Footer note
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 5, 'Este relatorio foi gerado automaticamente com base na analise de 100.000 transacoes. '
                         'Para detalhes completos, acesse os dashboards interativos.')
    
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
    pdf.cell(0, 10, 'Relatorio de Performance por Vendedor', 0, 1)
    pdf.ln(5)
    
    # Top 10 Sellers Table
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Top 10 Vendedores', 0, 1)
    pdf.ln(2)
    
    # Table header
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(139, 92, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 7, 'Vendedor', 1, 0, 'C', True)
    pdf.cell(40, 7, 'Faturamento', 1, 0, 'C', True)
    pdf.cell(30, 7, 'Ticket Medio', 1, 0, 'C', True)
    pdf.cell(25, 7, 'Vendas', 1, 0, 'C', True)
    pdf.cell(25, 7, 'Margem %', 1, 1, 'C', True)
    
    # Table data
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0, 0, 0)
    
    for idx, row in seller_data.head(10).iterrows():
        pdf.cell(30, 6, str(idx)[:10], 1, 0, 'L')
        pdf.cell(40, 6, f"R$ {row['Faturamento']:,.0f}", 1, 0, 'R')
        pdf.cell(30, 6, f"R$ {row['Ticket_Medio']:,.0f}", 1, 0, 'R')
        pdf.cell(25, 6, f"{row['Vendas']:.0f}", 1, 0, 'C')
        pdf.cell(25, 6, f"{row['Margem_%']:.1f}%", 1, 1, 'C')
    
    pdf.ln(5)
    
    # Key Insights
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Insights Principais', 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"• Top vendedor faturou R$ {seller_data.iloc[0]['Faturamento']:,.2f}\n"
                         f"• Ticket medio da equipe: R$ {seller_data['Ticket_Medio'].mean():,.2f}\n"
                         f"• Margem media: {seller_data['Margem_%'].mean():.1f}%\n"
                         f"• Gap de performance: {((seller_data.iloc[0]['Faturamento'] / seller_data['Faturamento'].mean() - 1) * 100):.1f}%")
    
    data = pdf.output(dest='S')
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    return str(data).encode('latin-1', errors='replace')

def create_pdf_download_button(pdf_data, filename, button_text="📥 Baixar Relatório PDF"):
    """Create a styled download button for PDF"""
    import streamlit as st
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label=button_text,
            data=pdf_data,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
            type="secondary"
        )
