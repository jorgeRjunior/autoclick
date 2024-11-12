try:
    import keyboard
    import mouse
except ImportError:
    import pip

    pip.main(['install', 'keyboard', 'mouse'])
    import keyboard
    import mouse

import time
import sys
import os
from threading import Thread, Event


class AutoPresser:
    def __init__(self):
        self.running = False
        self.stop_event = Event()
        self.input_type = None
        self.key = None
        self.interval = None
        self.mode = None  # 'hold' ou 'toggle'

    def get_valid_interval(self):
        while True:
            try:
                ms = float(input("\nInsira o tempo em ms (exemplo: 100): "))
                if ms <= 0:
                    print("Por favor, insira um valor positivo!")
                    continue
                return ms / 1000  # Converte ms para segundos
            except ValueError:
                print("Por favor, insira um número válido!")

    def get_key_choice(self):
        print("\n=== Escolha o tipo de entrada ===")
        print("1. Tecla do teclado")
        print("2. Mouse Button 4 (X2)")
        print("3. Mouse Button 5 (X1)")

        while True:
            try:
                choice = input("\nEscolha uma opção (1-3): ")
                if choice == "1":
                    key = input("Digite a tecla desejada (exemplo: e, a, z): ").lower()
                    return ("keyboard", key)
                elif choice == "2":
                    return ("mouse", "x2")
                elif choice == "3":
                    return ("mouse", "x1")
                else:
                    print("Opção inválida! Escolha entre 1 e 3.")
            except ValueError:
                print("Entrada inválida! Tente novamente.")

    def get_mode_choice(self):
        print("\n=== Escolha o modo de operação ===")
        print("1. Segurar (mantém pressionado para repetir)")
        print("2. Alternar (pressiona uma vez para iniciar, outra para parar)")

        while True:
            try:
                choice = input("\nEscolha uma opção (1-2): ")
                if choice in ["1", "2"]:
                    return "hold" if choice == "1" else "toggle"
                print("Opção inválida! Escolha entre 1 e 2.")
            except ValueError:
                print("Entrada inválida! Tente novamente.")

    def hold_press(self):
        """Função para o modo segurar"""
        while True:
            try:
                is_pressed = keyboard.is_pressed(self.key) if self.input_type == "keyboard" else mouse.is_pressed(
                    button=self.key)

                if is_pressed and not self.running:
                    print("\nIniciando repetição automática...")
                    self.running = True
                    self.stop_event.clear()
                    Thread(target=self.auto_press).start()
                elif not is_pressed and self.running:
                    print("\nParando repetição automática...")
                    self.running = False
                    self.stop_event.set()

                time.sleep(0.1)
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(1)

    def toggle_action(self, _):
        """Função para o modo alternar"""
        if not self.running:
            print("\nIniciando repetição automática...")
            self.running = True
            self.stop_event.clear()
            Thread(target=self.auto_press).start()
        else:
            print("\nParando repetição automática...")
            self.running = False
            self.stop_event.set()

    def auto_press(self):
        """Função que executa os pressionamentos automaticamente"""
        while self.running and not self.stop_event.is_set():
            try:
                if self.input_type == "keyboard":
                    keyboard.send(self.key)
                else:
                    mouse.click(button=self.key)
                time.sleep(self.interval)
            except Exception as e:
                print(f"Erro durante o pressionamento: {e}")
                time.sleep(1)

    def run(self):
        try:
            print("=== Configuração do Auto Presser ===")
            self.input_type, self.key = self.get_key_choice()
            self.interval = self.get_valid_interval()
            self.mode = self.get_mode_choice()

            print("\n=== Auto Presser Iniciado ===")
            print(f"Intervalo configurado: {self.interval * 1000:.1f}ms")
            print(f"Modo: {'Segurar' if self.mode == 'hold' else 'Alternar'}")

            if self.input_type == "keyboard":
                action_text = f"{'mantenha' if self.mode == 'hold' else 'pressione'} '{self.key.upper()}'"
            else:
                button_name = "Mouse Button 4" if self.key == "x2" else "Mouse Button 5"
                action_text = f"{'mantenha' if self.mode == 'hold' else 'pressione'} o {button_name}"

            print(
                f"\n{action_text} para {'manter' if self.mode == 'hold' else 'iniciar/parar'} os pressionamentos automáticos")

            print("\nLegenda dos botões do mouse:")
            print("- Mouse Button 4 = Botão lateral da frente do mouse")
            print("- Mouse Button 5 = Botão lateral de trás do mouse")
            print("\nPara fechar o programa, pressione Ctrl+C ou feche esta janela")
            print("=====================================\n")

            if self.mode == "toggle":
                # Configura o listener para modo alternar
                if self.input_type == "keyboard":
                    keyboard.on_press_key(self.key, self.toggle_action)
                else:
                    mouse.on_button(self.key, self.toggle_action, mouse.ButtonEvent.UP)

                # Mantém o programa rodando até Ctrl+C
                while True:
                    time.sleep(0.1)
            else:
                # Inicia o modo segurar
                self.hold_press()

        except KeyboardInterrupt:
            print("\nPrograma encerrado pelo usuário.")
        except Exception as e:
            print(f"\nErro crítico: {e}")
        finally:
            self.running = False
            self.stop_event.set()
            input("\nPressione Enter para sair...")


if __name__ == "__main__":
    auto_presser = AutoPresser()
    auto_presser.run()
