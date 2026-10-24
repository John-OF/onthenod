r"""
El pasillo del 4o piso (Noche 2): en L, como P.T. (documento, seccion 5).

Construye el pasillo low poly con codigo y lo renderiza con el post-proceso PS1 de la prueba
de estilo (480x270, 15 bits con dithering Bayer, escalado x4 sin suavizado). Usa las
texturas de la prueba de estilo (piso, pared, techo, puerta, metal) y agrega sus versiones
limpias para el efecto.

Esta en las coordenadas del 4B: la puerta de entrada del 4B esta en x 3.0-3.9, y = 0. En Unity
los dos modelos van en el origen, sin girar.

Plano (vista desde arriba, metros):

            x=0.8                                         x=17.8
    y=-0.14 +--4B--------4D--------4F-------------tel---+-+ elevador
            |  pasillo largo                            | |
    y=-1.94 +-A----4A--------4C--------4E----------+    | |
              escalera A      (4C: vacio)           |tra-| cuarto de
                                                    |mo  | limpieza
                                                    |corto
                                          y=-8.0    +-B--+
                                                     escalera B

La vuelta: Elias baja por la escalera B y sale por la A, al comienzo del pasillo largo. Las
dos escaleras son iguales (mismas piezas, texturas y luces); Unity lo lleva de una a la otra
en el descanso, donde no ve las puertas. El salto es EscaleraA_ancla - EscaleraB_ancla.

Colecciones:
  Estructura, Objetos     siempre
  Deterioro / Efecto      solo en la abstinencia / solo bajo el efecto (como el 4B)
  EscaleraA, EscaleraB    las dos escaleras
  Departamento4C          el departamento vacio tras la puerta entreabierta (escondite)
  VueltaN / VueltaN_Fuera lo que aparece / desaparece en la vuelta N (documento, seccion 5)
  Fachada4B, SoloRender, Plano   solo para los renders, no van a Unity: la puerta del 4B (en
                          Unity esta la del 4B), la silueta de Tomas y las etiquetas del plano

Estados (en el JSON de Unity): abstinencia (la vuelta 0), efecto y vuelta1 ... vuelta5.

Uso (PowerShell, desde la carpeta del proyecto):
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup `
      -P blender\scripts\pasillo_piso4.py -- blender
  Solo algunas vistas (mas rapido para probar): ... -- blender comienzo,vuelta1
  Sin exportar a Unity (para probar): ... -- blender comienzo --sin-unity

Vistas: comienzo, efecto, esquina, escalera, vuelta1 ... vuelta5, escondite, 4c, ascensor, plano

Salidas (dentro de la carpeta blender/):
  textures/*.png                    texturas nuevas (y las limpias de la prueba de estilo)
  scenes/pasillo_piso4.blend        la escena, para abrirla y retocarla
  renders/pasillo4_<vista>.png      cada vista a 1920x1080 (el plano a 1920x1200)
  renders/pasillo4_vuelta4_foto.png la Polaroid de la vuelta 4: la puerta que no se ve
  renders/pasillo4_hoja.png         diez vistas juntas

Y en el proyecto de Unity (ver exportar_unity.py), en el estado abstinencia:
  unity/Assets/Art/PasilloPiso4/pasillo_piso4.fbx
  unity/Assets/Art/PasilloPiso4/pasillo_piso4_escena.json   luces, camaras y los siete estados
  unity/Assets/Art/PasilloPiso4/Textures/*.png
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
ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ARGS = [a for a in ARGV if not a.startswith("--")]
SIN_UNITY = "--sin-unity" in ARGV  # para probar los renders sin exportar
ROOT = os.path.abspath(ARGS[0]) if ARGS else os.getcwd()
ONLY = ARGS[1].split(",") if len(ARGS) > 1 else None

TEX_DIR = os.path.join(ROOT, "textures")
SCENE_DIR = os.path.join(ROOT, "scenes")
RENDER_DIR = os.path.join(ROOT, "renders")

RES_X, RES_Y = 480, 270
UPSCALE = 4
COLOR_LEVELS = 32  # 15 bits de color, como la PS1

H = 2.6        # alto del techo
DOOR_H = 2.1   # alto de los vanos de puerta
T = 0.1        # grosor de los muros

# Pasillo largo: corre a lo largo de X, frente al 4B. Caras de adentro de sus muros.
XB, XE = 0.8, 17.8          # el fondo (detras del comienzo) y la pared del elevador
YN, YS = -0.14, -1.94       # el muro norte (una piel de 4 cm delante del muro del 4B) y el sur
YC = (YN + YS) / 2
# Tramo corto: baja hacia -Y desde la esquina del elevador
X2A = 16.0                  # su muro oeste (el este es la pared del elevador, XE)
YT2 = -8.0                  # su pared final, la de la escalera B
# Las escaleras: el origen es el centro de la puerta, en la cara del muro que da a la escalera.
# La A tiene la puerta de abajo en el pasillo largo; la B, la de arriba en el tramo corto.
O_A = Vector((1.65, YS - T, H))
O_B = Vector((16.9, YT2 - T, 0.0))

R = math.radians
rng = np.random.default_rng(404)
scene = bpy.context.scene


# ---------------------------------------------------------------------------
# Texturas pixeladas (numpy -> PNG). Fila 0 = abajo.
# ---------------------------------------------------------------------------
def noise(h, w, cy, cx, g=None):
    """Ruido suave que se repite sin cortes."""
    g = rng.random((cy + 1, cx + 1)) if g is None else g
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
    """Usa la textura de la prueba de estilo si ya existe (es la aprobada)."""
    if os.path.exists(os.path.join(TEX_DIR, name + ".png")):
        return load_image(name)
    return save_texture(name, make())


def tex_floor(clean=False):
    """Baldosas crema y rojo oxido de 25 cm. 128 px = 2 m (igual que la prueba de estilo)."""
    s = 128
    yy, xx = np.mgrid[0:s, 0:s]
    checker = ((xx // 16 + yy // 16) % 2).astype(np.float32)[:, :, None]
    cream = np.array([0.60, 0.56, 0.46])
    red = np.array([0.34, 0.11, 0.09])
    rgb = cream * (1 - checker) + red * checker
    tile_var = np.kron(rng.random((s // 16, s // 16)), np.ones((16, 16)))
    grout = ((xx % 16 == 0) | (yy % 16 == 0))[:, :, None]
    if clean:
        rgb = rgb * (0.95 + 0.05 * tile_var)[:, :, None] * 1.1
        rgb = np.where(grout, rgb * 0.72, rgb)
        return rgb * grime(s, s, 0.06)[:, :, None]
    rgb *= (0.82 + 0.18 * tile_var)[:, :, None]
    rgb = np.where(grout, rgb * 0.45, rgb)
    rgb *= grime(s, s, 0.5)[:, :, None]
    return rgb


def tex_wall(clean=False):
    """Zocalo oscuro, verde hasta 1.08 m, franja y crema. 128 x 166 px = 2 m x 2.6 m."""
    w, h = 128, 166
    z = (np.arange(h) + 0.5) / h * H
    base = np.array([0.16, 0.11, 0.07])
    green = np.array([0.22, 0.34, 0.27]) * (1.15 if clean else 1.0)
    strip = np.array([0.10, 0.17, 0.13])
    cream = np.array([0.62, 0.58, 0.46]) * (1.12 if clean else 1.0)
    rgb = np.zeros((h, w, 3))
    for i, zi in enumerate(z):
        rgb[i] = base if zi < 0.12 else green if zi < 1.08 else strip if zi < 1.14 else cream
    if clean:
        return rgb * grime(h, w, 0.07)[:, :, None]
    rgb *= (1.0 - 0.35 * np.clip(1.0 - z / 1.2, 0, 1))[:, None, None]
    rgb *= grime(h, w, 0.4)[:, :, None]
    for _ in range(5):
        x = int(rng.integers(0, w - 3))
        width = int(rng.integers(1, 3))
        length = int(rng.integers(12, 55))
        top = h - 1 - int(rng.integers(0, 6))
        for k in range(length):
            row = top - k
            if row < 0:
                break
            fade = (1 - k / length) ** 1.5
            xo = x + int(round(math.sin(k * 0.3 + x) * 0.8))
            rgb[row, xo:xo + width] *= 1 - 0.35 * fade
    stains = 0.7 * noise(h, w, 6, 5) + 0.3 * noise(h, w, 14, 12)
    stains *= np.clip(z / H + 0.3, 0, 1)[:, None]
    rgb = np.where((stains > 0.66)[:, :, None], rgb * np.array([0.82, 0.75, 0.6]), rgb)
    return rgb


def tex_ceiling(clean=False):
    s = 64
    if clean:
        return np.ones((s, s, 3)) * np.array([0.58, 0.57, 0.52]) * grime(s, s, 0.06)[:, :, None]
    rgb = np.ones((s, s, 3)) * np.array([0.48, 0.47, 0.43])
    rgb *= grime(s, s, 0.3)[:, :, None]
    st = 0.7 * noise(s, s, 5, 5) + 0.3 * noise(s, s, 12, 12)
    return np.where((st > 0.7)[:, :, None], rgb * np.array([0.75, 0.66, 0.48]), rgb)


def tex_door():
    w, h = 64, 128
    yy, xx = np.mgrid[0:h, 0:w]
    rgb = np.array([0.30, 0.17, 0.09]) * (0.72 + 0.28 * noise(h, w, 3, 20))[:, :, None]

    def panel(x0, y0, x1, y1):
        inside = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        return inside & ((xx == x0) | (xx == x1) | (yy == y0) | (yy == y1))

    rgb = np.where((panel(10, 12, 53, 58) | panel(10, 68, 53, 116))[:, :, None], rgb * 0.5, rgb)
    return rgb * grime(h, w, 0.35)[:, :, None]


def tex_metal():
    s = 64
    rgb = np.ones((s, s, 3)) * np.array([0.30, 0.34, 0.37])
    rgb *= grime(s, s, 0.35)[:, :, None]
    rust = 0.5 * noise(s, s, 8, 8) + 0.5 * noise(s, s, 20, 20)
    rust_color = np.array([0.33, 0.16, 0.07]) * (0.7 + 0.3 * rng.random((s, s, 1)))
    rgb = np.where((rust > 0.7)[:, :, None], rust_color, rgb)
    for _ in range(14):
        y, x, n = int(rng.integers(0, s)), int(rng.integers(0, s - 14)), int(rng.integers(4, 14))
        rgb[y, x:x + n] *= 1.35
    return rgb


def tex_stair_wall(clean=False):
    """La escalera: pintura de aceite verde grisaceo hasta 1.2 m, una linea roja y gris claro
    arriba. Manchas de manos a la altura del pasamanos. 128 x 166 px = 2 m x 2.6 m."""
    w, h = 128, 166
    z = (np.arange(h) + 0.5) / h * H
    low = np.array([0.17, 0.22, 0.19])
    line = np.array([0.30, 0.08, 0.06])
    high = np.array([0.50, 0.49, 0.44]) * (1.1 if clean else 1.0)
    rgb = np.zeros((h, w, 3))
    for i, zi in enumerate(z):
        rgb[i] = low if zi < 1.2 else line if zi < 1.24 else high
    if clean:
        return rgb * grime(h, w, 0.06)[:, :, None]
    rgb *= grime(h, w, 0.45)[:, :, None]
    hands = noise(h, w, 3, 16) * np.exp(-((z - 0.98) / 0.12) ** 2)[:, None]
    rgb *= (1.0 - 0.45 * hands)[:, :, None]
    rgb *= (1.0 - 0.3 * np.clip(1.0 - z / 0.4, 0, 1))[:, None, None]
    for _ in range(9):  # rayones
        x, y, n = int(rng.integers(0, w - 12)), int(rng.integers(20, 120)), int(rng.integers(4, 12))
        for k in range(n):
            rgb[min(h - 1, y + k // 3), x + k] *= 0.55
    return rgb


def tex_concrete(clean=False):
    """Concreto de los escalones y descansos. 64 px = 1 m."""
    s = 64
    rgb = np.ones((s, s, 3)) * np.array([0.40, 0.39, 0.36])
    rgb *= (0.85 + 0.15 * rng.random((s, s)))[:, :, None]
    if clean:
        return rgb * 1.1 * grime(s, s, 0.06)[:, :, None]
    rgb *= grime(s, s, 0.45)[:, :, None]
    spots = noise(s, s, 7, 7)
    return np.where((spots > 0.72)[:, :, None], rgb * 0.6, rgb)


def tex_4c_wall():
    """El 4C: papel tapiz de franjas desteñidas, arrancado a parches. 128 x 166 = 2 x 2.6 m."""
    w, h = 128, 166
    yy, xx = np.mgrid[0:h, 0:w]
    z = (yy + 0.5) / h * H
    stripe = ((xx // 8) % 2).astype(np.float32)
    rgb = np.where(stripe[:, :, None] > 0, np.array([0.46, 0.47, 0.36]), np.array([0.52, 0.49, 0.38]))
    dots = ((xx % 8 == 4) & (yy % 12 == 6))
    rgb = np.where(dots[:, :, None], rgb * 0.72, rgb)
    rgb *= grime(h, w, 0.45)[:, :, None]
    torn = 0.65 * noise(h, w, 5, 4) + 0.35 * noise(h, w, 13, 11)
    plaster = np.array([0.48, 0.45, 0.39]) * grime(h, w, 0.3)[:, :, None]
    edge = (torn > 0.6) & (torn < 0.63)
    rgb = np.where((torn > 0.63)[:, :, None], plaster, rgb)
    rgb = np.where(edge[:, :, None], rgb * 0.5, rgb)
    rgb *= (1.0 - 0.3 * np.clip(1.0 - z / 0.8, 0, 1))[:, :, None]
    return rgb


def tex_4c_floor():
    """Tablas de madera grises de polvo, con la marca clara de un mueble. 128 px = 2 m."""
    s = 128
    yy, xx = np.mgrid[0:s, 0:s]
    board = yy // 8
    var = rng.random(s // 8 + 1)[board]
    rgb = np.array([0.30, 0.24, 0.17]) * (0.8 + 0.2 * var)[:, :, None]
    rgb *= (0.85 + 0.15 * noise(s, s, 2, 24))[:, :, None]
    rgb = np.where((yy % 8 == 0)[:, :, None], rgb * 0.5, rgb)
    joint = (xx + board * 37) % 64 == 0
    rgb = np.where(joint[:, :, None], rgb * 0.55, rgb)
    rgb = rgb * 0.75 + np.array([0.36, 0.35, 0.32]) * 0.25  # polvo
    mark = (xx > 70) & (xx < 118) & (yy > 20) & (yy < 70)
    rgb = np.where(mark[:, :, None], rgb * 1.18, rgb)
    return rgb * grime(s, s, 0.3)[:, :, None]


def tex_cab_steel():
    """Acero cepillado de la cabina del elevador, con rayones. 64 x 128 px = 1 m x 2 m."""
    w, h = 64, 128
    rgb = np.ones((h, w, 3)) * np.array([0.30, 0.31, 0.32])
    rgb *= (0.88 + 0.12 * noise(h, w, 40, 2))[:, :, None]
    rgb *= grime(h, w, 0.35)[:, :, None]
    for _ in range(18):
        x, y, n = int(rng.integers(0, w - 10)), int(rng.integers(10, h - 10)), int(rng.integers(3, 10))
        d = int(rng.choice([-1, 1]))
        for k in range(n):
            rgb[y + d * k // 2, x + k] *= 1.18
    rgb[:, :] *= (1.0 - 0.25 * np.clip(1.0 - np.arange(h) / 30.0, 0, 1))[:, None, None]
    return rgb


def tex_cab_floor():
    """Goma negra con botones redondos. 32 px = 0.5 m."""
    s = 32
    yy, xx = np.mgrid[0:s, 0:s]
    rgb = np.ones((s, s, 3)) * 0.07
    stud = ((xx % 8 - 3.5) ** 2 + (yy % 8 - 3.5) ** 2) < 5
    rgb = np.where(stud[:, :, None], rgb * 1.8, rgb)
    return rgb * grime(s, s, 0.3)[:, :, None]


# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------
SWAPS = []   # (material, imagen sucia, imagen limpia): se cambian bajo el efecto
EMIS = {}    # clave -> {estado: (color, fuerza)} de los materiales que brillan


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


WARM = (1.0, 0.68, 0.38)
GOLD = (1.0, 0.78, 0.50)
COLD = (0.75, 1.0, 0.85)
TUBE = (0.8, 1.0, 0.88)
TUBE_WARM = (1.0, 0.85, 0.6)
SODIUM = (1.0, 0.50, 0.18)
GREEN = (0.15, 1.0, 0.35)
CAB = (0.85, 0.95, 1.0)


def build_materials():
    T_ = {
        "piso": load_or_make("piso_baldosa", tex_floor),
        "piso_l": save_texture("piso_baldosa_limpio", tex_floor(True)),
        "pared": load_or_make("pared_pasillo", tex_wall),
        "pared_l": save_texture("pared_pasillo_limpio", tex_wall(True)),
        "techo": load_or_make("techo", tex_ceiling),
        "techo_l": save_texture("techo_limpio", tex_ceiling(True)),
        "puerta": load_or_make("puerta_madera", tex_door),
        "metal": load_or_make("metal_oxidado", tex_metal),
        "esc_pared": save_texture("pared_escalera", tex_stair_wall()),
        "esc_pared_l": save_texture("pared_escalera_limpio", tex_stair_wall(True)),
        "concreto": save_texture("concreto_escalera", tex_concrete()),
        "concreto_l": save_texture("concreto_escalera_limpio", tex_concrete(True)),
        "pared_4c": save_texture("pared_4c", tex_4c_wall()),
        "piso_4c": save_texture("piso_4c", tex_4c_floor()),
        "acero": save_texture("acero_cabina", tex_cab_steel()),
        "goma": save_texture("goma_cabina", tex_cab_floor()),
    }
    S = mat_surface
    M = {
        # superficies con textura
        "piso": S("PasilloPiso", image=T_["piso"], rough=0.6, spec=0.4),
        "pared": S("PasilloPared", image=T_["pared"], rough=0.9),
        "techo": S("PasilloTecho", image=T_["techo"], rough=0.95),
        "puerta": S("PuertaDepartamento", image=T_["puerta"], rough=0.7),
        "metal": S("MetalOxidado", image=T_["metal"], rough=0.5, metallic=0.3),
        "esc_pared": S("EscaleraPared", image=T_["esc_pared"], rough=0.6, spec=0.4),
        "concreto": S("EscaleraPiso", image=T_["concreto"], rough=0.9),
        "pared_4c": S("Pared4C", image=T_["pared_4c"], rough=0.9),
        "piso_4c": S("Piso4C", image=T_["piso_4c"], rough=0.8),
        "acero": S("AceroCabina", image=T_["acero"], rough=0.35, metallic=0.6),
        "goma": S("GomaCabina", image=T_["goma"], rough=0.8),
        # colores lisos
        "marco": S("Marco", (0.12, 0.07, 0.04), rough=0.6),
        "umbral": S("Umbral", (0.42, 0.40, 0.36), rough=0.5),
        "metal_oscuro": S("MetalOscuro", (0.08, 0.09, 0.10), rough=0.5, metallic=0.3),
        "aluminio": S("Aluminio", (0.40, 0.41, 0.42), rough=0.35, metallic=0.8),
        "laton": S("Laton", (0.36, 0.27, 0.11), rough=0.45, metallic=0.8),
        "numero": S("NumeroPuerta", (0.03, 0.025, 0.02), rough=0.6),
        "negro": S("Negro", (0.0, 0.0, 0.0), rough=1.0, spec=0.0),
        "plastico_negro": S("PlasticoNegro", (0.03, 0.03, 0.035), rough=0.4),
        "plastico_rojo": S("PlasticoRojo", (0.42, 0.08, 0.06), rough=0.5),
        "pintura_roja": S("PinturaRoja", (0.42, 0.07, 0.05), rough=0.9),
        "puerta_esc": S("PuertaEscalera", (0.17, 0.21, 0.19), rough=0.5, metallic=0.2),
        "pasamanos": S("Pasamanos", (0.06, 0.05, 0.045), rough=0.4, metallic=0.5),
        "persiana": S("PinturaPersiana", (0.27, 0.25, 0.19), rough=0.8),
        "ropero": S("MaderaRopero", (0.20, 0.12, 0.07), rough=0.6),
        "tabla": S("Tabla", (0.27, 0.19, 0.11), rough=0.9),
        "sabana": S("Sabana", (0.58, 0.56, 0.50), rough=0.95, spec=0.1),
        "carton": S("Carton", (0.42, 0.31, 0.19), rough=0.95, spec=0.1),
        "bolsa": S("BolsaBasura", (0.02, 0.02, 0.025), rough=0.35, spec=0.5),
        "papel": S("Papel", (0.55, 0.53, 0.48), rough=0.9),
        "mancha": S("Mancha", (0.09, 0.03, 0.02), rough=0.15, spec=0.6),
        "humedad": S("ManchaHumedad", (0.035, 0.026, 0.015), rough=0.45, spec=0.45),
        "humedad_borde": S("ManchaHumedadBorde", (0.19, 0.14, 0.065), rough=0.9, spec=0.1),
        "humedad_centro": S("ManchaHumedadCentro", (0.012, 0.010, 0.007), rough=0.15, spec=0.7),
        "charco": S("Charco", (0.012, 0.012, 0.01), rough=0.04, spec=0.9),
        "sombra": S("Sombra", (0.012, 0.012, 0.012), rough=0.95, spec=0.05),
        "directorio": S("Directorio", (0.70, 0.58, 0.10), rough=0.8),
        "balde": S("Balde", (0.12, 0.22, 0.42), rough=0.4),
        "trapeador": S("Trapeador", (0.50, 0.46, 0.38), rough=0.95, spec=0.1),
        "mango": S("MaderaMango", (0.34, 0.24, 0.14), rough=0.7),
        "botella_azul": S("BotellaLimpieza", (0.10, 0.30, 0.45), rough=0.3, spec=0.5),
        "botella_blanca": S("BotellaCloro", (0.62, 0.62, 0.58), rough=0.3, spec=0.5),
        "lata": S("Lata", (0.35, 0.33, 0.30), rough=0.4, metallic=0.6),
        "boton": S("BotonCabina", (0.62, 0.60, 0.55), rough=0.3, metallic=0.5),
        "foco_quemado": S("FocoQuemado", (0.30, 0.30, 0.28), rough=0.3),
        "maceta": S("Maceta", (0.42, 0.18, 0.09), rough=0.85),
        "planta": S("Planta", (0.08, 0.26, 0.07), rough=0.8),
        "planta_seca": S("PlantaSeca", (0.28, 0.20, 0.11), rough=0.9),
        "tierra": S("Tierra", (0.10, 0.07, 0.05), rough=1.0),
        "tapete": S("Tapete", (0.34, 0.11, 0.07), rough=0.95, spec=0.1),
        "cuadro_marco": S("CuadroMarco", (0.30, 0.19, 0.07), rough=0.5),
        "cuadro": S("CuadroPintura", (0.36, 0.46, 0.30), rough=0.8),
        "estampita": S("Estampita", (0.30, 0.38, 0.62), rough=0.4),
        # Polaroid de Tomas (los mismos colores que en tomas.py)
        "pol_cuerpo": S("PolaroidCuerpo", (0.07, 0.07, 0.075), rough=0.5),
        "pol_frente": S("PolaroidFrente", (0.30, 0.30, 0.31), rough=0.5),
        "pol_lente": S("PolaroidLente", (0.02, 0.02, 0.025), rough=0.1),
        "pol_franja": S("PolaroidFranja", (0.60, 0.12, 0.08), rough=0.5),
        "pol_flash": S("PolaroidFlash", (0.80, 0.80, 0.78), rough=0.2),
        "pol_correa": S("PolaroidCorrea", (0.12, 0.08, 0.05), rough=0.8),
        # lo que brilla (cambia con el estado, ver EMIS)
        "foco": mat_emission("FocoPasillo", (1.0, 0.72, 0.42), 10.0),
        "foco_esc": mat_emission("FocoEscalera", (1.0, 0.72, 0.42), 8.0),
        "fluor_vest": mat_emission("TuboVestibulo", TUBE, 8.0),
        "fluor_t2": mat_emission("TuboTramoCorto", TUBE, 8.0),
        "fluor_cab": mat_emission("PanelCabina", CAB, 0.0),
        "cartel": mat_emission("CartelEscalera", GREEN, 3.0),
        "led": mat_emission("LedAmbar", (1.0, 0.42, 0.08), 6.0),
        "resplandor": mat_emission("ResplandorCalle", (1.0, 0.45, 0.15), 1.2),
        "etiqueta": mat_emission("EtiquetaPlano", (1.0, 0.95, 0.85), 1.5),
    }
    for key, dirty, clean in (("piso", "piso", "piso_l"), ("pared", "pared", "pared_l"),
                              ("techo", "techo", "techo_l"), ("esc_pared", "esc_pared", "esc_pared_l"),
                              ("concreto", "concreto", "concreto_l")):
        SWAPS.append((M[key], T_[dirty], T_[clean]))
    EMIS.update({
        "foco": {"abstinencia": ((1.0, 0.72, 0.42), 10.0), "efecto": ((1.0, 0.78, 0.5), 25.0),
                 "vuelta5": ((1.0, 0.72, 0.42), 0.0)},
        "foco_esc": {"abstinencia": ((1.0, 0.72, 0.42), 8.0), "efecto": ((1.0, 0.78, 0.5), 20.0)},
        "fluor_vest": {"abstinencia": (TUBE, 8.0), "efecto": (TUBE_WARM, 8.0), "vuelta5": (TUBE, 0.0)},
        "fluor_t2": {"abstinencia": (TUBE, 8.0), "efecto": (TUBE_WARM, 8.0), "vuelta5": (TUBE, 5.0)},
        "fluor_cab": {"abstinencia": (CAB, 0.0), "vuelta5": (CAB, 9.0)},
        "resplandor": {"abstinencia": ((1.0, 0.45, 0.15), 1.2), "efecto": (GOLD, 3.0)},
    })
    return M


# ---------------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------------
COLS = {}
CUR = [None]
CAMS = {}
LIGHTS = {}
CEILINGS = []   # se ocultan en el plano
ELEVATOR = {}   # las dos hojas de la puerta del elevador (se abren en la vuelta 5)


def use(name):
    CUR[0] = COLS[name]


def link(ob):
    CUR[0].objects.link(ob)
    return ob


def mover(obs, col):
    """Pasa objetos a otra coleccion (por ejemplo, el numero del 4D a Vuelta1_Fuera)."""
    for ob in obs:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        COLS[col].objects.link(ob)


def wb(axis, n0, n1, u0, u1, z0, z1):
    """Caja de un muro: axis 'x' = el muro corre a lo largo de X (n es Y); 'y' = a lo largo de Y."""
    if axis == "x":
        return (u0, n0, z0), (u1, n1, z1)
    return (n0, u0, z0), (n1, u1, z1)


def WB(axis, u0, u1, n0, n1, z0, z1):
    """Como wb, pero acepta los extremos en cualquier orden."""
    return wb(axis, min(n0, n1), max(n0, n1), min(u0, u1), max(u0, u1), z0, z1)


def P(axis, u, n, z):
    return (u, n, z) if axis == "x" else (n, u, z)


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


def boxes_obj(name, boxes, mat, uv=(1, 1, 1), origin=(0, 0, 0), world_uv=True, rot=None, loc=None,
              normal_mats=()):
    """Un objeto hecho de varias cajas (esquinas en coordenadas de mundo).
    origin: punto que sera el origen del objeto. world_uv: la textura sigue el mundo (continua
    entre muros) o el objeto (puertas, y las escaleras, que tienen que verse iguales).
    normal_mats: [(normal, material)], otro material para las caras que miran hacia ese lado
    (la cara de un muro que da a otro cuarto)."""
    o = Vector(origin)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for mn, mx in boxes:
        mn, mx = Vector(mn) - o, Vector(mx) - o
        c, s = (mn + mx) / 2, mx - mn
        bmesh.ops.create_cube(bm, size=1.0,
                              matrix=Matrix.Translation(c) @ Matrix.Diagonal((s.x, s.y, s.z, 1.0)))
    if normal_mats:
        bm.normal_update()
        for f in bm.faces:
            for i, (n, _) in enumerate(normal_mats):
                if f.normal.dot(Vector(n)) > 0.9:
                    f.material_index = i + 1
                    break
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    for _, m in normal_mats:
        me.materials.append(m)
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


def bar(name, p0, p1, w, h, mat):
    """Barra (caja) de p0 a p1: pasamanos, mangos, palos."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    c = (p0 + p1) / 2
    m = d.to_track_quat("X", "Z").to_matrix().to_4x4() @ Matrix.Diagonal((d.length, w, h, 1.0))
    return mesh_obj(name, lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=m), mat, loc=c)


