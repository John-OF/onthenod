r"""
El departamento 4B: sala, cocina, pasillo, dormitorio y bano.
Es el refugio de Elias (Noche 1, Noche 5 y el final).

Construye el departamento low poly con codigo y lo renderiza con el mismo
post-proceso PS1 de la prueba de estilo (480x270, 15 bits con dithering Bayer,
escalado x4 sin suavizado).

Las dos versiones del mundo viven en la misma escena (documento, seccion 10):
  abstinencia  Estructura + Muebles + Deterioro, luz de noche
  efecto       se oculta Deterioro y se muestra Efecto, texturas limpias, luz calida

Plano (vista desde arriba, metros; la entrada esta abajo):

    y=7.4 +--------------+---------+
          |              |  BANO   |
          |  DORMITORIO  +--puerta-+
          |              d PASILLO |
    y=4.2 +--------------+  vano  -+-----------+
          |                        |           |
          |   SALA                 vano COCINA |
          |                        |           |
    y=0   +-----------entrada------+-----------+
         x=0           3.0-3.9    4.8         7.2

Uso (PowerShell, desde la carpeta del proyecto):
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup `
      -P blender\scripts\departamento_4b.py -- blender
  Solo algunas vistas (mas rapido para probar): ... -- blender sala,bano

Vistas: sala, sala_efecto, bano, entrada, cocina, dormitorio, dormitorio_efecto, dosis, plano
  (no van en la hoja: dormitorio_efecto, y dosis, la media con la droga que asoma bajo el colchon)

Salidas (dentro de la carpeta blender/):
  textures/*_4b*.png               texturas pixeladas (version sucia y limpia)
  scenes/departamento_4b.blend     la escena, para abrirla y retocarla
  renders/4b_<vista>.png           cada vista a 1920x1080 (el plano a 1080x1080)
  renders/4b_hoja.png              las seis vistas en perspectiva juntas

Y en el proyecto de Unity (ver exportar_unity.py), en el estado abstinencia:
  unity/Assets/Art/Departamento4B/departamento_4b.fbx          sin la coleccion Plano
  unity/Assets/Art/Departamento4B/departamento_4b_escena.json  luces, camaras y los dos estados
  unity/Assets/Art/Departamento4B/Textures/*.png               sucias y limpias
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exportar_unity  # noqa: E402

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = os.path.abspath(ARGS[0]) if ARGS else os.getcwd()
ONLY = ARGS[1].split(",") if len(ARGS) > 1 else None

TEX_DIR = os.path.join(ROOT, "textures")
SCENE_DIR = os.path.join(ROOT, "scenes")
RENDER_DIR = os.path.join(ROOT, "renders")

RES_X, RES_Y = 480, 270
UPSCALE = 4
COLOR_LEVELS = 32  # 15 bits de color, como la PS1

H = 2.6        # alto del techo (igual que el pasillo)
DOOR_H = 2.1   # alto de los vanos de puerta

R = math.radians
rng = np.random.default_rng(48)
scene = bpy.context.scene


# ---------------------------------------------------------------------------
# Texturas pixeladas (numpy -> PNG). Fila 0 = abajo.
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


def grime(h, w, amount=0.35):
    """Factor multiplicador de suciedad (1 = limpio)."""
    n = 0.6 * noise(h, w, 4, 4) + 0.3 * noise(h, w, 12, 12) + 0.1 * rng.random((h, w))
    return 1.0 - amount * n


def load_image(name):
    img = bpy.data.images.load(os.path.join(TEX_DIR, name + ".png"))
    img.name = name
    return img


def save_texture(name, rgb):
    h, w, _ = rgb.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(rgb, 0.0, 1.0)
    tmp = bpy.data.images.new(name + "_tmp", w, h, alpha=False)
    tmp.pixels.foreach_set(rgba.ravel())
    tmp.filepath_raw = os.path.join(TEX_DIR, name + ".png")
    tmp.file_format = "PNG"
    tmp.save()
    bpy.data.images.remove(tmp)
    return load_image(name)


def load_or_make(name, make):
    """Usa la textura si otro script ya la creo (la puerta del pasillo)."""
    if os.path.exists(os.path.join(TEX_DIR, name + ".png")):
        return load_image(name)
    return save_texture(name, make())


def tex_wallpaper(kind):
    """Papel tapiz de franjas con rombos. 256x166 px = 4 m x 2.6 m.
    kind: 'sucio', 'limpio' o 'marca' (lo que queda donde colgaba un cuadro)."""
    w, h = 256, 166
    yy, xx = np.mgrid[0:h, 0:w]
    z = (yy + 0.5) / h * H
    clean = np.array([[0.80, 0.66, 0.44], [0.66, 0.50, 0.32], [0.72, 0.36, 0.25]])
    dirty = np.array([[0.50, 0.46, 0.34], [0.38, 0.39, 0.29], [0.42, 0.28, 0.21]])
    base, stripe, motif = {"limpio": clean, "sucio": dirty, "marca": 0.55 * dirty + 0.45 * clean}[kind]
    rgb = np.empty((h, w, 3))
    rgb[:] = base
    rgb[(xx % 16) < 2] = stripe
    col = xx // 16
    dx = (xx % 16) - 9
    dy = ((yy + 12 * (col % 2)) % 24) - 12
    rgb[(np.abs(dx) + np.abs(dy) * 0.6) <= 2.6] = motif
    # zocalo de madera abajo y moldura bajo el techo
    rgb[z < 0.12] = (0.30, 0.17, 0.08) if kind == "limpio" else (0.17, 0.10, 0.06)
    rgb[(z >= 0.12) & (z < 0.145)] *= 0.6
    rgb[z > 2.53] = (0.82, 0.76, 0.62) if kind == "limpio" else (0.52, 0.50, 0.44)
    if kind != "sucio":
        return rgb * (0.92 + 0.08 * noise(h, w, 8, 8))[:, :, None]

    rgb *= grime(h, w, 0.35)[:, :, None]
    rgb *= (1.0 - 0.35 * np.clip(1.0 - z / 1.0, 0, 1))[:, :, None]  # mas sucio abajo
    # papel despegado: se ve el yeso, con el borde enrollado mas oscuro
    peel = 0.55 * noise(h, w, 9, 19) + 0.45 * noise(h, w, 23, 47)
    mask = (peel > 0.71) & (z > 0.25) & (z < 2.45)
    edge = (np.roll(mask, 1, axis=0) | np.roll(mask, -1, axis=1)) & ~mask
    rgb[mask] = np.array([0.47, 0.46, 0.41]) * (0.8 + 0.2 * rng.random((mask.sum(), 1)))
    rgb[edge] *= 0.5
    # manchas de humedad que bajan del techo, con aureola
    st = (0.65 * noise(h, w, 4, 9) + 0.35 * noise(h, w, 12, 25)) * np.clip(z / H + 0.25, 0, 1)
    rgb[st > 0.60] *= np.array([0.80, 0.72, 0.55])
    rgb[(st > 0.58) & (st <= 0.60)] *= np.array([0.62, 0.52, 0.38])
    # moho junto al piso y al techo
    mold = noise(h, w, 20, 40) * (0.6 + 0.4 * rng.random((h, w)))
    m = (mold > 0.62) & ((z < 0.45) | (z > 2.3))
    rgb[m] = rgb[m] * 0.35 + 0.65 * np.array([0.09, 0.11, 0.07])
    return rgb


def tex_wood(clean):
    """Tablas de madera: 128 px = 2 m (tablas de 12.5 cm)."""
    s = 128
    yy, xx = np.mgrid[0:s, 0:s]
    plank = xx // 8
    tone = rng.uniform(0.75, 1.15, plank.max() + 1)[plank]
    base = np.array([0.42, 0.24, 0.11] if clean else [0.28, 0.17, 0.10]) * tone[:, :, None]
    rgb = base * (0.85 + 0.15 * noise(s, s, 64, 16))[:, :, None]
    rgb[xx % 8 == 0] *= 0.35                           # junta entre tablas
    rgb[(yy + (plank * 37) % 128) % 64 == 0] *= 0.45   # cortes de las tablas
    if clean:
        return rgb * (0.93 + 0.07 * noise(s, s, 6, 6))[:, :, None]
    rgb *= (1.0 - 0.45 * (0.6 * noise(s, s, 4, 4) + 0.4 * noise(s, s, 16, 16)))[:, :, None]
    st = 0.6 * noise(s, s, 5, 5) + 0.4 * noise(s, s, 13, 13)
    rgb[st > 0.74] *= 0.55                             # liquidos derramados
    return rgb


def tex_ceiling(clean):
    s = 64  # 2 m
    rgb = np.ones((s, s, 3)) * np.array([0.80, 0.74, 0.62] if clean else [0.50, 0.48, 0.43])
    if clean:
        return rgb * (0.95 + 0.05 * noise(s, s, 6, 6))[:, :, None]
    rgb *= grime(s, s, 0.3)[:, :, None]
    st = 0.7 * noise(s, s, 4, 4) + 0.3 * noise(s, s, 11, 11)
    rgb[st > 0.66] *= np.array([0.78, 0.68, 0.50])
    rgb[(st > 0.64) & (st <= 0.66)] *= np.array([0.60, 0.50, 0.36])
    m = noise(s, s, 16, 16) > 0.8
    rgb[m] = rgb[m] * 0.5 + 0.5 * np.array([0.10, 0.11, 0.08])
    return rgb


def tex_kitchen_floor(clean):
    """Baldosas de terracota de 25 cm: 128 px = 2 m."""
    s, t = 128, 16
    yy, xx = np.mgrid[0:s, 0:s]
    tone = np.kron(rng.random((s // t, s // t)), np.ones((t, t)))
    rgb = np.array([0.55, 0.25, 0.12] if clean else [0.36, 0.16, 0.10]) * (0.82 + 0.18 * tone)[:, :, None]
    rgb[(xx % t == 0) | (yy % t == 0)] = (0.45, 0.42, 0.36) if clean else (0.15, 0.13, 0.10)
    if not clean:
        rgb *= grime(s, s, 0.5)[:, :, None]
    return rgb


def tex_paint(clean):
    """Pintura lisa (cocina y parte alta del bano): 64 px = 2 m."""
    s = 64
    rgb = np.ones((s, s, 3)) * np.array([0.82, 0.74, 0.52] if clean else [0.54, 0.53, 0.40])
    if clean:
        return rgb * (0.95 + 0.05 * noise(s, s, 6, 6))[:, :, None]
    rgb *= grime(s, s, 0.4)[:, :, None]
    st = 0.6 * noise(s, s, 4, 4) + 0.4 * noise(s, s, 10, 10)
    rgb[st > 0.68] *= np.array([0.75, 0.68, 0.50])
    return rgb


def tex_wall_tiles():
    """Azulejos de 12.5 cm: 64 px = 1 m."""
    s, t = 64, 8
    yy, xx = np.mgrid[0:s, 0:s]
    tone = np.kron(rng.random((s // t, s // t)), np.ones((t, t)))
    rgb = np.array([0.62, 0.68, 0.60]) * (0.9 + 0.1 * tone)[:, :, None]
    rgb[(xx % t == 0) | (yy % t == 0)] = (0.30, 0.30, 0.26)
    rgb *= grime(s, s, 0.4)[:, :, None]
    for _ in range(3):  # azulejos caidos: se ve el cemento
        i, j = rng.integers(0, s // t, 2)
        rgb[i * t + 1:(i + 1) * t, j * t + 1:(j + 1) * t] = \
            np.array([0.30, 0.29, 0.26]) * (0.8 + 0.2 * rng.random((t - 1, t - 1, 1)))
    for _ in range(4):  # grietas
        r, c = int(rng.integers(0, s)), int(rng.integers(0, s))
        for _k in range(int(rng.integers(6, 14))):
            rgb[r % s, c % s] *= 0.45
            r += int(rng.integers(-1, 2))
            c += 1
    return rgb


def tex_mosaic():
    """Piso del bano: teselas de 6 cm, 64 px = 1 m."""
    s, t = 64, 4
    yy, xx = np.mgrid[0:s, 0:s]
    tone = np.kron(rng.random((s // t, s // t)), np.ones((t, t)))
    rgb = np.array([0.64, 0.64, 0.60]) * (0.85 + 0.15 * tone)[:, :, None]
    dark = np.kron(rng.random((s // t, s // t)) > 0.92, np.ones((t, t))).astype(bool)
    rgb[dark] = (0.12, 0.14, 0.16)
    rgb[(xx % t == 0) | (yy % t == 0)] = (0.26, 0.25, 0.22)
    rgb *= grime(s, s, 0.45)[:, :, None]
    return rgb


def tex_entrance_door():
    """Igual que la puerta del pasillo (prueba_estilo_pasillo.py), por si aun no existe."""
    w, h = 64, 128
    yy, xx = np.mgrid[0:h, 0:w]
    rgb = np.array([0.30, 0.17, 0.09]) * (0.72 + 0.28 * noise(h, w, 3, 20))[:, :, None]

    def panel(x0, y0, x1, y1):
        inside = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        return inside & ((xx == x0) | (xx == x1) | (yy == y0) | (yy == y1))

    rgb = np.where((panel(10, 12, 53, 58) | panel(10, 68, 53, 116))[:, :, None], rgb * 0.5, rgb)
    return rgb * grime(h, w, 0.35)[:, :, None]


def tex_inner_door():
    """Puertas interiores pintadas, con la pintura saltada y mugre de manos."""
    w, h = 64, 128
    yy, xx = np.mgrid[0:h, 0:w]
    rgb = np.ones((h, w, 3)) * np.array([0.58, 0.56, 0.48])

    def frame(x0, y0, x1, y1):
        inside = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        return inside & ((xx <= x0 + 1) | (xx >= x1 - 1) | (yy <= y0 + 1) | (yy >= y1 - 1))

    rgb[frame(9, 10, 54, 56) | frame(9, 66, 54, 118)] *= 0.62
    rgb *= grime(h, w, 0.35)[:, :, None]
    chips = noise(h, w, 10, 5) * (0.7 + 0.3 * rng.random((h, w))) > 0.74
    rgb[chips] = (0.36, 0.32, 0.25)
    hand = np.exp(-(((xx - 7) / 7.0) ** 2 + ((yy - 62) / 14.0) ** 2))
    rgb *= (1 - 0.45 * hand)[:, :, None]
    rgb *= (1 - 0.3 * np.clip(1 - yy / 30.0, 0, 1))[:, :, None]
    return rgb


def tex_cardboard():
    s = 64  # 1 m
    yy, xx = np.mgrid[0:s, 0:s]
    rgb = np.ones((s, s, 3)) * np.array([0.46, 0.34, 0.20])
    rgb[xx % 3 == 0] *= 0.93  # corrugado
    rgb *= grime(s, s, 0.3)[:, :, None]
    for r in (8, 41):  # cinta de embalar
        rgb[r:r + 4, :] = np.array([0.60, 0.53, 0.36]) * (0.9 + 0.1 * rng.random((4, s, 1)))
    rgb[noise(s, s, 5, 5) > 0.72] *= 0.7  # humedad
    for _ in range(3):  # garabatos de plumon
        r, c = int(rng.integers(14, 36)), int(rng.integers(4, 40))
        for k in range(int(rng.integers(8, 18))):
            rgb[(r + int(round(2 * math.sin(k * 0.9)))) % s, (c + k) % s] = (0.08, 0.07, 0.06)
    return rgb


def tex_newspaper():
    s = 64  # 0.5 m
    yy, xx = np.mgrid[0:s, 0:s]
    rgb = np.ones((s, s, 3)) * np.array([0.64, 0.62, 0.55])
    words = noise(s, s, s, 12) > 0.35
    text = (yy % 3 == 0) & (xx % 16 > 1) & (xx % 16 < 15) & (yy < 50) & words
    rgb[text] *= 0.5
    rgb[(yy > 53) & (yy < 60) & (xx > 3) & (xx < 58)] = (0.16, 0.15, 0.14)  # titular
    photo = (yy > 28) & (yy < 49) & (xx > 33) & (xx < 61)
    rgb[photo] = (0.22 + 0.3 * noise(s, s, 6, 6)[photo])[:, None]
    rgb *= np.array([1.0, 0.97, 0.86]) * grime(s, s, 0.3)[:, :, None]
    return rgb


def tex_fabric(clean):
    """Tela del sofa, cuadrille pequeno: 64 px = 0.5 m."""
    s = 64
    yy, xx = np.mgrid[0:s, 0:s]
    a = np.array([0.62, 0.34, 0.14] if clean else [0.34, 0.24, 0.14])
    b = np.array([0.48, 0.22, 0.09] if clean else [0.24, 0.17, 0.10])
    rgb = np.where((((xx // 4) + (yy // 4)) % 2 == 0)[:, :, None], a, b)
    rgb *= (0.9 + 0.1 * noise(s, s, 16, 16))[:, :, None]
    if clean:
        return rgb
    rgb *= grime(s, s, 0.4)[:, :, None]
    rgb[(0.6 * noise(s, s, 4, 4) + 0.4 * noise(s, s, 9, 9)) > 0.7] *= 0.6
    for _ in range(5):  # quemaduras de cigarro
        r, c = rng.integers(1, s - 1, 2)
        rgb[r - 1:r + 2, c - 1:c + 2] *= 0.5
        rgb[r, c] = (0.02, 0.02, 0.02)
    return rgb


def tex_mattress():
    s = 64  # 1 m
    yy, xx = np.mgrid[0:s, 0:s]
    rgb = np.ones((s, s, 3)) * np.array([0.58, 0.56, 0.50])
    rgb[xx % 6 < 2] = (0.30, 0.34, 0.42)
    rgb *= grime(s, s, 0.3)[:, :, None]
    st = 0.6 * noise(s, s, 3, 3) + 0.4 * noise(s, s, 8, 8)
    rgb[st > 0.6] *= np.array([0.85, 0.72, 0.45])
    rgb[(st > 0.6) & (st < 0.62)] *= np.array([0.7, 0.6, 0.4])
    return rgb


def tex_calendar():
    """Calendario detenido hace ocho meses, con un dia marcado en rojo. 32x48 px."""
    w, h = 32, 48
    yy, xx = np.mgrid[0:h, 0:w]
    rgb = np.ones((h, w, 3)) * np.array([0.68, 0.66, 0.60])
    rgb[yy >= 26] = (0.42, 0.55, 0.62)                       # cielo
    rgb[(yy >= 26) & (yy < 33)] = (0.30, 0.42, 0.22)         # campo
    rgb[(yy >= 33) & (yy < 33 + 9 - np.abs(xx - 20) // 2)] = (0.36, 0.38, 0.42)  # cerro
    rgb[(yy >= 22) & (yy < 25) & (xx >= 3) & (xx < 29)] = (0.55, 0.10, 0.08)     # el mes
    gx, gy = 2, 1
    in_grid = (xx >= gx) & (xx <= gx + 28) & (yy >= gy) & (yy <= gy + 20)
    rgb[in_grid & (((xx - gx) % 4 == 0) | ((yy - gy) % 4 == 0))] = (0.35, 0.34, 0.32)
    cx, cy = gx + 4 * 4 + 2, gy + 4 * 2 + 2
    ring = np.abs(np.hypot(xx - cx, yy - cy) - 2.2) < 0.8
    rgb[ring] = (0.70, 0.06, 0.04)
    return rgb * grime(h, w, 0.25)[:, :, None]


def tex_photo():
    """La foto familiar (solo en la version 'efecto'). 40x30 px."""
    w, h = 40, 30
    yy, xx = np.mgrid[0:h, 0:w]
    t = (yy / h)[:, :, None]
    rgb = (1 - t) * np.array([0.45, 0.50, 0.30]) + t * np.array([0.80, 0.66, 0.46])
    # padre, madre, Elias (12) y Tomas (6), de izquierda a derecha
    for cx, top, half, color in ((8, 27, 5, (0.18, 0.20, 0.30)), (17, 25, 4, (0.55, 0.16, 0.15)),
                                 (26, 20, 4, (0.20, 0.32, 0.55)), (33, 15, 3, (0.70, 0.58, 0.20))):
        body = (yy < top - 5) & (np.abs(xx - cx) <= half - np.clip(yy - (top - 8), 0, 3))
        rgb[body] = color
        head = np.hypot(xx - cx, yy - (top - 3)) <= 2.6
        rgb[head] = (0.80, 0.60, 0.44)
        rgb[head & (yy >= top - 2)] = (0.12, 0.08, 0.06)  # pelo
    return rgb * 0.88 + 0.06


# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------
SWAPS = []  # (material, imagen sucia, imagen limpia): se cambian en la version 'efecto'


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


def mat_surface(name, color=(0.5, 0.5, 0.5), image=None, rough=0.85, metallic=0.0, spec=0.3):
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
    bsdf.inputs["Metallic"].default_value = metallic
    _set_input(bsdf, ("Specular IOR Level", "Specular"), spec)
    return m


def mat_emission(name, color, strength):
    m, nt, out = _new_material(name)
    em = nt.nodes.new("ShaderNodeEmission")
    em.name = "Emision"
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def build_materials():
    T = {
        "papel": save_texture("papel_tapiz_4b", tex_wallpaper("sucio")),
        "papel_l": save_texture("papel_tapiz_4b_limpio", tex_wallpaper("limpio")),
        "papel_marca": save_texture("papel_tapiz_4b_marca", tex_wallpaper("marca")),
        "madera": save_texture("piso_madera_4b", tex_wood(False)),
        "madera_l": save_texture("piso_madera_4b_limpio", tex_wood(True)),
        "techo": save_texture("techo_4b", tex_ceiling(False)),
        "techo_l": save_texture("techo_4b_limpio", tex_ceiling(True)),
        "baldosa": save_texture("baldosa_cocina_4b", tex_kitchen_floor(False)),
        "baldosa_l": save_texture("baldosa_cocina_4b_limpia", tex_kitchen_floor(True)),
        "pintura": save_texture("pintura_4b", tex_paint(False)),
        "pintura_l": save_texture("pintura_4b_limpia", tex_paint(True)),
        "azulejo": save_texture("azulejo_4b", tex_wall_tiles()),
        "mosaico": save_texture("mosaico_bano_4b", tex_mosaic()),
        "puerta": load_or_make("puerta_madera", tex_entrance_door),
        "puerta_int": save_texture("puerta_interior_4b", tex_inner_door()),
        "carton": save_texture("carton_4b", tex_cardboard()),
        "periodico": save_texture("periodico_4b", tex_newspaper()),
        "sofa": save_texture("tela_sofa_4b", tex_fabric(False)),
        "sofa_l": save_texture("tela_sofa_4b_limpia", tex_fabric(True)),
        "colchon": save_texture("colchon_4b", tex_mattress()),
        "calendario": save_texture("calendario_4b", tex_calendar()),
        "foto": save_texture("foto_familia_4b", tex_photo()),
    }
    S = mat_surface
    M = {
        # superficies con textura
        "papel": S("PapelTapiz", image=T["papel"], rough=0.9),
        "papel_marca": S("PapelTapizMarca", image=T["papel_marca"], rough=0.9),
        "madera": S("PisoMadera", image=T["madera"], rough=0.7, spec=0.3),
        "techo": S("Techo4B", image=T["techo"], rough=0.95),
        "baldosa": S("BaldosaCocina", image=T["baldosa"], rough=0.6, spec=0.4),
        "pintura": S("Pintura", image=T["pintura"], rough=0.85),
        "azulejo": S("Azulejo", image=T["azulejo"], rough=0.3, spec=0.5),
        "mosaico": S("MosaicoBano", image=T["mosaico"], rough=0.4, spec=0.4),
        "puerta": S("PuertaEntrada", image=T["puerta"], rough=0.7),
        "puerta_int": S("PuertaInterior", image=T["puerta_int"], rough=0.6),
        "carton": S("Carton", image=T["carton"], rough=0.95, spec=0.1),
        "periodico": S("Periodico", image=T["periodico"], rough=0.9),
        "sofa": S("TelaSofa", image=T["sofa"], rough=0.95, spec=0.1),
        "colchon": S("Colchon", image=T["colchon"], rough=0.95, spec=0.1),
        "calendario": S("Calendario", image=T["calendario"], rough=0.8),
        "foto": S("FotoFamilia", image=T["foto"], rough=0.3, spec=0.5),
        # colores lisos
        "marco": S("MarcoMadera", (0.12, 0.07, 0.04), rough=0.6),
        "marco_claro": S("MarcoPintado", (0.46, 0.44, 0.37), rough=0.7),
        "mueble": S("MaderaMueble", (0.20, 0.12, 0.07), rough=0.6),
        "mueble_cocina": S("MuebleCocina", (0.30, 0.34, 0.27), rough=0.6),
        "encimera": S("Encimera", (0.38, 0.37, 0.33), rough=0.5),
        "cinta": S("CintaAdhesiva", (0.62, 0.55, 0.36), rough=0.4),
        "laton": S("Laton", (0.36, 0.27, 0.11), rough=0.45, metallic=0.8),
        "metal": S("Acero", (0.45, 0.46, 0.47), rough=0.35, metallic=0.8),
        "metal_oscuro": S("MetalOscuro", (0.08, 0.09, 0.10), rough=0.5, metallic=0.3),
        "esmalte": S("Esmalte", (0.48, 0.46, 0.36), rough=0.4, spec=0.5),
        "porcelana": S("Porcelana", (0.60, 0.60, 0.55), rough=0.2, spec=0.6),
        "espejo": S("Espejo", (0.55, 0.56, 0.56), rough=0.05, metallic=1.0),
        "plastico_beige": S("PlasticoBeige", (0.55, 0.50, 0.40), rough=0.4),
        "plastico_negro": S("PlasticoNegro", (0.03, 0.03, 0.035), rough=0.4),
        "plastico_gris": S("PlasticoGris", (0.13, 0.13, 0.13), rough=0.45),
        "plastico_rojo": S("PlasticoRojo", (0.42, 0.08, 0.06), rough=0.5),
        "plastico_azul": S("PlasticoAzul", (0.10, 0.20, 0.34), rough=0.5),
        "pantalla": S("PantallaTV", (0.02, 0.025, 0.03), rough=0.1, spec=0.7),
        "vidrio": S("Vidrio", (0.30, 0.34, 0.32), rough=0.08, spec=0.8),
        "vidrio_verde": S("VidrioVerde", (0.05, 0.13, 0.05), rough=0.1, spec=0.7),
        "vidrio_ambar": S("VidrioAmbar", (0.22, 0.09, 0.02), rough=0.1, spec=0.7),
        "botella_agua": S("BotellaAgua", (0.42, 0.52, 0.58), rough=0.15, spec=0.6),
        "agua": S("Agua", (0.55, 0.66, 0.72), rough=0.1, spec=0.7),
        "jeringa": S("Jeringa", (0.78, 0.78, 0.74), rough=0.25, spec=0.5),
        "media": S("Media", (0.66, 0.64, 0.55), rough=0.95, spec=0.1),
        "media_franja": S("MediaFranja", (0.40, 0.08, 0.06), rough=0.95, spec=0.1),
        "cuero": S("Cuero", (0.10, 0.06, 0.04), rough=0.5),
        "bolsa": S("BolsaBasura", (0.02, 0.02, 0.025), rough=0.35, spec=0.5),
        "ropa_azul": S("RopaAzul", (0.12, 0.15, 0.22), rough=0.95, spec=0.1),
        "ropa_gris": S("RopaGris", (0.30, 0.29, 0.27), rough=0.95, spec=0.1),
        "ropa_roja": S("RopaRoja", (0.30, 0.07, 0.05), rough=0.95, spec=0.1),
        "manta": S("Manta", (0.20, 0.23, 0.16), rough=0.95, spec=0.1),
        "almohada": S("Almohada", (0.50, 0.47, 0.40), rough=0.95, spec=0.1),
        "toalla": S("Toalla", (0.36, 0.30, 0.22), rough=0.95, spec=0.1),
        "tapa_cuaderno": S("TapaCuaderno", (0.10, 0.14, 0.28), rough=0.6),
        "hoja": S("Hoja", (0.66, 0.64, 0.56), rough=0.9),
        "colilla": S("Colilla", (0.75, 0.66, 0.50), rough=0.9),
        "unicel": S("Unicel", (0.68, 0.67, 0.62), rough=0.9),
        "frasco": S("FrascoPastillas", (0.70, 0.33, 0.06), rough=0.3, spec=0.5),
        "tanque_gas": S("TanqueGas", (0.42, 0.12, 0.06), rough=0.6),
        "cortina_bano": S("CortinaBano", (0.38, 0.44, 0.42), rough=0.6),
        "negro": S("Negro", (0.0, 0.0, 0.0), rough=1.0, spec=0.0),
        "mancha": S("Mancha", (0.07, 0.035, 0.02), rough=0.6, spec=0.25),
        "numero": S("NumeroPuerta", (0.03, 0.025, 0.02), rough=0.6),
        # solo en la version 'efecto'
        "cortina": S("Cortina", (0.72, 0.42, 0.18), rough=0.9, spec=0.1),
        "alfombra": S("Alfombra", (0.46, 0.14, 0.08), rough=0.95, spec=0.1),
        "pantalla_lampara": S("PantallaLampara", (0.85, 0.68, 0.42), rough=0.9),
        # luces
        "led": mat_emission("LedRojo", (1.0, 0.08, 0.04), 8.0),
        "foco": mat_emission("Foco", (1.0, 0.72, 0.42), 10.0),
        "foco_apagado": S("FocoApagado", (0.30, 0.30, 0.28), rough=0.3),
        "fluor": mat_emission("TuboFluorescente", (0.8, 1.0, 0.88), 8.0),
        "etiqueta": mat_emission("EtiquetaPlano", (1.0, 0.95, 0.85), 1.5),
        "resplandor_calle": mat_emission("ResplandorCalle", (1.0, 0.45, 0.15), 1.2),
        "resplandor_patio": mat_emission("ResplandorPatio", (0.35, 0.45, 0.60), 0.6),
    }
    for key, dirty, clean in (("papel", "papel", "papel_l"), ("madera", "madera", "madera_l"),
                              ("techo", "techo", "techo_l"), ("baldosa", "baldosa", "baldosa_l"),
                              ("pintura", "pintura", "pintura_l"), ("sofa", "sofa", "sofa_l")):
        SWAPS.append((M[key], T[dirty], T[clean]))
    return M


# ---------------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------------
COLS = {}
CUR = [None]
BACKDROPS = []
CAMS = {}
LIGHTS = {}


def use(name):
    CUR[0] = COLS[name]


def link(ob):
    CUR[0].objects.link(ob)
    return ob


def wb(axis, n0, n1, u0, u1, z0, z1):
    """Caja de un muro: axis 'x' = el muro corre a lo largo de X (n es Y); 'y' = a lo largo de Y."""
    if axis == "x":
        return (u0, n0, z0), (u1, n1, z1)
    return (n0, u0, z0), (n1, u1, z1)


def box_uv(me, s, offset):
    """UV por proyeccion de caja en metros: s = tamano de la textura en (x, y, z)."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            c = loop.vert.co + offset
            if ax == 0:
                loop[uv].uv = (c.y / s[1], c.z / s[2])
            elif ax == 1:
                loop[uv].uv = (c.x / s[0], c.z / s[2])
            else:
                loop[uv].uv = (c.x / s[0], c.y / s[1])
    bm.to_mesh(me)
    bm.free()


