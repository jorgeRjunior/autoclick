try:
    import keyboard
    import mouse
except ImportError:
    import pip

    pip.main(['install', 'keyboard', 'mouse'])
    import keyboard
    import mouse

import tkinter as tk
from tkinter import ttk
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import time
import sys
import os
from threading import Thread, Event


class AutoClickerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoClick V3 dev by jorgeRjunior")
        self.root.geometry("400x700")
        self.root.resizable(False, False)

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

        self.create_widgets()

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

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Título
        title_label = ttk.Label(main_frame, text="AutoClick V3", font=("Helvetica", 16, "bold"))
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
        ttk.Radiobutton(input_frame, text="Mouse 1 (Esquerdo)", variable=self.input_type, value="left").grid(row=0,
                                                                                                             column=1)
        ttk.Radiobutton(input_frame, text="Mouse 2 (Direito)", variable=self.input_type, value="right").grid(row=1,
                                                                                                             column=0)
        ttk.Radiobutton(input_frame, text="Mouse 4 (Lateral Frente)", variable=self.input_type, value="x2").grid(row=1,
                                                                                                                 column=1)
        ttk.Radiobutton(input_frame, text="Mouse 5 (Lateral Trás)", variable=self.input_type, value="x1").grid(row=2,
                                                                                                               column=0,
                                                                                                               columnspan=2)

        # Tecla (quando teclado selecionado)
        key_frame = ttk.Frame(main_frame)
        key_frame.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Label(key_frame, text="Tecla:").grid(row=0, column=0, padx=5)
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key, width=10)
        self.key_entry.grid(row=0, column=1)

        # Configura o estado inicial do campo de tecla
        self.on_input_type_change()

        # Intervalo
        interval_frame = ttk.Frame(main_frame)
        interval_frame.grid(row=5, column=0, columnspan=2, pady=5)

        ttk.Label(interval_frame, text="Intervalo (ms):").grid(row=0, column=0, padx=5)
        ttk.Entry(interval_frame, textvariable=self.interval, width=10).grid(row=0, column=1)

        # Modo de operação
        mode_frame = ttk.LabelFrame(main_frame, text="Modo de Operação", padding=10)
        mode_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Radiobutton(mode_frame, text="Segurar para repetir", variable=self.mode, value="hold").grid(row=0, column=0)
        ttk.Radiobutton(mode_frame, text="Alternar (Iniciar/Parar)", variable=self.mode, value="toggle").grid(row=0,
                                                                                                              column=1)

        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(status_frame, textvariable=self.status_text).grid(row=0, column=0)

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
        info_label.grid(row=9, column=0, columnspan=2, pady=10)

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
            Thread(target=self.auto_press).start()
        else:
            self.status_text.set("Repetição automática parada!")
            self.running = False
            self.stop_event.set()

    def hold_press(self):
        """Método para o modo 'Segurar para repetir'"""
        while not self.stop_event.is_set():
            try:
                # Verifica se o botão está pressionado atualmente
                if self.current_input_type == "keyboard":
                    estado_atual = keyboard.is_pressed(self.current_key)
                else:
                    estado_atual = mouse.is_pressed(button=self.current_key)

                # Se o botão estiver pressionado, executa a ação
                if estado_atual:
                    self.status_text.set("Repetição automática em andamento...")
                    # Executa a ação
                    if self.current_input_type == "keyboard":
                        keyboard.send(self.current_key)
                    else:
                        mouse.click(button=self.current_key)

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
                    mouse.click(button=self.current_key)
                time.sleep(intervalo)
            except Exception as e:
                print(f"Erro em auto_press: {e}")
                break

    def auto_press(self):
        intervalo = float(self.interval.get()) / 1000  # Converte ms para segundos
        while self.running and not self.stop_event.is_set():
            try:
                if self.current_input_type == "keyboard":
                    keyboard.send(self.current_key)
                else:
                    # Usa o mesmo mapeamento de botões para consistência
                    mouse.click(button=self.current_key)
                time.sleep(intervalo)
            except Exception as e:
                print(f"Erro em auto_press: {e}")
                break

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoClickerGUI()
    app.run()