def blob(name, base, size, mat, rot=(0, 0, 0), flat=0.45, amp=0.3, seed=None):
    """Bulto irregular apoyado en 'base' (bolsas de basura, ropa, plantas)."""
    g = np.random.default_rng(seed) if seed is not None else rng

    def build(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        for v in bm.verts:
            v.co *= 1.0 - amp / 2 + amp * g.random()
            v.co.z = max(v.co.z, -flat)
    loc = (base[0], base[1], base[2] + flat * size[2])
    return mesh_obj(name, build, mat, loc, rot, size)


def flat_poly(name, center, radius, mat, z, seed, n=14, sx=1.0, sy=1.0, down=False):
    """Mancha plana e irregular (en el piso o, con down, en el techo mirando hacia abajo)."""
    g = np.random.default_rng(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = radius * (0.65 + 0.5 * g.random())
        pts.append((center[0] + math.cos(a) * r * sx, center[1] + math.sin(a) * r * sy, z))
    if down:
        pts = pts[::-1]

    def build(bm):
        bm.faces.new([bm.verts.new(p) for p in pts])
    ob = mesh_obj(name, build, mat, uv=None)
    ob.visible_shadow = False
    return ob


def wall_poly(name, axis, nface, nrm, pts_uz, mat, seed=None):
    """Mancha plana pegada a un muro (pts en (u, z)), mirando hacia el pasillo."""
    n = nface + nrm * 0.002
    pts = [P(axis, u, n, z) for u, z in pts_uz]
    # que la cara mire hacia el pasillo
    a, b, c = (Vector(p) for p in pts[:3])
    normal = (b - a).cross(c - a)
    want = Vector((0, nrm, 0)) if axis == "x" else Vector((nrm, 0, 0))
    if normal.dot(want) < 0:
        pts = pts[::-1]

    def build(bm):
        bm.faces.new([bm.verts.new(p) for p in pts])
    ob = mesh_obj(name, build, mat, uv=None)
    ob.visible_shadow = False
    return ob


def empty(name, loc, rot=(0, 0, 0)):
    ob = link(bpy.data.objects.new(name, None))
    ob.location, ob.rotation_euler = loc, rot
    ob.empty_display_size = 0.2
    return ob


def face_rot(axis, nrm):
    """Giro de un texto pegado a un muro, para que se lea desde el pasillo."""
    if axis == "x":   # el muro corre a lo largo de X: el texto mira hacia +Y o -Y
        return (R(90), 0, R(180)) if nrm > 0 else (R(90), 0, 0)
    return (R(90), 0, R(90)) if nrm > 0 else (R(90), 0, R(-90))


def text_obj(name, body, size, mat, loc, rot=(0, 0, 0)):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.resolution_u = 2  # pocas caras: es un letrero de PS1
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    ob.location, ob.rotation_euler = loc, rot
    ob.visible_shadow = False
    return link(ob)


def aim(ob, target):
    ob.rotation_euler = (Vector(target) - Vector(ob.location)).to_track_quat("-Z", "Y").to_euler()


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


def muro(name, axis, n0, n1, u0, u1, vanos, mat, z0=0.0, z1=H, normal_mats=()):
    return boxes_obj(name, wall_pieces(axis, n0, n1, u0, u1, vanos, z0, z1), mat, uv=(2.0, 2.0, H),
                     normal_mats=normal_mats)


def marco_puerta(name, axis, n0, n1, a, b, z0, z1, mat, trim=0.06, d=0.015):
    """Marco de un vano de puerta (sin pieza abajo): tapa el canto del muro y sobresale 'd'."""
    bx = [wb(axis, n0 - d, n1 + d, a - trim, a + 0.01, z0, z1 + trim),
          wb(axis, n0 - d, n1 + d, b - 0.01, b + trim, z0, z1 + trim),
          wb(axis, n0 - d, n1 + d, a - trim, b + trim, z1 - 0.01, z1 + trim)]
    return boxes_obj(name, bx, mat, uv=(0.5, 0.5, 0.5))


def marco_ventana(name, axis, n0, n1, a, b, z0, z1, mat, inside, trim=0.06, d=0.015):
    bx = [wb(axis, n0 - d, n1 + d, a - trim, a + 0.01, z0 - trim, z1 + trim),
          wb(axis, n0 - d, n1 + d, b - 0.01, b + trim, z0 - trim, z1 + trim),
          wb(axis, n0 - d, n1 + d, a - trim, b + trim, z1 - 0.01, z1 + trim),
          wb(axis, n0 - d, n1 + d, a - trim, b + trim, z0 - trim, z0 + 0.01)]
    nn = (n1, n1 + 0.07) if inside > 0 else (n0 - 0.07, n0)
    bx.append(wb(axis, nn[0], nn[1], a - trim - 0.03, b + trim + 0.03, z0 - 0.035, z0 + 0.012))
    return boxes_obj(name, bx, mat, uv=(0.5, 0.5, 0.5))


def puerta(nombre, axis, cara, nrm, u0, u1, M, hoja="puerta", numero=None, mirilla=True, abre=False,
           ajar=0.0, hacia_adentro=True, bisagra=1, alto=DOOR_H, grosor=0.04, marco="marco", muro_t=T,
           z0=0.0, uv=None, mat_numero="numero"):
    """Puerta en el vano de un muro. axis 'x': el muro corre a lo largo de X (n es Y).
    cara: la cara del muro que da al pasillo; nrm: hacia que lado de n queda el pasillo.
    bisagra +1: en u1; -1: en u0. abre: los herrajes y el numero se mueven con la hoja (el
    origen de la hoja esta en la bisagra). ajar: grados abierta, hacia adentro o hacia el pasillo.
    Devuelve la hoja, sus piezas, el numero y el marco."""
    nc = cara - nrm * 0.01              # cara de la hoja que da al pasillo
    nr = nc - nrm * grosor              # la que da adentro
    ub = u1 - 0.005 if bisagra > 0 else u0 + 0.005
    uf = u0 + 0.005 if bisagra > 0 else u1 - 0.005
    um = (u0 + u1) / 2
    hinge = P(axis, ub, nr if hacia_adentro else nc, z0)
    w = u1 - u0
    mn, mx = WB(axis, u0 + 0.005, u1 - 0.005, nc, nr, z0 + 0.02, z0 + alto - 0.005)
    slab = box(nombre, mn, mx, M[hoja], uv=uv or (w, w, alto), pivot=hinge, world_uv=False)
    k = uf + (0.08 if bisagra > 0 else -0.08)
    hw = [(WB(axis, k - 0.03, k + 0.03, nc, nc + nrm * 0.05, z0 + 0.98, z0 + 1.04), M["laton"]),
          (WB(axis, k - 0.03, k + 0.03, nr, nr - nrm * 0.05, z0 + 0.98, z0 + 1.04), M["laton"])]
    if numero:
        hw.append((WB(axis, um - 0.09, um + 0.09, nc, nc + nrm * 0.008, z0 + 1.56, z0 + 1.68), M["laton"]))
    if mirilla:
        hw.append((WB(axis, um - 0.015, um + 0.015, nc, nc + nrm * 0.012, z0 + 1.46, z0 + 1.49), M["laton"]))
    piezas = [box(f"{nombre}_herraje_{i}", a, b, m) for i, ((a, b), m) in enumerate(hw)]
    texto = None
    if numero:
        texto = text_obj(f"{nombre}_numero", numero, 0.075, M[mat_numero],
                         P(axis, um, nc + nrm * 0.0095, z0 + 1.62), face_rot(axis, nrm))
        if abre:
            piezas.append(texto)
    if abre:
        inv = Matrix.Translation(Vector(hinge)).inverted()
        for p in piezas:
            p.parent = slab
            p.matrix_parent_inverse = inv
    s = (nrm if axis == "x" else -nrm) * bisagra * (1 if hacia_adentro else -1)
    slab.rotation_euler.z = R(s * ajar)
    marco_ob = None
    if marco:
        n0, n1 = sorted((cara, cara - nrm * muro_t))
        marco_ob = marco_puerta(nombre + "_marco", axis, n0, n1, u0, u1, z0, z0 + alto, M[marco])
    return dict(hoja=slab, piezas=piezas, texto=texto, marco=marco_ob, hinge=hinge)


def foco_colgante(nombre, x, y, techo, M, mat_foco=None, drop=0.36):
    """Foco colgando del techo: roseta, cable y portalamparas. mat_foco None: sin bombilla."""
    box(nombre + "_roseta", (x - 0.06, y - 0.06, techo - 0.03), (x + 0.06, y + 0.06, techo), M["metal"])
    box(nombre + "_cable", (x - 0.006, y - 0.006, techo - drop + 0.05), (x + 0.006, y + 0.006, techo - 0.03),
        M["negro"])
    box(nombre + "_socket", (x - 0.02, y - 0.02, techo - drop), (x + 0.02, y + 0.02, techo - drop + 0.06),
        M["plastico_negro"])
    if mat_foco is not None:
        bombilla(nombre, x, y, techo, mat_foco, drop)
    return (x, y, techo - drop - 0.11)  # donde va la luz


def bombilla(nombre, x, y, techo, mat, drop=0.36):
    b = mesh_obj(nombre, lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.05), mat,
                 loc=(x, y, techo - drop - 0.04))
    b.visible_shadow = False  # que no tape su propia luz
    return b


def fluorescente(nombre, x, y, a_lo_largo, mat_tubo, M, techo=H):
    """Fluorescente de techo. a_lo_largo: 'x' o 'y', hacia donde va el tubo."""
    if a_lo_largo == "y":
        box(nombre + "_base", (x - 0.06, y - 0.55, techo - 0.04), (x + 0.06, y + 0.55, techo), M["metal_oscuro"])
        t = box(nombre + "_tubo", (x - 0.02, y - 0.5, techo - 0.07), (x + 0.02, y + 0.5, techo - 0.04), mat_tubo)
    else:
        box(nombre + "_base", (x - 0.55, y - 0.06, techo - 0.04), (x + 0.55, y + 0.06, techo), M["metal_oscuro"])
        t = box(nombre + "_tubo", (x - 0.5, y - 0.02, techo - 0.07), (x + 0.5, y + 0.02, techo - 0.04), mat_tubo)
    t.visible_shadow = False


def persiana(nombre, axis, cara, nrm, u0, u1, M, alto=2.0, grosor=0.035, bisagra=1, hacia_adentro=False,
             ajar=0.0, z0=0.0):
    """Puerta de celosia (tablillas inclinadas): desde adentro se ve el pasillo entre las rendijas.
    El origen esta en la bisagra."""
    nc = cara - nrm * 0.01
    nr = nc - nrm * grosor
    ub = u1 - 0.005 if bisagra > 0 else u0 + 0.005
    uf = u0 + 0.005 if bisagra > 0 else u1 - 0.005
    hinge = Vector(P(axis, ub, nr if hacia_adentro else nc, z0))
    nm = (nc + nr) / 2
    a, b = u0 + 0.005, u1 - 0.005
    marcos = [WB(axis, a, a + 0.06, nc, nr, z0 + 0.02, z0 + alto), WB(axis, b - 0.06, b, nc, nr, z0 + 0.02, z0 + alto),
              WB(axis, a, b, nc, nr, z0 + 0.02, z0 + 0.17), WB(axis, a, b, nc, nr, z0 + alto - 0.1, z0 + alto),
              WB(axis, a, b, nc, nr, z0 + 0.99, z0 + 1.07)]
    tilt = Matrix.Rotation(R(30 * nrm), 4, "X" if axis == "x" else "Y")

    def build(bm):
        for mn, mx in marcos:
            mn, mx = Vector(mn) - hinge, Vector(mx) - hinge
            c, s = (mn + mx) / 2, mx - mn
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*s, 1.0)))
        for z_a, z_b in ((0.2, 0.96), (1.1, alto - 0.13)):
            z = z0 + z_a
            while z < z0 + z_b:
                c = Vector(P(axis, (a + b) / 2, nm, z)) - hinge
                L = b - a - 0.1
                size = (L, 0.045, 0.008) if axis == "x" else (0.045, L, 0.008)
                bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(c) @ tilt @ Matrix.Diagonal((*size, 1.0)))
                z += 0.05
    slab = mesh_obj(nombre, build, M["persiana"], loc=hinge)
    k = uf + (0.08 if bisagra > 0 else -0.08)
    inv = Matrix.Translation(hinge).inverted()
    for i, (n0, n1) in enumerate(((nc, nc + nrm * 0.05), (nr, nr - nrm * 0.05))):
        kn = box(f"{nombre}_manija_{i}", *WB(axis, k - 0.025, k + 0.025, n0, n1, z0 + 1.0, z0 + 1.06), M["laton"])
        kn.parent = slab
        kn.matrix_parent_inverse = inv
    s = (nrm if axis == "x" else -nrm) * bisagra * (1 if hacia_adentro else -1)
    slab.rotation_euler.z = R(s * ajar)
    return slab


