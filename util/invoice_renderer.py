import jinja2

class InvoiceRenderer:
    def __init__(self):
        self.template_loader = jinja2.FileSystemLoader(searchpath="./templates/invoices")
        self.template_env = jinja2.Environment(loader=self.template_loader)
        self.template_file = "invoice001.html"

    def render_html(self, attributes):
        """
        Render html page using jinja attributes
        """
        template = self.template_env.get_template(self.template_file)
        output_text = template.render(attributes)

        return output_text
