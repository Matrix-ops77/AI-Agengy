import os
from faker import Faker
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import random

def generate_invoice(file_path):
    """Generates a single fake PDF invoice."""
    fake = Faker()
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Invoice Header
    c.drawString(100, 750, "INVOICE")
    c.drawString(400, 750, f"Invoice #: {random.randint(1000, 9999)}")
    c.drawString(400, 735, f"Date: {fake.date_this_year().strftime('%Y-%m-%d')}")
    
    # Vendor and Client Info
    c.drawString(100, 700, "From:")
    c.drawString(100, 685, fake.company())
    c.drawString(100, 670, fake.address().replace('\n', ', '))
    
    c.drawString(400, 700, "To:")
    c.drawString(400, 685, fake.company())
    c.drawString(400, 670, fake.address().replace('\n', ', '))
    
    # Invoice Body
    c.drawString(100, 600, "Description")
    c.drawString(400, 600, "Amount")
    
    total_amount = 0
    for i in range(random.randint(1, 5)):
        description = fake.bs()
        amount = round(random.uniform(50, 500), 2)
        c.drawString(100, 580 - (i * 20), description)
        c.drawString(400, 580 - (i * 20), f"${amount}")
        total_amount += amount
        
    # Total
    c.drawString(350, 500, "Total:")
    c.drawString(400, 500, f"${total_amount:.2f}")
    
    c.save()

def main(num_invoices, output_dir):
    """Generates a specified number of fake invoices."""
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
for i in range(num_invoices):
        file_path = os.path.join(output_dir, f"invoice_{i+1}.pdf")
        generate_invoice(file_path)
        print(f"Generated {file_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate fake PDF invoices.")
    parser.add_argument("num_invoices", type=int, help="The number of invoices to generate.")
    parser.add_argument("--output-dir", default="test_invoices", help="The directory to save the generated invoices.")
    args = parser.parse_args()
    
    main(args.num_invoices, args.output_dir)