def boxes_obj(name, boxes, mat, uv=(1, 1, 1), origin=(0, 0, 0), world_uv=True, rot=None, loc=None):
    """Un objeto hecho de varias cajas (esquinas en coordenadas de mundo).
    origin: punto que sera el origen del objeto (la bisagra de una puerta, por ejemplo).
    world_uv: la textura sigue el mundo (continua entre muros) o el objeto (puertas, carteles)."""
    o = Vector(origin)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for mn, mx in boxes:
        mn, mx = Vector(mn) - o, Vector(mx) - o
        c, s = (mn + mx) / 2, mx - mn
        bmesh.ops.create_cube(bm, size=1.0,
                              matrix=Matrix.Translation(c) @ Matrix.Diagonal((s.x, s.y, s.z, 1.0)))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    box_uv(me, uv, o if world_uv else Vector())
    ob = bpy.data.objects.new(name, me)
    ob.location = o if loc is None else Vector(loc)
    if rot:
        ob.rotation_euler = rot
    return link(ob)


def box(name, mn, mx, mat, uv=(1, 1, 1), pivot=None, world_uv=True, rot=None):
    if pivot is None:  # por defecto, el centro de la base
        pivot = ((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2])
    return boxes_obj(name, [(mn, mx)], mat, uv, pivot, world_uv, rot)


