import cv2
import time
import numpy as np
import dxcam

import threading
from pynput.keyboard import Listener, KeyCode, Controller, Key

TOOGLE_KEY = KeyCode(char='t')
TEST_KEY = KeyCode(char='k')
EXIT_KEY = KeyCode(char='x')

running = False
closing = False

keyboard = Controller()
camera = dxcam.create()
camera.start(region=(630,700,1250,810), target_fps=120)

vazio_img = cv2.imread('img/vazio.png', cv2.IMREAD_UNCHANGED)

alvo_img = cv2.imread('img/alvo.png', cv2.IMREAD_UNCHANGED)
bola_img = cv2.imread('img/bola.png', cv2.IMREAD_UNCHANGED)
cima_img = cv2.imread('img/cima.png', cv2.IMREAD_UNCHANGED)
baixo_img = cv2.imread('img/baixo.png', cv2.IMREAD_UNCHANGED)
esquerda_img = cv2.imread('img/esquerda.png', cv2.IMREAD_UNCHANGED)
direita_img = cv2.imread('img/direita.png', cv2.IMREAD_UNCHANGED)

testes = [
    vazio_img,     #0
    alvo_img,      #1
    bola_img,      #2
    cima_img,      #3
    baixo_img,     #4
    esquerda_img,  #5
    direita_img    #6
    ]

def check_screen() -> list[list[int]]:
    resultados:list[list[int]] = []

    frame = camera.get_latest_frame()
    if frame is None:
        return resultados
    frame_img = cv2.cvtColor(np.array(
        frame
    ), cv2.COLOR_RGB2BGR)

    for i in range(0, len(testes)):
        heatmap = cv2.matchTemplate(frame_img, testes[i], cv2.TM_CCOEFF_NORMED)
        result = heatmap.max()
        threshold = 0.8
        (yloc, xloc) = np.where(heatmap >= threshold) # type: ignore

        for (x, y) in zip(xloc, yloc):
            adicionado = False
            for a in resultados:
                if abs(a[1] - x) <= 10:
                    adicionado = True
                    if x > a[1]:
                        a[1] = x
            if not adicionado:
                resultados.append([i, x])

    return resultados

def key_click(key: str | Key | KeyCode) -> None:
    keyboard.press(key)
    time.sleep(0.03)
    keyboard.release(key)

def bot():
    global closing
    global running
    while not closing:
        if running:
            alvos = check_screen()
            alvo = 0
            distancia = 0
            if len(alvos) == 0:
                alvo = 0
            else:
                for a in alvos:
                    if a[1] > distancia:
                        alvo = a[0]
                        distancia = a[1]

            if distancia < 490:
                if alvo > 0:
                    alvo = 1

            match alvo:
                case 0:
                    key_click(Key.enter)
                    time.sleep(0.7)
                case 2:
                    key_click(Key.space)
                case 3:
                    key_click('w')
                case 4:
                    key_click('s')
                case 5:
                    key_click('a')
                case 6:
                    key_click('d')
        time.sleep(0.001)

def toggle_event(key):
    global closing
    if key == TOOGLE_KEY:
        global running
        running = not running
    if key == TEST_KEY:
        check_screen()
    if key == EXIT_KEY:
        closing = True
        quit()


def main():
    bot_thread = threading.Thread(target=bot)
    bot_thread.start()

    with Listener(on_press=toggle_event) as listener:
        listener.join()

if __name__ == "__main__":
    main()
