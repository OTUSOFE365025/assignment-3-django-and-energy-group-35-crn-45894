############################################################################
## Django ORM Standalone Python Template
############################################################################
""" Here we'll import the parts of Django we need. It's recommended to leave
these settings as is, and skip to START OF APPLICATION section below """
import csv
from decimal import Decimal
from pathlib import Path
# Turn off bytecode generation
import sys
sys.dont_write_bytecode = True

# Import settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# setup django environment
import django
django.setup()

# Import your models for use in your script
from db.models import *

############################################################################
## START OF APPLICATION
############################################################################
""" Replace the code below with your own """

# Seed a few users in the database
# User.objects.create(name='Dan')
# User.objects.create(name='Robert')

# for u in User.objects.all():
#     print(f'ID: {u.id} \tUsername: {u.name}')

def data_from_csv(csv_path: str):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"Seed CSV not found at {csv_path}")
        return

    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            upc = row['upc'].strip()
            name = row['name'].strip()
            price_raw = row['price'].strip()
            
            # sanitize price
            try:
                price = Decimal(price_raw)
            except Exception:
                print(f"Skipping {upc} due to invalid price: {price_raw}")
                continue

            products.objects.update_or_create(
                upc=upc,
                defaults={'name': name, 'price': price}
            )
            count += 1
        print(f"Seeded/updated {count} products from {csv_path}")


def run_tk_ui():
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception as e:
        print("Tkinter not available:", e)
        sys.exit(1)

    root = tk.Tk()
    root.title("Cash Register - Scanner")

    frm = ttk.Frame(root, padding=12)
    frm.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frm, text="Scan UPC:").grid(column=0, row=0, sticky="w")
    upc_entry = ttk.Entry(frm, width=30)
    upc_entry.grid(column=1, row=0, sticky="w")
    result_var = tk.StringVar(value="Scan a UPC and press Scan \n add valid UPC from products.csv")

    cart = [] 
    total = 0.0  
    def do_scan(event=None):
        nonlocal total  # allow updating the outer variable if using nested function
        upc = upc_entry.get().strip()
        if not upc:
            result_var.set("Please enter a UPC.")
            return
        p = products.objects.filter(upc=upc).first()
        if p:
            cart.append((p.name, p.price))
            total += float(p.price)
            lines = [f"{name} - ${price}" for name, price in cart]
            lines.append(f"\nTotal: ${total:.2f}")
            result_var.set("\n".join(lines))
        else:
            result_var.set("Product not found.")

    scan_btn = ttk.Button(frm, text="Scan", command=do_scan)
    scan_btn.grid(column=2, row=0, padx=(6,0))

    ttk.Label(frm, textvariable=result_var, wraplength=400).grid(column=0, row=1, columnspan=3, pady=(10,0))

    # bind Enter to scan
    root.bind('<Return>', do_scan)

    root.mainloop()

# ---------- entry ----------
if __name__ == "__main__":
    # optional: take CSV path from argv
    csv_path =sys.argv[1] if len(sys.argv) > 1 else "products.csv"
    data_from_csv(csv_path)
    run_tk_ui()