# ---------------------------------------------------------------------------
# El pasillo
# ---------------------------------------------------------------------------
# Puertas de los departamentos: (nombre, muro, u0, u1)
PUERTAS_NORTE = [("4D", 8.2, 9.1), ("4F", 11.4, 12.3)]
PUERTAS_SUR = [("4A", 5.0, 5.9), ("4C", 9.6, 10.5), ("4E", 13.6, 14.5)]
ASCENSOR = (-1.64, -0.44)      # el vano del elevador, en la pared final (en y)
LIMPIEZA = (-4.9, -4.1)        # la puerta del cuarto de limpieza, en la misma pared
X4C = (8.4, 11.7)              # el 4C por dentro (en x); va de YS - T hasta -5.0


def pasillo(M):
    use("Estructura")
    # Pisos y techos por tramos (piezas sueltas: modulares, y cada una con pocas luces cerca)
    cortes = [XB, 4.8, 8.8, 12.8, X2A, XE]
    for i, (a, b) in enumerate(zip(cortes, cortes[1:])):
        box(f"piso_largo_{i + 1}", (a, YS, -0.1), (b, YN, 0.0), M["piso"], uv=(2, 2, 2))
        CEILINGS.append(box(f"techo_largo_{i + 1}", (a, YS, H), (b, YN, H + 0.1), M["techo"], uv=(2, 2, 2)))
    for i, (a, b) in enumerate(((YS, -5.0), (-5.0, YT2))):
        box(f"piso_corto_{i + 1}", (X2A, b, -0.1), (XE, a, 0.0), M["piso"], uv=(2, 2, 2))
        CEILINGS.append(box(f"techo_corto_{i + 1}", (X2A, b, H), (XE, a, H + 0.1), M["techo"], uv=(2, 2, 2)))

    # Muro norte: una piel delante del muro del 4B (que en Unity esta detras) y despues sigue sola
    vanos_n = [(3.0, 3.9, 0.0, DOOR_H)] + [(a, b, 0.0, DOOR_H) for _, a, b in PUERTAS_NORTE]
    for i, (a, b) in enumerate(zip([XB - T, 4.8, 8.8, 12.8, X2A], [4.8, 8.8, 12.8, X2A, XE + T])):
        muro(f"muro_norte_{i + 1}", "x", YN, YN + 0.04, a, b, vanos_n, M["pared"])
    muro("muro_fondo", "y", XB - T, XB, YS, YN, [], M["pared"])
    # Muro sur: de la escalera A (que pone su propio muro) a la esquina. Detras del 4C, su papel.
    vanos_s = [(a, b, 0.0, DOOR_H) for _, a, b in PUERTAS_SUR]
    x_esc = O_A.x + 1.3
    for i, (a, b) in enumerate(((x_esc, 4.8), (4.8, X4C[0]), X4C, (X4C[1], X2A))):
        nm = [((0, -1, 0), M["pared_4c"])] if (a, b) == X4C else ()
        muro(f"muro_sur_{i + 1}", "x", YS - T, YS, a, b, vanos_s, M["pared"], normal_mats=nm)
    # Pared final (la del elevador) y muro oeste del tramo corto
    muro("muro_final_1", "y", XE, XE + T, YS, YN, [(*ASCENSOR, 0.0, 2.2)], M["pared"])
    muro("muro_final_2", "y", XE, XE + T, -5.0, YS, [(*LIMPIEZA, 0.0, 2.0)], M["pared"],
         normal_mats=[((1, 0, 0), M["esc_pared"])])
    muro("muro_final_3", "y", XE, XE + T, YT2, -5.0, [], M["pared"])
    muro("muro_oeste_corto_1", "y", X2A - T, X2A, -5.0, YS - T, [], M["pared"])
    muro("muro_oeste_corto_2", "y", X2A - T, X2A, YT2, -5.0, [], M["pared"])

    # Umbrales (el piso dentro de cada vano)
    umb = [((3.0, YN, -0.1), (3.9, 0.0, 0.005))]
    umb += [((a, YN, -0.1), (b, YN + 0.04, 0.005)) for _, a, b in PUERTAS_NORTE]
    umb += [((a, YS - T, -0.1), (b, YS, 0.005)) for _, a, b in PUERTAS_SUR]
    umb += [((XE, LIMPIEZA[0], -0.1), (XE + T, LIMPIEZA[1], 0.005))]
    boxes_obj("umbrales", umb, M["umbral"], uv=(0.5, 0.5, 0.5))

    # Puertas de los departamentos. El 4C esta entreabierto: es el escondite.
    marco_puerta("marco_4b", "x", YN, YN + 0.04, 3.0, 3.9, 0.0, DOOR_H, M["marco"])
    puertas = {}
    for num, a, b in PUERTAS_NORTE:
        puertas[num] = puerta(f"puerta_{num.lower()}", "x", YN, -1, a, b, M, numero=num, muro_t=0.04)
    for num, a, b in PUERTAS_SUR:
        abre = num == "4C"
        puertas[num] = puerta(f"puerta_{num.lower()}", "x", YS, 1, a, b, M, numero=num, abre=abre,
                              ajar=25.0 if abre else 0.0)
    # Doña Carmen (4A): una estampita de la Virgen sobre el numero
    box("estampita_4a", (5.41, YS - 0.01, 1.73), (5.49, YS - 0.006, 1.84), M["estampita"])

    # Vuelta 1: la puerta del 4D tambien dice 4B
    mover([puertas["4D"]["texto"]], "Vuelta1_Fuera")
    use("Vuelta1")
    t = puertas["4D"]["texto"]
    text_obj("puerta_4d_numero_4b", "4B", 0.075, M["numero"], tuple(t.location), tuple(t.rotation_euler))
    return puertas


