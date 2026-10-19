r"""
Prueba de estilo: el pasillo del 4o piso (Noche 2).

Construye el pasillo low poly con codigo, lo renderiza a 480x270 y aplica un
post-proceso estilo PlayStation 1:
  - color de 15 bits (32 niveles por canal) con dithering Bayer 4x4
  - escalado x4 sin suavizado (pixeles duros)

Uso (PowerShell, desde la carpeta del proyecto):
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup `
      -P blender\scripts\prueba_estilo_pasillo.py -- blender

Salidas (dentro de la carpeta blender/):
  textures/*.png                       texturas pixeladas, reutilizables en Unity
  scenes/prueba_estilo_pasillo.blend   la escena, para abrirla y retocarla
  renders/pasillo_raw.png              render a 480x270
  renders/pasillo_ps1.png              render final a 1920x1080
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
ENGINE = (ARGS[1] if len(ARGS) > 1 else "EEVEE").upper()

TEX_DIR = os.path.join(ROOT, "textures")
SCENE_DIR = os.path.join(ROOT, "scenes")
RENDER_DIR = os.path.join(ROOT, "renders")

RES_X, RES_Y = 480, 270
UPSCALE = 4
COLOR_LEVELS = 32  # 15 bits de color, como la PS1

# Medidas del pasillo en metros. El pasillo corre a lo largo del eje Y.
HALF_W = 0.9
HEIGHT = 2.6
Y_START, Y_END = -1.0, 16.0

rng = np.random.default_rng(4)
scene = bpy.context.scene
COL = None


# ---------------------------------------------------------------------------
# Texturas pixeladas (numpy -> PNG)
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


def save_texture(name, rgb):
    """rgb: (alto, ancho, 3) en 0..1, fila 0 = abajo. Guarda el PNG y lo carga."""
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


def tex_floor():
    # 128 px = 2 m -> baldosas de 25 cm (16 px)
    s = 128
    yy, xx = np.mgrid[0:s, 0:s]
    checker = ((xx // 16 + yy // 16) % 2).astype(np.float32)[:, :, None]
    cream = np.array([0.60, 0.56, 0.46])
    red = np.array([0.34, 0.11, 0.09])
    rgb = cream * (1 - checker) + red * checker
    tile_var = np.kron(rng.random((s // 16, s // 16)), np.ones((16, 16)))
    rgb *= (0.82 + 0.18 * tile_var)[:, :, None]
    grout = ((xx % 16 == 0) | (yy % 16 == 0))[:, :, None]
    rgb = np.where(grout, rgb * 0.45, rgb)
    rgb *= grime(s, s, 0.5)[:, :, None]
    return save_texture("piso_baldosa", rgb)


def tex_wall():
    # 2 m de ancho x 2.6 m de alto
    w, h = 128, 166
    z = (np.arange(h) + 0.5) / h * HEIGHT
    base = np.array([0.16, 0.11, 0.07])
    green = np.array([0.22, 0.34, 0.27])
    strip = np.array([0.10, 0.17, 0.13])
    cream = np.array([0.62, 0.58, 0.46])
    rgb = np.zeros((h, w, 3))
    for i, zi in enumerate(z):
        rgb[i] = base if zi < 0.12 else green if zi < 1.08 else strip if zi < 1.14 else cream
    # mas sucio cerca del piso
    rgb *= (1.0 - 0.35 * np.clip(1.0 - z / 1.2, 0, 1))[:, None, None]
    rgb *= grime(h, w, 0.4)[:, :, None]
    # chorreados de humedad desde arriba: pocos, cortos e irregulares
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
    # manchas de agua: pocas y medianas, mas comunes en la parte alta
    stains = 0.7 * noise(h, w, 6, 5) + 0.3 * noise(h, w, 14, 12)
    stains *= np.clip(z / HEIGHT + 0.3, 0, 1)[:, None]
    rgb = np.where((stains > 0.66)[:, :, None], rgb * np.array([0.82, 0.75, 0.6]), rgb)
    return save_texture("pared_pasillo", rgb)


def tex_ceiling():
    s = 64
    rgb = np.ones((s, s, 3)) * np.array([0.48, 0.47, 0.43])
    rgb *= grime(s, s, 0.3)[:, :, None]
    st = 0.7 * noise(s, s, 5, 5) + 0.3 * noise(s, s, 12, 12)
    rgb = np.where((st > 0.7)[:, :, None], rgb * np.array([0.75, 0.66, 0.48]), rgb)
    return save_texture("techo", rgb)


def tex_door():
    w, h = 64, 128
    yy, xx = np.mgrid[0:h, 0:w]
    base = np.array([0.30, 0.17, 0.09])
    grain = 0.72 + 0.28 * noise(h, w, 3, 20)
    rgb = base * grain[:, :, None]

    def panel(x0, y0, x1, y1):
        inside = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        return inside & ((xx == x0) | (xx == x1) | (yy == y0) | (yy == y1))

    rgb = np.where((panel(10, 12, 53, 58) | panel(10, 68, 53, 116))[:, :, None], rgb * 0.5, rgb)
    rgb *= grime(h, w, 0.35)[:, :, None]
    return save_texture("puerta_madera", rgb)


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
    return save_texture("metal_oxidado", rgb)


# ---------------------------------------------------------------------------
# Materiales
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


def mat_surface(name, color=(0.5, 0.5, 0.5), image=None, rough=0.85, metallic=0.0, spec=0.3):
    m, nt, out = _new_material(name)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
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
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def build_materials():
    t = {
        "piso": tex_floor(),
        "pared": tex_wall(),
        "techo": tex_ceiling(),
        "puerta": tex_door(),
        "metal": tex_metal(),
    }
    return {
        "piso": mat_surface("Piso", image=t["piso"], rough=0.6, spec=0.4),
        "pared": mat_surface("Pared", image=t["pared"], rough=0.9),
        "techo": mat_surface("Techo", image=t["techo"], rough=0.95),
        "puerta": mat_surface("Puerta", image=t["puerta"], rough=0.7),
        "metal": mat_surface("Metal", image=t["metal"], rough=0.5, metallic=0.3),
        "marco": mat_surface("Marco", (0.12, 0.07, 0.04), rough=0.6),
        "metal_oscuro": mat_surface("MetalOscuro", (0.08, 0.09, 0.10), rough=0.5, metallic=0.3),
        "laton": mat_surface("Laton", (0.36, 0.27, 0.11), rough=0.45, metallic=0.8),
        "negro": mat_surface("Negro", (0.0, 0.0, 0.0), rough=1.0, spec=0.0),
        "led": mat_emission("LedAmbar", (1.0, 0.42, 0.08), 6.0),
        "foco": mat_emission("Foco", (1.0, 0.72, 0.42), 10.0),
        "foco_roto": mat_surface("FocoRoto", (0.3, 0.3, 0.28), rough=0.3),
        "fluor": mat_emission("TuboFluorescente", (0.8, 1.0, 0.88), 8.0),
        "plastico_rojo": mat_surface("PlasticoRojo", (0.42, 0.08, 0.06), rough=0.5),
        "pintura_roja": mat_surface("PinturaRoja", (0.32, 0.07, 0.05), rough=0.9),
        "bolsa": mat_surface("BolsaBasura", (0.02, 0.02, 0.025), rough=0.35, spec=0.5),
        "papel": mat_surface("Papel", (0.55, 0.53, 0.48), rough=0.9),
        "mancha": mat_surface("Mancha", (0.09, 0.03, 0.02), rough=0.15, spec=0.6),
        "sombra": mat_surface("Sombra", (0.012, 0.012, 0.012), rough=0.95, spec=0.05),
    }


# ---------------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------------
def link(ob):
    COL.objects.link(ob)
    return ob


def box_uv(me, s):
    """UV por proyeccion de caja en metros: s = tamano de la textura en (x, y, z)."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            c = loop.vert.co
            if ax == 0:
                loop[uv].uv = (c.y / s[1], c.z / s[2])
            elif ax == 1:
                loop[uv].uv = (c.x / s[0], c.z / s[2])
            else:
                loop[uv].uv = (c.x / s[0], c.y / s[1])
    bm.to_mesh(me)
    bm.free()


