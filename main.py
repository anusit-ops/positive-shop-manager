import flet as ft
import requests
import time
import threading
import math



# --- Config & State ---
API_URL = "https://oneth01.pythonanywhere.com"
proxies = {"http": None, "https": None}

# 🔥 รายการสีพื้นหลังยอดนิยม (สีพาสเทล อ่านง่าย)
BG_COLORS = [
    {"name": "Cream (ค่าเริ่มต้น)", "code": "#FFFAF0"},
    {"name": "White (ขาวสะอาด)", "code": "#FFFFFF"},
    {"name": "Ice Blue (ฟ้าสดใส)", "code": "#BBDEFB"},   # ฟ้าที่ดูเป็นฟ้าจริงๆ
    {"name": "Mint (เขียวชาเขียว)", "code": "#C8E6C9"},  # เขียวที่แยกออกจากขาวได้ชัดเจน
    {"name": "Lavender (ม่วงลาเวนเดอร์)", "code": "#E1BEE7"}, # ม่วงอ่อนที่ดูหวานๆ
    {"name": "Soft Pink (ชมพูนมเย็น)", "code": "#F8BBD0"}, # ชมพูที่ดูออกว่าเป็นชมพู
    {"name": "Classic Grey (เทาโมเดิร์น)", "code": "#E0E0E0"}, # เทาที่ดูเท่ๆ ไม่ใช่แค่จอมัว
    {"name": "Warm Peach (ส้มพีช)", "code": "#FFE0B2"},   # ส้มอ่อนๆ ดูอบอุ่น
    {"name": "Lemon (เหลืองมะนาว)", "code": "#FFF59D"},   # เหลืองนวล สว่างตา
    {"name": "Sand (น้ำตาลทราย)", "code": "#D7CCC8"},
]

# 🔥 รายการสีธีม (สำหรับบาร์ด้านบน)
THEME_COLORS = [
    # --- กลุ่มสีหลัก (ปรับให้ดู Modern ขึ้น) ---
    {"name": "Ocean Blue (ฟ้าทะเล)", "code": "#1976D2", "text": "white"},   # ฟ้าที่ดูเป็นทางการ ไม่สดจนแสบตา
    {"name": "Teal Green (เขียวอมฟ้า)", "code": "#009688", "text": "white"}, # สีฮิต สบายตา
    {"name": "Slate (เทาอมน้ำเงิน)", "code": "#607D8B", "text": "white"},    # สีสุภาพ ดูแพงมาก
    {"name": "Midnight (น้ำเงินเข้ม)", "code": "#283593", "text": "white"},   # สำหรับคนชอบเข้มๆ แต่อมม่วงนิดๆ
    
    # --- กลุ่มสีพาสเทล/สดใส (แนะนำให้ใช้ตัวหนังสือสีดำ) ---
    {"name": "Sky (ฟ้าท้องฟ้า)", "code": "#90CAF9", "text": "black"},       # ฟ้าอ่อน สดใส
    {"name": "Mint (เขียวมินท์)", "code": "#80CBC4", "text": "black"},       # เขียวน่ารัก
    {"name": "Peach (ส้มพีช)", "code": "#FFCC80", "text": "black"},          # ส้มอ่อนๆ
    {"name": "Rose (ชมพูกุหลาบ)", "code": "#F48FB1", "text": "black"},       # ชมพูหวาน
    {"name": "Lavender (ม่วงอ่อน)", "code": "#CE93D8", "text": "black"},     # ม่วงพาสเทล
    {"name": "Canary (เหลืองอ่อน)", "code": "#FFF59D", "text": "black"},     # เหลืองนวลๆ
    
    # --- กลุ่มสีคลาสสิค ---
    {"name": "Sand (ทรายทอง)", "code": "#D7CCC8", "text": "black"},         # เข้ากับธีมร้านกาแฟ/มินิมอล
    {"name": "Charcoal (ดำถ่าน)", "code": "#37474F", "text": "white"},       # ดำที่ไม่ดำสนิท ดูมีมิติ
    {"name": "White (ขาวสะอาด)", "code": "#FFFFFF", "text": "black"},        # ขาวคลีนๆ
]

# 🔥 สร้างรายการไอคอนทั้งหมดไว้ตรงนี้
ALL_ICONS = {
    # --- 💻 หมวด IT & Gadget ---
    "computer": "💻", 
    "phone_iphone": "📱", 
    "print": "🖨️",
    "camera_alt": "📷", 
    "headphones": "🎧", 
    "keyboard": "⌨️",  
    "mouse": "🖱️",
    "gamepad": "🎮",
    "watch": "⌚",

    # --- 🚗 หมวด ยานยนต์ (Automotive) ---
    "car": "🚗",
    "motorcycle": "🏍️",
    "tire": "🔘",   # ยางรถ
    "oil": "🛢️",    # น้ำมันเครื่อง
    "mechanic": "🔧", # อะไหล่/ซ่อม

    # --- 🌱 หมวด เกษตรกรรม (Agriculture) ---
    "fertilizer": "🌱", # ปุ๋ย/ต้นกล้า
    "tree": "🌳",       # ต้นไม้
    "flower": "🌻",     # ดอกไม้
    "tractor": "🚜",    # เครื่องจักรการเกษตร
    "rice": "🌾",       # ข้าว/ธัญพืช

    # --- 🏠 หมวด บ้านและของใช้ (Home & Living) ---
    "home": "🏠",
    "furniture": "🪑",  # เฟอร์นิเจอร์
    "bed": "🛏️",       # ห้องนอน
    "lamp": "💡",      # หลอดไฟ/ไฟฟ้า
    "kitchen": "🍳",   # เครื่องครัว
    "bath": "🛁",      # ห้องน้ำ
    "clean": "🧹",     # อุปกรณ์ทำความสะอาด

    # --- 👕 หมวด แฟชั่น (Fashion) ---
    "shirt": "👕",
    "dress": "👗",
    "shoe": "👟",
    "bag": "👜",

    # --- 📦 ทั่วไป (General) ---
    "pets": "🐾",      # สัตว์เลี้ยง
    "food": "🍔",      # อาหาร
    "drink": "🥤",     # เครื่องดื่ม
    "medicine": "💊",  # ยา/เภสัช
    "book": "📚",      # หนังสือ
    "sport": "⚽",     # กีฬา
    "gift": "🎁",      # ของขวัญ
    "category": "📦"   # ทั่วไป
}

# ==============================================================================
# 1. GLOBAL HELPER FUNCTIONS (แยกออกมาเพื่อให้โค้ดสะอาดและไม่ Error เรื่องตัวแปร)
# ==============================================================================

