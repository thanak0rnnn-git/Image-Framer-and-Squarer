# Image Resizer 1:1 (Windows) — v4
import os, ctypes, threading, queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import Tk, filedialog, Button, Label, Entry, StringVar, Radiobutton, IntVar, Checkbutton, BooleanVar, ttk, messagebox, Text, END, DISABLED, NORMAL, Scale, HORIZONTAL
from tkinter import font as tkfont
from PIL import Image, ImageOps, ImageColor, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
SUPPORTED_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")
def load_private_fonts(fonts_dir="fonts"):
    FR_PRIVATE = 0x10; added = 0
    if os.name == "nt" and os.path.isdir(fonts_dir):
        for f in os.listdir(fonts_dir):
            if f.lower().endswith(".ttf"):
                path = os.path.abspath(os.path.join(fonts_dir, f))
                try: 
                    res = ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0)
                    if res > 0: added += 1
                except Exception: pass
    return added
def prefer_anuphan(root):
    families = list(tkfont.families(root)); prefer_name=None
    for cand in ["Sarabun Bold","Sarabun Regular","Sarabun Medium"]:
        if cand in families: prefer_name=cand; break
    if prefer_name:
        tkfont.nametofont("TkDefaultFont").configure(family=prefer_name, size=10)
        tkfont.nametofont("TkTextFont").configure(family=prefer_name, size=10)
        tkfont.nametofont("TkHeadingFont").configure(family=prefer_name, size=10, weight="bold")
        tkfont.nametofont("TkMenuFont").configure(family=prefer_name, size=10)
        tkfont.nametofont("TkFixedFont").configure(family=prefer_name, size=10)
        ttk.Style().configure(".", font=(prefer_name,10))
def parse_hex_color(hex_code:str):
    try: return ImageColor.getrgb(hex_code.strip())
    except Exception: return (255,255,255)
def ensure_dir(path:str): os.makedirs(path, exist_ok=True)
def exif_transpose(img): 
    try: return ImageOps.exif_transpose(img)
    except Exception: return img
def contain_to_square(img,size,bg_rgb=(255,255,255)):
    img=exif_transpose(img.convert("RGBA"))
    scale=min(size/img.width,size/img.height)
    new_w=max(1,int(img.width*scale)); new_h=max(1,int(img.height*scale))
    resized=img.resize((new_w,new_h), Image.LANCZOS)
    canvas=Image.new("RGBA",(size,size), bg_rgb+(255,))
    offset=((size-new_w)//2,(size-new_h)//2); canvas.paste(resized, offset, resized); return canvas
def overlay_frame(canvas, frame_path):
    try: frame=Image.open(frame_path).convert("RGBA")
    except Exception: return canvas
    frame=frame.resize(canvas.size, Image.LANCZOS); canvas.alpha_composite(frame); return canvas
def save_force_format(img, save_base, fmt):
    fmt=fmt.lower()
    if fmt in ("jpeg","jpg"): save_path=save_base+".jpg"; img.convert("RGB").save(save_path, quality=90, optimize=True)
    elif fmt=="png": save_path=save_base+".png"; img.save(save_path, optimize=True)
    else: save_path=save_base+".webp"; img.save(save_path, quality=90, method=6)
    return save_path
def walk_images(root_dir):
    for root,_,files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXT): yield os.path.join(root,f)
