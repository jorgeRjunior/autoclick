import sys
import os
import tkinter as tk

# --- Helper para localizar recursos empacotados pelo PyInstaller ---
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# --- Splash Screen ---
def show_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.attributes('-topmost', True)
    splash.configure(bg='black')

    gif_path = resource_path("loading.gif")
    splash._after_id = None
    try:
        gif = tk.PhotoImage(file=gif_path)
        w, h = gif.width(), gif.height()
        screen_w = splash.winfo_screenwidth()
        screen_h = splash.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        splash.geometry(f"{w}x{h}+{x}+{y}")

        label = tk.Label(splash, image=gif, bg='black')
        label.pack()

        # Animar GIF
        frames = []
        try:
            i = 0
            while True:
                frame = tk.PhotoImage(file=gif_path, format=f"gif -index {i}")
                frames.append(frame)
                i += 1
        except tk.TclError:
            pass

        if frames:
            def animate(idx=0):
                if splash.winfo_exists():
                    label.configure(image=frames[idx])
                    splash._after_id = splash.after(80, animate, (idx + 1) % len(frames))
            animate()
    except Exception:
        splash.geometry("300x100+500+400")
        tk.Label(splash, text="Loading AutoClick V6...", fg='white', bg='black',
                 font=("Helvetica", 14)).pack(expand=True)

    splash.update()
    return splash

def close_splash(splash):
    """Fecha splash cancelando animacao e destruindo completamente"""
    try:
        if splash._after_id:
            splash.after_cancel(splash._after_id)
        splash.destroy()
    except Exception:
        pass

splash = show_splash()

# --- Imports pesados ---
import keyboard
import mouse
from tkinter import ttk, messagebox
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import time
import json
import random
import math
from threading import Thread, Event
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import ctypes
import atexit

# --- Windows High-Precision Timer ---
if sys.platform == 'win32':
    _winmm = ctypes.windll.winmm
    _winmm.timeBeginPeriod(1)
    atexit.register(_winmm.timeEndPeriod, 1)


