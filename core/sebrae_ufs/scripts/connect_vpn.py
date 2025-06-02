import pyautogui
import time
import inspect

# Função para abrir o FortiClient VPN
def connect_vpn():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # Abre o menu Iniciar
    pyautogui.press('winleft')
    time.sleep(1)
    
    # Digita 'FortiClient' no menu Iniciar
    pyautogui.write('FortiClient')
    time.sleep(1)
    
    # Pressiona 'enter' para abrir o FortiClient
    pyautogui.press('enter')
    time.sleep(5)  # Espera o aplicativo abrir

    # Pressiona 'tab' uma vez
    pyautogui.press('tab')
    time.sleep(1)
    
    # Pressiona a tecla 'seta para baixo' uma vez
    pyautogui.press('down')
    time.sleep(1)
    
    # Pressiona 'enter' para conectar
    pyautogui.press('enter')
    pyautogui.hotkey('alt', 'tab')
    time.sleep(10)
    
    print("🟢 " + inspect.currentframe().f_code.co_name)


def disconnect_vpn():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    # Abre o menu Iniciar
    pyautogui.press('winleft')
    time.sleep(1)
    
    # Digita 'FortiClient' no menu Iniciar
    pyautogui.write('FortiClient')
    time.sleep(1)

    # Pressiona 'enter' para abrir aplicativo
    pyautogui.press('enter')
    time.sleep(1)

    # Pressiona 'tab' uma vez
    pyautogui.press('tab')
    time.sleep(1)
    
    # Pressiona 'enter' para disconectar
    pyautogui.press('enter')
    time.sleep(5)

    # Fechar Aplicativo
    pyautogui.hotkey('alt', 'F4')


    print("🟢 " + inspect.currentframe().f_code.co_name)

