from twilio.rest import Client
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO

load_dotenv()

class TwilioMessageService:
    def __init__(self):
        # API Key Authentication
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')  # Main Account SID (AC...)
        api_key_sid = os.getenv('TWILIO_API_KEY_SID')  # API Key SID (SK...)
        api_key_secret = os.getenv('TWILIO_API_KEY_SECRET')  # API Key Secret
        
        # Create client using API Key authentication
        # Format: Client(api_key_sid, api_key_secret, account_sid)
        self.client = Client(api_key_sid, api_key_secret, account_sid)
    
    def get_messages_for_number(self, phone_number: str, days_back: int = 90) -> pd.DataFrame:
        """Get messages for a specific phone number"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            messages = self.client.messages.list(
                to=phone_number,
                date_sent_after=start_date,
                date_sent_before=end_date
            )
            
            data = []
            for msg in messages:
                data.append({
                    'Date': msg.date_sent.strftime('%Y-%m-%d %H:%M:%S'),
                    'SMS SID': msg.sid,
                    'Status': msg.status,
                    'Message': msg.body
                })
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return pd.DataFrame()
    
    def create_messages_pdf(self, phone_number: str, df: pd.DataFrame) -> bytes:
        """Create PDF from messages DataFrame"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>SMS Messages Report from Twilio</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Information
        info = Paragraph(
            f"<b>Number:</b> {phone_number}<br/>"
            f"<b>Total SMS messages:</b> {len(df)}", 
            styles['Normal']
        )
        elements.append(info)
        elements.append(Spacer(1, 20))
        
        if not df.empty:
            # Prepare table data
            table_data = [['Date', 'SMS SID', 'Status', 'Message']]
            for _, row in df.iterrows():
                date_para = Paragraph(row['Date'], styles['Normal'])
                sid_para = Paragraph(row['SMS SID'][:20] + '...' if len(row['SMS SID']) > 20 else row['SMS SID'], styles['Normal'])
                status_para = Paragraph(row['Status'], styles['Normal'])
                message_para = Paragraph(row['Message'], styles['Normal'])
                table_data.append([date_para, sid_para, status_para, message_para])
            
            elements.append(Spacer(1, 12))
            table = Table(table_data, colWidths=[1.5*inch, 1.8*inch, 0.8*inch, 3.4*inch], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ]))
            elements.append(table)
        else:
            no_data = Paragraph("No messages found in the specified date range.", styles['Normal'])
            elements.append(no_data)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()