from util.invoice_renderer import InvoiceRenderer
from util.pdf_gen import InvoicePDFGenerator

# Example usage
def invoice_to_pdf(full_invoice_data):
    # Renderizamos el contenido HTML del invoice
    renderer = InvoiceRenderer()

    html_content = renderer.render_html(full_invoice_data)

    # Generamos el PDF del invoice
    pdf_bytes = InvoicePDFGenerator.generate_pdf(html_content)

    return pdf_bytes

