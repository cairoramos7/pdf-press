import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image

# --- THEME CONFIGURATION ---
COLOR_BG = "#0B1116"         # Fundo Principal (Deep Dark)
COLOR_SURFACE = "#151F28"    # Cards e Containers
COLOR_PRIMARY = "#00C2FF"    # Azul Ciano (Botões, Progresso)
COLOR_SUCCESS = "#00FF9D"    # Verde Neon
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_SUB = "#8A94A0"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class PdfPressApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        # Janela
        self.title("PDF Press")
        self.geometry("400x650") # Proporção Mobile-like do design
        self.configure(fg_color=COLOR_BG)
        self.resizable(False, False)

        # Variáveis de Estado
        self.selected_file = None
        self.gs_path = self.find_ghostscript()
        self.compress_task = None
        
        # Container Principal (troca de telas)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # Inicializar Telas
        self.show_home_screen()

        # Checagem inicial
        if not self.gs_path:
            messagebox.showwarning("Setup Required", "Ghostscript engine not found.\nPlease ensure 'gs' folder is present.")

    # --- NAVEGAÇÃO ---
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_home_screen(self):
        self.clear_container()
        
        # Header
        header = ctk.CTkFrame(self.container, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(header, text="⬇", font=("Arial", 20, "bold"), text_color=COLOR_PRIMARY).pack(side="left")
        ctk.CTkLabel(header, text="PDF Press", font=("Arial", 18, "bold"), text_color="white").pack(side="left", padx=10)
        
        # Config Button (Fake for visual fidelity)
        ctk.CTkLabel(header, text="⚙", font=("Arial", 20), text_color="white").pack(side="right")

        # Titles
        ctk.CTkLabel(self.container, text="Otimize seus PDFs", font=("Arial", 26, "bold"), text_color="white").pack(pady=(20, 5))
        ctk.CTkLabel(self.container, text="Reduza o tamanho do arquivo sem\nperder a qualidade de leitura", 
                     font=("Arial", 14), text_color=COLOR_TEXT_SUB).pack(pady=(0, 30))

        # Drop Zone
        self.drop_frame = ctk.CTkFrame(self.container, fg_color="transparent", border_width=2, border_color="#2A3B4C", corner_radius=20)
        self.drop_frame.pack(fill="x", padx=30, pady=10, ipady=40)
        
        # Drop Zone Content
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.drop_file)
        
        # Icon Background Circle
        icon_bg = ctk.CTkFrame(self.drop_frame, width=60, height=60, corner_radius=30, fg_color="#1A2733")
        icon_bg.pack(pady=(20, 15))
        ctk.CTkLabel(icon_bg, text="☁", font=("Arial", 30), text_color=COLOR_PRIMARY).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.drop_frame, text="Arraste seu arquivo PDF aqui", font=("Arial", 14, "bold"), text_color="white").pack()
        link = ctk.CTkLabel(self.drop_frame, text="Toque para selecionar", font=("Arial", 13), text_color=COLOR_PRIMARY, cursor="hand2")
        link.pack(pady=5)
        link.bind("<Button-1>", lambda e: self.select_file())
        
        # Separator
        sep_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        sep_frame.pack(fill="x", padx=40, pady=30)
        ctk.CTkFrame(sep_frame, height=1, fg_color="#2A3B4C").pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(sep_frame, text="OU", text_color=COLOR_TEXT_SUB, padx=10).pack(side="left")
        ctk.CTkFrame(sep_frame, height=1, fg_color="#2A3B4C").pack(side="right", fill="x", expand=True)

        # Secondary Button
        btn_folder = ctk.CTkButton(self.container, text=" Clique para buscar pastas", 
                                   fg_color=COLOR_SURFACE, hover_color="#1E2B36", 
                                   text_color="white", height=50, corner_radius=10,
                                   font=("Arial", 14),
                                   command=self.select_file)
        btn_folder.pack(fill="x", padx=30)

        # Footer
        ctk.CTkLabel(self.container, text="🛡 Compressão segura e local", font=("Arial", 12), text_color=COLOR_TEXT_SUB).pack(side="bottom", pady=20)


    def show_processing_screen(self):
        self.clear_container()

        # Header
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="PDF Press", font=("Arial", 16, "bold"), text_color="white").pack()
        
        # Cancel Button (Top Right)
        btn_cancel = ctk.CTkButton(header, text="Cancel", fg_color="transparent", width=40, hover=False, text_color=COLOR_TEXT_SUB, command=self.show_home_screen)
        btn_cancel.place(relx=1.0, rely=0.5, anchor="e")

        # Loader UI
        loader_container = ctk.CTkFrame(self.container, fg_color="transparent")
        loader_container.pack(expand=True)

        # Placeholder for circular loader (using Label for now)
        # In a real impl, we'd use a canvas or custom image
        circle_frame = ctk.CTkFrame(loader_container, width=120, height=120, corner_radius=60, border_width=4, border_color=COLOR_PRIMARY, fg_color="transparent")
        circle_frame.pack(pady=30)
        ctk.CTkLabel(circle_frame, text="📄", font=("Arial", 40)).place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(circle_frame, text="FAST\nMODE", font=("Arial", 10, "bold"), text_color=COLOR_PRIMARY).place(relx=0.5, rely=0.75, anchor="center")

        ctk.CTkLabel(self.container, text="Comprimindo...", font=("Arial", 24, "bold"), text_color="white").pack(pady=10)
        ctk.CTkLabel(self.container, text="Otimizando imagens e fontes para\nreduzir o tamanho do arquivo.", 
                    font=("Arial", 14), text_color=COLOR_TEXT_SUB).pack()

        # File Card
        card = ctk.CTkFrame(self.container, fg_color=COLOR_SURFACE, corner_radius=15, height=70)
        card.pack(fill="x", padx=30, pady=40)
        
        ctk.CTkLabel(card, text="📄", font=("Arial", 20)).place(x=20, y=20)
        ctk.CTkLabel(card, text=os.path.basename(self.selected_file)[:25] + "...", font=("Arial", 14, "bold"), text_color="white").place(x=60, y=15)
        self.lbl_size = ctk.CTkLabel(card, text="Calculando...", font=("Arial", 12), text_color=COLOR_TEXT_SUB)
        self.lbl_size.place(x=60, y=40)
        
        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.container, height=6, progress_color=COLOR_PRIMARY, fg_color="#1A2733")
        self.progress.pack(fill="x", padx=30)
        self.progress.set(0)
        self.progress.start()

        # Start Work
        self.start_compression_thread()

    def show_success_screen(self, original_size, new_size, output_path):
        self.clear_container()
        
        # Header
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(header, text="<", width=30, fg_color="transparent", text_color="white", font=("Arial", 20), command=self.show_home_screen).pack(side="left")
        ctk.CTkLabel(header, text="PDF Press", font=("Arial", 16, "bold"), text_color="white").pack(side="left", padx=100) # Centering hack

        # Success Icon
        icon_circle = ctk.CTkFrame(self.container, width=100, height=100, corner_radius=50, fg_color="#112520", border_width=2, border_color=COLOR_SUCCESS)
        icon_circle.pack(pady=(40, 20))
        ctk.CTkLabel(icon_circle, text="✔", font=("Arial", 40), text_color=COLOR_SUCCESS).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.container, text="Pronto!", font=("Arial", 32, "bold"), text_color="white").pack()
        
        # Calculation
        reduction = 0
        if original_size > 0:
            reduction = (1 - (new_size / original_size)) * 100
        
        ctk.CTkLabel(self.container, text=f"Seu PDF ficou {int(reduction)}% mais leve.", font=("Arial", 16), text_color=COLOR_TEXT_SUB).pack(pady=10)

        # Stats Card
        card = ctk.CTkFrame(self.container, fg_color=COLOR_SURFACE, corner_radius=15)
        card.pack(fill="x", padx=30, pady=30, ipady=15)
        
        ctk.CTkLabel(card, text=os.path.basename(output_path)[:25] + "...", font=("Arial", 14, "bold"), text_color="white").pack(pady=(15, 5))
        ctk.CTkLabel(card, text="Compressed just now", font=("Arial", 12), text_color=COLOR_TEXT_SUB).pack(pady=(0, 20))
        
        stats_row = ctk.CTkFrame(card, fg_color="transparent")
        stats_row.pack(fill="x", padx=20)
        
        # Col 1
        col1 = ctk.CTkFrame(stats_row, fg_color="transparent")
        col1.pack(side="left", expand=True)
        ctk.CTkLabel(col1, text="ORIGINAL", font=("Arial", 10, "bold"), text_color=COLOR_TEXT_SUB).pack()
        ctk.CTkLabel(col1, text=self.format_bytes(original_size), font=("Arial", 16, "bold"), text_color="white").pack()
        
        # Divider
        ctk.CTkFrame(stats_row, width=1, height=30, fg_color="#2A3B4C").pack(side="left")

        # Col 2
        col2 = ctk.CTkFrame(stats_row, fg_color="transparent")
        col2.pack(side="left", expand=True)
        ctk.CTkLabel(col2, text="NOVO", font=("Arial", 10, "bold"), text_color=COLOR_TEXT_SUB).pack()
        ctk.CTkLabel(col2, text=self.format_bytes(new_size), font=("Arial", 16, "bold"), text_color=COLOR_SUCCESS).pack()

        # Action Button
        ctk.CTkButton(self.container, text="📂  Abrir Pasta", 
                      fg_color=COLOR_PRIMARY, text_color="black", 
                      height=55, corner_radius=12, font=("Arial", 16, "bold"),
                      command=lambda: subprocess.run(f'explorer /select,"{output_path}"')).pack(fill="x", padx=30, pady=(20, 10))

        # Secondary Action
        ctk.CTkButton(self.container, text="Comprimir Outro", 
                      fg_color="transparent", text_color="white", 
                      hover=False, font=("Arial", 14),
                      command=self.show_home_screen).pack(pady=10)

    # --- LOGIC ---
    def find_ghostscript(self):
        local_gs = os.path.join(os.getcwd(), 'gs', 'bin', 'gswin64c.exe')
        if os.path.exists(local_gs): return local_gs
        import shutil
        return shutil.which("gswin64c")

    def drop_file(self, event):
        path = event.data
        if path.startswith('{') and path.endswith('}'): path = path[1:-1]
        self.process_selected_file(path)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path: self.process_selected_file(path)

    def process_selected_file(self, path):
        if not path.lower().endswith('.pdf'):
             messagebox.showerror("Error", "Invalid file format.")
             return
        self.selected_file = path
        self.show_processing_screen()

    def start_compression_thread(self):
        thread = threading.Thread(target=self.run_compression)
        thread.start()

    def run_compression(self):
        try:
            input_path = self.selected_file
            original_size = os.path.getsize(input_path)
            
            # Update UI text
            self.lbl_size.configure(text=f"{self.format_bytes(original_size)}")
            
            directory = os.path.dirname(input_path)
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(directory, f"{name}_compressed{ext}")

            cmd = [
                self.gs_path, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                "-dDetectDuplicateImages=true", "-dCompressFonts=true",
                "-dDownsampleColorImages=true", "-dColorImageResolution=150", 
                "-dDownsampleGrayImages=true", "-dGrayImageResolution=150",
                "-dDownsampleMonoImages=false", "-dNOPAUSE", "-dBATCH",
                f"-sOutputFile={output_path}", input_path
            ]
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)

            if process.returncode == 0:
                new_size = os.path.getsize(output_path)
                self.after(500, lambda: self.show_success_screen(original_size, new_size, output_path))
            else:
                self.after(0, lambda: messagebox.showerror("Error", "Compression failed."))
                self.after(0, self.show_home_screen)

        except Exception as e:
            print(e)
            self.after(0, self.show_home_screen)

    def format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.1f} {power_labels[n]}B"

if __name__ == "__main__":
    app = PdfPressApp()
    app.mainloop()
