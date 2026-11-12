"""
fuegos.py
=========
PARTE 3: El cierre del parque - fuegos artificiales con RECURSIVIDAD.

Un cohete explota en varias partículas; cada partícula explota en otras más
chicas, y así sucesivamente hasta que la partícula es demasiado pequeña y se
apaga. Es la misma idea del árbol fractal / Sierpinski de la Clase 8.

Contenido:
    - explotar()      : la función RECURSIVA (el corazón de esta parte).
    - lanzar_cohete() : anima el cohete subiendo antes de la explosión.
    - Funciones auxiliares que dibujan o programan animaciones.

Nota sobre la animación:
    La recursión se ejecuta completa de golpe (calcula todas las partículas),
    pero cada dibujo se AGENDA con canvas.after(ms, ...) para que aparezca
    nivel por nivel, con un pequeño retraso entre uno y otro. Así se ve la
    explosión "creciendo" en vez de aparecer toda de una vez.
"""
import math
import random

# Milisegundos de espera entre un nivel de explosión y el siguiente.
DELAY_MS = 220

# Un color distinto por nivel de profundidad de la recursión.
COLORES = ["#ff4d8d", "#ffd23f", "#35d0ff", "#7cff6b", "#c77dff", "#ffffff"]


def _programar(canvas, ids, ms, accion):
    """
    Agenda `accion` para que se ejecute dentro de `ms` milisegundos.

    Guarda el identificador en la lista `ids` para poder cancelar todas las
    animaciones pendientes si el usuario pulsa "Limpiar cielo".
    """
    ids.append(canvas.after(ms, accion))


def _dibujar_linea(canvas, x1, y1, x2, y2, color, grosor):
    """Dibuja el rayo de una partícula y un puntito brillante en su extremo."""
    canvas.create_line(x1, y1, x2, y2, fill=color, width=grosor)
    canvas.create_oval(x2 - 2, y2 - 2, x2 + 2, y2 + 2, fill=color, outline="")


def _chispa_final(canvas, ids, x, y):
    """
    Dibuja la última chispa de una partícula demasiado chica: brilla un
    instante (300 ms) y luego se borra, es decir, "se apaga".
    """
    item = canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#ffffff", outline="")
    _programar(canvas, ids, 300, lambda: canvas.delete(item))


def explotar(canvas, ids, x, y, radio, nivel=0, retraso=0, hijas=5, radio_minimo=12):
    """
    FUNCIÓN RECURSIVA: explota una partícula y, de ella, las partículas hijas.

    Parámetros:
        canvas        : lienzo de tkinter donde se dibuja.
        ids           : lista donde se guardan las animaciones agendadas.
        x, y          : posición de la partícula que explota.
        radio         : tamaño de la explosión (largo de los rayos).
        nivel         : profundidad actual de la recursión (0 = cohete inicial).
        retraso       : milisegundos a esperar antes de dibujar este nivel.
        hijas         : cuántas partículas nacen de cada explosión.
        radio_minimo  : tamaño por debajo del cual la partícula se apaga.

    Retorna:
        Cuántas partículas se generaron en total (esta + todas sus descendientes).

    Cómo funciona:
        CASO BASE      -> si radio < radio_minimo: la partícula se apaga y la
                          función termina SIN llamarse de nuevo.
        CASO RECURSIVO -> dibuja `hijas` rayos y, para cada extremo, se llama
                          a sí misma con la MITAD del radio. Como el radio se
                          achica cada vez, tarde o temprano se llega al caso
                          base y la recursión termina.

    Ejemplo con radio inicial 90 y mínimo 12:
        90 -> 45 -> 22.5 -> 11.25 (ya es < 12: caso base)
    """
    # ---------------- CASO BASE ----------------
    if radio < radio_minimo:
        _programar(canvas, ids, retraso, lambda: _chispa_final(canvas, ids, x, y))
        return 1  # solo cuenta a sí misma; no crea hijas

    # ---------------- CASO RECURSIVO ----------------
    total = 1  # contamos esta partícula
    color = COLORES[nivel % len(COLORES)]   # color según la profundidad
    grosor = max(1, 4 - nivel)              # los rayos se hacen más finos
    angulo_inicial = random.uniform(0, 2 * math.pi)  # que cada explosión se vea distinta

    for i in range(hijas):
        # Repartimos las hijas en círculo, a ángulos iguales.
        angulo = angulo_inicial + i * (2 * math.pi / hijas)
        # Extremo del rayo = punto donde "nace" la partícula hija.
        x2 = x + math.cos(angulo) * radio
        y2 = y + math.sin(angulo) * radio

        # Agendamos el dibujo del rayo (los parámetros por defecto del lambda
        # "congelan" los valores de esta vuelta del ciclo).
        _programar(
            canvas, ids, retraso,
            lambda a=x, b=y, c=x2, d=y2, col=color, g=grosor:
                _dibujar_linea(canvas, a, b, c, d, col, g),
        )

        # >>> LLAMADA RECURSIVA <<<
        # La función se llama a sí misma sobre cada partícula hija, con la
        # mitad del tamaño, un nivel más de profundidad y un poco más de retraso.
        total += explotar(canvas, ids, x2, y2, radio * 0.5,
                          nivel + 1, retraso + DELAY_MS, hijas, radio_minimo)
    return total


def lanzar_cohete(canvas, ids, x, y_base, y_alto, al_llegar):
    """
    Anima el cohete subiendo desde `y_base` hasta `y_alto` dejando una estela.
    Al llegar arriba ejecuta `al_llegar()`, que es donde se llama a explotar().

    Nota: esta función de animación se re-agenda a sí misma con after(), pero
    NO es la recursión del ejercicio; la recursión "oficial" es explotar().
    """
    def subir(y):
        if y <= y_alto:        # llegó a la altura de la explosión
            al_llegar()
            return
        # Un trozo de estela; la etiqueta "cohete" permite borrarla después.
        canvas.create_line(x, y, x, y + 12, fill="#ffd23f", width=3, tags="cohete")
        _programar(canvas, ids, 15, lambda: subir(y - 9))

    subir(y_base)
