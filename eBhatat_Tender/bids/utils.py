from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

def generate_bid_receipt_pdf(bid):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    elements = []
    styles = getSampleStyleSheet()

    # ---------------- STYLES ----------------
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=24,
        textColor=colors.HexColor("#0f2a5e"),
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )

    subtitle_style = ParagraphStyle(
        'subtitle_style',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=12,
        textColor=colors.HexColor("#FF671F"),
        spaceAfter=20,
        fontName="Helvetica-Bold"
    )

    ack_style = ParagraphStyle(
        'ack_style',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=11,
        textColor=colors.black,
        leading=16,
        spaceAfter=20
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

    # ---------------- LOGO / TITLE AREA ----------------
    # Simulated Logo & Header Banner
    elements.append(Paragraph("eBharat Tender System", title_style))
    elements.append(Paragraph("OFFICIAL BID ACKNOWLEDGEMENT RECEIPT", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0f2a5e"), spaceAfter=20))

    # ---------------- ACKNOWLEDGEMENT PARAGRAPH ----------------
    ack_text = (
        f"This official document serves as a formal acknowledgement that <b>{bid.company_name}</b> "
        f"has successfully submitted a bid application for the tender <b>{bid.tender.title}</b> "
        f"(Reference ID: {bid.tender.tender_id}) on the eBharat electronic procurement platform. "
        f"The application was officially recorded on {bid.applied_at.strftime('%d %B %Y, %I:%M %p')}. "
        f"Please retain this document for future reference."
    )
    elements.append(Paragraph(ack_text, ack_style))

    # ---------------- IMPORTANT DATA TABLE ----------------
    elements.append(Paragraph("<b>1. Key Submission Data</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.1 * inch))

    key_data = [
        ["Tender Reference", bid.tender.tender_id],
        ["Bid Amount", f"INR {float(bid.bid_amount):,.2f}"],
        ["EMD Status", bid.payment_status.upper()],
        ["Razorpay ID", bid.razorpay_payment_id if bid.razorpay_payment_id else "N/A"],
        ["Submitted By", bid.bidder_name],
        ["Official Email", bid.official_email]
    ]

    key_table = Table(key_data, colWidths=[160, 310])
    key_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#0f2a5e")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(key_table)
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- COMPANY INFORMATION ----------------
    elements.append(Paragraph("<b>2. Registered Entity Details</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.1 * inch))

    company_data = [
        ["Entity Name", bid.company_name],
        ["GSTIN", bid.gst_number],
        ["Location", f"{bid.city}, {bid.state} - {bid.pin_code}"],
    ]

    company_table = Table(company_data, colWidths=[160, 310])
    company_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.6 * inch))

    # ---------------- SIGNATURE AREA ----------------
    sign_data = [
        ["__________________________", "__________________________"],
        ["Authorized Signatory", "Tender Inviting Authority"],
        [f"({bid.bidder_name})", "(Govt. of India e-Procurement)"]
    ]

    sign_table = Table(sign_data, colWidths=[235, 235])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('FONTSIZE', (0, 2), (-1, 2), 9),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.grey),
    ]))

    elements.append(sign_table)
    
    # =====================================================================
    # PAGE BREAK FOR TERMS & CONDITIONS
    # =====================================================================
    elements.append(PageBreak())

    elements.append(Paragraph("Annexure I: General Terms & Conditions", title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0f2a5e"), spaceAfter=20))
    
    terms = [
        "1. Validity of Bid: The bid submitted by the entity shall remain valid as per the timeframe stipulated in the official tender documents, typically 90 days from the date of opening.",
        "2. Earnest Money Deposit (EMD): The EMD paid (if applicable) is subject to the conditions of the tender. It may be forfeited if the bidder withdraws the bid within the validity period or fails to sign the contract if awarded.",
        "3. Verification of Documents: The eBharat Authority reserves the right to physically verify original documents (Technical, Financial, GST) at any stage of the procurement cycle. Discrepancies may lead to immediate disqualification.",
        "4. Non-Transferability: This acknowledgement receipt and the associated bid application are strictly non-transferable.",
        "5. Final Authority: The decision of the Tender Inviting Authority (TIA) regarding the acceptance or rejection of a bid is final and legally binding on all participating entities.",
        "6. Confidentiality: All details submitted within this portal are maintained under strict confidentiality acts in accordance with the Information Technology Act, 2000.",
        "7. Jurisdiction: Any disputes arising out of this procurement process shall be subject to the exclusive jurisdiction of the competent courts stationed in the state issuing the tender."
    ]
    
    for term in terms:
        elements.append(Paragraph(term, terms_style))

    # Build PDF
    doc.build(elements)

    return buffer.getvalue()
