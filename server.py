import os
import sqlite3
import json
import time
from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime



app = Flask(__name__)

# --- 1. ตั้งค่า Config และโฟลเดอร์รูป ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# ถ้าไม่มีโฟลเดอร์ uploads ให้สร้างใหม่
if not os.path.exists(UPLOAD_FOLDER): 
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DB_NAME = "positive.db"

# --- 2. ฟังก์ชันจัดการ Database ---

# แปลงผลลัพธ์จาก DB ให้เป็น Dictionary (Json อ่านได้)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # 1. ตาราง Users (คงโครงสร้างที่มีเงินเดือน/วุฒิ ไว้)
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE,
                     password TEXT,
                     display_name TEXT,
                     role TEXT,
                     education TEXT,
                     salary REAL,
                     profile_image TEXT DEFAULT 'default_avatar.png',
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                     )''')
        
        # 🔥 กู้คืนข้อมูลพนักงานทั้งหมดกลับมา (สำหรับโชว์) 🔥
        c.execute("SELECT count(*) FROM users")
        if c.fetchone()[0] == 0:
            # ข้อมูลชุดเดิมของคุณ (ผมเอากลับมาใส่ให้ครบทุกคน)
            employees_data = [
                # กลุ่มแอดมิน (Admin)
                ("10001", "1234", "นิญา จิรวาณิชย์",      "admin", "ปวส",   15000, "default_avatar.png"),
                ("10002", "1234", "ฟาริท ศรีสุข",          "admin", "ปวช",   14000, "default_avatar.png"),
                ("10003", "1234", "ฐิติภา พัฒนปรีชา",      "admin", "ปวช",   14000, "default_avatar.png"),
                ("10004", "1234", "นีรสร มงคงมั่น",        "admin", "ปวช",   14000, "default_avatar.png"),
                
                # กลุ่มตำแหน่งพิเศษ (HR, Manager, Assistant)
                ("10005", "4321", "ปวิมล จันทรสมบูรณ์",    "hr",    "ปวช",   15000, "default_avatar.png"),
                ("10006", "9999", "นิติธร พัฒนปรีชา",      "manager", "ป ตรี", 20000, "default_avatar.png"),
                ("10007", "8888", "นวพร จันทรสมบูรณ์",     "assistant", "ปวส", 17000, "default_avatar.png"),

                # กลุ่มพนักงานทั่วไป (Staff)
                ("10008", "0000", "ตฤณภัทร จันทรเพ็ญ",     "staff", "ปวส",   15000, "default_avatar.png"),
                ("10009", "0000", "เมริสา วัฒนโกศล",       "staff", "ปวส",   15000, "default_avatar.png"),
                ("10010", "0000", "โชคชัย รัชนวีระ",       "staff", "ปวส",   15000, "default_avatar.png"),
                ("10011", "0000", "ชนาธินาถ แสงดารา",      "staff", "ปวช",   15000, "default_avatar.png"),
                ("10012", "0000", "ดนิน จันทรทรัพย์",      "staff", "ปวส",   15000, "default_avatar.png"),
                ("10013", "0000", "สุริยนต์ ธารางาม",      "staff", "ปวส",   15000, "default_avatar.png"),
                ("10014", "0000", "พรพักตร์ พงศ์ธนา",      "staff", "ปวส",   15000, "default_avatar.png"),
                ("10015", "0000", "กิตติธร ยุทธนาวิวัฒน์",   "staff", "ปวช",   15000, "default_avatar.png"),
                ("10016", "0000", "มงคล จันทรหอม",        "staff", "ปวช",   15000, "default_avatar.png"),
            
                # Admin สำรอง
                ("admin", "1234", "System Admin", "admin", "System", 0, "default_avatar.png")
            ]
            
            # บันทึกลงฐานข้อมูลรวดเดียว
            c.executemany("INSERT INTO users (username, password, display_name, role, education, salary, profile_image) VALUES (?, ?, ?, ?, ?, ?, ?)", employees_data)

        # 🔥 1. สร้างตารางหมวดหมู่สินค้า (Categories)
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
                     code TEXT PRIMARY KEY,
                     name TEXT,
                     icon TEXT,
                     shipping_size TEXT
                     )''')
        
        c.execute("SELECT count(*) FROM categories")
        if c.fetchone()[0] == 0:
            initial_cats = []
            c.executemany("INSERT INTO categories (code, name, icon) VALUES (?, ?, ?)", initial_cats)

        conn.commit()
        print(">>> Database initialized with Icons.")

        # 2. ตาราง Products
        c.execute('''CREATE TABLE IF NOT EXISTS products (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     code TEXT, name TEXT, price REAL, type TEXT, desc TEXT, 
                     image TEXT, stock INTEGER DEFAULT 1, warranty TEXT, brand TEXT, video_url TEXT
                     )''')
        
        # 3. ตาราง Orders
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
                     order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     customer TEXT, address TEXT, total REAL, status TEXT, 
                     slip_image TEXT, timestamp TEXT, cashier_id INTEGER
                     )''')

        # 4. ตาราง Order Items
        c.execute('''CREATE TABLE IF NOT EXISTS order_items (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     order_id INTEGER, product_id INTEGER, product_name TEXT, 
                     price REAL, qty INTEGER
                     )''')
        
        # 5. ตาราง Settings (แบบ Key-Value เพื่อความยืดหยุ่น)
        # 🔥 ส่วนนี้คือของใหม่ที่ต้องมี เพื่อแก้ Error เรื่อง Zipcode/Logo 🔥
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                        )''')
        
        # กำหนดค่าเริ่มต้น
        defaults = {
            "banner_top": "default_top.jpg",
            "banner_promo": "default_promo.jpg",
            "shop_logo": "shop_logo_default.png",
            "shop_zipcode": "10000",
            "app_bgcolor": "#FFFAF0",
            "app_theme_color": "blue"

        }
        for k, v in defaults.items():
            c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

        conn.commit()
    print(">>> Database initialized successfully (With Demo Data).")
