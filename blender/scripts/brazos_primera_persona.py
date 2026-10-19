r"""
Brazos de Elias en primera persona.

Construye los dos brazos low poly (camiseta de manga corta, antebrazos y manos
con dedos), un esqueleto listo para animar en Unity y cuatro texturas:

  estado 0  limpio      como los ve Elias bajo el efecto (y en los recuerdos)
  estado 1  noche 1     anos de consumo: marcas viejas en el codo
  estado 2  recaidas    marcas por todo el antebrazo, moretones, venas oscuras
  estado 3  consumido   venas quemadas, abscesos, marcas en las manos

El brazo izquierdo esta peor que el derecho: Elias es diestro y se inyecta
sobre todo en el izquierdo.

Un solo material y una sola textura (atlas 256x256: brazo derecho a la izquierda
del atlas, brazo izquierdo a la derecha). Para cambiar de estado en Unity basta
con cambiar la textura. La forma "consumido" (shape key) adelgaza los brazos.

Uso (PowerShell, desde la carpeta del proyecto):
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup `
      -P blender\scripts\brazos_primera_persona.py -- blender
  Solo algunos estados (mas rapido para probar): ... -- blender 1,3

Salidas (dentro de la carpeta blender/):
  textures/brazos_estado0..3.png   texturas de los cuatro estados
  scenes/brazos_primera_persona.blend
  renders/brazos_estado0..3.png    un render PS1 por estado (1920x1080)
  renders/brazos_estados.png       los cuatro estados juntos
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = os.path.abspath(ARGS[0]) if ARGS else os.getcwd()

TEX_DIR = os.path.join(ROOT, "textures")
SCENE_DIR = os.path.join(ROOT, "scenes")
RENDER_DIR = os.path.join(ROOT, "renders")

RES_X, RES_Y = 480, 270
UPSCALE = 4
COLOR_LEVELS = 32  # 15 bits de color, como la PS1

TEX = 256        # atlas cuadrado
HALF = 128       # ancho de la mitad de cada brazo
ARM_ROWS = 176   # filas del atlas para el tubo del brazo (hombro -> muneca)
HAND_ROW0 = 176  # filas 176..255 para la mano

rng = np.random.default_rng(7)
scene = bpy.context.scene
COL = None

# Posicion de los hombros respecto a la camara (la camara esta en el origen
# mirando hacia +Y). En reposo los brazos apuntan rectos hacia adelante, con
# los pulgares hacia arriba.
SHOULDER = Vector((0.17, -0.06, -0.24))

# ---------------------------------------------------------------------------
# Medidas del brazo (en metros, brazo derecho, eje del brazo = +Y local)
# ---------------------------------------------------------------------------
# En reposo la palma mira hacia adentro (-X), el pulgar hacia arriba (+Z).
# Anillos del tubo: (y, radio x, radio z, fila del atlas, zona)
Y_ELBOW, Y_WRIST = 0.30, 0.56
RINGS = [
    (0.000, 0.052, 0.058, 0.0, "manga"),
    (0.070, 0.050, 0.054, 22.0, "manga"),
    (0.140, 0.049, 0.052, 44.0, "manga"),
    (0.140, 0.040, 0.043, 48.0, "piel"),   # borde de la manga
    (0.200, 0.039, 0.041, None, "piel"),
    (0.265, 0.036, 0.036, None, "piel"),
    (0.300, 0.040, 0.034, None, "piel"),   # codo
    (0.335, 0.040, 0.036, None, "piel"),
    (0.380, 0.037, 0.034, None, "piel"),
    (0.430, 0.032, 0.030, None, "piel"),
    (0.480, 0.026, 0.027, None, "piel"),
    (0.530, 0.019, 0.026, None, "piel"),
    (0.560, 0.018, 0.027, None, "piel"),   # muneca
    (0.585, 0.016, 0.036, None, "mano"),
    (0.625, 0.014, 0.042, None, "mano"),
    (0.655, 0.012, 0.043, None, "mano"),   # nudillos
]
SIDES = 8

# Cuanto adelgaza cada anillo con la forma "consumido" (1 = nada).
# Los huesos (codo, muneca) casi no cambian; el musculo si.
def thin_factor(y, zone):
    if zone == "manga":
        return 1.0
    if zone == "mano":
        return 0.93
    bones = (Y_ELBOW, Y_WRIST)
    d = min(abs(y - b) for b in bones)
    return 0.74 + 0.19 * max(0.0, 1.0 - d / 0.06)


# Dedos: (nombre, z, y del nudillo, largos de las 3 falanges, medio ancho)
FINGERS = [
    ("index", 0.028, 0.652, (0.040, 0.024, 0.020), 0.0085),
    ("middle", 0.009, 0.656, (0.044, 0.028, 0.021), 0.0088),
    ("ring", -0.010, 0.652, (0.041, 0.026, 0.020), 0.0084),
    ("pinky", -0.028, 0.643, (0.032, 0.019, 0.018), 0.0074),
]
FINGER_X = 0.001
THUMB = [Vector((-0.002, 0.576, 0.013)), Vector((-0.018, 0.612, 0.036)),
         Vector((-0.024, 0.641, 0.043)), Vector((-0.027, 0.664, 0.046))]
THUMB_W = 0.0095

# Huesos del tubo, en orden, con su tramo en Y
ARM_BONES = [("upperarm", 0.0, Y_ELBOW), ("forearm", Y_ELBOW, 0.36),
             ("forearm_twist.01", 0.36, 0.46), ("forearm_twist.02", 0.46, Y_WRIST),
             ("hand", Y_WRIST, 0.655)]
# Pesos del tubo: entre estos puntos de control el peso pasa de un hueso al
# siguiente. La torsion del antebrazo se reparte en dos huesos para que el
# brazo no se "estrangule" al girar la palma.
WEIGHT_ANCHORS = [(0.26, "upperarm"), (0.34, "forearm"), (0.41, "forearm_twist.01"),
                  (0.51, "forearm_twist.02"), (0.555, "forearm_twist.02"), (0.585, "hand")]

# Proyeccion de la mano en el atlas (coordenadas del brazo derecho en reposo)
HAND_Y0, HAND_Y1 = 0.555, 0.755
HAND_Z0, HAND_Z1 = -0.050, 0.065


def ring_row(y):
    return y / Y_WRIST * (ARM_ROWS - 1)


def ventral_col(y):
    """Columna del atlas donde queda la cara interna del brazo (las venas).

    En reposo el pliegue del codo mira hacia arriba y la cara interna de la
    muneca hacia adentro: la linea gira 90 grados a lo largo del antebrazo.
    """
    if y <= Y_ELBOW:
        return 64.0
    t = min(1.0, (y - Y_ELBOW) / (Y_WRIST - Y_ELBOW))
    return 64.0 + 32.0 * t


def hand_rc(y, z, back):
    row = HAND_ROW0 + (y - HAND_Y0) / (HAND_Y1 - HAND_Y0) * 79.0
    col = (z - HAND_Z0) / (HAND_Z1 - HAND_Z0) * 63.0 + (64.0 if back else 0.0)
    return row, col


# ---------------------------------------------------------------------------
# Texturas (numpy, fila 0 = arriba del atlas)
# ---------------------------------------------------------------------------
def noise(h, w, cy, cx):
    """Ruido suave que se repite sin cortes."""
    g = rng.random((cy + 1, cx + 1))
    g[-1, :] = g[0, :]
    g[:, -1] = g[:, 0]
    ys = np.arange(h) * cy / h
    xs = np.arange(w) * cx / w
    y0, x0 = ys.astype(int), xs.astype(int)
    fy, fx = (ys - y0)[:, None], (xs - x0)[None, :]
    a, b = g[y0][:, x0], g[y0][:, x0 + 1]
    c, d = g[y0 + 1][:, x0], g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


class Painter:
    """Pinta sobre la mitad del atlas de un brazo (256 filas x 128 columnas)."""

    def __init__(self, img):
        self.img = img
        self.h, self.w = img.shape[:2]

    def blob(self, r, c, radius, color, alpha, wrap=True, hard=False):
        rr = int(math.ceil(radius)) + 1
        color = np.asarray(color)
        for dr in range(-rr, rr + 1):
            for dc in range(-rr, rr + 1):
                d = math.hypot(dr, dc)
                if d > radius + 0.5:
                    continue
                a = alpha if hard else alpha * max(0.0, 1.0 - (d / (radius + 0.5)) ** 2)
                y = int(round(r + dr))
                x = int(round(c + dc))
                if not 0 <= y < self.h:
                    continue
                if wrap and y < ARM_ROWS:
                    x %= HALF
                elif not 0 <= x < self.w:
                    continue
                self.img[y, x] = self.img[y, x] * (1 - a) + color * a

    def dot(self, r, c, color, alpha=1.0):
        self.blob(r, c, 0.0, color, alpha, hard=True)

    def line(self, pts, width, color, alpha, wobble=0.0):
        for (r0, c0), (r1, c1) in zip(pts[:-1], pts[1:]):
            n = int(max(abs(r1 - r0), abs(c1 - c0)) * 2) + 1
            for i in range(n + 1):
                t = i / n
                r = r0 + (r1 - r0) * t
                c = c0 + (c1 - c0) * t + wobble * math.sin(r * 0.45)
                self.blob(r, c, (width - 1.0) * 0.5, color, alpha, hard=width <= 1.0)


def vein_paths():
    """Venas en (y del brazo, desplazamiento en columnas desde la linea interna).

    Desplazamiento negativo = lado del pulgar (radial)."""
    return {
        "mediana_cubital": [(0.345, -13), (0.312, -3), (0.272, 9)],
        "cefalica": [(0.560, -14), (0.500, -16), (0.420, -17), (0.330, -15), (0.260, -18), (0.180, -22)],
        "basilica": [(0.560, 13), (0.480, 16), (0.400, 17), (0.300, 15), (0.240, 18)],
        "mediana_antebrazo": [(0.540, 1), (0.470, -1), (0.400, 2), (0.335, -2)],
    }


def to_rc(y, off):
    return ring_row(y), ventral_col(y) + off


def points_along(path, n, spread=1.2, y_range=None):
    """n puntos al azar sobre una vena (con un poco de desorden)."""
    segs = list(zip(path[:-1], path[1:]))
    out = []
    tries = 0
    while len(out) < n and tries < n * 50:
        tries += 1
        (y0, o0), (y1, o1) = segs[rng.integers(len(segs))]
        t = rng.random()
        y, o = y0 + (y1 - y0) * t, o0 + (o1 - o0) * t
        if y_range and not (y_range[0] <= y <= y_range[1]):
            continue
        r, c = to_rc(y, o)
        out.append((r + rng.normal(0, spread), c + rng.normal(0, spread)))
    return out


STATES = {
    # piel, manga, venas (color, alpha, ancho), marcas, moretones, abscesos, mugre
    0: dict(skin=(0.76, 0.56, 0.44), shirt=(0.86, 0.85, 0.80), shirt_dirt=0.05,
            vein=((0.47, 0.52, 0.60), 0.14, 1.0), marks=0, fresh=0, tracks=0.0,
            bruises=0, abscess=0, scars=0, hand_marks=0, grime=0.0, sweat=0.0,
            nail=(0.86, 0.66, 0.60), nail_dirt=0.0),
    1: dict(skin=(0.71, 0.55, 0.45), shirt=(0.70, 0.68, 0.62), shirt_dirt=0.25,
            vein=((0.40, 0.46, 0.55), 0.26, 1.0), marks=12, fresh=3, tracks=0.22,
            bruises=2, abscess=0, scars=1, hand_marks=0, grime=0.15, sweat=0.0,
            nail=(0.72, 0.58, 0.50), nail_dirt=0.35),
    2: dict(skin=(0.66, 0.55, 0.46), shirt=(0.62, 0.60, 0.53), shirt_dirt=0.4,
            vein=((0.36, 0.32, 0.45), 0.38, 1.0), marks=30, fresh=7, tracks=0.40,
            bruises=5, abscess=0, scars=3, hand_marks=2, grime=0.3, sweat=0.3,
            nail=(0.60, 0.50, 0.42), nail_dirt=0.55),
    3: dict(skin=(0.60, 0.55, 0.47), shirt=(0.52, 0.50, 0.43), shirt_dirt=0.6,
            vein=((0.20, 0.13, 0.19), 0.62, 2.0), marks=60, fresh=12, tracks=0.6,
            bruises=8, abscess=2, scars=5, hand_marks=9, grime=0.45, sweat=0.6,
            nail=(0.40, 0.32, 0.24), nail_dirt=0.8),
}


def paint_arm(img, state, k):
    """Pinta un brazo. k = intensidad (1 = brazo izquierdo, el mas castigado)."""
    s = STATES[state]
    p = Painter(img)
    h, w = img.shape[:2]
    skin = np.array(s["skin"])

    # Piel base con manchas suaves
    mott = 0.7 * noise(h, w, 8, 4) + 0.3 * noise(h, w, 24, 12)
    img[:] = skin * (0.94 + 0.12 * mott)[:, :, None]
    # La cara interna es mas clara que la externa
    for r in range(ARM_ROWS):
        y = r / (ARM_ROWS - 1) * Y_WRIST
        vc = ventral_col(y)
        d = np.abs(((np.arange(HALF) - vc + 64) % 128) - 64) / 64.0  # 0 interna, 1 externa
        img[r, :HALF] *= (1.05 - 0.10 * d)[:, None]
    # Codo (cara externa): piel mas aspera y oscura
    p.blob(ring_row(Y_ELBOW), 0, 5, skin * 0.82, 0.5)

    # Manga de la camiseta
    sh = np.array(s["shirt"])
    rows = 44
    dirt = noise(rows, HALF, 6, 6)
    img[:rows, :HALF] = sh * (1.0 - s["shirt_dirt"] * 0.5 * dirt)[:, :, None]
    for _ in range(int(s["shirt_dirt"] * 10)):
        p.blob(rng.uniform(4, rows - 4), rng.uniform(0, HALF), rng.uniform(2, 5),
               sh * 0.65 + np.array([0.06, 0.05, 0.0]), 0.35)
    img[rows - 2:rows, :HALF] *= 0.8                      # costura
    img[rows:rows + 4, :HALF] = np.array([0.10, 0.08, 0.07])  # sombra bajo la manga

    # Venas
    vcol, valpha, vwidth = s["vein"]
    for name, path in vein_paths().items():
        pts = [to_rc(y, o) for y, o in path]
        a = valpha * (0.8 if name == "mediana_antebrazo" else 1.0)
        p.line(pts, vwidth if k > 0.8 else max(1.0, vwidth - 1), vcol, a * (0.7 + 0.3 * k), wobble=0.8)

    # "Tracks": la piel endurecida sobre las venas mas usadas
    if s["tracks"] > 0:
        track = (0.42, 0.26, 0.24)
        for name in ("cefalica", "mediana_antebrazo"):
            path = vein_paths()[name]
            if state < 3:
                path = [q for q in path if q[0] >= 0.33]
            pts = [to_rc(y, o) for y, o in path]
            p.line(pts, 1.0 if state < 3 else 2.0, track, s["tracks"] * k, wobble=0.8)

    # Moretones: morados (recientes) y verde-amarillo (viejos)
    for i in range(int(round(s["bruises"] * k))):
        y = rng.uniform(0.27, 0.36) if i < 2 else rng.uniform(0.25, 0.52)
        r, c = to_rc(y, rng.uniform(-14, 14))
        old = rng.random() < 0.45
        col = (0.60, 0.58, 0.32) if old else (0.34, 0.22, 0.36)
        p.blob(r, c, rng.uniform(3.0, 6.0), col, 0.32 if old else 0.42)

    # El pliegue del codo, el sitio de siempre: piel manchada y amoratada
    if state > 0:
        r, c = to_rc(0.31, 0)
        p.blob(r, c, 6.0 + 2.0 * state, (0.50, 0.36, 0.34), 0.18 + 0.08 * state * k)
        p.blob(r + 2, c - 4, 3.5 + state, (0.40, 0.26, 0.36), 0.15 + 0.1 * state * k)

    # Cicatrices claras de abscesos viejos
    for _ in range(int(round(s["scars"] * k))):
        r, c = to_rc(rng.uniform(0.32, 0.50), rng.uniform(-12, 12))
        p.blob(r, c, rng.uniform(1.5, 2.5), (0.82, 0.70, 0.64), 0.5)
        p.dot(r, c, (0.62, 0.50, 0.46), 0.6)

    # Marcas de pinchazos: casi todas sobre el pliegue del codo; con los
    # estados avanzan por el antebrazo y llegan a la muneca.
    veins = vein_paths()
    n = int(round(s["marks"] * k))
    n_codo = n if state == 1 else int(n * 0.45)
    marks = points_along(veins["mediana_cubital"], n_codo, 2.6)
    rest = n - n_codo
    if rest > 0:
        lower = 0.32 if state == 2 else 0.25
        marks += points_along(veins["cefalica"], rest // 3, 1.0, (lower, 0.56 if state == 3 else 0.48))
        marks += points_along(veins["mediana_antebrazo"], rest // 3, 1.0)
        marks += points_along(veins["basilica"], rest - 2 * (rest // 3), 1.0, (lower, 0.52))
    n_fresh = int(round(s["fresh"] * k))
    for i, (r, c) in enumerate(marks):
        if i < n_fresh:  # recientes: punto rojo oscuro con un halo rosado
            p.blob(r, c, 1.4, (0.78, 0.42, 0.40), 0.35)
            p.dot(r, c, (0.36, 0.05, 0.04))
        else:            # viejas: costra cafe
            p.dot(r, c, (0.40, 0.25, 0.20), 0.85)

    # Abscesos: piel roja e hinchada, centro amarillento y costra
    spots = [(0.405, -7), (0.350, 11), (0.470, 4)]
    for y, off in spots[:int(round(s["abscess"] * k + 0.25))]:
        r, c = to_rc(y, off)
        p.blob(r, c, 5.5, (0.70, 0.26, 0.22), 0.55)
        p.blob(r, c, 3.0, (0.62, 0.18, 0.16), 0.6)
        p.blob(r, c, 1.6, (0.86, 0.76, 0.46), 0.9)
        p.dot(r, c, (0.22, 0.08, 0.05))
        p.dot(r + 1, c - 1, (0.30, 0.12, 0.07))

    # Mano: palma mas clara, dorso con nudillos, venas y unas
    hand = img[HAND_ROW0:, :]
    palm = hand[:, :64]
    palm[:] = palm * 1.06 + np.array([0.03, 0.0, 0.0])
    for f_name, z, yk, lens, fw in FINGERS:
        y_pip, y_dip = yk + lens[0], yk + lens[0] + lens[1]
        tip = y_dip + lens[2]
        for yy in (yk, y_pip, y_dip):        # pliegues en la palma
            r, c = hand_rc(yy, z, back=False)
            p.line([(r, c - 2), (r, c + 2)], 1.0, skin * 0.75, 0.5)
            r, c = hand_rc(yy, z, back=True)  # arrugas de los nudillos
            p.line([(r, c - 1), (r, c + 1)], 1.0, skin * 0.8, 0.45)
        # Una
        r0, c = hand_rc(tip - 0.013, z, back=True)
        r1, _ = hand_rc(tip - 0.002, z, back=True)
        nail = np.array(s["nail"])
        for rr in range(int(r0), int(r1) + 1):
            for cc in range(int(c) - 1, int(c) + 2):
                p.dot(rr, cc, nail)
        if s["nail_dirt"] > 0:
            for cc in range(int(c) - 1, int(c) + 2):
                p.dot(int(r1), cc, (0.18, 0.13, 0.08), s["nail_dirt"])
    # Una del pulgar
    tr0, tc = hand_rc(THUMB[3].y - 0.011, THUMB[3].z - 0.002, back=True)
    tr1, _ = hand_rc(THUMB[3].y - 0.001, THUMB[3].z, back=True)
    for rr in range(int(tr0), int(tr1) + 1):
        for cc in range(int(tc) - 1, int(tc) + 2):
            p.dot(rr, cc, np.array(s["nail"]))
    if s["nail_dirt"] > 0:
        for cc in range(int(tc) - 1, int(tc) + 2):
            p.dot(int(tr1), cc, (0.18, 0.13, 0.08), s["nail_dirt"])

    # Venas del dorso de la mano
    dv = [[(0.565, -0.005), (0.600, 0.000), (0.640, -0.010)],
          [(0.570, 0.020), (0.610, 0.012), (0.645, 0.018)],
          [(0.600, 0.000), (0.612, 0.012)]]
    for path in dv:
        pts = [hand_rc(y, z, back=True) for y, z in path]
        p.line(pts, 1.0, vcol, valpha * 0.8, wobble=0.0)
    # Cuando las venas del brazo ya no sirven, pasan a las manos
    n_hand = int(round(s["hand_marks"] * k))
    for i in range(n_hand):
        path = dv[i % 2]
        j = rng.integers(len(path) - 1)
        t = rng.random()
        y = path[j][0] + (path[j + 1][0] - path[j][0]) * t
        z = path[j][1] + (path[j + 1][1] - path[j][1]) * t
        r, c = hand_rc(y, z, back=True)
        if i < 2:
            p.blob(r, c, 2.5, (0.36, 0.24, 0.36), 0.35)
        p.dot(r + rng.normal(0, 0.7), c + rng.normal(0, 0.7), (0.38, 0.10, 0.07))

    # Mugre en manos y dedos
    if s["grime"] > 0:
        g = 0.6 * noise(80, HALF, 6, 8) + 0.4 * noise(80, HALF, 20, 24)
        hand *= (1.0 - s["grime"] * 0.45 * np.clip(g - 0.35, 0, 1))[:, :, None]
        img[: ARM_ROWS] *= (1.0 - s["grime"] * 0.12 * noise(ARM_ROWS, HALF, 10, 6))[:, :, None]


def build_texture(state):
    img = np.zeros((TEX, TEX, 3), dtype=np.float32)
    # Brazo derecho (Elias se inyecta con la mano derecha: este brazo sufre menos)
    paint_arm(img[:, :HALF], state, 0.55)
    # Brazo izquierdo
    paint_arm(img[:, HALF:], state, 1.0)
    return np.clip(img, 0, 1)


def save_texture(name, rgb_top_down):
    """Guarda el PNG (la fila 0 de numpy es arriba) y lo carga en Blender."""
    rgb = np.flipud(rgb_top_down)
    h, w, _ = rgb.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(rgb, 0.0, 1.0)
    path = os.path.join(TEX_DIR, name + ".png")
    tmp = bpy.data.images.new(name + "_tmp", w, h, alpha=False)
    tmp.pixels.foreach_set(rgba.ravel())
    tmp.filepath_raw = path
    tmp.file_format = "PNG"
    tmp.save()
    bpy.data.images.remove(tmp)
    img = bpy.data.images.load(path)
    img.name = name
    return img


# ---------------------------------------------------------------------------
# Malla
# ---------------------------------------------------------------------------
class ArmBuilder:
    """Construye un brazo (side = +1 derecho, -1 izquierdo) dentro de un bmesh."""

    def __init__(self, bm, uv_layer, deform, groups, thin, side):
        self.bm, self.uv, self.dl = bm, uv_layer, deform
        self.groups, self.thin = groups, thin
        self.side = side
        self.sfx = ".R" if side > 0 else ".L"
        self.u_off = 0.0 if side > 0 else HALF
        self.origin = Vector((SHOULDER.x * side, SHOULDER.y, SHOULDER.z))

    # -- utilidades -------------------------------------------------------
    def world(self, p):
        return Vector((p[0] * self.side, p[1], p[2])) + self.origin

    def vert(self, p, center, factor, weights):
        v = self.bm.verts.new(self.world(p))
        for g, wgt in weights.items():
            if wgt > 0:
                v[self.dl][self.groups[g + self.sfx]] = wgt
        c = self.world(center)
        self.thin[v] = c + (v.co - c) * factor
        return v

    def uv_atlas(self, row, col):
        return ((col + self.u_off) / TEX, 1.0 - row / TEX)

    def face(self, verts, uvs):
        if self.side < 0:
            verts, uvs = verts[::-1], uvs[::-1]
        f = self.bm.faces.new(verts)
        for loop, uv in zip(f.loops, uvs):
            loop[self.uv].uv = uv
        f.smooth = True
        return f

    def hand_uv(self, canon_pts, normal_x):
        back = normal_x >= 0.0
        out = []
        for p in canon_pts:
            r, c = hand_rc(p[1], p[2], back)
            out.append(self.uv_atlas(r, min(max(c, 0.5), 127.5)))
        return out

    # -- tubo del brazo ---------------------------------------------------
    def tube_weights(self, y):
        a = WEIGHT_ANCHORS
        if y <= a[0][0]:
            return {a[0][1]: 1.0}
        if y >= a[-1][0]:
            return {a[-1][1]: 1.0}
        for (y0, b0), (y1, b1) in zip(a[:-1], a[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / (y1 - y0)
                if b0 == b1:
                    return {b0: 1.0}
                return {b0: 1.0 - t, b1: t}
        return {"hand": 1.0}

    def build_tube(self):
        rings = []
        for y, rx, rz, row, zone in RINGS:
            ring = []
            for j in range(SIDES):
                a = -math.pi / 2 + 2 * math.pi * j / SIDES  # j=0 abajo, j=4 arriba
                p = (rx * math.cos(a), y, rz * math.sin(a))
                ring.append((p, self.vert(p, (0, y, 0), thin_factor(y, zone), self.tube_weights(y))))
            rings.append((y, row if row is not None else ring_row(y), zone, ring))

        for i in range(len(rings) - 1):
            y0, row0, _, r0 = rings[i]
            y1, row1, _, r1 = rings[i + 1]
            for j in range(SIDES):
                j1 = (j + 1) % SIDES
                quad = [r0[j], r1[j], r1[j1], r0[j1]]
                vs = [q[1] for q in quad]
                if y0 >= Y_WRIST - 1e-4:  # mano: proyeccion plana
                    pts = [q[0] for q in quad]
                    mean_x = sum(q[0] for q in pts) / 4.0  # > 0 = dorso
                    uvs = self.hand_uv(pts, mean_x)
                else:                     # brazo: proyeccion cilindrica
                    cu0 = j / SIDES * (HALF - 0.01)
                    cu1 = (j + 1) / SIDES * (HALF - 0.01)
                    uvs = [self.uv_atlas(row0, cu0), self.uv_atlas(row1, cu0),
                           self.uv_atlas(row1, cu1), self.uv_atlas(row0, cu1)]
                self.face(vs, uvs)
        # Tapa del hombro (mira hacia -Y) y de los nudillos (mira hacia +Y)
        first = rings[0][3]
        self.face([q[1] for q in first], [self.uv_atlas(2, 10 + j * 12) for j in range(SIDES)])
        last = rings[-1][3]
        pts = [q[0] for q in last][::-1]
        self.face([q[1] for q in last][::-1], self.hand_uv(pts, 1.0))

    # -- dedos ------------------------------------------------------------
    def finger_tube(self, joints, widths, bone_names, base_weight):
        """joints: centros de los anillos (coordenadas del brazo derecho).

        El anillo i (sin contar el primero ni la punta) se reparte 50/50 entre
        bone_names[i-1] y bone_names[i]; la punta va entera al ultimo hueso."""
        rings = []
        for i, (c, wdt) in enumerate(zip(joints, widths)):
            d = (joints[min(i + 1, len(joints) - 1)] - joints[max(i - 1, 0)]).normalized()
            ax = Vector((1, 0, 0))
            a = (ax - ax.dot(d) * d).normalized()
            b = a.cross(d)
            if i == 0:
                wts = base_weight
            elif i == len(joints) - 1:
                wts = {bone_names[-1]: 1.0}
            else:
                wts = {bone_names[i - 1]: 0.5, bone_names[i]: 0.5}
            r = wdt / math.cos(math.pi / 4)
            ring = []
            for j in range(4):
                ang = math.pi / 4 + j * math.pi / 2
                p = c + a * (r * math.cos(ang)) + b * (r * math.sin(ang))
                ring.append((tuple(p), self.vert(tuple(p), tuple(c), 0.9, wts)))
            rings.append(ring)
        for i in range(len(rings) - 1):
            for j in range(4):
                j1 = (j + 1) % 4
                quad = [rings[i][j], rings[i + 1][j], rings[i + 1][j1], rings[i][j1]]
                pts = [q[0] for q in quad]
                n = (Vector(pts[1]) - Vector(pts[0])).cross(Vector(pts[3]) - Vector(pts[0]))
                self.face([q[1] for q in quad], self.hand_uv(pts, n.x))
        tip = rings[-1][::-1]
        self.face([q[1] for q in tip], self.hand_uv([q[0] for q in tip], 1.0))
        base = rings[0]
        self.face([q[1] for q in base], self.hand_uv([q[0] for q in base], -1.0))

    def build_fingers(self):
        for name, z, yk, lens, fw in FINGERS:
            y = [yk - 0.012, yk, yk + lens[0], yk + lens[0] + lens[1], yk + sum(lens)]
            joints = [Vector((FINGER_X, yy, z)) for yy in y]
            widths = [fw, fw, fw * 0.93, fw * 0.85, fw * 0.72]
            # El nudillo queda entre la mano y la primera falange
            chain = ["hand", f"{name}.01", f"{name}.02", f"{name}.03"]
            self.finger_tube(joints, widths, chain, {"hand": 1.0})
        self.finger_tube(THUMB, [THUMB_W, THUMB_W, THUMB_W * 0.9, THUMB_W * 0.75],
                         ["thumb.01", "thumb.02", "thumb.03"], {"hand": 0.6, "thumb.01": 0.4})

    def build(self):
        self.build_tube()
        self.build_fingers()


def bone_layout(side):
    """Huesos en reposo: nombre -> (cabeza, cola, padre), en coordenadas del mundo."""
    s = side
    o = Vector((SHOULDER.x * s, SHOULDER.y, SHOULDER.z))

    def w(x, y, z):
        return Vector((x * s, y, z)) + o

    sfx = ".R" if side > 0 else ".L"
    out = {}
    parent = "root"
    for name, y0, y1 in ARM_BONES:
        out[name + sfx] = (w(0, y0, 0), w(0, y1, 0), parent)
        parent = name + sfx
    for name, z, yk, lens, fw in FINGERS:
        ys = [yk, yk + lens[0], yk + lens[0] + lens[1], yk + sum(lens)]
        par = "hand" + sfx
        for i in range(3):
            bn = f"{name}.0{i + 1}{sfx}"
            out[bn] = (w(FINGER_X, ys[i], z), w(FINGER_X, ys[i + 1], z), par)
            par = bn
    par = "hand" + sfx
    for i in range(3):
        bn = f"thumb.0{i + 1}{sfx}"
        a, b = THUMB[i], THUMB[i + 1]
        out[bn] = (w(a.x, a.y, a.z), w(b.x, b.y, b.z), par)
        par = bn
    return out


def all_bone_names():
    names = []
    for side in (1, -1):
        names += list(bone_layout(side).keys())
    return names


def build_arms(mat):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    dl = bm.verts.layers.deform.verify()
    names = all_bone_names()
    groups = {n: i for i, n in enumerate(names)}
    thin = {}
    for side in (1, -1):
        b = ArmBuilder(bm, uv, dl, groups, thin, side)
        b.build()

    me = bpy.data.meshes.new("Brazos")
    bm.verts.index_update()
    thin_co = [None] * len(bm.verts)
    for v in bm.verts:
        thin_co[v.index] = thin[v]
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)

    ob = bpy.data.objects.new("Brazos", me)
    COL.objects.link(ob)
    for n in names:
        ob.vertex_groups.new(name=n)

    # Forma "consumido": brazos mas delgados
    ob.shape_key_add(name="Basis", from_mix=False)
    sk = ob.shape_key_add(name="consumido", from_mix=False)
    for i, co in enumerate(thin_co):
        sk.data[i].co = co
    return ob


# ---------------------------------------------------------------------------
# Esqueleto
# ---------------------------------------------------------------------------
def build_rig():
    arm = bpy.data.armatures.new("Brazos_Rig")
    ob = bpy.data.objects.new("Brazos_Rig", arm)
    COL.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    root = eb.new("root")
    root.head, root.tail = (0, 0, 0), (0, 0.1, 0)
    for side in (1, -1):
        layout = bone_layout(side)
        for name, (head, tail, parent) in layout.items():
            b = eb.new(name)
            b.head, b.tail, b.roll = head, tail, 0.0
        for name, (head, tail, parent) in layout.items():
            b = eb[name]
            b.parent = eb[parent]
            b.use_connect = (eb[parent].tail - b.head).length < 1e-5
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in ob.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return ob


# ---------------------------------------------------------------------------
# Pose: Elias se mira los brazos con las palmas hacia arriba
# ---------------------------------------------------------------------------
def frame(y_axis, z_hint, pos):
    """Matriz con el eje Y del hueso en y_axis y el eje Z lo mas cerca de z_hint."""
    y = y_axis.normalized()
    z = (z_hint - z_hint.dot(y) * y).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = pos
    return m


def set_matrix(rig, name, m):
    pb = rig.pose.bones[name]
    pb.matrix = m
    bpy.context.view_layer.update()


def pose_inspect(rig, cam_pos):
    for side in (1, -1):
        sfx = ".R" if side > 0 else ".L"
        S = Vector((SHOULDER.x * side, SHOULDER.y, SHOULDER.z))
        lu = Y_ELBOW
        lf = Y_WRIST - Y_ELBOW
        # Brazos extendidos hacia adelante y abajo, codos apenas doblados:
        # la pose de quien muestra los brazos
        d_u = Vector((-0.06 * side, 0.55, -0.55)).normalized()
        E = S + d_u * lu
        d_f = Vector((-0.10 * side, 0.80, -0.30)).normalized()
        W = E + d_f * lf

        z_u = (d_f - d_f.dot(d_u) * d_u).normalized()    # cara anterior del brazo
        set_matrix(rig, "upperarm" + sfx, frame(d_u, z_u, S))
        x_u = d_u.cross(z_u)                              # eje del codo
        z_f = x_u.cross(d_f).normalized()                 # pliegue del codo
        set_matrix(rig, "forearm" + sfx, frame(d_f, z_f, E))

        # Mano: palma mirando a la camara, dedos siguiendo el antebrazo
        d_h = (d_f + Vector((0, 0.0, -0.18))).normalized()
        n_palm = (cam_pos - W).normalized() + Vector((0, 0, 0.4))
        x_h = -n_palm if side > 0 else n_palm             # eje X local = dorso (der.) / palma (izq.)
        y_h = d_h
        x_h = (x_h - x_h.dot(y_h) * y_h).normalized()
        z_h = x_h.cross(y_h)                              # direccion del pulgar

        # Torsion: cuanto hay que girar el antebrazo para llegar a la mano
        zp = (z_h - z_h.dot(d_f) * d_f).normalized()
        theta = math.atan2(z_f.cross(zp).dot(d_f), z_f.dot(zp))
        print(f"[pose] {sfx}: torsion del antebrazo {math.degrees(theta):.0f} grados")
        P1 = E + d_f * (0.36 - Y_ELBOW)
        P2 = E + d_f * (0.46 - Y_ELBOW)
        rot1 = Matrix.Rotation(theta * 0.5, 3, d_f)
        rot2 = Matrix.Rotation(theta, 3, d_f)
        set_matrix(rig, "forearm_twist.01" + sfx, frame(d_f, rot1 @ z_f, P1))
        set_matrix(rig, "forearm_twist.02" + sfx, frame(d_f, rot2 @ z_f, P2))
        set_matrix(rig, "hand" + sfx, frame(y_h, z_h, W))

        # Dedos relajados, un poco mas cerrados hacia el menique
        flex = {"index": (12, 20, 12), "middle": (16, 26, 14), "ring": (22, 30, 16),
                "pinky": (28, 32, 18), "thumb": (0, 12, 14)}
        for f, angs in flex.items():
            for i, a in enumerate(angs):
                pb = rig.pose.bones[f"{f}.0{i + 1}{sfx}"]
                pb.rotation_quaternion = Matrix.Rotation(math.radians(a) * side, 3, "Z").to_quaternion()
        bpy.context.view_layer.update()


# ---------------------------------------------------------------------------
# Materiales y escena (el piso del 4B, oscuro, para dar contexto)
# ---------------------------------------------------------------------------
def _new_material(name):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True  # en Blender 5 ya siempre usa nodos
    except Exception:
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return m, nt, out


def _set_input(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


def mat_surface(name, color=(0.5, 0.5, 0.5), image=None, rough=0.85, spec=0.3):
    m, nt, out = _new_material(name)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "BSDF"
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.name = "Textura"
        tex.image = image
        tex.interpolation = "Closest"  # pixeles duros, sin suavizado
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    _set_input(bsdf, ("Specular IOR Level", "Specular"), spec)
    return m


def tex_floor():
    """Tablas de madera gastada: 128 px = 2 m."""
    s = 128
    yy, xx = np.mgrid[0:s, 0:s]
    plank = xx // 10
    tone = rng.uniform(0.75, 1.15, plank.max() + 1)[plank]
    base = np.array([0.28, 0.17, 0.10]) * tone[:, :, None]
    grain = 0.85 + 0.15 * noise(s, s, 64, 13)
    rgb = base * grain[:, :, None]
    rgb[xx % 10 == 0] *= 0.35                        # junta entre tablas
    ends = (yy + (plank * 37) % 128) % 64 == 0         # cortes de las tablas
    rgb[ends] *= 0.45
    rgb *= (1.0 - 0.45 * (0.6 * noise(s, s, 4, 4) + 0.4 * noise(s, s, 16, 16)))[:, :, None]
    return rgb


def tex_wall():
    s = 64
    rgb = np.ones((s, s, 3)) * np.array([0.40, 0.39, 0.31])
    rgb *= (1.0 - 0.4 * (0.6 * noise(s, s, 3, 3) + 0.4 * noise(s, s, 9, 9)))[:, :, None]
    return rgb


def quad(name, corners, uvs, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    f = bm.faces.new([bm.verts.new(c) for c in corners])
    for loop, t in zip(f.loops, uvs):
        loop[uv].uv = t
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    COL.objects.link(ob)
    return ob


def box(name, mn, mx, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector([mn[i] + (v.co[i] + 0.5) * (mx[i] - mn[i]) for i in range(3)])
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    COL.objects.link(ob)
    return ob


def build_room():
    # El piso lo genera departamento_4b.py; si ya existe, se usa el mismo.
    floor_path = os.path.join(TEX_DIR, "piso_madera_4b.png")
    if os.path.exists(floor_path):
        floor_img = bpy.data.images.load(floor_path)
        floor_img.name = "piso_madera_4b"
    else:
        floor_img = save_texture("piso_madera_4b", tex_floor())
    wall_img = save_texture("pared_4b", tex_wall())
    piso = mat_surface("Piso4B", image=floor_img, rough=0.75, spec=0.25)
    pared = mat_surface("Pared4B", image=wall_img, rough=0.95)
    z = -1.62
    quad("Piso", [(-3, -1, z), (3, -1, z), (3, 3.2, z), (-3, 3.2, z)],
         [(0, 0), (3, 0), (3, 2.1), (0, 2.1)], piso)
    quad("Pared", [(-3, 3.2, z), (3, 3.2, z), (3, 3.2, 1.0), (-3, 3.2, 1.0)],
         [(0, 0), (6, 0), (6, 2.6), (0, 2.6)], pared)
    papel = mat_surface("Periodico", (0.50, 0.48, 0.42), rough=0.9)
    colchon = mat_surface("Colchon", (0.16, 0.14, 0.11), rough=0.95)
    vidrio = mat_surface("Botella", (0.06, 0.12, 0.05), rough=0.15, spec=0.6)
    box("Colchon", (-2.1, 0.6, z), (-1.0, 2.6, z + 0.16), colchon)
    p1 = box("Periodico1", (0.35, 1.05, z), (0.75, 1.35, z + 0.004), papel)
    p1.rotation_euler.z = math.radians(18)
    p2 = box("Periodico2", (-0.35, 1.7, z), (0.05, 2.0, z + 0.004), papel)
    p2.rotation_euler.z = math.radians(-31)
    box("Botella", (0.95, 1.45, z), (1.02, 1.71, z + 0.07), vidrio)  # tirada en el piso


def point_light(name, loc, color, power, radius=0.03):
    ld = bpy.data.lights.new(name, "POINT")
    ld.color, ld.energy = color, power
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    COL.objects.link(ob)
    return ob


LIGHTING = {
    # foco (color, W), relleno (color, W), fondo, niebla
    "efecto": dict(key_pos=(0.22, 0.80, 0.45), key=((1.0, 0.80, 0.52), 60.0),
                   fill=((1.0, 0.68, 0.42), 25.0),
                   bg=(0.035, 0.022, 0.012), fog=(0.95, 0.75, 0.50)),
    "abstinencia": dict(key_pos=(0.12, 0.50, 0.05), key=((1.0, 0.74, 0.48), 6.5),
                        fill=((0.50, 0.70, 0.72), 2.0),
                        bg=(0.004, 0.005, 0.007), fog=(0.70, 0.78, 0.72)),
}


def setup_world():
    w = bpy.data.worlds.new("Mundo")
    scene.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.name = "Fondo"
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.name = "Niebla"
    vol.inputs["Density"].default_value = 0.03
    vol.inputs["Anisotropy"].default_value = 0.3
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return w


def apply_lighting(mode, key, fill):
    L = LIGHTING[mode]
    key.location = L["key_pos"]
    key.data.color, key.data.energy = L["key"]
    fill.data.color, fill.data.energy = L["fill"]
    nt = scene.world.node_tree
    nt.nodes["Fondo"].inputs["Color"].default_value = (*L["bg"], 1.0)
    nt.nodes["Niebla"].inputs["Color"].default_value = (*L["fog"], 1.0)


def setup_camera():
    cd = bpy.data.cameras.new("Camara")
    cd.lens = 24
    cd.clip_start, cd.clip_end = 0.02, 30.0
    cam = bpy.data.objects.new("Camara", cd)
    COL.objects.link(cam)
    cam.location = (0, 0, 0)
    cam.rotation_euler = (math.radians(30), 0, 0)  # mirando hacia abajo, a los brazos
    scene.camera = cam
    return cam


def _try_set(obj, attr, value):
    if hasattr(obj, attr):
        try:
            setattr(obj, attr, value)
        except Exception as e:
            print(f"[aviso] {attr}: {e}")


def setup_render():
    r = scene.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = RES_X, RES_Y, 100
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.image_settings.color_depth = "8"
    _try_set(r, "filter_size", 0.6)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            r.engine = eng
            break
        except TypeError:
            continue
    ee = scene.eevee
    _try_set(ee, "taa_render_samples", 16)
    _try_set(ee, "volumetric_tile_size", "4")
    _try_set(ee, "volumetric_samples", 32)
    _try_set(ee, "volumetric_start", 0.05)
    _try_set(ee, "volumetric_end", 8.0)
    _try_set(ee, "use_volumetric_shadows", True)


# ---------------------------------------------------------------------------
# Post-proceso PS1
# ---------------------------------------------------------------------------
BAYER4 = np.array([[0, 8, 2, 10],
                   [12, 4, 14, 6],
                   [3, 11, 1, 9],
                   [15, 7, 13, 5]], dtype=np.float32) / 16.0 - 0.5 + 1.0 / 32.0


def ps1_quantize(src):
    """Devuelve el render cuantizado a 15 bits con dithering (fila 0 = abajo)."""
    img = bpy.data.images.load(src)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    rgb = px.reshape(h, w, 4)[:, :, :3]
    threshold = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w, None]
    levels = COLOR_LEVELS - 1
    return np.clip(np.floor(rgb * levels + 0.5 + threshold) / levels, 0.0, 1.0)


def save_png(rgb, path, scale):
    q = np.repeat(np.repeat(rgb, scale, axis=0), scale, axis=1)
    H, W = q.shape[:2]
    out = np.ones((H, W, 4), dtype=np.float32)
    out[:, :, :3] = q
    o = bpy.data.images.new("post", W, H, alpha=False)
    o.pixels.foreach_set(out.ravel())
    o.filepath_raw = path
    o.file_format = "PNG"
    o.save()
    bpy.data.images.remove(o)


# ---------------------------------------------------------------------------
def keyframe_pose(rig, action_name):
    rig.animation_data_create()
    for pb in rig.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=1)
        pb.keyframe_insert("location", frame=1)
    if rig.animation_data.action:
        rig.animation_data.action.name = action_name


def main():
    global COL
    for d in (TEX_DIR, SCENE_DIR, RENDER_DIR):
        os.makedirs(d, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    COL = bpy.data.collections.new("Brazos")
    scene.collection.children.link(COL)

    textures = {st: save_texture(f"brazos_estado{st}", build_texture(st)) for st in STATES}
    piel = mat_surface("Brazos", image=textures[1], rough=0.7, spec=0.3)

    rig = build_rig()
    arms = build_arms(piel)
    arms.parent = rig
    mod = arms.modifiers.new("Armature", "ARMATURE")
    mod.object = rig

    tris = sum(len(p.vertices) - 2 for p in arms.data.polygons)
    print(f"[info] brazos: {len(arms.data.vertices)} vertices, {tris} triangulos, "
          f"{len(rig.data.bones)} huesos")

    build_room()
    setup_world()
    cam = setup_camera()
    setup_render()
    key = point_light("Foco", (0.22, 0.80, 0.45), (1, 1, 1), 1.0)
    fill = point_light("Relleno", (-1.6, 1.4, -0.4), (1, 1, 1), 1.0, radius=0.4)

    pose_inspect(rig, cam.location)
    keyframe_pose(rig, "mirar_brazos")

    only = [int(a) for a in ARGS[1].split(",")] if len(ARGS) > 1 else list(STATES)
    bsdf = piel.node_tree.nodes["BSDF"]
    tex_node = piel.node_tree.nodes["Textura"]
    thin = arms.data.shape_keys.key_blocks["consumido"]
    # estado: (iluminacion, delgadez, rugosidad: mas sudor = mas brillo)
    looks = {0: ("efecto", 0.0, 0.72), 1: ("abstinencia", 0.0, 0.62),
             2: ("abstinencia", 0.45, 0.52), 3: ("abstinencia", 1.0, 0.40)}
    panels = {}
    for st in only:
        mode, thin_v, rough = looks[st]
        tex_node.image = textures[st]
        thin.value = thin_v
        bsdf.inputs["Roughness"].default_value = rough
        apply_lighting(mode, key, fill)
        raw = os.path.join(RENDER_DIR, f"brazos_estado{st}_raw.png")
        scene.render.filepath = raw
        bpy.ops.render.render(write_still=True)
        q = ps1_quantize(raw)
        save_png(q, os.path.join(RENDER_DIR, f"brazos_estado{st}.png"), UPSCALE)
        panels[st] = q
        os.remove(raw)

    if len(panels) == 4:
        # Hoja con los cuatro estados (arriba: 0 y 1, abajo: 2 y 3)
        top = np.concatenate([panels[0], panels[1]], axis=1)
        bottom = np.concatenate([panels[2], panels[3]], axis=1)
        sheet = np.concatenate([bottom, top], axis=0)  # fila 0 = abajo
        sheet[RES_Y - 1:RES_Y + 1, :] = 0.0
        sheet[:, RES_X - 1:RES_X + 1] = 0.0
        save_png(sheet, os.path.join(RENDER_DIR, "brazos_estados.png"), 2)

    # Deja la escena en el estado 1 (el de la Noche 1)
    tex_node.image = textures[1]
    thin.value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.62
    apply_lighting("abstinencia", key, fill)
    blend = os.path.join(SCENE_DIR, "brazos_primera_persona.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print(f"[aviso] rutas relativas: {e}")
    print("[info] listo")


main()
