import os
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable

def generate_award_pdf(context):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=40, 
        bottomMargin=40
    )
    elements = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=20,
        textColor=colors.HexColor("#0f2a5e"),
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )
    
    subtitle_style = ParagraphStyle(
        'subtitle_style',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=12,
        textColor=colors.HexColor("#16a34a"),
        spaceAfter=24,
        fontName="Helvetica-Bold"
    )

    normal_style = ParagraphStyle(
        'normal_style',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=16,
        spaceAfter=14
    )

    terms_style = ParagraphStyle(
        'terms_style',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        leading=15,
        spaceAfter=12
    )
    
    # 1. Logo (Increased Size & Centered at Top)
    logo_path = os.path.join(settings.BASE_DIR, 'public', 'static', 'images', 'Logo', 'gov-logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=130, height=130)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 10))
        
    # 2. Header
    elements.append(Paragraph("eBharat Electronic Procurement System", title_style))
    elements.append(Paragraph("OFFICIAL LETTER OF AWARD", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f2a5e"), spaceAfter=20))
    
    # 3. Intro text
    intro_text = (
        f"Dear <b>{context.get('bidder_name', 'Authorized Representative')}</b>,<br/><br/>"
        f"On behalf of the eBharat Government Tender Authority, we are honored to officially inform you that "
        f"<b>{context.get('company_name', 'your company')}</b> has been successfully evaluated and awarded the contract "
        f"for the tender detailed below. This decision was based on technical and financial clearance."
    )
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 6))
    
    # 4. Table for data
    data = [
        ["I. Contract Information", ""],
        ["Reference ID:", context.get('tender_id', 'N/A')],
        ["Tender Title:", context.get('tender_title', 'N/A')],
        ["Department:", context.get('department', 'N/A')],
        ["Location:", context.get('location', 'N/A')],
        ["Awarded Amount:", f"INR {context.get('bid_amount', '0.00')}"],
        ["Award Date:", context.get('award_date', 'N/A')],
        ["", ""],
        ["II. Authorized Winning Entity", ""],
        ["Company Name:", context.get('company_name', 'N/A')],
        ["GST Identification:", context.get('gst_number', 'N/A')],
        ["Registered Address:", context.get('address', 'N/A')],
    ]
    
    table = Table(data, colWidths=[160, 320])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#0f2a5e")),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('TOPPADDING', (0, 0), (1, 0), 8),
        
        ('BACKGROUND', (0, 8), (1, 8), colors.HexColor("#0f2a5e")),
        ('TEXTCOLOR', (0, 8), (1, 8), colors.whitesmoke),
        ('FONTNAME', (0, 8), (1, 8), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 8), (1, 8), 8),
        ('TOPPADDING', (0, 8), (1, 8), 8),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0, 1), (0, 6), 'Helvetica-Bold'),
        ('FONTNAME', (0, 9), (0, 11), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # 5. Outro
    outro_text = (
        "The nodal procurement officer will contact you shortly regarding the formal contract signing, "
        "submission of the Performance Bank Guarantee (PBG), and project kickoff schedule. Please ensure all "
        "original physical copies of your documentation are ready for final verification.<br/><br/>"
        "Warm Regards,<br/><b>Tender Evaluation Committee</b><br/>eBharat Tender Portal"
    )
    elements.append(Paragraph(outro_text, normal_style))

    # =====================================================================
    # PAGE BREAK FOR TERMS & CONDITIONS
    # =====================================================================
    elements.append(PageBreak())

    elements.append(Paragraph("Annexure A: Standard Terms & Conditions of Contract (Award)", title_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f2a5e"), spaceAfter=20))
    
    terms = [
        "1. Acceptance of Award: The awarded entity must submit a formal letter of acceptance within 7 working days from the date of issuance of this award letter.",
        "2. Performance Security: The contractor must provide a Performance Bank Guarantee (PBG) equivalent to 5% of the total contract value prior to the contract signing.",
        "3. Physical Verification: The eBharat Authority reserves the right to request physical copies of all technical and financial documents. Any discrepancy will lead to immediate tender cancellation.",
        "4. Non-disclosure & Ethics: The contractor must strictly adhere to the integrity pact. Disclosure of confidential government information to third parties is heavily penalized.",
        "5. Subcontracting: No part of this contract shall be subcontracted to any third-party entity without prior written approval from the competent authority.",
        "6. Time is of the Essence: Strict adherence to the execution timeframe and milestones stated in the original tender notice is mandatory. Delays will attract Liquidated Damages (LD).",
        "7. Quality Assurance: The executed project/delivered items must explicitly abide by the technical specifications submitted during the bidding phases.",
        "8. Termination Clause: The Government reserves the right to terminate the contract at any stage giving a 14-day notice, should it find the work unsatisfactory or delayed.",
        "9. Dispute Resolution: In case of dispute, matters will primarily be referred to arbitration per the Arbitration and Conciliation Act, 1996, falling under the local governing jurisdiction.",
        "10. Final Binding: This provisional letter of award is legally binding and acts as the foundational agreement until the comprehensive multipartite physical contract is formally signed."
    ]
    
    for term in terms:
        elements.append(Paragraph(term, terms_style))
    
    doc.build(elements)
    
    return buffer.getvalue()
