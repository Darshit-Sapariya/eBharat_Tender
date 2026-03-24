import os
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def generate_award_pdf(context):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    normal_style = styles['Normal']
    
    # 1. Logo
    logo_path = os.path.join(settings.BASE_DIR, 'public', 'static', 'images', 'Logo', 'gov-logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=80, height=80)
        elements.append(img)
        elements.append(Spacer(1, 12))
        
    # 2. Header
    elements.append(Paragraph("<b>eBharat Tender Portal</b>", title_style))
    elements.append(Paragraph("<b>OFFICIAL AWARD OF CONTRACT</b>", title_style))
    elements.append(Spacer(1, 24))
    
    # 3. Intro text
    intro_text = f"Dear <b>{context['bidder_name']}</b>,<br/><br/>On behalf of the eBharat Government Tender Portal, we are honored to officially announce that <b>{context['company_name']}</b> has been awarded the contract for the following tender:"
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 12))
    
    # 4. Table for data
    data = [
        ["Contract Information", ""],
        ["Tender Title:", context['tender_title']],
        ["Tender ID:", context['tender_id']],
        ["Department:", context['department']],
        ["Location:", context['location']],
        ["Awarded Amount:", f"INR {context['bid_amount']}"],
        ["Award Date:", context['award_date']],
        ["", ""],
        ["Winning Bidder Profile", ""],
        ["Company Name:", context['company_name']],
        ["GST Number:", context['gst_number']],
        ["Registered Address:", context['address']],
    ]
    
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#166534")),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 8), (1, 8), colors.HexColor("#166534")),
        ('TEXTCOLOR', (0, 8), (1, 8), colors.whitesmoke),
        ('FONTNAME', (0, 8), (1, 8), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 8), (1, 8), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, 7), 'Helvetica-Bold'),
        ('FONTNAME', (0, 9), (0, 11), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # 5. Outro
    outro_text = "The procurement officer will contact you shortly regarding the contract signing and formal project kickoff. Please ensure all your documentation is ready for final verification.<br/><br/>Warm Regards,<br/><b>Regional Procurement Officer</b><br/>eBharat Tender Portal"
    elements.append(Paragraph(outro_text, normal_style))
    
    doc.build(elements)
    
    return buffer.getvalue()
