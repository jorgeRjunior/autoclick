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

# Import ttkbootstrap
try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
except ImportError:
    print("ttkbootstrap não está instalado. Instalando...")
    try:
        import pip
        pip.main(['install', 'ttkbootstrap'])
        import ttkbootstrap as tb
        from ttkbootstrap.constants import *
        print("ttkbootstrap instalado com sucesso!")
    except Exception as e:
        print(f"Falha ao instalar ttkbootstrap: {e}")
        print("Por favor, instale manualmente: pip install ttkbootstrap")
        sys.exit(1)


class AutoClickerGUI:
    def __init__(self):
        # Use ttkbootstrap Window with a theme
        # Examples: 'litera', 'cosmo', 'flatly', 'journal', 'lumen', 'minty', 
        # 'pulse', 'sandstone', 'united', 'yeti' (light themes)
        # 'cyborg', 'darkly', 'solar', 'superhero', 'vapor' (dark themes)
        self.root = tb.Window(themename="cosmo")
        
        self.root.title("AutoClick V5 dev by jorgeRjunior")
        self.root.geometry("700x650")
        self.root.resizable(True, True)  # Permitir redimensionamento em todas as direções

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
        
        # TOGGLE MODE REGISTRIES 
        self.toggle_registry = {}
        self.toggle_cleanup_indices = []
        
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
                    loaded_mappings = config.get('custom_mappings', [])
                    # Initialize runtime state for loaded mappings
                    self.custom_mappings = []
                    for m in loaded_mappings:
                        # --- Compatibility: Convert old 'once' key to 'mode' --- 
                        if 'once' in m and 'mode' not in m:
                            m['mode'] = 'once' if m['once'] else 'continuous'
                            del m['once']
                        elif 'mode' not in m:
                             m['mode'] = 'continuous' # Default for very old configs
                        # -----------------------------------------------------
                        
                        m['is_active'] = m.get('is_active', False) 
                        m['thread_ref'] = None 
                        m['stop_event'] = None
                        m['is_trigger_down'] = False 
                        m['is_repeating'] = False # State for toggle/continuous execution
                        self.custom_mappings.append(m)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.custom_mappings = []

    def save_config(self):
        """Save configurations to file"""
        try:
            mappings_to_save = []
            for m in self.custom_mappings:
                saved_m = m.copy()
                saved_m.pop('thread_ref', None) 
                saved_m.pop('stop_event', None) 
                saved_m.pop('is_trigger_down', None) 
                saved_m.pop('is_repeating', None) # Don't save runtime state
                saved_m.pop('once', None) # Remove old compatibility key
                mappings_to_save.append(saved_m)

            config = {
                'custom_mappings': mappings_to_save
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

            # Use ttk.Button for themed appearance
            button = ttk.Button(
                frame,
                image=photo,
                command=lambda: webbrowser.open(link),
                bootstyle="link" # Use link style for subtle buttons
            )
            button.image = photo
            button.grid(row=row, column=column, padx=5)
        except Exception as e:
            print(f"Error loading social icon {icon_url}: {e}")
            # Fallback to text button if image fails
            button_text = "GitHub" if "github" in link else "Instagram"
            button = ttk.Button(
                frame,
                text=button_text,
                command=lambda: webbrowser.open(link),
                bootstyle="link"
            )
            button.grid(row=row, column=column, padx=5)

    def create_main_tab_widgets(self):
        # Frame principal
        main_frame = self.main_tab
        
        # Configurar o gerenciamento de geometria para permitir expansão horizontal
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="AutoClick V5", font=("Helvetica", 16, "bold"))
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
        input_frame = ttk.LabelFrame(main_frame, text="Tipo de Entrada", padding=5)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        # Configure columns for radio buttons if needed (optional, may help spacing)
        # input_frame.columnconfigure(0, weight=1)
        # input_frame.columnconfigure(1, weight=1)
        # input_frame.columnconfigure(2, weight=1)

        # Arrange Radiobuttons in two rows, aligned left
        ttk.Radiobutton(input_frame, text="Teclado", variable=self.input_type, value="keyboard").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(input_frame, text="Mouse 1 (Esquerdo)", variable=self.input_type, value="left").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(input_frame, text="Mouse 2 (Direito)", variable=self.input_type, value="right").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(input_frame, text="Mouse 4 (Lateral Frente)", variable=self.input_type, value="x2").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(input_frame, text="Mouse 5 (Lateral Trás)", variable=self.input_type, value="x1").grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

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

        ttk.Radiobutton(mode_frame, text="Segurar para repetir", variable=self.mode, value="hold").grid(row=0, column=0, padx=5, pady=2)
        ttk.Radiobutton(mode_frame, text="Alternar (Iniciar/Parar)", variable=self.mode, value="toggle").grid(row=0, column=1, padx=5, pady=2)

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
        for i in range(7):
            self.mappings_frame.columnconfigure(i, weight=1)
        
        # Botões para adicionar/remover
        button_frame = ttk.Frame(custom_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Adicionar Nova Função", command=self.add_custom_mapping).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Salvar Configurações", command=self.save_config).grid(row=0, column=1, padx=5)
        
        # Refresh the mappings display
        self.refresh_mappings_display()
        
        # Register hooks based on loaded active states
        self._active_hook_removers = {} # Store hook removal functions {index: list_of_removers}
        self._running_threads = {} # Store running continuous threads {index: (thread, stop_event)}
        self.register_active_hooks() # Register hooks for initially active mappings
    
    def refresh_mappings_display(self):
        """Refresh the display of custom mappings"""
        # Clear existing widgets
        for widget in self.mappings_frame.winfo_children():
            widget.destroy()
            
        # Set column weights for proper resizing
        # Added one more column for the Checkbutton
        for i in range(7): 
            self.mappings_frame.columnconfigure(i, weight=1)
            
        # Header - Added "Ativo?" column
        ttk.Label(self.mappings_frame, text="Ativo?", width=5).grid(row=0, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Tecla Gatilho", width=15).grid(row=0, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Ação", width=15).grid(row=0, column=2, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Tipo", width=10).grid(row=0, column=3, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Intervalo (ms)", width=12).grid(row=0, column=4, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Modo", width=12).grid(row=0, column=5, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text="Ações", width=20).grid(row=0, column=6, padx=2, pady=2, sticky=(tk.W, tk.E))
        
        separator = ttk.Separator(self.mappings_frame, orient='horizontal')
        # Span across all 7 columns
        separator.grid(row=1, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=5)
        
        if not self.custom_mappings:
            ttk.Label(
                self.mappings_frame, 
                text="Não há funções personalizadas configuradas. Clique em 'Adicionar Nova Função'.",
                font=("Helvetica", 9, "italic")
            ).grid(row=2, column=0, columnspan=7, padx=5, pady=10, sticky=(tk.W, tk.E)) # Span 7
            return
        
        # Display each mapping
        for i, mapping in enumerate(self.custom_mappings):
            # Ensure 'is_active' exists
            if 'is_active' not in mapping:
                mapping['is_active'] = False
            # Ensure 'mode' exists (handle old configs converted in load_config)
            if 'mode' not in mapping:
                 mapping['mode'] = 'continuous' # Default if somehow missed

            # --- Checkbox for Active State ---
            active_var = tk.BooleanVar(value=mapping['is_active'])
            chk = ttk.Checkbutton(
                self.mappings_frame, 
                variable=active_var, 
                command=lambda idx=i, var=active_var: self.toggle_mapping_active_state(idx, var)
            )
            chk.grid(row=i+2, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
            # Store the var for potential external updates (though command is preferred)
            # mapping['_active_var'] = active_var # Optional: might not be needed

            # --- Other columns shifted by 1 ---
            ttk.Label(self.mappings_frame, text=mapping['trigger_key']).grid(row=i+2, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            action_text = mapping.get('action_key', '') if mapping['action_type'] == 'keyboard' else f"Mouse {mapping['action_type']}"
            ttk.Label(self.mappings_frame, text=action_text).grid(row=i+2, column=2, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            type_display = {'keyboard': 'Teclado', 'left': 'Mouse Esq.', 'right': 'Mouse Dir.', 'middle': 'Mouse Meio'}.get(mapping['action_type'], mapping['action_type'])
            ttk.Label(self.mappings_frame, text=type_display).grid(row=i+2, column=3, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            ttk.Label(self.mappings_frame, text=mapping['interval']).grid(row=i+2, column=4, padx=2, pady=2, sticky=(tk.W, tk.E))

            # --- Mode Display (Column 5) ---
            mode_display_text = {
                'continuous': 'Contínuo',
                'once': 'Uma vez',
                'toggle': 'Alternar'
            }.get(mapping['mode'], 'Contínuo') # Default display
            ttk.Label(self.mappings_frame, text=mode_display_text).grid(row=i+2, column=5, padx=2, pady=2, sticky=(tk.W, tk.E))
            
            # Container for the buttons (now in column 6)
            buttons_frame = ttk.Frame(self.mappings_frame)
            buttons_frame.grid(row=i+2, column=6, padx=2, pady=2, sticky=(tk.W, tk.E))
            buttons_frame.columnconfigure(0, weight=1)
            buttons_frame.columnconfigure(1, weight=1)
            
            # Edit/Delete buttons
            ttk.Button(buttons_frame, text="Editar", width=8, command=lambda idx=i: self.edit_mapping(idx)).grid(row=0, column=0, padx=2)
            ttk.Button(buttons_frame, text="Excluir", width=8, command=lambda idx=i: self.delete_mapping(idx)).grid(row=0, column=1, padx=2)
    
    def add_custom_mapping(self):
        """Add a new custom mapping"""
        if len(self.custom_mappings) >= 10:
            messagebox.showwarning("Limite atingido", "Você já atingiu o limite de 10 funções personalizadas.")
            return
            
        # Pass default values including is_active=False
        self.open_mapping_dialog() # Edits happen in place via save_mapping
    
    def edit_mapping(self, index):
        """Edit an existing mapping"""
        # Deactivate before editing to prevent issues with changed triggers
        if self.custom_mappings[index].get('is_active', False):
            self.custom_mappings[index]['is_active'] = False
            self.register_active_hooks() # Unhook the old trigger
            # Need to update the checkbox visually after unhooking
            self.refresh_mappings_display() 

        self.open_mapping_dialog(self.custom_mappings[index], index)
    
    def delete_mapping(self, index):
        """Delete a mapping"""
        if messagebox.askyesno("Confirmar exclusão", "Tem certeza que deseja excluir esta função?"):
            # Ensure hooks are removed and threads stopped before deleting
            mapping_to_delete = self.custom_mappings[index]
            if mapping_to_delete.get('is_active', False):
                 mapping_to_delete['is_active'] = False # Mark as inactive
                 self.register_active_hooks() # This will stop thread & unhook
            else:
                 # If it wasn't active, ensure any lingering thread state is cleared
                 self._stop_continuous_thread(index)

            # Now remove from list
            del self.custom_mappings[index]
            
            # Adjust indices in hook removers and running threads if needed (simpler to just re-register)
            # self.register_active_hooks() # Re-register remaining might be safest if indices matter elsewhere
            # Let's clear potentially dangling refs for the deleted index explicitly
            self._active_hook_removers.pop(index, None)
            self._running_threads.pop(index, None)
            # We might need to shift indices in these dicts if we don't re-register all
            # Re-registering all active hooks IS the cleaner approach here after deletion.
            self.register_active_hooks()

            self.refresh_mappings_display() # Update UI
            self.save_config() # Save changes
    
    def open_mapping_dialog(self, mapping=None, edit_index=None):
        """Open dialog to add or edit a mapping"""
        dialog = tb.Toplevel(self.root)
        dialog.title("Adicionar Nova Função" if mapping is None else "Editar Função")
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        dialog.grab_set()
        
        # --- Temporarily disable global hooks --- 
        self.register_active_hooks(temporarily_disable=True)
        
        default_mode = 'continuous'
        if mapping and 'mode' in mapping:
            default_mode = mapping['mode']
        elif mapping and 'once' in mapping: # Compatibility
             default_mode = 'once' if mapping['once'] else 'continuous'

        if mapping is None:
            mapping = {
                'trigger_key': '',
                'action_type': 'keyboard',
                'action_key': '',
                'interval': '100',
                'mode': default_mode,
                'is_active': False, 
                'thread_ref': None,
                'stop_event': None,
                'is_trigger_down': False,
                'is_repeating': False # Initialize new state
            }
        else: 
             mapping['thread_ref'] = None 
             mapping['stop_event'] = None
             mapping['is_trigger_down'] = False 
             mapping['is_repeating'] = False # Reset runtime state on edit
             if 'mode' not in mapping: # Ensure mode exists for edit
                  mapping['mode'] = default_mode

        trigger_key_var = tk.StringVar(value=mapping['trigger_key'])
        action_key_var = tk.StringVar(value=mapping.get('action_key', ''))
        action_type_var = tk.StringVar(value=mapping['action_type'])
        interval_var = tk.StringVar(value=mapping['interval'])
        mode_var = tk.StringVar(value=mapping['mode']) # New variable for mode

        # Variáveis de controle de captura
        capture_mode = None # 'trigger' or 'action'
        
        # Frame para conteúdo
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuração de expansão
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=0) # Column for buttons

        # --- 1. Captura do Gatilho ---
        ttk.Label(main_frame, text="1. Tecla/Botão Gatilho:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(5, 0))

        trigger_display_var = tk.StringVar(value=f"Gatilho Atual: {trigger_key_var.get()}" if trigger_key_var.get() else "Nenhum gatilho definido")
        ttk.Label(main_frame, textvariable=trigger_display_var, wraplength=350).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        trigger_capture_button = ttk.Button(main_frame, text="Capturar Gatilho")
        trigger_capture_button.grid(row=1, column=2, padx=5, pady=2, sticky=tk.E)

        # --- 2. Captura da Ação ---
        ttk.Label(main_frame, text="2. Tecla/Botão de Ação (a repetir):", font=("Helvetica", 10, "bold")).grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))

        action_display_text = "Nenhuma ação definida"
        if action_key_var.get():
            if action_type_var.get() == 'keyboard':
                action_display_text = f"Ação Atual: Tecla '{action_key_var.get()}'"
            else:
                 action_display_text = f"Ação Atual: Mouse '{action_type_var.get()}'"

        action_display_var = tk.StringVar(value=action_display_text)
        ttk.Label(main_frame, textvariable=action_display_var, wraplength=350).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        action_capture_button = ttk.Button(main_frame, text="Capturar Ação")
        action_capture_button.grid(row=3, column=2, padx=5, pady=2, sticky=tk.E)

        # --- 3. Intervalo ---
        ttk.Label(main_frame, text="3. Intervalo (ms):", font=("Helvetica", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))
        
        interval_entry = ttk.Entry(main_frame, textvariable=interval_var, width=15)
        interval_entry.grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)

        # --- 4. Modo de Repetição ---
        ttk.Label(main_frame, text="4. Modo de Repetição:", font=("Helvetica", 10, "bold")).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))
        
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=7, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        # Use mode_var (StringVar) now, pack vertically
        ttk.Radiobutton(mode_frame, text="Contínuo (segurar)", variable=mode_var, value='continuous').pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text="Uma vez (ao pressionar)", variable=mode_var, value='once').pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text="Alternar (liga/desliga)", variable=mode_var, value='toggle').pack(anchor=tk.W, pady=1)

        # --- Status de Captura ---
        capture_status_var = tk.StringVar(value="Clique em 'Capturar Gatilho' ou 'Capturar Ação'")
        capture_status = ttk.Label(main_frame, textvariable=capture_status_var, font=("Helvetica", 9, "italic"), wraplength=380)
        capture_status.grid(row=8, column=0, columnspan=3, padx=5, pady=(10, 5))

        # --- Lógica de Captura ---
        def start_capture(mode):
            nonlocal capture_mode
            capture_mode = mode
            if mode == 'trigger':
                capture_status_var.set("Aguardando gatilho... Pressione qualquer tecla ou botão do mouse.")
                trigger_capture_button.config(state=tk.DISABLED)
                action_capture_button.config(state=tk.NORMAL)
            else: # mode == 'action'
                capture_status_var.set("Aguardando ação... Pressione qualquer tecla ou botão do mouse.")
                action_capture_button.config(state=tk.DISABLED)
                trigger_capture_button.config(state=tk.NORMAL)
            # Give focus away to allow capture without entry focus
            dialog.focus_set() 

        trigger_capture_button.configure(command=lambda: start_capture('trigger'))
        action_capture_button.configure(command=lambda: start_capture('action'))
        
        # Função para capturar teclas do teclado
        def on_key_press(e):
            nonlocal capture_mode
            key_name = e.name
            
            if capture_mode == 'trigger':
                trigger_key_var.set(key_name)
                trigger_display_var.set(f"Gatilho Atual: Tecla '{key_name}'")
                capture_status_var.set(f"Gatilho capturado: Tecla '{key_name}'. Clique em 'Capturar Ação' ou 'Salvar'.")
                trigger_capture_button.config(state=tk.NORMAL)
                capture_mode = None # Stop capturing
                return False # Consume event
            
            elif capture_mode == 'action':
                action_key_var.set(key_name)
                action_type_var.set('keyboard') # Define o tipo como teclado
                action_display_var.set(f"Ação Atual: Tecla '{key_name}'")
                capture_status_var.set(f"Ação capturada: Tecla '{key_name}'. Ajuste o intervalo e clique em 'Salvar'.")
                action_capture_button.config(state=tk.NORMAL)
                capture_mode = None # Stop capturing
                return False # Consume event

            return True # Allow event propagation if not capturing
        
        # Função para capturar cliques do mouse (NOVA VERSÃO USANDO HOOK GENÉRICO)
        def dialog_mouse_handler(event):
            nonlocal capture_mode
            if not isinstance(event, mouse.ButtonEvent):
                return True 
            if event.event_type == mouse.DOWN:
                button_name = event.button
                if capture_mode == 'trigger':
                    trigger_key_var.set(button_name)
                    trigger_display_var.set(f"Gatilho Atual: Mouse '{button_name}'")
                    capture_status_var.set(f"Gatilho capturado: Mouse '{button_name}'. Clique em 'Capturar Ação' ou 'Salvar'.")
                    trigger_capture_button.config(state=tk.NORMAL)
                    capture_mode = None
                    return False
                elif capture_mode == 'action':
                    action_key_var.set('') # Clear keyboard action key
                    action_type_var.set(button_name) # Set action type to the mouse button
                    action_display_var.set(f"Ação Atual: Mouse '{button_name}'")
                    capture_status_var.set(f"Ação capturada: Mouse '{button_name}'. Ajuste o intervalo e clique em 'Salvar'.")
                    action_capture_button.config(state=tk.NORMAL)
                    capture_mode = None
                    return False
            return True 
        
        # Registrar hooks TEMPORÁRIOS do diálogo
        keyboard_hook = keyboard.hook(on_key_press)
        dialog_mouse_hook = mouse.hook(dialog_mouse_handler)
        
        # --- Botões Finais ---
        fixed_frame = ttk.Frame(dialog)
        fixed_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        def save_mapping():
            # Remover hooks TEMPORÁRIOS do diálogo
            try: keyboard.unhook(keyboard_hook)
            except Exception as e: print(f"Error unhooking dialog kbd: {e}")
            try: mouse.unhook(dialog_mouse_hook)
            except Exception as e: print(f"Error unhooking dialog mouse: {e}")
            
            # Validar inputs
            if not trigger_key_var.get():
                messagebox.showerror("Erro", "O gatilho é obrigatório.", parent=dialog)
                dialog.destroy() 
                return
                
            action_type = action_type_var.get()
            action_key = action_key_var.get()

            if not action_type or (action_type == 'keyboard' and not action_key):
                 messagebox.showerror("Erro", "A ação (tecla ou botão do mouse) é obrigatória.", parent=dialog)
                 dialog.destroy()
                 return
                
            try:
                interval = int(interval_var.get())
                if interval <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "O intervalo deve ser um número inteiro positivo.", parent=dialog)
                dialog.destroy()
                return
                
            # Create or update mapping data (excluding runtime state)
            new_mapping_data = {
                'trigger_key': trigger_key_var.get(),
                'action_type': action_type,
                'action_key': action_key if action_type == 'keyboard' else '',
                'interval': interval_var.get(),
                'mode': mode_var.get(), # Get mode from the new variable
                # is_active and runtime states handled below
            }
            
            needs_hook_registration = False
            if edit_index is not None:
                # Update existing mapping, set to ACTIVE after edit
                self.custom_mappings[edit_index].update(new_mapping_data)
                self.custom_mappings[edit_index]['is_active'] = True 
                self.custom_mappings[edit_index]['thread_ref'] = None
                self.custom_mappings[edit_index]['stop_event'] = None
                self.custom_mappings[edit_index]['is_trigger_down'] = False 
                self.custom_mappings[edit_index]['is_repeating'] = False # Reset runtime state
                needs_hook_registration = True 
            else:
                # Check limit again before appending
                if len(self.custom_mappings) >= 10:
                     messagebox.showwarning("Limite atingido", "Você já atingiu o limite de 10 funções personalizadas.", parent=dialog)
                     dialog.destroy()
                     return
                 
                # Add required fields for a new mapping, set to ACTIVE by default
                new_mapping_data['is_active'] = True 
                new_mapping_data['thread_ref'] = None
                new_mapping_data['stop_event'] = None
                new_mapping_data['is_trigger_down'] = False 
                new_mapping_data['is_repeating'] = False # Initialize new state
                self.custom_mappings.append(new_mapping_data)
                needs_hook_registration = True 
                
            self.refresh_mappings_display()
            self.save_config()
            # Register hooks if a new or edited active mapping was saved
            if needs_hook_registration:
                 self.register_active_hooks()
                 
            # Re-register GLOBAL hooks based on current state
            self.register_active_hooks()
            
            dialog.destroy()
            
        def cancel_dialog():
            # Remover hooks TEMPORÁRIOS do diálogo
            try: keyboard.unhook(keyboard_hook)
            except Exception as e: print(f"Error unhooking dialog kbd: {e}")
            try: mouse.unhook(dialog_mouse_hook)
            except Exception as e: print(f"Error unhooking dialog mouse: {e}")
            
            # Re-register GLOBAL hooks based on current state
            self.register_active_hooks()
            
            dialog.destroy()
        
        # Botões de Salvar e Cancelar    
        save_button = ttk.Button(fixed_frame, text="Salvar", command=save_mapping, width=10)
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(fixed_frame, text="Cancelar", command=cancel_dialog, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Definir ação para fechamento do diálogo
        dialog.protocol("WM_DELETE_WINDOW", cancel_dialog)
        
        # Dialog focus helps capture events initially
        dialog.focus_set()
    
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
    
    def run_custom_mapping(self, index, stop_event):
        """Runs the continuous action loop for a custom mapping."""
        if not (0 <= index < len(self.custom_mappings)):
             return # Safety check

        mapping = self.custom_mappings[index]
        # Define mode immediately after getting the mapping
        mode = mapping.get('mode', 'continuous') 

        trigger_key = mapping['trigger_key']
        action_type = mapping['action_type']
        action_key = mapping.get('action_key', '')
        is_mouse_trigger = trigger_key in ['left', 'right', 'middle', 'x1', 'x2']
        # mode = mapping.get('mode', 'continuous') # Already defined above

        interval = 0.01 # Default small interval
        try:
            interval = float(mapping['interval']) / 1000
            if interval <= 0: interval = 0.01
        except ValueError:
            pass

        while not stop_event.is_set():
            try:
                # --- Check if trigger is still pressed (ONLY for continuous mode) ---
                if mode == 'continuous':
                    trigger_pressed = False
                    if is_mouse_trigger:
                        trigger_pressed = mouse.is_pressed(button=trigger_key)
                    else: # Keyboard trigger
                        trigger_pressed = keyboard.is_pressed(trigger_key)
                    
                    if not trigger_pressed:
                        break # Stop thread if trigger released in continuous mode

                # --- Perform action --- 
                if action_type == 'keyboard':
                    keyboard.send(action_key)
                else:
                    mouse.click(button=action_type)
                    
                # Wait
                    time.sleep(interval)

            except Exception as e:
                print(f"Error in custom mapping thread for index {index}: {e}")
                break # Exit thread on error
        
        # Clean up thread reference from the central dict when thread finishes
        if index in self._running_threads and self._running_threads[index][1] == stop_event:
             del self._running_threads[index]
                
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

    def toggle_mapping_active_state(self, index, var):
        """Called when a mapping's active checkbox is toggled."""
        if 0 <= index < len(self.custom_mappings):
            mapping = self.custom_mappings[index]
            is_active = var.get()
            mapping['is_active'] = is_active
            
            if not is_active:
                # Ensure repeating state is off and stop any running thread
                mapping['is_repeating'] = False 
                self._stop_continuous_thread(index) 
                
            self.register_active_hooks() 
            self.save_config()

    def _stop_continuous_thread(self, index):
        """Signals the continuous thread for a given mapping index to stop."""
        # Setting is_repeating to False is handled by the caller or the thread itself
        if index in self._running_threads:
            _thread, stop_event = self._running_threads[index] 
            if stop_event:
                stop_event.set() 

    def register_active_hooks(self, temporarily_disable=False):
        """Unhooks all custom mappings and re-registers hooks for active ones."""
        hook_action = "Disabling" if temporarily_disable else "Registering"
        indices_to_clear_toggle = list(self.toggle_registry.keys())
        for index in indices_to_clear_toggle:
            toggle_info = self.toggle_registry.get(index)
            if toggle_info and toggle_info.get('stop_event'):
                toggle_info['stop_event'].set()
        indices_to_clear_cont = list(self._running_threads.keys())
        for index in indices_to_clear_cont:
             self._stop_continuous_thread(index) # Signals the event
        self._running_threads.clear()

        for index, removers in list(self._active_hook_removers.items()): # Use list to avoid runtime dict change error
            for remover in removers:
                try: remover() 
                except Exception as e: print(f"[{hook_action} Hooks] Error removing kbd hook {index}: {e}")
            if index in self._active_hook_removers: del self._active_hook_removers[index]
        
        try: mouse.unhook_all()
        except Exception as e: print(f"[{hook_action} Hooks] Error unhooking mouse: {e}")
        try: keyboard.unhook_all()
        except Exception as e: print(f"[{hook_action} Hooks] Error unhooking kbd: {e}")

        if temporarily_disable:
             self._global_mouse_hook_registered = False 
             return

        self._global_mouse_hook_registered = False
        any_mouse_trigger_active = False # Flag to check if global mouse hook is needed
        for i, mapping in enumerate(self.custom_mappings):
             mapping['is_trigger_down'] = False # Ensure clean state
             if mapping.get('is_active', False):
                 trigger_key = mapping['trigger_key']
                 mode = mapping.get('mode', 'continuous')
                 
                 is_mouse_trigger = trigger_key in ['left', 'right', 'middle', 'x1', 'x2', 'x'] 
                 is_keyboard_trigger = not is_mouse_trigger
                 
                 if is_mouse_trigger:
                     any_mouse_trigger_active = True
                     
                 try:
                     if is_keyboard_trigger:
                         removers = []
                         if mode == 'toggle':
                             def create_toggle_handler(idx):
                                 def keyboard_handler(event):
                                     if event.name == self.custom_mappings[idx]['trigger_key']:
                                         event_type_str = 'press' if event.event_type == keyboard.KEY_DOWN else 'release' if event.event_type == keyboard.KEY_UP else None
                                         if event_type_str:
                                             return self.handle_toggle_trigger(idx, event_type_str)
                                     return True
                                 return keyboard_handler
                             remover = keyboard.hook(create_toggle_handler(i))
                             removers.append(remover)
                         else: # Continuous or Once
                             def create_standard_keyboard_handler(idx):
                                 def keyboard_handler(event):
                                     if event.name == self.custom_mappings[idx]['trigger_key']:
                                         event_type_str = 'press' if event.event_type == keyboard.KEY_DOWN else 'release' if event.event_type == keyboard.KEY_UP else None
                                         if event_type_str:
                                             return self.handle_custom_trigger(idx, event_type_str)
                                     return True
                                 return keyboard_handler
                             
                             remover = keyboard.hook(create_standard_keyboard_handler(i))
                             removers.append(remover)
                             
                         if removers:
                             self._active_hook_removers[i] = removers
                         else:
                             print(f"    <-- [{hook_action} Hooks] KEYBOARD hook FAILED to register for index {i}")
                             
                 except Exception as e:
                     print(f"    XXX [{hook_action} Hooks] Error setting up index {i}: {e}")
                     mapping['is_active'] = False # Deactivate on error
                     self.root.after(10, self.refresh_mappings_display)
                     
        if any_mouse_trigger_active and not self._global_mouse_hook_registered:
             try:
                 mouse.hook(self.global_mouse_event_handler)
                 self._global_mouse_hook_registered = True
             except Exception as e:
                  print(f"    XXX [{hook_action} Hooks] Error registering global mouse hook: {e}")
        elif any_mouse_trigger_active and self._global_mouse_hook_registered:
             print(f"  -- [{hook_action} Hooks] Global mouse hook ALREADY registered.")
        elif not any_mouse_trigger_active:
             print(f"  -- [{hook_action} Hooks] No active mouse triggers found. Skipping global mouse hook.")
             
    def handle_toggle_trigger(self, index, event_type):
        """Dedicated handler for toggle mode triggers"""
        if not (0 <= index < len(self.custom_mappings)):
            return False
            
        mapping = self.custom_mappings[index]
        
        if event_type == 'press':
            if mapping.get('mode', 'continuous') == 'toggle' and mapping.get('is_active', False):
                toggle_info = self.toggle_registry.get(index)
                
                if toggle_info and toggle_info.get('active', False):
                    toggle_info['active'] = False
                    if toggle_info.get('stop_event'):
                        toggle_info['stop_event'].set()
                else:
                    stop_event = Event()
                    thread = Thread(
                        target=self.toggle_repeater_thread,
                        args=(index, stop_event),
                        daemon=True
                    )
                    
                    toggle_info = {
                        'active': True,
                        'thread': thread, 
                        'stop_event': stop_event
                    }
                    
                    self.toggle_registry[index] = toggle_info
                    thread.start()
            
            return False # Consume the event
            
        elif event_type == 'release':
            return False # Consume event
            
        return True # Let other events propagate
        
    def toggle_repeater_thread(self, index, stop_event):
        """Dedicated thread for toggle mode repeater"""
        if not (0 <= index < len(self.custom_mappings)):
            return
            
        mapping = self.custom_mappings[index]
        action_type = mapping.get('action_type', 'keyboard')
        action_key = mapping.get('action_key', '')
        
        try:
            interval = float(mapping.get('interval', '100')) / 1000
            if interval <= 0: interval = 0.01
        except ValueError:
            interval = 0.1 # Default
        
        try:
            repeat_count = 0
            while not stop_event.is_set():
                if not (0 <= index < len(self.custom_mappings)):
                    break
                    
                if not mapping.get('is_active', False):
                    break
                
                try:
                    if action_type == 'keyboard':
                        keyboard.send(action_key)
                    else:
                        mouse.click(button=action_type)
                    repeat_count += 1
                except Exception as action_error:
                    print(f"[TOGGLE Thread] Error performing action: {action_error}")
                
                if stop_event.is_set():
                    break
                
                time.sleep(interval)
                
        except Exception as e:
            print(f"[TOGGLE Thread] Error in toggle thread for index {index}: {e}")
        finally:
            self.toggle_cleanup_indices.append(index)
            self.root.after(100, self.toggle_registry_cleanup)
            
    def toggle_registry_cleanup(self):
        """Clean up toggle registry entries for finished threads"""
        if not self.toggle_cleanup_indices:
            return
            
        for index in self.toggle_cleanup_indices:
            if index in self.toggle_registry:
                del self.toggle_registry[index]
                
        self.toggle_cleanup_indices.clear()

    def handle_custom_trigger(self, index, event_type):
        """Handles the trigger event for non-toggle mappings."""
        if not (0 <= index < len(self.custom_mappings)): return 
        mapping = self.custom_mappings[index]
        if not mapping.get('is_active', False): return
        
        mode = mapping.get('mode', 'continuous')
        
        if mode == 'toggle': return True
        
        action_type = mapping['action_type']
        action_key = mapping.get('action_key', '')
        was_down = mapping.get('is_trigger_down', False)

        if event_type == 'press':
            mapping['is_trigger_down'] = True 
            
            if not was_down: 
                if mode == 'once':
                    try:
                        if action_type == 'keyboard': keyboard.send(action_key)
                        else: mouse.click(button=action_type)
                    except Exception as e: print(f"Error performing 'once' action for mapping {index}: {e}")
                
                elif mode == 'continuous':
                    if not mapping.get('is_repeating', False):
                        mapping['is_repeating'] = True
                        stop_event = Event()
                        thread = Thread(target=self.run_custom_mapping, args=(index, stop_event), daemon=True)
                        self._running_threads[index] = (thread, stop_event)
                        thread.start()

        elif event_type == 'release':
            mapping['is_trigger_down'] = False 
            if mode == 'continuous':
                if mapping.get('is_repeating', False):
                     mapping['is_repeating'] = False
                     self._stop_continuous_thread(index)

    # --- New Global Mouse Handler --- 
    def global_mouse_event_handler(self, event):
        if isinstance(event, mouse.ButtonEvent):
            event_type_str = 'press' if event.event_type == mouse.DOWN else 'release' if event.event_type == mouse.UP else None
            
            if event_type_str:
                for i, mapping in enumerate(self.custom_mappings):
                    stored_trigger = mapping.get('trigger_key')
                    detected_button = event.button
                    
                    is_match = False
                    if stored_trigger == detected_button:
                        is_match = True
                    elif stored_trigger == 'x1' and detected_button == 'x':
                        is_match = True
                    
                    if mapping.get('is_active', False) and is_match:
                        mode = mapping.get('mode', 'continuous')
                        if mode == 'toggle':
                            self.handle_toggle_trigger(i, event_type_str)
                        else: # 'continuous' or 'once'
                            self.handle_custom_trigger(i, event_type_str)
            
        return True # Allow event propagation
        
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoClickerGUI()
    app.run()