def tuberias(M):
    use("Objetos")
    for name, y, z, r in (("tubo_a", YN - 0.14, 2.47, 0.05), ("tubo_b", YN - 0.28, 2.52, 0.03)):
        cyl(name, (XB, y, z), r, XE - XB, M["metal"], rot=(0, R(90), 0))
    for i, x in enumerate(np.arange(2.0, XE, 2.5)):
        box(f"abrazadera_{i}", (x - 0.02, YN - 0.33, 2.5), (x + 0.02, YN - 0.09, H), M["metal_oscuro"])


def luces_del_pasillo(M):
    """Focos alternados (charcos de luz y zonas negras) y los fluorescentes."""
    use("Objetos")
    pos = {}
    for i, x in enumerate((3.8, 7.8, 11.8, 15.8)):
        encendido = i in (0, 2)
        pos[i + 1] = foco_colgante(f"foco_{i + 1}", x, YC, H, M, M["foco"] if encendido else None)
        if not encendido:  # quemado en la abstinencia, prendido bajo el efecto
            use("Deterioro")
            bombilla(f"foco_{i + 1}_quemado", x, YC, H, M["foco_quemado"])
            use("Efecto")
            bombilla(f"foco_{i + 1}_efecto", x, YC, H, M["foco"])
            use("Objetos")
    fluorescente("fluor_vestibulo", 17.1, YC, "y", M["fluor_vest"], M)
    fluorescente("fluor_corto", (X2A + XE) / 2, -5.0, "x", M["fluor_t2"], M)
    return pos