def box(name, mn, mx, mat, uv=(1.0, 1.0, 1.0), pivot=None):
    """Caja entre las esquinas mn y mx (coordenadas de mundo).
    pivot: punto de mundo que sera el origen del objeto (por ejemplo, la bisagra de una puerta)."""
    mn, mx = Vector(mn), Vector(mx)
    pivot = Vector(pivot) if pivot is not None else mn.copy()
    size, off = mx - mn, mn - pivot
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((
            (v.co.x + 0.5) * size.x + off.x,
            (v.co.y + 0.5) * size.y + off.y,
            (v.co.z + 0.5) * size.z + off.z,
        ))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    box_uv(me, uv)
    ob = bpy.data.objects.new(name, me)
    ob.location = pivot
    return link(ob)


def mesh_obj(name, build, mat, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), uv=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    if uv:
        box_uv(me, uv)
    ob = bpy.data.objects.new(name, me)
    ob.location, ob.rotation_euler, ob.scale = loc, rot, scale
    return link(ob)


def text_obj(name, body, size, mat, loc, rot):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = "CENTER"
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    ob.location, ob.rotation_euler = loc, rot
    return link(ob)


def point_light(name, loc, color, power, radius=0.04):
    ld = bpy.data.lights.new(name, "POINT")
    ld.color, ld.energy, ld.shadow_soft_size = color, power, radius
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    return link(ob)