def mesh_obj(name, build, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), uv=(0.5, 0.5, 0.5)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    if uv:
        box_uv(me, uv, Vector())
    ob = bpy.data.objects.new(name, me)
    ob.location, ob.rotation_euler, ob.scale = loc, rot, scale
    return link(ob)


def cyl(name, loc, r, h, mat, rot=(0, 0, 0), seg=8, r2=None):
    """Cilindro (o cono si r2) con la base en loc, a lo largo de su Z local."""
    r2 = r if r2 is None else r2
    return mesh_obj(name, lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r2, depth=h,
        matrix=Matrix.Translation((0, 0, h / 2))), mat, loc, rot)


def blob(name, base, size, mat, rot=(0, 0, 0), flat=0.45, amp=0.3):
    """Bulto irregular apoyado en 'base' (bolsas de basura, ropa tirada, toallas)."""
    def build(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        for v in bm.verts:
            v.co *= 1.0 - amp / 2 + amp * rng.random()
            v.co.z = max(v.co.z, -flat)
    loc = (base[0], base[1], base[2] + flat * size[2])
    return mesh_obj(name, build, mat, loc, rot, size)


def empty(name, loc, rot=(0, 0, 0)):
    ob = link(bpy.data.objects.new(name, None))
    ob.location, ob.rotation_euler = loc, rot
    ob.empty_display_size = 0.1
    return ob


def parent(children, root):
    for c in children:
        c.parent = root
    return root


def group(name, origin, children):
    """Junta piezas sueltas (ubicadas en el mundo) bajo un vacio en origin, sin moverlas: para
    llevarlas juntas (un rastro que Elias recoge). El vacio no gira, asi que basta con restar."""
    root = empty(name, origin)
    for c in children:
        c.parent = root
        c.location = Vector(c.location) - Vector(origin)
    return root


def text_obj(name, body, size, mat, loc, rot=(0, 0, 0)):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    ob.location, ob.rotation_euler = loc, rot
    return link(ob)


def aim(ob, target):
    ob.rotation_euler = (Vector(target) - Vector(ob.location)).to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------------------
# Arquitectura
# ---------------------------------------------------------------------------
# (nombre, eje, n0, n1, u0, u1, vanos [(u0, u1, z0, z1)])
WALLS = [
    ("muro_sur", "x", -0.1, 0.0, -0.1, 7.3, [(3.0, 3.9, 0.0, DOOR_H)]),               # puerta de entrada
    ("muro_oeste", "y", -0.1, 0.0, 0.0, 7.4, [(1.3, 2.8, 0.9, 2.2), (5.3, 6.6, 0.9, 2.2)]),
    ("muro_este", "y", 7.2, 7.3, 0.0, 4.3, [(0.7, 1.9, 1.15, 2.1)]),
    ("muro_norte", "x", 7.4, 7.5, -0.1, 5.7, [(4.5, 5.1, 1.85, 2.3)]),
    ("muro_central", "x", 4.2, 4.3, 0.0, 7.2, [(3.5, 4.7, 0.0, 2.2)]),                # vano al pasillo
    ("tabique_cocina", "y", 4.8, 4.9, 0.0, 4.2, [(1.0, 2.6, 0.0, 2.2)]),             # vano a la cocina
    ("tabique_dormitorio", "y", 3.4, 3.5, 4.3, 7.4, [(4.5, 5.3, 0.0, DOOR_H)]),
    ("tabique_pasillo", "y", 4.7, 4.8, 4.3, 5.6, []),
    ("muro_bano", "x", 5.6, 5.7, 3.5, 5.7, [(3.72, 4.48, 0.0, DOOR_H)]),              # puerta del bano
    ("muro_bano_este", "y", 5.6, 5.7, 5.7, 7.4, []),
]


def wall_pieces(axis, n0, n1, u0, u1, openings=(), z0=0.0, z1=H):
    """Cajas de un muro con sus vanos (puertas y ventanas) recortados."""
    cuts = {u0, u1}
    for oa, ob, _, _ in openings:
        cuts.add(min(max(oa, u0), u1))
        cuts.add(min(max(ob, u0), u1))
    cuts = sorted(cuts)
    pieces = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 1e-4:
            continue
        mid = (a + b) / 2
        ranges = [(z0, z1)]
        for oa, ob, oz0, oz1 in openings:
            if not oa < mid < ob:
                continue
            nxt = []
            for r0, r1 in ranges:
                if oz1 <= r0 or oz0 >= r1:
                    nxt.append((r0, r1))
                    continue
                if oz0 > r0:
                    nxt.append((r0, oz0))
                if oz1 < r1:
                    nxt.append((oz1, r1))
            ranges = nxt
        pieces += [wb(axis, n0, n1, a, b, r0, r1) for r0, r1 in ranges if r1 - r0 > 1e-4]
    return pieces


def opening_frame(name, axis, n0, n1, a, b, z0, z1, mat, inside=1, sill=False, sash=False,
                  trim=0.06, d=0.015):
    """Marco de un vano: tapa el canto del muro y sobresale 'd' por las dos caras."""
    bx = []
    zb = z0 - trim if z0 > 0 else 0.0
    bx.append(wb(axis, n0 - d, n1 + d, a - trim, a + 0.01, zb, z1 + trim))
    bx.append(wb(axis, n0 - d, n1 + d, b - 0.01, b + trim, zb, z1 + trim))
    bx.append(wb(axis, n0 - d, n1 + d, a - trim, b + trim, z1 - 0.01, z1 + trim))
    if z0 > 0:
        bx.append(wb(axis, n0 - d, n1 + d, a - trim, b + trim, z0 - trim, z0 + 0.01))
    if sill:
        nn = (n1, n1 + 0.07) if inside > 0 else (n0 - 0.07, n0)
        bx.append(wb(axis, nn[0], nn[1], a - trim - 0.03, b + trim + 0.03, z0 - 0.035, z0 + 0.012))
    if sash:  # hojas de la ventana, sin vidrio
        nm, t, w = (n0 + n1) / 2, 0.015, 0.035
        um, zm = (a + b) / 2, z0 + (z1 - z0) * 0.62
        bx += [wb(axis, nm - t, nm + t, a, a + w, z0, z1),
               wb(axis, nm - t, nm + t, b - w, b, z0, z1),
               wb(axis, nm - t, nm + t, a, b, z0, z0 + w),
               wb(axis, nm - t, nm + t, a, b, z1 - w, z1),
               wb(axis, nm - t, nm + t, um - w / 2, um + w / 2, z0, z1),
               wb(axis, nm - t, nm + t, a, b, zm - w / 2, zm + w / 2)]
    return boxes_obj(name, bx, mat, uv=(0.5, 0.5, 0.5))


def door(name, mn, mx, hinge, mat, uv, hardware, ajar=0.0):
    """Hoja de puerta con origen en la bisagra (lista para animar). hardware: [(mn, mx, mat)]."""
    slab = box(name, mn, mx, mat, uv=uv, pivot=hinge, world_uv=False)
    inv = Matrix.Translation(Vector(hinge)).inverted()
    for i, (hmn, hmx, hmat) in enumerate(hardware):
        k = box(f"{name}_herraje_{i}", hmn, hmx, hmat)
        k.parent = slab
        k.matrix_parent_inverse = inv
    slab.rotation_euler.z = R(ajar)
    return slab


def hanging_bulb(name, x, y, M, mat=None, drop=0.36):
    """Foco colgando del techo. mat=None: solo el socket (no hay foco)."""
    box(name + "_roseta", (x - 0.06, y - 0.06, H - 0.03), (x + 0.06, y + 0.06, H), M["marco_claro"])
    box(name + "_cable", (x - 0.006, y - 0.006, H - drop + 0.05), (x + 0.006, y + 0.006, H - 0.03), M["negro"])
    box(name + "_socket", (x - 0.02, y - 0.02, H - drop), (x + 0.02, y + 0.02, H - drop + 0.06),
        M["plastico_negro"])
    if mat is not None:
        bulb(name, x, y, mat, drop)


def bulb(name, x, y, mat, drop=0.36):
    """La bombilla de un foco colgante (va con el socket de hanging_bulb)."""
    b = mesh_obj(name, lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.05), mat,
                 loc=(x, y, H - drop - 0.04))
    b.visible_shadow = False  # que no tape su propia luz
    return b


