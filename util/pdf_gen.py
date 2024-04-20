import pdfkit

class InvoicePDFGenerator:
        
    @staticmethod
    def generate_pdf(html_content):
        # Generate PDF from HTML content
        pdf = pdfkit.from_string(html_content, False)

        # Return PDF as bytes
        return pdf
