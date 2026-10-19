r"""
Dona Carmen, la vecina del 4A: modelo low poly con esqueleto, dos vestuarios y el plato tapado.

  dia    (carmen_dia.png)    vestido oscuro de viuda, chaleco de lana, delantal de flores,
                             medias enrolladas y pantuflas. Asi le deja la comida a Elias.
  noche  (carmen_noche.png)  bata acolchada sobre el camison y redecilla en el pelo:
                             la noche en que murio Tomas, cuando oyo algo y toco (Noche 5).

No cambia con la abstinencia ni con el efecto: es lo unico real del juego.
Lleva el escapulario de la Virgen del Carmen (el Monte Carmelo de su nombre).

Como Tomas: piezas rigidas que se mueven con su hueso, una textura de 256x256 por
vestuario y un esqueleto con nombres de Mixamo (Unity lo reconoce como Humanoid).
El plato es un objeto aparte (plato de peltre tapado con una servilleta bordada).

Uso (PowerShell, desde la carpeta del proyecto):
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup `
      -P blender\scripts\dona_carmen.py -- blender
  Solo el modelo y la hoja (sin el pasillo): ... -- blender --solo-hoja

Salidas (dentro de la carpeta blender/):
  textures/carmen_dia.png, carmen_noche.png, plato_carmen.png
  scenes/dona_carmen.blend            el modelo, el plato y las poses
  renders/carmen_hoja.png             cuerpo y cara de los dos vestuarios, y el plato
  renders/carmen_mirilla_plato.png    por la mirilla: espera con el plato
  renders/carmen_mirilla_cerca.png    por la mirilla: se acerca a mirar
  renders/carmen_mirilla_noche.png    por la mirilla: aquella noche, en bata, tocando
  renders/carmen_mirilla_vacio.png    por la mirilla: nadie, solo los platos que se acumulan
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = os.path.abspath(ARGS[0]) if ARGS else os.getcwd()
SHEET_ONLY = "--solo-hoja" in ARGS

TEX_DIR = os.path.join(ROOT, "textures")
SCENE_DIR = os.path.join(ROOT, "scenes")
RENDER_DIR = os.path.join(ROOT, "renders")

RES_X, RES_Y = 480, 270
COLOR_LEVELS = 32
TEX = 256
OUTFITS = ("dia", "noche")
R = math.radians
rng = np.random.default_rng(31)
scene = bpy.context.scene

HEAD_DZ = -0.025   # la cabeza se modelo 2,5 cm mas alta; se baja para acortar el cuello

# Regiones del atlas: (x, y, ancho, alto) en pixeles, fila 0 arriba
REG = {
    "head": (0, 0, 128, 96), "torso": (128, 0, 128, 80), "skirt": (128, 80, 128, 64),
    "arm": (0, 96, 64, 96), "leg": (64, 96, 32, 64), "neck": (96, 96, 32, 16),
    "bun": (96, 112, 32, 32), "hand": (128, 144, 64, 64), "foot": (192, 144, 64, 64),
}
# Alturas (o largos) que cubre cada region, de la primera fila a la ultima
SPAN = {
    "head": (1.560 + HEAD_DZ, 1.335 + HEAD_DZ), "torso": (1.265, 0.86), "skirt": (0.92, 0.33), "neck": (1.335, 1.24),
    "arm": (0.12, 0.625), "leg": (0.52, 0.075), "bun": (0.070, 0.144), "foot": (0.06, -0.175),
}
HAND_X0, HAND_LEN = 0.62, 0.17


# ---------------------------------------------------------------------------
# Esqueleto (nombres de Mixamo). Mira hacia -Y; su izquierda es +X. Mide 1,55 m.
# ---------------------------------------------------------------------------
FRONT = Vector((0, -1, 0))
UP = Vector((0, 0, 1))


def bone_layout():
    L = {}

    def add(name, head, tail, parent, z=FRONT):
        L[name] = (Vector(head), Vector(tail), parent, z)

    add("Hips", (0, 0, 0.84), (0, 0, 0.91), None)
    add("Spine", (0, 0, 0.91), (0, 0, 1.01), "Hips")
    add("Spine1", (0, 0, 1.01), (0, 0, 1.11), "Spine")
    add("Spine2", (0, 0, 1.11), (0, 0, 1.25), "Spine1")
    add("Neck", (0, 0, 1.25), (0, -0.01, 1.335 + HEAD_DZ), "Spine2")
    add("Head", (0, -0.01, 1.335 + HEAD_DZ), (0, -0.01, 1.53 + HEAD_DZ), "Neck")
    for s, nm in ((1, "Left"), (-1, "Right")):
        add(nm + "Shoulder", (0.03 * s, 0.0, 1.205), (0.165 * s, 0.005, 1.215), "Spine2")
        add(nm + "Arm", (0.165 * s, 0.005, 1.215), (0.41 * s, 0.005, 1.215), nm + "Shoulder")
        add(nm + "ForeArm", (0.41 * s, 0.005, 1.215), (0.635 * s, 0.0, 1.215), nm + "Arm")
        add(nm + "Hand", (0.635 * s, 0.0, 1.215), (0.785 * s, 0.0, 1.205), nm + "ForeArm")
    for s, nm in ((1, "Left"), (-1, "Right")):
        add(nm + "UpLeg", (0.095 * s, 0.0, 0.81), (0.095 * s, 0.0, 0.445), "Hips")
        add(nm + "Leg", (0.095 * s, 0.0, 0.445), (0.095 * s, 0.01, 0.075), nm + "UpLeg")
        add(nm + "Foot", (0.095 * s, 0.01, 0.075), (0.095 * s, -0.10, 0.022), nm + "Leg", UP)
        add(nm + "ToeBase", (0.095 * s, -0.10, 0.022), (0.095 * s, -0.165, 0.022), nm + "Foot", UP)
    return L


LAYOUT = bone_layout()
BONES = list(LAYOUT.keys())


# ---------------------------------------------------------------------------
# Malla
# ---------------------------------------------------------------------------
def atlas_uv(region, u, v):
    x0, y0, w, h = REG[region]
    col = x0 + 0.5 + min(max(u, 0.0), 1.0) * (w - 1)
    row = y0 + 0.5 + min(max(v, 0.0), 1.0) * (h - 1)
    return (col / TEX, 1.0 - row / TEX)


def vfrac(region, p):
    a, b = SPAN[region]
    return (p - a) / (b - a)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.dl = self.bm.verts.layers.deform.verify()
        self.groups = {n: i for i, n in enumerate(BONES)}

    def vert(self, p, weights):
        v = self.bm.verts.new(p)
        for g, w in weights.items():
            if w > 0:
                v[self.dl][self.groups[g]] = w
        return v

    def face(self, verts, uvs):
        f = self.bm.faces.new(verts)
        for loop, uv in zip(f.loops, uvs):
            loop[self.uv].uv = uv
        f.smooth = True
        return f


def tube(B, rings, sides, region, U, V, caps=(None, None), flat=False):
    """Tubo de anillos elipticos. El angulo t=90 apunta a V (el frente); la costura queda atras.
    rings: dict(c, rx, ry, v, w (dict o funcion), push(j))."""
    grid = []
    for rg in rings:
        row = []
        for j in range(sides):
            t = math.radians(-90 + 360 * j / sides)
            sn = math.sin(t)
            if flat and sn < -1e-6:
                sn = -1.0  # suela plana
            off = U * (rg["rx"] * math.cos(t)) + V * (rg["ry"] * sn)
            push = rg["push"](j) if "push" in rg else Vector()
            p = rg["c"] + off + push
            w = rg["w"](p) if callable(rg["w"]) else rg["w"]
            row.append(B.vert(p, w))
        grid.append(row)
    for i in range(len(rings) - 1):
        v0, v1 = rings[i]["v"], rings[i + 1]["v"]
        for j in range(sides):
            j1 = j + 1
            q = [grid[i][j], grid[i][j1 % sides], grid[i + 1][j1 % sides], grid[i + 1][j]]
            u0, u1 = 1 - j / sides, 1 - j1 / sides
            B.face(q, [atlas_uv(region, u0, v0), atlas_uv(region, u1, v0),
                       atlas_uv(region, u1, v1), atlas_uv(region, u0, v1)])
    for k, cap in enumerate(caps):
        if cap is None:
            continue
        ring = grid[0] if k == 0 else grid[-1]
        v = rings[0]["v"] if k == 0 else rings[-1]["v"]
        if cap == "flat":
            B.face(list(ring), [atlas_uv(region, 1 - j / sides, v) for j in range(sides)])
            continue
        cv = B.vert(Vector(cap["p"]), cap["w"])
        for j in range(sides):
            j1 = (j + 1) % sides
            B.face([ring[j], ring[j1], cv], [atlas_uv(region, 1 - j / sides, v),
                                             atlas_uv(region, 1 - (j + 1) / sides, v),
                                             atlas_uv(region, 1 - (j + 0.5) / sides, cap["v"])])
    return grid


def rect_tube(B, pts, sizes, weights, a_axis):
    """Tubo de seccion rectangular (manos, pulgar) con UV plano: dorso y palma."""
    rings = []
    for c, (hw, ht), w in zip(pts, sizes, weights):
        c = Vector(c)
        ring = []
        for sa, sb in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            p = c + a_axis * (sa * hw) + UP * (sb * ht)
            ring.append((p, B.vert(p, w)))
        rings.append((c, ring))

    def uv(p, top):
        x0, y0, _, _ = REG["hand"]
        col = min(max((abs(p.x) - HAND_X0) / HAND_LEN * 31, 0), 31) + (0 if top else 32)
        row = min(max((p.y + 0.055) / 0.11 * 63, 0), 63)
        return ((x0 + 0.5 + col) / TEX, 1 - (y0 + 0.5 + row) / TEX)

    for i in range(len(rings) - 1):
        c0, r0 = rings[i]
        c1, r1 = rings[i + 1]
        mid_c = (c0 + c1) / 2
        for j in range(4):
            j1 = (j + 1) % 4
            quad = [r0[j], r0[j1], r1[j1], r1[j]]
            fc = sum((q[0] for q in quad), Vector()) / 4
            top = (fc - mid_c).dot(UP) > -1e-4
            B.face([q[1] for q in quad], [uv(q[0], top) for q in quad])
    for c, ring in (rings[0], rings[-1]):
        B.face([q[1] for q in ring], [uv(q[0], True) for q in ring])


# Pesos del torso a lo largo de la columna
SPINE_W = {0.86: {"Hips": 0.6, "Spine": 0.4}, 0.93: {"Hips": 0.2, "Spine": 0.8},
           1.01: {"Spine": 0.5, "Spine1": 0.5}, 1.09: {"Spine1": 1.0}, 1.16: {"Spine1": 0.3, "Spine2": 0.7},
           1.22: {"Spine2": 1.0}, 1.265: {"Spine2": 0.7, "Neck": 0.3}}


def torso_w(z):
    def f(p):
        w = dict(SPINE_W[z])
        if z >= 1.15 and abs(p.x) > 0.10:
            k = min(1.0, (abs(p.x) - 0.10) / 0.06) * 0.5
            w = {b: v * (1 - k) for b, v in w.items()}
            w[("Left" if p.x > 0 else "Right") + "Shoulder"] = k
        return w
    return f


def skirt_w(k):
    """La falda va con la cadera arriba; abajo se reparte con el muslo de su lado."""
    def f(p):
        if k <= 0:
            return {"Hips": 1.0}
        side = min(1.0, abs(p.x) / 0.07)
        main = ("Left" if p.x > 0 else "Right") + "UpLeg"
        other = ("Right" if p.x > 0 else "Left") + "UpLeg"
        return {"Hips": 1 - k, main: k * (0.5 + 0.5 * side), other: k * (0.5 - 0.5 * side)}
    return f


def blend_w(a, b, t):
    if t <= 0:
        return {a: 1.0}
    if t >= 1:
        return {b: 1.0}
    return {a: 1 - t, b: t}


def build_mesh(mat):
    B = Builder()
    X, Z = Vector((1, 0, 0)), Vector((0, 0, 1))
    F = Vector((0, -1, 0))

    # Falda (vestido y delantal), acampanada, con un poco de panza
    def belly(amount):
        return lambda j: Vector((0, -amount * (1.0 if j == 6 else 0.6 if j in (5, 7) else 0.0), 0))
    rings = [dict(c=Vector((0, 0.005, z)), rx=rx, ry=ry, v=vfrac("skirt", z), w=skirt_w(k), push=belly(b))
             for z, rx, ry, k, b in ((0.92, 0.160, 0.125, 0.0, 0.0), (0.85, 0.195, 0.150, 0.0, 0.018),
                                     (0.70, 0.205, 0.158, 0.25, 0.010), (0.52, 0.205, 0.160, 0.45, 0.0),
                                     (0.33, 0.198, 0.156, 0.60, 0.0))]
    tube(B, rings, 12, "skirt", X, F, caps=(None, "flat"))

    # Torso (chaleco): busto adelante y la joroba de la espalda
    rings = []
    for z, rx, ry, bust, hump in ((0.86, 0.205, 0.155, 0.0, 0.0), (0.93, 0.182, 0.138, 0.0, 0.0),
                                  (1.01, 0.178, 0.140, 0.010, 0.0), (1.09, 0.182, 0.150, 0.030, 0.0),
                                  (1.16, 0.180, 0.140, 0.018, 0.012), (1.22, 0.158, 0.112, 0.0, 0.028),
                                  (1.265, 0.082, 0.065, 0.0, 0.015)):
        def push(j, bust=bust, hump=hump):
            fr = 1.0 if j == 5 else 0.7 if j in (4, 6) else 0.0
            bk = 1.0 if j == 0 else 0.6 if j in (1, 9) else 0.0
            return Vector((0, -bust * fr + hump * bk, 0))
        rings.append(dict(c=Vector((0, 0, z)), rx=rx, ry=ry, v=vfrac("torso", z), w=torso_w(z), push=push))
    tube(B, rings, 10, "torso", X, F, caps=("flat", "flat"))

    # Cuello
    rings = [dict(c=Vector((0, dy, z)), rx=r, ry=r * 1.05, v=vfrac("neck", z), w=w)
             for z, r, dy, w in ((1.25, 0.053, 0.0, {"Spine2": 0.4, "Neck": 0.6}), (1.285, 0.050, -0.005, {"Neck": 1.0}),
                                 (1.33, 0.049, -0.012, {"Neck": 0.4, "Head": 0.6}))]
    tube(B, rings, 6, "neck", X, F)

    # Cabeza: el vertice del frente (j=5) forma la nariz
    head = [(1.335, 0.043, 0.046, -0.028, 0.0), (1.362, 0.065, 0.071, -0.010, 0.0),
            (1.400, 0.069, 0.081, -0.002, 0.017), (1.437, 0.073, 0.086, 0.004, 0.005),
            (1.475, 0.077, 0.091, 0.008, 0.003), (1.512, 0.079, 0.093, 0.010, 0.0),
            (1.545, 0.063, 0.076, 0.012, 0.0)]
    rings = [dict(c=Vector((0, dy, z + HEAD_DZ)), rx=rx, ry=ry, v=vfrac("head", z + HEAD_DZ), w={"Head": 1.0},
                  push=lambda j, nose=nose: Vector((0, -nose if j == 5 else 0.0, 0)))
             for z, rx, ry, dy, nose in head]
    tube(B, rings, 10, "head", X, F,
         caps=(dict(p=(0, -0.008, 1.343 + HEAD_DZ), w={"Head": 1.0}, v=1.0),
               dict(p=(0, 0.012, 1.566 + HEAD_DZ), w={"Head": 1.0}, v=0.0)))

    # Mono (rodete) atras y arriba de la cabeza
    rings = [dict(c=Vector((0, y, z + HEAD_DZ)), rx=r, ry=r * 0.88, v=vfrac("bun", y), w={"Head": 1.0})
             for y, z, r in ((0.070, 1.505, 0.030), (0.088, 1.512, 0.047), (0.112, 1.522, 0.050), (0.132, 1.530, 0.037))]
    tube(B, rings, 8, "bun", X, Z, caps=(None, dict(p=(0, 0.144, 1.535 + HEAD_DZ), w={"Head": 1.0}, v=1.0)))

    # Brazos (mangas del chaleco) y manos
    for s, nm in ((1, "Left"), (-1, "Right")):
        sh, ar, fa, ha = nm + "Shoulder", nm + "Arm", nm + "ForeArm", nm + "Hand"
        spec = [(0.13, 0.050, {sh: 0.85, ar: 0.15}), (0.19, 0.057, {sh: 0.15, ar: 0.85}), (0.30, 0.055, {ar: 1.0}),
                (0.375, 0.053, blend_w(ar, fa, 0.2)), (0.41, 0.053, blend_w(ar, fa, 0.5)),
                (0.445, 0.051, blend_w(ar, fa, 0.8)), (0.53, 0.047, {fa: 1.0}), (0.60, 0.045, {fa: 1.0}),
                (0.625, 0.047, {fa: 1.0})]
        rings = [dict(c=Vector((x * s, 0.005, 1.215)), rx=r, ry=r * 1.05, v=vfrac("arm", x), w=w) for x, r, w in spec]
        tube(B, rings, 6, "arm", Z, F, caps=("flat", "flat"))
        pts = [(0.62 * s, 0.0, 1.215), (0.67 * s, 0.0, 1.215), (0.72 * s, 0.0, 1.212), (0.785 * s, 0.0, 1.204)]
        sizes = [(0.024, 0.015), (0.039, 0.016), (0.041, 0.013), (0.033, 0.009)]
        rect_tube(B, pts, sizes, [{fa: 0.3, ha: 0.7}, {ha: 1.0}, {ha: 1.0}, {ha: 1.0}], Vector((0, 1, 0)))
        thumb = [(0.64 * s, -0.028, 1.208), (0.68 * s, -0.054, 1.199), (0.71 * s, -0.064, 1.195)]
        rect_tube(B, thumb, [(0.011, 0.010), (0.010, 0.009), (0.008, 0.007)], [{ha: 1.0}] * 3, X)

    # Pantorrillas (con medias) y pantuflas. Los muslos no hacen falta: los tapa la falda.
    for s, nm in ((1, "Left"), (-1, "Right")):
        ul, lg, ft, to = nm + "UpLeg", nm + "Leg", nm + "Foot", nm + "ToeBase"
        spec = [(0.52, 0.058, 0.0, blend_w(ul, lg, 0.3)), (0.445, 0.056, 0.0, blend_w(ul, lg, 0.6)),
                (0.36, 0.058, 0.006, {lg: 1.0}), (0.27, 0.054, 0.004, {lg: 1.0}), (0.17, 0.047, 0.0, {lg: 1.0}),
                (0.075, 0.046, 0.0, {lg: 1.0})]
        rings = [dict(c=Vector((0.095 * s, dy, z)), rx=r, ry=r, v=vfrac("leg", z), w=w) for z, r, dy, w in spec]
        tube(B, rings, 6, "leg", X, F, caps=("flat", "flat"))
        spec = [(0.06, 0.040, 0.034, {ft: 1.0}), (0.02, 0.048, 0.040, {ft: 1.0}), (-0.06, 0.052, 0.036, {ft: 1.0}),
                (-0.13, 0.046, 0.028, {ft: 0.4, to: 0.6}), (-0.175, 0.030, 0.019, {to: 1.0})]
        rings = [dict(c=Vector((0.095 * s, y, hh)), rx=hw, ry=hh, v=vfrac("foot", y), w=w) for y, hw, hh, w in spec]
        tube(B, rings, 8, "foot", X, Z, caps=("flat", "flat"), flat=True)

    bmesh.ops.recalc_face_normals(B.bm, faces=B.bm.faces)
    me = bpy.data.meshes.new("Carmen")
    B.bm.to_mesh(me)
    B.bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new("Carmen", me)
    for n in BONES:
        ob.vertex_groups.new(name=n)
    return ob


def build_rig():
    arm = bpy.data.armatures.new("Carmen_Rig")
    ob = bpy.data.objects.new("Carmen_Rig", arm)
    scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    for name, (head, tail, parent, z) in LAYOUT.items():
        b = eb.new(name)
        b.head, b.tail = head, tail
        b.align_roll(z)
        if parent:
            b.parent = eb[parent]
            b.use_connect = (eb[parent].tail - b.head).length < 1e-5
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in ob.pose.bones:
        pb.rotation_mode = "QUATERNION"
    arm.display_type = "STICK"
    return ob


# El plato: peltre blanco con borde azul, tapado con una servilleta bordada.
# Textura de 64x64: servilleta en x 0-47, y 0-47; peltre en x 48-63, y 0-31.
PLATE_TEX = 64


def build_plate(mat):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")

    def puv(col, row):
        return ((col + 0.5) / PLATE_TEX, 1 - (row + 0.5) / PLATE_TEX)

    def face(verts, uvs):
        f = bm.faces.new(verts)
        for loop, uv in zip(f.loops, uvs):
            loop[uvl].uv = uv
        return f

    sides = 10
    dish = [(0.065, 0.0, 15), (0.100, 0.010, 8), (0.115, 0.022, 1)]   # (radio, altura, fila)
    grid = []
    for r, z, _ in dish:
        grid.append([bm.verts.new((r * math.cos(2 * math.pi * j / sides), r * math.sin(2 * math.pi * j / sides), z))
                     for j in range(sides)])
    for i in range(len(dish) - 1):
        for j in range(sides):
            j1 = (j + 1) % sides
            c0, c1 = 48 + 15 * j / sides, 48 + 15 * (j + 1) / sides
            face([grid[i][j], grid[i][j1], grid[i + 1][j1], grid[i + 1][j]],
                 [puv(c0, dish[i][2]), puv(c1, dish[i][2]), puv(c1, dish[i + 1][2]), puv(c0, dish[i + 1][2])])
    face(list(reversed(grid[0])), [puv(55, 24)] * sides)
    face(list(grid[-1]), [puv(55, 24)] * sides)

    # Servilleta: un domo sobre la comida y las puntas caidas
    def cloth_z(r):
        if r <= 0.10:
            return 0.026 + 0.075 * (1 - (r / 0.10) ** 2) ** 0.6
        if r <= 0.125:
            return 0.026
        return max(0.002, 0.026 - (r - 0.125) * 1.4)

    n, half = 7, 0.135
    cv = []
    for i in range(n):
        row = []
        for j in range(n):
            x, y = -half + 2 * half * i / (n - 1), -half + 2 * half * j / (n - 1)
            row.append((bm.verts.new((x, y, cloth_z(math.hypot(x, y)))), (i / (n - 1), j / (n - 1))))
        cv.append(row)
    for i in range(n - 1):
        for j in range(n - 1):
            q = [cv[i][j], cv[i + 1][j], cv[i + 1][j + 1], cv[i][j + 1]]
            face([a[0] for a in q], [puv(a[1][0] * 47, a[1][1] * 47) for a in q])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Carmen_Plato")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.materials.append(mat)
    return bpy.data.objects.new("Carmen_Plato", me)


# ---------------------------------------------------------------------------
# Texturas: se pintan sobre la superficie (angulo alrededor de la pieza y altura)
# ---------------------------------------------------------------------------
def noise(h, w, cy, cx):
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


def dang(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def cyl(name):
    """Angulo T (grados; 90 = frente) y parametro P (altura o largo) de cada pixel de la region."""
    _, _, w, h = REG[name]
    a, b = SPAN[name]
    r = np.arange(h)[:, None].astype(float)
    c = np.arange(w)[None, :].astype(float)
    P = a + r / (h - 1) * (b - a) + 0 * c
    T = 270.0 - 360.0 * c / (w - 1) + 0 * r
    return T, P


def ell(T, P, t0, p0, dt, dp):
    return (dang(T, t0) / dt) ** 2 + ((P - p0) / dp) ** 2 <= 1.0


def view(A, name):
    x0, y0, w, h = REG[name]
    return A[y0:y0 + h, x0:x0 + w]


def mix(img, mask, color, a):
    img[mask] = img[mask] * (1 - a) + np.array(color) * a


def grid_rc(img):
    h, w, _ = img.shape
    return np.arange(h)[:, None] + 0 * np.arange(w)[None, :], 0 * np.arange(h)[:, None] + np.arange(w)[None, :]


def walk_lines(img, mask_fn, n, length, color, a, rs):
    """Venas: caminatas al azar."""
    h, w, _ = img.shape
    for _ in range(n):
        r, c = int(rs.integers(0, h)), int(rs.integers(0, w))
        for _k in range(length):
            if 0 <= r < h and mask_fn(r, c % w):
                img[r, c % w] = img[r, c % w] * (1 - a) + np.array(color) * a
            r += int(rs.integers(-1, 2))
            c += int(rs.integers(-1, 2))


def frac(x):
    return x - np.floor(x)


def palette(outfit):
    night = outfit == "noche"
    p = dict(
        skin=(0.64, 0.47, 0.37), skin_dark=(0.48, 0.33, 0.26), hair=(0.60, 0.59, 0.57), hair_dark=(0.38, 0.37, 0.36),
        brow=(0.38, 0.35, 0.32), lips=(0.52, 0.37, 0.35) if night else (0.58, 0.30, 0.31),
        frame=(0.15, 0.09, 0.05), iris=(0.17, 0.10, 0.06), dress=(0.085, 0.085, 0.105), knit=(0.45, 0.40, 0.33),
        apron=(0.40, 0.54, 0.64), robe=(0.62, 0.44, 0.50), gown=(0.80, 0.77, 0.68), stocking=(0.70, 0.55, 0.45),
        slipper=(0.36, 0.12, 0.16), brown=(0.30, 0.19, 0.10), gold=(0.78, 0.62, 0.26), net=(0.22, 0.20, 0.22),
    )
    return {k: np.array(v) for k, v in p.items()}


def dress_print(img, pal):
    """Vestido de luto: azul casi negro con lunares chiquitos."""
    rr, cc = grid_rc(img)
    h, w, _ = img.shape
    img[:] = pal["dress"] * (0.85 + 0.3 * noise(h, w, 6, 10))[:, :, None]
    dots = ((rr % 6 == 0) & (cc % 6 == 0)) | ((rr % 6 == 3) & (cc % 6 == 3))
    mix(img, dots, (0.30, 0.30, 0.36), 0.6)


def apron_print(img, pal):
    """Delantal celeste con florcitas blancas y rosadas."""
    rr, cc = grid_rc(img)
    h, w, _ = img.shape
    img[:] = pal["apron"] * (0.90 + 0.15 * noise(h, w, 6, 10))[:, :, None]
    mix(img, (rr % 5 == 0) & ((cc + (rr // 5) * 3) % 6 == 0), (0.90, 0.90, 0.86), 0.85)
    mix(img, (rr % 5 == 2) & ((cc + (rr // 5) * 3) % 6 == 3), (0.86, 0.56, 0.62), 0.75)


def gown_print(img, pal):
    rr, cc = grid_rc(img)
    img[:] = pal["gown"]
    mix(img, (rr % 4 == 0) & ((cc + rr) % 5 == 0), (0.55, 0.62, 0.78), 0.6)


def quilt(img, T, P, k=0.75):
    """Pespuntes en rombos de la bata acolchada."""
    a = T / 11.0 + P / 0.032
    b = T / 11.0 - P / 0.032
    lines = (frac(a) < 0.16) | (frac(b) < 0.16)
    mix(img, lines, (0, 0, 0), 1 - k)


def hairnet(img, mask, T, P, pal):
    a = T / 9.0 + P / 0.011
    b = T / 9.0 - P / 0.011
    mix(img, mask & ((frac(a) < 0.2) | (frac(b) < 0.2)), pal["net"], 0.45)


def paint_head(A, outfit, pal, rs):
    img = view(A, "head")
    T, P = cyl("head")
    P = P - HEAD_DZ          # se pinta en las alturas en que se diseno la cabeza
    d = dang(T, 90.0)
    ad = np.abs(d)
    h, w, _ = img.shape
    img[:] = pal["skin"] * (0.93 + 0.07 * noise(h, w, 6, 12))[:, :, None]
    mix(img, P < 1.352, pal["skin_dark"], 0.35)                                          # bajo el menton
    mix(img, (ad > 16) & (ad < 42) & (P < 1.372) & (P > 1.350), pal["skin_dark"], 0.25)  # papada
    mix(img, ell(T, P, 90 + 27, 1.405, 9, 0.012) | ell(T, P, 90 - 27, 1.405, 9, 0.012), (0.80, 0.42, 0.38), 0.14)
    mix(img, ell(T, P, 90 - 25, 1.392, 1.6, 0.0022), (0.22, 0.13, 0.08), 0.8)           # lunar

    # Nariz y surcos
    for sg in (-1, 1):
        mix(img, ell(T, P, 90 + 3.5 * sg, 1.3975, 1.4, 0.0018), (0, 0, 0), 0.35)
        fold = (P > 1.374) & (P < 1.396) & (np.abs(sg * d - (10 + (1.396 - P) / 0.022 * 4)) < 1.4)
        mix(img, fold, pal["skin_dark"], 0.30)
    mix(img, ell(T, P, 90, 1.393, 6, 0.0022), (0, 0, 0), 0.10)

    # Boca: labios finos, comisuras un poco caidas (preocupada)
    zl = 1.372
    curve = zl - 0.0013 * (ad / 10) ** 2
    lips = (ad < 10) & (np.abs(P - curve) < 0.0028)
    img[lips] = pal["lips"]
    mix(img, (ad < 10) & (np.abs(P - curve) < 0.0006), (0, 0, 0), 0.5)

    # Ojos (agrandados por los lentes de leer), bolsas y patas de gallo
    ze = 1.437
    for sg in (-1, 1):
        te = 90 + 20 * sg
        mix(img, ell(T, P, te, ze - 0.0075, 9, 0.004), pal["skin_dark"], 0.45)
        mix(img, ell(T, P, te, ze + 0.0068, 8.5, 0.0024), pal["skin_dark"], 0.35)      # parpado caido
        img[ell(T, P, te, ze, 7.5, 0.0044)] = (0.70, 0.66, 0.60)
        img[ell(T, P, te, ze - 0.0003, 3.0, 0.0042)] = pal["iris"]
        img[ell(T, P, te, ze + 0.0042, 8.0, 0.0012)] = pal["iris"] * 0.8
        x = sg * d
        for k in (-1, 0, 1):
            crow = (x > 34) & (x < 41) & (np.abs(P - (ze + k * 0.0035 * (1 + (x - 34) / 7))) < 0.0009)
            mix(img, crow, pal["skin_dark"], 0.5)
        # Cejas finas, con la punta de adentro levantada
        bh = 1.4555 + 0.0035 * np.clip(1 - (x - 8) / 22, 0, 1)
        mix(img, (x > 8) & (x < 30) & (np.abs(P - bh) < 0.0016), pal["brow"], 0.8)
    for zf in (1.474, 1.481):                                                            # arrugas de la frente
        mix(img, (ad < 22) & (np.abs(P - zf - 0.0012 * np.sin(d / 5)) < 0.0009), pal["skin_dark"], 0.3)

    # Lentes: marco de carey, puente y patillas hasta las orejas
    for sg in (-1, 1):
        te, zc = 90 + 20 * sg, ze + 0.001
        rr_ = ((np.abs(dang(T, te)) / 13.0) ** 3 + (np.abs(P - zc) / 0.0125) ** 3) ** (1 / 3)
        mix(img, rr_ < 0.86, (1, 1, 1), 0.10)
        img[np.abs(rr_ - 1) < 0.15] = pal["frame"]
        img[(sg * d > 33) & (sg * d < 82) & (np.abs(P - (ze + 0.005)) < 0.0012)] = pal["frame"]
    img[(ad < 7) & (np.abs(P - (ze + 0.004)) < 0.0013)] = pal["frame"]

    # Pelo canoso, tirado para atras, con raya al medio
    hl = np.where(ad < 28, 1.494, np.where(ad < 78, 1.494 - (ad - 28) / 50 * 0.044, 1.450 - (ad - 78) / 102 * 0.072))
    hair = P > hl + (noise(h, w, 4, 36) - 0.5) * 0.006
    hair_col = pal["hair"] * (0.72 + 0.40 * noise(h, w, 3, 64))[:, :, None]   # mechones peinados hacia atras
    img[hair] = hair_col[hair]
    mix(img, hair & (noise(h, w, 2, 40) > 0.6), pal["hair_dark"], 0.35)
    mix(img, hair & (P < hl + 0.006), pal["hair_dark"], 0.25)
    mix(img, (ad < 1.6) & (P > 1.50), pal["skin"], 0.3)
    if outfit == "noche":
        hairnet(img, hair, T, P, pal)

    # Orejas y aretes
    for sg in (-1, 1):
        img[ell(T, P, 90 + 86 * sg, 1.425, 6.5, 0.020)] = pal["skin"] * 0.92
        mix(img, ell(T, P, 90 + 86 * sg, 1.425, 3, 0.009), (0, 0, 0), 0.3)
        img[ell(T, P, 90 + 86 * sg, 1.408, 2.4, 0.0035)] = pal["gold"]


def paint_bun(A, outfit, pal, rs):
    img = view(A, "bun")
    T, P = cyl("bun")
    h, w, _ = img.shape
    img[:] = pal["hair"] * (0.85 + 0.3 * noise(h, w, 6, 6))[:, :, None]
    swirl = np.sin(np.radians(T) + (P - 0.075) / 0.077 * 4 * np.pi)
    mix(img, swirl > 0.55, pal["hair_dark"], 0.45)
    mix(img, P < 0.088, pal["hair_dark"], 0.35)
    for t0, p0, p1 in ((60, 0.095, 0.12), (200, 0.10, 0.125)):                        # horquillas
        mix(img, (np.abs(dang(T, t0)) < 5) & (P > p0) & (P < p1), (0.05, 0.05, 0.05), 0.85)
    if outfit == "noche":
        hairnet(img, np.ones(P.shape, bool), T, P, pal)


def paint_neck(A, outfit, pal, rs):
    img = view(A, "neck")
    T, P = cyl("neck")
    h, w, _ = img.shape
    img[:] = pal["skin"] * (0.92 + 0.08 * noise(h, w, 4, 8))[:, :, None]
    mix(img, P > 1.335, pal["skin_dark"], 0.35)
    for z in (1.285, 1.305):
        mix(img, (np.abs(dang(T, 90)) < 60) & (np.abs(P - z) < 0.0035), pal["skin_dark"], 0.3)


def paint_torso(A, outfit, pal, rs):
    img = view(A, "torso")
    T, P = cyl("torso")
    d = dang(T, 90.0)
    ad = np.abs(d)
    h, w, _ = img.shape
    vw = np.where(P > 1.10, 8 + (P - 1.10) / 0.165 * 30, -1.0)       # escote en V
    opening = ad < vw
    inner = np.zeros_like(img)
    if outfit == "dia":
        rib = (np.round(T / 2.8) % 2) == 0
        img[:] = pal["knit"] * (0.90 + 0.10 * noise(h, w, 10, 20))[:, :, None] * np.where(rib, 1.0, 0.92)[:, :, None]
        dress_print(inner, pal)
        img[opening] = inner[opening]
        img[(np.abs(ad - vw) < 2.6) & (P > 1.095)] = pal["knit"] * 0.78   # borde tejido
        img[(ad < 2.6) & (P <= 1.10)] = pal["knit"] * 0.78                 # tapeta
        buttons = (ad < 1.9) & (P > 0.90) & (P < 1.10) & (np.abs((P - 0.905) % 0.048) < 0.006)
        img[buttons] = (0.72, 0.66, 0.54)
        for sg in (-1, 1):                                                   # bolsillos
            box = (np.abs(d - 40 * sg) < 12) & (P > 0.905) & (P < 0.985)
            edge = box & ((np.abs(np.abs(d - 40 * sg) - 12) < 1.6) | (P > 0.978))
            mix(img, edge, (0, 0, 0), 0.25)
        img[P < 0.89] = pal["knit"] * 0.84 * np.where(rib, 1.0, 0.9)[P < 0.89][:, None]
        # Delantal atado a la cintura, con el mono atras
        apron = np.zeros_like(img)
        apron_print(apron, pal)
        front = (ad < 52) & (P < 0.893)
        img[front] = apron[front]
        img[(P >= 0.893) & (P < 0.908)] = pal["apron"] * 1.12
        mix(img, ell(T, P, 270, 0.900, 8, 0.013), pal["apron"] * 1.2, 0.9)
        for t0 in (266, 275):
            img[(np.abs(dang(T, t0)) < 1.8) & (P > 0.86) & (P < 0.90)] = pal["apron"] * 1.1
    else:
        img[:] = pal["robe"] * (0.92 + 0.08 * noise(h, w, 8, 16))[:, :, None]
        quilt(img, T, P)
        gown_print(inner, pal)
        img[opening] = inner[opening]
        mix(img, opening & (P > 1.245), (1, 1, 1), 0.5)                    # puntilla del camison
        collar = (np.abs(ad - vw) < 4.5) & (P > 1.08)
        img[collar] = pal["robe"] * 1.15                                    # cuello de raso
        img[(P > 0.893) & (P < 0.918)] = pal["robe"] * 0.86                 # cinturon
        mix(img, ell(T, P, 60, 0.905, 6, 0.02), pal["robe"] * 0.95, 1.0)    # el nudo
        for t0 in (57, 63):
            img[(np.abs(dang(T, t0)) < 1.8) & (P > 0.86) & (P < 0.90)] = pal["robe"] * 0.86
        img[P < 0.875] = pal["robe"] * 1.08
    # Escapulario de la Virgen del Carmen: el cordon y el recuadro de tela marron
    for sg in (-1, 1):
        cord = (sg * d > 0) & (P > 1.168) & (P < 1.262) & (np.abs(sg * d - (1.5 + (P - 1.168) / 0.094 * 30)) < 1.1)
        img[cord] = pal["brown"] * 0.8
    img[(ad < 3.4) & (P > 1.148) & (P < 1.170)] = pal["brown"]
    img[(ad < 1.8) & (P > 1.153) & (P < 1.165)] = (0.60, 0.48, 0.30)


def paint_skirt(A, outfit, pal, rs):
    img = view(A, "skirt")
    T, P = cyl("skirt")
    d = dang(T, 90.0)
    ad = np.abs(d)
    h, w, _ = img.shape
    if outfit == "dia":
        dress_print(img, pal)
        mix(img, np.abs(frac(T / 30.0) - 0.5) > 0.44, (0, 0, 0), 0.25)       # pliegues
        apron = np.zeros_like(img)
        apron_print(apron, pal)
        front = (ad < 54) & (P > 0.50)
        img[front] = apron[front]
        trim = ((np.abs(ad - 54) < 1.6) & (P > 0.50)) | ((ad < 55) & (np.abs(P - 0.50) < 0.005))
        img[trim] = (0.86, 0.85, 0.80)
        for sg in (-1, 1):
            pocket = (np.abs(d - 22 * sg) < 11) & (P > 0.64) & (P < 0.73)
            edge = pocket & ((np.abs(np.abs(d - 22 * sg) - 11) < 1.5) | (P < 0.647))
            mix(img, edge, (0, 0, 0), 0.3)
            img[(np.abs(d - 22 * sg) < 11) & (np.abs(P - 0.726) < 0.004)] = (0.86, 0.85, 0.80)
        img[P < 0.345] = pal["dress"] * 0.6
    else:
        img[:] = pal["robe"] * (0.92 + 0.08 * noise(h, w, 8, 16))[:, :, None]
        quilt(img, T, P)
        img[np.abs(d + 14) < 1.3] = pal["robe"] * 0.65                       # la bata cruzada
        img[(d > -14) & (d < -10)] = pal["robe"] * 1.12
        for sg in (-1, 1):
            pocket = (np.abs(d - 40 * sg) < 12) & (P > 0.66) & (P < 0.75)
            edge = pocket & ((np.abs(np.abs(d - 40 * sg) - 12) < 1.6) | (P > 0.744))
            mix(img, edge, (0, 0, 0), 0.3)
        img[(P >= 0.352) & (P < 0.362)] = pal["robe"] * 0.8
        img[P < 0.352] = pal["gown"]                                          # asoma el camison
        mix(img, (P < 0.346) & ((np.round(T / 3) % 2) == 0), (1, 1, 1), 0.4)
        img[P < 0.338] = pal["gown"] * 0.45


def paint_arm(A, outfit, pal, rs):
    img = view(A, "arm")
    T, P = cyl("arm")
    d = dang(T, 90.0)
    h, w, _ = img.shape
    if outfit == "dia":
        rib = (np.round(T / 6) % 2) == 0
        img[:] = pal["knit"] * (0.90 + 0.10 * noise(h, w, 12, 6))[:, :, None] * np.where(rib, 1.0, 0.93)[:, :, None]
        cuff = P > 0.585
        img[cuff] = pal["knit"] * 0.84 * np.where(rib, 1.0, 0.88)[cuff][:, None]
        mix(img, ell(T, P, 270, 0.41, 40, 0.03), (0, 0, 0), 0.12)                # codo gastado
    else:
        img[:] = pal["robe"] * (0.92 + 0.08 * noise(h, w, 10, 6))[:, :, None]
        quilt(img, T, P * 1.8)
        img[P > 0.58] = pal["robe"] * 1.15
    mix(img, np.abs(dang(T, 270)) < 3, (0, 0, 0), 0.2)


def paint_leg(A, outfit, pal, rs):
    img = view(A, "leg")
    T, P = cyl("leg")
    h, w, _ = img.shape
    img[:] = pal["skin"] * (0.92 + 0.08 * noise(h, w, 8, 4))[:, :, None]
    if outfit == "dia":
        sto = P < 0.305
        img[sto] = (pal["stocking"] * (0.94 + 0.06 * noise(h, w, 10, 4))[:, :, None])[sto]
        mix(img, sto & (np.abs(dang(T, 90)) < 25), (1, 1, 1), 0.10)
        img[(P >= 0.305) & (P < 0.322)] = pal["stocking"] * 0.80              # la media enrollada
        img[(P >= 0.311) & (P < 0.316)] = pal["stocking"] * 0.66
    else:
        walk_lines(img, lambda r, c: P[r, c] < 0.40, 10, 16, (0.40, 0.28, 0.44), 0.45, rs)  # varices
        mix(img, P < 0.12, pal["skin_dark"], 0.25)


def paint_hand(A, outfit, pal, rs):
    img = view(A, "hand")
    h, w, _ = img.shape
    rr, cc = grid_rc(img)
    x = HAND_X0 + (cc % 32) / 31 * HAND_LEN     # a lo largo de la mano
    y = -0.055 + rr / 63 * 0.11                  # de lado a lado (arriba = pulgar)
    top = cc < 32                                # dorso
    img[:] = pal["skin"] * (0.92 + 0.08 * noise(h, w, 6, 6))[:, :, None]
    mix(img, ~top, (1, 0.9, 0.85), 0.08)
    for yc in (-0.016, 0.0, 0.016):                                   # separacion de los dedos
        mix(img, (np.abs(y - yc) < 0.0016) & (x > 0.705), (0, 0, 0), 0.45)
    for yc in (-0.024, -0.008, 0.008, 0.024):
        mix(img, top & (np.abs(y - yc) < 0.004) & (np.abs(x - 0.70) < 0.004), pal["skin_dark"], 0.5)  # nudillos
        img[top & (np.abs(y - yc) < 0.0045) & (x > 0.772)] = (0.74, 0.62, 0.56)                        # unas
    mix(img, top & (rs.random((h, w)) > 0.975) & (x < 0.70), (0.40, 0.25, 0.16), 0.6)                 # manchas
    mix(img, top & (np.abs(y + 0.004 - (x - 0.62) * 0.15) < 0.0014) & (x < 0.70), (0.32, 0.34, 0.50), 0.45)
    mix(img, ~top & (np.abs(x - 0.68 - (y + 0.03) * 0.4) < 0.002), (0, 0, 0), 0.3)


def paint_foot(A, outfit, pal, rs):
    img = view(A, "foot")
    h, w, _ = img.shape
    rr, cc = grid_rc(img)
    u = cc / (w - 1)
    img[:] = pal["slipper"] * (0.82 + 0.36 * noise(h, w, 20, 20))[:, :, None]   # felpa
    img[(u < 0.14) | (u > 0.86)] = (0.20, 0.18, 0.17)                           # suela
    img[(np.abs(rr - 22) < 2.5) & (np.abs(u - 0.5) < 0.22)] = (0.62, 0.42, 0.44)  # borde de peluche
    pom = ((rr - 40) / 4.0) ** 2 + ((u - 0.5) / 0.07) ** 2 < 1
    img[pom] = (0.70, 0.48, 0.50)
    mix(img, (rr > 52) & (noise(h, w, 5, 5) > 0.45), (0.15, 0.12, 0.10), 0.35)


def build_texture(outfit):
    rs = np.random.default_rng(300 + OUTFITS.index(outfit))
    A = np.zeros((TEX, TEX, 3))
    pal = palette(outfit)
    for fn in (paint_head, paint_bun, paint_neck, paint_torso, paint_skirt, paint_arm, paint_leg,
               paint_hand, paint_foot):
        fn(A, outfit, pal, rs)
    return np.clip(A, 0, 1)


def build_plate_texture():
    """Servilleta blanca con flores bordadas en el borde y un ramito en una punta; peltre."""
    n = PLATE_TEX
    A = np.zeros((n, n, 3))
    cloth = A[0:48, 0:48]
    rr, cc = grid_rc(cloth)
    cloth[:] = np.array((0.86, 0.84, 0.77)) * (0.94 + 0.06 * noise(48, 48, 6, 6))[:, :, None]
    edge = np.minimum(np.minimum(rr, cc), np.minimum(47 - rr, 47 - cc))
    cloth[edge == 0] = (0.70, 0.66, 0.58)
    colors = [(0.75, 0.18, 0.16), (0.88, 0.70, 0.20), (0.22, 0.36, 0.68), (0.82, 0.45, 0.58)]
    k = 0
    for i in range(4, 44, 5):
        for (r, c) in ((3, i), (44, i), (i, 3), (i, 44)):
            col = colors[k % 4]
            k += 1
            for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                cloth[r + dr, c + dc] = col
            cloth[r, c] = (0.92, 0.85, 0.40)
            if i + 2 < 44:
                rr2, cc2 = (r, c + 2) if r in (3, 44) else (r + 2, c)
                cloth[rr2, cc2] = (0.25, 0.50, 0.25)
    for (r, c, col) in ((9, 9, 0), (11, 12, 3), (13, 9, 1), (8, 13, 2)):                 # ramito
        for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            cloth[r + dr, c + dc] = colors[col]
    for r, c in ((12, 10), (14, 12), (15, 13), (10, 14)):
        cloth[r, c] = (0.25, 0.50, 0.25)
    peltre = A[0:32, 48:64]
    peltre[:] = (0.84, 0.84, 0.82)
    peltre[0:4] = (0.07, 0.11, 0.30)                                                    # borde azul
    peltre[(rng.random((32, 16)) > 0.96)] = (0.05, 0.05, 0.06)                           # saltaduras
    return np.clip(A, 0, 1)


def save_texture(name, rgb_top_down):
    rgb = np.flipud(rgb_top_down)
    h, w, _ = rgb.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = rgb
    path = os.path.join(TEX_DIR, name + ".png")
    tmp = bpy.data.images.new(name + "_tmp", w, h, alpha=False)
    tmp.pixels.foreach_set(rgba.ravel())
    tmp.filepath_raw = path
    tmp.file_format = "PNG"
    tmp.save()
    bpy.data.images.remove(tmp)
    return get_image(name)


def get_image(name):
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.load(os.path.join(TEX_DIR, name + ".png"))
        img.name = name
    return img


# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------
def _new_material(name):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    nt.nodes.clear()
    return m, nt, nt.nodes.new("ShaderNodeOutputMaterial")


def mat_simple(name, color, rough):
    m, nt, out = _new_material(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    return m


def mat_textured(name, image, rough):
    m, nt, out = _new_material(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.name = "BSDF"
    b.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = "Textura"
    tex.image = image
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    for n in ("Specular IOR Level", "Specular"):
        if n in b.inputs:
            b.inputs[n].default_value = 0.3
            break
    return m


def set_outfit(body, outfit):
    body.data.materials[0].node_tree.nodes["Textura"].image = get_image(f"carmen_{outfit}")


# ---------------------------------------------------------------------------
# Poses: cada hueso apunta en una direccion (espacio del esqueleto) y su eje Z
# (el "frente" del hueso: rodilla, codo, cara, pulgar) mira hacia otra.
# ---------------------------------------------------------------------------
def frame(y_axis, z_hint, pos):
    y = Vector(y_axis).normalized()
    z = Vector(z_hint)
    z = (z - z.dot(y) * y).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = pos
    return m


LEN = {n: (LAYOUT[n][1] - LAYOUT[n][0]).length for n in LAYOUT}
IK_CHILD = {"LeftArm": "LeftForeArm", "RightArm": "RightForeArm", "LeftUpLeg": "LeftLeg", "RightUpLeg": "RightLeg"}


def two_bone(S, W, l1, l2, pole):
    """Codo (o rodilla) para que la cadena de dos huesos llegue de S a W; pole: hacia donde apunta."""
    v = W - S
    n = v.normalized()
    d = min(max(v.length, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    p = (pole - pole.dot(n) * n).normalized()
    return S + n * a + p * h, S + n * d


def apply_pose(rig, pose):
    """pose: direccion y 'frente' de cada hueso; '_ik' pone manos y tobillos en un punto."""
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()
    ik = pose.get("_ik", {})
    done = set()
    for name in BONES:
        if name in done:
            continue
        pb = rig.pose.bones[name]
        head = Vector(pose["_hips"]) if name == "Hips" else pb.head.copy()
        if name in ik:
            target, pole = ik[name]
            child = IK_CHILD[name]
            E, W = two_bone(head, Vector(target), LEN[name], LEN[child], Vector(pole).normalized())
            pb.matrix = frame(E - head, pose[name][1], head)
            bpy.context.view_layer.update()
            rig.pose.bones[child].matrix = frame(W - E, pose[child][1], E)
            bpy.context.view_layer.update()
            done.add(child)
            continue
        d, f = pose[name]
        pb.matrix = frame(d, f, head)
        bpy.context.view_layer.update()


def pose_de_pie():
    """Encorvada (la joroba de los anos), la cabeza adelantada, rodillas apenas flexionadas."""
    p = {"_hips": (0, 0.01, 0.825), "Hips": ((0, 0.06, 1), FRONT), "Spine": ((0, 0.03, 1), FRONT),
         "Spine1": ((0, -0.08, 1), FRONT), "Spine2": ((0, -0.25, 1), FRONT), "Neck": ((0, -0.50, 1), FRONT),
         "Head": ((0, -0.04, 1), FRONT)}
    for s, nm in ((1, "Left"), (-1, "Right")):
        p[nm + "Shoulder"] = ((s, 0.05, -0.25), FRONT)
        p[nm + "Arm"] = ((0.14 * s, -0.04, -1), FRONT)
        p[nm + "ForeArm"] = ((0.06 * s, -0.30, -1), FRONT)
        p[nm + "Hand"] = ((0.02 * s, -0.18, -1), FRONT)
        p[nm + "UpLeg"] = (None, FRONT)
        p[nm + "Leg"] = (None, FRONT)
        p[nm + "Foot"] = ((0.30 * s, -1, -0.45), UP)
        p[nm + "ToeBase"] = ((0.30 * s, -1, 0), UP)
    p["_ik"] = {"LeftUpLeg": ((0.115, 0.0, 0.075), (0.15, -1, 0)),
                "RightUpLeg": ((-0.115, 0.0, 0.075), (-0.15, -1, 0))}
    return p


def hand_on_chest(p):
    """La mano izquierda apretando la ropa contra el pecho (preocupada)."""
    p["_ik"]["LeftArm"] = ((0.07, -0.16, 1.10), (0.8, 0.2, -0.6))
    p["LeftArm"] = (None, FRONT)
    p["LeftForeArm"] = (None, (0.3, 0, 1))
    p["LeftHand"] = ((-1, -0.25, 0.25), (0.3, 0, 1))


def plate_on_palm(p):
    """El plato en la palma izquierda, contra la panza."""
    p["_ik"]["LeftArm"] = ((0.12, -0.24, 0.96), (0.7, 0.4, -0.6))
    p["LeftArm"] = (None, FRONT)
    p["LeftForeArm"] = (None, (1, -0.5, 0))
    p["LeftHand"] = ((-0.5, -1, 0), (1, -0.5, 0))
    p["_plato"] = (0.075, -0.31, 0.972)


def pose_con_plato():
    """Espera frente a la puerta con el plato en las dos manos."""
    p = pose_de_pie()
    p["_ik"]["LeftArm"] = ((0.15, -0.20, 0.975), (0.6, 0.5, -0.6))
    p["_ik"]["RightArm"] = ((-0.15, -0.20, 0.975), (-0.6, 0.5, -0.6))
    for s, nm in ((1, "Left"), (-1, "Right")):
        p[nm + "Arm"] = (None, FRONT)
        p[nm + "ForeArm"] = (None, UP)
        p[nm + "Hand"] = ((-0.25 * s, -1, 0.05), UP)
    p["_plato"] = (0.0, -0.285, 0.958)
    return p


def pose_tocando(plate=True):
    """Golpea la puerta con los nudillos (la puerta queda a 0,36 m adelante)."""
    p = pose_de_pie()
    p["RightShoulder"] = ((-1, 0.0, -0.08), FRONT)
    p["_ik"]["RightArm"] = ((-0.09, -0.27, 1.29), (-0.6, 0.25, -0.8))
    p["RightArm"] = (None, FRONT)
    p["RightForeArm"] = (None, (1, 0, 0))
    p["RightHand"] = ((0.05, -0.50, -0.86), (1, 0, 0))
    if plate:
        plate_on_palm(p)
    else:
        hand_on_chest(p)
    return p


def pose_mirilla(door_y=-0.25):
    """Se acerca a la puerta y levanta la cara hacia la mirilla (le queda alta: mide 1,55).
    door_y: donde queda la puerta, en el eje Y del esqueleto."""
    p = pose_de_pie()
    p["_hips"] = (0, 0.03, 0.82)
    p["Hips"] = ((0, 0.02, 1), FRONT)
    p["Spine"] = ((0, -0.10, 1), FRONT)
    p["Spine1"] = ((0, -0.30, 1), FRONT)
    p["Spine2"] = ((0, -0.45, 1), FRONT)
    p["Neck"] = ((0, -0.55, 1), FRONT)
    p["Head"] = ((0, 0.6, 1), (0, -1, 0.6))
    p["_ik"]["RightArm"] = ((-0.14, door_y + 0.03, 1.33), (-0.8, 0.3, -0.4))   # la mano apoyada en la puerta
    p["RightArm"] = (None, FRONT)
    p["RightForeArm"] = (None, (1, 0, 0))
    p["RightHand"] = ((0.05, -0.2, 1), (1, 0, 0))
    hand_on_chest(p)
    return p


def pose_preocupada():
    p = pose_de_pie()
    hand_on_chest(p)
    return p


POSES = {"de_pie": pose_de_pie, "con_plato": pose_con_plato, "tocando": pose_tocando,
         "mirilla": pose_mirilla, "preocupada": pose_preocupada}


def key_poses(rig):
    """Guarda cada pose como una accion de un cuadro (para abrirlas en Blender o en Unity)."""
    rig.animation_data_create()
    for name, fn in POSES.items():
        rig.animation_data.action = None
        apply_pose(rig, fn())
        for pb in rig.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=1, group=pb.name)
            if pb.name == "Hips":
                pb.keyframe_insert("location", frame=1, group=pb.name)
        act = rig.animation_data.action
        act.name = name
        act.use_fake_user = True
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)


def place_plate(rig, plate, pose):
    """Pone el plato donde lo tienen las manos (o lo esconde si la pose no lo lleva)."""
    if "_plato" not in pose:
        plate.hide_render = True
        return
    plate.hide_render = False
    plate.matrix_world = rig.matrix_world @ Matrix.Translation(pose["_plato"])


def eye_point(rig):
    """Punto entre los ojos, en coordenadas de mundo."""
    m = rig.matrix_world @ rig.pose.bones["Head"].matrix
    return m @ Vector((0, 0.10, 0.085))


# ---------------------------------------------------------------------------
# Render y post-proceso PS1
# ---------------------------------------------------------------------------
BAYER4 = np.array([[0, 8, 2, 10],
                   [12, 4, 14, 6],
                   [3, 11, 1, 9],
                   [15, 7, 13, 5]], dtype=np.float32) / 16.0 - 0.5 + 1.0 / 32.0


def load_rgb(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)[:, :, :3]


def quantize(rgb):
    h, w, _ = rgb.shape
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


def render_raw(cam, res, name):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    raw = os.path.join(RENDER_DIR, f"_{name}_raw.png")
    sc.render.filepath = raw
    bpy.ops.render.render(write_still=True)
    rgb = load_rgb(raw)
    os.remove(raw)
    return rgb


def render_to(cam, res, name):
    return quantize(render_raw(cam, res, name))


def set_engine(sc):
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    if hasattr(sc.render, "filter_size"):
        sc.render.filter_size = 0.6
    if hasattr(sc.eevee, "taa_render_samples"):
        sc.eevee.taa_render_samples = 48


def look_at(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()


def place_cam(cam, angle, dist, z, target):
    a = R(angle)
    cam.location = (target[0] + math.sin(a) * dist, target[1] - math.cos(a) * dist, z)
    look_at(cam, target)


def studio_sheet(rig, body, plate):
    """Hoja: cinco cuerpos (camara ortografica) arriba; cuatro caras y el plato abajo."""
    sc = bpy.context.scene
    set_engine(sc)
    col = bpy.data.collections.new("Estudio")
    sc.collection.children.link(col)
    w = bpy.data.worlds.new("Estudio")
    sc.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.013, 0.017, 1)

    floor_me = bpy.data.meshes.new("piso_estudio")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=4.0)
    bm.to_mesh(floor_me)
    bm.free()
    floor_me.materials.append(mat_simple("PisoEstudio", (0.035, 0.035, 0.038), 0.9))
    col.objects.link(bpy.data.objects.new("piso_estudio", floor_me))

    def light(name, kind, loc, target, energy, color, size=0.6):
        ld = bpy.data.lights.new(name, kind)
        ld.energy, ld.color = energy, color
        if kind == "AREA":
            ld.size = size
        if kind == "SPOT":
            ld.spot_size = R(40)
        ob = bpy.data.objects.new(name, ld)
        col.objects.link(ob)
        ob.location = loc
        look_at(ob, target)

    light("clave", "AREA", (-1.6, -2.2, 2.3), (0, 0, 1.0), 240, (1.0, 0.86, 0.72), 0.5)
    light("contra", "SPOT", (1.3, 1.6, 2.1), (0, 0, 1.0), 380, (0.62, 0.75, 1.0))
    light("relleno", "POINT", (1.8, -1.6, 0.9), (0, 0, 0.9), 25, (0.7, 0.75, 0.85))

    cd = bpy.data.cameras.new("cam_cuerpo")
    cd.type = "ORTHO"
    cd.ortho_scale = 1.75
    cam_body = bpy.data.objects.new("cam_cuerpo", cd)
    col.objects.link(cam_body)
    cf = bpy.data.cameras.new("cam_cara")
    cf.lens = 85
    cf.clip_start = 0.05
    cam_face = bpy.data.objects.new("cam_cara", cf)
    col.objects.link(cam_face)

    bodies, faces = [], []
    for outfit, pose_name, angle in (("dia", "de_pie", 12), ("dia", "con_plato", 35), ("dia", "tocando", -90),
                                     ("dia", "de_pie", 180), ("noche", "preocupada", 25)):
        set_outfit(body, outfit)
        pose = POSES[pose_name]()
        apply_pose(rig, pose)
        place_plate(rig, plate, pose)
        place_cam(cam_body, angle, 4.0, 0.80, (0, 0, 0.80))
        bodies.append(render_to(cam_body, (192, 360), f"cuerpo_{len(bodies)}"))
        print(f"[hoja] cuerpo {len(bodies)}")

    apply_pose(rig, pose_de_pie())
    plate.hide_render = True
    t = eye_point(rig) + Vector((0, 0.07, -0.01))
    for outfit, angle in (("dia", 0), ("dia", 35), ("dia", -90), ("noche", 20)):
        set_outfit(body, outfit)
        place_cam(cam_face, angle, 0.80, t.z + 0.02, t)
        faces.append(render_to(cam_face, (192, 192), f"cara_{len(faces)}"))
        print(f"[hoja] cara {len(faces)}")

    # El plato solo, en el piso
    body.hide_render = True
    plate.hide_render = False
    plate.matrix_world = Matrix.Identity(4)
    place_cam(cam_face, 30, 0.62, 0.36, (0, 0, 0.03))
    faces.append(render_to(cam_face, (192, 192), "plato"))
    body.hide_render = False

    top = np.concatenate(bodies, axis=1)
    bottom = np.concatenate(faces, axis=1)
    sheet = np.concatenate([bottom, top], axis=0)  # fila 0 = abajo
    for i in range(1, 5):
        sheet[:, i * 192 - 1:i * 192 + 1] = 0.0
    sheet[191:193, :] = 0.0
    save_png(sheet, os.path.join(RENDER_DIR, "carmen_hoja.png"), 2)


# ---------------------------------------------------------------------------
# La mirilla: el pasillo de la prueba de estilo visto desde la puerta del 4B
# ---------------------------------------------------------------------------
# En el pasillo (corre a lo largo de Y), la puerta del 4B es la primera de la pared
# izquierda (y 1,2-2,1) y la del 4A la primera de la derecha (y 3,2-4,1).
DOOR_4B_X = -0.87          # cara de la puerta que da al pasillo
PEEP = (-0.855, 1.65, 1.555)
PEEP_HALF_FOV = 85.0       # medio angulo del ojo de pez (170 grados, como una mirilla)


def fisheye(src, half_fov, diam=262):
    """Pasa un render rectilineo muy abierto a ojo de pez (equidistante), dentro de un circulo."""
    H, W, _ = src.shape
    t_max = math.radians(half_fov)
    k0 = t_max / math.tan(t_max)
    yy, xx = np.mgrid[0:RES_Y, 0:RES_X].astype(np.float32)
    acc = np.zeros((RES_Y, RES_X, 3), np.float32)
    for oy, ox in ((-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25)):
        dx = (xx + ox - (RES_X - 1) / 2) / (diam / 2)
        dy = (yy + oy - (RES_Y - 1) / 2) / (diam / 2)
        rho = np.sqrt(dx * dx + dy * dy)
        th = np.minimum(rho, 1.0) * t_max
        k = np.where(rho > 1e-6, np.tan(th) / (math.tan(t_max) * np.maximum(rho, 1e-6)), k0)
        col = np.clip(np.round((dx * k + 1) / 2 * (W - 1)), 0, W - 1).astype(int)
        row = np.clip(np.round((dy * k + 1) / 2 * (H - 1)), 0, H - 1).astype(int)
        acc += src[row, col]
    out = acc / 4
    dx = (xx - (RES_X - 1) / 2) / (diam / 2)
    dy = (yy - (RES_Y - 1) / 2) / (diam / 2)
    rho = np.sqrt(dx * dx + dy * dy)
    # Bordes borrosos, como el vidrio de una mirilla
    blur = out.copy()
    for _ in range(3):
        blur = (np.roll(blur, 1, 0) + np.roll(blur, -1, 0) + np.roll(blur, 1, 1) + np.roll(blur, -1, 1) + blur) / 5
    wgt = np.clip((rho - 0.55) / 0.35, 0, 1)[:, :, None]
    out = out * (1 - wgt) + blur * wgt
    vig = np.clip((1 - rho) / 0.10, 0, 1) ** 0.8 * (1 - 0.30 * np.minimum(rho, 1) ** 2)
    out *= vig[:, :, None] * np.array((0.96, 1.0, 0.90))[None, None, :]
    return out


FILL_W = 6.0
RECEIVERS = None


def append_carmen(path):
    global RECEIVERS
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = ["Carmen_Rig", "Carmen", "Carmen_Plato"]
    col = bpy.data.collections.new("Carmen")
    bpy.context.scene.collection.children.link(col)
    for ob in dst.objects:
        col.objects.link(ob)
    rig, body, plate = dst.objects
    RECEIVERS = bpy.data.collections.new("Carmen_rebote")
    for ob in (body, plate):
        RECEIVERS.objects.link(ob)
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return rig, body, plate, col


def find_door(x, y):
    for ob in bpy.data.objects:
        if ob.name.startswith("puerta") and (ob.location - Vector((x, y, 0))).length < 0.02:
            return ob
    return None


def hallway_extras(col):
    """La puerta del 4A entreabierta (con su luz tibia) y un rebote tenue frente al 4B."""
    door_4a = find_door(0.87, 4.10)
    m = bpy.data.materials.new("Interior4A")
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.62, 0.32, 1)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    me = bpy.data.meshes.new("interior_4A")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.894, 3.65, 1.025)) @
                          Matrix.Diagonal((0.010, 0.88, 2.04, 1)))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    interior = bpy.data.objects.new("interior_4A", me)
    col.objects.link(interior)

    def light(name, kind, loc, target, color, energy, spot=60, radius=0.05):
        ld = bpy.data.lights.new(name, kind)
        ld.color, ld.energy, ld.shadow_soft_size = color, energy, radius
        if kind == "SPOT":
            ld.spot_size, ld.spot_blend = R(spot), 0.6
        ob = bpy.data.objects.new(name, ld)
        col.objects.link(ob)
        ob.location = loc
        if target:
            look_at(ob, target)
        return ob

    spill = light("luz_4A", "SPOT", (0.80, 3.62, 1.95), (-0.4, 2.6, 0.0), (1.0, 0.68, 0.40), 60, spot=75)
    # Rebote: la luz del foco que vuelve desde la puerta del 4B. Solo ilumina a Carmen y a los platos.
    ld = bpy.data.lights.new("rebote_puerta", "AREA")
    ld.shape, ld.size, ld.size_y = "RECTANGLE", 0.9, 1.2
    ld.color, ld.energy = (1.0, 0.80, 0.58), FILL_W
    ld.use_shadow = False
    fill = bpy.data.objects.new("rebote_puerta", ld)
    col.objects.link(fill)
    fill.location = (DOOR_4B_X + 0.02, PEEP[1], 1.45)
    look_at(fill, (2.0, PEEP[1], 1.30))
    try:
        fill.light_linking.receiver_collection = RECEIVERS
    except Exception as e:
        print(f"[aviso] sin light linking: {e}")

    def set_4a(open_):
        if door_4a:
            door_4a.rotation_euler.z = R(-24) if open_ else 0.0
        interior.hide_render = not open_
        spill.hide_render = not open_
    return set_4a


def render_peephole(name):
    sc = bpy.context.scene
    cam = sc.camera
    raw = render_raw(cam, (2048, 2048), name)
    q = quantize(fisheye(raw, PEEP_HALF_FOV))
    save_png(q, os.path.join(RENDER_DIR, name + ".png"), 4)
    print(f"[render] {name}")


def render_hallway(asset):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(SCENE_DIR, "prueba_estilo_pasillo.blend"))
    set_engine(bpy.context.scene)
    sil = bpy.data.objects.get("Tomas_silueta")
    if sil:
        for ob in [sil] + list(sil.children_recursive):
            ob.hide_render = True
    rig, body, plate, col = append_carmen(asset)
    set_4a = hallway_extras(col)

    cd = bpy.data.cameras.new("Cam_mirilla")
    cd.angle = R(2 * PEEP_HALF_FOV)
    cd.clip_start = 0.005
    cam = bpy.data.objects.new("Cam_mirilla", cd)
    col.objects.link(cam)
    cam.location = PEEP
    look_at(cam, (2.0, PEEP[1], PEEP[2]))
    bpy.context.scene.camera = cam

    # Carmen mira hacia la puerta del 4B (hacia -X): su -Y local apunta a -X
    rig.rotation_euler = (0, 0, R(-90))

    def put(local_door_dist, y):
        """Ubica el esqueleto para que la puerta quede a 'local_door_dist' metros adelante."""
        rig.location = (DOOR_4B_X + local_door_dist, y, 0.0)
        bpy.context.view_layer.update()

    extra_plates = []

    def floor_plates(spots):
        for ob in extra_plates:
            ob.hide_render = True
        for i, (x, y, rz) in enumerate(spots):
            if i >= len(extra_plates):
                ob = plate.copy()
                col.objects.link(ob)
                RECEIVERS.objects.link(ob)
                extra_plates.append(ob)
            ob = extra_plates[i]
            ob.hide_render = False
            ob.matrix_world = Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(R(rz), 4, "Z")

    # 1. Espera con el plato
    set_outfit(body, "dia")
    set_4a(True)
    floor_plates([])
    put(0.50, 1.62)
    pose = pose_con_plato()
    apply_pose(rig, pose)
    place_plate(rig, plate, pose)
    render_peephole("carmen_mirilla_plato")

    # 2. Se acerca a mirar: la cara a 7 cm de la puerta, el plato ya en el piso
    floor_plates([(-0.48, 1.86, 20)])
    put(0.40, 1.60)
    apply_pose(rig, pose_mirilla())
    e = eye_point(rig)
    rig.location.x += (DOOR_4B_X + 0.07) - e.x
    rig.location.y += (PEEP[1] - 0.02) - e.y
    bpy.context.view_layer.update()
    door_y = -(rig.location.x - DOOR_4B_X)         # la puerta en el eje Y del esqueleto
    print(f"[mirilla] ojos en {tuple(round(c, 3) for c in eye_point(rig))}, esqueleto en "
          f"{tuple(round(c, 3) for c in rig.location)}")
    pose = pose_mirilla(door_y)
    apply_pose(rig, pose)
    place_plate(rig, plate, pose)
    render_peephole("carmen_mirilla_cerca")

    # 3. Aquella noche: en bata, tocando
    set_outfit(body, "noche")
    floor_plates([])
    put(0.36, 1.60)
    pose = pose_tocando(plate=False)
    apply_pose(rig, pose)
    place_plate(rig, plate, pose)
    render_peephole("carmen_mirilla_noche")

    # 4. Nadie: los platos sin tocar se acumulan
    for ob in (rig, body, plate):
        ob.hide_render = True
    set_4a(False)
    floor_plates([(-0.36, 1.46, 10), (-0.38, 1.86, 55), (-0.12, 1.68, -30)])
    render_peephole("carmen_mirilla_vacio")


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    for d in (TEX_DIR, SCENE_DIR, RENDER_DIR):
        os.makedirs(d, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    for outfit in OUTFITS:
        save_texture(f"carmen_{outfit}", build_texture(outfit))
    save_texture("plato_carmen", build_plate_texture())
    mat = mat_textured("Carmen", get_image("carmen_dia"), 0.78)

    rig = build_rig()
    body = build_mesh(mat)
    scene.collection.objects.link(body)
    body.parent = rig
    mod = body.modifiers.new("Armature", "ARMATURE")
    mod.object = rig
    plate = build_plate(mat_textured("PlatoCarmen", get_image("plato_carmen"), 0.55))
    scene.collection.objects.link(plate)
    plate.location = (0.5, -0.3, 0.0)

    tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
    ptris = sum(len(p.vertices) - 2 for p in plate.data.polygons)
    print(f"[info] Carmen: {len(body.data.vertices)} vertices, {tris} triangulos, {len(rig.data.bones)} huesos; "
          f"plato: {ptris} triangulos")

    key_poses(rig)
    set_outfit(body, "dia")
    asset = os.path.join(SCENE_DIR, "dona_carmen.blend")
    bpy.ops.wm.save_as_mainfile(filepath=asset)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print(f"[aviso] rutas relativas: {e}")
    if os.path.exists(asset + "1"):
        os.remove(asset + "1")

    studio_sheet(rig, body, plate)
    if not SHEET_ONLY:
        render_hallway(asset)
    print(f"[info] listo en {time.time() - t0:.0f} s")


main()
