#!/usr/bin/env bash
set -e
D="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.config/edgerunners"

mkdir -p "$DEST/themes"
cp "$D/edge.py" "$DEST/edge.py"
# las frases solo se copian si no tienes ya las tuyas
[ -f "$DEST/frases.txt" ] || cp "$D/frases.txt" "$DEST/frases.txt"

echo
echo "Instalado en $DEST"
if [ ! -f "$DEST/image.png" ]; then
    echo "Falta tu logo: copia una imagen PNG a $DEST/image.png (sin ella sale sin logo)."
fi
echo
echo "Pruebalo (dentro de kitty):  python3 $DEST/edge.py"
echo
echo "Para que salga solo, pon esto AL PRINCIPIO de tu ~/.zshrc (o ~/.bashrc):"
echo '  if [[ -z $TMUX && -z $NVIM && -n $KITTY_WINDOW_ID ]]; then python3 ~/.config/edgerunners/edge.py; fi'
echo
echo "Cambiar colores:  python3 $DEST/edge.py tema"