# ---------------------------------------------------------------------------
# Piezas del pasillo
# ---------------------------------------------------------------------------
def corridor(m):
    W, H = HALF_W, HEIGHT
    box("piso", (-W, Y_START, -0.1), (W, Y_END, 0), m["piso"], uv=(2, 2, 2))
    box("techo", (-W, Y_START, H), (W, Y_END, H + 0.1), m["techo"], uv=(2, 2, 2))
    box("pared_izq", (-W - 0.1, Y_START, 0), (-W, Y_END, H), m["pared"], uv=(2, 2, H))
    box("pared_der", (W, Y_START, 0), (W + 0.1, Y_END, H), m["pared"], uv=(2, 2, H))
    box("pared_fondo", (-W, Y_END, 0), (W, Y_END + 0.1, H), m["pared"], uv=(2, 2, H))
    box("pared_atras", (-W, Y_START - 0.1, 0), (W, Y_START, H), m["pared"], uv=(2, 2, H))


def door(y0, side, m, ajar_deg=0.0):
    """side = -1 pared izquierda, +1 derecha. y0 = borde de la puerta mas cercano a la camara."""
    wall, inward = side * HALF_W, -side
    dw, dh = 0.9, 2.05

    def X(d):  # x a 'd' metros desde la pared hacia el centro del pasillo
        return wall + inward * d

    def bx(name, d0, d1, ya, yb, za, zb, mat, **kw):
        xa, xb = sorted((X(d0), X(d1)))
        return box(name, (xa, ya, za), (xb, yb, zb), mat, **kw)

    bx("marco_a", 0, 0.06, y0 - 0.08, y0, 0, dh + 0.08, m["marco"])
    bx("marco_b", 0, 0.06, y0 + dw, y0 + dw + 0.08, 0, dh + 0.08, m["marco"])
    bx("marco_c", 0, 0.06, y0 - 0.08, y0 + dw + 0.08, dh, dh + 0.08, m["marco"])

    # La bisagra va en el borde lejano, asi la puerta se abre hacia la camara.
    hinge = (X(0.03), y0 + dw, 0.0)
    slab = bx("puerta", 0, 0.03, y0, y0 + dw, 0, dh, m["puerta"], uv=(dw, dw, dh), pivot=hinge)
    knob = bx("manija", 0.03, 0.08, y0 + 0.08, y0 + 0.14, 0.98, 1.04, m["laton"])
    plate = bx("numero", 0.03, 0.04, y0 + 0.38, y0 + 0.52, 1.58, 1.68, m["laton"])
    for child in (knob, plate):
        child.parent = slab
        child.matrix_parent_inverse = Matrix.Translation(hinge).inverted()

    if ajar_deg:
        bx("oscuridad", 0.0, 0.012, y0, y0 + dw, 0, dh, m["negro"])
        slab.rotation_euler.z = -side * math.radians(ajar_deg)


def bulb(y, power, m, x=0.0):
    """power = 0 -> foco quemado."""
    zc = HEIGHT
    box("roseta", (x - 0.06, y - 0.06, zc - 0.03), (x + 0.06, y + 0.06, zc), m["metal"])
    box("cable", (x - 0.008, y - 0.008, zc - 0.28), (x + 0.008, y + 0.008, zc - 0.03), m["negro"])
    zb = zc - 0.33
    mesh_obj("foco", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.055),
             m["foco"] if power else m["foco_roto"], loc=(x, y, zb))
    if power:
        point_light("luz_foco", (x, y, zb - 0.07), (1.0, 0.68, 0.38), power)


def fluorescent(y, m):
    zc = HEIGHT
    box("fluor_base", (-0.55, y - 0.06, zc - 0.04), (0.55, y + 0.06, zc), m["metal_oscuro"])
    box("fluor_tubo", (-0.5, y - 0.02, zc - 0.07), (0.5, y + 0.02, zc - 0.04), m["fluor"])
    ld = bpy.data.lights.new("luz_fluorescente", "AREA")
    ld.shape, ld.size, ld.size_y = "RECTANGLE", 1.0, 0.06
    ld.color, ld.energy = (0.75, 1.0, 0.85), 30.0
    ob = bpy.data.objects.new("luz_fluorescente", ld)
    ob.location = (0, y, zc - 0.09)
    link(ob)


