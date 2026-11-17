# Centroide de un Árbol: Búsqueda en Tiempo Lineal

## Overview
- **Topic**: Centroide de un árbol y su algoritmo de búsqueda en $O(n)$
- **Hook**: ¿Cómo podemos dividir un árbol de $n$ nodos de la forma más balanceada posible eliminando un solo vértice?
- **Target Audience**: Estudiantes de Algoritmos y Estructuras de Datos (CS2023)
- **Estimated Length**: ~1 minuto 55 segundos (dentro del rango sugerido de 1–2 min)
- **Key Insight**: Si desde cualquier nodo existe un subárbol vecino con más de $\lfloor n/2 \rfloor$ nodos, moverse hacia él *siempre* nos acerca al centroide y nunca necesitamos retroceder.

## Narrative Arc
Partimos del problema práctico de dividir un árbol de forma balanceada (ej. *Divide & Conquer* en árboles). Definimos visualmente qué es un centroide ($\text{máx. componente} \le \lfloor n/2 \rfloor$). Luego mostramos en vivo la ejecución del algoritmo real en dos fases —cálculo de tamaños con DFS y caminata greedy hacia el subárbol pesado—, probamos el caso borde de un árbol estrella, y cerramos demostrando la complejidad $O(n)$ junto con los créditos y referencia.

---

## Color Palette & Visual Style (Editorial / Lemnismath)
- **Background**: `#FAF6F0` (Papel crema cálido)
- **Ink (Texto, fórmulas y aristas)**: `#3D3834` (Gris carbón cálido)
- **Primary (Nodos estándar)**: `#2E86DE` con base/sombra `#1B5E9E` (Ficha táctil azul editorial)
- **Accent / Heavy Subtree**: `#D94E28` con base/sombra `#9E3215` (Terracota cálido para subárboles $> \lfloor n/2 \rfloor$)
- **Centroid / Balanced**: `#2A9D6F` con base/sombra `#1B6E4C` (Verde salvia para el centroide y componentes válidas)
- **Highlight / Pointer**: `#D9822B` (Ámbar cálido para el puntero actual y anotaciones)
- **Typography**: Serif editorial (`Tex` / `MathTex` Computer Modern o fuente serif para títulos)

---

## Scene 1: Portada e Introducción Conceptual
**Duration**: ~25 segundos
**Purpose**: Presentar el proyecto, plantear el problema y definir visualmente el centroide de un árbol.

### Visual Elements
- Lámina de título minimalista sobre papel crema: *"Centroide de un Árbol"* y subtítulo *"CS2023 — Algoritmos y Estructuras de Datos"*.
- Transformación suave hacia un árbol de ejemplo de 9 nodos con fichas azules.
- Fórmula clave en pantalla: $\text{tamaño de cada componente} \le \lfloor n/2 \rfloor$.
- Animación comparativa: eliminar un nodo hoja (deja una componente gigante de 8 nodos, marcado en terracota) vs. eliminar el centroide (deja componentes pequeñas y balanceadas, marcadas en verde).

### Content
1. Aparece el título del proyecto (2.5s) y se desvanece suavemente para dar paso al árbol.
2. Se muestra un árbol de 9 nodos ($\lfloor 9/2 \rfloor = 4$).
3. Se simula quitar un nodo extremo: la componente restante queda demasiado grande ($8 > 4$).
4. Se restaura y se resalta la condición de equilibrio: ninguna componente puede superar $\lfloor n/2 \rfloor$.

### Narration Notes (Guion sugerido para voz en off)
> *"Imagina que quieres dividir un árbol de $n$ nodos de la forma más equilibrada posible, eliminando un solo vértice. Si quitas una hoja o un extremo, casi todo el árbol queda unido en un solo bloque. Un **centroide** es justamente ese nodo especial cuya eliminación garantiza que todas las componentes resultantes tengan a lo más $\lfloor n/2 \rfloor$ nodos. Es la base de algoritmos como Centroid Decomposition para aplicar Divide y Vencerás en árboles."*

### Technical Notes
- Crear un helper `TokenNode` (`VGroup` de dos círculos superpuestos con ligero offset vertical) para el efecto de ficha 2.5D sobre papel.
- Dejar márgenes amplios (~0.8u) para mantener la estética limpia de lámina.

---

## Scene 2: Ejecución Real del Algoritmo (DFS + Búsqueda del Centroide)
**Duration**: ~45 segundos
**Purpose**: Mostrar paso a paso el algoritmo real implementado en Python (portado de `Centroid.cpp`) sobre una instancia ilustrativa de 9 nodos.

### Visual Elements
- Árbol de 9 nodos enraizado en el nodo `1` (ubicado en un extremo para que el algoritmo deba dar al menos 2 saltos).
- Panel lateral derecho tipo "tarjeta de papel" (`#F3ECE1`) que muestra:
  - $n = 9$, límite $\lfloor n/2 \rfloor = 4$.
  - Fase actual (`Fase 1: DFS` $\rightarrow$ `Fase 2: Caminata Greedy`).
- Etiquetas dinámicas `size[u]` junto a cada ficha.
- Puntero ámbar (`#D9822B`) que recorre los nodos durante la caminata.

### Content
1. **Fase 1 (DFS desde `1`):** El algoritmo Python ejecuta `dfs(1)`. Las aristas se recorren e iluminan, y al regresar de cada llamada recursiva aparece el tamaño real `sizes[u]` junto a cada nodo.
2. **Fase 2 (Caminata Greedy):**
   - El puntero inicia en `u = 1`. Revisa su hijo pesado (`sizes[v] = 8 > 4`). El subárbol se tiñe de terracota y el puntero salta a `v`.
   - En el siguiente nodo evalúa nuevamente a sus hijos; encuentra otro con tamaño `> 4` y avanza.
   - Al llegar al nodo centroide, todos sus hijos tienen tamaño $\le 4$ (y la parte superior restante $n - \text{size}[u] \le 4$).