init_db()

#--ดึงรายการสินค้าทั้งหมด--
@app.route('/api/products')
def get_products():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = dict_factory
            c = conn.cursor()
            # ดึงสินค้าที่ stock > 0 
            c.execute("SELECT * FROM products WHERE stock > 0 ORDER BY id DESC")
            return jsonify(c.fetchall())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
  
# ใน server.py

# 3.2 ดึงประวัติการสั่งซื้อของฉัน 
@app.route('/api/my_orders', methods=['POST'])
def get_my_orders():
    user_name = request.json.get('name')
    if not user_name: return jsonify([])

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = dict_factory
            c = conn.cursor()
            
            # 🔥 แก้ SQL: เพิ่ม comma หลัง p.name และดึงราคามาด้วย
            c.execute("""
                SELECT  p.name, 
                        p.image, 
                        p.warranty, 
                        oi.product_name, 
                        oi.price,       -- เพิ่มราคา
                        oi.qty,         -- เพิ่มจำนวน
                        oi.id AS item_id, 
                        p.id AS product_id,
                        o.timestamp AS purchase_date,
                        o.status
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.customer = ? 
                ORDER BY o.order_id DESC
            """, (user_name,))
            
            return jsonify(c.fetchall())
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return jsonify({"error": str(e)}), 500
    