def architecture(M):
    use("Estructura")
    for name, axis, n0, n1, u0, u1, ops in WALLS:
        boxes_obj(name, wall_pieces(axis, n0, n1, u0, u1, ops), M["papel"], uv=(4.0, 4.0, H))

    boxes_obj("piso_madera", [((0, 0, -0.1), (4.8, 4.25, 0)),          # sala
                              ((0, 4.25, -0.1), (3.45, 7.4, 0)),       # dormitorio
                              ((3.45, 4.25, -0.1), (4.75, 5.65, 0))],  # pasillo
              M["madera"], uv=(2, 2, 2))
    boxes_obj("piso_cocina", [((4.8, 0, -0.1), (7.2, 4.2, 0))], M["baldosa"], uv=(2, 2, 2))
    boxes_obj("piso_bano", [((3.5, 5.65, -0.1), (5.6, 7.4, 0))], M["mosaico"], uv=(1, 1, 1))
    techo = boxes_obj("techo", [((-0.1, -0.1, H), (7.3, 7.5, H + 0.1))], M["techo"], uv=(2, 2, 2))

    # Revestimientos: la cocina va pintada con azulejos sobre la mesada;
    # el bano lleva azulejos hasta 1.60 m y pintura arriba.
    c = 0.006
    paint_k = (wall_pieces("y", 4.9, 4.9 + c, 0.0, 4.2, [(1.0, 2.6, 0.0, 2.2)])
               + wall_pieces("x", 4.2 - c, 4.2, 4.9, 7.2)
               + wall_pieces("y", 7.2 - c, 7.2, 0.0, 4.2, [(0.7, 1.9, 1.15, 2.1)])
               + wall_pieces("x", 0.0, c, 4.9, 7.2))
    tiles_k = wall_pieces("y", 7.2 - 2 * c, 7.2 - c, 0.1, 2.6, [(0.7, 1.9, 1.15, 2.1)], 0.88, 1.5)
    paint_b, tiles_b = [], []
    for axis, n0, n1, u0, u1, ops in (("y", 3.5, 3.5 + c, 5.7, 7.4, []),
                                      ("y", 5.6 - c, 5.6, 5.7, 7.4, []),
                                      ("x", 7.4 - c, 7.4, 3.5, 5.6, [(4.5, 5.1, 1.85, 2.3)]),
                                      ("x", 5.7, 5.7 + c, 3.5, 5.6, [(3.72, 4.48, 0.0, DOOR_H)])):
        tiles_b += wall_pieces(axis, n0, n1, u0, u1, ops, 0.0, 1.6)
        paint_b += wall_pieces(axis, n0, n1, u0, u1, ops, 1.6, H)
    boxes_obj("pintura_cocina", paint_k, M["pintura"], uv=(2, 2, 2))
    boxes_obj("azulejos_cocina", tiles_k, M["azulejo"], uv=(1, 1, 1))
    boxes_obj("pintura_bano", paint_b, M["pintura"], uv=(2, 2, 2))
    boxes_obj("azulejos_bano", tiles_b, M["azulejo"], uv=(1, 1, 1))

    # Marcos de puertas, vanos y ventanas
    opening_frame("marco_entrada", "x", -0.1, 0.0, 3.0, 3.9, 0.0, DOOR_H, M["marco"])
    opening_frame("marco_bano", "x", 5.6, 5.7, 3.72, 4.48, 0.0, DOOR_H, M["marco_claro"])
    opening_frame("marco_dormitorio", "y", 3.4, 3.5, 4.5, 5.3, 0.0, DOOR_H, M["marco_claro"])
    opening_frame("marco_pasillo", "x", 4.2, 4.3, 3.5, 4.7, 0.0, 2.2, M["marco_claro"])
    opening_frame("marco_cocina", "y", 4.8, 4.9, 1.0, 2.6, 0.0, 2.2, M["marco_claro"])
    opening_frame("ventana_sala", "y", -0.1, 0.0, 1.3, 2.8, 0.9, 2.2, M["marco"], 1, True, True)
    opening_frame("ventana_dormitorio", "y", -0.1, 0.0, 5.3, 6.6, 0.9, 2.2, M["marco"], 1, True, True)
    opening_frame("ventana_cocina", "y", 7.2, 7.3, 0.7, 1.9, 1.15, 2.1, M["marco"], -1, True, True)
    opening_frame("ventana_bano", "x", 7.4, 7.5, 4.5, 5.1, 1.85, 2.3, M["marco"], -1, False, True)

    # Puerta de entrada (abre hacia adentro): cerrojos, cadena puesta y mirilla
    L = M["laton"]
    entrada = door("puerta_entrada", (3.01, -0.04, 0.03), (3.89, 0.0, 2.09), (3.01, 0.0, 0.0), M["puerta"],
         (0.88, 0.88, 2.09), [
             ((3.78, 0.0, 0.98), (3.84, 0.05, 1.04), L),             # manija
             ((3.78, -0.09, 0.98), (3.84, -0.04, 1.04), L),
             ((3.76, 0.0, 1.20), (3.84, 0.022, 1.25), L),            # cerrojos
             ((3.76, 0.0, 1.36), (3.84, 0.022, 1.41), L),
             ((3.60, 0.0, 1.90), (3.80, 0.018, 1.93), M["metal"]),   # pasador
             ((3.70, 0.0, 1.62), (3.82, 0.012, 1.645), L),           # riel de la cadena
             ((3.43, 0.0, 1.535), (3.47, 0.012, 1.575), L),          # mirilla
             # Del lado del pasillo (Noche 2): la placa con el numero y el lente de la mirilla
             ((3.36, -0.048, 1.64), (3.54, -0.04, 1.76), L),         # placa
             ((3.43, -0.052, 1.535), (3.47, -0.04, 1.575), L),       # mirilla, por fuera
         ])
    numero = text_obj("puerta_entrada_numero", "4B", 0.075, M["numero"], (3.45, -0.0485, 1.70), (R(90), 0, 0))
    numero.parent = entrada
    numero.matrix_parent_inverse = Matrix.Translation((3.01, 0.0, 0.0)).inverted()
    for i, (x, z) in enumerate(((3.925, 1.618), (3.90, 1.604), (3.875, 1.598), (3.85, 1.603), (3.825, 1.615))):
        box(f"cadena_{i}", (x - 0.012, 0.012, z - 0.006), (x + 0.012, 0.018, z + 0.006), M["metal"])

    # Bano: la puerta abre hacia el pasillo, por eso la silla la puede trabar
    P = M["puerta_int"]
    door("puerta_bano", (3.73, 5.60, 0.03), (4.47, 5.64, 2.09), (4.47, 5.60, 0.0), P, (0.74, 0.74, 2.09), [
        ((3.80, 5.55, 0.98), (3.86, 5.60, 1.04), L),
        ((3.80, 5.64, 0.98), (3.86, 5.69, 1.04), L),
    ])
    # Dormitorio: entreabierta hacia adentro
    door("puerta_dormitorio", (3.40, 4.51, 0.03), (3.44, 5.29, 2.09), (3.40, 5.29, 0.0), P, (0.78, 0.78, 2.09), [
        ((3.44, 4.57, 0.98), (3.49, 4.63, 1.04), L),
        ((3.35, 4.57, 0.98), (3.40, 4.63, 1.04), L),
    ], ajar=-28)
    return techo


# ---------------------------------------------------------------------------
# Objetos chicos (jeringas, botellas, sillas...)
# ---------------------------------------------------------------------------
def syringe(name, loc, yaw, M):
    """Jeringa usada, tirada (sin tapa)."""
    root = empty(name, (loc[0], loc[1], loc[2] + 0.0065), (0, R(90), yaw))
    return parent([
        cyl(name + "_cuerpo", (0, 0, 0), 0.0065, 0.08, M["jeringa"], seg=6),
        box(name + "_embolo", (-0.002, -0.002, 0.08), (0.002, 0.002, 0.115), M["jeringa"]),
        cyl(name + "_tope", (0, 0, 0.115), 0.009, 0.003, M["jeringa"], seg=6),
        cyl(name + "_pico", (0, 0, -0.008), 0.003, 0.008, M["jeringa"], seg=5),
        cyl(name + "_aguja", (0, 0, -0.024), 0.0008, 0.016, M["metal"], seg=4),
    ], root)


