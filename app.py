import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

# Configurações do CustomTkinter
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PdfPressApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        # Configuração da Janela
        self.title("PDF Press")
        self.geometry("600x450")
        self.iconbitmap(default='') # ToDo: Adicionar ícone .ico depois se houver
        
        # Layout Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Variáveis de Estado
        self.selected_file = None
        self.gs_path = self.find_ghostscript()

        # Frame Principal (Área de Drop)
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Configurar Drag and Drop no Frame
        self.main_frame.drop_target_register(DND_FILES)
        self.main_frame.dnd_bind('<<Drop>>', self.drop_file)

        # Conteúdo do Frame Principal
        self.label_icon = ctk.CTkLabel(self.main_frame, text="📄", font=("Arial", 64))
        self.label_icon.grid(row=0, column=0, pady=(40, 10))

        self.label_info = ctk.CTkLabel(self.main_frame, text="Arraste seu PDF aqui\nou clique para selecionar", font=("Arial", 18))
        self.label_info.grid(row=1, column=0, pady=10)

        # Tornar o label e frame clicáveis também
        self.label_info.bind("<Button-1>", lambda e: self.select_file())
        self.label_icon.bind("<Button-1>", lambda e: self.select_file())
        self.main_frame.bind("<Button-1>", lambda e: self.select_file())

        # Botão de Ação (Inicialmente Desabilitado)
        self.btn_compress = ctk.CTkButton(self, text="Comprimir PDF", command=self.start_compression, state="disabled", height=50, font=("Arial", 16, "bold"))
        self.btn_compress.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Barra de Status
        self.status_label = ctk.CTkLabel(self, text="Pronto", font=("Arial", 12), text_color="gray")
        self.status_label.grid(row=2, column=0, pady=(0, 10))

        # Aviso sobre Ghostscript se não encontrado
        if not self.gs_path:
            messagebox.showwarning("Aviso", "Ghostscript não encontrado!\nO aplicativo precisa do Ghostscript para funcionar.\n\nPor favor, instale-o ou coloque a pasta 'gs' junto ao executável.")
            self.status_label.configure(text="Erro: Ghostscript não encontrado", text_color="red")

    def find_ghostscript(self):
        """Tenta localizar o binário do gswin64c.exe:
           1. Na pasta local ./gs/bin/
           2. No PATH do sistema
        """
        # 1. Verifica pasta local (Portable mode)
        local_gs = os.path.join(os.getcwd(), 'gs', 'bin', 'gswin64c.exe')
        if os.path.exists(local_gs):
            return local_gs
        
        # 2. Tenta o comando do sistema
        import shutil
        sys_gs = shutil.which("gswin64c")
        if sys_gs:
            return sys_gs
        
        # 3. Fallback comum de instalação (opcional, pode ajudar)
        common_paths = [
            r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe", # Exemplo
        ]
        # Uma busca mais genérica poderia ser feita aqui se necessário
        
        return None

    def drop_file(self, event):
        file_path = event.data
        # TkinterDnD às vezes retorna caminhos entre chaves { } se houver espaços
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
            
        self.process_selected_file(file_path)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.process_selected_file(file_path)

    def process_selected_file(self, file_path):
        if not file_path.lower().endswith('.pdf'):
            messagebox.showerror("Erro", "Por favor, selecione um arquivo PDF válido.")
            return

        self.selected_file = file_path
        self.label_info.configure(text=f"Selecionado:\n{os.path.basename(file_path)}")
        self.label_icon.configure(text="✅", text_color="green")
        self.status_label.configure(text="Arquivo carregado. Pronto para comprimir.")
        
        if self.gs_path:
            self.btn_compress.configure(state="normal")
        else:
             self.status_label.configure(text="Erro: Ghostscript não configurado", text_color="red")

    def start_compression(self):
        if not self.selected_file or not self.gs_path:
            return

        self.btn_compress.configure(state="disabled", text="Comprimindo...")
        self.status_label.configure(text="Processando... Isso pode levar alguns segundos.")
        
        # Rodar em thread separada para não travar a UI
        thread = threading.Thread(target=self.run_ghostscript)
        thread.start()

    def run_ghostscript(self):
        try:
            input_file = self.selected_file
            directory = os.path.dirname(input_file)
            filename = os.path.basename(input_file)
            name, ext = os.path.splitext(filename)
            output_file = os.path.join(directory, f"{name}_compressed{ext}")

            # Comando fornecido pelo usuário
            # gswin64c -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 ...
            
            cmd = [
                self.gs_path,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dDetectDuplicateImages=true",
                "-dCompressFonts=true",
                "-dDownsampleColorImages=true",
                "-dColorImageResolution=180",
                "-dDownsampleGrayImages=true",
                "-dGrayImageResolution=180",
                "-dDownsampleMonoImages=false",
                "-dNOPAUSE",
                "-dBATCH",
                f"-sOutputFile={output_file}",
                input_file
            ]

            # No windows, subprocess.CREATE_NO_WINDOW esconde o terminal do GS
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)

            if process.returncode == 0:
                self.after(0, lambda: self.compression_success(output_file))
            else:
                error_msg = process.stderr.decode('utf-8', errors='ignore')
                self.after(0, lambda: self.compression_error(error_msg))

        except Exception as e:
            self.after(0, lambda: self.compression_error(str(e)))

    def compression_success(self, output_file):
        self.btn_compress.configure(state="normal", text="Comprimir PDF")
        self.status_label.configure(text="Concluído com sucesso!", text_color="green")
        
        resposta = messagebox.askyesno("Sucesso", f"Compressão concluída!\nSalvo em: {os.path.basename(output_file)}\n\nDeseja abrir a pasta?")
        if resposta:
            # Abrir explorer com o arquivo selecionado
            subprocess.run(f'explorer /select,"{output_file}"')
            
        # Resetar UI (Opcional, ou manter o arquivo para comprimir de novo se quiser)
        # self.reset_ui()

    def compression_error(self, error_msg):
        self.btn_compress.configure(state="normal", text="Comprimir PDF")
        self.status_label.configure(text="Erro na compressão.", text_color="red")
        messagebox.showerror("Erro de Compressão", f"Ocorreu um erro ao processar o PDF:\n{error_msg}")

if __name__ == "__main__":
    app = PdfPressApp()
    app.mainloop()