def ascensor(M):
    """El elevador: marco, dos hojas que se corren, la cabina, el indicador y el boton."""
    use("Estructura")
    y0, y1 = ASCENSOR
    marco_puerta("ascensor_marco", "y", XE, XE + T, y0, y1, 0.0, 2.2, M["metal_oscuro"], trim=0.08)
    box("ascensor_umbral", (XE, y0, -0.1), (XE + 0.15, y1, 0.008), M["aluminio"])
    use("Objetos")
    ym = (y0 + y1) / 2
    for lado, a, b in (("sur", y0, ym - 0.004), ("norte", ym + 0.004, y1)):
        ELEVATOR[lado] = box(f"ascensor_hoja_{lado}", (XE + 0.03, a, 0.0), (XE + 0.06, b, 2.18), M["metal"],
                             uv=(0.5, 0.5, 0.5), world_uv=False)
    # Un papel pegado en la hoja norte: NO FUNCIONA
    hoja = ELEVATOR["norte"]
    papel = box("ascensor_papel", (XE + 0.025, ym + 0.12, 1.30), (XE + 0.03, ym + 0.33, 1.58), M["papel"])
    letras = text_obj("ascensor_papel_texto", "NO\nFUNCIONA", 0.035, M["numero"], (XE + 0.024, ym + 0.225, 1.45),
                      face_rot("y", -1))
    for p in (papel, letras):
        p.parent = hoja
        p.matrix_parent_inverse = Matrix.Translation(hoja.location).inverted()
    # Indicador del piso y boton de llamada
    box("ascensor_indicador", (XE - 0.03, YC - 0.18, 2.33), (XE, YC + 0.18, 2.50), M["negro"])
    text_obj("ascensor_indicador_numero", "4", 0.11, M["led"], (XE - 0.032, YC, 2.415), face_rot("y", -1))
    box("ascensor_botonera", (XE - 0.03, -0.33, 1.0), (XE, -0.23, 1.25), M["metal_oscuro"])
    box("ascensor_boton", (XE - 0.045, -0.295, 1.10), (XE - 0.03, -0.265, 1.13), M["led"])

    # La cabina, detras de la pared
    use("Estructura")
    cx0, cx1, cy0, cy1, ch = XE + T + 0.05, XE + T + 1.55, -1.79, -0.29, 2.3
    muro("cabina_frente", "y", XE + T, cx0, cy0 - T, cy1 + T, [(y0, y1, 0.0, 2.2)], M["acero"], z1=ch)
    boxes_obj("cabina_muros", [((cx1, cy0 - T, 0.0), (cx1 + T, cy1 + T, ch)),
                               ((cx0, cy0 - T, 0.0), (cx1, cy0, ch)),
                               ((cx0, cy1, 0.0), (cx1, cy1 + T, ch))], M["acero"], uv=(1, 1, 2))
    box("cabina_piso", (XE + T, cy0, -0.1), (cx1, cy1, 0.0), M["goma"], uv=(0.5, 0.5, 0.5))
    CEILINGS.append(box("cabina_techo", (XE + T, cy0 - T, ch), (cx1 + T, cy1 + T, ch + 0.1), M["metal_oscuro"]))
    use("Objetos")
    panel = box("cabina_panel_luz", (cx0 + 0.4, YC - 0.26, ch - 0.02), (cx1 - 0.4, YC + 0.26, ch), M["fluor_cab"])
    panel.visible_shadow = False
    bar("cabina_pasamanos", (cx1 - 0.05, cy0 + 0.2, 0.9), (cx1 - 0.05, cy1 - 0.2, 0.9), 0.03, 0.03, M["aluminio"])
    # Botonera de adentro: 6 al 1, PB y uno sin numero (el piso que no deberia existir)
    box("cabina_botonera", (cx0 + 0.08, cy1 - 0.02, 0.95), (cx0 + 0.28, cy1, 1.62), M["acero"])
    for i, label in enumerate(("6", "5", "4", "3", "2", "1", "PB", "")):
        z = 1.53 - i * 0.075
        box(f"cabina_boton_{i}", (cx0 + 0.13, cy1 - 0.03, z), (cx0 + 0.16, cy1 - 0.02, z + 0.03), M["boton"])
        if label:
            text_obj(f"cabina_boton_{i}_numero", label, 0.028, M["numero"], (cx0 + 0.215, cy1 - 0.021, z + 0.015),
                     face_rot("x", -1))
    box("cabina_indicador", (cx0, YC - 0.1, 2.21), (cx0 + 0.02, YC + 0.1, 2.28), M["negro"])
    text_obj("cabina_indicador_numero", "4", 0.05, M["led"], (cx0 + 0.021, YC, 2.245), face_rot("y", 1))


def telefono(M):
    """El telefono publico, junto al elevador, con su repisa y el PISO 4 pintado."""
    use("Objetos")
    x0, x1 = 16.2, 16.42
    box("telefono_caja", (x0, YN - 0.09, 1.2), (x1, YN, 1.55), M["plastico_rojo"])
    box("telefono_gancho", (x0 - 0.02, YN - 0.06, 1.47), (x0, YN - 0.03, 1.5), M["metal_oscuro"])
    box("telefono_auricular", (x0 - 0.06, YN - 0.08, 1.23), (x0 - 0.02, YN - 0.03, 1.48), M["plastico_negro"])
    bar("telefono_cable", (x0 - 0.04, YN - 0.055, 1.23), (x0 + 0.02, YN - 0.07, 1.12), 0.012, 0.012,
        M["plastico_negro"])
    cyl("telefono_disco", (0.5 * (x0 + x1), YN - 0.09, 1.40), 0.045, 0.012, M["metal_oscuro"], rot=(R(90), 0, 0),
        seg=10)
    box("telefono_ranura", (x0 + 0.08, YN - 0.095, 1.5), (x0 + 0.14, YN - 0.09, 1.515), M["metal_oscuro"])
    box("telefono_repisa", (x0 - 0.12, YN - 0.22, 1.0), (x1 + 0.1, YN, 1.02), M["metal_oscuro"])
    for i, x in enumerate((x0 - 0.08, x1 + 0.06)):
        box(f"telefono_mensula_{i}", (x - 0.01, YN - 0.18, 0.86), (x + 0.01, YN, 1.0), M["metal_oscuro"])
    box("telefono_directorio", (x1 - 0.06, YN - 0.18, 1.02), (x1 + 0.08, YN - 0.04, 1.05), M["directorio"])
    text_obj("piso_pintado", "PISO 4", 0.16, M["pintura_roja"], (15.65, YN - 0.002, 1.72), face_rot("x", -1))
    return (x0 + 0.03, YN - 0.12, 1.02)  # donde va la Polaroid en la vuelta 3


def polaroid(M, loc, yaw):
    """La camara de Tomas (como en tomas.py), parada en la repisa, mirando al pasillo."""
    me = bpy.data.meshes.new("Polaroid")
    bm = bmesh.new()

    def add_box(mn, mx, mi):
        mn, mx = Vector(mn), Vector(mx)
        c, s = (mn + mx) / 2, mx - mn
        r = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(c) @ Matrix.Diagonal((s.x, s.y, s.z, 1)))
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi

    add_box((-0.058, -0.03, 0.0), (0.058, 0.03, 0.097), 0)        # cuerpo
    add_box((-0.050, -0.035, 0.007), (0.050, -0.03, 0.050), 1)     # frente claro
    add_box((-0.050, -0.036, 0.061), (0.050, -0.032, 0.067), 3)    # franja de color
    add_box((-0.042, -0.035, 0.075), (-0.012, -0.03, 0.091), 4)    # flash
    lens = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.022, radius2=0.022, depth=0.014,
                                 matrix=Matrix.Translation((0.012, -0.04, 0.03)) @ Matrix.Rotation(R(90), 4, "X"))
    for f in {f for v in lens["verts"] for f in v.link_faces}:
        f.material_index = 2
    for a, b in (((0.05, 0.0, 0.09), (0.09, 0.05, 0.004)), ((0.09, 0.05, 0.004), (0.02, 0.1, 0.004)),
                 ((0.02, 0.1, 0.004), (-0.07, 0.07, 0.004)), ((-0.07, 0.07, 0.004), (-0.05, 0.0, 0.09))):
        a, b = Vector(a), Vector(b)
        d = b - a
        m = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Y", "Z").to_matrix().to_4x4() \
            @ Matrix.Diagonal((0.014, d.length + 0.006, 0.004, 1))
        r = bmesh.ops.create_cube(bm, size=1.0, matrix=m)
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = 5
    bm.to_mesh(me)
    bm.free()
    for key in ("pol_cuerpo", "pol_frente", "pol_lente", "pol_franja", "pol_flash", "pol_correa"):
        me.materials.append(M[key])
    ob = link(bpy.data.objects.new("Polaroid", me))
    ob.location, ob.rotation_euler = loc, (0, 0, R(yaw))
    return ob


def cuarto_limpieza(M):
    """Detras de la puerta de celosia del tramo corto: el escondite de la vuelta 5."""
    use("Estructura")
    x0, x1, y0, y1 = XE + T, XE + T + 1.0, -5.0, -4.0
    boxes_obj("limpieza_muros", [((x1, y0 - T, 0.0), (x1 + T, y1 + T, H)), ((x0, y0 - T, 0.0), (x1, y0, H)),
                                 ((x0, y1, 0.0), (x1, y1 + T, H))], M["esc_pared"], uv=(2, 2, H))
    box("limpieza_piso", (x0, y0, -0.1), (x1, y1, 0.0), M["concreto"], uv=(1, 1, 1))
    CEILINGS.append(box("limpieza_techo", (x0, y0 - T, H), (x1 + T, y1 + T, H + 0.1), M["techo"], uv=(2, 2, 2)))
    marco_puerta("limpieza_marco", "y", XE, XE + T, *LIMPIEZA, 0.0, 2.0, M["marco"])
    persiana("puerta_limpieza", "y", XE, -1, *LIMPIEZA, M, alto=2.0, ajar=8.0)

    use("Objetos")
    for i, z in enumerate((1.25, 1.65)):
        box(f"limpieza_repisa_{i}", (x1 - 0.28, y0 + 0.03, z), (x1, y1 - 0.03, z + 0.02), M["ropero"])
    g = np.random.default_rng(7)
    for i in range(6):
        z = 1.27 if i < 3 else 1.67
        y = y0 + 0.15 + (i % 3) * 0.3 + g.uniform(-0.05, 0.05)
        kind = g.integers(0, 3)
        if kind == 0:
            cyl(f"limpieza_lata_{i}", (x1 - 0.14, y, z), 0.04, 0.12, M["lata"])
        else:
            cyl(f"limpieza_botella_{i}", (x1 - 0.14, y, z), 0.035, 0.24,
                M["botella_azul"] if kind == 1 else M["botella_blanca"], seg=6)
    cyl("limpieza_balde", (x1 - 0.25, y0 + 0.22, 0.0), 0.15, 0.28, M["balde"], r2=0.17, seg=10)
    blob("limpieza_trapeador", (x1 - 0.25, y0 + 0.22, 0.2), (0.12, 0.12, 0.08), M["trapeador"], seed=3)
    bar("limpieza_mango", (x1 - 0.25, y0 + 0.22, 0.2), (x1 - 0.06, y0 + 0.06, 1.5), 0.025, 0.025, M["mango"])
    bar("limpieza_escoba_palo", (x1 - 0.06, y1 - 0.08, 0.12), (x1 - 0.04, y1 - 0.2, 1.35), 0.025, 0.025, M["mango"])
    box("limpieza_escoba", (x1 - 0.12, y1 - 0.2, 0.0), (x1 - 0.02, y1 - 0.04, 0.14), M["trapeador"])
    box("limpieza_fusibles", (x0 + 0.35, y1 - 0.06, 1.3), (x0 + 0.65, y1, 1.7), M["metal_oscuro"])
    for i, x in enumerate((x0 + 0.42, x0 + 0.5, x0 + 0.58)):
        box(f"limpieza_cable_{i}", (x - 0.008, y1 - 0.03, 1.7), (x + 0.008, y1 - 0.015, H), M["negro"])
    foco_colgante("limpieza_foco", x0 + 0.45, (y0 + y1) / 2, H, M, None, drop=0.3)