def elevator(m):
    yf = Y_END
    box("ascensor_marco", (-0.66, yf - 0.06, 0), (0.66, yf, 2.28), m["metal_oscuro"])
    box("ascensor_puerta_izq", (-0.52, yf - 0.08, 0.0), (-0.006, yf - 0.06, 2.12), m["metal"], uv=(0.5, 0.5, 0.5))
    box("ascensor_puerta_der", (0.006, yf - 0.08, 0.0), (0.52, yf - 0.06, 2.12), m["metal"], uv=(0.5, 0.5, 0.5))
    box("indicador", (-0.18, yf - 0.03, 2.33), (0.18, yf, 2.50), m["negro"])
    text_obj("indicador_numero", "4", 0.13, m["led"], (0, yf - 0.035, 2.36), (math.radians(90), 0, 0))
    point_light("luz_indicador", (0, yf - 0.2, 2.42), (1.0, 0.45, 0.1), 0.6, radius=0.05)
    box("botonera", (0.72, yf - 0.03, 1.0), (0.82, yf, 1.25), m["metal_oscuro"])
    box("boton", (0.755, yf - 0.045, 1.10), (0.785, yf - 0.03, 1.13), m["led"])


def wall_phone(y, m):
    x = -HALF_W
    box("telefono_caja", (x, y, 1.22), (x + 0.09, y + 0.22, 1.55), m["plastico_rojo"])
    box("telefono_auricular", (x + 0.09, y + 0.03, 1.27), (x + 0.13, y + 0.07, 1.50), m["negro"])
    text_obj("piso_pintado", "PISO 4", 0.16, m["pintura_roja"],
             (x + 0.003, y - 0.55, 1.72), (math.radians(90), 0, math.radians(90)))


def pipes(m):
    length = Y_END - Y_START
    mid = (Y_START + Y_END) / 2
    for name, x, z, r in (("tubo_a", -0.76, 2.47, 0.05), ("tubo_b", -0.62, 2.52, 0.03)):
        mesh_obj(name,
                 lambda bm, r=r: bmesh.ops.create_cone(bm, cap_ends=True, segments=8,
                                                       radius1=r, radius2=r, depth=length),
                 m["metal"], loc=(x, mid, z), rot=(math.radians(90), 0, 0), uv=(1, 1, 1))


def clutter(m):
    def bag(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.25)
        for v in bm.verts:
            v.co *= 0.85 + 0.3 * rng.random()
            v.co.z = max(v.co.z, -0.12)

    mesh_obj("bolsa_basura", bag, m["bolsa"], loc=(0.66, 4.7, 0.12))
    mesh_obj("bolsa_basura_2", bag, m["bolsa"], loc=(0.58, 5.1, 0.10), scale=(0.8, 0.8, 0.7))

    for i in range(6):
        x = float(rng.choice([-1, 1]) * rng.uniform(0.3, 0.75))
        y = float(rng.uniform(1.5, 12.5))
        mesh_obj(f"periodico_{i}", lambda bm: bmesh.ops.create_cube(bm, size=1.0), m["papel"],
                 loc=(x, y, 0.004), rot=(0, 0, float(rng.uniform(0, math.pi))), scale=(0.38, 0.28, 0.006))

    def stain(bm):
        verts = []
        for i in range(12):
            a = 2 * math.pi * i / 12
            r = 0.35 * (0.6 + 0.6 * rng.random())
            verts.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r * 1.5, 0)))
        bm.faces.new(verts)

    mesh_obj("mancha", stain, m["mancha"], loc=(0.35, 7.4, 0.003))


def silhouette(mat, loc, rot_z=0.0):
    """Tomas al fondo del pasillo: una figura encorvada, a contraluz."""
    root = link(bpy.data.objects.new("Tomas_silueta", None))
    root.location, root.rotation_euler, root.scale = loc, (0, 0, rot_z), (0.95, 0.95, 1.06)

    def part(name, mn, mx, rot=(0, 0, 0), pivot=None):
        ob = box(name, mn, mx, mat, pivot=pivot)
        ob.rotation_euler = rot
        ob.parent = root
        return ob

    # flaco, hombros caidos, brazos demasiado largos, cabeza ladeada hacia abajo
    part("pierna_izq", (-0.12, -0.06, 0.0), (-0.03, 0.06, 0.88))
    part("pierna_der", (0.03, -0.06, 0.0), (0.12, 0.06, 0.88))
    part("torso", (-0.16, -0.08, 0.86), (0.16, 0.08, 1.42), rot=(math.radians(12), 0, 0), pivot=(0, 0, 0.86))
    part("brazo_izq", (-0.23, -0.12, 0.58), (-0.17, -0.06, 1.38), rot=(0, math.radians(-3), 0))
    part("brazo_der", (0.17, -0.12, 0.55), (0.23, -0.06, 1.38), rot=(0, math.radians(2), 0))
    part("cuello", (-0.04, -0.14, 1.38), (0.04, -0.06, 1.48))
    head = mesh_obj("cabeza", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.11), mat,
                    loc=(0.06, -0.15, 1.56), rot=(math.radians(28), math.radians(24), 0), scale=(0.88, 1.0, 1.15))
    head.parent = root