class App:
    def __init__(self, master:Tk):
        self.master=master; master.title("Image Resizer 1:1 with Overlay (Windows) — v4"); master.geometry("880x640")
        self.input_var=StringVar(); self.output_var=StringVar(); self.color_hex_var=StringVar(value="#FFFFFF")
        self.size_var=IntVar(value=1000); self.format_var=StringVar(value="jpeg")
        import os as _os; self.workers_var=IntVar(value=max(1, (_os.cpu_count() or 4)//2))
        self.color_hex_var.trace_add("write", lambda *a: self.update_swatch())
        outer=ttk.Frame(master, padding=12); outer.pack(fill="both", expand=True)
        grid=ttk.Frame(outer); grid.pack(fill="both", expand=True); grid.columnconfigure(0,weight=1); grid.columnconfigure(1,weight=3)
        Label(grid,text="Input Folder").grid(row=0,column=0,sticky="w",pady=6)
        r0=ttk.Frame(grid); r0.grid(row=0,column=1,sticky="ew"); r0.columnconfigure(0,weight=1)
        Entry(r0,textvariable=self.input_var).grid(row=0,column=0,sticky="ew")
        ttk.Button(r0,text="Browse...",command=self.choose_input).grid(row=0,column=1,padx=6)
        ttk.Button(r0,text="Open",command=lambda:self.open_folder(self.input_var.get())).grid(row=0,column=2)
        Label(grid,text="Output Folder").grid(row=1,column=0,sticky="w",pady=6)
        r1=ttk.Frame(grid); r1.grid(row=1,column=1,sticky="ew"); r1.columnconfigure(0,weight=1)
        Entry(r1,textvariable=self.output_var).grid(row=0,column=0,sticky="ew")
        ttk.Button(r1,text="Browse...",command=self.choose_output).grid(row=0,column=1,padx=6)
        ttk.Button(r1,text="Open",command=lambda:self.open_folder(self.output_var.get())).grid(row=0,column=2)
        Label(grid,text="Canvas Size (1:1)").grid(row=2,column=0,sticky="w",pady=6)
        r2=ttk.Frame(grid); r2.grid(row=2,column=1,sticky="w")
        for i,(label,val) in enumerate([("500 x 500",500),("1000 x 1000",1000),("2048 x 2048",2048)]):
            Radiobutton(r2,text=label,variable=self.size_var,value=val).grid(row=0,column=i,padx=(0,14))
        Label(grid,text="Background Color (HEX)").grid(row=3,column=0,sticky="w",pady=6)
        r3=ttk.Frame(grid); r3.grid(row=3,column=1,sticky="w")
        self.hex_entry=Entry(r3,textvariable=self.color_hex_var,width=12); self.hex_entry.grid(row=0,column=0,padx=(0,8))
        ttk.Button(r3,text="Pick Color",command=self.pick_color).grid(row=0,column=1)
        self.swatch=ttk.Label(r3,text="    ",relief="groove",width=8); self.swatch.grid(row=0,column=2,padx=8); self.update_swatch()
        Label(grid,text="Frame File (รองรับสูงสุด 4 เฟรมพร้อมกัน แบบจตุรัส 1:1)").grid(row=4,column=0,sticky="nw",pady=(12,6))
        self.frame_enable_vars=[]; self.frame_path_vars=[]
        for idx in range(4):
            enable_var=BooleanVar(value=(idx==0)); path_var=StringVar()
            self.frame_enable_vars.append(enable_var); self.frame_path_vars.append(path_var)
            fr=ttk.Frame(grid); fr.grid(row=4+idx,column=1,sticky="ew",pady=2); fr.columnconfigure(1,weight=1)
            Checkbutton(fr,text=f"Frame {idx+1}",variable=enable_var).grid(row=0,column=0,sticky="w")
            Entry(fr,textvariable=path_var).grid(row=0,column=1,sticky="ew",padx=6)
            ttk.Button(fr,text="Choose Frame PNG",command=lambda i=idx:self.choose_frame(i)).grid(row=0,column=2)
        Label(grid,text="Output Format").grid(row=8,column=0,sticky="w",pady=6)
        r8=ttk.Frame(grid); r8.grid(row=8,column=1,sticky="w")
        for i,(label,val) in enumerate([("JPG","jpeg"),("WEBP","webp"),("PNG","png")]):
            Radiobutton(r8,text=label,variable=self.format_var,value=val).grid(row=0,column=i,padx=(0,14))
        Label(grid,text="Parallel Workers").grid(row=9,column=0,sticky="w",pady=6)
        r9w=ttk.Frame(grid); r9w.grid(row=9,column=1,sticky="w")
        import os as _os; maxw=max(1,(_os.cpu_count() or 4))
        self.workers_scale=Scale(r9w,from_=1,to=maxw,orient=HORIZONTAL,length=220,showvalue=False,command=lambda v:self.workers_var.set(int(float(v))))
        self.workers_scale.set(self.workers_var.get()); self.workers_scale.grid(row=0,column=0,padx=(0,8))
        self.workers_label=ttk.Label(r9w,text=f"{self.workers_var.get()} threads"); self.workers_label.grid(row=0,column=1)
        self.workers_var.trace_add("write",lambda *a:self.workers_label.config(text=f"{self.workers_var.get()} threads"))
        r10=ttk.Frame(grid); r10.grid(row=10,column=1,sticky="ew",pady=(10,6)); r10.columnconfigure(0,weight=1)
        self.progress=ttk.Progressbar(r10,orient="horizontal",mode="determinate"); self.progress.grid(row=0,column=0,sticky="ew")
        self.percent_label=ttk.Label(r10,text="0%"); self.percent_label.grid(row=0,column=1,padx=8)
        self.start_btn=ttk.Button(r10,text="Start",command=self.start_processing); self.start_btn.grid(row=0,column=2,padx=(8,0))
        self.cancel_btn=ttk.Button(r10,text="Cancel",command=self.cancel_processing,state=DISABLED); self.cancel_btn.grid(row=0,column=3)
        ttk.Label(grid,text="Tips: Frame ควรมีขนาดเท่ากับ Canvas Size",foreground="#555").grid(row=11,column=1,sticky="w",pady=(0,6))
        log_frame=ttk.Frame(outer,padding=(0,8,0,0)); log_frame.pack(fill="both",expand=True)
        Label(log_frame,text="Log").pack(anchor="w"); self.log=Text(log_frame,height=10); self.log.pack(fill="both",expand=True)
        self.queue=queue.Queue(); self.cancel_flag=threading.Event(); self.processing_thread=None
        self.master.after(100,self.poll_queue)
    def log_print(self,text):
        self.log.configure(state=NORMAL); self.log.insert(END,text+"\n"); self.log.see(END); self.log.configure(state=DISABLED)
    def update_swatch(self):
        color=self.color_hex_var.get()
        try: rgb=parse_hex_color(color); hex_color=f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except Exception: hex_color="#FFFFFF"
        style=ttk.Style(); style.configure("Color.TLabel", background=hex_color)
        if hasattr(self,"swatch"): self.swatch.configure(style="Color.TLabel")
    def pick_color(self):
        from tkinter.colorchooser import askcolor
        chosen=askcolor(color=self.color_hex_var.get())
        if chosen and chosen[1]: self.color_hex_var.set(chosen[1])
    def choose_input(self):
        folder=filedialog.askdirectory()
        if folder: self.input_var.set(folder)
    def choose_output(self):
        folder=filedialog.askdirectory()
        if folder: self.output_var.set(folder)
    def choose_frame(self,idx):
        path=filedialog.askopenfilename(filetypes=[("PNG images","*.png"),("All files","*.*")])
        if path: self.frame_path_vars[idx].set(path)
    def open_folder(self,path):
        if path and os.path.isdir(path):
            try: os.startfile(path)
            except Exception: messagebox.showerror("Error","เปิดโฟลเดอร์ไม่สำเร็จ")
        else: messagebox.showinfo("Info","ยังไม่ได้เลือกโฟลเดอร์")
    def start_processing(self):
        in_dir=self.input_var.get().strip(); out_dir=self.output_var.get().strip()
        if not in_dir or not os.path.isdir(in_dir): messagebox.showerror("Error","กรุณาเลือก Input Folder ที่ถูกต้อง"); return
        if not out_dir: messagebox.showerror("Error","กรุณาเลือก Output Folder"); return
        ensure_dir(out_dir)
        selected=[]
        for i in range(4):
            if self.frame_enable_vars[i].get():
                p=self.frame_path_vars[i].get().strip()
                if os.path.isfile(p):
                    base=os.path.splitext(os.path.basename(p))[0]
                    safe="".join(c if c.isalnum() or c in (' ','-','_') else "_" for c in base).strip()
                    selected.append((safe or f"Frame{i+1}", p))
        if not selected: messagebox.showerror("Error","กรุณาเลือกอย่างน้อย 1 เฟรม (ติ๊กถูก + เลือกไฟล์ PNG)"); return
        paths=list(walk_images(in_dir))
        if not paths: messagebox.showinfo("Info","ไม่พบไฟล์รูปภาพในโฟลเดอร์ที่เลือก"); return
        self.start_btn.configure(state=DISABLED); self.cancel_btn.configure(state=NORMAL)
        self.log.configure(state=NORMAL); self.log.delete("1.0",END); self.log.configure(state=DISABLED)
        self.progress["maximum"]=len(paths)*len(selected); self.progress["value"]=0; self.percent_label.config(text="0%")
        self.cancel_flag.clear()
        args=dict(in_dir=in_dir,out_dir=out_dir,paths=paths,frames=selected,size=self.size_var.get(),
                  bg=parse_hex_color(self.color_hex_var.get() or "#FFFFFF"), fmt=self.format_var.get(), workers=self.workers_var.get())
        self.processing_thread=threading.Thread(target=self._process_in_background, args=(args,)); self.processing_thread.daemon=True; self.processing_thread.start()
    def cancel_processing(self):
        self.cancel_flag.set(); self.log_print("⚠️ กำลังยกเลิกงาน... โปรดรอสักครู่")
    def _process_in_background(self,args):
        in_dir=args["in_dir"]; out_dir=args["out_dir"]; paths=args["paths"]; frames=args["frames"]
        size=args["size"]; bg=args["bg"]; fmt=args["fmt"]; workers=max(1,int(args["workers"]))
        self.queue.put(("log", f"เริ่มประมวลผล | Images: {len(paths)} | Frames: {len(frames)} | Size: {size} | Format: {fmt.upper()} | Workers: {workers}"))
        total=len(paths)*len(frames); completed=0
        def task(frame_tuple, src):
            if self.cancel_flag.is_set(): return ("cancel", None)
            subname, frame_path = frame_tuple
            rel=os.path.relpath(os.path.dirname(src), in_dir); save_dir=os.path.join(out_dir, subname, rel); ensure_dir(save_dir)
            filename_wo_ext=os.path.splitext(os.path.basename(src))[0]
            try:
                with Image.open(src) as im:
                    canvas=contain_to_square(im, size=size, bg_rgb=bg)
                    canvas=overlay_frame(canvas, frame_path)
                    save_base=os.path.join(save_dir, filename_wo_ext)
                    saved=save_force_format(canvas, save_base, fmt)
                return ("ok", saved)
            except Exception as e:
                return ("err", f"{src} :: {e}")
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures=[ex.submit(task, frame_tuple, src) for frame_tuple in frames for src in paths]
            for fut in as_completed(futures):
                status,payload=fut.result()
                if status=="cancel": break
                if status=="ok": self.queue.put(("log", f"✓ {payload}"))
                elif status=="err": self.queue.put(("log", f"✗ {payload}"))
                completed+=1; self.queue.put(("progress", completed/total))
        self.queue.put(("done", None))
    def poll_queue(self):
        try:
            while True:
                msg,payload=self.queue.get_nowait()
                if msg=="log": self.log_print(payload)
                elif msg=="progress":
                    val=payload; self.progress["value"]=int(val*self.progress["maximum"]); self.percent_label.config(text=f"{int(val*100)}%")
                elif msg=="done":
                    self.start_btn.configure(state=NORMAL); self.cancel_btn.configure(state=DISABLED)
                    if self.cancel_flag.is_set(): messagebox.showinfo("Canceled","ยกเลิกงานแล้ว")
                    else: messagebox.showinfo("Success","เสร็จสมบูรณ์!")
        except queue.Empty: pass
        self.master.after(100, self.poll_queue)
def main():
    load_private_fonts(os.path.join(os.path.dirname(__file__),"fonts"))
    root=Tk()
    try: ttk.Style().theme_use("vista")
    except Exception: pass
    prefer_anuphan(root); App(root); root.mainloop()
if __name__=="__main__": main()
