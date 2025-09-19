# 📦 Image-Framer-and-Squarer
Resize images to **1:1 square ratio (contain)**, add background color, and overlay frame (PNG).  
Supports **JPG / PNG / WebP** and customizable **workers** for performance tuning.

---
## 💻 Usage (without Python)
- Download the latest **`.exe` (Windows)** or **`.app` (macOS)** from the **Releases** section.  
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