# --- Internationalization ---
TRANSLATIONS = {
    "en": {
        "window_title": "AutoClick V6 dev by jorgeRjunior",
        "tab_main": "Main Function",
        "tab_custom": "Custom Functions",
        "tab_test": "Test",
        "title": "AutoClick V6",
        "subtitle": "dev by jorgeRjunior",
        "input_type_frame": "Input Type",
        "radio_keyboard": "Keyboard",
        "radio_mouse_left": "Mouse 1 (Left)",
        "radio_mouse_right": "Mouse 2 (Right)",
        "radio_mouse_x2": "Mouse 4 (Side Front)",
        "radio_mouse_x1": "Mouse 5 (Side Back)",
        "lbl_key": "Key:",
        "interval_frame": "Interval (ms) - Random Range",
        "lbl_min": "Minimum:",
        "lbl_max": "Maximum:",
        "mode_frame": "Operation Mode",
        "mode_hold": "Hold to repeat",
        "mode_toggle": "Toggle (Start/Stop)",
        "status_frame": "Status",
        "status_waiting": "Waiting to start...",
        "btn_start": "Start",
        "btn_stop": "Stop",
        "info_text": "\nInstructions:\n- Mouse 1 = Left mouse button\n- Mouse 2 = Right mouse button\n- Mouse 4 = Front side mouse button\n- Mouse 5 = Back side mouse button\n- For keyboard keys, type the desired letter/key\n- The interval is the time between repetitions\n",
        "status_running": "Automatic repetition in progress...",
        "status_waiting_button": "Waiting for button to be pressed...",
        "status_started": "Program started! Waiting for command...",
        "status_stopped": "Program stopped!",
        "status_toggle_on": "Automatic repetition started!",
        "status_toggle_off": "Automatic repetition stopped!",
        "err_no_key": "Error: Enter a key!",
        "err_positive": "Error: Intervals must be positive!",
        "err_min_max": "Error: Minimum cannot be greater than maximum!",
        "err_invalid_interval": "Error: Invalid interval!",
        "custom_title": "Custom Functions",
        "custom_instructions": "Configure up to 10 keys or mouse buttons to activate automated repetitions.",
        "btn_add_function": "Add New Function",
        "btn_save_config": "Save Settings",
        "col_active": "Active?",
        "col_trigger": "Trigger Key",
        "col_action": "Action",
        "col_type": "Type",
        "col_interval": "Interval Min-Max",
        "col_mode": "Mode",
        "col_actions": "Actions",
        "no_functions": "No custom functions configured. Click 'Add New Function'.",
        "type_keyboard": "Keyboard",
        "type_mouse_left": "Mouse L.",
        "type_mouse_right": "Mouse R.",
        "type_mouse_middle": "Mouse Mid.",
        "mode_continuous": "Continuous",
        "mode_once": "Once",
        "mode_toggle_display": "Toggle",
        "btn_edit": "Edit",
        "btn_delete": "Delete",
        "limit_title": "Limit Reached",
        "limit_msg": "You have reached the limit of 10 custom functions.",
        "confirm_delete_title": "Confirm Delete",
        "confirm_delete_msg": "Are you sure you want to delete this function?",
        "err_title": "Error",
        "err_trigger_required": "Trigger is required.",
        "err_action_required": "Action (key or mouse button) is required.",
        "err_min_greater_max": "Minimum interval cannot be greater than maximum.",
        "err_positive_integers": "Intervals must be positive integers.",
        "dlg_title_new": "Add New Function",
        "dlg_title_edit": "Edit Function",
        "dlg_trigger_section": "1. Trigger Key/Button:",
        "dlg_current_trigger": "Current Trigger: {value}",
        "dlg_no_trigger": "No trigger defined",
        "dlg_btn_capture_trigger": "Capture Trigger",
        "dlg_action_section": "2. Action Key/Button (to repeat):",
        "dlg_current_action_key": "Current Action: Key '{value}'",
        "dlg_current_action_mouse": "Current Action: Mouse '{value}'",
        "dlg_no_action": "No action defined",
        "dlg_btn_capture_action": "Capture Action",
        "dlg_interval_section": "3. Interval (ms) - Random Range:",
        "dlg_min": "Min:",
        "dlg_max": "Max:",
        "dlg_mode_section": "4. Repetition Mode:",
        "dlg_mode_continuous": "Continuous (hold)",
        "dlg_mode_once": "Once (on press)",
        "dlg_mode_toggle": "Toggle (on/off)",
        "dlg_capture_status": "Click 'Capture Trigger' or 'Capture Action'",
        "dlg_waiting_trigger": "Waiting for trigger... Press any key or mouse button.",
        "dlg_waiting_action": "Waiting for action... Press any key or mouse button.",
        "dlg_captured_trigger_key": "Trigger captured: Key '{value}'. Click 'Capture Action' or 'Save'.",
        "dlg_captured_trigger_mouse": "Trigger captured: Mouse '{value}'. Click 'Capture Action' or 'Save'.",
        "dlg_captured_action_key": "Action captured: Key '{value}'. Adjust interval and click 'Save'.",
        "dlg_captured_action_mouse": "Action captured: Mouse '{value}'. Adjust interval and click 'Save'.",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "splash_loading": "Loading AutoClick V6...",
        "lbl_language": "Language:",
        "test_config_title": "Detected Configuration",
        "test_lbl_input": "Input:",
        "test_lbl_key": "Key:",
        "test_lbl_interval": "Interval:",
        "test_lbl_mode": "Mode:",
        "test_btn_start": "Start Test",
        "test_btn_stop": "Stop Test",
        "test_btn_clear": "Clear Results",
        "test_stats_title": "Real-time Statistics",
        "test_stat_configured": "Configured interval:",
        "test_stat_avg": "Real average:",
        "test_stat_minmax": "Min / Max:",
        "test_stat_stddev": "Std deviation:",
        "test_stat_precision": "Precision:",
        "test_stat_total": "Total actions:",
        "test_log_title": "Measurements Log",
        "test_col_num": "#",
        "test_col_real_time": "Real Time (ms)",
        "test_col_deviation": "Deviation (ms)",
        "test_col_status": "Status",
        "test_suggestion_title": "Suggestion",
        "test_suggestion_overhead": "Average system overhead: {overhead}ms. To get exactly {target}ms, set interval to {suggested}ms.",
        "test_suggestion_excellent": "Timing is excellent, no adjustment needed.",
        "test_suggestion_waiting": "At least 20 measurements needed for suggestion...",
        "test_no_config": "Configure the main tab first before testing.",
    },
    "pt-br": {
        "window_title": "AutoClick V6 dev by jorgeRjunior",
        "tab_main": "Função Principal",
        "tab_custom": "Funções Personalizadas",
        "tab_test": "Testes",
        "title": "AutoClick V6",
        "subtitle": "dev by jorgeRjunior",
        "input_type_frame": "Tipo de Entrada",
        "radio_keyboard": "Teclado",
        "radio_mouse_left": "Mouse 1 (Esquerdo)",
        "radio_mouse_right": "Mouse 2 (Direito)",
        "radio_mouse_x2": "Mouse 4 (Lateral Frente)",
        "radio_mouse_x1": "Mouse 5 (Lateral Trás)",
        "lbl_key": "Tecla:",
        "interval_frame": "Intervalo (ms) - Range Aleatório",
        "lbl_min": "Mínimo:",
        "lbl_max": "Máximo:",
        "mode_frame": "Modo de Operação",
        "mode_hold": "Segurar para repetir",
        "mode_toggle": "Alternar (Iniciar/Parar)",
        "status_frame": "Status",
        "status_waiting": "Aguardando início...",
        "btn_start": "Iniciar",
        "btn_stop": "Parar",
        "info_text": "\nInstruções:\n- Mouse 1 = Botão esquerdo do mouse\n- Mouse 2 = Botão direito do mouse\n- Mouse 4 = Botão lateral da frente do mouse\n- Mouse 5 = Botão lateral de trás do mouse\n- Para teclas do teclado, digite a letra/tecla desejada\n- O intervalo é o tempo entre as repetições\n",
        "status_running": "Repetição automática em andamento...",
        "status_waiting_button": "Aguardando botão ser pressionado...",
        "status_started": "Programa iniciado! Aguardando comando...",
        "status_stopped": "Programa parado!",
        "status_toggle_on": "Repetição automática iniciada!",
        "status_toggle_off": "Repetição automática parada!",
        "err_no_key": "Erro: Digite uma tecla!",
        "err_positive": "Erro: Intervalos devem ser positivos!",
        "err_min_max": "Erro: Mínimo não pode ser maior que máximo!",
        "err_invalid_interval": "Erro: Intervalo inválido!",
        "custom_title": "Funções Personalizadas",
        "custom_instructions": "Configure até 10 teclas ou botões de mouse para ativar repetições automatizadas.",
        "btn_add_function": "Adicionar Nova Função",
        "btn_save_config": "Salvar Configurações",
        "col_active": "Ativo?",
        "col_trigger": "Tecla Gatilho",
        "col_action": "Ação",
        "col_type": "Tipo",
        "col_interval": "Intervalo Min-Max",
        "col_mode": "Modo",
        "col_actions": "Ações",
        "no_functions": "Não há funções personalizadas configuradas. Clique em 'Adicionar Nova Função'.",
        "type_keyboard": "Teclado",
        "type_mouse_left": "Mouse Esq.",
        "type_mouse_right": "Mouse Dir.",
        "type_mouse_middle": "Mouse Meio",
        "mode_continuous": "Contínuo",
        "mode_once": "Uma vez",
        "mode_toggle_display": "Alternar",
        "btn_edit": "Editar",
        "btn_delete": "Excluir",
        "limit_title": "Limite atingido",
        "limit_msg": "Você já atingiu o limite de 10 funções personalizadas.",
        "confirm_delete_title": "Confirmar exclusão",
        "confirm_delete_msg": "Tem certeza que deseja excluir esta função?",
        "err_title": "Erro",
        "err_trigger_required": "O gatilho é obrigatório.",
        "err_action_required": "A ação (tecla ou botão do mouse) é obrigatória.",
        "err_min_greater_max": "O intervalo mínimo não pode ser maior que o máximo.",
        "err_positive_integers": "Os intervalos devem ser números inteiros positivos.",
        "dlg_title_new": "Adicionar Nova Função",
        "dlg_title_edit": "Editar Função",
        "dlg_trigger_section": "1. Tecla/Botão Gatilho:",
        "dlg_current_trigger": "Gatilho Atual: {value}",
        "dlg_no_trigger": "Nenhum gatilho definido",
        "dlg_btn_capture_trigger": "Capturar Gatilho",
        "dlg_action_section": "2. Tecla/Botão de Ação (a repetir):",
        "dlg_current_action_key": "Ação Atual: Tecla '{value}'",
        "dlg_current_action_mouse": "Ação Atual: Mouse '{value}'",
        "dlg_no_action": "Nenhuma ação definida",
        "dlg_btn_capture_action": "Capturar Ação",
        "dlg_interval_section": "3. Intervalo (ms) - Range Aleatório:",
        "dlg_min": "Mín:",
        "dlg_max": "Máx:",
        "dlg_mode_section": "4. Modo de Repetição:",
        "dlg_mode_continuous": "Contínuo (segurar)",
        "dlg_mode_once": "Uma vez (ao pressionar)",
        "dlg_mode_toggle": "Alternar (liga/desliga)",
        "dlg_capture_status": "Clique em 'Capturar Gatilho' ou 'Capturar Ação'",
        "dlg_waiting_trigger": "Aguardando gatilho... Pressione qualquer tecla ou botão do mouse.",
        "dlg_waiting_action": "Aguardando ação... Pressione qualquer tecla ou botão do mouse.",
        "dlg_captured_trigger_key": "Gatilho capturado: Tecla '{value}'. Clique em 'Capturar Ação' ou 'Salvar'.",
        "dlg_captured_trigger_mouse": "Gatilho capturado: Mouse '{value}'. Clique em 'Capturar Ação' ou 'Salvar'.",
        "dlg_captured_action_key": "Ação capturada: Tecla '{value}'. Ajuste o intervalo e clique em 'Salvar'.",
        "dlg_captured_action_mouse": "Ação capturada: Mouse '{value}'. Ajuste o intervalo e clique em 'Salvar'.",
        "btn_save": "Salvar",
        "btn_cancel": "Cancelar",
        "splash_loading": "Carregando AutoClick V6...",
        "lbl_language": "Idioma:",
        "test_config_title": "Configuração Detectada",
        "test_lbl_input": "Entrada:",
        "test_lbl_key": "Tecla:",
        "test_lbl_interval": "Intervalo:",
        "test_lbl_mode": "Modo:",
        "test_btn_start": "Iniciar Teste",
        "test_btn_stop": "Parar Teste",
        "test_btn_clear": "Limpar Resultados",
        "test_stats_title": "Estatísticas em Tempo Real",
        "test_stat_configured": "Intervalo configurado:",
        "test_stat_avg": "Média real:",
        "test_stat_minmax": "Mín / Máx:",
        "test_stat_stddev": "Desvio padrão:",
        "test_stat_precision": "Precisão:",
        "test_stat_total": "Total de ações:",
        "test_log_title": "Log de Medições",
        "test_col_num": "#",
        "test_col_real_time": "Tempo Real (ms)",
        "test_col_deviation": "Desvio (ms)",
        "test_col_status": "Status",
        "test_suggestion_title": "Sugestão",
        "test_suggestion_overhead": "Overhead médio do sistema: {overhead}ms. Para obter exatamente {target}ms, configure o intervalo para {suggested}ms.",
        "test_suggestion_excellent": "O timing está excelente, nenhum ajuste necessário.",
        "test_suggestion_waiting": "São necessárias pelo menos 20 medições para sugestão...",
        "test_no_config": "Configure a aba principal antes de testar.",
    }
}

# Verify translation key parity
assert set(TRANSLATIONS["en"].keys()) == set(TRANSLATIONS["pt-br"].keys()), \
    f"Translation keys mismatch! EN-only: {set(TRANSLATIONS['en'].keys()) - set(TRANSLATIONS['pt-br'].keys())}, PT-only: {set(TRANSLATIONS['pt-br'].keys()) - set(TRANSLATIONS['en'].keys())}"


# --- High-Precision Sleep ---
def precision_sleep(seconds):
    """High-precision sleep using hybrid spin-wait approach."""
    if seconds <= 0:
        return
    target = time.perf_counter() + seconds
    # For very short intervals (<5ms), use pure spin-wait
    if seconds < 0.005:
        while time.perf_counter() < target:
            pass
        return
    # Sleep most of the time (leave ~2ms margin)
    sleep_time = seconds - 0.002
    if sleep_time > 0:
        time.sleep(sleep_time)
    # Busy-wait the last ~2ms for precision
    while time.perf_counter() < target:
        pass


