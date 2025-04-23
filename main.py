try:
    import keyboard
    import mouse
except ImportError:
    import pip

    pip.main(['install', 'keyboard', 'mouse'])
    import keyboard
    import mouse

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import time
import sys
import os
import json
from threading import Thread, Event


class AutoClickerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoClick V4 dev by jorgeRjunior")
        self.root.geometry("500x700")
        self.root.resizable(True, True)  # Permitir redimensionamento em todas as direções

        # Configurando estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5)
        self.style.configure("TRadiobutton", padding=5)

        # Variáveis de controle
        self.input_type = tk.StringVar(value="keyboard")
        self.input_type.trace('w', self.on_input_type_change)  # Adiciona callback para mudança
        self.mode = tk.StringVar(value="toggle")
        self.key = tk.StringVar()
        self.interval = tk.StringVar(value="100")
        self.status_text = tk.StringVar(value="Aguardando início...")

        # Estado do programa
        self.running = False
        self.stop_event = Event()
        
        # Custom mappings
        self.custom_mappings = []
        self.active_mappings = []
        self.custom_mapping_threads = []
        
        # Config file path
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autoclick_config.json")
        
        # Load saved configurations
        self.load_config()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Função Principal")
        
        # Create custom mappings tab
        self.custom_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.custom_tab, text="Funções Personalizadas")
        
        self.create_main_tab_widgets()
        self.create_custom_tab_widgets()

    def load_config(self):
        """Load configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.custom_mappings = config.get('custom_mappings', [])
        except Exception as e:
            print(f"Error loading config: {e}")
            self.custom_mappings = []

    def save_config(self):
        """Save configurations to file"""
        try:
            config = {
                'custom_mappings': self.custom_mappings
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")

    def on_input_type_change(self, *args):
        """Callback para quando o tipo de entrada muda"""
        if self.input_type.get() == "keyboard":
            self.key_entry.configure(state='normal')
        else:
            self.key_entry.configure(state='disabled')
            self.key.set('')  # Limpa o campo quando desabilitado

    def create_social_button(self, frame, icon_url, link, row, column):
        try:
            response = requests.get(icon_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((20, 20))
            photo = ImageTk.PhotoImage(img)

            button = tk.Button(
                frame,
                image=photo,
                command=lambda: webbrowser.open(link),
                cursor="hand2"
            )
            button.image = photo
            button.grid(row=row, column=column, padx=5)
        except:
            # Fallback para botão de texto se não conseguir carregar o ícone
            button = tk.Button(
                frame,
                text="GitHub" if "github" in icon_url else "Instagram",
                command=lambda: webbrowser.open(link),
                cursor="hand2"
            )
            button.grid(row=row, column=column, padx=5)

    def create_main_tab_widgets(self):
        # Frame principal
        main_frame = self.main_tab
        
        # Configurar o gerenciamento de geometria para permitir expansão horizontal
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="AutoClick V4", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=5)

        dev_label = ttk.Label(main_frame, text="dev by jorgeRjunior", font=("Helvetica", 10, "italic"))
        dev_label.grid(row=1, column=0, columnspan=2)

        # Social Media Frame
        social_frame = ttk.Frame(main_frame)
        social_frame.grid(row=2, column=0, columnspan=2, pady=5)

        # GitHub e Instagram icons/links
        self.create_social_button(
            social_frame,
            "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "https://github.com/jorgeRjunior",
            0, 0
        )
        self.create_social_button(
            social_frame,
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/2048px-Instagram_icon.png",
            "https://www.instagram.com/jorge.r.jr",
            0, 1
        )

        # Tipo de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Tipo de Entrada", padding=10)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Radiobutton(input_frame, text="Teclado", variable=self.input_type, value="keyboard").grid(row=0, column=0)
        ttk.Radiobutton(input_frame, text="Mouse 1 (Esquerdo)", variable=self.input_type, value="left").grid(row=0, column=1)
        ttk.Radiobutton(input_frame, text="Mouse 2 (Direito)", variable=self.input_type, value="right").grid(row=1, column=0)
        ttk.Radiobutton(input_frame, text="Mouse 4 (Lateral Frente)", variable=self.input_type, value="x2").grid(row=1, column=1)
        ttk.Radiobutton(input_frame, text="Mouse 5 (Lateral Trás)", variable=self.input_type, value="x1").grid(row=2, column=0, columnspan=2)

        # Tecla (quando teclado selecionado)
        key_frame = ttk.Frame(main_frame)
        key_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        key_frame.columnconfigure(1, weight=1)  # Permitir que o campo de entrada se expanda

        ttk.Label(key_frame, text="Tecla:").grid(row=0, column=0, padx=5)
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key, width=10)
        self.key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Configura o estado inicial do campo de tecla
        self.on_input_type_change()

        # Intervalo
        interval_frame = ttk.Frame(main_frame)
        interval_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        interval_frame.columnconfigure(1, weight=1)  # Permitir que o campo de entrada se expanda

        ttk.Label(interval_frame, text="Intervalo (ms):").grid(row=0, column=0, padx=5)
        ttk.Entry(interval_frame, textvariable=self.interval, width=10).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Modo de operação
        mode_frame = ttk.LabelFrame(main_frame, text="Modo de Operação", padding=10)
        mode_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Radiobutton(mode_frame, text="Segurar para repetir", variable=self.mode, value="hold").grid(row=0, column=0)
        ttk.Radiobutton(mode_frame, text="Alternar (Iniciar/Parar)", variable=self.mode, value="toggle").grid(row=0, column=1)

        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        status_frame.columnconfigure(0, weight=1)  # Permitir que o texto de status se expanda

        ttk.Label(status_frame, textvariable=self.status_text).grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Botões de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=8, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(control_frame, text="Iniciar", command=self.start_program)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.stop_program, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Informações
        info_text = """
