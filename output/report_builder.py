import os
from jinja2 import Environment, FileSystemLoader

def build_html_report(master_data, output_html_file):
    """
    Renders the HTML report using the Jinja2 template.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(current_dir, "templates")
    
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report.html.j2")
    
    # Render with master_data values
    html_content = template.render(
        meta=master_data.get("meta", {}),
        summary=master_data.get("summary", {}),
        components=master_data.get("components", {}),
        relationships=master_data.get("relationships", []),
        orphans=master_data.get("orphans", []),
        endpoints=master_data.get("endpoints", [])
    )
    
    # Ensure output dir exists
    output_dir = os.path.dirname(output_html_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return html_content

def build_pdf_report(output_html_file, output_pdf_file):
    """
    Converts the generated HTML report to a PDF using WeasyPrint.
    """
    try:
        from weasyprint import HTML
        print(f"📄 Rendering PDF from {output_html_file}...")
        HTML(output_html_file).write_pdf(output_pdf_file)
        print(f"✅ PDF report created: {output_pdf_file}")
        return True
    except ImportError:
        print("⚠️ WeasyPrint is not installed or import failed. Skipping PDF generation.")
        print("hint: make sure pango/cairo system libraries are installed on macOS (e.g. brew install pango cairo)")
        return False
    except Exception as e:
        print(f"❌ Failed to build PDF: {e}")
        return False