class AutoClickerGUI:
    def __init__(self):
        self.root = tb.Window(themename="cosmo")
        self.root.geometry("700x680")
        self.root.resizable(True, True)

        # Language state (before load_config so it can be overwritten)
        self.current_language = "en"

        # Control variables
        self.input_type = tk.StringVar(value="keyboard")
        self.input_type.trace('w', self.on_input_type_change)
        self.mode = tk.StringVar(value="toggle")
        self.key = tk.StringVar()
        self.interval_min = tk.StringVar(value="80")
        self.interval_max = tk.StringVar(value="120")
        self.status_text = tk.StringVar(value="")

        # Program state
        self.running = False
        self.stop_event = Event()
        self.current_key = None
        self.current_input_type = None

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

        # Set initial status text after language is loaded
        self.status_text.set(self.t("status_waiting"))
        self.root.title(self.t("window_title"))

        # --- Toolbar with language selector ---
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill='x', padx=10, pady=(10, 0))

        self.lbl_lang = ttk.Label(self.toolbar, text=self.t("lbl_language"))
        self.lbl_lang.pack(side='right', padx=(0, 5))
        self.lang_combo = ttk.Combobox(
            self.toolbar,
            values=["English", "Português (BR)"],
            state="readonly",
            width=15
        )
        self.lang_combo.set("English" if self.current_language == "en" else "Português (BR)")
        self.lang_combo.pack(side='right')
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # --- Notebook for tabs ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text=self.t("tab_main"))

        self.custom_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.custom_tab, text=self.t("tab_custom"))

        self.test_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.test_tab, text=self.t("tab_test"))

        # Test tab state
        self.test_running = False
        self.test_stop_event = Event()
        self.test_thread = None
        self.test_measurements = []
        self.test_count = 0

        self.create_main_tab_widgets()
        self.create_custom_tab_widgets()
        self.create_test_tab_widgets()

        # Bind tab change for test tab refresh
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def t(self, key):
        """Get translated string for current language."""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS["en"]).get(key, key)

    def on_language_change(self, event=None):
        """Handle language selector change."""
        selected = self.lang_combo.get()
        self.current_language = "en" if selected == "English" else "pt-br"
        self.apply_language()
        self.save_config()

    def apply_language(self):
        """Update all UI text to current language."""
        # Window title
        self.root.title(self.t("window_title"))

        # Toolbar
        self.lbl_lang.configure(text=self.t("lbl_language"))

        # Notebook tabs
        self.notebook.tab(0, text=self.t("tab_main"))
        self.notebook.tab(1, text=self.t("tab_custom"))
        self.notebook.tab(2, text=self.t("tab_test"))

        # --- Main tab ---
        self.lbl_title.configure(text=self.t("title"))
        self.lbl_subtitle.configure(text=self.t("subtitle"))
        self.input_type_frame.configure(text=self.t("input_type_frame"))
        self.rb_keyboard.configure(text=self.t("radio_keyboard"))
        self.rb_mouse_left.configure(text=self.t("radio_mouse_left"))
        self.rb_mouse_right.configure(text=self.t("radio_mouse_right"))
        self.rb_mouse_x2.configure(text=self.t("radio_mouse_x2"))
        self.rb_mouse_x1.configure(text=self.t("radio_mouse_x1"))
        self.lbl_key_label.configure(text=self.t("lbl_key"))
        self.interval_frame_widget.configure(text=self.t("interval_frame"))
        self.lbl_interval_min.configure(text=self.t("lbl_min"))
        self.lbl_interval_max.configure(text=self.t("lbl_max"))
        self.mode_frame_widget.configure(text=self.t("mode_frame"))
        self.rb_hold.configure(text=self.t("mode_hold"))
        self.rb_toggle.configure(text=self.t("mode_toggle"))
        self.status_frame_widget.configure(text=self.t("status_frame"))
        self.start_button.configure(text=self.t("btn_start"))
        self.stop_button.configure(text=self.t("btn_stop"))
        self.lbl_info.configure(text=self.t("info_text"))

        # --- Custom tab ---
        self.lbl_custom_title.configure(text=self.t("custom_title"))
        self.lbl_custom_instructions.configure(text=self.t("custom_instructions"))
        self.btn_add.configure(text=self.t("btn_add_function"))
        self.btn_save_cfg.configure(text=self.t("btn_save_config"))
        self.refresh_mappings_display()

        # --- Test tab ---
        self.test_config_frame.configure(text=self.t("test_config_title"))
        self.test_lbl_input.configure(text=self.t("test_lbl_input"))
        self.test_lbl_key.configure(text=self.t("test_lbl_key"))
        self.test_lbl_interval.configure(text=self.t("test_lbl_interval"))
        self.test_lbl_mode.configure(text=self.t("test_lbl_mode"))
        self.test_btn_toggle.configure(
            text=self.t("test_btn_stop") if self.test_running else self.t("test_btn_start")
        )
        self.test_btn_clear.configure(text=self.t("test_btn_clear"))
        self.test_stats_frame.configure(text=self.t("test_stats_title"))
        self.test_lbl_stat_configured.configure(text=self.t("test_stat_configured"))
        self.test_lbl_stat_avg.configure(text=self.t("test_stat_avg"))
        self.test_lbl_stat_minmax.configure(text=self.t("test_stat_minmax"))
        self.test_lbl_stat_stddev.configure(text=self.t("test_stat_stddev"))
        self.test_lbl_stat_precision.configure(text=self.t("test_stat_precision"))
        self.test_lbl_stat_total.configure(text=self.t("test_stat_total"))
        self.test_log_frame.configure(text=self.t("test_log_title"))
        self.test_suggestion_frame.configure(text=self.t("test_suggestion_title"))
        self.refresh_test_config_display()

    def load_config(self):
        """Load configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_language = config.get('language', 'en')
                    loaded_mappings = config.get('custom_mappings', [])
                    self.custom_mappings = []
                    for m in loaded_mappings:
                        if 'once' in m and 'mode' not in m:
                            m['mode'] = 'once' if m['once'] else 'continuous'
                            del m['once']
                        elif 'mode' not in m:
                            m['mode'] = 'continuous'
                        if 'interval' in m and 'interval_min' not in m:
                            m['interval_min'] = m['interval']
                            m['interval_max'] = m['interval']
                            del m['interval']
                        m['is_active'] = m.get('is_active', False)
                        m['thread_ref'] = None
                        m['stop_event'] = None
                        m['is_trigger_down'] = False
                        m['is_repeating'] = False
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
                saved_m.pop('is_repeating', None)
                saved_m.pop('once', None)
                saved_m.pop('interval', None)
                mappings_to_save.append(saved_m)

            config = {
                'language': self.current_language,
                'custom_mappings': mappings_to_save
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
            messagebox.showerror(self.t("err_title"), f"Error saving config: {e}")

    def on_input_type_change(self, *args):
        """Callback para quando o tipo de entrada muda"""
        if hasattr(self, 'key_entry'):
            if self.input_type.get() == "keyboard":
                self.key_entry.configure(state='normal')
            else:
                self.key_entry.configure(state='disabled')
                self.key.set('')

    def create_social_button(self, frame, icon_url, link, row, column):
        try:
            response = requests.get(icon_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((20, 20))
            photo = ImageTk.PhotoImage(img)
            button = ttk.Button(
                frame, image=photo,
                command=lambda: webbrowser.open(link),
                bootstyle="link"
            )
            button.image = photo
            button.grid(row=row, column=column, padx=5)
        except Exception as e:
            print(f"Error loading social icon {icon_url}: {e}")
            button_text = "GitHub" if "github" in link else "Instagram"
            button = ttk.Button(
                frame, text=button_text,
                command=lambda: webbrowser.open(link),
                bootstyle="link"
            )
            button.grid(row=row, column=column, padx=5)

    def create_main_tab_widgets(self):
        main_frame = self.main_tab
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        self.lbl_title = ttk.Label(main_frame, text=self.t("title"), font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=2, pady=5)

        self.lbl_subtitle = ttk.Label(main_frame, text=self.t("subtitle"), font=("Helvetica", 10, "italic"))
        self.lbl_subtitle.grid(row=1, column=0, columnspan=2)

        # Social Media
        social_frame = ttk.Frame(main_frame)
        social_frame.grid(row=2, column=0, columnspan=2, pady=5)
        self.create_social_button(
            social_frame,
            "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            "https://github.com/jorgeRjunior", 0, 0
        )
        self.create_social_button(
            social_frame,
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/2048px-Instagram_icon.png",
            "https://www.instagram.com/jorge.r.jr", 0, 1
        )

        # Input Type
        self.input_type_frame = ttk.LabelFrame(main_frame, text=self.t("input_type_frame"), padding=5)
        self.input_type_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.rb_keyboard = ttk.Radiobutton(self.input_type_frame, text=self.t("radio_keyboard"), variable=self.input_type, value="keyboard")
        self.rb_keyboard.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.rb_mouse_left = ttk.Radiobutton(self.input_type_frame, text=self.t("radio_mouse_left"), variable=self.input_type, value="left")
        self.rb_mouse_left.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.rb_mouse_right = ttk.Radiobutton(self.input_type_frame, text=self.t("radio_mouse_right"), variable=self.input_type, value="right")
        self.rb_mouse_right.grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.rb_mouse_x2 = ttk.Radiobutton(self.input_type_frame, text=self.t("radio_mouse_x2"), variable=self.input_type, value="x2")
        self.rb_mouse_x2.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.rb_mouse_x1 = ttk.Radiobutton(self.input_type_frame, text=self.t("radio_mouse_x1"), variable=self.input_type, value="x1")
        self.rb_mouse_x1.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # Key
        key_frame = ttk.Frame(main_frame)
        key_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        key_frame.columnconfigure(1, weight=1)

        self.lbl_key_label = ttk.Label(key_frame, text=self.t("lbl_key"))
        self.lbl_key_label.grid(row=0, column=0, padx=5)
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key, width=10)
        self.key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.on_input_type_change()

        # Interval
        self.interval_frame_widget = ttk.LabelFrame(main_frame, text=self.t("interval_frame"), padding=5)
        self.interval_frame_widget.grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.interval_frame_widget.columnconfigure(1, weight=1)
        self.interval_frame_widget.columnconfigure(3, weight=1)

        self.lbl_interval_min = ttk.Label(self.interval_frame_widget, text=self.t("lbl_min"))
        self.lbl_interval_min.grid(row=0, column=0, padx=5)
        ttk.Entry(self.interval_frame_widget, textvariable=self.interval_min, width=8).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.lbl_interval_max = ttk.Label(self.interval_frame_widget, text=self.t("lbl_max"))
        self.lbl_interval_max.grid(row=0, column=2, padx=5)
        ttk.Entry(self.interval_frame_widget, textvariable=self.interval_max, width=8).grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)

        # Mode
        self.mode_frame_widget = ttk.LabelFrame(main_frame, text=self.t("mode_frame"), padding=10)
        self.mode_frame_widget.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.rb_hold = ttk.Radiobutton(self.mode_frame_widget, text=self.t("mode_hold"), variable=self.mode, value="hold")
        self.rb_hold.grid(row=0, column=0, padx=5, pady=2)
        self.rb_toggle = ttk.Radiobutton(self.mode_frame_widget, text=self.t("mode_toggle"), variable=self.mode, value="toggle")
        self.rb_toggle.grid(row=0, column=1, padx=5, pady=2)

        # Status
        self.status_frame_widget = ttk.LabelFrame(main_frame, text=self.t("status_frame"), padding=10)
        self.status_frame_widget.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.status_frame_widget.columnconfigure(0, weight=1)
        ttk.Label(self.status_frame_widget, textvariable=self.status_text).grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=8, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(control_frame, text=self.t("btn_start"), command=self.start_program)
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = ttk.Button(control_frame, text=self.t("btn_stop"), command=self.stop_program, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Info
        self.lbl_info = ttk.Label(main_frame, text=self.t("info_text"), justify=tk.LEFT)
        self.lbl_info.grid(row=9, column=0, columnspan=2, pady=10, sticky=(tk.W))

    def create_custom_tab_widgets(self):
        custom_frame = self.custom_tab
        custom_frame.columnconfigure(0, weight=1)
        custom_frame.columnconfigure(1, weight=1)

        self.lbl_custom_title = ttk.Label(custom_frame, text=self.t("custom_title"), font=("Helvetica", 14, "bold"))
        self.lbl_custom_title.grid(row=0, column=0, columnspan=2, pady=5)

        self.lbl_custom_instructions = ttk.Label(
            custom_frame, text=self.t("custom_instructions"), wraplength=450
        )
        self.lbl_custom_instructions.grid(row=1, column=0, columnspan=2, pady=5)

        self.mappings_frame = ttk.Frame(custom_frame)
        self.mappings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        for i in range(7):
            self.mappings_frame.columnconfigure(i, weight=1)

        button_frame = ttk.Frame(custom_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.btn_add = ttk.Button(button_frame, text=self.t("btn_add_function"), command=self.add_custom_mapping)
        self.btn_add.grid(row=0, column=0, padx=5)
        self.btn_save_cfg = ttk.Button(button_frame, text=self.t("btn_save_config"), command=self.save_config)
        self.btn_save_cfg.grid(row=0, column=1, padx=5)

        self.refresh_mappings_display()

        # Register hooks based on loaded active states
        self._active_hook_removers = {}
        self._running_threads = {}
        self.register_active_hooks()

    def refresh_mappings_display(self):
        """Refresh the display of custom mappings"""
        for widget in self.mappings_frame.winfo_children():
            widget.destroy()

        for i in range(7):
            self.mappings_frame.columnconfigure(i, weight=1)

        # Headers
        ttk.Label(self.mappings_frame, text=self.t("col_active"), width=5).grid(row=0, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text=self.t("col_trigger"), width=15).grid(row=0, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text=self.t("col_action"), width=15).grid(row=0, column=2, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text=self.t("col_type"), width=10).grid(row=0, column=3, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text=self.t("col_interval"), width=14).grid(row=0, column=4, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text=self.t("col_mode"), width=12).grid(row=0, column=5, padx=2, pady=2, sticky=(tk.W, tk.E))
        ttk.Label(self.mappings_frame, text=self.t("col_actions"), width=20).grid(row=0, column=6, padx=2, pady=2, sticky=(tk.W, tk.E))

        separator = ttk.Separator(self.mappings_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=5)

        if not self.custom_mappings:
            ttk.Label(
                self.mappings_frame, text=self.t("no_functions"),
                font=("Helvetica", 9, "italic")
            ).grid(row=2, column=0, columnspan=7, padx=5, pady=10, sticky=(tk.W, tk.E))
            return

        for i, mapping in enumerate(self.custom_mappings):
            if 'is_active' not in mapping:
                mapping['is_active'] = False
            if 'mode' not in mapping:
                mapping['mode'] = 'continuous'

            active_var = tk.BooleanVar(value=mapping['is_active'])
            chk = ttk.Checkbutton(
                self.mappings_frame, variable=active_var,
                command=lambda idx=i, var=active_var: self.toggle_mapping_active_state(idx, var)
            )
            chk.grid(row=i+2, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))

            ttk.Label(self.mappings_frame, text=mapping['trigger_key']).grid(row=i+2, column=1, padx=2, pady=2, sticky=(tk.W, tk.E))

            action_text = mapping.get('action_key', '') if mapping['action_type'] == 'keyboard' else f"Mouse {mapping['action_type']}"
            ttk.Label(self.mappings_frame, text=action_text).grid(row=i+2, column=2, padx=2, pady=2, sticky=(tk.W, tk.E))

            type_map = {
                'keyboard': self.t("type_keyboard"),
                'left': self.t("type_mouse_left"),
                'right': self.t("type_mouse_right"),
                'middle': self.t("type_mouse_middle")
            }
            type_display = type_map.get(mapping['action_type'], mapping['action_type'])
            ttk.Label(self.mappings_frame, text=type_display).grid(row=i+2, column=3, padx=2, pady=2, sticky=(tk.W, tk.E))

            interval_display = f"{mapping.get('interval_min', '100')}-{mapping.get('interval_max', '100')}"
            ttk.Label(self.mappings_frame, text=interval_display).grid(row=i+2, column=4, padx=2, pady=2, sticky=(tk.W, tk.E))

            mode_map = {
                'continuous': self.t("mode_continuous"),
                'once': self.t("mode_once"),
                'toggle': self.t("mode_toggle_display")
            }
            mode_display_text = mode_map.get(mapping['mode'], self.t("mode_continuous"))
            ttk.Label(self.mappings_frame, text=mode_display_text).grid(row=i+2, column=5, padx=2, pady=2, sticky=(tk.W, tk.E))

            buttons_frame = ttk.Frame(self.mappings_frame)
            buttons_frame.grid(row=i+2, column=6, padx=2, pady=2, sticky=(tk.W, tk.E))
            buttons_frame.columnconfigure(0, weight=1)
            buttons_frame.columnconfigure(1, weight=1)

            ttk.Button(buttons_frame, text=self.t("btn_edit"), width=8, command=lambda idx=i: self.edit_mapping(idx)).grid(row=0, column=0, padx=2)
            ttk.Button(buttons_frame, text=self.t("btn_delete"), width=8, command=lambda idx=i: self.delete_mapping(idx)).grid(row=0, column=1, padx=2)

    def add_custom_mapping(self):
        if len(self.custom_mappings) >= 10:
            messagebox.showwarning(self.t("limit_title"), self.t("limit_msg"))
            return
        self.open_mapping_dialog()

    def edit_mapping(self, index):
        if self.custom_mappings[index].get('is_active', False):
            self.custom_mappings[index]['is_active'] = False
            self.register_active_hooks()
            self.refresh_mappings_display()
        self.open_mapping_dialog(self.custom_mappings[index], index)

    def delete_mapping(self, index):
        if messagebox.askyesno(self.t("confirm_delete_title"), self.t("confirm_delete_msg")):
            mapping_to_delete = self.custom_mappings[index]
            if mapping_to_delete.get('is_active', False):
                mapping_to_delete['is_active'] = False
                self.register_active_hooks()
            else:
                self._stop_continuous_thread(index)

            del self.custom_mappings[index]
            self._active_hook_removers.pop(index, None)
            self._running_threads.pop(index, None)
            self.register_active_hooks()
            self.refresh_mappings_display()
            self.save_config()

    def open_mapping_dialog(self, mapping=None, edit_index=None):
        dialog = tb.Toplevel(self.root)
        dialog.title(self.t("dlg_title_new") if mapping is None else self.t("dlg_title_edit"))
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        dialog.grab_set()

        self.register_active_hooks(temporarily_disable=True)

        default_mode = 'continuous'
        if mapping and 'mode' in mapping:
            default_mode = mapping['mode']
        elif mapping and 'once' in mapping:
            default_mode = 'once' if mapping['once'] else 'continuous'

        if mapping is None:
            mapping = {
                'trigger_key': '', 'action_type': 'keyboard', 'action_key': '',
                'interval_min': '80', 'interval_max': '120', 'mode': default_mode,
                'is_active': False, 'thread_ref': None, 'stop_event': None,
                'is_trigger_down': False, 'is_repeating': False
            }
        else:
            mapping['thread_ref'] = None
            mapping['stop_event'] = None
            mapping['is_trigger_down'] = False
            mapping['is_repeating'] = False
            if 'mode' not in mapping:
                mapping['mode'] = default_mode

        trigger_key_var = tk.StringVar(value=mapping['trigger_key'])
        action_key_var = tk.StringVar(value=mapping.get('action_key', ''))
        action_type_var = tk.StringVar(value=mapping['action_type'])
        interval_min_var = tk.StringVar(value=mapping.get('interval_min', '80'))
        interval_max_var = tk.StringVar(value=mapping.get('interval_max', '120'))
        mode_var = tk.StringVar(value=mapping['mode'])

        capture_mode = None

        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=0)

        # 1. Trigger
        ttk.Label(main_frame, text=self.t("dlg_trigger_section"), font=("Helvetica", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(5, 0))

        trigger_text = self.t("dlg_current_trigger").format(value=trigger_key_var.get()) if trigger_key_var.get() else self.t("dlg_no_trigger")
        trigger_display_var = tk.StringVar(value=trigger_text)
        ttk.Label(main_frame, textvariable=trigger_display_var, wraplength=350).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        trigger_capture_button = ttk.Button(main_frame, text=self.t("dlg_btn_capture_trigger"))
        trigger_capture_button.grid(row=1, column=2, padx=5, pady=2, sticky=tk.E)

        # 2. Action
        ttk.Label(main_frame, text=self.t("dlg_action_section"), font=("Helvetica", 10, "bold")).grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))

        action_display_text = self.t("dlg_no_action")
        if action_key_var.get():
            if action_type_var.get() == 'keyboard':
                action_display_text = self.t("dlg_current_action_key").format(value=action_key_var.get())
            else:
                action_display_text = self.t("dlg_current_action_mouse").format(value=action_type_var.get())

        action_display_var = tk.StringVar(value=action_display_text)
        ttk.Label(main_frame, textvariable=action_display_var, wraplength=350).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        action_capture_button = ttk.Button(main_frame, text=self.t("dlg_btn_capture_action"))
        action_capture_button.grid(row=3, column=2, padx=5, pady=2, sticky=tk.E)

        # 3. Interval
        ttk.Label(main_frame, text=self.t("dlg_interval_section"), font=("Helvetica", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))

        interval_range_frame = ttk.Frame(main_frame)
        interval_range_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
        ttk.Label(interval_range_frame, text=self.t("dlg_min")).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Entry(interval_range_frame, textvariable=interval_min_var, width=8).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(interval_range_frame, text=self.t("dlg_max")).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Entry(interval_range_frame, textvariable=interval_max_var, width=8).pack(side=tk.LEFT)

        # 4. Mode
        ttk.Label(main_frame, text=self.t("dlg_mode_section"), font=("Helvetica", 10, "bold")).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))

        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=7, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(mode_frame, text=self.t("dlg_mode_continuous"), variable=mode_var, value='continuous').pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text=self.t("dlg_mode_once"), variable=mode_var, value='once').pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(mode_frame, text=self.t("dlg_mode_toggle"), variable=mode_var, value='toggle').pack(anchor=tk.W, pady=1)

        # Capture status
        capture_status_var = tk.StringVar(value=self.t("dlg_capture_status"))
        capture_status = ttk.Label(main_frame, textvariable=capture_status_var, font=("Helvetica", 9, "italic"), wraplength=380)
        capture_status.grid(row=8, column=0, columnspan=3, padx=5, pady=(10, 5))

        # Capture logic
        def start_capture(mode):
            nonlocal capture_mode
            capture_mode = mode
            if mode == 'trigger':
                capture_status_var.set(self.t("dlg_waiting_trigger"))
                trigger_capture_button.config(state=tk.DISABLED)
                action_capture_button.config(state=tk.NORMAL)
            else:
                capture_status_var.set(self.t("dlg_waiting_action"))
                action_capture_button.config(state=tk.DISABLED)
                trigger_capture_button.config(state=tk.NORMAL)
            dialog.focus_set()

        trigger_capture_button.configure(command=lambda: start_capture('trigger'))
        action_capture_button.configure(command=lambda: start_capture('action'))

        def on_key_press(e):
            nonlocal capture_mode
            key_name = e.name
            if capture_mode == 'trigger':
                trigger_key_var.set(key_name)
                trigger_display_var.set(self.t("dlg_current_trigger").format(value=key_name))
                capture_status_var.set(self.t("dlg_captured_trigger_key").format(value=key_name))
                trigger_capture_button.config(state=tk.NORMAL)
                capture_mode = None
                return False
            elif capture_mode == 'action':
                action_key_var.set(key_name)
                action_type_var.set('keyboard')
                action_display_var.set(self.t("dlg_current_action_key").format(value=key_name))
                capture_status_var.set(self.t("dlg_captured_action_key").format(value=key_name))
                action_capture_button.config(state=tk.NORMAL)
                capture_mode = None
                return False
            return True

        def dialog_mouse_handler(event):
            nonlocal capture_mode
            if not isinstance(event, mouse.ButtonEvent):
                return True
            if event.event_type == mouse.DOWN:
                button_name = event.button
                if capture_mode == 'trigger':
                    trigger_key_var.set(button_name)
                    trigger_display_var.set(self.t("dlg_captured_trigger_mouse").format(value=button_name))
                    capture_status_var.set(self.t("dlg_captured_trigger_mouse").format(value=button_name))
                    trigger_capture_button.config(state=tk.NORMAL)
                    capture_mode = None
                    return False
                elif capture_mode == 'action':
                    action_key_var.set('')
                    action_type_var.set(button_name)
                    action_display_var.set(self.t("dlg_current_action_mouse").format(value=button_name))
                    capture_status_var.set(self.t("dlg_captured_action_mouse").format(value=button_name))
                    action_capture_button.config(state=tk.NORMAL)
                    capture_mode = None
                    return False
            return True

        keyboard_hook = keyboard.hook(on_key_press)
        dialog_mouse_hook = mouse.hook(dialog_mouse_handler)

        # Bottom buttons
        fixed_frame = ttk.Frame(dialog)
        fixed_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        def save_mapping():
            try: keyboard.unhook(keyboard_hook)
            except Exception as e: print(f"Error unhooking dialog kbd: {e}")
            try: mouse.unhook(dialog_mouse_hook)
            except Exception as e: print(f"Error unhooking dialog mouse: {e}")

            if not trigger_key_var.get():
                messagebox.showerror(self.t("err_title"), self.t("err_trigger_required"), parent=dialog)
                dialog.destroy()
                return

            action_type = action_type_var.get()
            action_key = action_key_var.get()
            if not action_type or (action_type == 'keyboard' and not action_key):
                messagebox.showerror(self.t("err_title"), self.t("err_action_required"), parent=dialog)
                dialog.destroy()
                return

            try:
                imin = int(interval_min_var.get())
                imax = int(interval_max_var.get())
                if imin <= 0 or imax <= 0:
                    raise ValueError()
                if imin > imax:
                    messagebox.showerror(self.t("err_title"), self.t("err_min_greater_max"), parent=dialog)
                    return
            except ValueError:
                messagebox.showerror(self.t("err_title"), self.t("err_positive_integers"), parent=dialog)
                return

            new_mapping_data = {
                'trigger_key': trigger_key_var.get(),
                'action_type': action_type,
                'action_key': action_key if action_type == 'keyboard' else '',
                'interval_min': interval_min_var.get(),
                'interval_max': interval_max_var.get(),
                'mode': mode_var.get(),
            }

            if edit_index is not None:
                self.custom_mappings[edit_index].update(new_mapping_data)
                self.custom_mappings[edit_index]['is_active'] = True
                self.custom_mappings[edit_index]['thread_ref'] = None
                self.custom_mappings[edit_index]['stop_event'] = None
                self.custom_mappings[edit_index]['is_trigger_down'] = False
                self.custom_mappings[edit_index]['is_repeating'] = False
            else:
                if len(self.custom_mappings) >= 10:
                    messagebox.showwarning(self.t("limit_title"), self.t("limit_msg"), parent=dialog)
                    dialog.destroy()
                    return
                new_mapping_data['is_active'] = True
                new_mapping_data['thread_ref'] = None
                new_mapping_data['stop_event'] = None
                new_mapping_data['is_trigger_down'] = False
                new_mapping_data['is_repeating'] = False
                self.custom_mappings.append(new_mapping_data)

            self.refresh_mappings_display()
            self.save_config()
            self.register_active_hooks()
            dialog.destroy()

        def cancel_dialog():
            try: keyboard.unhook(keyboard_hook)
            except Exception as e: print(f"Error unhooking dialog kbd: {e}")
            try: mouse.unhook(dialog_mouse_hook)
            except Exception as e: print(f"Error unhooking dialog mouse: {e}")
            self.register_active_hooks()
            dialog.destroy()

        save_button = ttk.Button(fixed_frame, text=self.t("btn_save"), command=save_mapping, width=10)
        save_button.pack(side=tk.LEFT, padx=5)
        cancel_button = ttk.Button(fixed_frame, text=self.t("btn_cancel"), command=cancel_dialog, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)

        dialog.protocol("WM_DELETE_WINDOW", cancel_dialog)
        dialog.focus_set()

    # =====================================================
    # ============== TEST TAB =============================
    # =====================================================

    def create_test_tab_widgets(self):
        test_frame = self.test_tab
        test_frame.columnconfigure(0, weight=1)

        # --- Config panel ---
        self.test_config_frame = ttk.LabelFrame(test_frame, text=self.t("test_config_title"), padding=10)
        self.test_config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))
        self.test_config_frame.columnconfigure(1, weight=1)
        self.test_config_frame.columnconfigure(3, weight=1)

        self.test_lbl_input = ttk.Label(self.test_config_frame, text=self.t("test_lbl_input"))
        self.test_lbl_input.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.test_lbl_input_val = ttk.Label(self.test_config_frame, text="—")
        self.test_lbl_input_val.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        self.test_lbl_key = ttk.Label(self.test_config_frame, text=self.t("test_lbl_key"))
        self.test_lbl_key.grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.test_lbl_key_val = ttk.Label(self.test_config_frame, text="—")
        self.test_lbl_key_val.grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)

        self.test_lbl_interval = ttk.Label(self.test_config_frame, text=self.t("test_lbl_interval"))
        self.test_lbl_interval.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.test_lbl_interval_val = ttk.Label(self.test_config_frame, text="—")
        self.test_lbl_interval_val.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        self.test_lbl_mode = ttk.Label(self.test_config_frame, text=self.t("test_lbl_mode"))
        self.test_lbl_mode.grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        self.test_lbl_mode_val = ttk.Label(self.test_config_frame, text="—")
        self.test_lbl_mode_val.grid(row=1, column=3, padx=5, pady=2, sticky=tk.W)

        # --- Control buttons ---
        btn_frame = ttk.Frame(test_frame)
        btn_frame.grid(row=1, column=0, pady=5)

        self.test_btn_toggle = ttk.Button(btn_frame, text=self.t("test_btn_start"), command=self.toggle_test, bootstyle="success")
        self.test_btn_toggle.pack(side=tk.LEFT, padx=5)
        self.test_btn_clear = ttk.Button(btn_frame, text=self.t("test_btn_clear"), command=self.clear_test, bootstyle="warning")
        self.test_btn_clear.pack(side=tk.LEFT, padx=5)

        # --- Statistics panel ---
        self.test_stats_frame = ttk.LabelFrame(test_frame, text=self.t("test_stats_title"), padding=10)
        self.test_stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        self.test_stats_frame.columnconfigure(1, weight=1)
        self.test_stats_frame.columnconfigure(3, weight=1)

        self.test_lbl_stat_configured = ttk.Label(self.test_stats_frame, text=self.t("test_stat_configured"))
        self.test_lbl_stat_configured.grid(row=0, column=0, padx=5, pady=1, sticky=tk.W)
        self.test_stat_configured_val = ttk.Label(self.test_stats_frame, text="—", font=("Helvetica", 10, "bold"))
        self.test_stat_configured_val.grid(row=0, column=1, padx=5, pady=1, sticky=tk.W)

        self.test_lbl_stat_avg = ttk.Label(self.test_stats_frame, text=self.t("test_stat_avg"))
        self.test_lbl_stat_avg.grid(row=0, column=2, padx=5, pady=1, sticky=tk.W)
        self.test_stat_avg_val = ttk.Label(self.test_stats_frame, text="—", font=("Helvetica", 10, "bold"))
        self.test_stat_avg_val.grid(row=0, column=3, padx=5, pady=1, sticky=tk.W)

        self.test_lbl_stat_minmax = ttk.Label(self.test_stats_frame, text=self.t("test_stat_minmax"))
        self.test_lbl_stat_minmax.grid(row=1, column=0, padx=5, pady=1, sticky=tk.W)
        self.test_stat_minmax_val = ttk.Label(self.test_stats_frame, text="—")
        self.test_stat_minmax_val.grid(row=1, column=1, padx=5, pady=1, sticky=tk.W)

        self.test_lbl_stat_stddev = ttk.Label(self.test_stats_frame, text=self.t("test_stat_stddev"))
        self.test_lbl_stat_stddev.grid(row=1, column=2, padx=5, pady=1, sticky=tk.W)
        self.test_stat_stddev_val = ttk.Label(self.test_stats_frame, text="—")
        self.test_stat_stddev_val.grid(row=1, column=3, padx=5, pady=1, sticky=tk.W)

        self.test_lbl_stat_precision = ttk.Label(self.test_stats_frame, text=self.t("test_stat_precision"))
        self.test_lbl_stat_precision.grid(row=2, column=0, padx=5, pady=1, sticky=tk.W)
        self.test_stat_precision_val = ttk.Label(self.test_stats_frame, text="—", font=("Helvetica", 10, "bold"))
        self.test_stat_precision_val.grid(row=2, column=1, padx=5, pady=1, sticky=tk.W)

        self.test_lbl_stat_total = ttk.Label(self.test_stats_frame, text=self.t("test_stat_total"))
        self.test_lbl_stat_total.grid(row=2, column=2, padx=5, pady=1, sticky=tk.W)
        self.test_stat_total_val = ttk.Label(self.test_stats_frame, text="0")
        self.test_stat_total_val.grid(row=2, column=3, padx=5, pady=1, sticky=tk.W)

        # --- Measurements log ---
        self.test_log_frame = ttk.LabelFrame(test_frame, text=self.t("test_log_title"), padding=5)
        self.test_log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        test_frame.rowconfigure(3, weight=1)
        self.test_log_frame.columnconfigure(0, weight=1)
        self.test_log_frame.rowconfigure(0, weight=1)

        cols = ("num", "real_time", "deviation", "status")
        self.test_tree = ttk.Treeview(self.test_log_frame, columns=cols, show="headings", height=8)
        self.test_tree.heading("num", text=self.t("test_col_num"))
        self.test_tree.heading("real_time", text=self.t("test_col_real_time"))
        self.test_tree.heading("deviation", text=self.t("test_col_deviation"))
        self.test_tree.heading("status", text=self.t("test_col_status"))
        self.test_tree.column("num", width=50, anchor="center")
        self.test_tree.column("real_time", width=120, anchor="center")
        self.test_tree.column("deviation", width=120, anchor="center")
        self.test_tree.column("status", width=80, anchor="center")

        self.test_tree.tag_configure("ok", foreground="#28a745")
        self.test_tree.tag_configure("warn", foreground="#ffc107")
        self.test_tree.tag_configure("bad", foreground="#dc3545")

        scrollbar = ttk.Scrollbar(self.test_log_frame, orient="vertical", command=self.test_tree.yview)
        self.test_tree.configure(yscrollcommand=scrollbar.set)
        self.test_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # --- Suggestion panel ---
        self.test_suggestion_frame = ttk.LabelFrame(test_frame, text=self.t("test_suggestion_title"), padding=10)
        self.test_suggestion_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=(5, 10))

        self.test_suggestion_var = tk.StringVar(value=self.t("test_suggestion_waiting"))
        ttk.Label(self.test_suggestion_frame, textvariable=self.test_suggestion_var, wraplength=600).pack(fill='x')

    def on_tab_changed(self, event=None):
        """Refresh test tab config display when switching to it."""
        try:
            current = self.notebook.index(self.notebook.select())
            if current == 2:
                self.refresh_test_config_display()
        except Exception:
            pass

    def refresh_test_config_display(self):
        """Update the test tab's config panel with current tab 1 settings."""
        input_type = self.input_type.get()
        key = self.key.get()
        imin = self.interval_min.get()
        imax = self.interval_max.get()
        mode = self.mode.get()

        input_display = {
            'keyboard': self.t("radio_keyboard"),
            'left': self.t("radio_mouse_left"),
            'right': self.t("radio_mouse_right"),
            'x2': self.t("radio_mouse_x2"),
            'x1': self.t("radio_mouse_x1"),
        }.get(input_type, input_type)

        self.test_lbl_input_val.configure(text=input_display)
        self.test_lbl_key_val.configure(text=key if key else "—")
        self.test_lbl_interval_val.configure(
            text=f"{imin}ms" if imin == imax else f"{imin}-{imax}ms"
        )
        mode_display = {
            'hold': self.t("mode_hold"),
            'toggle': self.t("mode_toggle"),
        }.get(mode, mode)
        self.test_lbl_mode_val.configure(text=mode_display)

    def toggle_test(self):
        if self.test_running:
            self.stop_test()
        else:
            self.start_test()

    def start_test(self):
        """Start the timing test."""
        # Mutual exclusivity: stop main tab if running
        if self.running:
            self.stop_program()

        self.test_running = True
        self.test_stop_event.clear()
        self.test_measurements = []
        self.test_count = 0
        self.test_btn_toggle.configure(text=self.t("test_btn_stop"), bootstyle="danger")

        # Refresh config display
        self.refresh_test_config_display()

        # Start test loop thread
        self.test_thread = Thread(target=self.test_loop, daemon=True)
        self.test_thread.start()

        # Start UI update timer
        self.update_test_stats()

    def stop_test(self):
        """Stop the timing test."""
        self.test_stop_event.set()
        self.test_running = False
        self.test_btn_toggle.configure(text=self.t("test_btn_start"), bootstyle="success")

    def clear_test(self):
        """Clear test results."""
        self.test_measurements = []
        self.test_count = 0
        for item in self.test_tree.get_children():
            self.test_tree.delete(item)
        self.test_stat_configured_val.configure(text="—")
        self.test_stat_avg_val.configure(text="—")
        self.test_stat_minmax_val.configure(text="—")
        self.test_stat_stddev_val.configure(text="—")
        self.test_stat_precision_val.configure(text="—")
        self.test_stat_total_val.configure(text="0")
        self.test_suggestion_var.set(self.t("test_suggestion_waiting"))

    def test_loop(self):
        """Simulated timing loop that measures precision_sleep accuracy."""
        try:
            interval_min_ms = float(self.interval_min.get())
            interval_max_ms = float(self.interval_max.get())
        except ValueError:
            return

        interval_min_s = interval_min_ms / 1000.0
        interval_max_s = interval_max_ms / 1000.0

        if interval_min_s <= 0 or interval_max_s <= 0:
            return

        prev_time = time.perf_counter()

        # First iteration - just sleep, no measurement
        interval = random.uniform(interval_min_s, interval_max_s)
        t_action_start = time.perf_counter()
        time.sleep(0.0005)  # Simulate action overhead
        action_overhead = time.perf_counter() - t_action_start
        precision_sleep(max(0, interval - action_overhead))
        prev_time = time.perf_counter()

        while not self.test_stop_event.is_set():
            interval = random.uniform(interval_min_s, interval_max_s)

            # Simulate action overhead (~0.5ms)
            t_action_start = time.perf_counter()
            time.sleep(0.0005)
            action_overhead = time.perf_counter() - t_action_start

            # Precision sleep with compensation
            precision_sleep(max(0, interval - action_overhead))

            # Measure actual time
            now = time.perf_counter()
            actual_ms = (now - prev_time) * 1000.0
            prev_time = now

            self.test_measurements.append(actual_ms)
            self.test_count += 1

            # Keep max 100 measurements
            if len(self.test_measurements) > 100:
                self.test_measurements.pop(0)

    def update_test_stats(self):
        """Update test statistics display every 250ms."""
        if not self.test_running:
            return

        measurements = self.test_measurements.copy()

        if len(measurements) > 1:
            target_min = float(self.interval_min.get())
            target_max = float(self.interval_max.get())
            target = (target_min + target_max) / 2.0

            avg = sum(measurements) / len(measurements)
            mn = min(measurements)
            mx = max(measurements)

            variance = sum((x - avg) ** 2 for x in measurements) / len(measurements)
            stddev = math.sqrt(variance)

            precision = max(0, 1 - abs(avg - target) / target) * 100 if target > 0 else 0

            configured_text = f"{target_min:.0f}ms" if target_min == target_max else f"{target_min:.0f}-{target_max:.0f}ms"
            self.test_stat_configured_val.configure(text=configured_text)
            self.test_stat_avg_val.configure(text=f"{avg:.1f}ms")
            self.test_stat_minmax_val.configure(text=f"{mn:.1f}ms / {mx:.1f}ms")
            self.test_stat_stddev_val.configure(text=f"\u00b1{stddev:.1f}ms")
            self.test_stat_precision_val.configure(text=f"{precision:.1f}%")
            self.test_stat_total_val.configure(text=str(self.test_count))

            self.update_test_treeview(measurements, target, target_min, target_max)
            self.update_test_suggestion(measurements, target)

        if self.test_running:
            self.root.after(250, self.update_test_stats)

    def update_test_treeview(self, measurements, target, target_min, target_max):
        """Update the measurements treeview."""
        for item in self.test_tree.get_children():
            self.test_tree.delete(item)

        for i, ms in enumerate(reversed(measurements)):
            num = self.test_count - i
            deviation = ms - target

            if target_min <= ms <= target_max:
                status, tag = "OK", "ok"
            elif target > 0 and abs(deviation) / target <= 0.05:
                status, tag = "OK", "ok"
            elif target > 0 and abs(deviation) / target <= 0.10:
                status = "High" if deviation > 0 else "Low"
                tag = "warn"
            else:
                status = "High" if deviation > 0 else "Low"
                tag = "bad"

            self.test_tree.insert("", "end",
                values=(num, f"{ms:.1f}", f"{deviation:+.1f}", status),
                tags=(tag,)
            )

    def update_test_suggestion(self, measurements, target):
        """Update the suggestion panel based on measurements."""
        if len(measurements) < 20:
            self.test_suggestion_var.set(self.t("test_suggestion_waiting"))
            return

        avg = sum(measurements) / len(measurements)
        precision = max(0, 1 - abs(avg - target) / target) * 100 if target > 0 else 0

        if precision >= 98:
            self.test_suggestion_var.set(self.t("test_suggestion_excellent"))
        else:
            overhead = avg - target
            suggested = target - overhead
            text = self.t("test_suggestion_overhead").format(
                overhead=f"{overhead:+.1f}",
                target=f"{target:.0f}",
                suggested=f"{suggested:.0f}"
            )
            self.test_suggestion_var.set(text)

    # =====================================================
    # ============== EXISTING ACTION LOGIC ================
    # =====================================================

    def activate_all_mappings(self):
        self.deactivate_all_mappings()
        if not self.custom_mappings:
            return
        for mapping in self.custom_mappings:
            trigger_key = mapping['trigger_key']
            action_type = mapping['action_type']
            action_key = mapping['action_key']
            interval_min = int(mapping.get('interval_min', '100'))
            interval_max = int(mapping.get('interval_max', '100'))
            once = mapping.get('once', False)
            stop_event = Event()
            self.active_mappings.append({'mapping': mapping, 'stop_event': stop_event})

            def create_handler(m, stop_evt):
                def handler(event=None):
                    if m['once']:
                        if m['action_type'] == 'keyboard':
                            keyboard.send(m['action_key'])
                        else:
                            mouse.click(button=m['action_type'])
                    else:
                        thread = Thread(target=self.run_custom_mapping, args=(m, stop_evt), daemon=True)
                        self.custom_mapping_threads.append(thread)
                        thread.start()
                return handler

            handler = create_handler(mapping, stop_event)
            if trigger_key in ['left', 'right', 'middle', 'x1', 'x2']:
                if trigger_key == 'left':
                    mouse.on_click(lambda: handler())
                elif trigger_key == 'right':
                    mouse.on_right_click(lambda: handler())
                elif trigger_key == 'middle':
                    mouse.on_middle_click(lambda: handler())
            else:
                keyboard.on_press_key(trigger_key, handler)

    def deactivate_all_mappings(self):
        for active in self.active_mappings:
            active['stop_event'].set()
        keyboard.unhook_all()
        self.active_mappings = []
        self.custom_mapping_threads = []

    def run_custom_mapping(self, index, stop_event):
        """Runs the continuous action loop for a custom mapping."""
        if not (0 <= index < len(self.custom_mappings)):
            return

        mapping = self.custom_mappings[index]
        mode = mapping.get('mode', 'continuous')
        trigger_key = mapping['trigger_key']
        action_type = mapping['action_type']
        action_key = mapping.get('action_key', '')
        is_mouse_trigger = trigger_key in ['left', 'right', 'middle', 'x1', 'x2']

        interval_min = 0.01
        interval_max = 0.01
        try:
            interval_min = float(mapping.get('interval_min', '100')) / 1000
            interval_max = float(mapping.get('interval_max', '100')) / 1000
            if interval_min <= 0: interval_min = 0.01
            if interval_max <= 0: interval_max = 0.01
            if interval_min > interval_max: interval_min, interval_max = interval_max, interval_min
        except ValueError:
            pass

        while not stop_event.is_set():
            try:
                if mode == 'continuous':
                    trigger_pressed = False
                    if is_mouse_trigger:
                        trigger_pressed = mouse.is_pressed(button=trigger_key)
                    else:
                        trigger_pressed = keyboard.is_pressed(trigger_key)
                    if not trigger_pressed:
                        break

                # Perform action with dynamic compensation
                interval = random.uniform(interval_min, interval_max)
                t_action_start = time.perf_counter()
                if action_type == 'keyboard':
                    keyboard.send(action_key)
                else:
                    mouse.click(button=action_type)
                action_overhead = time.perf_counter() - t_action_start
                precision_sleep(max(0, interval - action_overhead))

            except Exception as e:
                print(f"Error in custom mapping thread for index {index}: {e}")
                break

        if index in self._running_threads and self._running_threads[index][1] == stop_event:
            del self._running_threads[index]

    def hold_press(self):
        """Hold mode action loop."""
        while not self.stop_event.is_set():
            try:
                if self.current_input_type == "keyboard":
                    estado_atual = keyboard.is_pressed(self.current_key)
                else:
                    estado_atual = mouse.is_pressed(button=self.current_input_type)

                if estado_atual:
                    self.status_text.set(self.t("status_running"))
                    imin = float(self.interval_min.get()) / 1000
                    imax = float(self.interval_max.get()) / 1000
                    interval = random.uniform(imin, imax)
                    t_action_start = time.perf_counter()
                    if self.current_input_type == "keyboard":
                        keyboard.send(self.current_key)
                    else:
                        mouse.click(button=self.current_input_type)
                    action_overhead = time.perf_counter() - t_action_start
                    precision_sleep(max(0, interval - action_overhead))
                else:
                    self.status_text.set(self.t("status_waiting_button"))
                    time.sleep(0.01)
            except Exception as e:
                print(f"Error in hold_press: {e}")
                time.sleep(0.1)

    def auto_press(self):
        """Toggle mode auto-press loop."""
        while self.running and not self.stop_event.is_set():
            try:
                imin = float(self.interval_min.get()) / 1000
                imax = float(self.interval_max.get()) / 1000
                interval = random.uniform(imin, imax)
                t_action_start = time.perf_counter()
                if self.current_input_type == "keyboard":
                    keyboard.send(self.current_key)
                else:
                    mouse.click(button=self.current_input_type)
                action_overhead = time.perf_counter() - t_action_start
                precision_sleep(max(0, interval - action_overhead))
            except Exception as e:
                print(f"Error in auto_press: {e}")
                break

    def validate_inputs(self):
        if self.input_type.get() == "keyboard" and not self.key.get():
            self.status_text.set(self.t("err_no_key"))
            return False
        try:
            imin = float(self.interval_min.get())
            imax = float(self.interval_max.get())
            if imin <= 0 or imax <= 0:
                self.status_text.set(self.t("err_positive"))
                return False
            if imin > imax:
                self.status_text.set(self.t("err_min_max"))
                return False
        except ValueError:
            self.status_text.set(self.t("err_invalid_interval"))
            return False
        return True

    def start_program(self):
        if not self.validate_inputs():
            return

        # Mutual exclusivity: stop test if running
        if self.test_running:
            self.stop_test()

        self.stop_event.set()
        time.sleep(0.1)
        self.stop_event.clear()

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
            Thread(target=self.hold_press, daemon=True).start()

        self.status_text.set(self.t("status_started"))

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
        self.status_text.set(self.t("status_stopped"))

    def toggle_action(self, event=None):
        if not self.running:
            self.status_text.set(self.t("status_toggle_on"))
            self.running = True
            self.stop_event.clear()
            Thread(target=self.auto_press, daemon=True).start()
        else:
            self.status_text.set(self.t("status_toggle_off"))
            self.running = False
            self.stop_event.set()

    def toggle_mapping_active_state(self, index, var):
        if 0 <= index < len(self.custom_mappings):
            mapping = self.custom_mappings[index]
            is_active = var.get()
            mapping['is_active'] = is_active
            if not is_active:
                mapping['is_repeating'] = False
                self._stop_continuous_thread(index)
            self.register_active_hooks()
            self.save_config()

    def _stop_continuous_thread(self, index):
        if index in self._running_threads:
            _thread, stop_event = self._running_threads[index]
            if stop_event:
                stop_event.set()

    def register_active_hooks(self, temporarily_disable=False):
        hook_action = "Disabling" if temporarily_disable else "Registering"
        indices_to_clear_toggle = list(self.toggle_registry.keys())
        for index in indices_to_clear_toggle:
            toggle_info = self.toggle_registry.get(index)
            if toggle_info and toggle_info.get('stop_event'):
                toggle_info['stop_event'].set()
        indices_to_clear_cont = list(self._running_threads.keys())
        for index in indices_to_clear_cont:
            self._stop_continuous_thread(index)
        self._running_threads.clear()

        for index, removers in list(self._active_hook_removers.items()):
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
        any_mouse_trigger_active = False
        for i, mapping in enumerate(self.custom_mappings):
            mapping['is_trigger_down'] = False
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
                        else:
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
                    mapping['is_active'] = False
                    self.root.after(10, self.refresh_mappings_display)

        if any_mouse_trigger_active and not self._global_mouse_hook_registered:
            try:
                mouse.hook(self.global_mouse_event_handler)
                self._global_mouse_hook_registered = True
            except Exception as e:
                print(f"    XXX [{hook_action} Hooks] Error registering global mouse hook: {e}")

    def handle_toggle_trigger(self, index, event_type):
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
                    thread = Thread(target=self.toggle_repeater_thread, args=(index, stop_event), daemon=True)
                    toggle_info = {'active': True, 'thread': thread, 'stop_event': stop_event}
                    self.toggle_registry[index] = toggle_info
                    thread.start()
            return False
        elif event_type == 'release':
            return False
        return True

    def toggle_repeater_thread(self, index, stop_event):
        if not (0 <= index < len(self.custom_mappings)):
            return
        mapping = self.custom_mappings[index]
        action_type = mapping.get('action_type', 'keyboard')
        action_key = mapping.get('action_key', '')

        try:
            interval_min = float(mapping.get('interval_min', '100')) / 1000
            interval_max = float(mapping.get('interval_max', '100')) / 1000
            if interval_min <= 0: interval_min = 0.01
            if interval_max <= 0: interval_max = 0.01
            if interval_min > interval_max: interval_min, interval_max = interval_max, interval_min
        except ValueError:
            interval_min = 0.1
            interval_max = 0.1

        try:
            while not stop_event.is_set():
                if not (0 <= index < len(self.custom_mappings)):
                    break
                if not mapping.get('is_active', False):
                    break

                try:
                    interval = random.uniform(interval_min, interval_max)
                    t_action_start = time.perf_counter()
                    if action_type == 'keyboard':
                        keyboard.send(action_key)
                    else:
                        mouse.click(button=action_type)
                    action_overhead = time.perf_counter() - t_action_start
                    precision_sleep(max(0, interval - action_overhead))
                except Exception as action_error:
                    print(f"[TOGGLE Thread] Error performing action: {action_error}")

                if stop_event.is_set():
                    break

        except Exception as e:
            print(f"[TOGGLE Thread] Error in toggle thread for index {index}: {e}")
        finally:
            self.toggle_cleanup_indices.append(index)
            self.root.after(100, self.toggle_registry_cleanup)

    def toggle_registry_cleanup(self):
        if not self.toggle_cleanup_indices:
            return
        for index in self.toggle_cleanup_indices:
            if index in self.toggle_registry:
                del self.toggle_registry[index]
        self.toggle_cleanup_indices.clear()

    def handle_custom_trigger(self, index, event_type):
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
                        else:
                            self.handle_custom_trigger(i, event_type_str)
        return True

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    close_splash(splash)
    app = AutoClickerGUI()
    try:
        app.run()
    finally:
        if sys.platform == 'win32':
            try:
                _winmm.timeEndPeriod(1)
            except Exception:
                pass