Instruções:
- Mouse 1 = Botão esquerdo do mouse
- Mouse 2 = Botão direito do mouse
- Mouse 4 = Botão lateral da frente do mouse
- Mouse 5 = Botão lateral de trás do mouse
- Para teclas do teclado, digite a letra/tecla desejada
- O intervalo é o tempo entre as repetições
        """
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=9, column=0, columnspan=2, pady=10, sticky=(tk.W))

    def create_custom_tab_widgets(self):
        # Frame para a tab de funções personalizadas
        custom_frame = self.custom_tab
        
        # Configurar o gerenciamento de geometria para permitir expansão horizontal
        custom_frame.columnconfigure(0, weight=1)
        custom_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(custom_frame, text="Funções Personalizadas", font=("Helvetica", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Instruções
        instructions = ttk.Label(
            custom_frame, 
            text="Configure até 10 teclas ou botões de mouse para ativar repetições automatizadas.",
            wraplength=450
        )
        instructions.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Criar frame para os mapeamentos
        self.mappings_frame = ttk.Frame(custom_frame)
        self.mappings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configurar colunas para redimensionamento
        for i in range(6):
            self.mappings_frame.columnconfigure(i, weight=1)
        
        # Botões para adicionar/remover
        button_frame = ttk.Frame(custom_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Adicionar Nova Função", command=self.add_custom_mapping).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Salvar Configurações", command=self.save_config).grid(row=0, column=1, padx=5)
        
        # Status
        custom_status_frame = ttk.LabelFrame(custom_frame, text="Status das Funções Personalizadas", padding=10)
        custom_status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        custom_status_frame.columnconfigure(0, weight=1)
        
        self.custom_status_text = tk.StringVar(value="Sem funções ativas")
        ttk.Label(custom_status_frame, textvariable=self.custom_status_text).grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Botões para ativar/desativar todas as funções
        control_frame = ttk.Frame(custom_frame)
        control_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.activate_all_button = ttk.Button(control_frame, text="Ativar Todas", command=self.activate_all_mappings)
        self.activate_all_button.grid(row=0, column=0, padx=5)
        
        self.deactivate_all_button = ttk.Button(control_frame, text="Desativar Todas", command=self.deactivate_all_mappings)
        self.deactivate_all_button.grid(row=0, column=1, padx=5)
        
        # Refresh the mappings display
        self.refresh_mappings_display()
    
    def refresh_mappings_display(self):
        """Refresh the display of custom mappings"""
        # Clear existing widgets
        for widget in self.mappings_frame.winfo_children():
            widget.destroy()
            
        # Set column weights for proper resizing
        for i in range(6):
            self.mappings_frame.columnconfigure(i, weight=1)
            
        # Header
        ttk.Label(self.mappings_frame, text="Tecla Gatilho", width=15).grid(row=0, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Ação", width=15).grid(row=0, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Tipo", width=10).grid(row=0, column=2, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Intervalo (ms)", width=12).grid(row=0, column=3, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Modo", width=12).grid(row=0, column=4, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Ações", width=20).grid(row=0, column=5, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        separator = ttk.Separator(self.mappings_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        
        if not self.custom_mappings:
            # Mostrar mensagem quando não há mapeamentos configurados
            ttk.Label(
                self.mappings_frame, 
                text="Não há funções personalizadas configuradas. Clique em 'Adicionar Nova Função'.",
                font=("Helvetica", 9, "italic")
            ).grid(row=2, column=0, columnspan=6, padx=5, pady=10, sticky=(tk.W, tk.E))
            return
        
        # Display each mapping
        for i, mapping in enumerate(self.custom_mappings):
            ttk.Label(self.mappings_frame, text=mapping['trigger_key']).grid(row=i+2, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            # Exibir valor de ação adequado com base no tipo
            if mapping['action_type'] == 'keyboard':
                action_text = mapping['action_key']
            else:
                action_text = f"Mouse {mapping['action_type']}"
            ttk.Label(self.mappings_frame, text=action_text).grid(row=i+2, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            # Tipo formatado para melhor leitura
            type_display = {
                'keyboard': 'Teclado',
                'left': 'Mouse Esq.',
                'right': 'Mouse Dir.',
                'middle': 'Mouse Meio'
            }.get(mapping['action_type'], mapping['action_type'])
            ttk.Label(self.mappings_frame, text=type_display).grid(row=i+2, column=2, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            ttk.Label(self.mappings_frame, text=mapping['interval']).grid(row=i+2, column=3, padx=2, pady=2, sticky=(tk.W, tk.E))
            ttk.Label(self.mappings_frame, text="Uma vez" if mapping['once'] else "Contínuo").grid(row=i+2, column=4, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            # Container para os botões
            buttons_frame = ttk.Frame(self.mappings_frame)
            buttons_frame.grid(row=i+2, column=5, padx=2, pady=2, sticky=(tk.W, tk.E))
            buttons_frame.columnconfigure(0, weight=1)
            buttons_frame.columnconfigure(1, weight=1)
            
            # Botões de edição e exclusão
            ttk.Button(
                buttons_frame, 
                text="Editar", 
                width=8, 
                command=lambda idx=i: self.edit_mapping(idx)
            ).grid(row=0, column=0, padx=2)
            
            ttk.Button(
                buttons_frame, 
                text="Excluir", 
                width=8,
                command=lambda idx=i: self.delete_mapping(idx)
            ).grid(row=0, column=1, padx=2)
    
    def add_custom_mapping(self):
        """Add a new custom mapping"""
        if len(self.custom_mappings) >= 10:
            messagebox.showwarning("Limite atingido", "Você já atingiu o limite de 10 funções personalizadas.")
            return
            
        self.open_mapping_dialog()
    
    def edit_mapping(self, index):
        """Edit an existing mapping"""
        self.open_mapping_dialog(self.custom_mappings[index], index)
    
    def delete_mapping(self, index):
        """Delete a mapping"""
        if messagebox.askyesno("Confirmar exclusão", "Tem certeza que deseja excluir esta função?"):
            del self.custom_mappings[index]
            self.refresh_mappings_display()
            self.save_config()
            self.custom_status_text.set("Função personalizada excluída")
    
    def open_mapping_dialog(self, mapping=None, edit_index=None):
        """Open dialog to add or edit a mapping"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Nova Função" if mapping is None else "Editar Função")
        dialog.geometry("420x400")
        dialog.resizable(True, True)  # Permitir redimensionamento em todas as direções
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame para conteúdo
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scroll para o conteúdo
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        content_frame = ttk.Frame(canvas)
        
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configuração de expansão
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Variáveis para controle de captura de teclas
        is_capturing_trigger = False
        is_capturing_action = False
        
        # Tecla gatilho
        ttk.Label(content_frame, text="Tecla Gatilho:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        trigger_key_var = tk.StringVar(value=mapping['trigger_key'] if mapping else "")
        trigger_key_entry = ttk.Entry(content_frame, textvariable=trigger_key_var, width=15)
        trigger_key_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Botão para captura de tecla gatilho
        trigger_capture_button = ttk.Button(content_frame, text="Capturar")
        trigger_capture_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Botões de teste do mouse para gatilho
        mouse_trigger_frame = ttk.Frame(content_frame)
        mouse_trigger_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(mouse_trigger_frame, text="Mouse como gatilho:").pack(side=tk.LEFT, padx=(0, 5))
        for btn_name, btn_value in [("Esquerdo", "left"), ("Direito", "right"), ("Meio", "middle")]:
            btn = ttk.Button(
                mouse_trigger_frame, 
                text=btn_name,
                width=8,
                command=lambda v=btn_value: trigger_key_var.set(v)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Tipo de ação
        ttk.Label(content_frame, text="Tipo de Ação:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        action_type_var = tk.StringVar(value=mapping['action_type'] if mapping else "keyboard")
        
        action_type_frame = ttk.Frame(content_frame)
        action_type_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(action_type_frame, text="Teclado", variable=action_type_var, value="keyboard").pack(side=tk.LEFT)
        ttk.Radiobutton(action_type_frame, text="Mouse Esq.", variable=action_type_var, value="left").pack(side=tk.LEFT)
        ttk.Radiobutton(action_type_frame, text="Mouse Dir.", variable=action_type_var, value="right").pack(side=tk.LEFT)
        
        # Tecla de ação (para teclado)
        ttk.Label(content_frame, text="Tecla/Botão de Ação:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        action_key_var = tk.StringVar(value=mapping['action_key'] if mapping else "")
        action_key_entry = ttk.Entry(content_frame, textvariable=action_key_var, width=15)
        action_key_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Botão para captura de tecla de ação
        action_capture_button = ttk.Button(content_frame, text="Capturar")
        action_capture_button.grid(row=3, column=2, padx=5, pady=5)
        
        # Função para atualizar estado do campo de ação com base no tipo de ação
        def update_action_key_state(*args):
            if action_type_var.get() == "keyboard":
                action_key_entry.configure(state="normal")
                action_capture_button.configure(state="normal")
            else:
                action_key_entry.configure(state="disabled")
                action_capture_button.configure(state="disabled")
                action_key_var.set("")  # Limpa o campo quando desabilitado
        
        # Associar callback à variável de tipo de ação
        action_type_var.trace("w", update_action_key_state)
        
        # Aplicar estado inicial
        update_action_key_state()
        
        # Intervalo
        ttk.Label(content_frame, text="Intervalo (ms):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        interval_var = tk.StringVar(value=mapping['interval'] if mapping else "100")
        interval_entry = ttk.Entry(content_frame, textvariable=interval_var, width=15)
        interval_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Modo de repetição
        ttk.Label(content_frame, text="Modo de Repetição:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        once_var = tk.BooleanVar(value=mapping['once'] if mapping else False)
        
        mode_frame = ttk.Frame(content_frame)
        mode_frame.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Contínuo", variable=once_var, value=False).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Uma vez", variable=once_var, value=True).pack(side=tk.LEFT)
        
        # Status de captura
        capture_status_var = tk.StringVar(value="Clique nos campos ou botões de captura para registrar teclas...")
        capture_status = ttk.Label(content_frame, textvariable=capture_status_var, font=("Helvetica", 9, "italic"), wraplength=380)
        capture_status.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
        
        # Variáveis de controle para foco atual
        current_focus = None
        
        # Função para detectar quando um campo recebe foco
        def on_entry_focus_in(entry_type):
            nonlocal current_focus
            current_focus = entry_type
            if entry_type == "trigger":
                capture_status_var.set("Pressione uma tecla ou clique com o mouse para capturar...")
            elif entry_type == "action" and action_type_var.get() == "keyboard":
                capture_status_var.set("Pressione uma tecla para capturar...")
        
        # Função para detectar quando um campo perde foco
        def on_entry_focus_out():
            nonlocal current_focus
            current_focus = None
            capture_status_var.set("Clique nos campos ou botões de captura para registrar teclas...")
            
        # Associar eventos de foco aos campos
        trigger_key_entry.bind("<FocusIn>", lambda e: on_entry_focus_in("trigger"))
        trigger_key_entry.bind("<FocusOut>", lambda e: on_entry_focus_out())
        action_key_entry.bind("<FocusIn>", lambda e: on_entry_focus_in("action"))
        action_key_entry.bind("<FocusOut>", lambda e: on_entry_focus_out())
        
        # Função para captura de teclas
        def start_capture_trigger():
            nonlocal is_capturing_trigger, is_capturing_action
            is_capturing_trigger = True
            is_capturing_action = False
            trigger_capture_button.configure(text="Aguardando...")
            action_capture_button.configure(text="Capturar")
            capture_status_var.set("Pressione qualquer tecla ou botão do mouse...")
            # Dá foco ao campo
            trigger_key_entry.focus_set()
            
        def start_capture_action():
            nonlocal is_capturing_trigger, is_capturing_action
            if action_type_var.get() != "keyboard":
                return
                
            is_capturing_trigger = False
            is_capturing_action = True
            action_capture_button.configure(text="Aguardando...")
            trigger_capture_button.configure(text="Capturar")
            capture_status_var.set("Pressione qualquer tecla...")
            # Dá foco ao campo
            action_key_entry.focus_set()
        
        # Configurar botões de captura
        trigger_capture_button.configure(command=start_capture_trigger)
        action_capture_button.configure(command=start_capture_action)
        
        # Explicação detalhada de uso
        ttk.Label(content_frame, text="Observações:", font=("Helvetica", 9, "bold")).grid(row=7, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))
        ttk.Label(content_frame, text="• Para gatilhos de mouse, use os botões 'Mouse como gatilho' acima.", wraplength=380).grid(row=8, column=0, columnspan=3, sticky=tk.W, padx=5)
        ttk.Label(content_frame, text="• No modo contínuo, a ação será repetida enquanto segurar o gatilho.", wraplength=380).grid(row=9, column=0, columnspan=3, sticky=tk.W, padx=5)
        
        # Função para capturar teclas do teclado
        def on_key_press(e):
            nonlocal is_capturing_trigger, is_capturing_action, current_focus
            
            # Captura baseada em foco do campo ou botão de captura
            if current_focus == "trigger" or is_capturing_trigger:
                key_name = e.name
                trigger_key_var.set(key_name)
                is_capturing_trigger = False
                trigger_capture_button.configure(text="Capturar")
                capture_status_var.set(f"Tecla capturada: {key_name}")
                return False  # Evita propagação do evento
                
            elif (current_focus == "action" or is_capturing_action) and action_type_var.get() == "keyboard":
                key_name = e.name
                action_key_var.set(key_name)
                is_capturing_action = False
                action_capture_button.configure(text="Capturar")
                capture_status_var.set(f"Tecla capturada: {key_name}")
                return False  # Evita propagação do evento
                
            return True
        
        # Função para capturar cliques do mouse
        def on_mouse_click(button):
            nonlocal is_capturing_trigger, is_capturing_action, current_focus
            
            # Captura baseada em foco do campo ou botão de captura
            if current_focus == "trigger" or is_capturing_trigger:
                trigger_key_var.set(button)
                is_capturing_trigger = False
                trigger_capture_button.configure(text="Capturar")
                capture_status_var.set(f"Botão capturado: {button}")
                return False
                
            elif current_focus == "action" or is_capturing_action:
                if action_type_var.get() != "keyboard":
                    action_type_var.set(button)
                    is_capturing_action = False
                    action_capture_button.configure(text="Capturar")
                    capture_status_var.set(f"Botão capturado: {button}")
                    return False
                    
            return True
        
        # Registrar hooks temporários
        keyboard_hook = keyboard.hook(on_key_press)
        mouse_hook_left = mouse.on_click(lambda: on_mouse_click("left") if current_focus or is_capturing_trigger or is_capturing_action else True)
        mouse_hook_right = mouse.on_right_click(lambda: on_mouse_click("right") if current_focus or is_capturing_trigger or is_capturing_action else True)
        mouse_hook_middle = mouse.on_middle_click(lambda: on_mouse_click("middle") if current_focus or is_capturing_trigger or is_capturing_action else True)
        
        # Frame fixo para botões no final da janela
        fixed_frame = ttk.Frame(dialog)
        fixed_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        def save_mapping():
            # Remover hooks antes de salvar
            keyboard.unhook(keyboard_hook)
            mouse.unhook(mouse_hook_left)
            mouse.unhook(mouse_hook_right)
            mouse.unhook(mouse_hook_middle)
            
            # Validar inputs
            if not trigger_key_var.get():
                messagebox.showerror("Erro", "A tecla gatilho é obrigatória.")
                return
                
            if action_type_var.get() == "keyboard" and not action_key_var.get():
                messagebox.showerror("Erro", "A tecla de ação é obrigatória para ações de teclado.")
                return
                
            try:
                interval = int(interval_var.get())
                if interval <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("Erro", "O intervalo deve ser um número inteiro positivo.")
                return
                
            # Criar ou atualizar mapeamento
            new_mapping = {
                'trigger_key': trigger_key_var.get(),
                'action_type': action_type_var.get(),
                'action_key': action_key_var.get(),
                'interval': interval_var.get(),
                'once': once_var.get()
            }
            
            if edit_index is not None:
                self.custom_mappings[edit_index] = new_mapping
            else:
                self.custom_mappings.append(new_mapping)
                
            self.refresh_mappings_display()
            self.save_config()
            dialog.destroy()
            
        def cancel_dialog():
            # Remover hooks antes de fechar
            keyboard.unhook(keyboard_hook)
            mouse.unhook(mouse_hook_left)
            mouse.unhook(mouse_hook_right)
            mouse.unhook(mouse_hook_middle)
            dialog.destroy()
        
        # Botões de Salvar e Cancelar    
        save_button = ttk.Button(fixed_frame, text="Salvar", command=save_mapping, width=10)
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(fixed_frame, text="Cancelar", command=cancel_dialog, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Definir ação para fechamento do diálogo
        dialog.protocol("WM_DELETE_WINDOW", cancel_dialog)
        
        # Dar foco inicial ao campo de tecla gatilho para facilitar a captura
        trigger_key_entry.focus_set()
    
    def activate_all_mappings(self):
        """Activate all custom mappings"""
        self.deactivate_all_mappings()  # First deactivate any active mappings
        
        if not self.custom_mappings:
            self.custom_status_text.set("Nenhuma função personalizada configurada")
            return
            
        for mapping in self.custom_mappings:
            trigger_key = mapping['trigger_key']
            action_type = mapping['action_type']
            action_key = mapping['action_key']
            interval = int(mapping['interval'])
            once = mapping['once']
            
            # Create a stop event for this mapping
            stop_event = Event()
            self.active_mappings.append({
                'mapping': mapping,
                'stop_event': stop_event
            })
            
            # Define handler function
            def create_handler(m, stop_evt):
                def handler(event=None):
                    if m['once']:
                        # Para modo "uma vez"
                        if m['action_type'] == 'keyboard':
                            keyboard.send(m['action_key'])
                        else:
                            mouse.click(button=m['action_type'])
                    else:
                        # Para modo "contínuo"
                        thread = Thread(
                            target=self.run_custom_mapping,
                            args=(m, stop_evt),
                            daemon=True
                        )
                        self.custom_mapping_threads.append(thread)
                        thread.start()
                return handler
                
            handler = create_handler(mapping, stop_event)
            
            # Register the hotkey or mouse hook
            if trigger_key in ['left', 'right', 'middle', 'x1', 'x2']:
                # É um botão do mouse, configura mouse hook
                if trigger_key == 'left':
                    mouse.on_click(lambda: handler())
                elif trigger_key == 'right':
                    mouse.on_right_click(lambda: handler())
                elif trigger_key == 'middle':
                    mouse.on_middle_click(lambda: handler())
                # X1 e X2 não têm hooks específicos em algumas versões da biblioteca
            else:
                # É uma tecla de teclado
                keyboard.on_press_key(trigger_key, handler)
            
        self.custom_status_text.set(f"{len(self.custom_mappings)} funções personalizadas ativadas")
    
    def deactivate_all_mappings(self):
        """Deactivate all custom mappings"""
        # Stop all running threads
        for active in self.active_mappings:
            active['stop_event'].set()
            
        # Clear all keyboard hooks
        keyboard.unhook_all()
        
        # Clear lists
        self.active_mappings = []
        self.custom_mapping_threads = []
        
        self.custom_status_text.set("Funções personalizadas desativadas")
    
    def run_custom_mapping(self, mapping, stop_event):
        """Run a custom mapping in a separate thread"""
        interval = float(mapping['interval']) / 1000  # Convert ms to seconds
        
        while not stop_event.is_set():
            try:
                # Verificar o estado do gatilho com base no tipo (teclado ou mouse)
                if mapping['trigger_key'] in ['left', 'right', 'middle', 'x1', 'x2']:
                    # É um botão do mouse
                    trigger_pressed = mouse.is_pressed(button=mapping['trigger_key'])
                else:
                    # É uma tecla do teclado
                    trigger_pressed = keyboard.is_pressed(mapping['trigger_key'])
                
                # Se o gatilho estiver pressionado, execute a ação
                if trigger_pressed:
                    if mapping['action_type'] == 'keyboard':
                        keyboard.send(mapping['action_key'])
                    else:
                        mouse.click(button=mapping['action_type'])
                    
                    time.sleep(interval)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"Error in custom mapping: {e}")
                break
                
    def hold_press(self):
        """Método para o modo 'Segurar para repetir'"""
        while not self.stop_event.is_set():
            try:
                # Verifica se o botão está pressionado atualmente
                if self.current_input_type == "keyboard":
                    estado_atual = keyboard.is_pressed(self.current_key)
                else:
                    estado_atual = mouse.is_pressed(button=self.current_input_type)

                # Se o botão estiver pressionado, executa a ação
                if estado_atual:
                    self.status_text.set("Repetição automática em andamento...")
                    # Executa a ação
                    if self.current_input_type == "keyboard":
                        keyboard.send(self.current_key)
                    else:
                        mouse.click(button=self.current_input_type)

                    # Espera o intervalo definido
                    intervalo = float(self.interval.get()) / 1000
                    time.sleep(intervalo)
                else:
                    self.status_text.set("Aguardando botão ser pressionado...")
                    time.sleep(0.01)

            except Exception as e:
                print(f"Erro em hold_press: {e}")
                time.sleep(0.1)

    def auto_press(self):
        intervalo = float(self.interval.get()) / 1000  # Converte ms para segundos
        while self.running and not self.stop_event.is_set():
            try:
                if self.current_input_type == "keyboard":
                    keyboard.send(self.current_key)
                else:
                    # Usa o mesmo mapeamento de botões para consistência
                    mouse.click(button=self.current_input_type)
                time.sleep(intervalo)
            except Exception as e:
                print(f"Erro em auto_press: {e}")
                break

    def validate_inputs(self):
        if self.input_type.get() == "keyboard" and not self.key.get():
            self.status_text.set("Erro: Digite uma tecla!")
            return False

        try:
            interval = float(self.interval.get())
            if interval <= 0:
                self.status_text.set("Erro: Intervalo deve ser positivo!")
                return False
        except ValueError:
            self.status_text.set("Erro: Intervalo inválido!")
            return False

        return True

    def start_program(self):
        if not self.validate_inputs():
            return

        self.stop_event.set()  # Para qualquer thread anterior
        time.sleep(0.1)
        self.stop_event.clear()  # Prepara para nova execução

        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)

        key = self.key.get().lower() if self.input_type.get() == "keyboard" else self.input_type.get()
        self.current_key = key
        self.current_input_type = self.input_type.get()

        if self.mode.get() == "toggle":
            if self.current_input_type == "keyboard":
                keyboard.on_press_key(key, self.toggle_action)
            else:
                mouse.on_click(lambda: self.toggle_action(None))
        else:
            # Modo "hold"
            Thread(target=self.hold_press, daemon=True).start()

        self.status_text.set("Programa iniciado! Aguardando comando...")

    def stop_program(self):
        self.stop_event.set()
        self.running = False

        try:
            if self.current_input_type == "keyboard":
                keyboard.unhook_all()
            else:
                mouse.unhook_all()
        except:
            pass

        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.status_text.set("Programa parado!")

    def toggle_action(self, event=None):  # Tornando o parâmetro opcional
        if not self.running:
            self.status_text.set("Repetição automática iniciada!")
            self.running = True
            self.stop_event.clear()
            Thread(target=self.auto_press, daemon=True).start()
        else:
            self.status_text.set("Repetição automática parada!")
            self.running = False
            self.stop_event.set()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoClickerGUI()
    app.run()
