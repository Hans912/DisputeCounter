

def get_invoice_by_id() -> str:
    return """
    SELECT 
        InvoiceId,
        CustomerId,
        CustomerFullName,
        CompanyName,
        CAST(IssuedOn AS VARCHAR(23)) as IssuedOn
    FROM RP_Invoices
    WHERE InvoiceId = ?
    """

def get_dispute_by_id() -> str:
    return """
    SELECT *
    FROM StripeChargeDisputes
    WHERE ExternalPaymentDisputeId = ?
    """

def get_customer_phone_by_id() -> str:
    return """
    SELECT PhoneNumber
    FROM CustomerAuthenticationAccounts
    WHERE CustomerId = ?
    """

def get_invoices_query():
    return """
    SELECT
        i.InvoiceID,
        i.CustomerID,
        i.Amount,
        CONVERT(NVARCHAR(33), i.CreatedAt, 127) AS CreatedAt,  -- was DATETIMEOFFSET
        -- other columns...
    FROM dbo.Invoices i
    """