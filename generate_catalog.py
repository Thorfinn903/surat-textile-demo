import sqlite3
import csv
import os

# -----------------------------
# CONFIGURATION
# -----------------------------
DB_PATH = "instance/textile.db" 
CSV_PATH = r"C:\Users\shubham\OneDrive\Desktop\catelog.csv" # Absolute path to your CSV

print(f"🚀 Starting Import from {CSV_PATH}...")

# Connect to Database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Clear existing data (Optional: Remove if you want to append)
print("⚠️ Clearing existing products...")
cursor.execute("DELETE FROM product;")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='product';")
conn.commit()

# 2. Read CSV and Insert
try:
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        design_counter = 1001 # Start Design No from 1001
        
        for row in reader:
            # Extract fields from CSV
            name = row.get('name', '').strip()
            category = row.get('category', '').strip()
            material = row.get('material_type', '').strip()
            work = row.get('work_type', '').strip()
            image = row.get('image', '').strip()
            
            # Auto-generate or Default values for missing DB columns
            design_no = str(design_counter)
            color = "Multi" # Default color since CSV doesn't have it
            stock_status = "In Stock"
            views = 0
            clicks = 0
            
            # Insert into DB
            cursor.execute("""
                INSERT INTO product (
                    name, design_no, category, material_type, work_type, 
                    color, image_file, stock_status, views, whatsapp_clicks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, design_no, category, material, work, 
                color, image, stock_status, views, clicks
            ))
            
            print(f"✅ Added: {design_no} - {name}")
            design_counter += 1

    conn.commit()
    print(f"\n🎉 Successfully imported {design_counter - 1001} products!")

except FileNotFoundError:
    print(f"❌ Error: CSV file not found at {CSV_PATH}")
except Exception as e:
    print(f"❌ Error: {e}")

finally:
    conn.close()
