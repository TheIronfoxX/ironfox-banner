#!/usr/bin/env python3
import os, random, re, subprocess, shutil, sys

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def rgb(r, g, b):
    return f"\x1b[38;2;{r};{g};{b}m"

R, B = "\x1b[0m", "\x1b[1m"
PINK, CYAN, VIO = rgb(255, 64, 129), rgb(0, 229, 255), rgb(186, 156, 255)
WHITE, GRAY = "\x1b[97m", "\x1b[90m"

# colores del tema activo de Lyne (current-theme.conf de kitty); si falta algo, quedan los fijos
def _lyne_colors():
    c = {}
    try:
        for line in open(os.path.expanduser("~/.config/kitty/current-theme.conf")):
            p = line.split()
            if len(p) >= 2 and len(p[1]) == 7 and p[1].startswith("#"):
                c[p[0]] = tuple(int(p[1][i:i + 2], 16) for i in (1, 3, 5))
    except (OSError, ValueError):
        pass
    return c
_c = _lyne_colors()
if "color9" in _c: PINK = rgb(*_c["color9"])
if "color14" in _c: CYAN = rgb(*_c["color14"])
if "color13" in _c: VIO = rgb(*_c["color13"])
if "foreground" in _c: WHITE = rgb(*_c["foreground"])
if "color8" in _c: GRAY = rgb(*_c["color8"])

# paletas fijas (acento 1, acento 2, acento 3). Con "tema" se usan los colores de Lyne.
_PALETAS = {
    "cyberpunk": ((252, 238, 10), (0, 240, 255), (255, 0, 60)),
    "vaporwave": ((255, 113, 206), (1, 205, 254), (185, 103, 255)),
    "edgerunners": ((255, 64, 129), (0, 229, 255), (186, 156, 255)),
    "matrix": ((0, 255, 65), (0, 200, 140), (170, 255, 190)),
    "rojoblanco": ((255, 40, 60), (245, 245, 245), (214, 48, 63)),
    "noir": ((230, 30, 50), (255, 255, 255), (160, 160, 165)),
    "oceano": ((52, 201, 205), (190, 245, 240), (39, 150, 152)),
    "marino": ((70, 165, 235), (205, 235, 255), (40, 115, 195)),
    "sunset": ((255, 120, 50), (255, 210, 120), (255, 60, 110)),
    "hielo": ((90, 170, 255), (235, 245, 255), (150, 120, 255)),
    "toxico": ((190, 255, 0), (255, 0, 170), (120, 255, 200)),
}
# paleta elegida: variable EDGE_PALETTE > archivo ~/.config/edgerunners/paleta > rojoblanco
# la paleta se guarda POR CADA preset de Lyne: ~/.config/edgerunners/paletas/<preset>.txt
PRESET = sh("lyne theme 2>/dev/null | sed -n 's/^Active preset: //p'")
_TEMA_DIR = os.path.expanduser("~/.config/edgerunners/paletas")
_TEMA_FILE = os.path.join(_TEMA_DIR, re.sub(r"[^\w.-]", "_", PRESET or "_default") + ".txt")
def _tema_actual():
    try:
        return open(_TEMA_FILE).read().strip()
    except OSError:
        return ""

# paletas propias: ~/.config/edgerunners/mis-paletas.txt  (una por linea: nombre #hex #hex #hex)
_MIAS_FILE = os.path.expanduser("~/.config/edgerunners/mis-paletas.txt")
_MIAS = {}
_INTEGRADAS = set(_PALETAS)

def _hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _cargar_mias():
    try:
        for _l in open(_MIAS_FILE, encoding="utf-8"):
            _q = _l.split()
            if len(_q) == 4 and not _l.startswith("#"):
                try:
                    _MIAS[_q[0]] = tuple(_hex2rgb(x) for x in _q[1:])
                except ValueError:
                    pass
    except OSError:
        pass

_cargar_mias()
_PALETAS.update(_MIAS)

def _guardar_mias():
    os.makedirs(os.path.dirname(_MIAS_FILE), exist_ok=True)
    with open(_MIAS_FILE, "w", encoding="utf-8") as f:
        f.write("# nombre #acento1 #acento2 #acento3\n")
        for k, v in _MIAS.items():
            f.write(k + " " + " ".join("#%02x%02x%02x" % c for c in v) + "\n")

def _colores_de_imagen(path):
    try:
        import colorsys
        from PIL import Image
    except ImportError:
        print("Hace falta Pillow:  sudo pacman -S python-pillow")
        sys.exit(1)
    try:
        im = Image.open(os.path.expanduser(path)).convert("RGB")
    except OSError:
        print(f"No puedo abrir la imagen: {path}")
        sys.exit(1)
    im.thumbnail((200, 200))
    q = im.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:24]
    cuentas = q.getcolors() or []
    total = sum(n for n, _ in cuentas) or 1
    cand = []
    for n, idx in cuentas:
        r, g, b = pal[idx * 3:idx * 3 + 3]
        h, sa, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        cand.append((sa * (n / total) ** 0.5, h, sa))
    cand.sort(reverse=True)
    h1, s1 = cand[0][1], cand[0][2]
    def conv(h, sa, v):
        return tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(h, sa, v))
    a1 = conv(h1, min(0.85, max(0.5, s1)), 0.88)
    a2 = conv(h1, 0.12, 0.97)
    otro = None
    for _, h, sa in cand[1:]:
        d = abs(h - h1)
        if min(d, 1 - d) > 0.1 and sa > 0.2:
            otro = (h, sa)
            break
    a3 = conv(otro[0], min(0.85, max(0.5, otro[1])), 0.75) if otro else conv(h1, min(0.85, max(0.5, s1)), 0.62)
    return (a1, a2, a3)