# 3.3 เพิ่มสินค้าใหม่ (Admin)
@app.route('/api/products/add', methods=['POST'])
def add_product():
    try:
        code = request.form.get('code', '')
        name = request.form.get('name')
        price = float(request.form.get('price', 0))
        p_type = request.form.get('type')
        desc = request.form.get('desc')
        stock = int(request.form.get('stock', 1))
        warranty = request.form.get('warranty', '-') 
        brand = request.form.get('brand', '')
        video_url = request.form.get('video_url', '')
        unit = request.form.get('unit', 'ชิ้น')
        # จัดการรูปภาพ
        image_name = ""
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                image_name = f"prod_{int(time.time())}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()    
            c.execute('''INSERT INTO products (code, name, price, type, desc, image, stock, warranty, brand, video_url, unit)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (code, name, price, p_type, desc, image_name, stock, warranty, brand, video_url, unit)) 
            conn.commit()
        return jsonify({"message": "Saved successfully"})
    except Exception as e:
        print(f"Error adding product: {e}")
        return jsonify({"error": str(e)}), 500

# 3.4 สั่งซื้อสินค้า (Checkout)
@app.route('/api/checkout', methods=['POST'])
def checkout():
    try:
        # 1. รับค่า user เพิ่มเข้ามา (สำคัญมาก!)
        user_name = request.form.get('user') 
        
        name = request.form.get('name')
        address = request.form.get('address')
        total = float(request.form.get('total', 0))
        
        # จัดการรูปสลิป
        slip_name = "no_slip.jpg"
        if 'slip' in request.files:
            file = request.files['slip']
            if file.filename != '':
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                slip_name = f"slip_{int(time.time())}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], slip_name))

        # บันทึกลง Database
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            
            # A. สร้าง Order ใหม่
            c.execute('''INSERT INTO orders (customer, address, total, status, slip_image, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                     (name, address, total, "รอตรวจสอบ", slip_name, datetime.now().strftime("%d/%m/%Y %H:%M")))
            new_order_id = c.lastrowid

            # B. บันทึกรายการสินค้า (Loop จากตะกร้าของคนนั้น)
            global CART_DATA
            
            # 🔥 แก้ตรงนี้: ดึงตะกร้าของ user คนนั้นออกมา (ไม่ใช่ดึงทั้งหมด)
            my_cart = CART_DATA.get(user_name, [])
            
            for item in my_cart: # ✅ วนลูปสินค้าของ user คนนี้
                # 1. บันทึกลง order_items
                c.execute('''INSERT INTO order_items (product_name, price, qty, order_id, product_id)
                             VALUES (?, ?, ?, ?, ?)''', 
                             (item['name'], item['price'], item['qty'], new_order_id, item['id']))
                
                # 2. ตัดสต็อก (เพิ่มเงื่อนไขความปลอดภัย)
                c.execute("UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?", 
                          (item['qty'], item['id'], item['qty']))
                
                # 3. เช็คว่าตัดสำเร็จไหม (ถ้าของหมด rowcount จะเป็น 0)
                if c.rowcount == 0:
                     raise Exception(f"สินค้า '{item['name']}' หมดพอดี หรือมีจำนวนไม่พอ!")
            
            conn.commit()
        
        # สั่งซื้อเสร็จ ล้างตะกร้าของคนนั้น
        if user_name in CART_DATA:
            CART_DATA[user_name] = [] 
            
        return jsonify({"message": "Order Saved"})
            
    except Exception as e:
        print(f"Checkout Error: {e}")
        return jsonify({"error": str(e)}), 500

# 3.5 ดูรายการออเดอร์ (Admin)
@app.route('/api/orders')
def get_orders():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * FROM orders ORDER BY order_id DESC")
        return jsonify(c.fetchall())

# 3.6 อัปเดตสถานะออเดอร์
@app.route('/api/orders/update', methods=['POST'])
def update_order():
    oid = request.json.get('order_id')
    status = request.json.get('status')

    admin_name = request.json.get('admin_name', '-')
    
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("UPDATE orders SET status = ?, handled_by = ? WHERE order_id = ?", 
                  (status, admin_name, oid))
        
        # ถ้าสถานะเป็น "จัดส่งแล้ว" เราอาจจะไปอัปเดต owner ของสัตว์เลี้ยงให้เป็นชื่อลูกค้าได้ตรงนี้
        # (Logic นี้ใส่เพิ่มทีหลังได้ครับ)
        
        conn.commit()
    return jsonify({"message": "Updated"})

# --- 4. ระบบตะกร้า (ใช้ Memory ชั่วคราว เพื่อให้แอปทำงานลื่นไหล) ---
CART_DATA = {}


# 4.1 ดูตะกร้า (ต้องเปลี่ยนเป็น POST เพื่อรับชื่อคนดู)
@app.route('/api/cart', methods=['POST']) 
def get_cart():
    # รับชื่อ User (ถ้าไม่มีให้เป็น guest)
    user = request.json.get('user', 'guest') 
    
    # ดึงตะกร้าของคนนั้นออกมา (ถ้าไม่มีให้คืนค่าว่าง [])
    return jsonify(CART_DATA.get(user, []))

# 4.2 เพิ่มลงตะกร้า
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    user = request.json.get('user', 'guest') # 🔥 รับชื่อคนซื้อ
    pid = request.json.get('id')
    
    # ถ้าคนนี้ยังไม่มีตะกร้า ให้สร้างใหม่
    if user not in CART_DATA: CART_DATA[user] = []
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE id = ?", (pid,))
        product = c.fetchone()
        
        if product:
            found = False
            # วนลูปเช็คในตะกร้าของ user คนนั้น
            for item in CART_DATA[user]:
                if item['id'] == pid:
                    item['qty'] += 1
                    found = True
                    break
            
            if not found:
                CART_DATA[user].append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'qty': 1,
                    'type': product['type'],
                    'image': product['image'],
                    'icon': "inventory_2"
                })
                
    return jsonify({"message": "Added"})

