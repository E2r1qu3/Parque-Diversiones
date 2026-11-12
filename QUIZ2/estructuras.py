"""
estructuras.py
==============
Estructuras de datos propias del parque, implementadas con NODOS ENLAZADOS.

Contenido:
    - Nodo  : el "eslabon" basico que usan las dos estructuras.
    - Cola  : fila de la montana rusa     (FIFO: primero en entrar, primero en salir).
    - Pila  : libro de reclamos "deshacer" (LIFO: ultimo en entrar, primero en salir).

IMPORTANTE: no se usan list.append() / list.pop() como si fueran la cola o la
pila. La logica de enlazar y desenlazar nodos esta escrita a mano, que es lo
que pide el enunciado.

Idea general de una lista enlazada:

    [dato|siguiente] -> [dato|siguiente] -> [dato|siguiente] -> None

Cada nodo guarda un dato y una "flecha" (referencia) al nodo que sigue.
"""


class Nodo:
    """
    Un eslabon de la cadena.

    Atributos:
        dato      : lo que guarda el nodo (un nombre, una acción, etc.).
        siguiente : referencia al nodo que le sigue, o None si es el último.
    """

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None  # al crearse, todavía no apunta a nadie


# ======================================================================
# PARTE 1: COLA (FIFO) - La fila de la montaña rusa
# ======================================================================
class Cola:
    """
    Cola FIFO (First In, First Out): el primero que llega es el primero que sale.

    Se guardan DOS referencias para que agregar y sacar sea rápido:

        frente -> [A] -> [B] -> [C] <- final
        (sale primero)           (entró de último)

    Atributos:
        frente  : nodo del visitante que lleva más tiempo esperando.
        final   : nodo del último visitante que llegó.
        _tamano : cuántos elementos hay (para devolver len() sin recorrer todo).
    """

    def __init__(self):
        self.frente = None
        self.final = None
        self._tamano = 0

    def esta_vacia(self):
        """Devuelve True si no hay nadie en la fila."""
        return self.frente is None

    def encolar(self, dato):
        """
        Agrega un elemento al FINAL de la fila.

        Dos casos:
            - Fila vacía: el nuevo nodo es a la vez frente y final.
            - Fila con gente: el que era último ahora apunta al nuevo,
              y el nuevo pasa a ser el final.
        """
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo  # enlazamos al final de la cadena
            self.final = nuevo            # el nuevo es ahora el último
        self._tamano += 1

    def desencolar(self):
        """
        Saca y devuelve el elemento del FRENTE (el que lleva más tiempo esperando).
        Devuelve None si la fila está vacía.
        """
        if self.esta_vacia():
            return None

        nodo = self.frente
        self.frente = nodo.siguiente   # el segundo pasa a ser el primero

        # Si ya no queda nadie, también hay que limpiar la referencia al final,
        # si no 'final' quedaría apuntando a un nodo que ya salió.
        if self.frente is None:
            self.final = None

        self._tamano -= 1
        return nodo.dato

    def ver_frente(self):
        """Devuelve (sin sacar) el elemento que está al frente, o None si no hay."""
        return None if self.esta_vacia() else self.frente.dato

    def a_lista(self):
        """
        Recorre la cola de frente a final y devuelve los datos en una lista
        normal de Python. Solo sirve para MOSTRAR la cola en pantalla; no
        modifica nada.
        """
        datos = []
        actual = self.frente
        while actual is not None:
            datos.append(actual.dato)
            actual = actual.siguiente
        return datos

    def __len__(self):
        """Permite usar len(cola)."""
        return self._tamano


# ======================================================================
# PARTE 2: PILA (LIFO) - El libro de reclamos con "deshacer"
# ======================================================================
class Pila:
    """
    Pila LIFO (Last In, First Out): lo último que entró es lo primero que sale.
    Funciona igual que una pila de platos o el Ctrl+Z de un editor de texto.

        tope -> [acción 3] -> [acción 2] -> [acción 1] -> None
        (la más reciente)                   (la más antigua)

    Atributos:
        tope    : nodo de la acción más reciente.
        _tamano : cuántas acciones hay vigentes.
    """

    def __init__(self):
        self.tope = None
        self._tamano = 0

    def esta_vacia(self):
        """Devuelve True si no hay acciones registradas."""
        return self.tope is None

    def apilar(self, dato):
        """
        Registra una acción nueva ENCIMA de todas las demás.

        El nuevo nodo apunta al antiguo tope, y luego pasa a ser el tope.
        """
        nuevo = Nodo(dato)
        nuevo.siguiente = self.tope  # lo que había arriba queda debajo del nuevo
        self.tope = nuevo
        self._tamano += 1

    def desapilar(self):
        """
        Deshace la acción más reciente: la saca y la devuelve.
        Devuelve None si no hay nada que deshacer.
        """
        if self.esta_vacia():
            return None

        nodo = self.tope
        self.tope = nodo.siguiente  # la anterior pasa a ser la más reciente
        self._tamano -= 1
        return nodo.dato

    def ver_tope(self):
        """Devuelve (sin sacar) la acción más reciente, o None si no hay."""
        return None if self.esta_vacia() else self.tope.dato

    def a_lista(self):
        """
        Recorre la pila de la acción más reciente a la más antigua y devuelve
        una lista normal. Solo sirve para MOSTRAR el historial.
        """
        datos = []
        actual = self.tope
        while actual is not None:
            datos.append(actual.dato)
            actual = actual.siguiente
        return datos

    def __len__(self):
        """Permite usar len(pila)."""
        return self._tamano