if len(sys.argv) > 1 and sys.argv[1] in ("tema", "--tema"):
    _a = sys.argv[2:]
    _cmd = _a[0] if _a else ""

    def _relanzar():
        os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)])

    def _elegir(nombre):
        os.makedirs(_TEMA_DIR, exist_ok=True)
        open(_TEMA_FILE, "w").write(nombre + "\n")
        _relanzar()

    def _nombre_ok(n):
        if not re.fullmatch(r"[a-z0-9_-]+", n or ""):
            print("El nombre solo puede llevar letras minusculas, numeros, - y _")
            sys.exit(1)
        if n in _INTEGRADAS or n in ("lyne", "tema", "crear", "nueva", "imagen", "borrar", "probar", "ayuda"):
            print(f"'{n}' ya esta cogido, elige otro nombre.")
            sys.exit(1)
        return n

    def _lista():
        _act = os.environ.get("EDGE_PALETTE") or _tema_actual() or "rojoblanco"
        print(f"  Preset de Lyne: {PRESET or '(desconocido)'}\n")
        for _k, _v in _PALETAS.items():
            _sw = "".join(f"{rgb(*c)}\u2588\u2588{R} " for c in _v)
            print(f"  {_sw} {_k}" + ("  (tuya)" if _k in _MIAS else "") + ("   <-- actual" if _k == _act else ""))
        print("  (colores de Lyne)  lyne" + ("   <-- actual" if _act == "lyne" else ""))
        print("\n  tema NOMBRE                  elegir (se guarda para este preset de Lyne)")
        print("  tema probar NOMBRE           verla sin guardar")
        print("  tema crear NOMBRE A B C      crear con 3 colores hex, p. ej.  tema crear rosa ff66aa ffffff aa3377")
        print("  tema imagen NOMBRE foto.png  crear sacando los colores de una imagen")
        print("  tema borrar NOMBRE           borrar una tuya")

    try:
        if _cmd in ("crear", "nueva"):
            if len(_a) != 5:
                print("Uso:  tema crear NOMBRE A B C   (A=titulos, B=lineas y LOGIN, C=etiquetas izquierda)")
                sys.exit(1)
            _n = _nombre_ok(_a[1].lower())
            _MIAS[_n] = tuple(_hex2rgb(x) for x in _a[2:5])
            _guardar_mias()
            _elegir(_n)
        elif _cmd == "imagen":
            if len(_a) != 3:
                print("Uso:  tema imagen NOMBRE ruta/a/la/foto.png")
                sys.exit(1)
            _n = _nombre_ok(_a[1].lower())
            _MIAS[_n] = _colores_de_imagen(_a[2])
            _guardar_mias()
            _elegir(_n)
        elif _cmd == "borrar":
            _n = _a[1] if len(_a) > 1 else ""
            if _n not in _MIAS:
                print(f"'{_n}' no es una de tus paletas (las integradas no se pueden borrar).")
                sys.exit(1)
            del _MIAS[_n]
            _guardar_mias()
            print(f"Borrada: {_n}")
            sys.exit(0)
        elif _cmd == "probar":
            _n = _a[1] if len(_a) > 1 else ""
            if _n not in _PALETAS and _n != "lyne":
                print(f"No existe la paleta '{_n}'.")
                sys.exit(1)
            os.environ["EDGE_PALETTE"] = _n
            _relanzar()
        elif _cmd in _PALETAS or _cmd == "lyne":
            _elegir(_cmd)
        elif _cmd and _cmd != "ayuda":
            print(f"No existe la paleta '{_cmd}'.\n")
    except ValueError:
        print("Los colores tienen que ser hex de 6 cifras, como ff66aa (con o sin #).")
        sys.exit(1)
    _lista()
    sys.exit(0)


_sel = os.environ.get("EDGE_PALETTE") or _tema_actual() or "rojoblanco"
if _sel not in _PALETAS and _sel not in ("lyne", "tema"):
    _sel = "rojoblanco"  # por ejemplo, si borraste la paleta que tenias elegida
_p = _PALETAS.get(_sel)
if _p:
    PINK, CYAN, VIO = (rgb(*x) for x in _p)  # PINK=acento 1, CYAN=acento 2, VIO=acento 3



