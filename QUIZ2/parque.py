"""
parque.py
=========
Programa principal: "Un día en el parque" con interfaz gráfica (tkinter).

Es UN solo programa con tres pestañas, una por cada herramienta del curso:

    Pestaña 1 -> Fila de la montaña rusa  -> COLA          (estructuras.Cola)
    Pestaña 2 -> Libro de reclamos        -> PILA          (estructuras.Pila)
    Pestaña 3 -> Cierre con fuegos        -> RECURSIVIDAD  (fuegos.explotar)

Para correrlo:
    python parque.py

Estructura de este archivo:
    1. Paleta de colores y funciones de dibujo (muñecos, cajas, carrito).
    2. Animaciones y tooltips (globos de ayuda al pasar el mouse).
    3. Clase Parque (la ventana), en secciones:
         - Estilos y encabezado
         - PARTE 1: Cola      (fila de visitantes + carrito)
         - PARTE 2: Pila      (cajas apiladas + encargado)
         - PARTE 3: Recursión (fuegos artificiales)
    Las líneas marcadas con  # <-- COLA / PILA / RECURSIÓN  son los puntos
    exactos donde se usa cada estructura.
"""
import math
import random
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

from estructuras import Cola, Pila
from fuegos import explotar, lanzar_cohete

# ----------------------------------------------------------------------
# Paleta: azul noche con colores vivos (no es solo negro)
# ----------------------------------------------------------------------
FONDO = "#0d0b2b"         # azul noche: fondo general
PANEL = "#1c1747"         # violeta oscuro: fondo de las pestañas
PANEL_CLARO = "#2a2360"   # pestañas no seleccionadas y detalles
LIENZO = "#140f3a"        # fondo de los dibujos (fila, pila, historial)
TXT = "#f5f3ff"           # texto claro
TXT_SUAVE = "#b8b3e6"     # texto secundario
ROSA = "#ff4d8d"
DORADO = "#ffd23f"
CELESTE = "#35d0ff"
VERDE = "#7cff6b"
MORADO = "#c77dff"
NARANJA = "#ff9f43"
PIEL = "#ffd9b3"          # color de la cara de los muñecos
CAMISETAS = [ROSA, DORADO, CELESTE, VERDE, MORADO, NARANJA]

# Nombres para el botón "+ Visitante aleatorio".
NOMBRES = ["Juan", "María", "Luis", "Ana", "Carlos", "Sofía", "Diego", "Valeria",
           "Pedro", "Camila", "Andrés", "Lucía", "Mateo", "Elena", "Tomás", "Isabel"]

# Cómo se redacta cada tipo de acción en el libro de reclamos.
# El {} se reemplaza por el nombre del cliente.
PLANTILLAS_ACCION = {
    "Boleto vendido": "Boleto vendido a {}",
    "Reclamo": "Reclamo registrado de {}",
    "Reembolso": "Reembolso solicitado por {}",
}

# Cuántas personas caben en un carrito de la montaña rusa.
CAPACIDAD_CARRITO = 4

# Medidas de la pista de la montaña rusa (en píxeles dentro del canvas del carrito).
PISTA_BASE = 195   # altura del riel en las partes planas (estación y salida)
SUELO = 222        # altura del suelo, de donde salen los soportes
DURACION_VIAJE = 2.5   # segundos que dura el recorrido completo (menor = más rápido)


# ======================================================================
# 1. FUNCIONES DE DIBUJO Y UTILIDADES
# ======================================================================
def color_de(nombre):
    """Elige siempre el mismo color para el mismo nombre (suma de sus letras)."""
    return CAMISETAS[sum(ord(ch) for ch in nombre) % len(CAMISETAS)]


def dibujar_persona(c, x, y, color, nombre="", tags=()):
    """
    Dibuja un muñeco estilo "palito" con cabeza, ojos, sonrisa, camiseta,
    brazos y piernas. (x, y) es el centro del cuerpo.
    Todas sus piezas llevan los `tags`, así se pueden mover juntas.
    """
    t = tuple(tags)
    # Brazos (van antes del cuerpo para que la camiseta los tape en el hombro)
    c.create_line(x - 14, y - 24, x - 26, y - 8, fill=color, width=6, capstyle="round", tags=t)
    c.create_line(x + 14, y - 24, x + 26, y - 8, fill=color, width=6, capstyle="round", tags=t)
    # Piernas
    c.create_line(x - 6, y + 2, x - 9, y + 22, fill="#3b3585", width=6, capstyle="round", tags=t)
    c.create_line(x + 6, y + 2, x + 9, y + 22, fill="#3b3585", width=6, capstyle="round", tags=t)
    # Cuerpo (camiseta)
    c.create_rectangle(x - 14, y - 28, x + 14, y + 4, fill=color, outline="", tags=t)
    # Cabeza, ojos y sonrisa
    c.create_oval(x - 12, y - 54, x + 12, y - 30, fill=PIEL, outline="", tags=t)
    c.create_oval(x - 6, y - 46, x - 3, y - 43, fill="#1c1747", outline="", tags=t)
    c.create_oval(x + 3, y - 46, x + 6, y - 43, fill="#1c1747", outline="", tags=t)
    c.create_arc(x - 6, y - 44, x + 6, y - 34, start=200, extent=140,
                 style="arc", outline="#1c1747", width=2, tags=t)
    if nombre:
        c.create_text(x, y + 36, text=nombre[:10], fill=TXT,
                      font=("Helvetica", 10, "bold"), tags=t)