def bottle(name, base, mat, h=0.24, r=0.035, lying=False, yaw=0.0):
    if lying:
        root = empty(name, (base[0], base[1], base[2] + r), (R(90), 0, yaw))
    else:
        root = empty(name, base, (0, 0, yaw))
    return parent([
        cyl(name + "_cuerpo", (0, 0, 0), r, h * 0.66, mat),
        cyl(name + "_hombro", (0, 0, h * 0.66), r, h * 0.12, mat, r2=r * 0.35),
        cyl(name + "_cuello", (0, 0, h * 0.78), r * 0.35, h * 0.22, mat, seg=6),
    ], root)


def chair(name, loc, rot, M, pivot=(0, 0, 0)):
    """Silla de madera. Mira hacia -Y; el respaldo queda en +Y."""
    bx = [((-0.2, -0.2, 0.43), (0.2, 0.2, 0.47))]
    bx += [((x - 0.015, y - 0.015, 0.0), (x + 0.015, y + 0.015, 0.43)) for x in (-0.175, 0.175) for y in (-0.175, 0.175)]
    bx += [((-0.2, 0.16, 0.47), (-0.16, 0.2, 0.95)), ((0.16, 0.16, 0.47), (0.2, 0.2, 0.95)),
           ((-0.16, 0.165, 0.70), (0.16, 0.195, 0.76)), ((-0.16, 0.165, 0.86), (0.16, 0.195, 0.93))]
    return boxes_obj(name, bx, M["mueble"], origin=pivot, world_uv=False, rot=rot, loc=loc)


def table_legs(x0, x1, y0, y1, z, t=0.04):
    return [((x, y, 0.0), (x + t, y + t, z)) for x in (x0, x1 - t) for y in (y0, y1 - t)]


def panel(name, axis, face, inside, depth, u0, u1, z0, z1, mat, angle=0.0, thick=0.008):
    """Lamina pegada a un muro (carton, periodico, cinta). angle: giro en el plano del muro."""
    n0 = face + inside * depth
    n1 = n0 + inside * thick
    mn, mx = wb(axis, min(n0, n1), max(n0, n1), u0, u1, z0, z1)
    pivot = tuple((mn[i] + mx[i]) / 2 for i in range(3))
    rot = (R(angle), 0, 0) if axis == "y" else (0, R(angle), 0)
    uv = (0.5, 0.5, 0.5) if mat.name.startswith("Periodico") else (1, 1, 1)
    return box(name, mn, mx, mat, uv=uv, pivot=pivot, rot=rot)


def cover_window(prefix, axis, face, inside, pieces, M):
    for i, (kind, u0, u1, z0, z1, angle, depth) in enumerate(pieces):
        panel(f"{prefix}_{kind}_{i}", axis, face, inside, depth, u0, u1, z0, z1, M[kind], angle)


def curtain(name, axis, face, inside, u0, u1, z0, z1, mat, pleats=5, depth=0.06):
    """Cortina con pliegues (zigzag)."""
    def build(bm):
        cols = pleats * 2 + 1
        bot, top = [], []
        for i in range(cols):
            u = u0 + (u1 - u0) * i / (cols - 1)
            n = face + inside * (depth + (0.035 if i % 2 else 0.0))
            p0, p1 = wb(axis, n, n, u, u, z0, z1)
            bot.append(bm.verts.new(p0))
            top.append(bm.verts.new(p1))
        for i in range(cols - 1):
            bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    return mesh_obj(name, build, mat, uv=(1, 1, 1))


def floor_lamp(name, loc, rot, M):
    root = empty(name, loc, rot)
    shade = cyl(name + "_pantalla", (0, 0, 1.30), 0.21, 0.26, M["pantalla_lampara"], r2=0.13)
    shade.visible_shadow = False
    return parent([
        cyl(name + "_base", (0, 0, 0), 0.13, 0.03, M["metal_oscuro"]),
        cyl(name + "_poste", (0, 0, 0.03), 0.012, 1.30, M["metal_oscuro"], seg=6),
        shade,
    ], root)


def newspaper_floor(name, x, y, yaw, M):
    return box(name, (x - 0.19, y - 0.14, 0.0), (x + 0.19, y + 0.14, 0.004), M["periodico"],
               uv=(0.5, 0.5, 0.5), world_uv=False, rot=(0, 0, R(yaw)))


def floor_stain(name, x, y, r, M, z=0.0015):
    def build(bm):
        verts = []
        for i in range(12):
            a = 2 * math.pi * i / 12
            rr = r * (0.6 + 0.6 * rng.random())
            verts.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr * 1.3, 0)))
        bm.faces.new(verts)
    return mesh_obj(name, build, M["mancha"], loc=(x, y, z))


# ---------------------------------------------------------------------------
# Cuartos
# ---------------------------------------------------------------------------
def sala(M):
    use("Muebles")
    # Sofa contra la pared del fondo, mirando a la entrada (aqui aparece Tomas vivo)
    boxes_obj("sofa", [((0.5, 3.38, 0.08), (2.6, 4.16, 0.42)),
                       ((0.5, 3.93, 0.42), (2.6, 4.16, 0.88)),
                       ((0.5, 3.38, 0.42), (0.7, 4.16, 0.64)),
                       ((2.4, 3.38, 0.42), (2.6, 4.16, 0.64))], M["sofa"], uv=(0.5, 0.5, 0.5))
    boxes_obj("sofa_patas", [((x, y, 0), (x + 0.05, y + 0.05, 0.08)) for x in (0.55, 2.5) for y in (3.42, 4.06)],
              M["mueble"])
    box("cojin_asiento_1", (0.71, 3.40, 0.42), (1.54, 3.93, 0.54), M["sofa"], uv=(0.5, 0.5, 0.5))
    box("cojin_asiento_2", (1.56, 3.40, 0.42), (2.39, 3.93, 0.52), M["sofa"], uv=(0.5, 0.5, 0.5))

    def back_cushion(name, x0, x1):
        return box(name, (x0, 3.78, 0.53), (x1, 3.94, 0.86), M["sofa"], uv=(0.5, 0.5, 0.5),
                   pivot=((x0 + x1) / 2, 3.94, 0.53), rot=(R(-10), 0, 0))

    back_cushion("cojin_respaldo_1", 0.72, 1.54)

    # Mesita con el telefono y la contestadora
    boxes_obj("mesita_telefono", [((2.72, 3.68, 0.58), (3.24, 4.16, 0.62)), ((2.74, 3.70, 0.16), (3.22, 4.14, 0.18))]
              + table_legs(2.74, 3.22, 3.70, 4.14, 0.58, 0.03), M["mueble"])
    boxes_obj("telefono", [((2.78, 3.80, 0.62), (2.98, 4.02, 0.67)), ((2.80, 3.84, 0.67), (2.96, 4.00, 0.695))],
              M["plastico_beige"])
    boxes_obj("telefono_auricular", [((2.79, 3.865, 0.695), (2.97, 3.905, 0.722)),
                                     ((2.78, 3.845, 0.69), (2.83, 3.925, 0.735)),
                                     ((2.93, 3.845, 0.69), (2.98, 3.925, 0.735))], M["plastico_beige"])
    box("contestadora", (3.02, 3.76, 0.62), (3.22, 4.06, 0.665), M["plastico_negro"])
    box("contestadora_cinta", (3.07, 3.87, 0.665), (3.18, 3.98, 0.668), M["plastico_gris"])
    box("contestadora_luz", (3.04, 3.775, 0.665), (3.075, 3.80, 0.669), M["led"])

    # Mesa de centro y el cuaderno de Elias (aqui se guarda la partida)
    boxes_obj("mesa_centro", [((0.95, 2.45, 0.38), (2.15, 2.95, 0.42))] + table_legs(0.97, 2.13, 2.47, 2.93, 0.38),
              M["mueble"])
    box("cuaderno", (1.06, 2.56, 0.42), (1.28, 2.86, 0.435), M["tapa_cuaderno"], rot=(0, 0, R(8)))
    cyl("pluma", (1.31, 2.60, 0.424), 0.004, 0.14, M["plastico_azul"], rot=(R(90), 0, R(-15)), seg=5)

    # Tele vieja frente al sofa
    boxes_obj("mueble_tv", [((0.85, 0.02, 0.0), (1.85, 0.47, 0.46))], M["mueble"])
    box("tele", (1.03, 0.05, 0.46), (1.67, 0.50, 0.96), M["plastico_gris"])
    box("tele_pantalla", (1.08, 0.50, 0.53), (1.56, 0.506, 0.91), M["pantalla"])
    box("tele_controles", (1.58, 0.50, 0.55), (1.64, 0.504, 0.90), M["plastico_negro"])
    box("antena_base", (1.30, 0.20, 0.96), (1.40, 0.30, 0.99), M["plastico_negro"])
    box("antena_1", (1.345, 0.245, 0.99), (1.355, 0.255, 1.42), M["metal"], rot=(R(-8), R(-30), 0))
    box("antena_2", (1.345, 0.245, 0.99), (1.355, 0.255, 1.42), M["metal"], rot=(R(10), R(24), 0))

    # Mesa del comedor: falta una de las dos sillas (esta trabando la puerta del bano)
    boxes_obj("mesa_comedor", [((4.0, 2.85, 0.74), (4.72, 3.55, 0.78))] + table_legs(4.02, 4.70, 2.87, 3.53, 0.74),
              M["mueble"])
    chair("silla", (4.36, 3.84, 0.0), (0, 0, R(-6)), M)

    # Ventana: tapada con carton y periodicos; la luz de la calle entra por las rendijas
    use("Deterioro")
    cover_window("ventana_sala", "y", 0.0, 1, [
        ("carton", 1.22, 1.92, 1.50, 2.28, 2.0, 0.020),
        ("carton", 1.97, 2.64, 1.42, 2.25, -3.0, 0.022),
        ("periodico", 2.60, 2.92, 1.42, 1.86, 9.0, 0.026),
        ("carton", 1.22, 2.30, 0.82, 1.47, -1.5, 0.024),
        ("periodico", 2.27, 2.90, 0.84, 1.40, 4.0, 0.030),
        ("periodico", 1.84, 2.14, 1.90, 2.30, -6.0, 0.034),
        ("cinta", 1.84, 2.04, 1.64, 1.68, 0.0, 0.040),
        ("cinta", 1.36, 1.40, 1.38, 1.60, 0.0, 0.040),
        ("cinta", 2.48, 2.52, 1.33, 1.50, 3.0, 0.040),
        ("cinta", 1.20, 1.40, 2.10, 2.14, 25.0, 0.040),
    ], M)

    # Donde colgaba la foto familiar queda el papel menos gastado y el clavo
    box("marca_cuadro", (1.25, 4.197, 1.30), (1.85, 4.2, 1.75), M["papel_marca"], uv=(4.0, 4.0, H))
    box("clavo", (1.545, 4.17, 1.72), (1.555, 4.2, 1.73), M["metal_oscuro"])

    # Lo que dejo el consumo: en la mesa de centro y alrededor. Cada rastro es un objeto, o un
    # vacio con sus piezas, con el origen en su base: en la Noche 1 Elias los recoge (los clips
    # recoger_mesa y recoger_piso de brazos_animaciones.py)
    piezas = [cyl("cenicero_vidrio", (1.55, 2.62, 0.42), 0.06, 0.02, M["vidrio"])]
    for i in range(6):
        a = rng.uniform(0, 2 * math.pi)
        piezas.append(cyl(f"colilla_{i}", (1.55 + 0.03 * math.cos(a), 2.62 + 0.03 * math.sin(a), 0.445), 0.005,
                          0.028, M["colilla"], rot=(R(90), 0, a), seg=5))
    group("cenicero", (1.55, 2.62, 0.42), piezas)
    group("cuchara", (1.84, 2.80, 0.42), [
        mesh_obj("cuchara_cazo", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0), M["metal"],
                 loc=(1.78, 2.80, 0.428), scale=(0.022, 0.016, 0.006)),
        mesh_obj("cuchara_hollin", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0),
                 M["negro"], loc=(1.78, 2.80, 0.4245), scale=(0.018, 0.013, 0.004)),
        box("cuchara_mango", (1.80, 2.796, 0.424), (1.93, 2.806, 0.428), M["metal"], rot=(0, 0, R(12)))])
    syringe("jeringa_mesa", (1.86, 2.57, 0.42), R(-20), M)
    syringe("jeringa_piso", (2.35, 2.62, 0.0), R(70), M)
    piezas = [box(f"cinturon_{i}", (x - 0.06, y - 0.015, 0.42), (x + 0.06, y + 0.015, 0.424), M["cuero"],
                  pivot=(x, y, 0.42), rot=(0, 0, R(yaw)))
              for i, (x, y, yaw) in enumerate(((1.42, 2.88, 0), (1.53, 2.90, 15), (1.64, 2.88, 30), (1.73, 2.85, 45)))]
    piezas.append(box("hebilla", (1.34, 2.865, 0.42), (1.37, 2.895, 0.426), M["laton"]))
    group("cinturon", (1.56, 2.875, 0.42), piezas)
    box("encendedor", (1.96, 2.86, 0.42), (2.04, 2.885, 0.435), M["plastico_rojo"], rot=(0, 0, R(-25)))
    bottle("botella_mesa", (2.06, 2.56, 0.42), M["vidrio_ambar"])
    bottle("botella_sofa", (0.42, 3.28, 0.0), M["vidrio_verde"])
    bottle("botella_tirada", (2.62, 3.30, 0.0), M["vidrio_verde"], lying=True, yaw=R(40))
    bottle("botella_tele", (1.95, 0.25, 0.0), M["vidrio_ambar"], h=0.3, r=0.04)
    box("cojin_respaldo_2_caido", (2.30, 2.95, 0.0), (3.12, 3.27, 0.16), M["sofa"], uv=(0.5, 0.5, 0.5),
        rot=(0, 0, R(25)))
    blob("ropa_sofa", (2.05, 3.62, 0.52), (0.28, 0.20, 0.07), M["ropa_gris"])
    blob("bolsa_entrada", (2.55, 0.35, 0.0), (0.26, 0.24, 0.30), M["bolsa"])
    floor_lamp("lampara_caida", (0.32, 3.9, 0.13), (R(85), 0, R(15)), M)
    for i, (x, y, yaw) in enumerate(((1.0, 1.4, 20), (2.4, 2.05, -35), (0.75, 3.1, 70), (3.75, 1.95, 10))):
        newspaper_floor(f"periodico_piso_{i}", x, y, yaw, M)
    floor_stain("mancha_piso", 0.8, 2.15, 0.22, M)
    box("comida_1", (4.08, 2.93, 0.78), (4.30, 3.13, 0.85), M["unicel"], rot=(0, 0, R(12)))
    box("comida_2", (4.36, 3.18, 0.78), (4.58, 3.38, 0.81), M["unicel"], rot=(0, 0, R(-20)))

    # Version 'efecto': como era antes
    use("Efecto")
    back_cushion("cojin_respaldo_2", 1.56, 2.38)
    chair("silla_2", (3.78, 3.2, 0.0), (0, 0, R(90)), M)
    floor_lamp("lampara", (0.28, 3.95, 0.0), (0, 0, 0), M)
    curtain("cortina_sala_1", "y", 0.0, 1, 1.18, 1.60, 0.75, 2.35, M["cortina"])
    curtain("cortina_sala_2", "y", 0.0, 1, 2.50, 2.92, 0.75, 2.35, M["cortina"])
    cyl("barra_cortina", (0.07, 1.12, 2.38), 0.012, 1.86, M["laton"], rot=(R(-90), 0, 0), seg=6)
    box("alfombra", (0.70, 2.05, 0.0), (2.40, 3.30, 0.01), M["alfombra"])
    box("cuadro", (1.25, 4.17, 1.30), (1.85, 4.2, 1.75), M["marco"])
    box("foto", (1.29, 4.165, 1.34), (1.81, 4.17, 1.71), M["foto"], uv=(0.52, 0.52, 0.37),
        pivot=(1.29, 4.165, 1.34), world_uv=False)
    cyl("vaso_1", (1.62, 2.64, 0.42), 0.03, 0.1, M["vidrio"])
    cyl("vaso_2", (1.78, 2.72, 0.42), 0.03, 0.1, M["vidrio"])

    use("Estructura")
    hanging_bulb("foco_sala", 2.4, 2.2, M, M["foco"])
    hanging_bulb("foco_pasillo", 4.1, 4.95, M, None)  # no hay foco