_EMB_DIR = os.path.expanduser(f"~/.config/edgerunners/themes/{PRESET}")
def _elegir_emblema():
    exts = (".png", ".jpg", ".jpeg", ".webp", ".gif")
    fotos = []
    if PRESET and os.path.isdir(_EMB_DIR):
        fotos = sorted(f for f in os.listdir(_EMB_DIR) if f.lower().endswith(exts))
    if not fotos:
        suelta = os.path.expanduser(f"~/.config/edgerunners/themes/{PRESET}.png")
        if PRESET and os.path.exists(suelta):
            return suelta
        return os.path.expanduser("~/.config/edgerunners/image.png")
    fijo = os.environ.get("EDGE_EMBLEMA", "").strip()
    fijado = os.path.join(_EMB_DIR, "activo.txt")
    if not fijo and os.path.exists(fijado):
        fijo = open(fijado, encoding="utf-8").read().strip()
    if fijo in fotos:
        return os.path.join(_EMB_DIR, fijo)
    import random
    return os.path.join(_EMB_DIR, random.choice(fotos))
IMG = _elegir_emblema()
LOGO_X = 64
LOGO_W, LOGO_H = 34, 10
LOGO_Y = 3
C = 31             # ancho de la columna izquierda

w = shutil.get_terminal_size((100, 24)).columns

def gap(left, right):
    return " " * max(1, w - len(left) - len(right))

user = os.environ.get("USER", "user").upper()
distro = sh("grep ^PRETTY_NAME= /etc/os-release | cut -d= -f2 | tr -d '\"'")
desktop = os.environ.get("XDG_CURRENT_DESKTOP", "unknown")
shell = os.path.basename(os.environ.get("SHELL", "zsh")).upper()
term = "kitty" if os.environ.get("KITTY_WINDOW_ID") else os.environ.get("TERM", "?")
raw = sh("lspci | grep -iE 'vga|3d' | head -n1")
br = re.findall(r"\[(.*?)\]", raw)
gpu = br[-1] if br else raw.split(": ", 1)[-1]
if "GeForce" in gpu:
    gpu = "NVIDIA " + gpu

# pantalla limpia y el alien primero, con el cursor en 0,0
sys.stdout.write("\x1b[2J\x1b[H")
sys.stdout.flush()
if shutil.which("kitten") and os.path.exists(IMG):
    subprocess.run(["kitten", "icat", "--stdin=no", "--transfer-mode=memory",
                    "--place", f"{LOGO_W}x{LOGO_H}@{LOGO_X}x{LOGO_Y}", IMG])
sys.stdout.write("\x1b[H")
sys.stdout.flush()

txt = f"LOGIN: {user}"
print(f"{B}{PINK}EDGERUNNERS{R}{gap('EDGERUNNERS', '[ NC-2077 ]')}{GRAY}[ NC-2077 ]{R}")
print(f"{PINK}{'─' * w}{R}")
print(f"{PINK}{B}///////// UNAUTHORIZED ACCESS DETECTED{R}")
print(f"{B}{CYAN}\x1b]66;s=2;{txt}\x07{R}")
print()
print(f"{CYAN}{'─' * (len(txt) * 2)}{R}")
try:
    _fr = [l.strip() for l in open(os.path.expanduser("~/.config/edgerunners/frases.txt"), encoding="utf-8")
           if l.strip() and not l.startswith("#")]
except OSError:
    _fr = []
_fr = _fr or ["Wake up, choom. Time to raise hell. | x NO RULES. NO LIMITS. NO MERCY."]
_a, _, _b = random.choice(_fr).partition("|")
print(f"{WHITE}{_a.strip()}{R}")
print(f"{PINK}{_b.strip()}{R}" if _b.strip() else "")

print()

def row(l1, v1, l2, v2):
    print(f"{VIO}{l1:<{C}}{PINK}{l2}{R}")
    print(f"{WHITE}{v1:<{C}}{v2}{R}")

row("01 // DISTRO", distro, "04 // GPU", gpu)
row("02 // DESKTOP", desktop, "05 // TERMINAL", term)
def _online():
    try:
        for n in os.listdir("/sys/class/net"):
            if n == "lo" or n.startswith(("docker", "veth", "br-", "virbr")):
                continue
            if open(f"/sys/class/net/{n}/operstate").read().strip() == "up":
                return True
    except OSError:
        pass
    return False

def _bateria():
    try:
        for n in sorted(os.listdir("/sys/class/power_supply")):
            if n.startswith("BAT"):
                d = f"/sys/class/power_supply/{n}"
                pct = open(d + "/capacity").read().strip()
                cargando = open(d + "/status").read().strip() == "Charging"
                return f"BAT {pct}%" + (" (CHG)" if cargando else "")
    except OSError:
        pass
    return ""

_net = f"{CYAN}●{WHITE} ONLINE" if _online() else f"{PINK}●{WHITE} OFFLINE"
_bat = _bateria()
status = _net + (f"  {GRAY}|{WHITE}  {_bat}" if _bat else "")
row("03 // SHELL", shell, "06 // STATUS", status)

L, Rr = "| SYSTEM OVERRIDE |", "ACCESS GRANTED"
print(f"{CYAN}{'─' * w}{R}")
print(f"{PINK}{L}{R}{gap(L, Rr)}{B}{CYAN}{Rr}{R}")