def mover_suave(root, c, tag, dx, dy=0, pasos=20, intervalo=16,
                vigente=lambda: True, al_terminar=None):
    """
    Mueve todo lo que tenga `tag` en el canvas `c`, de forma suave, sumando
    en `pasos` pasos un desplazamiento total de (dx, dy).

    Se usa after() para no congelar la ventana: cada paso programa el siguiente.
    `vigente` permite cancelar la animación si ya hay una nueva.
    """
    previo = [0.0, 0.0]

    def paso(i):
        if not vigente():
            return
        t = min(i / pasos, 1.0)
        e = 1 - (1 - t) ** 2          # efecto "frenar al final" (ease-out)
        nx, ny = dx * e, dy * e
        c.move(tag, nx - previo[0], ny - previo[1])
        previo[0], previo[1] = nx, ny
        if i < pasos:
            root.after(intervalo, lambda: paso(i + 1))
        elif al_terminar:
            al_terminar()

    paso(0)


class Tooltip:
    """
    Globo de ayuda: aparece al pasar el mouse sobre un botón o campo
    y explica qué hace y qué función de código ejecuta.
    """

    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self.ventana = None
        widget.bind("<Enter>", self.mostrar, add="+")
        widget.bind("<Leave>", self.ocultar, add="+")

    def mostrar(self, _evento=None):
        if self.ventana:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.ventana = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)           # sin barra de título
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.texto, bg="#fff8dc", fg=FONDO, justify="left",
                 font=("Helvetica", 10), padx=8, pady=6, relief="solid",
                 borderwidth=1, wraplength=300).pack()

    def ocultar(self, _evento=None):
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None