3. **Verificación visual:** El nodo centroide se corona en verde salvia (`#2A9D6F`), sus aristas se desvanecen suavemente para simular su eliminación y cada componente resultante muestra su conteo $\le 4$.

### Narration Notes (Guion sugerido para voz en off)
> *"¿Cómo lo encontramos sin probar cada nodo? En dos pasos muy simples. Primero, enraizamos el árbol en cualquier nodo —aquí el nodo 1— y lanzamos un DFS para calcular el tamaño de cada subárbol. Luego, comenzamos una caminata desde la raíz: miramos si algún hijo tiene más de $\lfloor n/2 \rfloor$ nodos. Como aquí ese subárbol pesa más de la mitad, sabemos con certeza que el centroide está allá abajo, así que avanzamos hacia él. Repetimos hasta llegar a un nodo donde ningún vecino supera $\lfloor n/2 \rfloor$. Al eliminarlo, todas las piezas quedan equilibradas."*

### Technical Notes
- Impulsar cada `play(...)` leyendo la lista de eventos retornada por `find_centroid_trace(edges, root=1)`.
- No hardcodear los valores de `sizes` ni la secuencia de saltos.

---

## Scene 3: Caso Borde — Árbol Estrella
**Duration**: ~20 segundos
**Purpose**: Demostrar el comportamiento del algoritmo real en un caso límite muy visual: un árbol estrella ($n = 7$, un centro conectado a 6 hojas).

### Visual Elements
- Disposición radial: nodo `2` en el centro, rodeado por 6 hojas (`1, 3, 4, 5, 6, 7`).
- Enraizado en una hoja (nodo `1`, arriba/izquierda) para ver qué ocurre cuando empezamos desde el peor extremo de la estrella.

### Content
1. El mismo algoritmo Python corre sobre el árbol estrella.
2. El DFS asigna `size = 1` a las 5 hojas restantes, `size = 6` al centro y `size = 7` a la raíz hoja `1`.
3. En la caminata greedy, desde `1` detecta inmediatamente `size[centro] = 6 > 3`, da un único salto al centro y termina ahí.
4. Se separan brevemente las 6 hojas alrededor del centroide para mostrar que cada componente tiene tamaño $1 \le 3$.

### Narration Notes (Guion sugerido para voz en off)
> *"Veamos un caso borde interesante: un árbol estrella de 7 nodos, donde un vértice central conecta con 6 hojas. Incluso si empezamos el algoritmo desde una de las hojas, el DFS detecta que el nodo central sostiene a casi todo el árbol. En un solo salto el puntero llega al centro y confirma que, al quitarlo, cada hoja queda aislada con tamaño 1, muy por debajo del límite 3."*

### Technical Notes
- Reutilizar el mismo motor de animación de la Escena 2 pasándole la lista de aristas de la estrella.

---

## Scene 4: Complejidad Temporal, Créditos y Referencia
**Duration**: ~20 segundos
**Purpose**: Justificar formalmente la complejidad $O(n)$ y cerrar con los integrantes y la referencia solicitada.

### Visual Elements
- Tarjeta resumen dividida en dos bloques limpios:
  - **Fase 1 (DFS):** Cada vértice y arista se visita una vez $\rightarrow O(n)$.
  - **Fase 2 (Caminata):** Solo avanza hacia el único subárbol $> \lfloor n/2 \rfloor$, nunca retrocede $\rightarrow O(n)$.
  - **Complejidad Total:** Tiempo $O(n)$ | Espacio $O(n)$.
- Transición a lámina final con:
  - Título: *Centroide de un Árbol*
  - Integrantes: Maxwell Gregorio Lupus Collazos Solis, Renzo Vladimir Cuba Zari, José Luis Villalobos Jiménez.
  - Referencia: `geeksforgeeks.org/dsa/centroid-decomposition-of-tree/`

### Content
1. Aparecen las dos ecuaciones/bloques de complejidad y se suman en $O(n)$.
2. Breve pausa para la voz en off.
3. Desvanecimiento a los créditos finales y referencia.

### Narration Notes (Guion sugerido para voz en off)
> *"Analizando su complejidad: el DFS inicial recorre cada nodo y arista exactamente una vez en tiempo $O(n)$. Y en la segunda fase, como solo puede existir a lo más un subárbol con más de la mitad de los nodos, el puntero avanza en una sola dirección sin retroceder jamás, tomando también $O(n)$ en el peor caso. Así, encontramos un centroide en tiempo y espacio lineal $O(n)$. ¡Gracias por ver!"*

---

## Implementation Order
1. **`centroid_algo.py`**: Portar `Centroid.cpp` a Python generando eventos estructurados (`DFSEnter`, `DFSSize`, `CheckChild`, `MoveTo`, `FoundCentroid`) para cualquier grafo árbol.
2. **`theme.py`**: Paleta Lemnismath, tipografía, componente `TokenNode` (ficha 2.5D) y tarjetas de papel.
3. **`scene.py`**: Implementar las 4 escenas en ManimCE conectadas a `centroid_algo.py`.
4. **Render de prueba** en baja calidad (`-pql`) para ajustar tiempos con el guion de voz en off, y render final en `1080p60` (`-pqh`).
