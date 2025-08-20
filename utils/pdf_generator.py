from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

def generate_mock_pdf(document_type: str, invoice_id: str, dispute_id: str) -> bytes:
    """Generate mock PDF documents for evidence"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor='#1f4e79'
    )
    
    content = []
    
    # Title
    title = Paragraph(f"STAMP - {document_type}", title_style)
    content.append(title)
    content.append(Spacer(1, 20))
    
    # Document info
    info_style = styles['Normal']
    content.append(Paragraph(f"<b>Document Type:</b> {document_type}", info_style))
    content.append(Paragraph(f"<b>Invoice ID:</b> {invoice_id}", info_style))
    content.append(Paragraph(f"<b>Dispute ID:</b> {dispute_id}", info_style))
    content.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    content.append(Spacer(1, 30))
    
    # Document-specific content
    if "Invoice" in document_type:
        content.extend(generate_invoice_content(styles, invoice_id))
    elif "Terms" in document_type:
        content.extend(generate_terms_content(styles))
    else:
        content.extend(generate_generic_content(styles, document_type))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()

def generate_invoice_content(styles, invoice_id: str) -> list:
    """Generate mock invoice content"""
    content = []
    
    content.append(Paragraph("<b>INVOICE DETAILS</b>", styles['Heading2']))
    content.append(Spacer(1, 12))
    
    invoice_data = [
        f"Invoice Number: {invoice_id}",
        "Customer: John Doe",
        "Email: john.doe@example.com",
        "Purchase Date: 2024-01-15",
        "Item: Electronics Purchase",
        "Subtotal: €250.00",
        "VAT (20%): €50.00",
        "Total: €300.00",
        "VAT Exemption: Applied (Non-EU Traveler)",
        "Final Amount: €250.00"
    ]
    
    for line in invoice_data:
        content.append(Paragraph(line, styles['Normal']))
        content.append(Spacer(1, 6))
    
    return content

def generate_terms_content(styles) -> list:
    """Generate mock terms and conditions content"""
    content = []
    
    content.append(Paragraph("<b>TERMS AND CONDITIONS</b>", styles['Heading2']))
    content.append(Spacer(1, 12))
    
    terms_text = """
    1. STAMP provides VAT-free shopping services for eligible non-EU travelers.
    
    2. Customers must meet all customs requirements for VAT exemption.
    
    3. Failure to complete customs procedures may result in VAT charges.
    
    4. All transactions are processed securely through our platform.
    
    5. Customer data is protected according to GDPR regulations.
    
    6. Disputes will be handled according to Stripe's dispute resolution process.
    """
    
    content.append(Paragraph(terms_text, styles['Normal']))
    
    return content

def generate_generic_content(styles, document_type: str) -> list:
    """Generate generic document content"""
    content = []
    
    content.append(Paragraph(f"<b>{document_type.upper()}</b>", styles['Heading2']))
    content.append(Spacer(1, 12))
    
    generic_text = f"""
    This is a placeholder document for {document_type}.
    
    In a production environment, this would contain:
    - Actual transaction data
    - Customer verification information
    - Relevant timestamps and metadata
    - Supporting documentation
    
    This mock document demonstrates the PDF generation capability
    of the STAMP Dispute Counter system.
    """
    
    content.append(Paragraph(generic_text, styles['Normal']))
    
    return content