# ---------------------------------------------------------------------------
# Mundo, camara y render
# ---------------------------------------------------------------------------
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
    bg.inputs["Color"].default_value = (0.004, 0.005, 0.007, 1.0)
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    # Niebla en todo el pasillo
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 0.022
    vol.inputs["Color"].default_value = (0.75, 0.8, 0.72, 1.0)
    vol.inputs["Anisotropy"].default_value = 0.35
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])


def setup_camera():
    cd = bpy.data.cameras.new("Camara")
    cd.lens = 24
    cd.clip_start, cd.clip_end = 0.05, 60.0
    cam = link(bpy.data.objects.new("Camara", cd))
    cam.location = (0.2, -0.4, 1.6)
    cam.rotation_euler = (math.radians(89), math.radians(1.5), math.radians(3))
    scene.camera = cam


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

    if ENGINE == "CYCLES":
        r.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    else:
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
        _try_set(ee, "volumetric_start", 0.1)
        _try_set(ee, "volumetric_end", 25.0)
        _try_set(ee, "use_volumetric_shadows", True)
    print(f"[info] motor de render: {r.engine}")


BAYER4 = np.array([[0, 8, 2, 10],
                   [12, 4, 14, 6],
                   [3, 11, 1, 9],
                   [15, 7, 13, 5]], dtype=np.float32) / 16.0 - 0.5 + 1.0 / 32.0


def ps1_post(src, dst):
    """Cuantiza a 32 niveles por canal con dithering Bayer y escala sin suavizado."""
    img = bpy.data.images.load(src)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    rgb = px.reshape(h, w, 4)[:, :, :3]
    threshold = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w, None]
    levels = COLOR_LEVELS - 1
    q = np.clip(np.floor(rgb * levels + 0.5 + threshold) / levels, 0.0, 1.0)
    q = np.repeat(np.repeat(q, UPSCALE, axis=0), UPSCALE, axis=1)
    H, W = q.shape[:2]
    out = np.ones((H, W, 4), dtype=np.float32)
    out[:, :, :3] = q
    o = bpy.data.images.new("post", W, H, alpha=False)
    o.pixels.foreach_set(out.ravel())
    o.filepath_raw = dst
    o.file_format = "PNG"
    o.save()
    bpy.data.images.remove(o)
    bpy.data.images.remove(img)


# ---------------------------------------------------------------------------
def main():
    global COL
    for d in (TEX_DIR, SCENE_DIR, RENDER_DIR):
        os.makedirs(d, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    COL = bpy.data.collections.new("Pasillo")
    scene.collection.children.link(COL)

    m = build_materials()
    corridor(m)
    # (borde cercano de la puerta, lado, grados de apertura)
    for y0, side, ajar in ((1.2, -1, 0), (5.0, -1, 0), (9.6, -1, 0),
                           (3.2, 1, 0), (7.8, 1, 18), (11.8, 1, 0)):
        door(y0, side, m, ajar)
    # Luz alternada: charcos de luz y zonas negras entre ellos.
    # La puerta entreabierta y la figura quedan en las zonas negras.
    for y, power in ((2.0, 22.0), (6.0, 0.0), (10.0, 22.0), (14.0, 0.0)):
        bulb(y, power, m)
    fluorescent(15.3, m)
    elevator(m)
    wall_phone(14.55, m)
    pipes(m)
    clutter(m)
    silhouette(m["sombra"], (-0.12, 13.3, 0.0), rot_z=math.radians(-8))

    setup_world()
    setup_camera()
    setup_render()

    blend = os.path.join(SCENE_DIR, "prueba_estilo_pasillo.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print(f"[aviso] rutas relativas: {e}")

    raw = os.path.join(RENDER_DIR, "pasillo_raw.png")
    scene.render.filepath = raw
    bpy.ops.render.render(write_still=True)
    ps1_post(raw, os.path.join(RENDER_DIR, "pasillo_ps1.png"))
    print("[info] listo")


main()
