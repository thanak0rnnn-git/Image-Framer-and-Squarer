# Image-Framer-and-Squarer
Image Framer / Resizer to 1:1 Ratio by Contain original width then add frame color as you want! (Support WebP,JPG,PNG) and Customize Worker Base on your Powers.

# How to install (with Python)
1. Install python on your devices (if exiest skip this)
2. Download as zip Files then Uncompress The file
3. Open terminal and cd /your-folder/ or open your folder in terminal
4. run pip install -r requirements.txt
5. finished
   
# How to use (after install)
1. Open terminal cd /your-folder/
2. run py main.py or python main.py
3. enter and start using

# How to use (without Python)
1. Download .exe or .app file in Release Section
2. Open file and Enjoy!

# For Developer
## Build .exe/.app files
1. open terminal and cd /your-folder/
2. run pip install pyinstaller
3. [for windows] run pyinstaller --noconsole --onefile --name ImageResizer1x1 ^ --add-data "fonts;fonts" main.py
4. [for mac] run pyinstaller --windowed --onefile --name ImageResizer1x1 \ --add-data "fonts:fonts" main.py
5. result are create in /your-folder/dist
