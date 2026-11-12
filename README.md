# Parque de Diversiones — Quiz 2 (Estructuras de Datos)

Simulador de **«Un día en el parque»** con interfaz gráfica. El programa reúne tres herramientas vistas en clase:

| Parte | Estructura | Implementación |
| --- | --- | --- |
| Fila de la montaña rusa | **Cola (FIFO)** con nodos enlazados | `estructuras.py` → `Cola` |
| Libro de reclamos con opción de deshacer | **Pila (LIFO)** con nodos enlazados | `estructuras.py` → `Pila` |
| Fuegos artificiales de cierre | **Recursividad** | `fuegos.py` → `explotar()` |

## Requisitos

- Python 3.8 o posterior.
- No se necesitan paquetes adicionales. `tkinter` viene incluido con Python en Windows y macOS. En Linux, si no está instalado, puedes agregarlo con:

  ```bash
  sudo apt install python3-tk
  ```

## Cómo ejecutar

Desde la carpeta del proyecto, ejecuta:

```bash
python parque.py
```

## Cómo probarlo

1. **Montaña rusa:** agrega visitantes o pulsa **«+ Visitante aleatorio»**. Luego pulsa **«Subir al primero»**; sube siempre quien llegó antes.
2. **Reclamos:** registra varias acciones y pulsa **«Deshacer»**. Se deshace primero la acción más reciente. También puedes usar **Ctrl+Z**.
3. **Cierre:** pulsa **«Lanzar fuegos artificiales»**. Cuantos más visitantes hayan subido, más grande será la explosión.

El historial de reclamos también se puede guardar en un archivo de texto.

## Equipo

(Nombres de los integrantes)
Kendall A. Quesada Mendoza
Jose Mendez Mayorga.
