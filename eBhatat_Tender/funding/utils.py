import os
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable

def generate_funding_award_pdf(app):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14

    # 1. Logo
    logo_path = os.path.join(settings.BASE_DIR, 'public', 'static', 'images', 'Logo', 'gov-logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=80, height=80)
        elements.append(img)
        elements.append(Spacer(1, 12))
        
    # 2. Header
    elements.append(Paragraph("<b>eBharat Tender Portal</b>", title_style))
    elements.append(Paragraph("<b>OFFICIAL NOTIFICATION OF FUNDING APPROVAL</b>", title_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 24))
    
    # 3. Intro text
    intro_text = f"Dear <b>{app.bidder.first_name or app.bidder.username}</b>,<br/><br/>" \
                 f"The <b>eBharat Financial Assistance Division</b> is pleased to inform you that your application for financial support under the scheme <b>{app.funding.title}</b> has been thoroughly reviewed and <b>officially approved</b>.<br/><br/>" \
                 f"This document serves as the formal record of your approved grant. The approved amount of <b>INR {app.amount_requested}</b> has been successfully credited to your <b>eBharat Funding Wallet</b> and may be utilized for procurement activities associated with the designated tender."
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 24))

    # 4. Table for data
    data = [
        ["Funding Approval Details", ""],
        ["Funding Scheme:", app.funding.title],
        ["Purpose/Utilization:", app.purpose[:100] + "..." if len(app.purpose)>100 else app.purpose],
        ["Approved Amount:", f"INR {app.amount_requested}"],
        ["Interest Rate:", f"{app.funding.interest_rate}% p.a."],
        ["Wallet Status:", "ADDED (Available for Use)"],
        ["", ""],
        ["Associated Tender Information", ""],
        ["Tender Title:", app.tender.title],
        ["Tender ID:", app.tender.tender_id],
        ["Department:", app.tender.department],
        ["Total Tender Value:", f"INR {app.tender.estimated_value}"],
    ]
    
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#166534")),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 7), (1, 7), colors.HexColor("#166534")),
        ('TEXTCOLOR', (0, 7), (1, 7), colors.whitesmoke),
        ('FONTNAME', (0, 7), (1, 7), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 7), (1, 7), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, 5), 'Helvetica-Bold'),
        ('FONTNAME', (0, 8), (0, 11), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # 5. Outro
    outro_text = "<b>Important Guideline:</b> The allocated funds must strictly be applied toward the execution of the specified tender project. Failure to adhere to the terms and conditions outlined in the scheme guidelines may result in immediate revocation of the awarded funds.<br/><br/>Warm Regards,<br/><b>Financial Support Division</b><br/>eBharat Tender Portal"
    elements.append(Paragraph(outro_text, normal_style))
    
    doc.build(elements)
    
    return buffer.getvalue()
