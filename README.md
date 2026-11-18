# Centroide de un Árbol

**Integrantes:**
- Maxwell Gregorio Lupus Collazos Solis
- Renzo Vladimir Cuba Zari
- José Luis Villalobos Jiménez

**Referencia:**
- [Centroid Decomposition of Tree — GeeksforGeeks](https://www.geeksforgeeks.org/dsa/centroid-decomposition-of-tree/)

---

## Estructura del proyecto

- `Centroid.cpp`: Implementación original del algoritmo en C++.
- `centroid_algo.py`: Implementación en Python que ejecuta el algoritmo en tiempo real y genera la traza de eventos para la animación.
- `scene.py`: Escenas de Manim Community Edition (`Parte1`, `Parte2`, `Parte3` y `CentroidFullVideo`).
- `index.html`: Presentación web interactiva equivalente a la animación.

---

## Software requerido

- **Python** (`>=3.11, <3.14`)
- **FFmpeg** (`ffmpeg`)
- **LaTeX** (`latex`, `dvisvgm` — paquete básico de TeX Live + `amsmath`/`amssymb`)
- Dependencias de sistema requeridas por ManimCE (`cairo`, `pango`, `pkg-config`).

---

## Instalación y compilación

### Opción 1: Con `pip`

1. Crear y activar un entorno virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   *(En Windows: `.venv\Scripts\activate`)*

2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Renderizar el video:
   ```bash
   # Video completo en alta definición (1080p60)
   manim -qh scene.py CentroidFullVideo

   # O cada parte por separado:
   manim -qh scene.py Parte1 Parte2 Parte3

   # Vista previa rápida (480p15)
   manim -pql scene.py CentroidFullVideo
   ```

### Opción 2: Con `uv`

1. Sincronizar el entorno y las dependencias:
   ```bash
   uv sync
   ```

2. Renderizar el video:
   ```bash
   # Video completo en alta definición (1080p60)
   uv run manim -qh scene.py CentroidFullVideo

   # O cada parte por separado:
   uv run manim -qh scene.py Parte1 Parte2 Parte3

   # Vista previa rápida (480p15)
   uv run manim -pql scene.py CentroidFullVideo
   ```

Los archivos `.mp4` generados se guardan en `media/videos/scene/1080p60/` (o `480p15/` para vista previa).

---

## Ejecución del algoritmo por consola

```bash
# C++
g++ -O2 Centroid.cpp -o centroid && ./centroid

# Python
python3 centroid_algo.py
```
