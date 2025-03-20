import os
from urllib.parse import quote
import webbrowser
from time import sleep
import pyautogui


def enviar_whatsapp(mensagem):
    try:
        # whatsapp = f'https://web.whatsapp.com/send?phone={telefone}&text={quote(mensagem)}'
        grupo = 'GPE Embrapii'
        whatsapp = f'https://web.whatsapp.com/send?text={quote(mensagem)}&app_absent=0&selectedContactName={quote(grupo)}'
        webbrowser.open(whatsapp)
        sleep(50)
        
        #selecionar o grupo
        pyautogui.typewrite(grupo)
        sleep(2)
        pyautogui.press('enter')
        sleep(2)
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')

        #enviar a mensagem
        sleep(2)
        pyautogui.press('enter')
        sleep(10)

        #fechar
        pyautogui.hotkey('ctrl', 'f4')
    except:
        print('Não foi possível enviar a mensagem.')