def departamento_4c(M):
    """El 4C, vacio: un cuarto con un ropero (escondite), muebles tapados y la ventana con tablas."""
    use("Departamento4C")
    x0, x1 = X4C
    y0, y1 = -5.0, YS - T
    ventana = (9.5, 10.7, 0.9, 2.1)
    boxes_obj("4c_muros", [((x0 - T, y0 - T, 0.0), (x0, y1, H)), ((x1, y0 - T, 0.0), (x1 + T, y1, H))],
              M["pared_4c"], uv=(2, 2, H))
    muro("4c_muro_sur", "x", y0 - T, y0, x0, x1, [ventana], M["pared_4c"])
    box("4c_piso", (x0, y0, -0.1), (x1, y1, 0.0), M["piso_4c"], uv=(2, 2, 2))
    CEILINGS.append(box("4c_techo", (x0 - T, y0 - T, H), (x1 + T, y1, H + 0.1), M["techo"], uv=(2, 2, 2)))
    marco_ventana("4c_ventana_marco", "x", y0 - T, y0, *ventana, M["marco"], inside=1)
    # Tablas clavadas por dentro, con rendijas por donde entra la luz de la calle
    for i, (z, tilt) in enumerate(((1.02, 3), (1.34, -2), (1.66, 4), (1.97, -3))):
        c = Vector((10.1, y0 + 0.03, z))
        m = Matrix.Rotation(R(tilt), 4, "Y") @ Matrix.Diagonal((1.45, 0.025, 0.17, 1.0))
        mesh_obj(f"4c_tabla_{i}", lambda bm, m=m: bmesh.ops.create_cube(bm, size=1.0, matrix=m), M["tabla"], loc=c)
    r = box("4c_resplandor", (9.4, y0 - 0.32, 0.8), (10.8, y0 - 0.3, 2.2), M["resplandor"])
    r.visible_shadow = False
    # El ropero contra la pared oeste: hueco por dentro, una puerta entreabierta
    rx0, rx1, ry0, ry1, rh = x0, x0 + 0.6, -3.9, -2.7, 2.0
    boxes_obj("4c_ropero", [((rx0, ry0, 0.0), (rx0 + 0.03, ry1, rh)), ((rx0, ry0, 0.0), (rx1, ry0 + 0.03, rh)),
                            ((rx0, ry1 - 0.03, 0.0), (rx1, ry1, rh)), ((rx0, ry0, rh - 0.03), (rx1, ry1, rh)),
                            ((rx0, ry0, 0.0), (rx1, ry1, 0.08))], M["ropero"], uv=(0.5, 0.5, 0.5))
    bar("4c_ropero_barra", (rx0 + 0.3, ry0 + 0.03, 1.75), (rx0 + 0.3, ry1 - 0.03, 1.75), 0.02, 0.02, M["metal_oscuro"])
    ym = (ry0 + ry1) / 2
    for lado, a, b, hinge_y, ang in (("izq", ry0 + 0.03, ym, ry0 + 0.03, -4.0), ("der", ym, ry1 - 0.03, ry1 - 0.03, 22.0)):
        hoja = box(f"4c_ropero_puerta_{lado}", (rx1 - 0.025, a, 0.08), (rx1, b, rh - 0.03), M["ropero"],
                   pivot=(rx1, hinge_y, 0.0), world_uv=False)
        ky = b - 0.05 if lado == "izq" else a + 0.05
        k = box(f"4c_ropero_manija_{lado}", (rx1, ky - 0.01, 1.0), (rx1 + 0.02, ky + 0.01, 1.08), M["laton"])
        k.parent = hoja
        k.matrix_parent_inverse = Matrix.Translation((rx1, hinge_y, 0.0)).inverted()
        hoja.rotation_euler.z = R(ang)
    # Muebles tapados con sabanas, cajas, un cuadro caido
    blob("4c_sillon_tapado", (10.95, -4.35, 0.0), (0.48, 0.42, 0.52), M["sabana"], flat=0.6, amp=0.15, seed=11)
    box("4c_mesa_tapada", (9.9, -3.0, 0.0), (10.9, -2.45, 0.74), M["sabana"])
    for i, (x, y, z, s) in enumerate(((11.35, -3.6, 0.0, 0.45), (11.35, -3.6, 0.45, 0.38), (11.3, -3.05, 0.0, 0.4))):
        box(f"4c_caja_{i}", (x - s / 2, y - s / 2, z), (x + s / 2, y + s / 2, z + s * 0.9), M["carton"])
    c = Vector((x1 - 0.06, -4.4, 0.32))
    m = Matrix.Rotation(R(-12), 4, "Y") @ Matrix.Diagonal((0.03, 0.55, 0.42, 1.0))
    mesh_obj("4c_cuadro_caido", lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=m), M["cuadro_marco"], loc=c)
    foco_colgante("4c_socket", 10.05, -3.5, H, M, None)
    for i, (x, y, yaw) in enumerate(((9.3, -4.3, 20), (10.4, -3.8, -35))):
        box(f"4c_periodico_{i}", (x - 0.19, y - 0.14, 0.0), (x + 0.19, y + 0.14, 0.006), M["papel"],
            rot=(0, 0, R(yaw)))


def escalera(letra, O, M):
    """Una escalera en U entre dos pisos. Las dos (A y B) son iguales: mismas piezas, mismas
    texturas (pegadas a la escalera, no al mundo) y mismas luces, para que el salto no se note.
    Origen: el centro de las puertas, en la cara del muro que da a la escalera. La puerta de
    arriba esta en z = 0 y la de abajo en z = -2.6 (relativo al origen)."""
    col = "Escalera" + letra
    use(col)
    p = f"esc{letra}_"
    ox, oy, oz = O
    tread, rise = 1.9 / 7, 1.3 / 8

    def W(x, y, z):
        return (ox + x, oy + y, oz + z)

    def cajas(name, bxs, mat, uv=(2, 2, H)):
        return boxes_obj(p + name, [(W(*a), W(*b)) for a, b in bxs], mat, uv=uv, origin=O, world_uv=False)

    empty(f"Escalera{letra}_ancla", O)
    # Muro de las puertas: por dentro la pintura de la escalera; por fuera el papel del pasillo,
    # pegado al mundo para que siga al de los muros vecinos
    vanos = [(ox - 0.45, ox + 0.45, oz, oz + DOOR_H), (ox - 0.45, ox + 0.45, oz - H, oz - H + DOOR_H)]
    boxes_obj(p + "muro_puertas", wall_pieces("x", oy, oy + 0.05, ox - 1.3, ox + 1.3, vanos, oz - H, oz + H),
              M["esc_pared"], uv=(2, 2, H), origin=O, world_uv=False)
    boxes_obj(p + "muro_puertas_pasillo", wall_pieces("x", oy + 0.05, oy + T, ox - 1.3, ox + 1.3, vanos, oz - H, oz + H),
              M["pared"], uv=(2, 2, H))
    cajas("muros", [((-1.3, -4.4, -H - 0.1), (-1.2, 0.0, H + 0.1)), ((1.2, -4.4, -H - 0.1), (1.3, 0.0, H + 0.1)),
                    ((-1.2, -4.4, -H - 0.1), (1.2, -4.3, H + 0.1))], M["esc_pared"])
    cajas("piso", [((-1.2, -4.3, -H - 0.1), (1.2, T, -H))], M["concreto"], uv=(1, 1, 1))
    techo = cajas("techo", [((-1.2, -4.3, H), (1.2, 0.0, H + 0.1))], M["techo"], uv=(2, 2, 2))
    CEILINGS.append(techo)
    cajas("umbrales", [((-0.45, 0.0, -0.02), (0.45, T, 0.01)), ((-0.45, 0.0, -H - 0.02), (0.45, T, -H + 0.01))],
          M["umbral"], uv=(0.5, 0.5, 0.5))
    # Rellano de arriba, descanso y los dos tramos (macizos hasta el piso de abajo)
    cajas("rellano", [((-1.2, -1.2, -0.15), (1.2, 0.0, 0.0))], M["concreto"], uv=(1, 1, 1))
    cajas("descanso", [((-1.2, -4.3, -H), (1.2, -3.1, -1.3))], M["concreto"], uv=(1, 1, 1))
    cajas("tramo_1", [((-1.2, -1.2 - k * tread, -H), (-0.06, -1.2 - (k - 1) * tread, -k * rise)) for k in range(1, 8)],
          M["concreto"], uv=(1, 1, 1))
    cajas("tramo_2", [((0.06, -3.1 + (k - 1) * tread, -H), (1.2, -3.1 + k * tread, -1.3 - k * rise))
                      for k in range(1, 8)], M["concreto"], uv=(1, 1, 1))
    cajas("muro_central", [((-0.06, -3.1, -H), (0.06, -1.2, H))], M["esc_pared"])
    # Baranda sobre el hueco del tramo 2 y pasamanos en los muros
    cajas("baranda", [((0.06, -1.23, 0.9), (1.2, -1.17, 0.95))] +
          [((x - 0.015, -1.215, 0.0), (x + 0.015, -1.185, 0.9)) for x in (0.12, 0.62, 1.15)],
          M["pasamanos"], uv=(0.5, 0.5, 0.5))
    bar(p + "pasamanos_1", W(-1.16, -1.1, 0.9), W(-1.16, -3.2, -1.3 + 0.9), 0.04, 0.04, M["pasamanos"])
    bar(p + "pasamanos_2", W(1.16, -3.2, -1.3 + 0.9), W(1.16, -1.1, -H + 0.9), 0.04, 0.04, M["pasamanos"])
    # Luces: un foco en el rellano de arriba y una lampara con jaula en el descanso
    luz_rellano = foco_colgante(p + "foco", ox, oy - 0.6, oz + H, M, M["foco_esc"])
    cajas("lampara_base", [((-0.07, -4.3, 0.72), (0.07, -4.26, 0.86))], M["metal_oscuro"], uv=(0.5, 0.5, 0.5))
    b = bombilla(p + "lampara", ox, oy - 4.17, oz + 0.79 + 0.36 + 0.04, M["foco_esc"])
    b.location = W(0.0, -4.17, 0.79)
    cajas("lampara_jaula", [((sx * 0.06 - 0.004, -4.26, 0.72), (sx * 0.06 + 0.004, -4.1, 0.73)) for sx in (-1, 1)] +
          [((sx * 0.06 - 0.004, -4.11, 0.72), (sx * 0.06 + 0.004, -4.10, 0.87)) for sx in (-1, 1)] +
          [((-0.064, -4.26, 0.865), (0.064, -4.1, 0.875))], M["metal_oscuro"], uv=(0.5, 0.5, 0.5))
    foco_colgante(p + "foco_abajo", ox, oy - 0.6, oz - 0.15, M, M["foco_esc"], drop=0.25)
    # PISO 4 pintado junto a las dos puertas (y un 4 grande en el descanso)
    for nivel, zz in (("arriba", 0.0), ("abajo", -H)):
        text_obj(f"{p}piso_{nivel}", "PISO 4", 0.15, M["pintura_roja"], W(0.86, -0.002, zz + 1.55), face_rot("x", -1))
    text_obj(p + "cuatro", "4", 0.45, M["pintura_roja"], W(0.62, -4.298, -1.3 + 1.5), face_rot("x", 1))
    # Las dos puertas (abren hacia la escalera) y el cartel verde sobre cada una, del lado del pasillo
    puertas = {}
    for nivel, zz in (("arriba", 0.0), ("abajo", -H)):
        d = puerta(f"{p}puerta_{nivel}", "x", oy + T, 1, ox - 0.45, ox + 0.45, M, hoja="puerta_esc", mirilla=False,
                   abre=True, z0=oz + zz, uv=(0.5, 0.5, 0.5))
        cartel = cajas(f"cartel_{nivel}", [((-0.3, T, zz + 2.2), (0.3, T + 0.03, zz + 2.38))], M["cartel"],
                       uv=(0.5, 0.5, 0.5))
        letras = text_obj(f"{p}cartel_{nivel}_texto", "ESCALERA", 0.075, M["numero"], W(0.0, T + 0.031, zz + 2.29),
                          face_rot("x", 1))
        d["cartel"] = [cartel, letras]
        puertas[nivel] = d
    # Basura (igual en las dos)
    use("Deterioro")
    cyl(p + "lata_aplastada", W(0.85, -3.85, -1.3), 0.033, 0.05, M["lata"], rot=(R(90), 0, R(30)))
    box(p + "cajetilla", W(-0.35, -0.55, -H), W(-0.27, -0.5, -H + 0.02), M["papel"])
    flat_poly(p + "mancha", W(0.4, -0.7, 0.0)[:2], 0.25, M["mancha"], oz - H + 0.002, seed=5)
    use(col)
    return puertas


def fachada_4b(M):
    """Solo para los renders: el muro y la puerta del 4B vistos desde el pasillo (en Unity
    estan los del 4B)."""
    use("Fachada4B")
    muro("fachada_4b_muro", "x", -0.1, 0.0, XB - T, 7.3, [(3.0, 3.9, 0.0, DOOR_H)], M["pared"])
    puerta("fachada_4b_puerta", "x", -0.05, -1, 3.0, 3.9, M, numero="4B", bisagra=-1, marco=None)