# 4.3 ลบจากตะกร้า
@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    user = request.json.get('user', 'guest') # 🔥 รับชื่อ
    pid = request.json.get('id')
    
    if user in CART_DATA:
        # กรองเอาเฉพาะอันที่ไม่ใช่ pid ที่ส่งมา
        CART_DATA[user] = [item for item in CART_DATA[user] if item['id'] != pid]
        
    return jsonify({"message": "Removed"})

# 4.4 ล้างตะกร้า
@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    # กันแอปพังถ้าไม่ได้ส่ง JSON มา โดยใช้ get_json(silent=True)
    data = request.get_json(silent=True) or {}
    user = data.get('user', 'guest')
    
    if user in CART_DATA:
        CART_DATA[user] = [] 
        
    return jsonify({"message": "Cleared"})

# --- 5. Serve รูปภาพ ---
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/print_order/<int:order_id>')
def print_order_page(order_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. ดึงข้อมูลออเดอร์
    c.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order = c.fetchone()
    if not order:
        return "ไม่พบออเดอร์นี้", 404
    
    # 2. ดึงรายการสินค้า
    c.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    items = c.fetchall()
    conn.close()

    # --- ส่วนคำนวณเงินย้อนกลับ ---
    grand_total = float(order[3])
    
    items_total = 0
    items_html = ""
    
    if items:
        for item in items:
            # 🔥🔥🔥 แก้ไขตรงนี้ครับ (เปลี่ยนตัวเลข Index ให้ถูก) 🔥🔥🔥
            # โครงสร้างตาราง: 0=id, 1=order_id, 2=product_id, 3=name, 4=price, 5=qty
            
            p_name = item[3]        # ชื่อสินค้า (แก้จาก item[1])
            price = float(item[4])  # ราคา (แก้จาก item[2])
            qty = int(item[5])      # จำนวน (แก้จาก item[3])
            
            line_total = price * qty 
            items_total += line_total
            
            items_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;">{p_name}</td>
                <td style="padding: 10px; text-align: center;">{qty}</td>
                <td style="padding: 10px; text-align: right;">{line_total:,.2f} ฿</td>
            </tr>
            """
    else:
        items_html = '<tr><td colspan="3" style="text-align:center; padding:20px;">ไม่มีรายการสินค้า</td></tr>'

    # ... (ส่วนคำนวณ VAT และ HTML ด้านล่าง ใช้ของเดิมได้เลยครับ ไม่ต้องแก้) ...
    # สูตร: GrandTotal = (Items + Shipping) * 1.07
    total_before_vat = grand_total / 1.07
    vat_amount = grand_total - total_before_vat
    shipping_cost = total_before_vat - items_total
    
    if shipping_cost < 0: shipping_cost = 0

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ใบเสร็จ Order #{order[0]}</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #eee; }}
            .receipt {{ max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ text-align: left; background: #f0f0f0; padding: 10px; }}
            .summary-row td {{ padding: 5px 10px; text-align: right; }}
            .grand-total {{ color: #007bff; font-size: 18px; font-weight: bold; border-top: 2px solid #ddd; padding-top: 10px !important; }}
        </style>
    </head>
    <body>
        <div class="receipt">
            <h2 style="text-align: center;">📄 ใบเสร็จรับเงิน</h2>
            <hr>
            <div class="header">
                <div>
                    <b>Order ID:</b> #{order[0]}<br>
                    <b>วันที่:</b> {order[6]} <br> 
                    <b>ลูกค้า:</b> {order[1]}
                </div>
                <div style="text-align: right;">
                    <b>สถานะ:</b> {order[4]} 
                </div>
            </div>

            <div style="background: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <b>📍 ที่อยู่จัดส่ง:</b><br>
                {order[2]} 
            </div>

            <table>
                <thead>
                    <tr><th>สินค้า</th> <th style="text-align:center;">จำนวน</th> <th style="text-align:right;">ราคา</th></tr>
                </thead>
                <tbody>
                    {items_html}
                    
                    <tr class="summary-row"><td colspan="3" style="height: 10px;"></td></tr>
                    
                    <tr class="summary-row">
                        <td colspan="2">ราคาสินค้า (Subtotal):</td>
                        <td>{items_total:,.2f} ฿</td>
                    </tr>
                    <tr class="summary-row">
                        <td colspan="2" style="color:red;">ค่าจัดส่ง (Shipping):</td>
                        <td style="color:red;">{shipping_cost:,.2f} ฿</td>
                    </tr>
                    <tr class="summary-row">
                        <td colspan="2" style="color:orange;">VAT (7%):</td>
                        <td style="color:orange;">{vat_amount:,.2f} ฿</td>
                    </tr>
                    <tr class="summary-row">
                        <td colspan="2" class="grand-total">ยอดสุทธิ (Grand Total):</td>
                        <td class="grand-total">{grand_total:,.2f} ฿</td>
                    </tr>
                </tbody>
            </table>

            <button onclick="window.print()" style="width:100%; padding:15px; margin-top:20px; background:#007bff; color:white; border:none; cursor:pointer;">🖨️ พิมพ์ใบเสร็จ</button>
        </div>
    </body>
    </html>
    """
    return html_content
# --- Main Entry Point ---

# --- เพิ่ม API สำหรับดึงรายชื่อสมาชิก (จากประวัติการสั่งซื้อ) ---
@app.route('/api/members')
def get_members():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        # 🔥 จุดที่แก้: เพิ่ม "WHERE status != 'ยกเลิก'" เพื่อไม่เอาออเดอร์ที่ยกเลิกมาคำนวณเงิน
        c.execute('''
            SELECT customer as name, 
                   MAX(address) as address, 
                   COUNT(order_id) as order_count, 
                   SUM(total) as total_spent,
                   MAX(timestamp) as last_seen
            FROM orders 
            WHERE status != 'ยกเลิก'  -- <--- เพิ่มบรรทัดนี้ครับ
            GROUP BY customer
            ORDER BY total_spent DESC
        ''')
        return jsonify(c.fetchall())
    
# --- API สำหรับแก้ไขสินค้า (Edit Product) [ฉบับอัปเกรด: เปลี่ยนรูปได้] ---
@app.route('/api/products/update', methods=['POST'])
def update_product():
    try:
        # 1. เปลี่ยนการรับค่าจาก JSON เป็น Form Data
        p_id = request.form.get('id')
        name = request.form.get('name')
        code = request.form.get('code')
        # แปลงเป็นตัวเลข (กัน Error)
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        unit = request.form.get('unit', 'ชิ้น')

        # 2. จัดการรูปภาพ (ถ้ามีการส่งรูปใหม่มา)
        new_image_name = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # ตั้งชื่อไฟล์ใหม่ตามเวลา (กันชื่อซ้ำ)
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                new_image_name = f"prod_edit_{int(time.time())}.{ext}"
                # บันทึกรูป
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_image_name))

        # 3. อัปเดต Database
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            
            # กรณีที่ 1: มีการเปลี่ยนรูปด้วย
            if new_image_name:
                c.execute('''UPDATE products SET 
                             name=?, price=?, stock=?, code=?, image=?, unit=?
                             WHERE id=?''',
                          (name, price, stock, code, new_image_name, unit, p_id))
            
            # กรณีที่ 2: ไม่เปลี่ยนรูป (ใช้รูปเดิม)
            else:
                c.execute('''UPDATE products SET 
                             name=?, price=?, stock=?, code=?, unit=?
                             WHERE id=?''',
                          (name, price, stock, code, unit, p_id))
        
        return jsonify({'status': 'success', 'message': 'แก้ไขสินค้าเรียบร้อย'})

    except Exception as e:
        print(f"Update Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
# --- API สำหรับลบสินค้า (Delete Product) ---
@app.route('/api/products/delete', methods=['POST'])
def delete_product():
    try:
        data = request.json
        p_id = data.get('id') # รับค่า ID สินค้าที่จะลบ

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            # สั่งลบแถวที่มี id ตรงกัน
            c.execute("DELETE FROM products WHERE id=?", (p_id,))
            conn.commit()

        return jsonify({'status': 'success', 'message': 'ลบสินค้าเรียบร้อย'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

def check_and_update_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # --- เช็คและเพิ่มช่อง product_id (สำคัญมาก! ใช้เชื่อมโยงสินค้ากับออเดอร์) ---
        try:
            # ลองดึงข้อมูลดูว่ามีช่องนี้หรือยัง
            c.execute("SELECT product_id FROM order_items LIMIT 1")
        except:
            # ถ้า Error แปลว่ายังไม่มี -> สั่งเพิ่มคอลัมน์ใหม่
            print("กำลังเพิ่มช่อง 'product_id' ลงในฐานข้อมูล ...")
            try:
                c.execute("ALTER TABLE order_items ADD COLUMN product_id INTEGER")
                conn.commit()
                print("✅ เพิ่มช่อง product_id สำเร็จ")
            except Exception as e: 
                print(f"❌ Add product_id error: {e}")

        try:
            c.execute("SELECT unit FROM products LIMIT 1")
        except:
            print("กำลังเพิ่มช่อง 'unit' (หน่วยนับ) ...")
            c.execute("ALTER TABLE products ADD COLUMN unit TEXT DEFAULT 'ชิ้น'")
            conn.commit()
            print("✅ เพิ่มช่อง unit สำเร็จ")    

        try:
            c.execute("SELECT handled_by FROM orders LIMIT 1")
        except:
            print("กำลังเพิ่มช่อง 'handled_by' (ผู้รับผิดชอบ) ...")
            c.execute("ALTER TABLE orders ADD COLUMN handled_by TEXT")
            conn.commit()
            print("✅ เพิ่มช่อง handled_by สำเร็จ")

        conn.close()
    except Exception as e:
        print(f"DB Check Error: {e}")

# เรียกใช้งานฟังก์ชันตรวจสอบทันทีที่เริ่ม Server
check_and_update_db()
# --- API: จัดการพนักงาน (HR) โดยใช้ตาราง users ---
@app.route('/api/employees', methods=['GET'])
def get_employees():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        return jsonify(c.fetchall())
    
if not os.path.exists('assets'):
    os.makedirs('assets')

@app.route('/api/employees/add', methods=['POST'])
def add_employee():
    try:
        # 1. รับข้อมูลตัวหนังสือ (ใช้ request.form แทน request.json)
        username = request.form.get('user')
        password = request.form.get('pass')
        display_name = request.form.get('name')
        role = request.form.get('role')

        # (ค่า Default สำหรับพวกวุฒิและเงินเดือน ถ้าหน้าบ้านยังไม่ได้ทำช่องกรอก)
        education = request.form.get('education', 'ไม่ระบุ') 
        salary = request.form.get('salary', 0)

        # 2. รับไฟล์รูปภาพ (ถ้ามี)
        image_filename = 'default_avatar.png' # ค่าเริ่มต้น

        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # ตั้งชื่อไฟล์ใหม่กันซ้ำ (เช่น 10001_photo.jpg)
                ext = file.filename.split('.')[-1]
                new_filename = f"{username}_profile.{ext}"

                # บันทึกลงโฟลเดอร์ assets
                file.save(os.path.join('assets', new_filename))
                image_filename = new_filename

        # 3. บันทึกลงฐานข้อมูล
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (username, password, display_name, role, education, salary, profile_image) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, password, display_name, role, education, salary, image_filename))
            conn.commit()

        return jsonify({'message': 'Success', 'image': image_filename})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/delete', methods=['POST'])
def delete_employee():
    eid = request.json.get('id')
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        # ✅ แก้ไข: ลบจากตาราง users
        c.execute("DELETE FROM users WHERE id = ?", (eid,))
        conn.commit()
    return jsonify({'message': 'Deleted'})

@app.route('/api/login', methods=['POST'])
def login_check():
    data = request.json
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        # ✅ แก้ไข: เช็ค Login จากตาราง users
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (data['user'], data['pass']))
        user = c.fetchone()
        if user:
            return jsonify({'status': 'success', 'user': user})
        else:
            return jsonify({'status': 'fail', 'message': 'ชื่อหรือรหัสผ่านผิด'})

