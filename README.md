# 📦 Image-Framer-and-Squarer
Resize images to **1:1 square ratio (contain)**, add background color, and overlay frame (PNG).  
Supports **JPG / PNG / WebP** and customizable **workers** for performance tuning.
**[Co-Generated with GPT-5]**
---
## ⚡ TL;DR (For Thai)
* โปรแกรมนี้ใช้ปรับขนาดรูปภาพให้เป็น สี่เหลี่ยมจัตุรัส (1:1) เติมสีพื้นหลัง + ใส่เฟรม (PNG) ไดเเท่าที่ต้องดาร
* รองรับ JPG / PNG / WebP
* เลือกจำนวน Workers (เธรด) ได้ เพื่อปรับความเร็วตามสเปกเครื่อง
* ถ้าไม่มี Python → โหลด .exe (Windows) หรือ .app (macOS) ใน Release ไปเปิดใช้ได้เลย 🎉
* ถ้ามี Python, อยากโมเพิ่ม → pip install -r requirements.txt แล้วรัน python main.py
---
## 💻 Usage (without Python)
- Download the latest **`.exe` (Windows)** or **`.app` (macOS)** from the **Releases** section.
  (https://github.com/thanak0rnnn-git/Image-Framer-and-Squarer/releases/)
- Run it directly — no installation needed. 🎉
---
## 🔧 Installation (with Python)
1. Install [Python 3.x](https://www.python.org/downloads/) (skip if already installed).  
2. Download this repository as ZIP and extract.  
3. Open terminal in the project folder:  
   ```bash
   cd /path/to/project
   ```  
4. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage (with Python)
```bash
python main.py
```
or
```bash
py main.py   # on Windows
```

---

## 👨‍💻 For Developers (Build)
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build executable:

   **Windows:**
   ```bash
   pyinstaller --noconsole --onefile --name ImageResizer1x1 ^
     --add-data "fonts;fonts" main.py
   ```

   **macOS:**
   ```bash
   pyinstaller --windowed --onefile --name ImageResizer1x1 \
     --add-data "fonts:fonts" main.py
   ```

3. Output will be inside:
   ```
   dist/ImageResizer1x1(.exe/.app)
   ```

---