def create_order_card(order, page, api_url, update_callback, admin_name):
    """ฟังก์ชันสร้างการ์ดออเดอร์สำหรับหน้า Admin (ฉบับสมบูรณ์)"""
    
    # 1. ปุ่มดูสลิป
    btn_slip = ft.Container() 
    if order.get('slip_image') and order['slip_image'] != 'no_slip.jpg':
        slip_url = f"{api_url}/uploads/{order['slip_image']}"
        btn_slip = ft.ElevatedButton(
            "ดูสลิป", 
            icon="image", 
            bgcolor="#9C27B0", 
            color="white", 
            on_click=lambda e: page.launch_url(slip_url)
        )

    # 2. ปุ่มใบเสร็จ
    print_url = f"{api_url}/print_order/{order['order_id']}"
    btn_print = ft.ElevatedButton(
        "ใบเสร็จ", 
        icon="description", 
        bgcolor="#FF9800", 
        color="white", 
        on_click=lambda e: page.launch_url(print_url)
    )

    # 3. เช็คสถานะ
    is_shipped = "จัดส่ง" in order['status']
    is_cancelled = "ยกเลิก" in order['status']

    # ปุ่มยืนยัน
    btn_confirm = ft.ElevatedButton(
        "ยืนยัน" if not is_shipped else "ส่งแล้ว", 
        icon="check_circle", 
        bgcolor="#4CAF50" if not is_shipped else "grey", 
        color="white",
        disabled=(is_shipped or is_cancelled), 
        on_click=lambda e: update_callback(order['order_id'], "จัดส่งแล้ว")
    )

    # 4. ปุ่มยกเลิก/คืนของ (Logic)
    def cancel_action(e):
        try:
            res = requests.post(f"{api_url}/api/orders/cancel", json={'order_id': order['order_id'], 'admin_name': admin_name})
            if res.status_code == 200:
                page.open(ft.SnackBar(ft.Text(f"คืนสต็อก Order #{order['order_id']} แล้ว!", color="white"), bgcolor="red"))
                btn_cancel.disabled = True
                btn_cancel.text = "ยกเลิกแล้ว"
                btn_cancel.update()
                time.sleep(0.5)
            else:
                print(res.text)
        except Exception as ex:
            print(f"Cancel Error: {ex}")

    btn_cancel = ft.ElevatedButton(
        "คืนของ/ยกเลิก", 
        icon="cancel", 
        bgcolor="red", 
        color="white",
        disabled=(is_shipped or is_cancelled),
        on_click=cancel_action
    )

    # 5. ส่วนแสดงชื่อผู้ดูแล (Admin Name) - ที่คุณถามหา
    handler_info = ft.Container()
    if order.get('handled_by'):
        handler_info = ft.Container(
            content=ft.Row([
                ft.Icon("assignment_ind", size=16, color="blue"),
                ft.Text(f"ผู้ดูแล: {order['handled_by']}", size=12, color="blue", weight="bold")
            ]),
            bgcolor="#E3F2FD", 
            padding=5,
            border_radius=5,
            margin=ft.margin.only(top=5, bottom=5) 
        )

    # 6. สีสถานะ
    status_color = "grey"
    if order['status'] == "รอตรวจสอบ": status_color = "orange"
    elif "จัดส่ง" in order['status']: status_color = "green"
    elif "ยกเลิก" in order['status']: status_color = "red"

    # =========================================================
    # Return ตัวการ์ด (ประกอบร่างทุกอย่างเข้าด้วยกัน)
    # =========================================================
    return ft.Container(
        bgcolor="white",
        padding=20,
        border_radius=10,
        margin=ft.margin.only(bottom=10),
        shadow=ft.BoxShadow(blur_radius=5, color="#11000000"),
        content=ft.Column([
            # แถวบนสุด: Order ID + Status
            ft.Row([
                ft.Text(f"Order #{order['order_id']}", weight="bold", size=16),
                ft.Container(
                    content=ft.Text(order['status'], size=12, color="white"),
                    bgcolor=status_color,
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=15
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            # 🔥 ใส่ชื่อคนดูแลตรงนี้ครับ (ใต้ Order ID) 🔥
            handler_info,

            # ข้อมูลเวลา
            ft.Text(f"🕒 {order.get('timestamp', '-')}", size=12, color="grey"),
            ft.Divider(height=20, thickness=1),
            
            # ข้อมูลลูกค้า
            ft.Text(f"ลูกค้า: {order['customer']}", weight="bold"),
            ft.Row([
                ft.Text("ยอด: ", color="blue"), 
                ft.Text(f"{order['total']:,.0f} บาท", weight="bold", size=18, color="blue")
            ]),
            ft.Row([
                ft.Icon("location_on", size=14, color="pink"), 
                ft.Text(order['address'], size=12, color="grey", expand=True)
            ]),

            ft.Container(height=10),
            
            # 🔥 ใส่ปุ่มทั้งหมด (รวมถึงปุ่มยกเลิก) ตรงนี้
            ft.Row([btn_slip, btn_print, btn_confirm, btn_cancel], spacing=10, scroll="auto")
        ])
    )

# ==============================================================================
# 2. MAIN APP
# ==============================================================================

def main(page: ft.Page):
 

    page.theme = ft.Theme(color_scheme_seed="blue")
    # --- ตั้งค่าหน้าจอ ---
    page.title = "POSitive Shop Manager System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#FFFAF0"
    try:
        res = requests.get(f'{API_URL}/api/settings')
        if res.status_code == 200:
            d = res.json()
            if d.get('app_bgcolor'):
                page.bgcolor = d['app_bgcolor']
    except: pass

    page.padding = 0
    
    # ล็อคขนาดจอ Mobile (จำลอง)
    page.window.width = 400
    page.window.height = 600
    page.window.resizable = True
    page.window.maximizable = True
    
    
    
    current_user = {"name": "", "phone": ""}
    current_admin_role = None 
    selected_file_path = None
    current_admin_name = ""

    # --- Utility Functions (ฟังก์ชันช่วยเหลือภายใน) ---

    def api_bg(method, endpoint, json_data=None):
        """ฟังก์ชันยิง API แบบ Background Thread"""
        def task():
            try:
                if method == 'POST': requests.post(f'{API_URL}{endpoint}', json=json_data)
                elif method == 'GET': requests.get(f'{API_URL}{endpoint}')
            except: pass
        threading.Thread(target=task).start()

    def save_user_data(name, phone):
        page.client_storage.set("user_name", name)
        page.client_storage.set("user_phone", phone)
        current_user["name"] = name
        current_user["phone"] = phone

    def load_user_data():
        try:
            if page.client_storage.get("user_name"):
                current_user["name"] = page.client_storage.get("user_name")
                current_user["phone"] = page.client_storage.get("user_phone")
                return True
        except: return False
        return False
    
    def clear_user_data():
        page.client_storage.clear()
        current_user["name"] = ""
        current_user["phone"] = ""

    # --- Components ที่ใช้ร่วมกัน ---

    emp_img_path = None  # เปลี่ยนชื่อจาก selected_file_path
    emp_img_name = ft.Text("ยังไม่ได้เลือกรูป", size=12, color="grey")
    # ฟังก์ชันเมื่อเลือกไฟล์เสร็จ
    # ฟังก์ชันเมื่อเลือกรูปพนักงานเสร็จ
    def on_emp_img_picked(e: ft.FilePickerResultEvent):
        nonlocal emp_img_path
        if e.files:
            file = e.files[0]
            emp_img_path = file.path
            
            # อัปเดตข้อความ
            emp_img_name.value = f"เลือกรูป: {file.name}"
            emp_img_name.color = "green"
            emp_img_name.update()
        else:
            emp_img_name.value = "ยกเลิกการเลือก"
            emp_img_name.color = "grey"
            emp_img_name.update()

    # สร้างตัวเลือกไฟล์ (ตั้งชื่อใหม่ว่า emp_file_picker)
    emp_file_picker = ft.FilePicker(on_result=on_emp_img_picked)
    page.overlay.append(emp_file_picker)

    # File Picker (สำหรับอัปโหลดสลิป)
    def on_file_picked(e: ft.FilePickerResultEvent):
        nonlocal selected_file_path
        if e.files:
            selected_file_path = e.files[0].path
            # อัปเดตปุ่มเมื่อเลือกรูปแล้ว
            if upload_btn_ref.current:
                upload_btn_ref.current.content = ft.Row([ft.Icon("check", color="white"), ft.Text("แนบรูปแล้ว", color="white")], alignment="center")
                upload_btn_ref.current.bgcolor = "green"
                upload_btn_ref.current.update()
            
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)
    
    upload_btn_ref = ft.Ref() # ใช้ Ref เพื่ออ้างอิงปุ่มในหน้า Cart

    # ปุ่มเมนูด้านล่าง
    def create_menu_button(icon, text, func):
        return ft.Container(
            content=ft.Column([ft.Icon(icon, size=30, color="blue"), ft.Text(text, size=12)], alignment="center", spacing=5), 
            width=100, height=80, 
            bgcolor="white", 
            border_radius=15, 
            alignment=ft.alignment.center, 
            on_click=func, 
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color="grey300")
        )

    
    def show_product_details(product):
        try:
            # 1. จัดการรูปภาพ (ถ้ามีรูปให้โชว์รูป ถ้าไม่มีให้โชว์ไอคอน)
            img_content = ft.Container(
                content=ft.Icon(ft.icons.COMPUTER, size=80, color="blue"),
                alignment=ft.alignment.center, bgcolor="#FFF8E1", height=200, border_radius=10
            )
            
            if product.get('image'):
                img_url = f"{API_URL}/uploads/{product['image']}"
            else:
                img_url = "https://via.placeholder.com/400x250.png?text=No+Image"

            images_list = [
                img_url,                              
                "https://picsum.photos/id/1/400/250", # รูปหลอก 1
                "https://picsum.photos/id/7/400/250"  # รูปหลอก 2
            ]

            current_idx = [0]
            img_display = ft.Image(
                src=images_list[0],
                width=250, 
                height=250, 
                fit=ft.ImageFit.CONTAIN,
                border_radius=10
            )

            txt_indicator = ft.Text(f"1 / {len(images_list)}", size=12, color="grey")

            def change_image(e, delta):
                new_index = current_idx[0] + delta
                if new_index >= len(images_list): new_index = 0
                elif new_index < 0: new_index = len(images_list) - 1
                
                current_idx[0] = new_index
                img_display.src = images_list[new_index]
                txt_indicator.value = f"{new_index + 1} / {len(images_list)}"
                img_display.update()
                txt_indicator.update()

            img_display.width = 300
            img_display.height = 250
            img_display.fit = ft.ImageFit.CONTAIN
            img_content = ft.Container(
                width=300,  # ล็อคความกว้างไว้แค่นี้พอ (พอดีจอมือถือ)
                height=250,
                border=ft.border.all(1, "grey"),
                border_radius=10,
                content=ft.Stack(
                    controls=[
                        # ชั้นล่าง: รูปภาพ
                        img_display,
                        
                        # ชั้นกลาง: ปุ่มซ้าย (ลอยชิดซ้าย)
                        ft.Container(
                            content=ft.IconButton(
                                ft.icons.ARROW_BACK_IOS, 
                                icon_color="white", 
                                bgcolor=ft.colors.with_opacity(0.5, "black"),
                                icon_size=16,
                                on_click=lambda e: change_image(e, -1)
                            ),
                            alignment=ft.alignment.center_left,
                            left=5, top=0, bottom=0
                        ),
                        
                        # ชั้นกลาง: ปุ่มขวา (ลอยชิดขวา)
                        ft.Container(
                            content=ft.IconButton(
                                ft.icons.ARROW_FORWARD_IOS, 
                                icon_color="white", 
                                bgcolor=ft.colors.with_opacity(0.5, "black"),
                                icon_size=16,
                                on_click=lambda e: change_image(e, 1)
                            ),
                            alignment=ft.alignment.center_right,
                            right=5, top=0, bottom=0
                        ),
                        
                        # ชั้นบนสุด: เลขหน้า (ลอยขวาล่าง)
                        ft.Container(
                            content=ft.Container(
                                content=txt_indicator,
                                bgcolor=ft.colors.with_opacity(0.7, "white"),
                                padding=5, border_radius=5
                            ),
                            bottom=10, right=10
                        )
                    ]
                )
            )
            
            # 2. จัดการวิดีโอ (ถ้ามีลิงก์)
            video_btn = ft.Container()
            if product.get('video_url'):
                video_btn = ft.ElevatedButton(
                    "ดูคลิปรีวิวสินค้า ▶️", 
                    icon=ft.icons.PLAY_CIRCLE, 
                    bgcolor="red", color="white",
                    on_click=lambda e: page.launch_url(product['video_url'])
                )

            # 3. จัดการข้อมูลเฉพาะ (ยี่ห้อ และ ประกัน)
            brand_text = product.get('brand', '-')
            if not brand_text: brand_text = "-"

            warranty_text = product.get('warranty', '-')
            if not warranty_text: warranty_text = "-"

            p_unit = product.get('unit', 'ชิ้น')

            dlg = ft.AlertDialog(
                title=ft.Text(f"📦 รายละเอียด: {product['name']}"),
                content=ft.Container(
                    content=ft.Column([
                        img_content, # โชว์รูป
                        ft.Container(height=10),
                        # โชว์ราคา และ จำนวน
                        ft.Row([
                            ft.Text("ราคา:", weight="bold"), 
                            ft.Text(f"{product.get('price', 0):,.2f} บาท", color="green", size=16, weight="bold")
                        ]),
                        ft.Row([ft.Text("คงเหลือ:", weight="bold"), ft.Text(f"{product.get('stock', 0)} {p_unit}")]),
                        
                        ft.Divider(),
                        # โชว์ยี่ห้อ และ ประกัน 
                        ft.Row([ft.Icon(ft.icons.BRANDING_WATERMARK, size=16), ft.Text("รุ่น / แบรนด์ / ผู้ผลิต: ", weight="bold"), ft.Text(brand_text)]),
                        ft.Row([ft.Icon(ft.icons.VERIFIED_USER, size=16), ft.Text("การรับประกัน: ", weight="bold"), ft.Text(warranty_text)]),
                        
                        ft.Divider(),
                        ft.Text("📝 รายละเอียดสินค้า", weight="bold", color="blue"),
                        ft.Text(product.get('desc', '-'), size=14),
                        
                        ft.Container(height=10),
                        ft.Row([video_btn], alignment="center") # ปุ่มวิดีโอ
                        
                    ], scroll="auto", height=400) 
                ),
                actions=[
                    ft.TextButton("ปิด", on_click=lambda e: page.close(dlg))
                ],
                actions_alignment="center"
            )
            page.open(dlg)
            
        except Exception as e: 
            print(f"Popup Error: {e}")

    # ==========================================================================
    # 3. ROUTING SYSTEM (ระบบเปลี่ยนหน้า)
    # ==========================================================================
    def route_change(route):
        page.views.clear()
        
        logo_src = "https://via.placeholder.com/150" # รูปสำรองกันเหนียว
        my_theme_color = "blue" # <--- 🔥 ประกาศตัวแปรสีเริ่มต้น
        my_text_color = "white"   # <--- 🔥 ตัวแปรใหม่สำหรับสีตัวหนังสือ

        try:
            # ถาม Server ว่าตอนนี้ใช้รูปอะไร
            res = requests.get(f'{API_URL}/api/settings') 
            if res.status_code == 200:
                d = res.json()
                # ถ้า Server บอกชื่อรูปมา ก็ใช้ชื่อนั้น
                if d.get('shop_logo'):
                    logo_src = f"{API_URL}/uploads/{d['shop_logo']}?v={int(time.time())}"

                if d.get('app_theme_color'):
                    my_theme_color = d['app_theme_color']
                    for color_option in THEME_COLORS:
                        if color_option['code'] == my_theme_color:
                            my_text_color = color_option['text']
                            break   
        except:
            pass

        
        # --- หน้า LOGIN ---
        if page.route == "/login":
            
            # สร้างตัวแปร UI
            name = ft.TextField(label="ชื่อ", prefix_icon="person", border_radius=15, bgcolor="#F5F5F5", filled=True)
            phone = ft.TextField(label="เบอร์โทร", prefix_icon="phone", border_radius=15, bgcolor="#F5F5F5", keyboard_type="number", filled=True)
            
            def login(e):
                if name.value: 
                    save_user_data(name.value, phone.value)
                    page.go("/")

            skip_btn = ft.TextButton("เข้าชมสินค้าโดยไม่ล็อกอิน >", on_click=lambda _: page.go("/"))        
            
            # Popup Login Admin
            
            admin_user_input = ft.TextField(label="Username", text_align="center") # เพิ่มช่อง User
            admin_pass_input = ft.TextField(label="Password", password=True, text_align="center")
            
            def check_admin_login(e):
                try:
                    # ยิง API ไปเช็ค Login ที่ Server
                    res = requests.post(f'{API_URL}/api/login', json={
                        'user': admin_user_input.value, 
                        'pass': admin_pass_input.value
                    })
                    data = res.json()

                    if data['status'] == 'success':
                        
                        # 1. บันทึกยศ (Role) เอาไว้ใช้จัดหน้าจอ (ของเดิม)
                        nonlocal current_admin_role
                        current_admin_role = data['user']['role'] 
                        
                        # 🔥🔥🔥 2. เพิ่มส่วนนี้ครับ: บันทึกชื่อคนล็อกอิน (Audit Trail) 🔥🔥🔥
                        nonlocal current_admin_name
                        # พยายามดึง display_name ก่อน ถ้าไม่มีให้ใช้ username แทน
                        current_admin_name = data['user'].get('display_name', data['user']['username'])
                        # -------------------------------------------------------------
                        
                        page.close(admin_dialog)
                        page.go("/admin")
                        
                        user_display_name = data['user'].get('display_name', 'Admin')
                        page.open(ft.SnackBar(ft.Text(f"ยินดีต้อนรับคุณ {user_display_name}")))
                    else:
                        admin_pass_input.error_text = "ชื่อหรือรหัสผิด"
                        admin_pass_input.update()
                except Exception as ex: 
                    print(f"Login Error: {ex}") 
                    admin_pass_input.error_text = "เกิดข้อผิดพลาดในการเชื่อมต่อ"
                    admin_pass_input.update()
            
            admin_dialog = ft.AlertDialog(
                title=ft.Text("Admin Login"), 
                content=ft.Column([
                    admin_user_input, # ใส่ช่อง User เพิ่มเข้าไป
                    admin_pass_input
                ], height=150),
                actions=[ft.TextButton("ยกเลิก", on_click=lambda e: page.close(admin_dialog)), ft.ElevatedButton("เข้าสู่ระบบ", on_click=check_admin_login)]
            )

            # --- แก้ไขจุดเสี่ยงจอเทา ---
            page.views.append(ft.View("/login", [
                ft.Stack([
                    ft.Container(
                        expand=True, padding=30,
                        content=ft.Column([
                            
                            # 🔥 จุดที่แก้: ใส่ error_content กันแอปพัง 🔥
                            ft.Image(
                                src=logo_src, 
                                width=150, 
                                height=150, 
                                fit=ft.ImageFit.CONTAIN,
                                error_content=ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED, size=50, color="grey") # <--- ใส่บรรทัดนี้ครับ จอจะไม่เทา
                            ),
                            
                            ft.Text("Welcome", size=24, weight="bold"),
                            ft.Container(height=20),
                            name,
                            phone,
                            ft.Container(height=20),
                            ft.ElevatedButton("เข้าสู่ระบบ", width=400, height=50, on_click=login),
                            ft.Container(height=10),
                            skip_btn

                        ], alignment="center", horizontal_alignment="center")
                    ),
                    
                    # ปุ่ม Admin (รูปโล่)
                    ft.Container(
                        content=ft.IconButton(
                            icon="security", 
                            icon_color="grey",
                            tooltip="Admin Login",
                            on_click=lambda _: page.open(admin_dialog)
                        ),
                        top=30, right=10,
                    )
              
                ], expand=True) 
            ], padding=0, bgcolor=page.bgcolor))
            
        # --- หน้า HOME ---
        if page.route == "/":
            is_logged_in = current_user["name"] != ""
            appbar_title = f"Hi, {current_user['name']}" if is_logged_in else "ยินดีต้อนรับ"
            recommend_items = ft.Row(scroll="auto")

            img_top = "https://via.placeholder.com/800x400"
            img_promo = "https://via.placeholder.com/800x200"
            
            try:
                res = requests.get(f'{API_URL}/api/settings')
                d = res.json()
                if d:
                    if d.get('banner_top'): img_top = f"{API_URL}/uploads/{d['banner_top']}"
                    if d.get('banner_promo'): img_promo = f"{API_URL}/uploads/{d['banner_promo']}"
            except: pass

            try:
                res = requests.get(f'{API_URL}/api/products')
                products = res.json()
                for p in products[:4]: 
                    if p.get('image'):
                        img_url = f"{API_URL}/uploads/{p['image']}"
                        item_image = ft.Image(src=img_url, width=100, height=100, fit=ft.ImageFit.COVER, border_radius=10, gapless_playback=True)
                    else:
                        icon = ft.icons.COMPUTER if p.get('type') == 'supply' else "cruelty_free"
                        col = "blue" if p.get('type') == 'supply' else "pink"
                        item_image = ft.Icon(icon, size=50, color=col)

                    recommend_items.controls.append(
                        ft.Container(
                            width=140, height=180, bgcolor="white", border_radius=15, padding=10, margin=5,
                            shadow=ft.BoxShadow(blur_radius=5, color="#11000000"),
                            content=ft.Column([
                                ft.Container(content=item_image, alignment=ft.alignment.center, height=100),
                                ft.Text(p['name'], size=14, weight="bold", no_wrap=True, text_align="center"),
                                ft.Text(f"{p['price']:,} ฿", color="blue", size=14, weight="bold")
                            ], alignment="center"),
                            on_click=lambda e, x=p: show_product_details(x)
                        )
                    )
            except Exception as e:
                print(f"Home products error: {e}")

            page.views.append(ft.View("/", [
                ft.AppBar(
                    leading=ft.Container(
                        content=ft.Image(
                            src=logo_src,          # ✅ แก้ตรงนี้ครับ
                            fit=ft.ImageFit.CONTAIN
                            
                         ),
                        padding=10,
                        on_click=lambda _: page.go("/")
                        
            ),
                    leading_width=60,

                    # 2. ใส่ชื่อร้านตัวใหญ่ๆ ตรงกลาง
                    title=ft.Column([
                        ft.Text("POSitive Shop", size=18, weight="bold"),
                        ft.Text(f"สวัสดีคุณ, {current_user['name']}" if is_logged_in else "Welcome", size=12)
                    ], spacing=0),
                    
                    # 3. แก้สีพื้นหลังเป็น "blue" (กันเหนียวไว้ก่อน)
                    bgcolor=my_theme_color, 
                    color=my_text_color,
                    
                    # 4. 🔥 แก้ตรงนี้ครับ: ลบ ... ออก แล้วใส่ปุ่มจริงๆ ลงไป
                    actions=[
                        ft.IconButton(icon="person", icon_color=my_text_color, on_click=lambda _: page.go("/profile") if is_logged_in else page.go("/login"))
                    ]
                ),
                ft.Column([
                    ft.Container(expand=True, padding=20, content=ft.Column([
                        # 🔥 [รูปที่ 1] แบนเนอร์บน (Top Banner) 🔥
                        ft.Container(
                            content=ft.Image(
                                src=img_top,   # ใช้ตัวแปร img_top ที่ดึงมาจาก Server
                                fit=ft.ImageFit.COVER, 
                                border_radius=15
                            ),
                            height=200,        # ความสูงรูปบน
                            width=float("inf"),
                            shadow=ft.BoxShadow(blur_radius=10, color="#33000000"),
                            border_radius=15, 
                            margin=ft.margin.only(bottom=10)
                        ),

                        # 🔥 [รูปที่ 2] โปรโมชั่น (Promo Banner) 🔥
                        ft.Container(
                            content=ft.Image(
                                src=img_promo, # ใช้ตัวแปร img_promo ที่ดึงมาจาก Server
                                fit=ft.ImageFit.COVER, 
                                border_radius=15
                            ),
                            height=150,        # ความสูงรูปล่าง (ปรับได้ตามชอบ)
                            width=float("inf"),
                            shadow=ft.BoxShadow(blur_radius=10, color="#33000000"),
                            border_radius=15, 
                            margin=ft.margin.only(bottom=20)
                        ),
                        # -----------------------------------------------------

                        ft.Container(height=10),
                        
                        # 3. สินค้าแนะนำ (อันเดิมของคุณ)
                        ft.Text("สินค้าแนะนำ 🔥", size=18, weight="bold"),
                        ft.Container(content=recommend_items, height=210),
                        
                    ], scroll="auto")),
                    ft.Container(padding=0, content=ft.Row([
                        create_menu_button("store", "สินค้า", lambda _: page.go("/shop")), 
                        create_menu_button("shopping_cart", "ตะกร้า", lambda _: page.go("/cart")), 
                        create_menu_button("person", "ข้อมูล", lambda _: page.go("/profile") if is_logged_in else page.go("/login"))
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY))
                ], expand=True)
            ], bgcolor=page.bgcolor))
 
        # --- หน้า SHOP (รายการสินค้า) ---
        # --- SHOP PAGE (แก้ไข: ให้โชว์รูปสินค้าจริง) ---
        if page.route == "/shop":
            # 1. นับจำนวนสินค้าในตะกร้า (เพื่อโชว์ที่ปุ่มมุมขวาล่าง)
            cart_count = 0
            try:
                res = requests.post(f'{API_URL}/api/cart', json={'user': current_user['name']})
                cart_data = res.json()
                if cart_data:
                    cart_count = sum(item['qty'] for item in cart_data)
            except: pass
            
            cart_fab = ft.FloatingActionButton(
                icon="shopping_cart", 
                text=str(cart_count) if cart_count > 0 else None, 
                bgcolor="blue", 
                foreground_color="white",  # <--- แก้เป็น foreground_color ครับ
                on_click=lambda _: page.go("/cart")
            )
            
            # 2. ฟังก์ชันกดเพิ่มลงตะกร้า
            def add_to_cart(pid):
                # เช็คว่าล็อกอินหรือยัง?
                if not current_user["name"]:
                    page.go("/login")
                    return
                payload = {'id': pid, 'user': current_user['name']}
                api_bg('POST', '/api/cart/add', payload)
                
                # อัปเดตตัวเลขที่ปุ่มทันที
                nonlocal cart_count
                cart_count += 1
                cart_fab.text = str(cart_count)
                cart_fab.update()
                
                page.snack_bar = ft.SnackBar(ft.Text("เพิ่มลงตะกร้าแล้ว")); page.snack_bar.open = True; page.update()

            # 3. โหลดรายการสินค้า
            items = ft.Column(scroll="auto", expand=True)
            try:
                res = requests.get(f'{API_URL}/api/products')
                products = res.json()
                
                for p in products:
                    # --- ส่วนสำคัญ: เช็คว่ามีรูปไหม? ---
                    display_content = None
                    if p.get('image'):
                        img_src = f"{API_URL}/uploads/{p['image']}"
                        product_img = ft.Image(src=img_src, width=100, height=100, fit=ft.ImageFit.COVER, border_radius=10, gapless_playback=True)
                    else:
                        product_img = ft.Container(
                            content=ft.Icon("pets", size=40, color="grey"),
                            width=100, height=100, bgcolor="#f0f0f0", border_radius=10, alignment=ft.alignment.center
                        )

                    # 2. สร้างการ์ดสินค้าแบบใหม่ (Premium Design) ✨
                    items.controls.append(ft.Container(
                        bgcolor="white",
                        padding=10,
                        border_radius=15,
                        margin=ft.margin.only(bottom=15, left=10, right=10),
                        # เพิ่มเงาฟุ้งๆ ให้ดูลอยมีมิติ
                        shadow=ft.BoxShadow(blur_radius=8, color="#15000000", offset=ft.Offset(0, 4)),
                        
                        content=ft.Row([
                            # ส่วนรูปภาพ (ซ้าย)
                            product_img,
                            
                            # ส่วนข้อมูล (กลาง)
                            ft.Column([
                                # ชื่อสินค้า
                                ft.Text(p['name'], weight="bold", size=16, no_wrap=True),
                                
                                # ป้ายกำกับประกัน (Warranty Tag) 🛡️
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.icons.VERIFIED_USER, size=12, color="#1565C0"), 
                                        ft.Text(f"ประกัน {p.get('warranty', '-')}", size=12, color="#0D47A1", weight="bold")
                                    ], spacing=5, alignment="start"),
                                    
                                    bgcolor="#E3F2FD", 
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=20, 
                                ),
                                # ราคา
                                ft.Text(f"{p['price']:,} ฿", color="blue", weight="bold", size=18)
                            ], expand=True, spacing=5),
                            
                            # ส่วนปุ่มกด (ขวา)
                            ft.Column([
                                # ปุ่มดูรายละเอียด (ตัว i)
                                ft.IconButton(icon="info_outline", icon_color="grey", icon_size=20, on_click=lambda e, x=p: show_product_details(x)),
                                
                                # ปุ่มเพิ่มลงตะกร้า 
                                ft.Container(
                                    content=ft.Icon("add", color="white"),
                                    width=40, height=40,
                                    bgcolor="blue", # สีปุ่มเด่นๆ
                                    border_radius=10, # สี่เหลี่ยมมน
                                    alignment=ft.alignment.center,
                                    on_click=lambda e, pid=p['id']: add_to_cart(pid),
                                    ink=True # กดแล้วมีเอฟเฟกต์น้ำกระเพื่อม
                                )
                            ], alignment="spaceBetween", spacing=10)
                            
                        ], alignment="start")
                    ))
                    
                items.controls.append(ft.Container(height=80)) # เว้นที่ว่างด้านล่างกันปุ่มบัง
            except Exception as e: 
                items.controls.append(ft.Text(f"โหลดข้อมูลไม่สำเร็จ: {e}", color="red"))

            page.views.append(ft.View("/shop", [
                ft.AppBar(
                    title=ft.Text("สินค้าทั้งหมด"), 
                    bgcolor=my_theme_color, 
                    color=my_text_color,
                    leading=ft.IconButton(icon="arrow_back", icon_color=my_text_color, on_click=lambda _: page.go("/"))
                ),
                ft.Container(content=items, expand=True)
            ], floating_action_button=cart_fab, bgcolor=page.bgcolor))

        # --- หน้า CART (ตะกร้าสินค้า) ---
        # --- หน้า CART (ตะกร้าสินค้า) ---
        if page.route == "/cart":
            nonlocal selected_file_path; selected_file_path = None

            DYNAMIC_MAPPING = {}
            try:
                cat_res = requests.get(f'{API_URL}/api/categories')
                if cat_res.status_code == 200:
                    for c in cat_res.json():
                        DYNAMIC_MAPPING[c['code']] = c.get('shipping_size', 'size_s')

            except: pass

            SHOP_ZIPCODE = "10000" # ค่า Default
            local_cart_data = []
            try:
                res = requests.get(f'{API_URL}/api/settings')
                if res.status_code == 200:
                    d = res.json()
                    if d.get('shop_zipcode'): SHOP_ZIPCODE = d['shop_zipcode']
            except: pass
            # -----------
            
            # ==========================================
            # 1. เตรียมตัวแปร UI (สร้างรอไว้ก่อน)
            # ==========================================
            
            # ช่องกรอกชื่อและที่อยู่
            name_field = ft.TextField(label="ชื่อผู้รับ", value=current_user['name'], bgcolor="white", prefix_icon="person")
            
            # ช่องกรอกรหัสไปรษณีย์ (ZIP Code)
            txt_zipcode = ft.TextField(
                label="รหัสไปรษณีย์", 
                keyboard_type="number", 
                max_length=5,
                border_radius=10,
                bgcolor="white",
                prefix_icon="map"
            )

            # Dropdown เลือกบริษัทขนส่ง
            dropdown_provider = ft.Dropdown(
                label="เลือกวิธีการจัดส่ง",
                options=[
                    ft.dropdown.Option("pickup", "🏪 รับสินค้าที่ร้าน (ฟรี)"),
                    ft.dropdown.Option("lalamove","🚚 Lalamove (ส่งด่วน)"),
                    
                    # 🔥 เติม Emoji ให้ครบทุกอันตรงนี้ครับ
                    ft.dropdown.Option("kerry", "🟠 Kerry Express"),      # สีส้ม
                    ft.dropdown.Option("flash", "⚡ Flash Express"),      # สายฟ้า (สีเหลือง)
                    ft.dropdown.Option("thaipost", "📮 ไปรษณีย์ไทย (EMS)"), # ตู้ไปรษณีย์แดง
                    ft.dropdown.Option("pet_move", "🐾 รถรับส่งสัตว์เลี้ยง"), # รอยเท้าสัตว์
                ],
                value="pickup",
                bgcolor="white",
                prefix_icon="local_shipping",
            )

            # ที่อยู่ (เหลือแค่บ้านเลขที่/ถนน)
            address_field = ft.TextField(
                label="ที่อยู่ (บ้านเลขที่ / หมู่บ้าน / ซอย / ถนน / ตำบล)", 
                multiline=True, 
                min_lines=2, 
                bgcolor="white",
                prefix_icon="home"
            )

            confirm_btn = ft.ElevatedButton("ยืนยันการสั่งซื้อ", bgcolor="blue", color="white")

            # กล่องข้อมูลธนาคาร
            bank_info_ui = ft.Container(
                bgcolor="#E3F2FD", # สีฟ้าอ่อน
                padding=15,
                border_radius=10,
                border=ft.border.all(1, "blue"),
                content=ft.Column([
                    ft.Row([ft.Icon("account_balance", color="blue"), ft.Text("โอนเงินเข้าบัญชี", weight="bold", size=16)]),
                    ft.Divider(height=10, color="blue"),
                    ft.Row([
                        # ถ้าไม่มีโลโก้ อาจใช้ Icon แทนได้
                        ft.Image(src="https://upload.wikimedia.org/wikipedia/commons/5/59/Kbank_Logo.png", width=40, height=40,
                                 error_content=ft.Icon("account_balance_wallet")), 
                        ft.Column([
                            ft.Text("ธนาคารกสิกรไทย (K-Bank)", weight="bold"),
                            ft.Text("เลขที่: 123-4-56789-0", size=16, weight="bold", color="blue"),
                            ft.Text("ชื่อ: POSitive Shop Official")
                        ], spacing=2)
                    ])
                ])
            )
            
            # ปุ่มอัปโหลดสลิป
            upload_ui = ft.Container(
                ref=upload_btn_ref, # ต้องมั่นใจว่าประกาศ upload_btn_ref = ft.Ref() ไว้ข้างบน main แล้ว
                content=ft.Row([ft.Icon("cloud_upload", color="blue"), ft.Text("แนบสลิป", color="blue")], alignment="center"), 
                bgcolor="white", border=ft.border.all(1, "blue"), border_radius=10, padding=10, 
                on_click=lambda _: file_picker.pick_files()
            )

            # ตัวแปรเก็บค่าตัวเลข
            shipping_cost = 0; subtotal = 0; vat_amount = 0; grand_total = 0
            
            # ตัวแสดงผลราคา (Text)
            txt_subtotal = ft.Text("0.00 บ.", weight="bold")
            txt_vat = ft.Text("0.00 บ.", color="orange")
            txt_shipping = ft.Text("รอรหัสไปรษณีย์...", color="grey")
            txt_total = ft.Text("0.00 บ.", size=20, weight="bold", color="blue")
            
            summary_text = ft.Column() # ตัวแปร Placeholder สำหรับกล่องสรุปราคา

            # ==========================================
            # 2. ฟังก์ชัน Logic (คำนวณเงิน)
            # ==========================================

            # --- ฟังก์ชันรวมเงิน (Total Calculation) ---
            # --- ฟังก์ชันรวมเงิน (Total Calculation) ---
            # --- ฟังก์ชันรวมเงิน (Total Calculation) ---
            def calculate_totals_logic():
                nonlocal subtotal, vat_amount, grand_total, shipping_cost
                
                # คำนวณยอดเงิน
                total_before_vat = subtotal + shipping_cost
                vat_amount = total_before_vat * 0.07 
                grand_total = total_before_vat + vat_amount
                
                # อัปเดตข้อความตัวเลข
                txt_subtotal.value = f"{subtotal:,.2f} บ."
                txt_vat.value = f"{vat_amount:,.2f} บ."
                txt_total.value = f"{grand_total:,.2f} บ."
                
                # 🔥 ดึงรายละเอียดที่ซ่อนไว้ใน .data ออกมา (ถ้าไม่มีให้เป็นข้อความว่าง)
                shipping_details = txt_shipping.data if txt_shipping.data else ""

                # สร้าง UI กล่องสรุปราคาใหม่
                summary_content = [
                    ft.Row([ft.Text("ราคาสินค้า:", color="black"), txt_subtotal], alignment="spaceBetween"),
                    ft.Row([ft.Text("VAT (7%):", color="orange"), txt_vat], alignment="spaceBetween"),
                    
                    # 🔥🔥🔥 แก้ไขใหม่: ใช้ Column เพื่อจัดชิดขวาและแสดงรายละเอียด 🔥🔥🔥
                    ft.Row([
                        ft.Text("ค่าจัดส่ง:", color="black"), 
                        
                        # ใช้ Container ดันให้เต็มพื้นที่
                        ft.Container(
                            content=ft.Column([
                                # 1. บรรทัดราคา (ตัวใหญ่ ชิดขวา)
                                ft.Text(txt_shipping.value, color="blue", weight="bold", text_align=ft.TextAlign.RIGHT),
                                
                                # 2. บรรทัดรายละเอียด (ตัวเล็ก สีเทา ชิดขวา)
                                ft.Text(shipping_details, size=12, color="grey", text_align=ft.TextAlign.RIGHT)
                            ], 
                            # สั่งให้ Content ใน Column ชิดขวา (สำคัญมาก!)
                            horizontal_alignment=ft.CrossAxisAlignment.END, 
                            spacing=2
                            ),
                            expand=True, # ขยายพื้นที่ให้สุด
                            alignment=ft.alignment.center_right # บังคับให้ก้อน Column ไปกองรวมกันทางขวา
                        )
                    ], 
                    alignment="spaceBetween", 
                    vertical_alignment=ft.CrossAxisAlignment.START # ให้คำว่า "ค่าจัดส่ง:" ลอยอยู่บรรทัดบนสุด
                    ),
                    # -----------------------------------------------------

                    ft.Divider(),
                    ft.Row([ft.Text("ยอดสุทธิ:", size=18, weight="bold", color="black"), txt_total], alignment="spaceBetween")
                ]
                summary_text.controls = summary_content
                if summary_text.page: summary_text.update()

            # --- ฟังก์ชันคำนวณค่าส่ง (Shipping Logic) ---
            # --- ฟังก์ชันคำนวณค่าส่ง (Shipping Logic: ฉบับแก้ไข Origin) ---
            # --- ฟังก์ชันคำนวณค่าส่ง (ฉบับสมบูรณ์ + แก้ Lalamove) ---
            def calculate_shipping(e=None):
                nonlocal shipping_cost
                
                # ---------------------------------------------------------
                # 1. เช็คกรณี "รับสินค้าที่ร้าน" (Pickup)
                # ---------------------------------------------------------
                if dropdown_provider.value == "pickup":
                    shipping_cost = 0
                    txt_shipping.value = "0.00 บ."
                    txt_shipping.data = "(รับสินค้าที่ร้าน)" 
                    txt_shipping.color = "green"
                    calculate_totals_logic()
                    return 

                # ---------------------------------------------------------
                # 2. เริ่มขั้นตอนคำนวณราคาเริ่มต้น (Base Price) ตามระยะทาง
                # ---------------------------------------------------------
                code = txt_zipcode.value
                
                # เช็คระยะทาง (ใช้ตัวแปร SHOP_ZIPCODE ที่โหลดไว้หน้า Cart)
                if len(code) == 5:
                    shop_prefix = SHOP_ZIPCODE[:2]
                    cust_prefix = code[:2]
                    
                    if dropdown_provider.value == "lalamove":
                        base_price = 150.0
                        zone_name = "Lalamove"
                    elif shop_prefix == cust_prefix:
                        base_price = 45.0
                        zone_name = "พื้นที่ใกล้เคียง"
                    else:
                        base_price = 80.0
                        zone_name = "ข้ามเขต/ตจว."
                else:
                    # กรณีรหัสไปรษณีย์ไม่ครบ
                    shipping_cost = 0
                    txt_shipping.value = "รอรหัสปณ..."
                    txt_shipping.data = "" 
                    txt_shipping.color = "grey"
                    calculate_totals_logic()
                    return

                # ---------------------------------------------------------
                # 3. คำนวณค่าส่งเพิ่มตามไซส์ (Weight Charge) [จุดที่คุณแก้]
                # ---------------------------------------------------------
                
                # ราคามาตรฐานของแต่ละไซส์
                SIZE_PRICES = {
                    'size_s': 0,   # <--- เปลี่ยนจาก 20 เป็น 0 บาท (สมเหตุสมผลที่สุด)
                    'size_m': 50,  # ไซส์กลาง บวก 50
                    'size_l': 150, 
                    'size_xl': 300, # ของหนัก บวก 300 (ถูกต้องแล้ว)
                    'pet_small': 500, 
                    'pet_large': 1500
                }
                
                # สร้างตารางเทียบไซส์ (Mapping) จาก Database
                # 1. โหลดข้อมูล Mapping ไซส์มาเช็คก่อน
                

                has_pet = False
                has_heavy = False

                if cart_data:
                    for item in cart_data:
                        p_type = item.get('type', '9000')
                        size = DYNAMIC_MAPPING.get(p_type, 'size_s')
                        
                        if size in ['pet_small', 'pet_large']: has_pet = True
                        if size == 'size_xl': has_heavy = True

                # เริ่มวนลูปคำนวณสินค้าในตะกร้า
                weight_charge = 0
                try:
                    
                    current_cart = local_cart_data

                    for item in current_cart:
                        qty = item['qty']
                        p_type = item.get('type', '9000') 
                        
                        # 1. หาไซส์ของสินค้าชิ้นนี้
                        my_size = DYNAMIC_MAPPING.get(p_type, 'size_s') 
                        
                        # 🔥🔥🔥 2. Logic ใหม่: เช็ค Lalamove ตรงนี้ 🔥🔥🔥
                        if dropdown_provider.value == "lalamove":
                            # ถ้าเป็น Lalamove และเป็นของชิ้นเล็ก (S, M) -> ไม่คิดเงินเพิ่ม (0 บาท)
                            if my_size in ['size_s', 'size_m']:
                                price_per_item = 0
                            else:
                                # ถ้าเป็นชิ้นใหญ่ (L, XL) ยังคิดเงินตามเดิม
                                price_per_item = SIZE_PRICES.get(my_size, 0)
                        else:
                            # ถ้าเป็นขนส่งอื่น (Kerry/Flash) คิดเงินตามปกติทุกไซส์
                            price_per_item = SIZE_PRICES.get(my_size, 0)
                        # ------------------------------------------------
                        
                        # 3. รวมยอด
                        weight_charge += (price_per_item * qty)
                            
                except Exception as ex:
                    print(f"Calc Error: {ex}")
                    weight_charge = 0

                # ---------------------------------------------------------
                # 4. รวมยอดทั้งหมดและแสดงผล
                # ---------------------------------------------------------
                shipping_cost = base_price + weight_charge
                
                # สร้างข้อความรายละเอียด
                detail_text = f"{base_price:.0f} ({zone_name})"
                if weight_charge > 0:
                    detail_text += f" + ไซส์พิเศษ {weight_charge:,.0f}"
                
                # อัปเดตหน้าจอ (แยก value กับ data เพื่อให้ Column จัดหน้าสวยๆ)
                txt_shipping.value = f"{shipping_cost:,.2f} บ."
                txt_shipping.data = f"[{detail_text}]"
                txt_shipping.color = "blue"
                
                calculate_totals_logic()
            # ผูกฟังก์ชันกับช่องกรอกรหัสไปรษณีย์
            txt_zipcode.on_change = calculate_shipping
            dropdown_provider.on_change = calculate_shipping

            # --- ฟังก์ชันกดสั่งซื้อ (Submit Order) ---
            def confirm_order(e):
                # 1. เช็คก่อนว่าลูกค้าเลือก "รับเอง" หรือไม่?
                is_pickup = (dropdown_provider.value == "pickup")


                if not name_field.value or not selected_file_path:
                     page.snack_bar = ft.SnackBar(ft.Text("⚠️ กรุณากรอกชื่อและแนบสลิป"), bgcolor="red")
                     page.snack_bar.open = True; page.update()
                     return

                if not is_pickup:
                    if not address_field.value or len(txt_zipcode.value) != 5:
                        page.snack_bar = ft.SnackBar(ft.Text("⚠️ กรุณากรอกที่อยู่และรหัสไปรษณีย์ให้ครบ"), bgcolor="red")
                        page.snack_bar.open = True; page.update()
                        return
                
                # เริ่มส่งข้อมูล
                confirm_btn.disabled = True; confirm_btn.text = "กำลังส่ง..."; page.update()
                try:
                    # ถ้าเป็นรับเอง ให้เขียนที่อยู่ว่า "รับที่ร้าน"
                    full_address = f"รับสินค้าที่ร้าน (โดยคุณ {name_field.value})"
                    
                    if not is_pickup:
                        full_address = f"{address_field.value} รหัส {txt_zipcode.value} ({dropdown_provider.value})"
                    
                    files = {'slip': open(selected_file_path, 'rb')}
                    data = {
                        'user': current_user['name'],
                        'name': name_field.value,
                        'address': full_address,
                        'subtotal': subtotal, 'shipping': shipping_cost, 'vat': vat_amount, 'total': grand_total
                    }
                    requests.post(f'{API_URL}/api/checkout', data=data, files=files)
                    page.go("/success")
                except Exception as ex:
                    confirm_btn.disabled = False; confirm_btn.text = "ลองใหม่"; page.update()
                    print(ex)

            confirm_btn.on_click = confirm_order

            # ==========================================
            # 3. โหลดข้อมูลตะกร้า & จัดวาง Layout (พร้อม Auto-Filter)
            # ==========================================
            cart_content = []
            try:
                res = requests.post(f'{API_URL}/api/cart', json={'user': current_user['name']})
                cart_data = res.json()
                local_cart_data = cart_data
                
                if not cart_data:
                    cart_content.append(ft.Column([
                        ft.Icon("remove_shopping_cart", size=60, color="grey"),
                        ft.Text("ตะกร้าว่างเปล่า", color="grey")
                    ], alignment="center", horizontal_alignment="center"))
                else:
                    # 🔥🔥🔥 ส่วนที่เพิ่มใหม่: ระบบกรองขนส่งอัตโนมัติ (Auto-Filter) 🔥🔥🔥
                    # 1. เช็คว่าในตะกร้ามี "สัตว์เลี้ยง" หรือ "ของใหญ่" ไหม?
                    DYNAMIC_MAPPING = {}
                    try:
                        cat_res = requests.get(f'{API_URL}/api/categories')
                        if cat_res.status_code == 200:
                            for c in cat_res.json():
                                DYNAMIC_MAPPING[c['code']] = c.get('shipping_size', 'size_s')
                    except: pass

                    has_pet = False
                    has_heavy = False

                    for item in cart_data:
                        p_type = item.get('type', '9000')
                        size = DYNAMIC_MAPPING.get(p_type, 'size_s')
                        if size in ['pet_small', 'pet_large']: has_pet = True
                        if size == 'size_xl': has_heavy = True

                    # 2. ปรับเปลี่ยนตัวเลือก Dropdown ตามเงื่อนไข
                    new_options = [ft.dropdown.Option("pickup", "🏪 รับสินค้าที่ร้าน (ฟรี)")]
                    
                    if has_pet:
                        # 🐶 มีสัตว์เลี้ยง -> บังคับ Pet Move
                        new_options.append(ft.dropdown.Option("pet_move", "🐾 รถรับส่งสัตว์เลี้ยง (Pet Move)"))
                        # ถ้าของเดิมไม่ใช่ pet_move หรือ pickup ให้เปลี่ยนเป็น pet_move ทันที
                        if dropdown_provider.value not in ["pickup", "pet_move"]:
                            dropdown_provider.value = "pet_move"
                            
                    elif has_heavy:
                        # 🚛 มีของใหญ่ -> บังคับ Lalamove
                        new_options.append(ft.dropdown.Option("lalamove", "🚚 Lalamove (สำหรับของชิ้นใหญ่)"))
                        if dropdown_provider.value not in ["pickup", "lalamove"]:
                            dropdown_provider.value = "lalamove"
                            
                    else:
                        # 📦 สินค้าปกติ -> เลือกได้ครบ
                        new_options.extend([
                            ft.dropdown.Option("lalamove", "🚚 Lalamove (ส่งด่วน)"),
                            
                            # 🔥 แก้ให้เหมือนข้างบนครับ
                            ft.dropdown.Option("kerry", "🟠 Kerry Express"),
                            ft.dropdown.Option("flash", "⚡ Flash Express"),
                            ft.dropdown.Option("thaipost", "📮 ไปรษณีย์ไทย (EMS)"),
                            ft.dropdown.Option("pet_move", "🐾 รถรับส่งสัตว์เลี้ยง"),
                        ])
                        # ถ้าค่าเดิมหลุดไปจากตัวเลือก ให้รีเซ็ตเป็น pickup
                        valid_values = ["pickup", "lalamove", "kerry", "flash", "thaipost", "pet_move"]
                        if dropdown_provider.value not in valid_values:
                             dropdown_provider.value = "pickup"

                    dropdown_provider.options = new_options
                    # ---------------------------------------------------------------------

                    # วนลูปแสดงสินค้า (ส่วนนี้เหมือนเดิม)
                    for item in cart_data:
                        item_total = item['price'] * item['qty']
                        subtotal += item_total
                        cart_content.append(ft.Container(
                            bgcolor="white", padding=10, border_radius=10, margin=ft.margin.only(bottom=5),
                            content=ft.Row([
                                ft.Image(
                                    src=f"{API_URL}/uploads/{item['image'] if item.get('image') else 'no_image.jpg'}",
                                    width=50, 
                                    height=50, 
                                    fit=ft.ImageFit.CONTAIN,
                                    border_radius=5,
                                    error_content=ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED, color="grey")
                                ),
                                ft.Column([
                                    ft.Text(item['name'], weight="bold"),
                                    ft.Text(f"{item['price']} x {item['qty']} = {item_total:,.0f} บ.", size=12, color="grey")
                                ], expand=True),
                                ft.Text(f"x{item['qty']}", weight="bold")
                            ])
                        ))
                    
                    # คำนวณยอดเงิน
                    calculate_totals_logic()

                    # (ส่วนล่าง UI Components... เหมือนเดิมยาวลงไปจนจบ)
                    # ใส่ส่วนประกอบอื่นๆ ลงหน้าจอ
                    cart_content.extend([
                        ft.Divider(height=20, thickness=1),
                        
                        ft.Text("ข้อมูลจัดส่ง", weight="bold", size=18), 
                        ft.Container(height=10),
                        
                        # 1. ชื่อ
                        name_field,
                        ft.Container(height=10),
                        
                        # 2. ที่อยู่ (กล่องใหญ่)
                        address_field,
                        ft.Container(height=10),
                        
                        # 3. เลือกขนส่ง (ตอนนี้ Options ถูกกรองมาแล้ว!)
                        dropdown_provider,
                        ft.Container(height=10),

                        # 4. รหัสไปรษณีย์
                        txt_zipcode,
                        
                        ft.Container(height=20),

                        # ส่วนชำระเงิน
                        ft.Text("ชำระเงิน", weight="bold"),
                        bank_info_ui,
                        ft.Container(height=10),

                        # ส่วนแนบสลิป
                        ft.Text("หลักฐานการโอน", weight="bold"), 
                        upload_ui,
                        ft.Container(height=20),
                        
                        # ส่วนแสดงราคารวม
                        ft.Container(
                            content=summary_text, 
                            bgcolor="white", 
                            padding=15, 
                            border_radius=10, 
                            border=ft.border.all(1, "#E0E0E0")
                        ),
                        
                        ft.Container(height=20),
                        
                        # ปุ่มกดด้านล่าง
                        ft.Row([
                            ft.ElevatedButton("ลบตะกร้า", bgcolor="red", color="white", 
                                              on_click=lambda e: (api_bg('POST', '/api/cart/clear',{'user': current_user['name']}), page.go("/shop"))), 
                            ft.Container(content=confirm_btn, expand=True)
                        ])
                    ])
                    
            except Exception as ex: 
                print(f"Cart Error: {ex}")
                cart_content.append(ft.Text(f"Error Loading Cart: {ex}", color="red"))

            # เพิ่ม View เข้า Page
            page.views.append(ft.View("/cart", [
                ft.AppBar(
                    title=ft.Text("ชำระเงิน"), 
                    bgcolor=my_theme_color, 
                    color=my_text_color, 
                    leading=ft.IconButton(icon="arrow_back", icon_color=my_text_color, on_click=lambda _: page.go("/shop"))
                ),
                ft.Container(
                    content=ft.Column(cart_content, scroll="auto"), 
                    expand=True, 
                    padding=15
                )
            ], bgcolor=page.bgcolor))

        # --- หน้า SUCCESS ---
        if page.route == "/success":
            page.views.append(ft.View("/success", [
                ft.Container(expand=True, bgcolor="white", alignment=ft.alignment.center, content=ft.Column([
                    ft.Icon("check_circle", color="green", size=100),
                    ft.Text("สั่งซื้อสำเร็จ!", size=24, weight="bold"),
                    ft.ElevatedButton("กลับหน้าหลัก", on_click=lambda _: page.go("/"))
                ], horizontal_alignment="center"))
            ]))

        # --- หน้า PROFILE ---
        # --- หน้า PROFILE (โค้ดใหม่: ประวัติการสั่งซื้อ) ---
        if page.route == "/profile":
            
            
            history_column = ft.Column(scroll="auto", spacing=10)

            # 2. ฟังก์ชันโหลดข้อมูล (ยิงไปหา api/my_orders แทน)
            def load_history():
                history_column.controls.clear() # ล้างของเก่าก่อน
                try:
                    res = requests.post(f'{API_URL}/api/my_orders', json={'name': current_user['name']})
                    history_data = res.json()

                    if not history_data:
                        history_column.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon("history", size=60, color="grey"),
                                    ft.Text("ยังไม่มีประวัติการสั่งซื้อ", color="grey"),
                                    ft.ElevatedButton("ไปช้อปปิ้งเลย", on_click=lambda _: page.go("/shop"))
                                ], horizontal_alignment="center"),
                                alignment=ft.alignment.center, padding=30
                            )
                        )
                    else:
                        for item in history_data:
                            # แกะข้อมูลสินค้า IT
                            p_name = item['product_name']
                            img_path = item['image']
                            warranty = item['warranty']
                            price = item['price']
                            qty = item['qty']
                            date = item.get('purchase_date', '-')
                            status = item.get('status', 'รอตรวจสอบ')

                            img_url = f"{API_URL}/uploads/{img_path}" if img_path else "https://via.placeholder.com/100"

                            # สร้างการ์ดแสดงผล
                            card = ft.Container(
                                bgcolor="white", padding=15, border_radius=15,
                                shadow=ft.BoxShadow(blur_radius=5, color="#10000000"),
                                content=ft.Row([
                                    # รูปสินค้า
                                    ft.Container(
                                        content=ft.Image(src=img_url, fit=ft.ImageFit.COVER), 
                                        width=80, height=80, border_radius=10, 
                                        border=ft.border.all(1, "#eee")
                                    ),
                                    # ข้อมูลสินค้า
                                    ft.Column([
                                        ft.Text(p_name, weight="bold", size=16, no_wrap=True),
                                        ft.Row([
                                            ft.Icon("verified_user", size=14, color="blue"),
                                            ft.Text(f"ประกัน: {warranty}", size=12, color="blue"),
                                            ft.Text(f"| {date}", size=12, color="grey")
                                        ], spacing=5),
                                        ft.Row([
                                            ft.Text(f"{price:,.0f} x {qty} ชิ้น", size=14, weight="bold"),
                                            ft.Container(
                                                content=ft.Text(status, size=10, color="white"),
                                                bgcolor="green" if "จัดส่ง" in status else "orange",
                                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                                border_radius=10
                                            )
                                        ], alignment="spaceBetween", width=200)
                                    ], spacing=5, expand=True)
                                ])
                            )
                            history_column.controls.append(card)
                            
                except Exception as e:
                    history_column.controls.append(ft.Text(f"Error: {e}", color="red"))
                
                if page: page.update()

            # 3. เรียกโหลดข้อมูลทันที
            load_history()

            # 4. ปุ่ม Logout
            def logout(e): 
                clear_user_data()
                page.go("/login")

            # 5. จัดหน้าจอ
            page.views.append(ft.View("/profile", [
                ft.AppBar(
                    title=ft.Text("ข้อมูลส่วนตัว"), 
                    bgcolor=my_theme_color, 
                    color=my_text_color,
                    leading=ft.IconButton(icon="arrow_back", icon_color=my_text_color, on_click=lambda _: page.go("/"))
                ),
                ft.Container(
                    padding=20, 
                    content=ft.Column([
                        # ส่วนหัว Profile
                        ft.Container(
                            padding=20, bgcolor="white", border_radius=15,
                            shadow=ft.BoxShadow(blur_radius=10, color="#10000000"),
                            content=ft.Row([
                                ft.Icon("account_circle", size=60, color="blue"),
                                ft.Column([
                                    ft.Text(current_user["name"], size=22, weight="bold"),
                                    ft.Text(f"เบอร์โทร: {current_user['phone']}", color="grey")
                                ], alignment="center")
                            ])
                        ),
                        ft.Container(height=20),
                        
                        # ส่วนแสดงรายการ (ที่เปลี่ยนใหม่)
                        ft.Text("ประวัติการสั่งซื้อ 📦", size=18, weight="bold"), 
                        ft.Container(height=10),
                        history_column, 
                        
                        ft.Divider(height=30),
                        ft.Container(
                            content=ft.ElevatedButton("ออกจากระบบ", icon="logout", bgcolor="red", color="white", on_click=logout),
                            alignment=ft.alignment.center
                        )
                    ], scroll="auto")
                )
            ], bgcolor=page.bgcolor))
            
        # --- หน้า ADMIN DASHBOARD (แบบ 4 เมนู: แยกดูของ vs เพิ่มของ) ---
        # ======================================================================
        if page.route == "/admin":
            

                      # --- 1. หน้า "ออเดอร์" (Orders) ---
            orders_list = ft.Column(scroll="auto", expand=True)

            # ฟังก์ชันโหลดออเดอร์ (เรียกใช้เพื่อรีเฟรชหน้าจอ)
            def load_orders():
                orders_list.controls.clear()
                try:
                    res = requests.get(f'{API_URL}/api/orders')
                    orders_data = res.json()
                    
                    if not orders_data:
                        orders_list.controls.append(ft.Column([
                            ft.Icon("inbox", size=50, color="grey"), 
                            ft.Text("ยังไม่มีออเดอร์", color="grey")
                        ], alignment="center", horizontal_alignment="center"))
                    else:
                        for order in orders_data:
                            # เรียกใช้ create_order_card และส่ง handle_update_status เข้าไป
                            orders_list.controls.append(create_order_card(order, page, API_URL, handle_update_status, current_admin_name))
                except Exception as e:
                    orders_list.controls.append(ft.Text(f"Error loading orders: {e}", color="red"))
                if orders_list.page:
                    orders_list.update()

            # ฟังก์ชันกดปุ่มยืนยัน (กดแล้วจะสั่งให้โหลดหน้าจอใหม่ทันที)
            def handle_update_status(oid, status):
                try:
                    # 🔥 แก้ไขตรงนี้: เพิ่ม admin_name ส่งไปด้วย
                    payload = {
                        'order_id': oid, 
                        'status': status,
                        'admin_name': current_admin_name # <--- ส่งชื่อคนล็อกอินไปบันทึก
                    }

                    # ยิง API ไปอัปเดตสถานะ
                    res = requests.post(f'{API_URL}/api/orders/update', json=payload)
                    
                    if res.status_code == 200:
                        page.open(ft.SnackBar(ft.Text("อัปเดตเรียบร้อย!")))
                        
                        # --- 🛠️ รอ 0.2 วินาที ให้ Database หายใจทัน ---
                        time.sleep(0.2) 
                        # -----------------------------------------------------
                        
                        load_orders() 
                except Exception as ex:
                    print(f"Update Error: {ex}")

            # --- 2. หน้า "ดูคลังสินค้า" (Stock List) ---
            stock_list_container = ft.Column(scroll="auto", expand=True) # ตัวเก็บรายการสินค้า
            
            def load_stock_items():
                stock_list_container.controls.clear()
                try:
                    res = requests.get(f'{API_URL}/api/products')
                    products = res.json()
                    if not products:
                        stock_list_container.controls.append(ft.Column([ft.Icon("inventory_2", size=50, color="grey"), ft.Text("คลังสินค้าว่างเปล่า", color="grey")], alignment="center"))
                    else:
                        for p in products:
                            img_url = f"{API_URL}/uploads/{p['image']}" if p.get('image') else "https://via.placeholder.com/100"
                            stock_list_container.controls.append(
                                ft.Container(
                                    bgcolor="white", padding=10, border_radius=10, margin=ft.margin.only(bottom=5),
                                    shadow=ft.BoxShadow(blur_radius=2, color="#11000000"),
                                    content=ft.Row([
                                        ft.Image(src=img_url, width=60, height=60, fit=ft.ImageFit.COVER, border_radius=5),
                                        ft.Column([
                                        ft.Text(p['name'], weight="bold"),
                                        ft.Text(f"Stock: {p['stock']} | {p['price']:,} บ.", size=12, color="grey"),
                                        ft.Text(f"Code: {p.get('code','-')}", size=10, color="blue")
                                    ], expand=True),
                                    
                                    # 🔥🔥🔥 แก้ไขตรงนี้ครับ 🔥🔥🔥
                                    # เปลี่ยนจาก Icon เป็น IconButton เพื่อให้กดได้
                                    ft.IconButton(
                                        icon="edit", 
                                        icon_color="blue",
                                        tooltip="แก้ไขสินค้า",
                                        # เมื่อกด ให้ส่งข้อมูลสินค้า (p) ไปที่ฟังก์ชัน show_edit_dialog
                                        on_click=lambda e, x=p: show_edit_dialog(x) 
                                    )
                                    # -----------------------------
                                ])
                                )
                            )
                except Exception as e:
                    stock_list_container.controls.append(ft.Text(f"Error: {e}", color="red"))
                if page: page.update()

            def show_edit_dialog(product):
                # 1. สร้างช่องกรอกข้อมูล (เหมือนเดิม)
                txt_edit_name = ft.TextField(label="ชื่อสินค้า", value=product['name'], text_size=14)
                txt_edit_code = ft.TextField(label="รหัสสินค้า", value=product.get('code', ''), text_size=14)
                
                txt_edit_price = ft.TextField(label="ราคา", value=str(product['price']), keyboard_type="number", expand=True, text_size=14)
                txt_edit_stock = ft.TextField(label="สต็อก", value=str(product['stock']), keyboard_type="number", expand=True, text_size=14)
                
                # ตัวแปรเก็บรูปใหม่
                new_img_path = None
                img_status = ft.Text("ใช้รูปเดิม", size=12, color="grey")

                def on_edit_img_picked(e: ft.FilePickerResultEvent):
                    nonlocal new_img_path
                    if e.files:
                        new_img_path = e.files[0].path
                        img_status.value = f"เปลี่ยนเป็น: {e.files[0].name}"
                        img_status.color = "green"
                        img_status.update()

                edit_file_picker = ft.FilePicker(on_result=on_edit_img_picked)
                page.overlay.append(edit_file_picker)

                btn_change_img = ft.Container(
                    content=ft.Row([
                        ft.Icon("image", color="blue"),
                        ft.Text("เปลี่ยนรูปภาพสินค้า", color="blue"),
                        img_status
                    ]),
                    padding=10, 
                    border=ft.border.all(1, "blue"),
                    border_radius=10,
                    on_click=lambda _: edit_file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
                )

                # --- 🔥 ส่วนใหม่: ระบบลบสินค้าแบบมีรหัสผ่าน 🔥 ---
                
                # 1. สร้างหน้าต่างถามรหัสผ่าน
                txt_del_pass = ft.TextField(label="รหัสอนุมัติ (PIN)", password=True, text_align="center", autofocus=True)
                
                def confirm_delete_click(e):
                    # 🔑 กำหนดรหัสผ่านสำหรับลบตรงนี้ (เช่น 1234 หรือ admin)
                    if txt_del_pass.value == "1234": 
                        # รหัสถูก -> สั่งลบจริง
                        try:
                            res = requests.post(f"{API_URL}/api/products/delete", json={'id': product['id']})
                            if res.status_code == 200:
                                page.close(dlg_confirm) # ปิดหน้าถามรหัส
                                page.close(dlg_edit)    # ปิดหน้าแก้ไขสินค้า
                                
                                snack = ft.SnackBar(ft.Text("🗑️ ลบสินค้าเรียบร้อย!", color="white"), bgcolor="red")
                                page.overlay.append(snack); snack.open = True; page.update()
                                
                                load_stock_items() # โหลดรายการใหม่
                            else:
                                print(f"Delete failed: {res.text}")
                        except Exception as ex: print(f"Error: {ex}")
                    else:
                        # รหัสผิด -> แจ้งเตือน
                        txt_del_pass.error_text = "รหัสผ่านไม่ถูกต้อง!"
                        txt_del_pass.update()

                dlg_confirm = ft.AlertDialog(
                    title=ft.Text("⚠️ ยืนยันการลบ"),
                    content=ft.Column([
                        ft.Text("การลบสินค้าไม่สามารถกู้คืนได้", color="red"),
                        ft.Text("กรุณาใส่รหัสหัวหน้างานเพื่อยืนยัน:"),
                        txt_del_pass
                    ], height=120, tight=True),
                    actions=[
                        ft.TextButton("ยกเลิก", on_click=lambda e: page.close(dlg_confirm)),
                        ft.ElevatedButton("ยืนยันลบ", bgcolor="red", color="white", on_click=confirm_delete_click)
                    ]
                )

                # 2. ปุ่มลบ (ย้ายมาสร้างตรงนี้ เพื่อเอาไปใส่ในเนื้อหา)
                def open_confirm_dialog(e):
                    txt_del_pass.value = "" # ล้างรหัสเก่า
                    txt_del_pass.error_text = None
                    page.open(dlg_confirm)

                btn_delete_secure = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.DELETE_FOREVER, color="red"),
                        ft.Text("ลบสินค้านี้ (ต้องใช้รหัส)", color="red", weight="bold")
                    ], alignment="center"),
                    padding=10,
                    border=ft.border.all(1, "red"), # กรอบสีแดง
                    border_radius=10,
                    bgcolor=ft.colors.RED_50,       # พื้นหลังแดงอ่อนๆ
                    on_click=open_confirm_dialog,   # กดแล้วเปิดหน้าถามรหัส
                    margin=ft.margin.only(top=20)   # เว้นระยะห่างจากด้านบนเยอะๆ
                )

                # ----------------------------------------------------

                # ฟังก์ชันบันทึก (Save)
                def save_edit(e):
                    try:
                        payload = {
                            'id': product['id'],
                            'name': txt_edit_name.value,
                            'code': txt_edit_code.value,
                            'price': txt_edit_price.value,
                            'stock': txt_edit_stock.value
                        }
                        files = {'image': open(new_img_path, 'rb')} if new_img_path else {}
                        res = requests.post(f'{API_URL}/api/products/update', data=payload, files=files)
                        
                        if res.status_code == 200:
                            page.close(dlg_edit)
                            snack = ft.SnackBar(ft.Text("✅ แก้ไขสำเร็จ!"), bgcolor="green")
                            page.overlay.append(snack); snack.open = True; page.update()
                            load_stock_items()
                        else:
                            snack = ft.SnackBar(ft.Text("แก้ไขล้มเหลว"), bgcolor="red")
                            page.overlay.append(snack); snack.open = True; page.update()
                    except Exception as ex: print(f"Error: {ex}")

                # สร้าง Dialog หลัก
                dlg_edit = ft.AlertDialog(
                    title=ft.Text("แก้ไขข้อมูลสินค้า"),
                    content=ft.Column([
                        txt_edit_name,
                        txt_edit_code,
                        ft.Row([txt_edit_price, ft.Container(width=10), txt_edit_stock]),
                        ft.Container(height=10),
                        ft.Text("รูปภาพ:", size=14, weight="bold"),
                        btn_change_img,
                        
                        # 🔥 ใส่เส้นคั่น และ ปุ่มลบ ไว้ล่างสุด ตรงนี้!
                        ft.Divider(height=30, thickness=1),
                        btn_delete_secure 
                        
                    ], height=450, width=400, scroll="auto"),
                    
                    actions=[
                        # ปุ่ม Save/Cancel อยู่ด้านล่างเหมือนเดิม (แต่ไม่มีปุ่มลบแล้ว)
                        ft.TextButton("ยกเลิก", on_click=lambda e: page.close(dlg_edit)),
                        ft.ElevatedButton("บันทึก", bgcolor="blue", color="white", on_click=save_edit)
                    ],
                    actions_alignment="end" # จัดชิดขวา
                )
                page.open(dlg_edit)

            stock_view_page = ft.Container(padding=10, content=stock_list_container, expand=True)


            # --- 3. หน้า "เพิ่มสินค้า" (Add Product) [UPDATED] ---
            selected_product_path = None
            
            def on_product_img_picked(e: ft.FilePickerResultEvent):
                nonlocal selected_product_path
                if e.files:
                    selected_product_path = e.files[0].path
                    btn_upload.content = ft.Row([ft.Icon("check", color="white"), ft.Text("เลือกรูปแล้ว", color="white")], alignment="center")
                    btn_upload.bgcolor = "green"
                    btn_upload.update()
            
            product_picker = ft.FilePicker(on_result=on_product_img_picked)
            page.overlay.append(product_picker)

            # --- สร้างช่องกรอกข้อมูล ---
            txt_code = ft.TextField(label="รหัสสินค้า", prefix_icon="qr_code", text_size=14)
            txt_name = ft.TextField(label="ชื่อสินค้า", text_size=14)
            txt_price = ft.TextField(label="ราคา", keyboard_type="number", text_size=14)
            txt_stock = ft.TextField(label="จำนวน", value="1", keyboard_type="number", text_size=14)
            txt_unit = ft.TextField(label="หน่วยนับ", value="ชิ้น", text_size=14, width=100)
            txt_desc = ft.TextField(label="รายละเอียด", multiline=True, text_size=14)
            txt_brand = ft.TextField(label="รุ่น / แบรนด์ / ผู้ผลิต", icon=ft.icons.INFO_OUTLINE, text_size=14)
            txt_warranty = ft.TextField(label="การรับประกัน", icon=ft.icons.VERIFIED_USER, text_size=14)
            txt_video = ft.TextField(label="ลิงก์รีวิวสินค้า", icon=ft.icons.PLAY_CIRCLE, text_size=14)

            # 🔥 1. แก้ไข Dropdown ให้เป็นแบบ Dynamic (ไม่ต้อง Hardcode ตัวเลือก)
            dropdown_type = ft.Dropdown(
                label="รหัสประเภทสินค้า", 
                options=[], # เริ่มต้นเป็นค่าว่าง เดี๋ยวโหลดจาก Server
                text_size=14,
                prefix_icon=ft.icons.CATEGORY, 
                expand=True # สั่งให้ขยายเต็มความกว้าง (เพื่อแบ่งที่กับปุ่ม +)
            )

            # 🔥 แก้ไขฟังก์ชันโหลดหมวดหมู่
            def load_categories():
                try:
                    res = requests.get(f'{API_URL}/api/categories')
                    if res.status_code == 200:
                        cats = res.json()
                        dropdown_type.options = []
                        
                        for c in cats:
                            icon_name = c.get('icon', 'category')
                            # 🔥 ดึง Emoji จากตัวแปร Global
                            emoji = ALL_ICONS.get(icon_name, "📦")
                            
                            dropdown_type.options.append(
                                ft.dropdown.Option(
                                    key=c['code'], 
                                    text=f"{emoji}  {c['code']} : {c['name']}" 
                                )
                            )
                        dropdown_type.update()
                except Exception as ex:
                    print(f"Load Cat Error: {ex}")

            # 🔥 3. ฟังก์ชันเปิดหน้าต่าง "เพิ่มหมวดหมู่ใหม่"
            # --- แก้ไขฟังก์ชันจัดการหมวดหมู่ (ลบ icon=... ออก แล้วใช้ Emoji แทน) ---
            def open_add_cat_dialog(e):
                # 1. ส่วนกรอกข้อมูลเพิ่มใหม่
                txt_new_cat_code = ft.TextField(label="รหัสประเภท", autofocus=True, height=40, text_size=14, expand=True)
                txt_new_cat_name = ft.TextField(label="ชื่อประเภทสินค้า", height=40, text_size=14, expand=True)
                
                # 🔥 สร้างตัวเลือกไอคอนอัตโนมัติจาก ALL_ICONS
                icon_options = []
                for key, emoji in ALL_ICONS.items():
                    # สร้างตัวเลือก: 💻 computer
                    icon_options.append(ft.dropdown.Option(key, f"{emoji} {key}"))
                
                dd_icon_picker = ft.Dropdown(
                    label="เลือกไอคอน", options=icon_options, value="category", 
                    height=45, text_size=14, content_padding=5, prefix_icon="art_track"
                )

                # 🔥🔥 ส่วนเพิ่มใหม่: Dropdown เลือกขนาดค่าส่ง 🔥🔥
                dd_size_picker = ft.Dropdown(
                    label="รูปแบบการจัดส่ง (Shipping Class)",
                    options=[
                        ft.dropdown.Option("size_s", "📦 S - เล็ก/เบา (ค่าส่ง 20)"),
                        ft.dropdown.Option("size_m", "📦 M - กลาง (ค่าส่ง 50)"),
                        ft.dropdown.Option("size_l", "📦 L - ใหญ่ (ค่าส่ง 150)"),
                        ft.dropdown.Option("size_xl", "🚚 XL - หนักมาก/ปุ๋ย/อะไหล่รถ (ค่าส่ง 300)"),
                        
                        # 🔥 เพิ่ม 2 อันนี้ครับ สำหรับสัตว์เลี้ยง 🔥
                        ft.dropdown.Option("pet_small", "🐾 สัตว์เลี้ยงเล็ก (หนู/ปลา/นก) - (ค่าส่ง 500)"),
                        ft.dropdown.Option("pet_large", "🐕 สัตว์เลี้ยงใหญ่ (หมา/แมว) - (ค่าส่ง 1,500)"),
                    ],
                    value="size_s", 
                    height=45, text_size=14, content_padding=5,
                    prefix_icon="local_shipping"
                )

                # 2. ส่วนแสดงรายชื่อหมวดหมู่เดิม
                cats_list = ft.Column(scroll="auto", height=150) 

                # ฟังก์ชันสั่งลบ
                def delete_cat_action(code_to_del):
                    try:
                        requests.post(f'{API_URL}/api/categories/delete', json={'code': code_to_del})
                        load_cats_in_dialog()
                        load_categories()
                        
                        # (แก้ Deprecation Warning: snack_bar)
                        snack = ft.SnackBar(ft.Text(f"ลบ {code_to_del} เรียบร้อย"), bgcolor="red")
                        page.overlay.append(snack)
                        snack.open = True
                        page.update()
                    except Exception as ex: print(ex)

                def load_cats_in_dialog():
                    cats_list.controls.clear()
                    try:
                        res = requests.get(f'{API_URL}/api/categories')
                        if res.status_code == 200:
                            for c in res.json():
                                # 🔥 ดึง Emoji จากตัวแปร Global
                                emoji = ALL_ICONS.get(c.get('icon'), "📦")
                                
                                row = ft.Container(
                                    padding=5, border=ft.border.only(bottom=ft.border.BorderSide(1, "grey")),
                                    content=ft.Row([
                                        ft.Text(f"{emoji} {c['code']} : {c['name']}", size=12),
                                        # ... (ปุ่มลบ เหมือนเดิม) ...
                                        ft.IconButton(ft.icons.DELETE, icon_color="red", icon_size=18, 
                                                      on_click=lambda e, code=c['code']: delete_cat_action(code))
                                    ], alignment="spaceBetween")
                                )
                                cats_list.controls.append(row)
                        cats_list.update()
                    except: pass   

                def save_new_cat(e):
                    if not txt_new_cat_code.value or not txt_new_cat_name.value: return
                    try:
                        requests.post(f'{API_URL}/api/categories/add', json={
                            'code': txt_new_cat_code.value,
                            'name': txt_new_cat_name.value,
                            'icon': dd_icon_picker.value,
                            'shipping_size': dd_size_picker.value
                        })
                        txt_new_cat_code.value = ""
                        txt_new_cat_name.value = ""
                        txt_new_cat_code.update()
                        txt_new_cat_name.update()
                        
                        load_cats_in_dialog() 
                        load_categories() 
                        
                        # (แก้ Deprecation Warning)
                        snack = ft.SnackBar(ft.Text("✅ เพิ่มสำเร็จ!"), bgcolor="green")
                        page.overlay.append(snack)
                        snack.open = True
                        page.update()
                    except Exception as ex: print(ex)

                load_cats_in_dialog()

                dlg_cat = ft.AlertDialog(
                    title=ft.Text("จัดการประเภทสินค้า"),
                    content=ft.Container(
                        width=400, height=450,
                        content=ft.Column([
                            ft.Text("เพิ่มหมวดใหม่:", weight="bold"),
                            ft.Row([txt_new_cat_code, txt_new_cat_name]),
                            dd_icon_picker,
                            dd_size_picker,
                            ft.ElevatedButton("บันทึกเพิ่ม", bgcolor="green", color="white", width=400, on_click=save_new_cat),
                            ft.Divider(),
                            ft.Text("รายการที่มีอยู่ ():", weight="bold"),
                            cats_list
                        ])
                    ),
                    actions=[ft.TextButton("ปิดหน้าต่าง", on_click=lambda e: page.close(dlg_cat))]
                )
                page.open(dlg_cat)

            # 🔥 4. ปุ่มบวก (+)
            btn_add_cat = ft.Container(
                content=ft.Icon(ft.icons.ADD, color="white"),
                width=50, height=50,
                bgcolor="green",
                border_radius=10,
                on_click=open_add_cat_dialog,
                tooltip="เพิ่มรหัสประเภทใหม่"
            )

            btn_upload = ft.Container(
                content=ft.Row([ft.Icon("cloud_upload", color="blue"), ft.Text("รูปภาพ", color="blue")], alignment="center"),
                bgcolor="white", border=ft.border.all(1, "blue"), border_radius=10, padding=10,
                on_click=lambda _: product_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
            )

            def add_product_click(e):
                # 🔥 แก้ไข: ย้าย nonlocal มาไว้บรรทัดแรกสุด ตรงนี้ครับ!
                nonlocal selected_product_path 
                
                if not txt_name.value or not txt_price.value: return
                
                try:
                    data = {
                        'code': txt_code.value, 'name': txt_name.value, 'price': txt_price.value, 
                        'type': dropdown_type.value, 'stock': txt_stock.value, 'desc': txt_desc.value, 
                        'warranty': txt_warranty.value, 'brand': txt_brand.value, 'video_url': txt_video.value, 'unit': txt_unit.value
                    }
                    
                    # ตรงนี้มีการเรียกใช้ selected_product_path (ถ้าวาง nonlocal ไว้ข้างล่างจะ Error ตรงนี้)
                    files = {'image': open(selected_product_path, 'rb')} if selected_product_path else {}
                    
                    requests.post(f'{API_URL}/api/products/add', data=data, files=files)
                    
                    page.snack_bar = ft.SnackBar(ft.Text("เพิ่มสินค้าสำเร็จ!")); page.snack_bar.open = True
                    
                    # --- ล้างค่า (Reset) ---
                    txt_code.value = ""
                    txt_name.value = ""; txt_price.value = ""; txt_desc.value = ""; 
                    txt_stock.value = "1"
                    txt_warranty.value = ""; txt_brand.value = ""; txt_video.value = ""
                    dropdown_type.value = None 

                    # รีเซ็ตตัวแปรรูปภาพ
                    selected_product_path = None 
                    
                    # รีเซ็ตปุ่มอัปโหลด
                    btn_upload.bgcolor = "white"
                    btn_upload.content = ft.Row([ft.Icon("cloud_upload", color="blue"), ft.Text("รูปภาพ", color="blue")], alignment="center")
                    btn_upload.update()
                    
                    page.update()

                except Exception as ex: 
                    print(ex)
                    page.snack_bar = ft.SnackBar(ft.Text(f"เกิดข้อผิดพลาด: {ex}")); page.snack_bar.open = True
                    page.update()

            add_product_view = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("เพิ่มสินค้าใหม่", size=20, weight="bold"),
                    
                    # 1. แถวเลือกหมวดหมู่
                    ft.Row([
                        dropdown_type,
                        btn_add_cat
                    ]),
                    
                    # 2. รหัสสินค้า (แยกมาอยู่บรรทัดเดี่ยว เต็มความกว้าง)
                    txt_code,
                    
                    # 3. จำนวน และ หน่วยนับ (วางคู่กัน)
                    ft.Row([
                        # จำนวน (Stock)
                        ft.Container(content=txt_stock, expand=True),
                        
                        ft.Container(width=10), # ช่องว่างคั่นกลาง
                        
                        # หน่วยนับ (Unit) - ให้ขยายเต็มพื้นที่ที่เหลือ
                        ft.Container(content=txt_unit, expand=True) 
                    ]),

                    txt_name, 
                    txt_price, 
                    txt_desc,
                    ft.Divider(),
                    txt_brand,
                    txt_warranty,
                    txt_video,                   
                    ft.Divider(height=20),
                    ft.Row([ft.Text("รูปภาพ:", size=16), btn_upload]),
                    ft.Container(height=20),
                    ft.ElevatedButton("บันทึก", bgcolor="blue", color="white", width=400, height=50, on_click=add_product_click)
                ], scroll="auto")
            )

            # --- 4. หน้า "สมาชิก" (Members) ---
                  
            members_list = ft.Column(scroll="auto", expand=True)

            def load_members():
                members_list.controls.clear()
                try:
                    # ดึงข้อมูลจาก API (ที่เราเพิ่งเพิ่มใน server.py)
                    res = requests.get(f'{API_URL}/api/members')
                    members = res.json()
                    
                    if not members:
                        members_list.controls.append(ft.Column([
                            ft.Icon("person_off", size=50, color="grey"),
                            ft.Text("ยังไม่มีข้อมูลลูกค้า", color="grey")
                        ], alignment="center"))
                    else:
                        for m in members:
                            # สร้างการ์ดลูกค้า 1 คน
                            card = ft.Container(
                                bgcolor="white", padding=15, border_radius=10, margin=ft.margin.only(bottom=10),
                                shadow=ft.BoxShadow(blur_radius=2, color="#11000000"),
                                content=ft.Row([
                                    # ไอคอนคน
                                    ft.Container(
                                        content=ft.Icon("person", size=30, color="blue"),
                                        bgcolor="#E3F2FD", padding=10, border_radius=50
                                    ),
                                    # ชื่อและที่อยู่
                                    ft.Column([
                                        ft.Text(m['name'], weight="bold", size=16),
                                        ft.Text(f"ล่าสุด: {m['last_seen']}", size=12, color="grey"),
                                        ft.Text(m['address'][:30] + "..." if m['address'] else "-", size=12, color="grey", no_wrap=True),
                                    ], expand=True),
                                    # สรุปยอดเงิน
                                    ft.Column([
                                        ft.Text(f"{m['total_spent']:,.0f} ฿", weight="bold", color="green", size=16),
                                        ft.Text(f"{m['order_count']} ออเดอร์", size=12, color="black"),
                                    ], alignment="end", horizontal_alignment="end")
                                ])
                            )
                            members_list.controls.append(card)
                            
                except Exception as e:
                    members_list.controls.append(ft.Text(f"ยังไม่เชื่อมต่อ Server หรือ Error: {e}", color="red"))
                
                # เช็คว่าหน้าจอยังอยู่ไหมก่อนอัปเดต
                if members_list.page:
                    members_list.update()

            members_view = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Text("รายชื่อลูกค้า VIP", size=20, weight="bold"),
                        ft.IconButton(icon="refresh", on_click=lambda _: load_members())
                    ], alignment="spaceBetween"),
                    ft.Divider(),
                    members_list
                ], scroll="auto")
            )

            # ==========================================
            # 7. หน้า "รายงานผลประกอบการ" (กราฟแท่ง) 📊
            # ==========================================
            chart_container = ft.Container(expand=True)
            
            def load_chart(mode="daily"):
                try:
                    res = requests.get(f'{API_URL}/api/stats/{mode}')
                    data = res.json()
                    labels = data['labels']
                    values = data['values']

                    # 1. กำหนดสี
                    chart_color = "blue"
                    if mode == 'weekly': chart_color = "orange"
                    elif mode == 'monthly': chart_color = "green"

                    # 2. คำนวณแกน Y (สร้างขั้นบันได)
                    data_max = max(values) if values else 0
                    temp_max = data_max * 1.2 if data_max > 0 else 1000
                    if temp_max > 0:
                        digits = len(str(int(temp_max)))
                        power = 10 ** (digits - 1) 
                        # ปัดขึ้นให้หาร 5 ลงตัว (เช่น 72000 -> 80000)
                        max_y = math.ceil(temp_max / (power/2)) * (power/2)
                    else:
                        max_y = 1000
                    
                    y_labels = []
                    steps = 5 
                    step_val = max_y / steps
                    
                    for i in range(steps + 1):
                        val = i * step_val
                        # แปลงตัวเลขเป็น K (เช่น 10000 -> 10K)
                        if val >= 1000:
                            txt = f"{val/1000:.0f}K"
                        else:
                            txt = f"{val:.0f}"
                        
                        y_labels.append(
                            ft.ChartAxisLabel(value=val, label=ft.Text(txt, size=10, color="grey"))
                        )

                    # 3. สร้างแท่งกราฟ
                    chart_groups = []
                    for i, val in enumerate(values):
                        chart_groups.append(
                            ft.BarChartGroup(
                                x=i,
                                bar_rods=[
                                    ft.BarChartRod(
                                        from_y=0,
                                        to_y=val,
                                        width=20,
                                        color=chart_color,
                                        tooltip=f"{val:,.0f} THB",
                                        border_radius=5
                                    )
                                ]
                            )
                        )

                    # 4. สร้างป้ายกำกับแกน X
                    my_labels = [
                        ft.ChartAxisLabel(value=i, label=ft.Text(l[:3], size=10)) 
                        for i, l in enumerate(labels)
                    ]

                    # 5. สร้างตัวกราฟ
                    chart_view = ft.BarChart(
                        bar_groups=chart_groups,
                        border=ft.border.all(1, ft.colors.GREY_200),
                        
                        # ✅ ส่วนนี้ถูกต้องแล้วครับ ใส่ labels=y_labels เพื่อโชว์สเกลที่เราทำเอง
                        left_axis=ft.ChartAxis(
                            labels=y_labels,  
                            labels_size=40, 
                            title=ft.Text("บาท"), 
                            title_size=16
                        ),
                        
                        bottom_axis=ft.ChartAxis(labels=my_labels),
                        horizontal_grid_lines=ft.ChartGridLines(color=ft.colors.GREY_300, width=1, dash_pattern=[3, 3]),
                        tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
                        max_y=max_y,
                        expand=True
                    )
                    
                    chart_container.content = chart_view
                    if chart_container.page:
                        chart_container.update()

                except Exception as e:
                    print(f"Chart Error: {e}")
                    chart_container.content = ft.Text("ไม่สามารถโหลดกราฟได้")
                    if chart_container.page:
                        chart_container.update()
            
            # (ส่วน UI ปุ่มกดด้านล่างคงไว้เหมือนเดิม)
            stats_view = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("สรุปยอดขาย", size=24, weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("รายวัน", on_click=lambda _: load_chart("daily"), bgcolor="blue", color="white"),
                        ft.ElevatedButton("สัปดาห์", on_click=lambda _: load_chart("weekly"), bgcolor="orange", color="white"),
                        ft.ElevatedButton("รายเดือน", on_click=lambda _: load_chart("monthly"), bgcolor="green", color="white"),
                    ], alignment="center"),
                    ft.Divider(),
                    ft.Container(content=chart_container, height=400, border_radius=10, bgcolor="white", padding=10, shadow=ft.BoxShadow(blur_radius=10, color="#11000000"))
                ], scroll="auto")
            )
            
            

            # ==========================================
            # 6. หน้า "HR จัดการพนักงาน" (ใช้ตาราง users) 👔
            # ==========================================


            # 1. สร้างตัวแปร list รอไว้ก่อน
            hr_list = ft.Column(spacing=10, scroll="auto")

            # 2. ฟังก์ชันลบพนักงาน
            def delete_emp(eid):
                try:
                    requests.post(f'{API_URL}/api/employees/delete', json={'id': eid})
                    load_employees()
                except Exception as ex:
                    print(f"Delete Error: {ex}")

            # 3. ฟังก์ชันโหลดรายชื่อ (โชว์รูปจริง + กดดูรายละเอียดได้)
            def load_employees():
                hr_list.controls.clear() 
                try:
                    res = requests.get(f'{API_URL}/api/employees')
                    if res.status_code == 200:
                        employees = res.json()
                        for emp in employees:
                            # เตรียม URL รูปภาพ
                            img_name = emp.get('profile_image', 'default_avatar.png')
                            img_url = f"{API_URL}/assets/{img_name}"
                            
                            # ฟังก์ชันเปิด Popup ดูรายละเอียด (Closure)
                            def show_detail(e, employee_data=emp, image_url=img_url):
                                detail_dlg = ft.AlertDialog(
                                    title=ft.Text("ข้อมูลพนักงาน", size=20, weight="bold"),
                                    content=ft.Column([
                                        ft.Container(
                                            content=ft.CircleAvatar(
                                                foreground_image_url=image_url,
                                                radius=50,
                                            ), alignment=ft.alignment.center
                                        ),
                                        ft.Divider(),
                                        ft.Text(f"ชื่อ: {employee_data.get('display_name')}", size=18, weight="bold"),
                                        ft.Text(f"User: {employee_data.get('username')}", size=16),
                                        ft.Text(f"ตำแหน่ง: {employee_data.get('role')}", size=16, color="blue"),
                                        ft.Text(f"วุฒิ: {employee_data.get('education', '-')}", size=16),
                                        ft.Text(f"เงินเดือน: {employee_data.get('salary', 0):,} บาท", size=16, color="green", weight="bold"),
                                    ], height=350, width=400, scroll="auto"),
                                    actions=[ft.TextButton("ปิด", on_click=lambda _: page.close(detail_dlg))]
                                )
                                page.open(detail_dlg)

                            # สร้างการ์ดพนักงาน
                            card = ft.Container(
                                padding=10, bgcolor="white", border_radius=10,
                                content=ft.Row([
                                    # รูปโปรไฟล์ (CircleAvatar)
                                    ft.CircleAvatar(
                                        foreground_image_url=img_url,
                                        content=ft.Text(emp['display_name'][0]) if emp['display_name'] else ft.Icon(ft.icons.PERSON),
                                        radius=25
                                    ),
                                    # ชื่อและตำแหน่ง
                                    ft.Column([
                                        ft.Text(emp['display_name'], weight="bold", size=16),
                                        ft.Text(f"User: {emp['username']} | Role: {emp['role']}", size=12, color="grey")
                                    ], expand=True),
                                    # ปุ่มดูข้อมูล (i)
                                    ft.IconButton(ft.icons.INFO_OUTLINE, icon_color="blue", tooltip="ดูรายละเอียด", on_click=show_detail),
                                    # ปุ่มลบ
                                    ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e, eid=emp['id']: delete_emp(eid))
                                ], alignment="spaceBetween")
                            )
                            hr_list.controls.append(card)
                except Exception as ex:
                    print(f"Error: {ex}")
                    hr_list.controls.append(ft.Text(f"Error: {ex}", color="red"))
                
                if hr_list.page: hr_list.update()

            # 4. ฟังก์ชันเปิดหน้าต่างเพิ่มพนักงาน (เพิ่มช่อง วุฒิ + เงินเดือน)
            def add_emp_click(e):
                nonlocal emp_img_path
                emp_img_path = None # รีเซ็ตรูป
                if isinstance(emp_img_name, ft.Text):
                    emp_img_name.value = "ยังไม่ได้เลือกรูป"
                    emp_img_name.color = "grey"

                dlg_add_emp = ft.AlertDialog(
                    title=ft.Text("เพิ่มพนักงานใหม่"),
                    content=ft.Column([
                        ft.TextField(label="ชื่อ-นามสกุล", ref=(name_ref := ft.Ref())),
                        ft.TextField(label="รหัสพนักงาน (User)", ref=(user_ref := ft.Ref())),
                        ft.TextField(label="รหัสผ่าน (Pass)", password=True, ref=(pass_ref := ft.Ref())),
                        
                        # ✅ เพิ่ม 2 ช่องนี้เข้าไปครับ
                        ft.TextField(label="วุฒิการศึกษา", ref=(edu_ref := ft.Ref())),
                        ft.TextField(label="เงินเดือน", keyboard_type=ft.KeyboardType.NUMBER, ref=(salary_ref := ft.Ref())),

                        ft.Dropdown(
                            label="ตำแหน่ง", 
                            options=[
                                ft.dropdown.Option("admin", "แอดมิน"),
                                ft.dropdown.Option("hr", "HR"),
                                ft.dropdown.Option("manager", "ผู้จัดการ"),
                                ft.dropdown.Option("assistant", "รองผู้จัดการ"),
                                ft.dropdown.Option("staff", "พนักงานทั่วไป"),
                            ], value="staff", ref=(role_ref := ft.Ref())
                        ),
                        ft.Divider(),
                        ft.Row([
                            ft.ElevatedButton("📷 เลือกรูปโปรไฟล์", 
                                              on_click=lambda _: emp_file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)),
                            emp_img_name 
                        ])
                    ], height=500, scroll="auto"), # เพิ่มความสูงเป็น 500 และเปิด scroll
                    actions=[
                        # ส่ง edu_ref และ salary_ref ไปด้วย
                        ft.ElevatedButton("บันทึก", on_click=lambda e: submit_emp(dlg_add_emp, name_ref, user_ref, pass_ref, role_ref, edu_ref, salary_ref))
                    ]
                )
                page.open(dlg_add_emp)

            # 5. ฟังก์ชันบันทึก (รับค่า วุฒิ + เงินเดือน)
            def submit_emp(dlg, name, user, pw, role, edu, salary):
                nonlocal emp_img_path
                try:
                    form_data = {
                        'name': name.current.value,
                        'user': user.current.value,
                        'pass': pw.current.value,
                        'role': role.current.value,
                        # ✅ ดึงค่าจากช่องกรอกจริงๆ มาใส่
                        'education': edu.current.value if edu.current.value else '-',
                        'salary': salary.current.value if salary.current.value else 0
                    }

                    files = {}
                    if emp_img_path: files = {'image': open(emp_img_path, 'rb')}

                    res = requests.post(f'{API_URL}/api/employees/add', data=form_data, files=files)

                    if res.status_code == 200:
                        page.close(dlg)
                        page.snack_bar = ft.SnackBar(ft.Text("เพิ่มพนักงานสำเร็จ!"), bgcolor="green")
                        page.snack_bar.open = True
                        page.update()
                        emp_img_path = None
                        load_employees()
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("Error: ข้อมูลอาจซ้ำ หรือ Server มีปัญหา"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                except Exception as ex:
                    print(f"Error: {ex}")

            # 6. สร้างหน้าจอ HR View
            hr_view = ft.Container(padding=20, content=ft.Column([
                ft.Row([ft.Text("จัดการพนักงาน", size=20, weight="bold"), ft.IconButton("add_circle", icon_color="green", on_click=add_emp_click)], alignment="spaceBetween"),
                ft.Divider(),
                hr_list
            ], scroll="auto"))

            # 1. 📦 ประกาศตัวแปรเก็บค่า (Variables)
            # 1. ตัวแปรเก็บค่า (Variables)
            logo_path = None      
            path_top = None       
            path_promo = None     
            
            # ข้อความแสดงชื่อไฟล์โลโก้
            logo_text = ft.Text("", color="grey")
            
            # 2. ฟังก์ชันสร้างปุ่ม (Helper Function)
            def create_upload_btn(text, on_click_func):
                return ft.ElevatedButton(
                    text=text,
                    icon="cloud_upload",
                    height=45,
                    bgcolor=ft.colors.BLUE_50,
                    color="blue",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    # รับ event (e) แต่ไม่ใช้ ให้โยนทิ้งไปที่ _ แล้วเรียกฟังก์ชันที่เราส่งมา
                    on_click=lambda _: on_click_func() 
                )

            # 3. สร้างปุ่ม (Buttons)
            
            btn_logo = create_upload_btn("เลือกรูป logo (Home)", lambda: picker_logo.pick_files(allow_multiple=False))
            btn_top = create_upload_btn("เลือกรูปแบนเนอร์ (บน)", lambda: picker_top.pick_files())
            btn_promo = create_upload_btn("เลือกรูปโปรโมชั่น (ล่าง)", lambda: picker_promo.pick_files())

            # 4. ฟังก์ชัน Callback (ทำงานเมื่อเลือกไฟล์เสร็จ)
            
            def on_logo_picked(e: ft.FilePickerResultEvent):
                nonlocal logo_path
                if e.files:
                    logo_path = e.files[0].path
                    
                    # 🔥 เปลี่ยนปุ่มเป็นสีเขียว + ไอคอนติ๊กถูก
                    btn_logo.bgcolor = "green"
                    btn_logo.content = ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color="white"), 
                        ft.Text(f"เลือกไฟล์แล้ว", color="white", weight="bold")
                    ], alignment="center")
                    btn_logo.update()
                    
                    
            # 3.2 ฟังก์ชันเมื่อเลือก "แบนเนอร์บน" เสร็จ
            def on_top_picked(e: ft.FilePickerResultEvent):
                nonlocal path_top
                if e.files:
                    path_top = e.files[0].path
                    
                    # 🔥 เปลี่ยนปุ่มเป็นสีเขียว
                    btn_top.bgcolor = "green"
                    btn_top.content = ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color="white"), 
                        ft.Text("พร้อมอัปโหลด (Top)", color="white", weight="bold")
                    ], alignment="center")
                    btn_top.update()

            # 3.3 ฟังก์ชันเมื่อเลือก "แบนเนอร์ล่าง" เสร็จ
            def on_promo_picked(e: ft.FilePickerResultEvent):
                nonlocal path_promo
                if e.files:
                    path_promo = e.files[0].path
                    
                    # 🔥 เปลี่ยนปุ่มเป็นสีเขียว
                    btn_promo.bgcolor = "green"
                    btn_promo.content = ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color="white"), 
                        ft.Text("พร้อมอัปโหลด (Promo)", color="white", weight="bold")
                    ], alignment="center")
                    btn_promo.update()

            # 5. ตัวจัดการไฟล์ (FilePickers)
            picker_logo = ft.FilePicker(on_result=on_logo_picked)
            picker_top = ft.FilePicker(on_result=on_top_picked)
            picker_promo = ft.FilePicker(on_result=on_promo_picked)
            
            # เพิ่มลง Page overlay
            page.overlay.extend([picker_logo, picker_top, picker_promo])
            
            # ❌ ลบส่วนที่ซ้ำซ้อนด้านล่างทิ้งได้เลยครับ (btn_logo.on_click = ...) เพราะเราใส่ไปในข้อ 3 แล้ว

            # ==========================================
            # 4. 💾 ฟังก์ชันบันทึกข้อมูล (Save)
            # ==========================================
           
            def save_settings(e):
                current_btn = e.control 
                current_btn.content = ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2, color="white"),
                    ft.Text("กำลังอัปโหลด...", color="white")
                ], alignment="center")
                current_btn.disabled = True 
                current_btn.update()

                time.sleep(1.5)

                try:
                    files = {}
                    if path_top: files['banner_top'] = open(path_top, 'rb')
                    if path_promo: files['banner_promo'] = open(path_promo, 'rb')
                    if logo_path: files['shop_logo'] = open(logo_path, 'rb')
                    
                    # 🔥 เพิ่มบรรทัดนี้: เก็บค่า Zipcode ใส่ตัวแปร
                    data_payload = {
                        'zipcode': txt_shop_zipcode.value,
                        'bgcolor': dropdown_bgcolor.value,
                        'theme_color': dropdown_theme.value
                        } 

                    # 🔥 แก้ตรงนี้: ส่ง data_payload ไปด้วย พร้อมกับ files
                    requests.post(f'{API_URL}/api/settings/update', data=data_payload, files=files)
                    
                    page.snack_bar = ft.SnackBar(ft.Text("✅ บันทึกข้อมูลเรียบร้อย!"), bgcolor="green")
                        
                    # --- รีเซ็ตปุ่มทั้งหมดให้กลับมาเป็นค่าเริ่มต้น ---
                    btn_top.bgcolor = ft.colors.BLUE_50; btn_top.content = None
                    btn_promo.bgcolor = ft.colors.BLUE_50; btn_promo.content = None
                    btn_logo.bgcolor = ft.colors.BLUE_50; btn_logo.content = None
                    
                    btn_top.update(); btn_promo.update(); btn_logo.update()

                except Exception as ex:
                    print(ex)
                    page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {ex}"), bgcolor="red")

                page.snack_bar.open = True
                current_btn.content = None
                current_btn.text = "บันทึกทั้งหมด"
                current_btn.disabled = False
                current_btn.update()
                page.update()

            # ปุ่มบันทึกหลัก
            btn_save_all = ft.ElevatedButton(
                "บันทึกทั้งหมด", 
                bgcolor="blue", color="white", width=400, height=50, 
                on_click=save_settings 
            )

            # ==========================================
            # 5. 🖥️ จัดหน้าจอ (UI Layout)
            # ==========================================
            # 1. ประกาศตัวแปรช่องกรอกรหัสไปรษณีย์ 
            txt_shop_zipcode = ft.TextField(
                label="รหัสไปรษณีย์ร้าน (ต้นทาง)", 
                hint_text="เช่น 10280", 
                width=200, 
                prefix_icon="map",
                border_radius=10
            )

            icon_bg_preview = ft.Icon(name="color_lens", color="grey", size=24)
            icon_theme_preview = ft.Icon(name="palette", color="grey", size=24)

            dropdown_bgcolor = ft.Dropdown(
                label="ธีมสีพื้นหลังแอป (Background Color)",
                width=300,
                border_radius=10,
                prefix=icon_bg_preview,
                options=[
                    ft.dropdown.Option(c['code'], c['name']) for c in BG_COLORS
                ]
            )

            dropdown_theme = ft.Dropdown(
                label="สีหัวข้อแอป (AppBar Color)",
                width=300,
                border_radius=10,
                prefix=icon_theme_preview,
                options=[
                    ft.dropdown.Option(c['code'], c['name']) for c in THEME_COLORS
                ]
            )


            # ฟังก์ชันเปลี่ยนสีทันทีที่เลือก (Preview)
            def on_color_change(e):
                page.bgcolor = dropdown_bgcolor.value
                page.update()
            
            dropdown_bgcolor.on_change = on_color_change

            def update_preview_colors(e=None):
                # 1. เปลี่ยนสีไอคอนพื้นหลัง
                if dropdown_bgcolor.value:
                    icon_bg_preview.color = dropdown_bgcolor.value
                    icon_bg_preview.update()
                    
                    # (แถม) เปลี่ยนสีพื้นหลังแอปให้เห็นจริงๆ ด้วยเลยก็ได้
                    page.bgcolor = dropdown_bgcolor.value
                    page.update()

                # 2. เปลี่ยนสีไอคอนธีมบาร์
                if dropdown_theme.value:
                    icon_theme_preview.color = dropdown_theme.value
                    icon_theme_preview.update()
                    
                    # (แถม) เปลี่ยนสี AppBar ด้านบนให้เห็นด้วย
                    # (ต้องเข้าถึง AppBar ของหน้านี้... ซึ่งอาจจะซับซ้อน ถ้าเอาแค่ไอคอนก็พอครับ)

            # ผูกฟังก์ชันกับเหตุการณ์ on_change
            dropdown_bgcolor.on_change = update_preview_colors
            dropdown_theme.on_change = update_preview_colors

            def load_settings_data():
                try:
                    # ยิงไปขอข้อมูลจาก Server
                    res = requests.get(f'{API_URL}/api/settings')
                    
                    if res.status_code == 200:
                        d = res.json()
                        # ถ้ามีค่า shop_zipcode ส่งมา ให้เอาไปใส่ในช่อง
                        if d.get('shop_zipcode'):
                            txt_shop_zipcode.value = d['shop_zipcode']
                            txt_shop_zipcode.update() # ⚠️ สำคัญมาก! ต้องสั่ง update หน้าจอถึงจะเปลี่ยน
                        if d.get('app_bgcolor'):
                            dropdown_bgcolor.value = d['app_bgcolor'] 
                        if d.get('app_theme_color'):
                            dropdown_theme.value = d['app_theme_color']
                        update_preview_colors()
                        page.update()
                except Exception as ex:
                    print(f"Load Settings Error: {ex}")

            settings_view = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("จัดการหน้าร้านค้า 🎨", size=24, weight="bold"),
                    ft.Divider(),

                    ft.Text("🎨 ธีมสีของแอปพลิเคชัน", size=16, weight="bold"),
                    dropdown_bgcolor,
                    ft.Container(height=20),

                    dropdown_theme,     #--ธีม
                    ft.Container(height=20),

                    ft.Text("📍 ที่ตั้งร้านค้า (สำหรับคำนวณค่าส่ง)", size=16, weight="bold"),
                    txt_shop_zipcode,
                    ft.Container(height=20),
                    
                    # 🔥 ย้ายส่วนนี้ขึ้นมาเป็นอันดับ 1 (แก้เลขข้อเป็น 1.)
                    ft.Text("1. โลโก้ร้านค้า (Logo)", size=16, weight="bold"),
                    ft.Row([
                        btn_logo,
                        logo_text
                    ]),
                    ft.Container(height=10), # เพิ่มช่องว่างนิดนึงให้สวยงาม

                    # ⬇️ เลื่อนอันนี้ลงมาเป็นอันดับ 2
                    ft.Text("2. แบนเนอร์หลัก (Top)", size=16, weight="bold"),
                    btn_top,
                    ft.Container(height=10),

                    # ⬇️ เลื่อนอันนี้ลงมาเป็นอันดับ 3
                    ft.Text("3. แบนเนอร์โปรโมชั่น (Promo)", size=16, weight="bold"),
                    btn_promo,
                    ft.Container(height=10),
                    
                    ft.Divider(),
                    ft.Container(height=10),
                    
                    # ปุ่มบันทึกอยู่ล่างสุดเหมือนเดิม
                    btn_save_all
                ], scroll="auto") 
            )

            ALL_MENUS = [
                {
                    "id": "orders", "icon": "receipt_long", "label": "ออเดอร์",
                    "view": ft.Container(content=orders_list, padding=10), 
                    "loader": load_orders,
                    # ✅ รองผู้จัดการ ดูออเดอร์ได้
                    "roles": ["admin", "manager", "assistant", "staff"] 
                },
                {
                    "id": "stock", "icon": "inventory", "label": "ดูคลัง",
                    "view": stock_view_page,
                    "loader": load_stock_items,
                    # ✅ รองผู้จัดการ ดูสต็อกได้
                    "roles": ["admin", "manager", "assistant", "staff"]
                },
                {
                    "id": "add", "icon": "add_circle", "label": "เพิ่มของ",
                    "view": add_product_view,
                    "loader": load_categories, 
                    # ✅ รองผู้จัดการ เพิ่มของได้ (ช่วย Manager)
                    "roles": ["admin", "manager", "assistant"] 
                },
                {
                    "id": "members", "icon": "people", "label": "สมาชิก",
                    "view": members_view,
                    "loader": load_members,
                    # ✅ รองผู้จัดการ ดูลูกค้าได้
                    "roles": ["admin", "manager", "assistant", "staff"]
                },
                {
                    "id": "stats", "icon": "bar_chart", "label": "สถิติ",
                    "view": stats_view,
                    "loader": lambda: load_chart("daily"),
                    # ✅ รองผู้จัดการ ดูยอดขายได้ (เพื่อช่วยบริหาร)
                    "roles": ["admin", "manager", "assistant"] 
                },
                {
                    "id": "hr", "icon": "badge", "label": "HR",
                    "view": hr_view,
                    "loader": load_employees,
                    # ❌ รองผู้จัดการ ห้ามดูเงินเดือนคนอื่น
                    "roles": ["admin", "hr"] 
                },
                {
                    "id": "settings", "icon": "settings", "label": "ตั้งค่าร้าน",
                    "view": settings_view,
                    "loader": load_settings_data,
                    # ❌ รองผู้จัดการ ห้ามแก้ระบบร้าน
                    "roles": ["admin"] 
                }
            ]

            # 2. กรองเมนู: เลือกเฉพาะอันที่ User คนนี้มีสิทธิ์
            my_role = current_admin_role if current_admin_role else "staff" # ถ้า error ให้เป็น staff ไว้ก่อน
            
            allowed_menus = []
            for menu in ALL_MENUS:
                if my_role in menu['roles']:
                    allowed_menus.append(menu)

            # 3. สร้าง Destination สำหรับ NavigationBar
            nav_destinations = [
                ft.NavigationBarDestination(icon=m['icon'], label=m['label']) 
                for m in allowed_menus
            ]

            # 4. พื้นที่แสดงเนื้อหา (Content Area)
            # เริ่มต้นให้โชว์เมนูแรกสุดที่เขามีสิทธิ์
            initial_content = allowed_menus[0]['view'] if allowed_menus else ft.Text("ไม่มีสิทธิ์เข้าถึง")
            content_area = ft.Container(content=initial_content, expand=True)

            # โหลดข้อมูลของหน้าแรกทันที
            if allowed_menus:
                if allowed_menus[0].get('loader'):
                    allowed_menus[0]['loader']()

            # 5. ฟังก์ชันเปลี่ยนหน้า (Smart Tab Change)
            def change_tab(e):
                idx = e.control.selected_index
                if 0 <= idx < len(allowed_menus):
                    selected_menu = allowed_menus[idx]
                    
                    # เปลี่ยนเนื้อหา
                    content_area.content = selected_menu['view']
                    content_area.update()
                    
                    # เรียกฟังก์ชันโหลดข้อมูล (Refresh Data)
                    if selected_menu.get('loader'):
                        selected_menu['loader']()

            # 6. ประกอบร่างหน้า Admin
            page.views.append(ft.View("/admin", [
                ft.AppBar(
                    title=ft.Text(f"Dashboard ({my_role.upper()})"), # โชว์ตำแหน่งให้ดูเท่ๆ
                    bgcolor=my_theme_color, 
                    color=my_text_color, 
                    leading=ft.IconButton(icon="arrow_back", icon_color=my_text_color, on_click=lambda _: page.go("/login"))
                ),
                content_area,
                ft.NavigationBar(
                    destinations=nav_destinations,
                    on_change=change_tab,
                    selected_index=0 # รีเซ็ตให้เลือกอันแรกเสมอ
                )
            ], bgcolor="#f5f5f5"))

        page.update()

    def view_pop(view):
        page.views.pop()
        
        # เช็คว่ายังมีหน้าเหลือไหม?
        if len(page.views) > 0:
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            # ถ้าไม่เหลือหน้าไหนเลย ให้กลับไปหน้าแรก (Home)
            page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    load_user_data()
    page.go("/")



# แบบ Desktop (เพื่ออัปรูป)
ft.app(target=main, assets_dir="assets")
# เปิดโหมด Web เพื่อให้มือถือเข้ามาได้
#ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8000, host="192.168.1.37")