# --- API: ข้อมูลกราฟ (Sales Analytics) ---
# ส่วนนี้เหมือนเดิม เพราะดึงจากตาราง orders ไม่ได้ยุ่งกับ users
@app.route('/api/stats/<mode>') 
def get_stats(mode):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT timestamp, total FROM orders WHERE status != 'ยกเลิก'") 
        orders = c.fetchall()

    labels = []
    values = []
    from datetime import datetime
    data_map = {} 
    now = datetime.now()

    for o in orders:
        try:
            dt = datetime.strptime(o['timestamp'], "%d/%m/%Y %H:%M")
            key = ""
            if mode == 'daily':
                if (now - dt).days <= 7:
                    key = dt.strftime("%d/%m")
            elif mode == 'weekly':
                if (now - dt).days <= 30:
                    week_num = dt.strftime("%W")
                    key = f"W{week_num}"
            elif mode == 'monthly':
                if dt.year == now.year:
                    key = dt.strftime("%b")
            
            if key:
                if key in data_map: data_map[key] += o['total']
                else: data_map[key] = o['total']
        except: pass

    if mode == 'monthly':
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for m in months:
            if m in data_map:
                labels.append(m)
                values.append(data_map[m])
    else:
        for k in sorted(data_map.keys()):
            labels.append(k)
            values.append(data_map[k])

    return jsonify({'labels': labels, 'values': values})