def cocina(M):
    use("Muebles")
    # mueble bajo con el hueco del fregadero
    boxes_obj("mueble_cocina", [((6.62, 0.12, 0.0), (7.188, 1.9, 0.68)),
                                ((6.62, 0.12, 0.68), (7.188, 0.62, 0.86)),
                                ((6.62, 1.22, 0.68), (7.188, 1.9, 0.86)),
                                ((6.62, 0.62, 0.68), (6.66, 1.22, 0.86)),
                                ((7.10, 0.62, 0.68), (7.188, 1.22, 0.86))], M["mueble_cocina"])
    boxes_obj("manijas_cocina", [((6.60, y, 0.70), (6.62, y + 0.1, 0.72)) for y in (0.30, 0.95, 1.45)], M["metal"])
    boxes_obj("encimera", [((6.58, 0.10, 0.86), (7.188, 0.62, 0.90)), ((6.58, 1.22, 0.86), (7.188, 1.92, 0.90)),
                           ((6.58, 0.62, 0.86), (6.66, 1.22, 0.90)), ((7.10, 0.62, 0.86), (7.188, 1.22, 0.90))],
              M["encimera"])
    boxes_obj("fregadero", [((6.66, 0.62, 0.70), (7.10, 1.22, 0.715)),
                            ((6.66, 0.62, 0.715), (6.675, 1.22, 0.9)), ((7.085, 0.62, 0.715), (7.10, 1.22, 0.9)),
                            ((6.675, 0.62, 0.715), (7.085, 0.635, 0.9)), ((6.675, 1.205, 0.715), (7.085, 1.22, 0.9))],
              M["metal"])
    cyl("llave_agua", (7.14, 0.92, 0.90), 0.012, 0.2, M["metal"], seg=6)
    box("llave_agua_pico", (7.0, 0.91, 1.075), (7.152, 0.93, 1.095), M["metal"])
    # La manija en cruz, arriba de la llave: gira un cuarto de vuelta para abrir el agua. Su
    # origen esta en el eje de la llave (ver brazos_animaciones.py, el clip tomar_agua).
    boxes_obj("llave_agua_manija", [((7.135, 0.915, 1.10), (7.145, 0.925, 1.112)),
                                    ((7.105, 0.914, 1.112), (7.175, 0.926, 1.124)),
                                    ((7.134, 0.885, 1.112), (7.146, 0.955, 1.124))],
              M["metal"], origin=(7.14, 0.92, 1.10))
    # El chorro: sale de la punta del pico y cae dentro de la taza que se pone abajo. No se ve
    # en los renders del 4B; en Unity lo muestra el fregadero mientras corre el agua.
    cyl("chorro_agua", (7.012, 0.92, 0.94), 0.005, 0.135, M["agua"], seg=5).hide_render = True
    # estufa de cuatro hornillas y el tanque de gas
    box("estufa", (6.62, 1.95, 0.0), (7.18, 2.55, 0.88), M["esmalte"])
    box("estufa_respaldo", (7.12, 1.95, 0.88), (7.18, 2.55, 1.0), M["esmalte"])
    for i, (x, y) in enumerate(((6.76, 2.10), (6.76, 2.40), (7.0, 2.10), (7.0, 2.40))):
        cyl(f"hornilla_{i}", (x, y, 0.88), 0.055, 0.012, M["metal_oscuro"])
    box("horno_vidrio", (6.612, 2.03, 0.22), (6.62, 2.47, 0.60), M["pantalla"])
    box("horno_manija", (6.585, 2.05, 0.66), (6.60, 2.45, 0.68), M["metal"])
    boxes_obj("perillas", [((6.605, y - 0.02, 0.75), (6.62, y + 0.02, 0.79)) for y in (2.06, 2.18, 2.32, 2.44)],
              M["plastico_negro"])
    cyl("tanque_gas", (7.0, 2.78, 0.0), 0.15, 0.6, M["tanque_gas"], seg=10)
    cyl("tanque_valvula", (7.0, 2.78, 0.6), 0.03, 0.06, M["metal"], seg=6)
    # refrigerador viejo (la puerta mira hacia la cocina)
    box("refrigerador", (6.48, 3.42, 0.06), (7.15, 4.15, 1.64), M["esmalte"])
    box("refrigerador_base", (6.50, 3.45, 0.0), (7.12, 4.12, 0.06), M["metal_oscuro"])
    box("refrigerador_junta", (6.475, 3.42, 1.18), (6.48, 4.15, 1.19), M["negro"])
    boxes_obj("refrigerador_manijas", [((6.45, 3.50, 0.85), (6.475, 3.54, 1.12)),
                                       ((6.45, 3.50, 1.25), (6.475, 3.54, 1.40))], M["metal"])
    # calendario detenido en el mes en que murio Tomas
    box("calendario", (5.75, 4.18, 1.35), (6.05, 4.188, 1.80), M["calendario"], uv=(0.30, 0.30, 0.45),
        pivot=(5.75, 4.18, 1.35), world_uv=False)

    use("Estructura")
    box("fluorescente_base", (5.93, 1.55, H - 0.04), (6.07, 2.65, H), M["metal_oscuro"])
    box("fluorescente_tubo", (5.98, 1.60, H - 0.07), (6.02, 2.60, H - 0.04), M["fluor"])

    use("Deterioro")
    cover_window("ventana_cocina", "y", 7.2, -1, [
        ("periodico", 0.62, 1.32, 1.08, 1.62, 2.0, 0.015),
        ("periodico", 1.26, 1.98, 1.10, 1.66, -3.0, 0.018),
        ("periodico", 0.62, 1.30, 1.58, 2.18, -2.0, 0.021),
        ("periodico", 1.28, 1.98, 1.63, 2.16, 4.0, 0.024),
        ("cinta", 1.22, 1.36, 1.60, 1.64, 0.0, 0.030),
    ], M)
    for i in range(3):  # platos sucios en el fregadero
        cyl(f"plato_{i}", (6.86 + 0.01 * i, 0.84 - 0.008 * i, 0.715 + 0.014 * i), 0.11, 0.012, M["porcelana"], seg=10)
    cyl("taza_1", (6.78, 1.08, 0.715), 0.04, 0.09, M["porcelana"])
    cyl("taza_2", (6.98, 1.10, 0.715), 0.04, 0.09, M["porcelana"], rot=(R(70), 0, R(30)))
    cyl("olla", (6.76, 2.10, 0.892), 0.10, 0.12, M["metal_oscuro"], seg=10)
    bottle("botella_cocina_1", (6.72, 0.30, 0.90), M["vidrio_verde"])
    bottle("botella_cocina_2", (6.84, 0.36, 0.90), M["vidrio_ambar"], h=0.3, r=0.04)
    bottle("botella_cocina_3", (6.78, 1.62, 0.90), M["vidrio_verde"])
    bottle("botella_cocina_4", (6.20, 3.70, 0.0), M["vidrio_verde"], lying=True, yaw=R(-30))
    blob("bolsa_cocina_1", (5.18, 3.86, 0.0), (0.28, 0.26, 0.34), M["bolsa"])
    blob("bolsa_cocina_2", (5.50, 3.98, 0.0), (0.22, 0.20, 0.26), M["bolsa"])
    floor_stain("mancha_cocina", 6.2, 1.6, 0.25, M)