def deterioro_y_efecto(M):
    use("Deterioro")
    g = np.random.default_rng(21)
    blob("bolsa_basura", (14.75, -1.62, 0.0), (0.26, 0.24, 0.27), M["bolsa"], seed=1)
    blob("bolsa_basura_2", (15.15, -1.7, 0.0), (0.21, 0.2, 0.2), M["bolsa"], seed=2)
    blob("bolsa_basura_3", (X2A + 0.3, -7.6, 0.0), (0.22, 0.2, 0.22), M["bolsa"], seed=4)
    for i in range(7):
        x = float(g.uniform(2.5, 16.5))
        y = float(g.uniform(YS + 0.3, YN - 0.3))
        box(f"periodico_{i}", (x - 0.19, y - 0.14, 0.0), (x + 0.19, y + 0.14, 0.006), M["papel"],
            rot=(0, 0, float(g.uniform(0, math.pi))))
    flat_poly("mancha_piso", (9.2, -1.3), 0.35, M["mancha"], 0.003, seed=8, sy=1.5)
    flat_poly("mancha_piso_2", (16.7, -6.4), 0.3, M["mancha"], 0.003, seed=9, sx=1.4)
    for i in range(5):
        x, y = float(g.uniform(15.5, 17.4)), float(g.uniform(-1.8, -0.4))
        bar(f"colilla_{i}", (x, y, 0.006), (x + 0.03, y + 0.01, 0.006), 0.008, 0.008, M["papel"])
    # La planta del vestibulo: seca en la abstinencia, viva bajo el efecto
    for col, hojas in (("Deterioro", "planta_seca"), ("Efecto", "planta")):
        use(col)
        sfx = "_seca" if col == "Deterioro" else ""
        cyl(f"maceta{sfx}", (15.15, YN - 0.25, 0.0), 0.13, 0.3, M["maceta"], r2=0.16, seg=8)
        cyl(f"maceta_tierra{sfx}", (15.15, YN - 0.25, 0.26), 0.15, 0.02, M["tierra"], seg=8)
        if col == "Efecto":
            for i, (dx, dy, s) in enumerate(((0, 0, 0.22), (0.08, 0.05, 0.16), (-0.07, -0.04, 0.17))):
                blob(f"planta_hojas_{i}", (15.15 + dx, YN - 0.25 + dy, 0.3 + i * 0.12), (s, s, s * 1.2), M["planta"],
                     seed=30 + i)
        else:
            for i, (dx, dy, lean) in enumerate(((0.04, 0.0, 25), (-0.03, 0.04, -30), (0.0, -0.05, 10))):
                a = (15.15 + dx, YN - 0.25 + dy, 0.28)
                b = (a[0] + 0.25 * math.sin(R(lean)), a[1] + 0.1, 0.62 - abs(lean) / 200)
                bar(f"planta_tallo_{i}", a, b, 0.012, 0.012, M["planta_seca"])
    # Bajo el efecto: tapetes, un cuadro entre el 4D y el 4F
    use("Efecto")
    box("tapete_4a", (5.1, YS + 0.05, 0.0), (5.8, YS + 0.5, 0.012), M["tapete"])
    box("tapete_4d", (8.3, YN - 0.5, 0.0), (9.0, YN - 0.05, 0.012), M["tapete"])
    box("cuadro_marco", (9.85, YN - 0.03, 1.3), (10.85, YN, 1.95), M["cuadro_marco"])
    box("cuadro", (9.92, YN - 0.035, 1.37), (10.78, YN - 0.03, 1.88), M["cuadro"])
    use("Deterioro")
    box("cuadro_clavo", (10.34, YN - 0.02, 1.93), (10.36, YN, 1.95), M["metal_oscuro"])


def vueltas(M, repisa, esc_b):
    """Lo que cambia en cada vuelta (documento, seccion 5). La vuelta 1 esta en pasillo()."""
    # Vuelta 2: una mancha de humedad en el techo, sobre la puerta del 4B, que gotea
    use("Vuelta2")
    flat_poly("humedad_techo_borde", (3.42, -0.5), 0.62, M["humedad_borde"], H - 0.002, seed=12, sx=1.3, down=True)
    flat_poly("humedad_techo", (3.42, -0.5), 0.52, M["humedad"], H - 0.003, seed=12, sx=1.3, down=True)
    flat_poly("humedad_techo_centro", (3.45, -0.48), 0.2, M["humedad_centro"], H - 0.004, seed=13, down=True)
    wall_poly("humedad_muro_borde", "x", YN, -1, [(2.9, H - 0.01), (4.0, H - 0.01), (3.92, 2.3), (3.7, 2.18),
                                                (3.55, 2.24), (3.3, 2.17), (3.02, 2.3)], M["humedad_borde"])
    wall_poly("humedad_muro", "x", YN - 0.001, -1, [(3.0, H - 0.01), (3.9, H - 0.01), (3.82, 2.36), (3.66, 2.24),
                                                   (3.52, 2.31), (3.34, 2.22), (3.1, 2.36)], M["humedad"])
    flat_poly("charco", (3.45, -0.48), 0.32, M["charco"], 0.003, seed=14, sx=1.3)
    for i, z in enumerate((H - 0.03, H - 0.45, H - 1.4)):
        mesh_obj(f"gota_{i}", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.012), M["charco"],
                 loc=(3.45, -0.48, z), scale=(1, 1, 1.8))
    # Vuelta 3: la Polaroid de Tomas en la repisa del telefono
    use("Vuelta3")
    polaroid(M, repisa, 15.0)
    # Vuelta 4: no hay puerta a la escalera: el vano queda tapado (por los dos lados, como el muro)
    use("Vuelta4")
    ox, oy = O_B.x, O_B.y
    boxes_obj("pared_sin_puerta", [((ox - 0.45, oy, 0.0), (ox + 0.45, oy + 0.05, DOOR_H))], M["esc_pared"],
              uv=(2, 2, H), origin=O_B, world_uv=False)
    boxes_obj("pared_sin_puerta_pasillo", [((ox - 0.45, oy + 0.05, 0.0), (ox + 0.45, oy + T, DOOR_H))], M["pared"],
              uv=(2, 2, H))
    arriba = esc_b["arriba"]
    mover([arriba["hoja"], *arriba["piezas"], arriba["marco"], *arriba["cartel"]], "Vuelta4_Fuera")


def silueta(M):
    """Tomas en la vuelta 5 (solo para el render; en Unity va Tomas): frente al elevador, de
    espaldas al pasillo, contando."""
    use("SoloRender")
    root = link(bpy.data.objects.new("Tomas_silueta", None))
    root.location, root.rotation_euler, root.scale = (XE - 0.55, YC + 0.05, 0.0), (0, 0, R(96)), (0.95, 0.95, 1.06)
    mat = M["sombra"]

    def part(name, mn, mx, rot=(0, 0, 0), pivot=None):
        ob = box(name, mn, mx, mat, pivot=pivot)
        ob.rotation_euler = rot
        ob.parent = root
        return ob

    part("pierna_izq", (-0.12, -0.06, 0.0), (-0.03, 0.06, 0.88))
    part("pierna_der", (0.03, -0.06, 0.0), (0.12, 0.06, 0.88))
    part("torso", (-0.16, -0.08, 0.86), (0.16, 0.08, 1.42), rot=(R(12), 0, 0), pivot=(0, 0, 0.86))
    part("brazo_izq", (-0.23, -0.12, 0.58), (-0.17, -0.06, 1.38), rot=(0, R(-3), 0))
    part("brazo_der", (0.17, -0.12, 0.55), (0.23, -0.06, 1.38), rot=(0, R(2), 0))
    part("cuello", (-0.04, -0.14, 1.38), (0.04, -0.06, 1.48))
    head = mesh_obj("cabeza", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.11), mat,
                    loc=(0.0, -0.17, 1.55), rot=(R(35), 0, 0), scale=(0.88, 1.0, 1.15))
    head.parent = root


def etiquetas(M):
    use("Plano")
    for text, x, y, size in (("4B", 3.45, 0.7, 0.4), ("4D", 8.65, 0.5, 0.32), ("4F", 11.85, 0.5, 0.32),
                             ("4A", 5.45, -2.6, 0.32), ("4C VAC\u00cdO", 10.05, -3.3, 0.3), ("4E", 14.05, -2.6, 0.32),
                             ("ESCALERA A", O_A.x, -4.4, 0.28), ("ESCALERA B", O_B.x, -10.4, 0.28),
                             ("ELEVADOR", 18.75, -0.65, 0.2), ("LIMPIEZA", 18.45, -3.7, 0.16),
                             ("TEL\u00c9FONO", 16.3, 0.5, 0.24), ("PASILLO LARGO", 7.0, YC, 0.3),
                             ("TRAMO CORTO", 16.9, -3.4, 0.22)):
        text_obj("etiqueta_" + text.split()[0].lower(), text, size, M["etiqueta"], (x, y, H + 3.0))


# ---------------------------------------------------------------------------
# Luces, mundo y camaras
# ---------------------------------------------------------------------------
def light(name, kind, loc, states, target=None, radius=0.05, size=(0.5, 0.5), spot=(45, 0.3)):
    """states: {estado: (color, potencia) o None}. Las vueltas 1 a 4 y el plano usan la de
    la abstinencia salvo que digan otra cosa; si un estado no aparece, la luz se apaga."""
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


def resolve(states, state):
    if state in states:
        return states[state]
    if state.startswith("vuelta") or state == "plano":
        return states.get("abstinencia")
    return None


def lights(focos):
    use("Luces")
    for i, loc in focos.items():
        if i in (1, 3):
            st = {"abstinencia": (WARM, 22), "efecto": (GOLD, 30), "vuelta5": None}
        else:
            st = {"efecto": (GOLD, 30)}
        light(f"luz_foco_{i}", "POINT", loc, st, radius=0.03)
    light("luz_fluor_vestibulo", "AREA", (17.1, YC, H - 0.09),
          {"abstinencia": (COLD, 30), "efecto": (GOLD, 25), "vuelta5": None}, size=(0.06, 1.0))
    light("luz_fluor_corto", "AREA", ((X2A + XE) / 2, -5.0, H - 0.09),
          {"abstinencia": (COLD, 16), "efecto": (GOLD, 25), "vuelta5": (COLD, 8)}, size=(1.0, 0.06))
    light("luz_indicador", "POINT", (XE - 0.2, YC, 2.42),
          {"abstinencia": ((1.0, 0.45, 0.1), 0.6), "efecto": ((1.0, 0.45, 0.1), 0.6)}, radius=0.05)
    light("luz_cartel_a", "POINT", (O_A.x, YS + 0.3, 2.29), {"abstinencia": (GREEN, 2.0), "efecto": (GREEN, 1.5)},
          radius=0.1)
    light("luz_cartel_b", "POINT", (O_B.x, YT2 + 0.3, 2.29),
          {"abstinencia": (GREEN, 2.0), "efecto": (GREEN, 1.5), "vuelta4": None}, radius=0.1)
    for letra, O in (("a", O_A), ("b", O_B)):
        light(f"esc{letra}_luz_rellano", "POINT", (O.x, O.y - 0.6, O.z + H - 0.47),
              {"abstinencia": (WARM, 18), "efecto": (GOLD, 28)}, radius=0.03)
        light(f"esc{letra}_luz_descanso", "POINT", (O.x, O.y - 4.12, O.z + 0.79),
              {"abstinencia": (WARM, 24), "efecto": (GOLD, 30)}, radius=0.03)
        light(f"esc{letra}_luz_abajo", "POINT", (O.x, O.y - 0.6, O.z - 0.51),
              {"abstinencia": (WARM, 8), "efecto": (GOLD, 16)}, radius=0.03)
    light("luz_cabina", "AREA", (XE + T + 0.8, YC, 2.27), {"vuelta5": (CAB, 24)}, size=(0.7, 0.5))
    light("farola_4c", "SPOT", (10.1, -7.6, 3.4), {"abstinencia": (SODIUM, 3200), "efecto": (GOLD, 2400)},
          target=(9.4, -3.3, 0.5), spot=(40, 0.2), radius=0.1)
    # Rebote: EEVEE no hace rebotar la luz de la calle en el piso del 4C. En Unity lo da la luz
    # precalculada (truco: rebote, ver exportar_unity.py).
    rb = light("rebote_4c", "POINT", (9.9, -3.6, 0.45), {"abstinencia": (SODIUM, 16), "efecto": (GOLD, 24)}, radius=0.5)
    rb.data.use_shadow = False
    rb["truco"] = "rebote"
    sol = light("sol_plano", "SUN", (9.0, -5.0, 12.0), {"plano": ((1.0, 1.0, 1.0), 2.5)}, target=(9.2, -5.2, 0.0))
    sol.data.specular_factor = 0.0  # sin brillos en el plano


