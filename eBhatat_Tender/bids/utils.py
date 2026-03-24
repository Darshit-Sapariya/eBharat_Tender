from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_bid_receipt_pdf(bid):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # ---------------- HEADER ----------------
    header_style = ParagraphStyle(
        'header_style',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=18,
        spaceAfter=10
    )

    sub_header_style = ParagraphStyle(
        'sub_header_style',
        parent=styles['Normal'],
        alignment=1,
        fontSize=11,
        textColor=colors.grey
    )

    elements.append(Paragraph("eBharat Tender Portal", header_style))
    elements.append(Paragraph("Official Procurement Submission Record", sub_header_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------- SECTION 1 ----------------
    elements.append(Paragraph("<b>1. Tender Information</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.2 * inch))

    tender_data = [
        ["Tender Title", bid.tender.title],
        ["Category", str(bid.tender.category)],
        ["Issued By", str(bid.tender.created_by.username if bid.tender.created_by else 'Official Team')],
        ["Closing Date", bid.tender.closing_date.strftime("%d %B %Y")],
        ["Estimated Value", f"INR {bid.tender.estimated_value}"],
    ]

    tender_table = Table(tender_data, colWidths=[170, 300])
    tender_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(tender_table)
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- SECTION 2 ----------------
    elements.append(Paragraph("<b>2. Company Information</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.2 * inch))

    company_data = [
        ["Company Name", bid.company_name],
        ["GST Number", bid.gst_number],
        ["City", bid.city],
        ["State", bid.state],
        ["Pin Code", bid.pin_code],
    ]

    company_table = Table(company_data, colWidths=[170, 300])
    company_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(company_table)
    elements.append(Spacer(1, 0.4 * inch))

    # ---------------- SECTION 3 ----------------
    elements.append(Paragraph("<b>3. Bid Submission Details</b>", styles['Heading3']))
    elements.append(Spacer(1, 0.2 * inch))

    submission_data = [
        ["Authorized Representative", bid.bidder_name],
        ["Designation", bid.designation],
        ["Email", bid.official_email],
        ["Mobile", bid.mobile_number],
        ["Bid Amount", f"INR {bid.bid_amount}"],
        ["Status", bid.status.capitalize()],
        ["Submitted On", bid.applied_at.strftime("%d %B %Y")],
    ]

    submission_table = Table(submission_data, colWidths=[170, 300])
    submission_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
    ]))

    elements.append(submission_table)
    elements.append(Spacer(1, 0.6 * inch))

    # ---------------- SIGNATURE AREA ----------------
    sign_data = [
        ["__________________________", "__________________________"],
        ["Authorized Signatory", "Procurement Officer"],
    ]

    sign_table = Table(sign_data, colWidths=[250, 250])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))

    elements.append(sign_table)
    elements.append(Spacer(1, 0.5 * inch))
    
    # Build PDF
    doc.build(elements)

    return buffer.getvalue()