def dormitorio(M):
    use("Muebles")
    box("colchon", (0.25, 5.35, 0.0), (1.65, 7.3, 0.18), M["colchon"], uv=(1, 1, 1))
    box("almohada", (0.42, 6.86, 0.18), (1.10, 7.22, 0.28), M["almohada"], rot=(0, 0, R(-6)))

    def blanket(bm):
        bmesh.ops.create_grid(bm, x_segments=7, y_segments=7, size=0.5)
        for v in bm.verts:
            v.co.z = 0.05 * rng.random() + 0.03 * math.sin(v.co.x * 11) + 0.02 * math.cos(v.co.y * 9)

    mesh_obj("manta", blanket, M["manta"], loc=(0.98, 6.05, 0.20), rot=(0, 0, R(14)), scale=(1.3, 1.25, 1.0))
    # ropero (escondite): una de las puertas quedo entreabierta
    box("ropero", (2.80, 5.80, 0.0), (3.38, 7.35, 2.0), M["mueble"])
    box("ropero_rendija", (2.795, 6.555, 0.06), (2.80, 6.60, 1.94), M["negro"])
    boxes_obj("ropero_manijas", [((2.78, 6.47, 1.0), (2.795, 6.50, 1.15)), ((2.78, 6.66, 1.0), (2.795, 6.69, 1.15))],
              M["laton"])

    # El foco del techo: quemado en la abstinencia, prendido bajo el efecto
    use("Estructura")
    hanging_bulb("foco_dormitorio", 1.7, 5.85, M)
    use("Efecto")
    bulb("foco_dormitorio_efecto", 1.7, 5.85, M["foco"])
    # Bajo el efecto, cortinas como en la sala: por el medio entra el atardecer
    curtain("cortina_dormitorio_1", "y", 0.0, 1, 5.18, 5.60, 0.75, 2.35, M["cortina"])
    curtain("cortina_dormitorio_2", "y", 0.0, 1, 6.30, 6.72, 0.75, 2.35, M["cortina"])
    cyl("barra_cortina_dormitorio", (0.07, 5.12, 2.38), 0.012, 1.66, M["laton"], rot=(R(-90), 0, 0), seg=6)

    use("Deterioro")
    bulb("foco_dormitorio", 1.7, 5.85, M["foco_apagado"])
    cover_window("ventana_dormitorio", "y", 0.0, 1, [
        ("carton", 5.22, 6.05, 0.82, 1.70, 1.0, 0.020),
        ("carton", 6.02, 6.68, 0.82, 1.55, -2.0, 0.022),
        ("carton", 5.22, 6.10, 1.66, 2.28, -1.5, 0.024),
        ("periodico", 6.12, 6.62, 1.52, 1.98, 18.0, 0.030),
        ("cinta", 5.98, 6.12, 1.20, 1.24, 0.0, 0.036),
    ], M)
    cyl("cubeta", (1.95, 5.80, 0.0), 0.14, 0.28, M["plastico_azul"], r2=0.16, seg=10)
    bottle("agua_1", (1.78, 6.95, 0.0), M["botella_agua"], h=0.28, r=0.04)
    bottle("agua_2", (1.85, 6.45, 0.0), M["botella_agua"], h=0.28, r=0.04, lying=True, yaw=R(20))
    syringe("jeringa_colchon", (1.72, 6.05, 0.0), R(-40), M)
    blob("ropa_1", (2.30, 4.75, 0.0), (0.30, 0.25, 0.10), M["ropa_azul"])
    blob("ropa_2", (0.75, 4.70, 0.0), (0.25, 0.22, 0.08), M["ropa_roja"])
    blob("ropa_3", (2.45, 5.35, 0.0), (0.20, 0.18, 0.07), M["ropa_gris"])
    hidden_dose(M)


# La dosis escondida: bajo el borde del colchon que da al cuarto, cerca de la almohada. La
# media va de canto al borde (la boca hacia adentro): la punta asoma 6 cm por el costado.
DOSIS = (1.61, 6.60, 0.0)
DOSIS_GIRO = 90.0


def hidden_dose(M):
    """La dosis de la Noche 1 (secciones 5 y 6.3): Elias la escondio de si mismo bajo el colchon,
    envuelta en una media. Por el costado del colchon asoma la punta de la media; la jeringa sale
    por la boca, que queda bajo el colchon, asi que no se ve hasta sacarla. La raiz esta en el
    piso, bajo el eje de la media. No usa el generador de ruido, para no cambiar el resto del 4B."""
    use("Deterioro")
    r, flat = 0.027, 0.8      # la media va aplastada bajo el colchon
    zc = r * flat

    def tube(name, y0, y1, rad, mat, rad2=None):
        """Tramo de la media a lo largo de Y; rad en el extremo y0, rad2 en el y1."""
        m = (Matrix.Translation((0, (y0 + y1) / 2, zc)) @ Matrix.Diagonal((1, 1, flat, 1))
             @ Matrix.Rotation(R(-90), 4, "X"))
        return mesh_obj(name, lambda bm: bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=8, radius1=rad, radius2=rad if rad2 is None else rad2,
            depth=y1 - y0, matrix=m), mat)

    root = empty("dosis_colchon", DOSIS, (0, 0, R(DOSIS_GIRO)))
    return parent([
        tube("dosis_media", -0.08, 0.06, r, M["media"]),
        tube("dosis_media_punta", -0.10, -0.08, 0.014, M["media"], rad2=r),
        tube("dosis_media_franja_1", 0.035, 0.042, r + 0.0015, M["media_franja"]),
        tube("dosis_media_franja_2", 0.047, 0.054, r + 0.0015, M["media_franja"]),
        # el embolo hacia la boca de la media: asoma 7 cm
        syringe("dosis_jeringa", (0.0, 0.012, zc - 0.0065), R(90), M),
    ], root)


def bano(M):
    use("Muebles")
    boxes_obj("tina", [((4.12, 6.70, 0.0), (5.594, 7.394, 0.06)),
                       ((4.12, 6.70, 0.06), (4.18, 7.394, 0.52)), ((5.534, 6.70, 0.06), (5.594, 7.394, 0.52)),
                       ((4.18, 6.70, 0.06), (5.534, 6.76, 0.52)), ((4.18, 7.334, 0.06), (5.534, 7.394, 0.52))],
              M["porcelana"])
    cyl("barra_cortina_bano", (4.12, 6.73, 1.95), 0.01, 1.47, M["metal"], rot=(0, R(90), 0), seg=6)
    curtain("cortina_bano", "x", 6.73, 1, 4.14, 4.80, 0.60, 1.93, M["cortina_bano"], pleats=4, depth=-0.015)
    # inodoro contra la pared oeste
    box("inodoro_tanque", (3.506, 6.83, 0.40), (3.70, 7.27, 0.80), M["porcelana"])
    cyl("inodoro_taza", (3.88, 7.05, 0.0), 0.15, 0.40, M["porcelana"], r2=0.19, seg=8)
    cyl("inodoro_asiento", (3.88, 7.05, 0.40), 0.20, 0.025, M["plastico_beige"], seg=8)
    box("inodoro_tapa", (3.70, 6.86, 0.42), (3.73, 7.24, 0.84), M["plastico_beige"])
    # lavamanos con espejo
    boxes_obj("lavamanos", [((5.14, 5.88, 0.78), (5.594, 6.40, 0.80)),
                            ((5.14, 5.88, 0.80), (5.17, 6.40, 0.90)), ((5.564, 5.88, 0.80), (5.594, 6.40, 0.90)),
                            ((5.17, 5.88, 0.80), (5.564, 5.91, 0.90)), ((5.17, 6.37, 0.80), (5.564, 6.40, 0.90))],
              M["porcelana"])
    cyl("lavamanos_pie", (5.40, 6.14, 0.0), 0.07, 0.78, M["porcelana"])
    cyl("lavamanos_llave", (5.54, 6.14, 0.90), 0.01, 0.12, M["metal"], seg=6)
    box("botiquin", (5.50, 5.92, 1.15), (5.594, 6.36, 1.70), M["porcelana"])
    box("espejo", (5.494, 5.95, 1.18), (5.50, 6.33, 1.67), M["espejo"])

    use("Estructura")
    hanging_bulb("foco_bano", 4.55, 6.35, M, M["foco_apagado"])

    use("Deterioro")
    blob("toalla", (4.55, 6.15, 0.0), (0.30, 0.22, 0.06), M["toalla"])
    cyl("frasco_1", (5.22, 5.94, 0.90), 0.018, 0.06, M["frasco"], seg=6)
    cyl("frasco_2", (5.27, 5.95, 0.90), 0.018, 0.06, M["frasco"], rot=(R(90), 0, R(40)), seg=6)

    # La silla atrancando la puerta del bano desde el pasillo: el respaldo,
    # inclinado, queda bajo la manija.
    chair("silla_atrancada", (3.92, 5.20, 0.0), (R(-25), 0, 0), M, pivot=(0, 0.2, 0))


def backdrops(M):
    """Lo que se ve por las rendijas de las ventanas: el resplandor de la calle y del patio.
    No proyectan sombra, para no tapar las luces que estan afuera."""
    use("Estructura")
    for name, mn, mx, mat in (("resplandor_sala", (-0.32, 1.1, 0.6), (-0.30, 3.0, 2.6), "resplandor_calle"),
                              ("resplandor_dormitorio", (-0.32, 5.1, 0.6), (-0.30, 6.8, 2.6), "resplandor_calle"),
                              ("resplandor_cocina", (7.50, 0.5, 0.9), (7.52, 2.1, 2.4), "resplandor_patio"),
                              ("resplandor_bano", (4.3, 7.70, 1.6), (5.3, 7.72, 2.6), "resplandor_patio")):
        ob = box(name, mn, mx, M[mat])
        ob.visible_shadow = False
        BACKDROPS.append(ob)


LUZ_PASILLO = (3.45, -1.4, 0.25)  # la luz-truco pasillo_edificio, que se cuela bajo la puerta de entrada


def eventos(M):
    """Golpes en la puerta (Noche 1): alguien parado afuera tapa la luz que entra por abajo.

    En Blender, los pies tapan la luz y dejan dos sombras en el piso de adentro. En Unity esa luz
    esta precalculada y los pies no la tapan, asi que van tambien las sombras ya hechas: la forma
    de cada pie proyectada desde la luz sobre el piso de adentro, hasta donde llega la franja de
    luz. No salen en los renders (aqui ya estan las de verdad); en Unity las muestra
    GolpesEnLaPuerta, sin los pies, que se verian por la mirilla."""
    use("Eventos")
    pies = {"izq": ((3.22, -0.32, 0.0), (3.36, -0.06, 0.10)), "der": ((3.54, -0.30, 0.0), (3.68, -0.05, 0.10))}
    lx, ly, _ = LUZ_PASILLO
    for lado, (mn, mx) in pies.items():
        box("pie_" + lado, mn, mx, M["negro"])
        # En cada borde de la sombra (y de adentro), el ancho que tapa el pie visto desde la luz
        bordes = []
        for yp in (0.0, 0.22):
            ks = [(yp - ly) / (yf - ly) for yf in (mn[1], mx[1])]
            d = [(x - lx) * k for x in (mn[0], mx[0]) for k in ks]
            bordes.append((lx + min(d), lx + max(d), yp))

        def build(bm, b=bordes):
            (a0, a1, y0), (c0, c1, y1) = b
            bm.faces.new([bm.verts.new(p) for p in ((a0, y0, 0.003), (a1, y0, 0.003), (c1, y1, 0.003), (c0, y1, 0.003))])
        sombra = mesh_obj("sombra_pie_" + lado, build, M["negro"], uv=None)
        sombra.hide_render = True
        sombra.visible_shadow = False


def labels(M):
    use("Plano")
    for text, x, y, size in (("SALA", 2.0, 1.55, 0.30), ("COCINA", 5.75, 3.0, 0.22),
                             ("DORMITORIO", 1.75, 4.75, 0.22), ("BA\u00d1O", 4.85, 6.3, 0.20),
                             ("PASILLO", 4.1, 4.95, 0.13), ("ENTRADA", 3.45, 0.35, 0.13)):
        text_obj("etiqueta_" + text.lower(), text, size, M["etiqueta"], (x, y, 2.45))


# ---------------------------------------------------------------------------
# Luces, mundo y camaras
# ---------------------------------------------------------------------------
WARM = (1.0, 0.68, 0.38)
GOLD = (1.0, 0.78, 0.50)
COLD = (0.75, 1.0, 0.85)
SODIUM = (1.0, 0.50, 0.18)
MOON = (0.55, 0.70, 0.92)


def light(name, kind, loc, states, target=None, radius=0.05, size=(0.5, 0.5), spot=(45, 0.3)):
    """states: {estado: (color, potencia)}. Si un estado no aparece, la luz se apaga."""
    ld = bpy.data.lights.new(name, kind)
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = radius
    if kind == "SPOT":
        ld.spot_size, ld.spot_blend = R(spot[0]), spot[1]
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size
    if kind == "SUN":
        ld.angle = R(3)
    ob = link(bpy.data.objects.new(name, ld))
    ob.location = loc
    if target is not None:
        aim(ob, target)
    LIGHTS[name] = (ob, states)
    return ob