WORLD = {
    "abstinencia": dict(bg=(0.004, 0.005, 0.007), fog=(0.75, 0.80, 0.72), density=0.022),
    "efecto": dict(bg=(0.07, 0.045, 0.025), fog=(1.0, 0.82, 0.60), density=0.018),
    "vuelta5": dict(bg=(0.002, 0.003, 0.005), fog=(0.62, 0.72, 0.82), density=0.02),
    "plano": dict(bg=(0.30, 0.30, 0.30), fog=(1.0, 1.0, 1.0), density=0.0),
}


def setup_world():
    w = bpy.data.worlds.new("MundoPasillo")
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


def set_state(state, M, solo_render=False):
    """Cambia la escena a 'abstinencia', 'efecto', 'vuelta1' ... 'vuelta5' o 'plano'."""
    efecto = state == "efecto"
    vuelta = int(state[-1]) if state.startswith("vuelta") else 0
    COLS["Deterioro"].hide_render = efecto
    COLS["Efecto"].hide_render = not efecto
    for n in (1, 2, 3, 4):
        COLS[f"Vuelta{n}"].hide_render = vuelta != n
    for n in (1, 4):
        COLS[f"Vuelta{n}_Fuera"].hide_render = vuelta == n
    COLS["SoloRender"].hide_render = not solo_render
    COLS["Plano"].hide_render = state != "plano"
    for ob in CEILINGS:
        ob.hide_render = state == "plano"
    for mat, dirty, clean in SWAPS:
        mat.node_tree.nodes["Textura"].image = clean if efecto else dirty
    for ob, states in LIGHTS.values():
        cfg = resolve(states, state)
        ob.hide_render = cfg is None
        if cfg:
            ob.data.color, ob.data.energy = cfg
    for key, states in EMIS.items():
        cfg = resolve(states, state) or (states["abstinencia"][0], 0.0)
        em = M[key].node_tree.nodes["Emision"]
        em.inputs["Color"].default_value = (*cfg[0], 1.0)
        em.inputs["Strength"].default_value = cfg[1]
    W = WORLD.get(state, WORLD["abstinencia"])
    nt = scene.world.node_tree
    nt.nodes["Fondo"].inputs["Color"].default_value = (*W["bg"], 1.0)
    nt.nodes["Niebla"].inputs["Density"].default_value = W["density"]
    nt.nodes["Niebla"].inputs["Color"].default_value = (*W["fog"], 1.0)
    # La puerta del elevador: abierta solo en la vuelta 5
    abierto = 0.56 if vuelta == 5 else 0.0
    for lado, s in (("sur", -1), ("norte", 1)):
        ob = ELEVATOR[lado]
        y0 = ELEVATOR.setdefault(lado + "_y0", ob.location.y)
        ob.location.y = y0 + s * abierto


def camera(name, loc, target, lens=24.0, ortho=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start, cd.clip_end = 0.03, 60.0
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
    camera("Cam_comienzo", (1.4, -1.12, 1.6), (17.8, -1.45, 1.3))            # recien salido de la escalera A
    camera("Cam_esquina", (16.9, -0.75, 1.6), (16.9, -8.0, 1.15))             # el tramo corto, desde el elevador
    camera("Cam_escalera", tuple(O_B + Vector((0.75, -3.85, -1.3 + 1.6))),    # bajando: el descanso de la B
           tuple(O_B + Vector((0.3, -0.2, -H + 0.7))), lens=20.0)
    camera("Cam_vuelta1", (6.9, -1.55, 1.6), (8.65, -0.14, 1.5))              # el 4D dice 4B
    camera("Cam_vuelta2", (6.0, -1.75, 1.6), (3.45, -0.35, 1.25), lens=20.0)  # la mancha sobre el 4B
    camera("Cam_vuelta3", (14.75, -1.55, 1.6), (16.3, -0.2, 1.1))             # el telefono y la Polaroid
    camera("Cam_vuelta4", (16.9, -2.3, 1.6), (16.9, -8.0, 1.1))               # el tramo corto, sin puerta
    camera("Cam_vuelta5", (5.0, -1.1, 1.6), (17.8, -1.02, 1.15))              # Tomas frente al elevador
    camera("Cam_escondite", (XE + T + 0.55, -4.5, 1.55), (16.0, -4.4, 1.35))  # desde el cuarto de limpieza
    camera("Cam_4c", (10.15, -2.25, 1.6), (9.2, -4.6, 0.9), lens=20.0)       # adentro del 4C, desde la puerta
    camera("Cam_ascensor", (16.2, -1.35, 1.6), (19.4, -0.9, 1.1))             # la cabina abierta
    camera("Cam_plano", (9.6, -5.8, 20.0), None, ortho=22.0)                  # desde arriba, sin techo


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
    _try_set(ee, "volumetric_tile_size", "4")
    _try_set(ee, "volumetric_samples", 64)
    _try_set(ee, "volumetric_start", 0.05)
    _try_set(ee, "volumetric_end", 25.0)
    _try_set(ee, "use_volumetric_shadows", True)


# ---------------------------------------------------------------------------
# Post-proceso PS1
# ---------------------------------------------------------------------------
BAYER4 = np.array([[0, 8, 2, 10],
                   [12, 4, 14, 6],
                   [3, 11, 1, 9],
                   [15, 7, 13, 5]], dtype=np.float32) / 16.0 - 0.5 + 1.0 / 32.0


def load_rgb(src):
    img = bpy.data.images.load(src)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)[:, :, :3].copy()


def quantize(rgb):
    """15 bits con dithering Bayer (fila 0 = abajo)."""
    h, w = rgb.shape[:2]
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


def foto_polaroid(rgb):
    """Recorta el centro del render y le pone el marco de una Polaroid, con el color lavado."""
    h, w = rgb.shape[:2]
    s = 232
    y0, x0 = (h - s) // 2, (w - s) // 2
    foto = rgb[y0:y0 + s, x0:x0 + s]
    foto = np.clip(0.09 + 1.25 * foto * np.array([1.0, 0.95, 0.84]), 0.0, 1.0)
    side, bottom = 16, 62
    out = np.ones((s + side + bottom, s + 2 * side, 3)) * np.array([0.86, 0.84, 0.78])
    g = np.random.default_rng(2)
    out *= (0.96 + 0.04 * g.random(out.shape[:2]))[:, :, None]
    out[bottom:bottom + s, side:side + s] = foto  # fila 0 = abajo: el borde ancho queda abajo
    return out


VIEWS = {
    "comienzo": dict(cam="Cam_comienzo", state="abstinencia"),
    "efecto": dict(cam="Cam_comienzo", state="efecto"),
    "esquina": dict(cam="Cam_esquina", state="abstinencia"),
    "escalera": dict(cam="Cam_escalera", state="abstinencia"),
    "vuelta1": dict(cam="Cam_vuelta1", state="vuelta1"),
    "vuelta2": dict(cam="Cam_vuelta2", state="vuelta2"),
    "vuelta3": dict(cam="Cam_vuelta3", state="vuelta3"),
    "vuelta4": dict(cam="Cam_vuelta4", state="vuelta4"),
    "vuelta5": dict(cam="Cam_vuelta5", state="vuelta5", solo_render=True),
    "escondite": dict(cam="Cam_escondite", state="abstinencia"),
    "4c": dict(cam="Cam_4c", state="abstinencia"),
    "ascensor": dict(cam="Cam_ascensor", state="vuelta5"),
    "plano": dict(cam="Cam_plano", state="plano", res=(640, 400), up=3),
}
SHEET = [["comienzo", "efecto"], ["esquina", "escalera"], ["vuelta1", "vuelta2"], ["vuelta3", "vuelta4"],
         ["vuelta5", "escondite"]]
ESTADOS = ("abstinencia", "efecto", "vuelta1", "vuelta2", "vuelta3", "vuelta4", "vuelta5")


def render_view(key, cfg, M):
    set_state(cfg["state"], M, cfg.get("solo_render", False))
    scene.camera = CAMS[cfg["cam"]]
    rx, ry = cfg.get("res", (RES_X, RES_Y))
    scene.render.resolution_x, scene.render.resolution_y = rx, ry
    raw = os.path.join(RENDER_DIR, f"pasillo4_{key}_raw.png")
    scene.render.filepath = raw
    bpy.ops.render.render(write_still=True)
    rgb = load_rgb(raw)
    os.remove(raw)
    return rgb


def main():
    t0 = time.time()
    for d in (TEX_DIR, SCENE_DIR, RENDER_DIR):
        os.makedirs(d, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

    root = bpy.data.collections.new("Pasillo_Piso4")
    scene.collection.children.link(root)
    for name in ("Estructura", "Objetos", "Deterioro", "Efecto", "EscaleraA", "EscaleraB", "Departamento4C",
                 "Vuelta1", "Vuelta1_Fuera", "Vuelta2", "Vuelta3", "Vuelta4", "Vuelta4_Fuera",
                 "Fachada4B", "SoloRender", "Luces", "Camaras", "Plano"):
        COLS[name] = bpy.data.collections.new(name)
        root.children.link(COLS[name])

    M = build_materials()
    pasillo(M)
    tuberias(M)
    focos = luces_del_pasillo(M)
    ascensor(M)
    repisa = telefono(M)
    cuarto_limpieza(M)
    departamento_4c(M)
    escalera("A", O_A, M)
    esc_b = escalera("B", O_B, M)
    fachada_4b(M)
    deterioro_y_efecto(M)
    vueltas(M, repisa, esc_b)
    silueta(M)
    etiquetas(M)
    lights(focos)
    cameras()
    setup_world()
    setup_render()

    excluir = ("Plano", "Fachada4B", "SoloRender")
    mallas = [o for o in bpy.data.objects if o.type in ("MESH", "FONT") and not any(
        c.name in excluir for c in o.users_collection)]
    dg = bpy.context.evaluated_depsgraph_get()
    tris = 0
    for o in mallas:
        me = o.evaluated_get(dg).to_mesh()
        tris += sum(len(p.vertices) - 2 for p in me.polygons)
        o.evaluated_get(dg).to_mesh_clear()
    print(f"[info] pasillo: {len(mallas)} objetos, {tris} triangulos")

    panels = {}
    for key, cfg in VIEWS.items():
        if ONLY and key not in ONLY:
            continue
        t = time.time()
        q = quantize(render_view(key, cfg, M))
        save_png(q, os.path.join(RENDER_DIR, f"pasillo4_{key}.png"), cfg.get("up", UPSCALE))
        panels[key] = q
        print(f"[render] {key}: {time.time() - t:.1f} s")
        if key == "vuelta4":
            # La foto de la vuelta 4: la misma vista, pero con la puerta que la camara si ve
            foto = foto_polaroid(render_view("vuelta4_foto", dict(cam="Cam_vuelta4", state="abstinencia"), M))
            save_png(quantize(foto), os.path.join(RENDER_DIR, "pasillo4_vuelta4_foto.png"), 3)

    if all(k in panels for row in SHEET for k in row):
        rows = []
        for row in SHEET:
            r = np.concatenate([panels[k] for k in row], axis=1)
            r[:, RES_X - 1:RES_X + 1] = 0.0
            rows.append(r)
        sheet = np.concatenate(rows[::-1], axis=0)  # fila 0 = abajo
        for i in range(1, len(SHEET)):
            sheet[i * RES_Y - 1:i * RES_Y + 1, :] = 0.0
        save_png(sheet, os.path.join(RENDER_DIR, "pasillo4_hoja.png"), 2)

    # Deja la escena en la vuelta 0, vista desde el comienzo
    set_state("abstinencia", M)
    scene.camera = CAMS["Cam_comienzo"]
    scene.render.resolution_x, scene.render.resolution_y = RES_X, RES_Y
    blend = os.path.join(SCENE_DIR, "pasillo_piso4.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print(f"[aviso] rutas relativas: {e}")

    if SIN_UNITY:
        print(f"[info] listo (sin Unity) en {time.time() - t0:.1f} s")
        return
    # Unity: se fotografian los siete estados y el FBX queda en la vuelta 0 (abstinencia)
    estados = {}
    for estado in ESTADOS:
        set_state(estado, M)
        estados[estado] = exportar_unity.foto_estado()
    set_state("abstinencia", M)
    exportar_unity.exportar(ROOT, "PasilloPiso4", "pasillo_piso4", excluir=excluir, estados=estados,
                            extra={"anclas_escalera": {"A": list(O_A), "B": list(O_B)}})
    print(f"[info] listo en {time.time() - t0:.1f} s")


main()