# ======================================================================
# 2. LA VENTANA DEL PARQUE
# ======================================================================
class Parque(tk.Tk):
    """
    Ventana principal del parque. Hereda de tk.Tk, así que ES la ventana.

    Atributos importantes:
        fila           : Cola con los visitantes esperando (PARTE 1).
        reclamos       : Pila con las acciones registradas (PARTE 2).
        subieron       : contador de visitantes que ya subieron en el día.
        ids_fuegos     : animaciones de fuegos pendientes (para cancelarlas).
        _token_carrito : número de viaje actual; si cambia, el viaje anterior se detiene.
    """

    def __init__(self):
        super().__init__()
        self.title("Un día en el parque de diversiones")
        self.geometry("1100x860")
        self.minsize(960, 760)
        self.configure(bg=FONDO)

        # ---- Las estructuras de datos del parque ----
        self.fila = Cola()          # PARTE 1: fila de la montaña rusa
        self.reclamos = Pila()      # PARTE 2: libro de reclamos
        self.subieron = 0
        self.ids_fuegos = []
        self._token_carrito = 0

        # ---- Construcción de la interfaz ----
        self._configurar_estilos()
        self._crear_encabezado()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._crear_tab_fila()
        self._crear_tab_reclamos()
        self._crear_tab_fuegos()
        self._actualizar_stats()

    # ==================================================================
    # Estilos, encabezado y piezas reutilizables
    # ==================================================================
    def _configurar_estilos(self):
        """Colores de pestañas, botones (uno por color) y campos de texto."""
        s = ttk.Style(self)
        s.theme_use("clam")  # tema que permite cambiar colores en todos los sistemas
        s.configure("TNotebook", background=FONDO, borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL_CLARO, foreground=TXT,
                    padding=(18, 10), font=("Helvetica", 12, "bold"))
        s.map("TNotebook.Tab", background=[("selected", ROSA)],
              foreground=[("selected", "#ffffff")])
        s.configure("TFrame", background=PANEL)
        s.configure("TLabel", background=PANEL, foreground=TXT, font=("Helvetica", 11))
        s.configure("TEntry", fieldbackground="#ffffff", foreground=FONDO, padding=6)
        s.configure("TCombobox", fieldbackground="#ffffff", foreground=FONDO, padding=4)

        # Un estilo de botón por color. Así cada botón se distingue de un vistazo.
        for nombre, fondo, texto in [("Rosa", ROSA, "#ffffff"),
                                     ("Celeste", CELESTE, FONDO),
                                     ("Dorado", DORADO, FONDO),
                                     ("Verde", VERDE, FONDO),
                                     ("Morado", MORADO, FONDO)]:
            s.configure(f"{nombre}.TButton", background=fondo, foreground=texto,
                        font=("Helvetica", 11, "bold"), padding=(12, 8), borderwidth=0)
            s.map(f"{nombre}.TButton", background=[("active", "#ffffff")],
                  foreground=[("active", FONDO)])

    def _crear_encabezado(self):
        """Título del parque y resumen de estadísticas del día."""
        top = tk.Frame(self, bg=FONDO)
        top.pack(fill="x", padx=12, pady=12)
        tk.Label(top, text="PARQUE DE DIVERSIONES", bg=FONDO, fg=DORADO,
                 font=("Helvetica", 24, "bold")).pack(side="left")
        self.lbl_stats = tk.Label(top, bg=PANEL_CLARO, fg=TXT, padx=14, pady=6,
                                  font=("Helvetica", 11, "bold"))
        self.lbl_stats.pack(side="right")

    def _banner(self, padre, texto, color):
        """Franja de color con una explicación corta de la estructura."""
        franja = tk.Frame(padre, bg=color, padx=14, pady=10)
        franja.pack(fill="x", pady=(0, 12))
        tk.Label(franja, text=texto, bg=color, fg=FONDO, justify="left",
                 font=("Helvetica", 11, "bold"), wraplength=900).pack(anchor="w")

    def _actualizar_stats(self):
        self.lbl_stats.config(
            text=f"En fila: {len(self.fila)}    Ya subieron: {self.subieron}"
                 f"    Acciones vigentes: {len(self.reclamos)}")

    # ==================================================================
    # PARTE 1: COLA - Fila de la montaña rusa
    # ==================================================================
    def _crear_tab_fila(self):
        """Pestaña de la montaña rusa: controles, fila de muñecos y carrito."""
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="  Montaña rusa · COLA  ")

        self._banner(tab, "COLA (FIFO): los visitantes entran por ATRÁS y salen por ADELANTE. "
                          "El primero que llega es el primero que sube.", CELESTE)

        # --- Controles ---
        controles = ttk.Frame(tab)
        controles.pack(fill="x")
        ttk.Label(controles, text="Visitante:").pack(side="left")
        self.ent_visitante = ttk.Entry(controles, width=18)
        self.ent_visitante.pack(side="left", padx=6)
        self.ent_visitante.bind("<Return>", lambda e: self.agregar_visitante())
        Tooltip(self.ent_visitante, "Escribe el nombre del visitante y presiona Enter.")

        b = ttk.Button(controles, text="Agregar a la fila", style="Verde.TButton",
                       command=self.agregar_visitante)
        b.pack(side="left", padx=4)
        Tooltip(b, "ENCOLAR: agrega al visitante al FINAL de la fila.\n"
                   "Es Cola.encolar(), que enlaza un nodo nuevo al final.")

        b = ttk.Button(controles, text="+ Visitante aleatorio", style="Celeste.TButton",
                       command=self.agregar_aleatorio)
        b.pack(side="left", padx=4)
        Tooltip(b, "Crea un visitante con nombre al azar y lo encola al final.")

        b = ttk.Button(controles, text="Subir al primero", style="Rosa.TButton",
                       command=self.subir_primero)
        b.pack(side="left", padx=(24, 4))
        Tooltip(b, "DESENCOLAR: saca al visitante del FRENTE, el que lleva más tiempo "
                   "esperando, y lo sube al carrito.\nEs Cola.desencolar().")

        b = ttk.Button(controles, text=f"Subir carrito ({CAPACIDAD_CARRITO})",
                       style="Dorado.TButton", command=self.subir_carrito)
        b.pack(side="left", padx=4)
        Tooltip(b, f"Llena el carrito con hasta {CAPACIDAD_CARRITO} personas.\n"
                   "Las saca del frente UNA por UNA, así que suben en orden de llegada.")

        # --- Fila de muñecos ---
        ttk.Label(tab, text="Fila de espera (el muñeco con aro dorado es el FRENTE)",
                  style="TLabel").pack(anchor="w", pady=(14, 4))
        self.cv_fila = tk.Canvas(tab, bg=LIENZO, height=250, highlightthickness=0)
        self.cv_fila.pack(fill="x")
        self.cv_fila.bind("<Configure>", lambda e: self._dibujar_fila())

        # --- Carrito ---
        ttk.Label(tab, text="Carrito de la montaña rusa").pack(anchor="w", pady=(10, 4))
        self.cv_carrito = tk.Canvas(tab, bg=LIENZO, height=250, highlightthickness=0)
        self.cv_carrito.pack(fill="x")
        self.cv_carrito.bind("<Configure>", lambda e: self._pintar_estacion())

        # Registro del viaje: quién va (o iba) al frente del carrito.
        self.lbl_viaje = ttk.Label(tab, text="Aún no ha salido ningún viaje.",
                                   foreground=DORADO, font=("Helvetica", 11, "bold"))
        self.lbl_viaje.pack(anchor="w", pady=(6, 0))

        # --- Mensaje de estado ---
        self.lbl_fila_msg = ttk.Label(tab, text="Agrega visitantes para empezar el día.")
        self.lbl_fila_msg.pack(anchor="w", pady=(8, 0))

        self._dibujar_fila()
        self._pintar_estacion()

    def _dibujar_fila(self, saliente=None, animar_nuevo=False):
        """
        Dibuja la fila de muñecos. Lee los datos con self.fila.a_lista()
        (de frente a final).

        saliente     : nombre de quien acaba de subir; se dibuja saliendo
                       por la izquierda con una animación.
        animar_nuevo : si es True, el último de la fila entra deslizándose
                       desde la derecha.
        """
        c = self.cv_fila
        c.delete("all")
        ancho = max(c.winfo_width(), 500)

        # Etiquetas de los extremos de la fila
        c.create_text(16, 16, text="◀ SALE (frente)", anchor="w",
                      fill=DORADO, font=("Helvetica", 11, "bold"))
        c.create_text(ancho - 16, 16, text="ENTRA (final) ▶", anchor="e",
                      fill=CELESTE, font=("Helvetica", 11, "bold"))

        visitantes = self.fila.a_lista()

        # Quién está al frente y subirá primero (se lee sin sacarlo de la fila).
        siguiente = self.fila.ver_frente()              # <-- COLA: ver_frente
        if siguiente:
            c.create_text(ancho / 2, 16, text=f"SIGUIENTE EN SUBIR: {siguiente}",
                          fill=DORADO, font=("Helvetica", 13, "bold"))

        if not visitantes:
            c.create_text(ancho / 2, 150, text="Nadie en la fila. ¡Agrega visitantes!",
                          fill=TXT_SUAVE, font=("Helvetica", 15, "italic"))

        margen = 110       # espacio a la izquierda para la etiqueta SALE
        n = len(visitantes)
        # Si hay muchos visitantes, se acercan un poco para caber en una sola línea.
        paso = max(56, min(120, (ancho - margen - 40) // max(n, 1)))
        por_fila = max(3, (ancho - margen - 30) // paso)

        # Qué muñecos se dibujan. Si no caben todos, se muestran los primeros,
        # un marcador "+N" y SIEMPRE el último: el FRENTE y el FINAL nunca se ocultan.
        if n <= por_fila:
            mostrar = list(enumerate(visitantes))
            ocultos = 0
        else:
            k = por_fila - 2
            mostrar = list(enumerate(visitantes[:k])) + [(n - 1, visitantes[-1])]
            ocultos = n - k - 1
            xm = margen + k * paso               # posición del marcador "···"
            c.create_text(xm, 105, text="···", fill=CELESTE,
                          font=("Helvetica", 26, "bold"))
            c.create_text(xm, 140, text=f"+{ocultos} en la fila", fill=TXT_SUAVE,
                          font=("Helvetica", 10, "italic"))

        for slot, (i, nombre) in enumerate(mostrar):
            # El último (cuando hay marcador) va un hueco más a la derecha.
            desplazamiento = 1 if (ocultos and i == n - 1) else 0
            x = margen + (slot + desplazamiento) * paso
            y = 120

            es_nuevo = animar_nuevo and i == n - 1
            tags = ("persona", "nuevo") if es_nuevo else ("persona",)
            es_frente, es_final = (i == 0), (i == n - 1)

            if es_frente:   # aro dorado y etiqueta FRENTE
                c.create_oval(x - 34, y - 66, x + 34, y + 46, outline=DORADO,
                              width=3, dash=(4, 3), tags=tags)
                c.create_text(x, y - 76, fill=DORADO, font=("Helvetica", 9, "bold"),
                              text="FRENTE y FINAL" if es_final else "FRENTE", tags=tags)
            elif es_final:  # aro celeste y etiqueta FINAL (el último que llegó)
                c.create_oval(x - 34, y - 66, x + 34, y + 46, outline=CELESTE,
                              width=3, dash=(4, 3), tags=tags)
                c.create_text(x, y - 76, text="FINAL", fill=CELESTE,
                              font=("Helvetica", 9, "bold"), tags=tags)

            dibujar_persona(c, x, y, color_de(nombre), nombre, tags=tags)

        # Quien acaba de subir se dibuja encima y sale por la izquierda.
        if saliente is not None:
            dibujar_persona(c, margen, 120, color_de(saliente), saliente, tags=("salida",))
            mover_suave(self, c, "salida", -260, pasos=22, intervalo=18,
                        al_terminar=lambda: c.delete("salida"))

        # Quien acaba de llegar entra deslizándose desde la derecha.
        if animar_nuevo and visitantes:
            c.move("nuevo", 200, 0)
            mover_suave(self, c, "nuevo", -200, pasos=16, intervalo=16)

    def _texto_frente(self):
        """Dice quién quedó al frente de la fila después de subir gente."""
        siguiente = self.fila.ver_frente()              # <-- COLA: ver_frente
        if siguiente:
            return f"Ahora al frente de la fila: {siguiente}."
        return "La fila quedó vacía."

    def _texto_viaje(self, nombres):
        """Lista de pasajeros de adelante hacia atrás (el primero de la fila va al frente)."""
        if not nombres:
            return ""
        return " → ".join([f"{nombres[0]} (al frente)"] + list(nombres[1:]))

    def _pista(self, ancho):
        """
        Calcula los puntos (x, y) del riel de la montaña rusa.

        La pista tiene tramos: estación plana, una colina grande (la de
        "subida lenta"), varias colinas más chicas y una salida plana.
        Entre punto y punto se usa coseno para que las curvas sean suaves.
        Devuelve una lista de puntos separados 2 px en horizontal.
        """
        x0 = 70                              # donde está la estación (entrada)
        x1 = max(ancho - 330, x0 + 300)      # donde está la zona de salida
        clave = [(0.00, PISTA_BASE), (0.10, PISTA_BASE), (0.30, 125),
                 (0.47, PISTA_BASE), (0.60, 150), (0.72, PISTA_BASE),
                 (0.84, 160), (0.94, PISTA_BASE), (1.00, PISTA_BASE)]
        pts = []
        for (f0, y0), (f1, y1) in zip(clave, clave[1:]):
            xa = x0 + (x1 - x0) * f0
            xb = x0 + (x1 - x0) * f1
            n = max(1, int((xb - xa) / 2))
            for k in range(n):
                t = k / n
                y = y0 + (y1 - y0) * (1 - math.cos(math.pi * t)) / 2
                pts.append((xa + (xb - xa) * t, y))
        pts.append((x1, clave[-1][1]))
        return pts

    def _dibujar_pista(self, c, ancho, pts):
        """Dibuja el suelo, los soportes, el riel, los letreros y el túnel."""
        c.create_line(0, SUELO, ancho, SUELO, fill="#3b3585", width=3)
        for i in range(0, len(pts), 14):                    # soportes verticales
            x, y = pts[i]
            c.create_line(x, y, x, SUELO, fill="#3b3585", width=3)
        # Riel de entrada, pista principal y riel de salida hasta el túnel
        c.create_line(0, PISTA_BASE, pts[0][0], PISTA_BASE, fill=CELESTE, width=5)
        plano = [v for punto in pts for v in punto]
        c.create_line(*plano, fill=CELESTE, width=5, capstyle="round", joinstyle="round")
        c.create_line(pts[-1][0], PISTA_BASE, ancho, PISTA_BASE, fill=CELESTE, width=5)
        c.create_text(pts[0][0], SUELO + 16, text="ENTRADA", fill=VERDE,
                      font=("Helvetica", 10, "bold"))
        c.create_text(pts[-1][0], SUELO + 16, text="SALIDA", fill=ROSA,
                      font=("Helvetica", 10, "bold"))
        # Túnel por donde se va el carro vacío después del viaje
        c.create_rectangle(ancho - 46, PISTA_BASE - 75, ancho, PISTA_BASE + 6,
                           fill="#05021a", outline=MORADO, width=3, tags="tunel")
        c.create_text(ancho - 23, PISTA_BASE - 88, text="TÚNEL", fill=MORADO,
                      font=("Helvetica", 9, "bold"), tags="tunel")

    def _dibujar_vagon(self, c, cx, ty, nombres, tags):
        """
        Dibuja el carrito con sus pasajeros sentados y sus nombres.
        (cx, ty) es el punto del riel donde se apoya el centro del carrito.

        El carrito avanza hacia la DERECHA, así que el asiento de ADELANTE es
        el de la derecha: ahí va el primero de la fila (nombre en dorado) y la
        "trompa" dorada marca el frente del carrito.
        """
        n = max(len(nombres), 2)
        w = 40 * n + 16
        for i, nombre in enumerate(nombres):
            px = cx + w / 2 - 28 - i * 40             # i = 0 -> asiento de adelante
            dibujar_persona(c, px, ty - 38, color_de(nombre), tags=tags)
            c.create_text(px, ty - 100, text=nombre[:6], tags=tags,
                          fill=DORADO if i == 0 else TXT, font=("Helvetica", 9, "bold"))
        c.create_rectangle(cx - w / 2, ty - 34, cx + w / 2, ty - 12,
                           fill=PANEL_CLARO, outline=DORADO, width=3, tags=tags)
        c.create_rectangle(cx - w / 2, ty - 22, cx + w / 2, ty - 12,
                           fill=DORADO, outline="", tags=tags)
        c.create_polygon(cx + w / 2, ty - 34, cx + w / 2 + 18, ty - 23,
                         cx + w / 2, ty - 12, fill=DORADO, outline="", tags=tags)  # trompa
        for rx in (cx - w / 2 + 14, cx + w / 2 - 14):       # ruedas
            c.create_oval(rx - 7, ty - 12, rx + 7, ty + 2, fill="#ffffff",
                          outline=DORADO, width=2, tags=tags)
    def _pintar_estacion(self, mensaje="Un carrito espera en la estación"):
        """Dibuja la pista con un carrito vacío esperando en la estación."""
        self._token_carrito += 1           # detiene cualquier viaje en curso
        c = self.cv_carrito
        c.delete("all")
        ancho = max(c.winfo_width(), 500)
        pts = self._pista(ancho)
        self._dibujar_pista(c, ancho, pts)
        self._dibujar_vagon(c, pts[0][0], pts[0][1], [], tags=("carro_espera",))
        c.create_text(ancho / 2, 22, text=mensaje, fill=TXT_SUAVE,
                      font=("Helvetica", 13, "italic"))
    def agregar_visitante(self):
        """Agrega al FINAL de la fila el nombre escrito en la caja de texto."""
        nombre = self.ent_visitante.get().strip()
        if not nombre:
            messagebox.showinfo("Falta el nombre", "Escribe el nombre del visitante.")
            return
        self.fila.encolar(nombre)                       # <-- COLA: encolar
        self.ent_visitante.delete(0, "end")
        self.lbl_fila_msg.config(text=f"{nombre} se unió al final de la fila.")
        self._dibujar_fila(animar_nuevo=True)
        self._actualizar_stats()

    def agregar_aleatorio(self):
        """Encola un visitante con nombre elegido al azar."""
        nombre = random.choice(NOMBRES)
        self.fila.encolar(nombre)                       # <-- COLA: encolar
        self.lbl_fila_msg.config(text=f"{nombre} llegó y se formó al final de la fila.")
        self._dibujar_fila(animar_nuevo=True)
        self._actualizar_stats()

    def subir_primero(self):
        """Sube al carrito a UNA persona: la que lleva más tiempo esperando (FIFO)."""
        visitante = self.fila.desencolar()              # <-- COLA: desencolar (FIFO)
        if visitante is None:
            self.lbl_fila_msg.config(text="No hay nadie en la fila.")
            return
        self.subieron += 1
        self.lbl_fila_msg.config(
            text=f"{visitante} lleva más tiempo esperando: ¡sube a la montaña rusa! "
                 + self._texto_frente())
        self._dibujar_fila(saliente=visitante)
        self._animar_carrito([visitante])
        self._actualizar_stats()

    def subir_carrito(self):
        """
        Llena un carrito con hasta CAPACIDAD_CARRITO personas, sacándolas de la
        fila una por una (siempre el primero), así que suben en orden de llegada.
        """
        subidos = []
        while len(subidos) < CAPACIDAD_CARRITO:
            v = self.fila.desencolar()                  # <-- COLA: desencolar (FIFO)
            if v is None:  # se acabó la fila antes de llenar el carrito
                break
            subidos.append(v)
        if not subidos:
            self.lbl_fila_msg.config(text="No hay nadie en la fila.")
            return
        self.subieron += len(subidos)
        self.lbl_fila_msg.config(text="Suben (en orden de llegada): " + ", ".join(subidos)
                                 + ". " + self._texto_frente())
        self._dibujar_fila()
        self._animar_carrito(subidos)
        self._actualizar_stats()

    def _animar_carrito(self, nombres):
        """
        Lleva el carrito por la pista: sale de la ENTRADA, sube y baja las
        colinas (lento al subir, rápido al bajar) y termina en la SALIDA.
        No regresa a la estación: ahí se bajan los pasajeros y el carro se va por un túnel.

        La velocidad se calcula con el RELOJ (DURACION_VIAJE segundos en total),
        así el viaje dura lo mismo en cualquier computador.
        """
        self._token_carrito += 1          # cualquier viaje anterior se detiene
        tok = self._token_carrito
        c = self.cv_carrito
        c.delete("all")
        ancho = max(c.winfo_width(), 500)
        pts = self._pista(ancho)
        self._dibujar_pista(c, ancho, pts)
        self._dibujar_vagon(c, pts[0][0], pts[0][1], nombres, tags=("carrito",))
        c.create_text(ancho - 16, 16, anchor="e", text="¡Wiiiii!", fill=DORADO,
                      font=("Helvetica", 14, "bold"), tags="wii")
        self.lbl_viaje.config(text="En el carrito (de adelante hacia atrás): "
                                   + self._texto_viaje(nombres))

        # "Costo de tiempo" de cada tramo: subir cuesta más (lento), bajar menos (rápido).
        costos = [0.0]
        for i in range(len(pts) - 1):
            bajada = pts[i + 1][1] - pts[i][1]               # > 0 si el riel baja
            costos.append(costos[-1] + max(0.3, 1 - 0.45 * bajada))
        # Segundo en el que el carrito debe estar en cada punto de la pista.
        tiempos = [t * DURACION_VIAJE / costos[-1] for t in costos]

        estado = {"i": 0, "t0": time.perf_counter()}

        def avanzar():
            if tok != self._token_carrito:
                return
            i = estado["i"]
            if i >= len(pts) - 1:         # llegó al final de la pista
                self._bajar(c, tok, nombres, pts[-1], ancho)
                return
            transcurrido = time.perf_counter() - estado["t0"]
            j = i
            while j < len(pts) - 1 and tiempos[j + 1] <= transcurrido:
                j += 1                    # avanza hasta donde toca según el reloj
            if j != i:
                c.move("carrito", pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
                estado["i"] = j
            self.after(10, avanzar)

        avanzar()
    def _bajar(self, c, tok, nombres, fin, ancho):
        """
        Final del viaje: los pasajeros bajan en la SALIDA y el carro vacío
        sigue de largo hacia el túnel. Después aparece otro carro en la estación.
        """
        if tok != self._token_carrito:
            return
        vigente = lambda: tok == self._token_carrito
        x, y = fin
        c.delete("carrito")
        c.delete("wii")
        self.lbl_viaje.config(text="Último viaje (de adelante hacia atrás): "
                                   + self._texto_viaje(nombres))
        self._dibujar_vagon(c, x, y, [], tags=("carro",))
        w = 40 * max(len(nombres), 2) + 16
        for i, nombre in enumerate(nombres):
            dibujar_persona(c, x + w / 2 + 30 + i * 40, y - 22,
                            color_de(nombre), nombre, tags=("bajan",))
        c.tag_raise("tunel")
        c.create_text(ancho / 2, 22, text="¡Fin del viaje! Los pasajeros bajan por la salida",
                      fill=DORADO, font=("Helvetica", 13, "bold"))

        def carro_al_tunel():
            if not vigente():
                return
            mover_suave(self, c, "carro", 420, pasos=45, intervalo=16, vigente=vigente,
                        al_terminar=lambda: self.after(
                            500, lambda: vigente() and self._pintar_estacion(
                                "Llegó otro carrito a la estación")))

        mover_suave(self, c, "bajan", 40, pasos=25, intervalo=20, vigente=vigente,
                    al_terminar=lambda: (c.delete("bajan"), carro_al_tunel()))
    # ==================================================================
    # PARTE 2: PILA - Libro de reclamos con "deshacer"
    # ==================================================================
    def _crear_tab_reclamos(self):
        """Pestaña del libro de reclamos: cajas apiladas, controles e historial."""
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="  Libro de reclamos · PILA  ")

        self._banner(tab, "PILA (LIFO): cada acción se pone ENCIMA de las demás. "
                          "Deshacer siempre quita la de ARRIBA, la más reciente.", MORADO)

        # --- Controles ---
        controles = ttk.Frame(tab)
        controles.pack(fill="x")
        ttk.Label(controles, text="Tipo:").pack(side="left")
        self.cb_tipo = ttk.Combobox(controles, values=list(PLANTILLAS_ACCION),
                                    state="readonly", width=16)
        self.cb_tipo.current(0)
        self.cb_tipo.pack(side="left", padx=6)
        Tooltip(self.cb_tipo, "Qué tipo de acción vas a registrar.")

        ttk.Label(controles, text="Cliente:").pack(side="left", padx=(10, 0))
        self.ent_cliente = ttk.Entry(controles, width=16)
        self.ent_cliente.pack(side="left", padx=6)
        self.ent_cliente.bind("<Return>", lambda e: self.ent_comentario.focus_set())
        Tooltip(self.ent_cliente, "Nombre de la persona. Si lo dejas vacío, dirá 'Anónimo'.\n"
                                  "Enter pasa al campo de comentario.")

        ttk.Label(controles, text="Comentario:").pack(side="left", padx=(10, 0))
        self.ent_comentario = ttk.Entry(controles, width=36)
        self.ent_comentario.pack(side="left", padx=6, fill="x", expand=True)
        self.ent_comentario.bind("<Return>", lambda e: self.registrar_accion())
        Tooltip(self.ent_comentario, "Opcional: agrega un detalle a la acción "
                                     "(por ejemplo, el motivo del reclamo).\nEnter registra.")

        botones = ttk.Frame(tab)
        botones.pack(fill="x", pady=(8, 0))
        b = ttk.Button(botones, text="Registrar (apilar)", style="Verde.TButton",
                       command=self.registrar_accion)
        b.pack(side="left", padx=(0, 4))
        Tooltip(b, "APILAR: crea la acción con la hora y el comentario, y la pone "
                   "ENCIMA de todas.\nEs Pila.apilar().")

        b = ttk.Button(botones, text="Deshacer (Ctrl+Z)", style="Rosa.TButton",
                       command=self.deshacer_accion)
        b.pack(side="left", padx=(24, 4))
        Tooltip(b, "DESAPILAR: quita la acción de ARRIBA (la más reciente) y la muestra.\n"
                   "Es Pila.desapilar(). También funciona con Ctrl+Z.")
        self.bind("<Control-z>", lambda e: self.deshacer_accion())

        # --- Pila dibujada ---
        ttk.Label(tab, text="Pila de acciones vigentes (la caja de arriba es lo que se deshace primero)"
                  ).pack(anchor="w", pady=(14, 4))
        self.cv_pila = tk.Canvas(tab, bg=LIENZO, height=270, highlightthickness=0)
        self.cv_pila.pack(fill="x")
        self.cv_pila.bind("<Configure>", lambda e: self._dibujar_pila())

        # --- Historial en lista ---
        ttk.Label(tab, text="Historial completo (arriba = más reciente)").pack(anchor="w", pady=(10, 4))
        marco = tk.Frame(tab, bg=LIENZO)
        marco.pack(fill="both", expand=True)
        self.lst_reclamos = tk.Listbox(marco, bg=LIENZO, fg=TXT, font=("Courier", 12),
                                       selectbackground=ROSA, highlightthickness=0,
                                       borderwidth=0, height=5)
        barra = ttk.Scrollbar(marco, command=self.lst_reclamos.yview)
        self.lst_reclamos.config(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lst_reclamos.pack(side="left", fill="both", expand=True)

        # --- Pie ---
        pie = ttk.Frame(tab)
        pie.pack(fill="x", pady=(8, 0))
        self.lbl_reclamo_msg = ttk.Label(pie, text="Aún no hay acciones registradas.")
        self.lbl_reclamo_msg.pack(side="left")
        b = ttk.Button(pie, text="Guardar historial", style="Celeste.TButton",
                       command=self.guardar_historial)
        b.pack(side="right")
        Tooltip(b, "Guarda el historial en un archivo .txt (de la más antigua a la más reciente).")

        self._dibujar_pila()

    def _dibujar_caja(self, c, x, base_y, pos, accion, color, ancho_caja, tags):
        """
        Dibuja una caja de la pila con forma de boleto.
        pos = 0 es la caja de abajo; cada posición sube una altura de caja.
        `accion` es un diccionario con hora, texto y comentario.
        Si la acción tiene comentario, se muestra en una segunda línea.
        """
        h, gap = 54, 10
        y2 = base_y - pos * (h + gap) - 6
        y1 = y2 - h
        c.create_rectangle(x, y1, x + ancho_caja, y2, fill=color,
                           outline="#ffffff", width=2, tags=tags)
        # Muescas laterales (como un boleto)
        c.create_oval(x - 8, y1 + h / 2 - 8, x + 8, y1 + h / 2 + 8, fill=LIENZO,
                      outline="", tags=tags)
        c.create_oval(x + ancho_caja - 8, y1 + h / 2 - 8, x + ancho_caja + 8,
                      y1 + h / 2 + 8, fill=LIENZO, outline="", tags=tags)

        cx, cy = x + ancho_caja / 2, y1 + h / 2
        linea1 = f"[{accion['hora']}] {accion['texto']}"
        comentario = accion["comentario"]
        if comentario:
            if len(comentario) > 58:
                comentario = comentario[:57] + "…"
            c.create_text(cx, cy - 10, text=linea1, fill=FONDO, tags=tags,
                          font=("Helvetica", 11, "bold"), width=ancho_caja - 40)
            c.create_text(cx, cy + 11, text="Comentario: " + comentario, fill=FONDO,
                          font=("Helvetica", 10, "italic"), width=ancho_caja - 40, tags=tags)
        else:
            c.create_text(cx, cy, text=linea1, fill=FONDO,
                          font=("Helvetica", 11, "bold"), width=ancho_caja - 40, tags=tags)
    def _dibujar_pila(self, animacion=None, saliente=None):
        """
        Dibuja la pila de cajas con el encargado a un lado.

        animacion : "push" -> la caja nueva cae desde arriba.
        saliente  : texto de la caja que se acaba de deshacer; vuela hacia la derecha.
        """
        c = self.cv_pila
        c.delete("all")
        ancho = max(c.winfo_width(), 500)
        alto = max(c.winfo_height(), 300)
        base_y = alto - 50
        caja_ancho = min(520, ancho - 320)
        x1 = 60

        # Plataforma donde se apilan las cajas
        c.create_rectangle(x1 - 30, base_y, x1 + caja_ancho + 30, base_y + 12,
                           fill="#3b3585", outline="")

        acciones = self.reclamos.a_lista()    # de la más reciente a la más antigua
        n = len(acciones)
        for i, texto in enumerate(acciones):
            pos = n - 1 - i                    # así la más reciente queda arriba
            h, gap = 54, 10
            y1 = base_y - pos * (h + gap) - 6 - h
            if y1 < 5:                         # ya no cabe en el canvas
                c.create_text(x1, 20, anchor="w", fill=TXT_SUAVE,
                              text=f"(hay {n - i} acciones más abajo, no caben en pantalla)",
                              font=("Helvetica", 10, "italic"))
                break
            tags = ("caja", "tope") if i == 0 else ("caja",)
            self._dibujar_caja(c, x1, base_y, pos, texto,
                               CAMISETAS[pos % len(CAMISETAS)], caja_ancho, tags)
            if i == 0:
                c.create_text(x1 + caja_ancho + 22, y1 + 27, anchor="w", fill=DORADO,
                              text="◀ TOPE\n(se deshace primero)",
                              font=("Helvetica", 10, "bold"), tags=("tope",))

        # Encargado (muñeco) junto a la pila
        dibujar_persona(c, ancho - 80, base_y - 60, DORADO, "Encargado")

        # Animación de la caja nueva: cae desde arriba
        if animacion == "push" and n > 0:
            c.move("tope", 0, -260)
            mover_suave(self, c, "tope", 0, 260, pasos=18, intervalo=16)

        # Animación de la caja deshecha: sale volando hacia la derecha
        if saliente is not None:
            pos = n                            # justo encima de la pila actual
            self._dibujar_caja(c, x1, base_y, pos, saliente, DORADO, caja_ancho, ("vuelo",))
            mover_suave(self, c, "vuelo", 420, -160, pasos=22, intervalo=16,
                        al_terminar=lambda: c.delete("vuelo"))

    def _texto_accion(self, accion):
        """Convierte una acción (diccionario) en una línea de texto legible."""
        linea = f"[{accion['hora']}] {accion['texto']}"
        if accion["comentario"]:
            linea += f" | Comentario: {accion['comentario']}"
        return linea

    def registrar_accion(self):
        """Arma la acción (hora, texto y comentario) y la apila encima de las demás."""
        cliente = self.ent_cliente.get().strip() or "Anónimo"
        comentario = self.ent_comentario.get().strip()
        texto = PLANTILLAS_ACCION[self.cb_tipo.get()].format(cliente)
        accion = {"hora": f"{datetime.now():%H:%M:%S}",
                  "texto": texto,
                  "comentario": comentario}
        self.reclamos.apilar(accion)                    # <-- PILA: apilar
        self.ent_cliente.delete(0, "end")
        self.ent_comentario.delete(0, "end")
        self.lbl_reclamo_msg.config(text=f"Registrado (apilado arriba): {texto}")
        self._dibujar_pila(animacion="push")
        self._refrescar_reclamos()
    def deshacer_accion(self):
        """Deshace la acción MÁS RECIENTE (LIFO) y muestra cuál fue."""
        accion = self.reclamos.desapilar()              # <-- PILA: desapilar (LIFO)
        if accion is None:
            self.lbl_reclamo_msg.config(text="No hay nada que deshacer.")
            return
        self.lbl_reclamo_msg.config(
            text=f"Se deshizo la de arriba: {self._texto_accion(accion)}")
        self._dibujar_pila(saliente=accion)
        self._refrescar_reclamos()
    def _refrescar_reclamos(self):
        """Vuelve a llenar la lista con el historial vigente (más reciente arriba)."""
        self.lst_reclamos.delete(0, "end")
        for i, accion in enumerate(self.reclamos.a_lista()):
            self.lst_reclamos.insert("end", ("▶ " if i == 0 else "   ") + self._texto_accion(accion))
        self._actualizar_stats()
    def guardar_historial(self):
        """(Extra) Guarda el historial vigente en un .txt, de la más antigua a la más reciente."""
        if self.reclamos.esta_vacia():
            messagebox.showinfo("Historial vacío", "No hay acciones para guardar.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".txt",
                                            initialfile="historial_reclamos.txt",
                                            filetypes=[("Texto", "*.txt")])
        if not ruta:
            return
        with open(ruta, "w", encoding="utf-8") as f:
            # a_lista() va de reciente a antigua; lo invertimos para el archivo.
            for accion in reversed(self.reclamos.a_lista()):
                f.write(self._texto_accion(accion) + "\n")
        messagebox.showinfo("Listo", "Historial guardado.")

    # ==================================================================
    # PARTE 3: RECURSIVIDAD - Fuegos artificiales
    # ==================================================================
    def _crear_tab_fuegos(self):
        """Pestaña del cierre: banner, botones y el cielo."""
        tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(tab, text="  Cierre · RECURSIVIDAD  ")

        self._banner(tab, "RECURSIVIDAD: la función explotar() se llama a sí misma sobre cada "
                          "partícula, con la mitad del tamaño, hasta llegar al caso base "
                          "(la partícula es demasiado chica).", VERDE)

        controles = ttk.Frame(tab)
        controles.pack(fill="x")
        b = ttk.Button(controles, text="Lanzar fuegos", style="Rosa.TButton",
                       command=self.lanzar_fuegos)
        b.pack(side="left")
        Tooltip(b, "Lanza el cohete. Al llegar arriba se llama a explotar(), "
                   "la función recursiva.")
        b = ttk.Button(controles, text="Limpiar cielo", style="Celeste.TButton",
                       command=self.limpiar_cielo)
        b.pack(side="left", padx=8)
        Tooltip(b, "Cancela las animaciones pendientes y borra el cielo.")
        self.lbl_fuegos = ttk.Label(
            controles, text="Cuantos más visitantes hayan subido, más grande es la explosión.")
        self.lbl_fuegos.pack(side="left", padx=12)

        self.cv_fuegos = tk.Canvas(tab, bg="#05021a", highlightthickness=0)
        self.cv_fuegos.pack(fill="both", expand=True, pady=(10, 0))

    def limpiar_cielo(self):
        """Cancela las animaciones pendientes y borra el cielo."""
        for i in self.ids_fuegos:
            try:
                self.after_cancel(i)
            except Exception:
                pass  # si ya se ejecutó, no pasa nada
        self.ids_fuegos.clear()
        self.cv_fuegos.delete("all")

    def lanzar_fuegos(self):
        """
        Lanza el cohete y, al llegar arriba, llama a la función recursiva explotar().
        El radio inicial crece con los visitantes que subieron, con un tope
        proporcional a la ventana.
        """
        self.limpiar_cielo()
        c = self.cv_fuegos
        c.update_idletasks()
        ancho, alto = max(c.winfo_width(), 300), max(c.winfo_height(), 300)

        radio = min(80 + self.subieron * 8, alto * 0.30, ancho * 0.30)
        x = ancho / 2          # el cohete sube por el centro
        y_alto = alto * 0.36   # altura donde explota

        def al_llegar():
            """Cuando el cohete llega arriba, empieza la recursión."""
            c.delete("cohete")
            total = explotar(c, self.ids_fuegos, x, y_alto, radio)   # <-- RECURSIÓN
            self.lbl_fuegos.config(
                text=f"Radio inicial: {radio:.0f}px   Partículas generadas: {total}")
            self.ids_fuegos.append(c.after(
                4200, lambda: c.create_text(ancho / 2, alto - 40,
                                            text="¡Gracias por visitarnos! Hasta mañana",
                                            fill=DORADO, font=("Helvetica", 20, "bold"))))

        lanzar_cohete(c, self.ids_fuegos, x, alto - 10, y_alto, al_llegar)


# Punto de entrada: crea la ventana y arranca el ciclo de eventos de tkinter.
if __name__ == "__main__":
    Parque().mainloop() 