def lights():
    use("Luces")
    light("luz_sala", "POINT", (2.4, 2.2, H - 0.48), {"abstinencia": (WARM, 24), "efecto": (GOLD, 45)}, radius=0.03)
    light("luz_cocina", "AREA", (6.0, 2.1, H - 0.09), {"abstinencia": (COLD, 22), "efecto": (GOLD, 30)},
          size=(0.06, 1.0))
    # El farol de la calle esta al noroeste: sus haces cruzan la sala hacia la puerta
    light("farola_sala", "SPOT", (-2.2, 4.6, 3.4), {"abstinencia": (SODIUM, 3000)},
          target=(2.0, 0.8, 0.0), spot=(40, 0.2))
    # Bajo el efecto: luz dorada de atardecer que cae sobre el sofa
    light("sol_efecto", "SPOT", (-3.0, -0.6, 2.4), {"efecto": ((1.0, 0.70, 0.40), 2500)},
          target=(1.6, 3.8, 0.4), radius=0.05, spot=(30, 0.4))
    light("farola_dormitorio", "SPOT", (-2.4, 6.2, 3.6), {"abstinencia": (SODIUM, 3000)},
          target=(1.2, 6.0, 0.0), spot=(40, 0.2))
    light("patio_cocina", "SPOT", (9.2, 1.3, 3.8), {"abstinencia": (MOON, 250), "efecto": (GOLD, 400)},
          target=(6.4, 1.3, 0.6), radius=0.2, spot=(35, 0.3))
    light("luna_bano", "AREA", (4.8, 7.3, 2.1), {"abstinencia": (MOON, 25)}, target=(4.6, 6.2, 0.0), size=(0.5, 0.3))
    # Trucos: luces bajas para que la luz se cuele por debajo de las puertas.
    # La propiedad "truco" va al JSON de Unity (ver exportar_unity.py).
    light("fuga_bano", "POINT", (4.1, 6.2, 0.12), {"abstinencia": ((0.62, 0.78, 0.95), 25)}, radius=0.02)["truco"] = "fuga"
    light("pasillo_edificio", "POINT", LUZ_PASILLO, {"abstinencia": (WARM, 100)}, radius=0.02)["truco"] = "fuga"
    # Rebote: Eevee no hace rebotar la luz; una luz tenue sin sombra junto a la
    # ventana del dormitorio hace de luz rebotada del piso. En Unity no se usan: el
    # rebote lo da la luz precalculada.
    rb = light("rebote_dormitorio", "POINT", (1.0, 6.0, 0.5), {"abstinencia": (SODIUM, 6)}, radius=0.5)
    rb.data.use_shadow = False
    rb["truco"] = "rebote"
    # y la luz que sale bajo la puerta del bano rebota en el piso del pasillo
    rb = light("rebote_bano", "POINT", (4.1, 5.35, 0.06), {"abstinencia": ((0.62, 0.78, 0.95), 3.0)}, radius=0.3)
    rb.data.use_shadow = False
    rb["truco"] = "rebote"
    light("led_contestadora", "POINT", (3.058, 3.79, 0.69), {"abstinencia": ((1.0, 0.1, 0.04), 0.04)}, radius=0.005)
    light("lampara_pie", "POINT", (0.28, 3.95, 1.42), {"efecto": ((1.0, 0.72, 0.45), 30)}, radius=0.08)
    # El dormitorio bajo el efecto (ahi se toma la dosis de la Noche 1): el foco del techo y el
    # atardecer, que entra por la ventana a 35 grados y cae sobre el colchon y el piso. En Unity
    # van enteras en la luz precalculada ("precalculada" en el JSON): como luces mixtas se
    # juntaban con otras, y Unity pasaba a precalculadas la de la sala y la del patio de la cocina.
    light("luz_dormitorio", "POINT", (1.7, 5.85, H - 0.48), {"efecto": (GOLD, 30)}, radius=0.03)["precalculada"] = True
    light("sol_dormitorio", "SPOT", (-3.0, 4.90, 3.80), {"efecto": ((1.0, 0.70, 0.40), 2500)},
          target=(2.0, 6.65, 0.05), radius=0.05, spot=(30, 0.4))["precalculada"] = True
    light("sol_plano", "SUN", (3.6, 3.7, 10.0), {"plano": ((1.0, 1.0, 1.0), 2.5)}, target=(3.4, 3.9, 0.0))


WORLD = {
    "abstinencia": dict(bg=(0.004, 0.005, 0.007), fog=(0.75, 0.80, 0.72), density=0.022),
    "efecto": dict(bg=(0.07, 0.045, 0.025), fog=(1.0, 0.82, 0.60), density=0.018),
    "plano": dict(bg=(0.30, 0.30, 0.30), fog=(1.0, 1.0, 1.0), density=0.0),
}


def setup_world():
    w = bpy.data.worlds.new("Mundo4B")
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
    vol.inputs["Anisotropy"].default_value = 0.35
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])


def set_state(state, techo, M, eventos_on=False):
    """Cambia toda la escena a 'abstinencia', 'efecto' o 'plano'."""
    COLS["Deterioro"].hide_render = state == "efecto"
    COLS["Efecto"].hide_render = state != "efecto"
    COLS["Eventos"].hide_render = not eventos_on
    COLS["Plano"].hide_render = state != "plano"
    techo.hide_render = state == "plano"
    for ob in BACKDROPS:
        ob.hide_render = state == "plano"
    for mat, dirty, clean in SWAPS:
        mat.node_tree.nodes["Textura"].image = clean if state == "efecto" else dirty
    for ob, states in LIGHTS.values():
        cfg = states.get(state) or (states.get("abstinencia") if state == "plano" else None)
        ob.hide_render = cfg is None
        if cfg:
            ob.data.color, ob.data.energy = cfg
    W = WORLD[state]
    nt = scene.world.node_tree
    nt.nodes["Fondo"].inputs["Color"].default_value = (*W["bg"], 1.0)
    nt.nodes["Niebla"].inputs["Density"].default_value = W["density"]
    nt.nodes["Niebla"].inputs["Color"].default_value = (*W["fog"], 1.0)
    efecto = state == "efecto"
    M["led"].node_tree.nodes["Emision"].inputs["Strength"].default_value = 0.0 if efecto else 8.0
    M["foco"].node_tree.nodes["Emision"].inputs["Strength"].default_value = 25.0 if efecto else 10.0
    M["fluor"].node_tree.nodes["Emision"].inputs["Color"].default_value = \
        (1.0, 0.85, 0.6, 1.0) if efecto else (0.8, 1.0, 0.88, 1.0)
    for key, night, strength in (("resplandor_calle", (1.0, 0.45, 0.15), 1.2),
                                 ("resplandor_patio", (0.35, 0.45, 0.60), 0.6)):
        em = M[key].node_tree.nodes["Emision"]
        em.inputs["Color"].default_value = (1.0, 0.78, 0.50, 1.0) if efecto else (*night, 1.0)
        em.inputs["Strength"].default_value = 3.0 if efecto else strength


def camera(name, loc, target, lens=24.0, ortho=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start, cd.clip_end = 0.03, 40.0
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    ob = link(bpy.data.objects.new(name, cd))
    ob.location = loc
    if target is not None:
        aim(ob, target)
    CAMS[name] = ob
    return ob


def cameras():
    use("Camaras")
    camera("Cam_sala", (3.45, 0.30, 1.6), (3.0, 5.0, 1.2))            # desde la entrada
    camera("Cam_bano", (4.1, 3.0, 1.5), (4.1, 5.6, 1.04))             # el pasillo y la puerta del bano
    camera("Cam_entrada", (2.75, 2.2, 1.6), (3.25, 0.0, 0.9))         # la puerta: alguien toca
    camera("Cam_cocina", (5.15, 0.35, 1.6), (6.9, 2.9, 0.95))
    camera("Cam_dormitorio", (3.05, 4.75, 1.6), (0.3, 6.3, 0.75))
    camera("Cam_dosis", (2.55, 5.80, 1.6), (1.62, 6.58, 0.05))         # junto al colchon: asoma la media
    camera("Cam_plano", (3.6, 3.7, 12.0), None, ortho=8.0)            # desde arriba, sin techo


def _try_set(obj, attr, value):
    if hasattr(obj, attr):
        try:
            setattr(obj, attr, value)
        except Exception as e:
            print(f"[aviso] {attr}: {e}")


def setup_render():
    r = scene.render
    r.resolution_percentage = 100
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
    _try_set(ee, "volumetric_tile_size", "2")
    _try_set(ee, "volumetric_samples", 64)
    _try_set(ee, "volumetric_start", 0.05)
    _try_set(ee, "volumetric_end", 14.0)
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
    hh, ww = q.shape[:2]
    out = np.ones((hh, ww, 4), dtype=np.float32)
    out[:, :, :3] = q
    o = bpy.data.images.new("post", ww, hh, alpha=False)
    o.pixels.foreach_set(out.ravel())
    o.filepath_raw = path
    o.file_format = "PNG"
    o.save()
    bpy.data.images.remove(o)


# ---------------------------------------------------------------------------
VIEWS = {
    "sala": dict(cam="Cam_sala", state="abstinencia"),
    "sala_efecto": dict(cam="Cam_sala", state="efecto"),
    "bano": dict(cam="Cam_bano", state="abstinencia"),
    "entrada": dict(cam="Cam_entrada", state="abstinencia", eventos=True),
    "cocina": dict(cam="Cam_cocina", state="abstinencia"),
    "dormitorio": dict(cam="Cam_dormitorio", state="abstinencia"),
    "dormitorio_efecto": dict(cam="Cam_dormitorio", state="efecto"),
    "dosis": dict(cam="Cam_dosis", state="abstinencia"),
    "plano": dict(cam="Cam_plano", state="plano", res=(360, 360), up=3),
}
SHEET = [["sala", "sala_efecto"], ["bano", "entrada"], ["cocina", "dormitorio"]]


def main():
    t0 = time.time()
    for d in (TEX_DIR, SCENE_DIR, RENDER_DIR):
        os.makedirs(d, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

    root = bpy.data.collections.new("Departamento_4B")
    scene.collection.children.link(root)
    for name in ("Estructura", "Muebles", "Deterioro", "Efecto", "Eventos", "Luces", "Camaras", "Plano"):
        COLS[name] = bpy.data.collections.new(name)
        root.children.link(COLS[name])

    M = build_materials()
    techo = architecture(M)
    sala(M)
    cocina(M)
    dormitorio(M)
    bano(M)
    backdrops(M)
    eventos(M)
    labels(M)
    lights()
    cameras()
    setup_world()
    setup_render()

    tris = sum(len(p.vertices) - 2 for ob in bpy.data.objects if ob.type == "MESH" for p in ob.data.polygons)
    print(f"[info] 4B: {sum(1 for o in bpy.data.objects if o.type == 'MESH')} mallas, {tris} triangulos")

    panels = {}
    for key, cfg in VIEWS.items():
        if ONLY and key not in ONLY:
            continue
        set_state(cfg["state"], techo, M, cfg.get("eventos", False))
        scene.camera = CAMS[cfg["cam"]]
        rx, ry = cfg.get("res", (RES_X, RES_Y))
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        raw = os.path.join(RENDER_DIR, f"4b_{key}_raw.png")
        scene.render.filepath = raw
        t = time.time()
        bpy.ops.render.render(write_still=True)
        q = ps1_quantize(raw)
        save_png(q, os.path.join(RENDER_DIR, f"4b_{key}.png"), cfg.get("up", UPSCALE))
        os.remove(raw)
        panels[key] = q
        print(f"[render] {key}: {time.time() - t:.1f} s")

    if all(k in panels for row in SHEET for k in row):
        rows = []
        for row in SHEET:
            r = np.concatenate([panels[k] for k in row], axis=1)
            r[:, RES_X - 1:RES_X + 1] = 0.0
            rows.append(r)
        sheet = np.concatenate(rows[::-1], axis=0)  # fila 0 = abajo
        for i in range(1, len(SHEET)):
            sheet[i * RES_Y - 1:i * RES_Y + 1, :] = 0.0
        save_png(sheet, os.path.join(RENDER_DIR, "4b_hoja.png"), 2)

    # Deja la escena como en la Noche 1, vista desde la entrada
    set_state("abstinencia", techo, M)
    scene.camera = CAMS["Cam_sala"]
    scene.render.resolution_x, scene.render.resolution_y = RES_X, RES_Y
    blend = os.path.join(SCENE_DIR, "departamento_4b.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print(f"[aviso] rutas relativas: {e}")

    # Unity: se fotografian los dos estados del mundo y el FBX queda en abstinencia
    estados = {}
    for estado in ("abstinencia", "efecto"):
        set_state(estado, techo, M)
        estados[estado] = exportar_unity.foto_estado()
    set_state("abstinencia", techo, M)
    exportar_unity.exportar(ROOT, "Departamento4B", "departamento_4b", excluir=("Plano",), estados=estados)
    print(f"[info] listo en {time.time() - t0:.1f} s")


main()
