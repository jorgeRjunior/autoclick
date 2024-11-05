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
from threading import Thread


def get_valid_interval():
    while True:
        try:
            ms = float(input("\nInsira o tempo em ms (exemplo: 100): "))
            if ms <= 0:
                print("Por favor, insira um valor positivo!")
                continue
            return ms / 1000  # Converte ms para segundos
        except ValueError:
            print("Por favor, insira um número válido!")


def get_key_choice():
    print("\n=== AutoClick criado por Git @ jorgeRjunior ===")
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


def auto_presser(interval, input_type, key):
    print("\n=== Auto Presser Iniciado ===")
    print(f"Intervalo configurado: {interval * 1000:.1f}ms")

    if input_type == "keyboard":
        print(f"Mantenha a tecla '{key.upper()}' pressionada para ativar pressionamentos automáticos")
    else:
        button_name = "Mouse Button 4" if key == "x2" else "Mouse Button 5"
        print(f"Mantenha o {button_name} pressionado para ativar pressionamentos automáticos")

    print("\nLegenda dos botões do mouse:")
    print("- Mouse Button 4 = Botão lateral da frente do mouse")
    print("- Mouse Button 5 = Botão lateral de trás do mouse")
    print("\nPara fechar o programa, pressione Ctrl+C ou feche esta janela")
    print("=====================================\n")

    while True:
        try:
            if input_type == "keyboard" and keyboard.is_pressed(key):
                keyboard.press(key)
                keyboard.release(key)
                time.sleep(interval)
            elif input_type == "mouse" and mouse.is_pressed(button=key):
                mouse.press(button=key)
                mouse.release(button=key)
                time.sleep(interval)
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        print("=== Configuração do Auto Presser ===")
        input_type, key = get_key_choice()
        interval = get_valid_interval()
        auto_presser(interval, input_type, key)
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
    except Exception as e:
        print(f"\nErro crítico: {e}")
    finally:
        input("\nPressione Enter para sair...")