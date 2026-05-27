# 🏪 POSitive Shop Manager & Delivery (Full Stack Application)

**POSitive Shop Manager** คือระบบบริหารจัดการหน้าร้าน (Point of Sale) และการจัดส่งสินค้าแบบครบวงจร ที่ถูกออกแบบมาเพื่อแก้ปัญหาการจัดการคลังสินค้า การคำนวณค่าจัดส่งที่ซับซ้อน และการดูยอดขายแบบ Real-time โปรเจกต์นี้แสดงให้เห็นถึงความเข้าใจในการออกแบบสถาปัตยกรรมซอฟต์แวร์แบบ Client-Server อย่างเป็นระบบ## หน้าตาแอปพลิเคชัน (Screenshots)

## หน้าตาแอปพลิเคชัน (Screenshots)

### 1. หน้าแรก Welcome & Login
<img src="Screenshot_25690527_211519.jpg" width="500">

### 2. หน้าจอ Dashboard ระบบจัดการหลังบ้าน
<img src="Screenshot_25690527_211528.jpg" width="500">

### 3. หน้าจัดการข้อมูลพนักงาน
<img src="Screenshot_25690527_211611.jpg" width="500">

### 4. ระบบเพิ่มสินค้าเข้าคลัง
<img src="Screenshot_25690527_211620.jpg" width="500">

### 5. แผงควบคุมและจัดการออเดอร์
<img src="Screenshot_25690527_211637.jpg" width="500">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-00A4EF?style=for-the-badge&logo=flutter&logoColor=white)

---

## 📱 ลองใช้งานแอปพลิเคชัน (Try it out!)
คุณสามารถดาวน์โหลดแอปพลิเคชันเวอร์ชัน Android ไปทดลองติดตั้งและใช้งานได้ทันที:
[![Download APK](https://img.shields.io/badge/Download_APK-Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/anusit-ops/positive-shop-manager/releases/download/v1.0.0/POS_test.apk)

---

## 🚀 ฟีเจอร์เด่น (Key Features)
โปรเจกต์นี้เป็นการพัฒนาระบบแบบ Full Stack ครอบคลุมการทำงานตั้งแต่หน้าบ้าน (Client) ไปจนถึงหลังบ้าน (Server):

### ⚙️ Backend (API & Database) - `server.py`
* **RESTful API Architecture:** พัฒนาด้วย Flask Framework โดยแยก Endpoint อย่างเป็นระเบียบ รองรับการทำ CRUD Operations (Create, Read, Update, Delete) สำหรับสินค้า, คำสั่งซื้อ และผู้ใช้งาน
* **Relational Database:** ออกแบบฐานข้อมูลด้วย SQLite มีการจัดการความสัมพันธ์ของตาราง (เช่น การ JOIN ข้อมูล Order และ Products) พร้อมระบบตัดสต็อกอัตโนมัติ
* **Secure File Handling:** ระบบจัดการการอัปโหลดไฟล์รูปภาพสินค้าและสลิปโอนเงิน โดยแยกเก็บใน Local Storage อย่างเป็นสัดส่วน
* **Dynamic Configuration:** ระบบตั้งค่าร้านค้าแบบยืดหยุ่น สามารถเปลี่ยนธีมสี โลโก้ และเรทค่าจัดส่งจากหน้า Admin โดยดึงข้อมูลจาก Database แบบ Real-time

### 🎨 Frontend (UI & UX) - `main.py`
* **Cross-Platform UI:** พัฒนาส่วนแสดงผลด้วย Flet Framework ทำให้โค้ดชุดเดียวสามารถรันได้ทั้งบน Web, Desktop และ Mobile
* **Role-Based Access Control (RBAC):** ระบบจำกัดสิทธิ์ผู้ใช้งานที่รัดกุม แบ่งเป็นระดับ Admin, Manager, HR, Staff และ Customer โดยแต่ละสิทธิ์จะเห็นเมนูการทำงานที่แตกต่างกัน
* **Smart Shipping Algorithm:** โลจิกคำนวณค่าจัดส่งอัตโนมัติสุดอัจฉริยะ อ้างอิงจากรหัสไปรษณีย์ปลายทาง ผสมผสานกับน้ำหนักและขนาดของสินค้า (Size S, M, L, XL และหมวดหมู่พิเศษ)
* **Interactive Dashboard:** หน้าต่างสรุปสถิติยอดขาย (Sales Analytics) ที่เข้าใจง่าย สำหรับผู้บริหาร

---

## 🛠 วิธีการติดตั้งและรันโปรเจกต์ (Installation Guide)
สำหรับผู้ที่ต้องการนำ Source Code ไปรันบนเครื่อง Local:

1. **Clone repository:**
   ```bash
   git clone [https://github.com/anusit-ops/positive-shop-manager.git](https://github.com/anusit-ops/positive-shop-manager.git)
   cd positive-shop-manager