# ✅ เพิ่มฟังก์ชันนี้ เพื่อให้ App ดึงรูปจากโฟลเดอร์ assets ไปโชว์ได้
@app.route('/assets/<path:filename>')
def serve_image(filename):
    return send_from_directory('assets', filename)

# และอย่าลืมแก้ API GET ให้ส่ง zipcode กลับมาด้วย
@app.route('/api/settings', methods=['GET'])
def get_settings():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT key, value FROM settings")
        data = {row[0]: row[1] for row in c.fetchall()} # แปลงเป็น Dict
        return jsonify(data)

@app.route('/api/settings/update', methods=['POST'])
def update_settings():
    try:
        updates = {}
        
        # 1. รับค่า Text (Zipcode)
        if request.form.get('zipcode'):
            updates['shop_zipcode'] = request.form.get('zipcode')

        if request.form.get('bgcolor'):
            updates['app_bgcolor'] = request.form.get('bgcolor')

        if request.form.get('theme_color'):
            updates['app_theme_color'] = request.form.get('theme_color')

        # 2. รับไฟล์ภาพ
        file_map = {'banner_top': 'top', 'banner_promo': 'promo', 'shop_logo': 'logo'}
        
        for key, prefix in file_map.items():
            if key in request.files:
                file = request.files[key]
                if file.filename != '':
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    new_name = f"{prefix}_{int(time.time())}.{ext}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
                    updates[key] = new_name

        # 3. บันทึกลง Database
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            for k, v in updates.items():
                c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
            conn.commit()
            
        return jsonify({"message": "Settings updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- เพิ่ม API สำหรับดึงและเพิ่มหมวดหมู่
@app.route('/api/categories', methods=['GET'])
def get_categories():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY code ASC")
        return jsonify(c.fetchall())

@app.route('/api/categories/add', methods=['POST'])
def add_category():
    try:
        data = request.json
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            # 🔥 บันทึก shipping_size ลงไปด้วย
            c.execute("INSERT INTO categories (code, name, icon, shipping_size) VALUES (?, ?, ?, ?)",
                      (
                          data['code'], 
                          data['name'], 
                          data.get('icon', 'category'),
                          data.get('shipping_size', 'size_s') # ถ้าไม่ส่งมา ให้ถือว่าเป็นไซส์ S (ฟรี)
                      ))
            conn.commit()
        return jsonify({'message': 'Success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/categories/delete', methods=['POST'])
def delete_category():
    try:
        data = request.json
        code = data.get('code') # รับรหัสหมวดที่ต้องการลบ
        
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            # ลบออกจากตาราง categories
            c.execute("DELETE FROM categories WHERE code = ?", (code,))
            conn.commit()
            
        return jsonify({'message': 'Deleted Success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/orders/cancel', methods=['POST'])
def cancel_order():
    try:
        oid = request.json.get('order_id')
        admin_name = request.json.get('admin_name', '-') # <--- 1. รับชื่อแอดมินที่ส่งมา (ถ้าไม่มีให้เป็น -)

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            # ... (ส่วน code คืนสต็อกสินค้า เหมือนเดิม) ...
            c.execute("SELECT product_id, qty FROM order_items WHERE order_id = ?", (oid,))
            items = c.fetchall()
            for item in items:
                pid, qty = item
                c.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, pid))

            # 2. แก้ไขคำสั่ง SQL ให้อัปเดต handled_by ด้วย
            c.execute("UPDATE orders SET status = 'ยกเลิก', handled_by = ? WHERE order_id = ?", (admin_name, oid))

            conn.commit()
        return jsonify({"message": "Order Cancelled and Stock Restored"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # host='0.0.0.0' เพื่อให้มือถือในวง LAN เดียวกันเชื่อมต่อได้
    app.run(host='0.0.0.0', port=5000, debug=True)