import streamlit as st
import pandas as pd
from db.data_loader import get_invoice_data, get_dispute_data, get_customer_phone
from services.twilio_service import TwilioMessageService
from datetime import datetime

# Configure page to use wide layout
st.set_page_config(
    page_title="STAMP Dispute Tool",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ STAMP Dispute Tool")

# Sidebar inputs
with st.sidebar:
    st.header("Query Inputs")
    dispute_id = st.text_input("Dispute ID")
    
    if st.button("Get Data", use_container_width=True):
        # Store results in session state
        if dispute_id:
            # First get dispute data
            st.session_state.dispute_data = get_dispute_data(dispute_id)
            
            # Then automatically get invoice data using ServiceId from dispute
            if not st.session_state.dispute_data.empty and 'ServiceId' in st.session_state.dispute_data.columns:
                service_id = st.session_state.dispute_data['ServiceId'].iloc[0]
                if service_id:
                    st.session_state.invoice_data = get_invoice_data(service_id)
                    
                    # Get customer phone number
                    if not st.session_state.invoice_data.empty and 'CustomerId' in st.session_state.invoice_data.columns:
                        customer_id = st.session_state.invoice_data['CustomerId'].iloc[0]
                        st.session_state.customer_phone = get_customer_phone(customer_id)
                else:
                    st.session_state.invoice_data = pd.DataFrame()
                    st.session_state.customer_phone = None
            else:
                st.session_state.invoice_data = pd.DataFrame()
                st.session_state.customer_phone = None

# Main area - display results using full width
if hasattr(st.session_state, 'invoice_data') and not st.session_state.invoice_data.empty:
    st.subheader("Invoice Data")
    st.dataframe(st.session_state.invoice_data, use_container_width=True)
elif hasattr(st.session_state, 'invoice_data'):
    st.info("No invoice data found")

if hasattr(st.session_state, 'dispute_data') and not st.session_state.dispute_data.empty:
    st.subheader("Dispute Data")
    st.dataframe(st.session_state.dispute_data, use_container_width=True)
    
    # Add Dispute Type section
    st.subheader("Dispute Type")
    dispute_reason = ""
    if 'ExternalPaymentDisputeReason' in st.session_state.dispute_data.columns:
        dispute_reason = str(st.session_state.dispute_data['ExternalPaymentDisputeReason'].iloc[0])
    
    st.write(dispute_reason if dispute_reason else 'Unknown')
elif hasattr(st.session_state, 'dispute_data'):
    st.info("No dispute data found")

# Show sections only if both data sets exist
if (hasattr(st.session_state, 'invoice_data') and not st.session_state.invoice_data.empty and 
    hasattr(st.session_state, 'dispute_data') and not st.session_state.dispute_data.empty):
    
    # Why should you win this dispute? Section
    st.subheader("⚖️ Why should you win this dispute?")
    
    # Get dispute reason from the data
    dispute_reason = ""
    if 'ExternalPaymentDisputeReason' in st.session_state.dispute_data.columns:
        dispute_reason = str(st.session_state.dispute_data['ExternalPaymentDisputeReason'].iloc[0]).lower()
    
    # Define available options based on dispute type (from screenshots analysis)
    def get_available_options(dispute_reason):
        # Fraudulent dispute options (Screenshot 1 - 4 options)
        fraudulent_options = [
            "The cardholder withdrew the dispute",
            "The cardholder was refunded", 
            "The purchase was made by the rightful cardholder",
            "Other"
        ]
        
        # General dispute options (Screenshot 2 - 10 options)
        general_options = [
            "The cardholder withdrew the dispute",
            "The cardholder was refunded",
            "The transaction was non-refundable",
            "The dispute was made past the return or cancellation period of your terms",
            "The cardholder received a credit or voucher",
            "The product, service, event or booking was cancelled or delayed due to a government order (COVID-19)",
            "The cardholder received the product or service",
            "The purchase was made by the rightful cardholder",
            "The purchase is unique",
            "Other"
        ]
        
        # Credit not processed dispute options (Screenshot 3 - 7 options)
        credit_not_processed_options = [
            "The cardholder withdrew the dispute",
            "The cardholder was refunded",
            "The transaction was non-refundable",
            "The dispute was made past the return or cancellation period of your terms",
            "The cardholder received a credit or voucher",
            "The product, service, event or booking was cancelled or delayed due to a government order (COVID-19)",
            "Other"
        ]
        
        # Map dispute reasons to available options
        if "fraud" in dispute_reason or "fraudulent" in dispute_reason:
            return fraudulent_options
        elif "general" in dispute_reason or "unrecognized" in dispute_reason:
            return general_options
        elif "credit_not_processed" in dispute_reason or "credit not processed" in dispute_reason or "duplicated" in dispute_reason or "duplicate" in dispute_reason:
            return credit_not_processed_options
        else:
            # Default to general options for unknown dispute types
            return general_options
    
    # Get available options for this dispute type
    available_options = get_available_options(dispute_reason)
    
    # Determine recommended option based on dispute type
    def get_recommended_option(dispute_reason, available_options):
        if "fraud" in dispute_reason or "fraudulent" in dispute_reason:
            return "The purchase was made by the rightful cardholder"
        elif "credit_not_processed" in dispute_reason or "credit not processed" in dispute_reason or "duplicated" in dispute_reason or "duplicate" in dispute_reason:
            return "The transaction was non-refundable"
        elif "general" in dispute_reason or "unrecognized" in dispute_reason:
            return "The cardholder received the product or service"
        else:
            # Default to first available option
            return available_options[0] if available_options else "Other"
    
    recommended_option = get_recommended_option(dispute_reason, available_options)
    
    # Manual override dropdown - only show available options
    manual_override = st.selectbox(
        "Select your response:",
        ["Use recommended"] + available_options,
        help="Options are limited based on the dispute type detected"
    )
    
    # Determine selected option
    if manual_override == "Use recommended":
        selected_option = recommended_option
    else:
        selected_option = manual_override
    
    st.write("**Selected option:**")
    
    # Display only available options with selection indicator
    for option in available_options:
        if option == selected_option:
            st.markdown(f"● **{option}** ✓")
        else:
            st.markdown(f"○ {option}")

    # Product or Service Details Section
    st.subheader("📦 Product or service details")
    
    st.write("**Description**")
    
    # Get dynamic values from invoice data
    customer_name = "[Customer Name]"
    issued_date = "[Invoice Date]"
    company_name = "[Company Name]"
    
    if hasattr(st.session_state, 'invoice_data') and not st.session_state.invoice_data.empty:
        if 'CustomerFullName' in st.session_state.invoice_data.columns:
            customer_name = str(st.session_state.invoice_data['CustomerFullName'].iloc[0])
        if 'IssuedOn' in st.session_state.invoice_data.columns:
            issued_date = str(st.session_state.invoice_data['IssuedOn'].iloc[0])
        if 'CompanyName' in st.session_state.invoice_data.columns:
            company_name = str(st.session_state.invoice_data['CompanyName'].iloc[0])
    
    product_description = st.text_area(
        "",
        value=f"""STAMP is a Real Tax Free service provider that enables eligible non-EU travelers to shop without paying VAT at the point of purchase in participating European stores.

Travelers register with STAMP and accept our Terms & Conditions, which explain that VAT will be charged if the required customs export validation is not completed. This process complies with EU VAT regulations.

{customer_name} made a one-time purchase using STAMP's service on {issued_date} at {company_name}. The VAT charge for this dispute was applied because no customs validation was received, in line with the agreed terms and legal requirements.""",
        height=200,
        label_visibility="collapsed"
    )
    
    st.write("**What type of product or service is this?**")
    
    # Product type options
    product_options = [
        "Physical product",
        "Digital product or service",
        "Offline service", 
        "Event",
        "Booking or reservation",
        "Other"
    ]
    
    # Pre-select "Digital product or service" and make it the only selectable option
    selected_product_type = "Digital product or service"
    
    # Display all options but only allow the correct one to be selected
    for option in product_options:
        if option == selected_product_type:
            st.markdown(f"● **{option}** ✓")
        else:
            st.markdown(f"<span style='color: #888888'>○ {option}</span>", unsafe_allow_html=True)
    
    # Documents Section
    st.subheader("📄 Documents")
    
    # Show customer phone number if available
    if hasattr(st.session_state, 'customer_phone') and st.session_state.customer_phone:
        st.write(f"**Customer Phone Number:** {st.session_state.customer_phone}")
        
        # Twilio Messages Section
        st.write("**SMS Messages Report**")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            days_back = st.number_input("Days to look back", min_value=1, max_value=365, value=90)
        
        with col2:
            if st.button("Generate SMS Report", use_container_width=True):
                with st.spinner("Retrieving SMS messages..."):
                    twilio_service = TwilioMessageService()
                    messages_df = twilio_service.get_messages_for_number(
                        st.session_state.customer_phone, 
                        days_back
                    )
                    
                    if not messages_df.empty:
                        st.session_state.messages_df = messages_df
                        
                        # Generate PDF
                        pdf_bytes = twilio_service.create_messages_pdf(
                            st.session_state.customer_phone,
                            messages_df
                        )
                        st.session_state.messages_pdf = pdf_bytes
                        
                        st.success(f"Found {len(messages_df)} messages")
                    else:
                        st.warning("No messages found for this phone number")
        
        # Display messages if available
        if hasattr(st.session_state, 'messages_df') and not st.session_state.messages_df.empty:
            st.write("**Messages Preview:**")
            st.dataframe(st.session_state.messages_df, use_container_width=True)
            
            # Download button for PDF
            if hasattr(st.session_state, 'messages_pdf'):
                st.download_button(
                    label="📥 Download SMS Report PDF",
                    data=st.session_state.messages_pdf,
                    file_name=f"sms_report_{st.session_state.customer_phone.replace('+', '')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        st.info("Customer phone number not found. Please ensure invoice data is loaded.")