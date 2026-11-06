# ironfox-banner

Pantalla de bienvenida para la terminal con estilo *Cyberpunk: Edgerunners*:
cabecera `[ NC-2077 ]`, tu usuario en grande, una frase aleatoria, datos del
sistema (distro, escritorio, shell, GPU, kernel, red) y un logo a la derecha.
Está hecha en Python, sin dependencias de Python, y pensada para **kitty**.

*English: a small Python script that prints an Edgerunners-style system banner
in the kitty terminal, with selectable colour palettes.*

## Requisitos

- **kitty 0.40 o superior** (el logo y el texto grande usan funciones de kitty).
- **python3** y **pciutils** (para leer la GPU con `lspci`).
- Opcional: **python-pillow**, solo para crear paletas desde una imagen.
- Opcional: los dotfiles de Lyne. Si los tienes, cada tema de Lyne recuerda su paleta. Sin Lyne funciona igual.

## Instalación

```bash
git clone https://github.com/TU_USUARIO/ironfox-banner.git
cd ironfox-banner
./install.sh
python3 ~/.config/edgerunners/edge.py
```

El instalador copia todo a `~/.config/edgerunners/`. Para que salga al abrir la
terminal, añade esto **al principio** de tu `~/.zshrc` (si usas powerlevel10k, tiene
que ir antes del instant prompt):

```bash
if [[ -z $TMUX && -z $NVIM && -n $KITTY_WINDOW_ID ]]; then
  python3 ~/.config/edgerunners/edge.py
fi
```

## Tu logo

El repo **no incluye imagen**. Copia un PNG a `~/.config/edgerunners/image.png` y
saldrá a la derecha. Sin imagen, el banner sale igual pero sin logo.

## Paletas de colores

```bash
python3 ~/.config/edgerunners/edge.py tema                     # ver las paletas
python3 ~/.config/edgerunners/edge.py tema probar hielo        # verla sin guardar
python3 ~/.config/edgerunners/edge.py tema hielo               # elegirla
python3 ~/.config/edgerunners/edge.py tema crear rosa ff66aa ffffff aa3377
python3 ~/.config/edgerunners/edge.py tema imagen agua foto.png   # sacar colores de una foto
python3 ~/.config/edgerunners/edge.py tema borrar rosa
```

Con `crear`, el primer color pinta títulos y etiquetas de la derecha, el segundo
las líneas y `LOGIN`, y el tercero las etiquetas de la izquierda. Si quieres un
alias corto: `alias tema='python3 ~/.config/edgerunners/edge.py tema'`.

## Frases

Edita `~/.config/edgerunners/frases.txt`: una frase por línea, con el formato
`frase blanca | frase de acento` (la segunda parte es opcional).

## Aviso

Proyecto de fans, sin relación con CD PROJEKT RED, Studio Trigger ni Netflix.
Los nombres y las frases pertenecen a sus dueños. Las imágenes no se incluyen.

## Licencia

MIT. Mira el archivo `LICENSE`.
