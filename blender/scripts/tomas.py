r"""
Tomas, el hermano menor de Elias: modelo low poly con esqueleto y cinco estados.

  estado 0  vivo, sonriente    bajo el efecto y en los recuerdos (con la Polaroid)
  estado 1  vivo, "mal"        en abstinencia: palido, ojeroso
  estado 2  recien muerto      piel gris, labios morados, espuma en la boca
  estado 3  descomposicion     piel verdosa con vetas, ojos hundidos, dientes a la vista
  estado 4  calavera

Como en los personajes de PS1, el cuerpo esta hecho de piezas (cabeza, torso,
brazos, piernas...) que se mueven con su hueso. Una sola textura de 256x256 por
estado: en Unity, cambiar de estado es cambiar la textura (y dos blendshapes:
"descompuesto" adelgaza el cuerpo y "calavera" hunde la cara).

El esqueleto usa los nombres de Mixamo (Hips, Spine, LeftArm...), asi Unity lo
reconoce como Humanoid y se le pueden pasar animaciones de Mixamo.

Uso (PowerShell, desde la carpeta del proyecto):
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup `
      -P blender\scripts\tomas.py -- blender
  Solo el modelo y la hoja de estados (sin el 4B ni el pasillo): ... -- blender --solo-hoja

Salidas (dentro de la carpeta blender/):
  textures/tomas_estado0..4.png
  scenes/tomas.blend                 el modelo, con las poses de_pie, muerto_de_pie, sentado, sentado_muerto
  renders/tomas_estados.png          los cinco estados: cuerpo y cara
  renders/tomas_sofa.png             vivo en el sofa del 4B (Noche 1)
  renders/tomas_sofa_muerto.png      la misma toma: muerto, donde estaba el vivo
  renders/tomas_pasillo.png          muerto al fondo del pasillo (Noche 2)
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
STATES = (0, 1, 2, 3, 4)
R = math.radians
rng = np.random.default_rng(20)
scene = bpy.context.scene

# Regiones del atlas: (x, y, ancho, alto) en pixeles, fila 0 arriba
REG = {
    "head": (0, 0, 128, 80), "torso": (128, 0, 128, 80),
    "arm": (0, 80, 64, 96), "leg": (64, 80, 64, 128),
    "pelvis": (128, 80, 128, 32), "hand": (128, 112, 64, 64),
    "foot": (192, 112, 64, 64), "neck": (128, 176, 64, 16),
}
# Alturas (o largos) que cubre cada region, de la primera fila a la ultima
SPAN = {
    "head": (1.715, 1.495), "torso": (1.445, 0.94), "neck": (1.535, 1.42),
    "pelvis": (0.97, 0.80), "leg": (0.93, 0.10), "arm": (0.13, 0.715), "foot": (0.065, -0.20),
}

# Como se ve cada estado (rugosidad de la piel y forma)
LOOK = {
    0: dict(rough=0.75, desc=0.0, skull=0.0, polaroid=True),
    1: dict(rough=0.70, desc=0.25, skull=0.0, polaroid=False),
    2: dict(rough=0.50, desc=0.25, skull=0.0, polaroid=False),
    3: dict(rough=0.38, desc=0.80, skull=0.0, polaroid=False),
    4: dict(rough=0.80, desc=1.0, skull=1.0, polaroid=False),
}


# ---------------------------------------------------------------------------
# Esqueleto (nombres de Mixamo). El personaje mira hacia -Y; su izquierda es +X.
# ---------------------------------------------------------------------------
FRONT = Vector((0, -1, 0))
UP = Vector((0, 0, 1))


def bone_layout():
    L = {}

    def add(name, head, tail, parent, z=FRONT):
        L[name] = (Vector(head), Vector(tail), parent, z)

    add("Hips", (0, 0, 0.95), (0, 0, 1.03), None)
    add("Spine", (0, 0, 1.03), (0, 0, 1.15), "Hips")
    add("Spine1", (0, 0, 1.15), (0, 0, 1.27), "Spine")
    add("Spine2", (0, 0, 1.27), (0, 0, 1.42), "Spine1")
    add("Neck", (0, 0, 1.42), (0, -0.005, 1.52), "Spine2")
    add("Head", (0, -0.005, 1.52), (0, -0.005, 1.73), "Neck")
    for s, nm in ((1, "Left"), (-1, "Right")):
        add(nm + "Shoulder", (0.03 * s, 0.0, 1.375), (0.17 * s, 0.005, 1.385), "Spine2")
        add(nm + "Arm", (0.17 * s, 0.005, 1.385), (0.45 * s, 0.005, 1.385), nm + "Shoulder")
        add(nm + "ForeArm", (0.45 * s, 0.005, 1.385), (0.71 * s, 0.0, 1.385), nm + "Arm")
        add(nm + "Hand", (0.71 * s, 0.0, 1.385), (0.88 * s, 0.0, 1.375), nm + "ForeArm")
    for s, nm in ((1, "Left"), (-1, "Right")):
        add(nm + "UpLeg", (0.095 * s, 0.0, 0.92), (0.095 * s, 0.0, 0.50), "Hips")
        add(nm + "Leg", (0.095 * s, 0.0, 0.50), (0.095 * s, 0.01, 0.09), nm + "UpLeg")
        add(nm + "Foot", (0.095 * s, 0.01, 0.09), (0.095 * s, -0.11, 0.025), nm + "Leg", UP)
        add(nm + "ToeBase", (0.095 * s, -0.11, 0.025), (0.095 * s, -0.19, 0.025), nm + "Foot", UP)
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
        self.keys = {"descompuesto": {}, "calavera": {}}

    def vert(self, p, weights, alt):
        v = self.bm.verts.new(p)
        for g, w in weights.items():
            if w > 0:
                v[self.dl][self.groups[g]] = w
        for k in self.keys:
            self.keys[k][v] = Vector(alt.get(k, p))
        return v

    def face(self, verts, uvs):
        f = self.bm.faces.new(verts)
        for loop, uv in zip(f.loops, uvs):
            loop[self.uv].uv = uv
        f.smooth = True
        return f


def tube(B, rings, sides, region, U, V, caps=(None, None), flat=False):
    """Tubo de anillos elipticos. El angulo t=90 apunta a V (el frente); la costura queda atras.
    rings: dict(c, rx, ry, v, w (dict o funcion), push(j), thin, skull(j, off))."""
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
            desc = rg["c"] + off * rg.get("thin", 1.0) + push
            cal = p + (rg["skull"](j, off) if "skull" in rg else Vector())
            w = rg["w"](p) if callable(rg["w"]) else rg["w"]
            row.append(B.vert(p, w, {"descompuesto": desc, "calavera": cal}))
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
        cp = Vector(cap["p"])
        cv = B.vert(cp, cap["w"], {"calavera": cp + cap.get("skull", Vector())})
        for j in range(sides):
            j1 = (j + 1) % sides
            B.face([ring[j], ring[j1], cv], [atlas_uv(region, 1 - j / sides, v),
                                             atlas_uv(region, 1 - (j + 1) / sides, v),
                                             atlas_uv(region, 1 - (j + 0.5) / sides, cap["v"])])
    return grid


def rect_tube(B, pts, sizes, weights, side, a_axis, thin=1.0, skull=1.0):
    """Tubo de seccion rectangular (manos, pulgar) con UV plano: dorso y palma."""
    rings = []
    for c, (hw, ht), w in zip(pts, sizes, weights):
        c = Vector(c)
        ring = []
        for sa, sb in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            off = a_axis * (sa * hw) + UP * (sb * ht)
            p = c + off
            ring.append((p, B.vert(p, w, {"descompuesto": c + off * thin, "calavera": p + off * (skull - 1)})))
        rings.append((c, ring))

    def uv(p, top):
        x0, y0, _, _ = REG["hand"]
        col = min(max((abs(p.x) - 0.70) / 0.185 * 31, 0), 31) + (0 if top else 32)
        row = min(max((p.y + 0.05) / 0.10 * 63, 0), 63)
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
SPINE_W = {0.94: {"Hips": 0.5, "Spine": 0.5}, 1.02: {"Spine": 1.0}, 1.12: {"Spine": 0.5, "Spine1": 0.5},
           1.24: {"Spine1": 0.4, "Spine2": 0.6}, 1.34: {"Spine2": 1.0}, 1.40: {"Spine2": 1.0},
           1.445: {"Spine2": 0.7, "Neck": 0.3}}


def torso_w(z):
    def f(p):
        w = dict(SPINE_W[z])
        if z >= 1.30 and abs(p.x) > 0.12:
            k = min(1.0, (abs(p.x) - 0.12) / 0.06) * 0.5
            w = {b: v * (1 - k) for b, v in w.items()}
            w[("Left" if p.x > 0 else "Right") + "Shoulder"] = k
        return w
    return f


def blend_w(a, b, t):
    if t <= 0:
        return {a: 1.0}
    if t >= 1:
        return {b: 1.0}
    return {a: 1 - t, b: t}


def build_mesh(mat):
    B = Builder()
    X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    F = Vector((0, -1, 0))

    # Pelvis (jean)
    rings = [dict(c=Vector((0, 0, z)), rx=rx, ry=ry, v=vfrac("pelvis", z), w={"Hips": 1.0}, thin=0.95)
             for z, rx, ry in ((0.97, 0.155, 0.095), (0.88, 0.162, 0.102), (0.80, 0.13, 0.09))]
    tube(B, rings, 10, "pelvis", X, F, caps=(None, dict(p=(0, 0, 0.78), w={"Hips": 1.0}, v=1.0)))

    # Torso (sudadera con la capucha caida atras)
    hood = {1.40: 0.035, 1.445: 0.05}
    rings = []
    for z, rx, ry in ((0.94, 0.165, 0.105), (1.02, 0.158, 0.100), (1.12, 0.160, 0.105), (1.24, 0.172, 0.112),
                      (1.34, 0.188, 0.108), (1.40, 0.190, 0.095), (1.445, 0.100, 0.075)):
        hb = hood.get(z, 0.0)
        rings.append(dict(c=Vector((0, 0, z)), rx=rx, ry=ry, v=vfrac("torso", z), w=torso_w(z),
                          thin=0.93 if z < 1.38 else 1.0,
                          push=lambda j, hb=hb: Vector((0, hb * (1.0 if j == 0 else 0.6 if j in (1, 9) else 0.0), 0))))
    tube(B, rings, 10, "torso", X, F, caps=("flat", "flat"))

    # Cuello
    rings = [dict(c=Vector((0, dy, z)), rx=r, ry=r * 1.05, v=vfrac("neck", z), w=w, thin=0.8)
             for z, r, dy, w in ((1.42, 0.050, 0.0, {"Spine2": 0.4, "Neck": 0.6}), (1.48, 0.045, 0.0, {"Neck": 1.0}),
                                 (1.535, 0.045, -0.01, {"Neck": 0.4, "Head": 0.6}))]
    tube(B, rings, 6, "neck", X, F)

    # Cabeza: el vertice del frente (j=5) forma la nariz
    def skull_fn(ring):
        def f(j, off):
            front_side = j in (4, 6)
            if ring == 0:
                return -off * 0.15 + Vector((0, 0.004, 0))
            if ring == 1:
                return -off * 0.16
            if ring == 2:
                d = -off * 0.10
                if j == 5:
                    d += Vector((0, 0.022, 0))
                return d
            if ring == 3:
                if front_side:
                    return -off.normalized() * 0.014
                if j == 5:
                    return Vector((0, 0.006, 0))
                return -off * 0.03
            if ring == 4 and (front_side or j == 5):
                return Vector((0, 0.003, 0))
            return Vector()
        return f

    head = [(1.495, 0.042, 0.046, -0.035, 0.0, 1.0), (1.525, 0.062, 0.070, -0.012, 0.0, 0.93),
            (1.565, 0.072, 0.085, -0.002, 0.018, 0.93), (1.605, 0.077, 0.092, 0.004, 0.006, 0.97),
            (1.645, 0.081, 0.099, 0.008, 0.004, 1.0), (1.685, 0.080, 0.098, 0.010, 0.0, 1.0),
            (1.715, 0.064, 0.080, 0.012, 0.0, 1.0)]
    rings = []
    for i, (z, rx, ry, dy, nose, th) in enumerate(head):
        rings.append(dict(c=Vector((0, dy, z)), rx=rx, ry=ry, v=vfrac("head", z), w={"Head": 1.0}, thin=th,
                          push=lambda j, nose=nose: Vector((0, -nose if j == 5 else 0.0, 0)), skull=skull_fn(i)))
    tube(B, rings, 10, "head", X, F,
         caps=(dict(p=(0, 0.012, 1.505), w={"Head": 1.0}, v=1.0, skull=Vector((0, 0.01, 0))),
               dict(p=(0, 0.012, 1.738), w={"Head": 1.0}, v=0.0)))

    # Brazos (mangas) y manos
    for s, nm in ((1, "Left"), (-1, "Right")):
        sh, ar, fa, ha = nm + "Shoulder", nm + "Arm", nm + "ForeArm", nm + "Hand"
        spec = [(0.13, 0.050, {sh: 0.4, ar: 0.6}), (0.20, 0.052, {ar: 1.0}), (0.32, 0.048, {ar: 1.0}),
                (0.41, 0.046, blend_w(ar, fa, 0.2)), (0.45, 0.045, blend_w(ar, fa, 0.5)),
                (0.49, 0.045, blend_w(ar, fa, 0.8)), (0.58, 0.043, {fa: 1.0}), (0.69, 0.041, {fa: 1.0}),
                (0.715, 0.043, {fa: 1.0})]
        rings = [dict(c=Vector((x * s, 0.005, 1.385)), rx=r, ry=r * 1.05, v=vfrac("arm", x), w=w, thin=0.85)
                 for x, r, w in spec]
        tube(B, rings, 6, "arm", Z, F, caps=("flat", "flat"))
        # mano tipo manopla: palma abajo, pulgar hacia adelante
        pts = [(0.70 * s, 0.0, 1.385), (0.755 * s, 0.0, 1.385), (0.81 * s, 0.0, 1.382), (0.875 * s, 0.0, 1.373)]
        sizes = [(0.026, 0.016), (0.042, 0.017), (0.044, 0.014), (0.036, 0.010)]
        wts = [{fa: 0.3, ha: 0.7}, {ha: 1.0}, {ha: 1.0}, {ha: 1.0}]
        rect_tube(B, pts, sizes, wts, s, Y, thin=0.85, skull=0.75)
        thumb = [(0.725 * s, -0.030, 1.377), (0.77 * s, -0.058, 1.368), (0.805 * s, -0.070, 1.363)]
        rect_tube(B, thumb, [(0.012, 0.011), (0.011, 0.010), (0.009, 0.008)], [{ha: 1.0}] * 3, s, X,
                  thin=0.85, skull=0.75)

    # Piernas (jean) y zapatillas
    for s, nm in ((1, "Left"), (-1, "Right")):
        ul, lg, ft, to = nm + "UpLeg", nm + "Leg", nm + "Foot", nm + "ToeBase"
        spec = [(0.93, 0.082, 0.0, {"Hips": 0.3, ul: 0.7}), (0.80, 0.083, 0.0, {ul: 1.0}),
                (0.64, 0.068, 0.0, {ul: 1.0}), (0.54, 0.060, 0.0, blend_w(ul, lg, 0.2)),
                (0.50, 0.058, 0.0, blend_w(ul, lg, 0.5)), (0.46, 0.058, 0.0, blend_w(ul, lg, 0.8)),
                (0.36, 0.058, 0.008, {lg: 1.0}), (0.22, 0.048, 0.0, {lg: 1.0}), (0.10, 0.053, 0.0, {lg: 1.0})]
        rings = [dict(c=Vector((0.095 * s, dy, z)), rx=r, ry=r, v=vfrac("leg", z), w=w, thin=0.85)
                 for z, r, dy, w in spec]
        tube(B, rings, 6, "leg", X, F, caps=("flat", "flat"))
        spec = [(0.065, 0.038, 0.045, {ft: 1.0}), (0.02, 0.046, 0.055, {ft: 1.0}), (-0.07, 0.051, 0.045, {ft: 1.0}),
                (-0.15, 0.047, 0.032, {ft: 0.4, to: 0.6}), (-0.20, 0.032, 0.022, {to: 1.0})]
        rings = [dict(c=Vector((0.095 * s, y, hh)), rx=hw, ry=hh, v=vfrac("foot", y), w=w)
                 for y, hw, hh, w in spec]
        tube(B, rings, 8, "foot", X, Z, caps=("flat", "flat"), flat=True)

    bmesh.ops.recalc_face_normals(B.bm, faces=B.bm.faces)
    me = bpy.data.meshes.new("Tomas")
    B.bm.verts.index_update()
    alt = {k: [None] * len(B.bm.verts) for k in B.keys}
    for k, d in B.keys.items():
        for v, co in d.items():
            alt[k][v.index] = co
    B.bm.to_mesh(me)
    B.bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new("Tomas", me)
    for n in BONES:
        ob.vertex_groups.new(name=n)
    ob.shape_key_add(name="Basis", from_mix=False)
    for k in ("descompuesto", "calavera"):
        sk = ob.shape_key_add(name=k, from_mix=False)
        for i, co in enumerate(alt[k]):
            sk.data[i].co = co
    return ob


def build_rig():
    arm = bpy.data.armatures.new("Tomas_Rig")
    ob = bpy.data.objects.new("Tomas_Rig", arm)
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


def build_polaroid():
    """La camara instantanea de Tomas, colgada del cuello (solo en el estado 0)."""
    me = bpy.data.meshes.new("Tomas_Polaroid")
    bm = bmesh.new()
    mats = []

    def add_box(mn, mx, mi):
        mn, mx = Vector(mn), Vector(mx)
        c, s = (mn + mx) / 2, mx - mn
        r = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(c) @ Matrix.Diagonal((s.x, s.y, s.z, 1)))
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi

    add_box((-0.058, -0.178, 1.165), (0.058, -0.118, 1.262), 0)       # cuerpo
    add_box((-0.050, -0.183, 1.172), (0.050, -0.178, 1.215), 1)       # frente claro
    add_box((-0.050, -0.184, 1.226), (0.050, -0.180, 1.232), 3)       # franja de color
    add_box((-0.042, -0.183, 1.240), (-0.012, -0.178, 1.256), 4)      # flash
    lens = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.022, radius2=0.022, depth=0.014,
                                 matrix=Matrix.Translation((0.012, -0.188, 1.195)) @ Matrix.Rotation(R(90), 4, "X"))
    for f in {f for v in lens["verts"] for f in v.link_faces}:
        f.material_index = 2
    # correa: de la camara, por los hombros, hasta la nuca
    for s in (1, -1):
        path = [(0.05 * s, -0.150, 1.262), (0.075 * s, -0.10, 1.38), (0.075 * s, -0.04, 1.44),
                (0.05 * s, 0.05, 1.47), (0.0, 0.085, 1.465)]
        for a, b in zip(path, path[1:]):
            a, b = Vector(a), Vector(b)
            d = b - a
            m = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Y", "Z").to_matrix().to_4x4() \
                @ Matrix.Diagonal((0.014, d.length + 0.006, 0.004, 1))
            r = bmesh.ops.create_cube(bm, size=1.0, matrix=m)
            for f in {f for v in r["verts"] for f in v.link_faces}:
                f.material_index = 5
    bm.to_mesh(me)
    bm.free()
    for name, col, rough in (("PolaroidCuerpo", (0.07, 0.07, 0.075), 0.5), ("PolaroidFrente", (0.30, 0.30, 0.31), 0.5),
                             ("PolaroidLente", (0.02, 0.02, 0.025), 0.1), ("PolaroidFranja", (0.60, 0.12, 0.08), 0.5),
                             ("PolaroidFlash", (0.80, 0.80, 0.78), 0.2), ("PolaroidCorrea", (0.12, 0.08, 0.05), 0.8)):
        me.materials.append(mat_simple(name, col, rough))
    return bpy.data.objects.new("Tomas_Polaroid", me)


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


def walk_lines(img, mask_fn, n, length, color, a, rs):
    """Vetas o grietas: caminatas al azar."""
    h, w, _ = img.shape
    for _ in range(n):
        r, c = int(rs.integers(0, h)), int(rs.integers(0, w))
        for _k in range(length):
            if 0 <= r < h and mask_fn(r, c % w):
                img[r, c % w] = img[r, c % w] * (1 - a) + np.array(color) * a
            r += int(rs.integers(-1, 2))
            c += int(rs.integers(-1, 2))


def palette(s):
    base = dict(
        skin=[(0.68, 0.49, 0.35), (0.60, 0.46, 0.38), (0.49, 0.51, 0.54), (0.42, 0.46, 0.34), (0.80, 0.76, 0.62)][s],
        lips=[(0.62, 0.30, 0.26), (0.50, 0.32, 0.30), (0.34, 0.24, 0.42), (0.16, 0.14, 0.11), (0.1, 0.1, 0.1)][s],
        hair=[(0.07, 0.05, 0.04), (0.07, 0.05, 0.04), (0.06, 0.05, 0.05), (0.10, 0.08, 0.06), (0.09, 0.07, 0.05)][s],
        hood=[(0.62, 0.14, 0.10), (0.50, 0.12, 0.09), (0.46, 0.11, 0.09), (0.34, 0.10, 0.08), (0.30, 0.13, 0.10)][s],
        denim=[(0.18, 0.23, 0.38), (0.15, 0.19, 0.31), (0.14, 0.18, 0.29), (0.12, 0.15, 0.22), (0.12, 0.14, 0.19)][s],
        shoe=[(0.82, 0.80, 0.76), (0.70, 0.68, 0.63), (0.66, 0.64, 0.60), (0.48, 0.45, 0.38), (0.40, 0.37, 0.31)][s],
        tee=[(0.86, 0.84, 0.78), (0.72, 0.70, 0.64), (0.68, 0.67, 0.62), (0.50, 0.48, 0.38), (0.42, 0.38, 0.30)][s],
    )
    base = {k: np.array(v) for k, v in base.items()}
    base["stitch"] = np.array((0.55, 0.45, 0.28)) * (0.6 if s >= 3 else 1.0)
    return base


def paint_skin_region(img, s, pal, T, P, rs):
    h, w, _ = img.shape
    img[:] = pal["skin"] * (0.93 + 0.07 * noise(h, w, 6, 12))[:, :, None]
    if s == 3:  # piel moteada con vetas oscuras
        m = noise(h, w, 5, 9) * 0.6 + noise(h, w, 13, 23) * 0.4
        mix(img, m > 0.55, (0.24, 0.27, 0.20), 0.55)
        mix(img, m < 0.30, (0.55, 0.52, 0.38), 0.35)
        walk_lines(img, lambda r, c: True, 18, 20, (0.18, 0.20, 0.16), 0.7, rs)
    if s == 2:
        mix(img, noise(h, w, 5, 9) > 0.62, (0.42, 0.40, 0.50), 0.4)  # livideces


def paint_head(A, s, pal, rs):
    img = view(A, "head")
    T, P = cyl("head")
    d = dang(T, 90.0)
    ad = np.abs(d)
    h, w, _ = img.shape
    paint_skin_region(img, s, pal, T, P, rs)
    if s == 4:
        img[:] = pal["skin"] * (0.88 + 0.12 * noise(h, w, 6, 10))[:, :, None]
        mix(img, (ad > 55) & (ad < 110), (0.55, 0.50, 0.38), 0.45)       # sienes
        mix(img, (ad > 18) & (ad < 50) & (P < 1.58) & (P > 1.54), (0.45, 0.40, 0.30), 0.5)

    # Pelo: linea del pelo mas baja en los costados y la nuca
    hl = np.where(ad < 38, 1.660, np.where(ad < 80, 1.660 - (ad - 38) / 42 * 0.067, 1.593 - (ad - 80) / 100 * 0.065))
    fringe = (noise(h, w, 4, 40) - 0.5) * 0.016 * (ad < 45)
    hair = P > hl + fringe
    hair_col = pal["hair"] * (0.8 + 0.4 * noise(h, w, 30, 6))[:, :, None]
    if s < 3:
        img[hair] = hair_col[hair]
    elif s == 3:  # pelo opaco y con calvas
        bald = noise(h, w, 6, 14) > 0.62
        img[hair & ~bald] = hair_col[hair & ~bald]
    else:  # mechones sueltos sobre el craneo
        clumps = (noise(h, w, 7, 16) > 0.60) & (P > 1.66) & (ad > 40)
        img[clumps] = hair_col[clumps]
        dried = (noise(h, w, 5, 11) > 0.74) & (P > 1.64)
        mix(img, dried, (0.30, 0.24, 0.17), 0.8)

    # Orejas
    for sg in (-1, 1):
        ear = ell(T, P, 90 + 86 * sg, 1.598, 7, 0.022)
        img[ear] = pal["skin"] * 0.9 if s < 4 else np.array((0.28, 0.22, 0.16))
        mix(img, ell(T, P, 90 + 86 * sg, 1.598, 3, 0.010), (0, 0, 0), 0.35)

    if s == 4:
        paint_skull_face(img, T, P, d, ad, pal, rs)
        return

    # Cejas
    for sg in (-1, 1):
        arch = 1.6415 + 0.0025 * np.clip(1 - np.abs(d - 19 * sg) / 12, 0, 1)
        brow = (np.abs(P - arch) < 0.0019) & (sg * d > 9) & (sg * d < 30)
        if s < 3:
            mix(img, brow, pal["hair"], 0.8)
        else:
            mix(img, brow, pal["hair"], 0.4)

    # Ojos
    white = [(0.86, 0.84, 0.78), (0.80, 0.74, 0.70), (0.74, 0.71, 0.58), (0.70, 0.72, 0.62)][s]
    for sg in (-1, 1):
        te, ze = 90 + 21 * sg, 1.607
        if s == 1:
            mix(img, ell(T, P, te, ze - 0.0075, 8, 0.0045), (0.40, 0.28, 0.33), 0.55)   # ojeras
        if s == 3:
            mix(img, ell(T, P, te, ze, 11, 0.010), (0.10, 0.09, 0.07), 0.85)           # ojos hundidos
        eye = ell(T, P, te, ze, 8.0, 0.0048)
        img[eye] = white
        if s < 3:
            iris = ell(T, P, te, ze - 0.0004, 3.2, 0.0044)
            img[iris] = (0.16, 0.10, 0.06) if s < 2 else (0.22, 0.18, 0.15)
        if s < 2:
            img[ell(T, P, te, ze + 0.0046, 8.5, 0.0013)] = pal["hair"] * 1.2     # pestanas
        else:  # muerto: parpados a medio cerrar
            img[ell(T, P, te, ze, 7.0, 0.0050) & (P > ze - 0.0008)] = pal["skin"] * 0.82
            mix(img, ell(T, P, te, ze - 0.0008, 7.0, 0.0010), (0, 0, 0), 0.5)

    # Nariz
    for sg in (-1, 1):
        mix(img, ell(T, P, 90 + 3.5 * sg, 1.561, 1.6, 0.0022), (0, 0, 0), 0.55)
    mix(img, ell(T, P, 90, 1.5555, 7, 0.0028), (0, 0, 0), 0.22)
    mix(img, (ad > 22) & (ad < 46) & (P > 1.545) & (P < 1.575), (0, 0, 0), 0.10)      # bajo los pomulos
    mix(img, P < 1.51, (0, 0, 0), 0.15)

    # Boca
    zl = 1.531
    if s == 0:  # sonrisa: comisuras arriba y dientes
        curve = zl + 0.0045 * (ad / 12) ** 2
        lips = (ad < 13) & (np.abs(P - curve) < 0.0042)
        img[lips] = pal["lips"]
        teeth = (ad < 9) & (P > curve - 0.0012) & (P < curve + 0.0022)
        img[teeth] = (0.86, 0.84, 0.76)
        mix(img, (ad < 13) & (np.abs(P - (curve - 0.0016)) < 0.0008), (0, 0, 0), 0.6)
        mix(img, ell(T, P, 90 + 20, 1.545, 7, 0.008) | ell(T, P, 90 - 20, 1.545, 7, 0.008), (0.75, 0.35, 0.30), 0.15)
    elif s in (1, 2):
        curve = zl - 0.0015 * (ad / 11) ** 2
        lips = (ad < 11) & (np.abs(P - curve) < 0.0038)
        img[lips] = pal["lips"]
        mix(img, (ad < 11) & (np.abs(P - curve) < 0.0007), (0, 0, 0), 0.55)
    else:  # labios retraidos: dientes a la vista
        mouth = (ad < 13) & (np.abs(P - zl) < 0.009)
        img[mouth] = (0.06, 0.05, 0.04)
        teeth = (ad < 11) & (((P > zl + 0.0005) & (P < zl + 0.0055)) | ((P < zl - 0.001) & (P > zl - 0.006)))
        gaps = (np.round(d / 3.2) * 3.2 - d) ** 2 < 0.4
        img[teeth & ~gaps] = (0.70, 0.64, 0.45)
    if s < 3:  # sombra de barba
        mix(img, (P < 1.548) & (ad < 30) & ~lips, (0.20, 0.15, 0.12), 0.12)
    if s == 2:  # cianosis y espuma (sobredosis)
        mix(img, (P < 1.548) & (ad < 18), (0.30, 0.30, 0.50), 0.25)
        img[lips] = pal["lips"]
        foam = (ad < 12) & (np.abs(P - zl) < 0.0035) & (rs.random(P.shape) > 0.35)
        foam |= (d > 3) & (d < 11) & (P < zl) & (P > 1.497 + (11 - d) * 0.002) & (rs.random(P.shape) > 0.45)
        img[foam] = (0.88, 0.88, 0.84)
        mix(img, ell(T, P, 90, 1.598, 30, 0.012), (0.30, 0.28, 0.36), 0.25)  # ojeras moradas
    if s == 3:  # liquido oscuro de la nariz y la boca
        for t0, z0 in ((90 + 3, 1.558), (90 - 6, 1.522), (90 + 9, 1.522)):
            drip = (np.abs(dang(T, t0)) < 1.6) & (P < z0) & (P > z0 - 0.02 - rs.random() * 0.01)
            mix(img, drip, (0.12, 0.09, 0.05), 0.7)


def paint_skull_face(img, T, P, d, ad, pal, rs):
    bone = pal["skin"]
    for sg in (-1, 1):
        mix(img, ell(T, P, 90 + 22 * sg, 1.605, 14, 0.016), (0.35, 0.30, 0.22), 0.6)   # borde de la cuenca
        img[ell(T, P, 90 + 22 * sg, 1.604, 10.5, 0.012)] = (0.02, 0.02, 0.02)          # cuenca
        mix(img, (np.abs(d - 30 * sg) < 18) & (np.abs(P - 1.585) < 0.004), (1, 1, 1), 0.18)  # pomulo
    cav = (P > 1.554) & (P < 1.582) & (ad < 7.5 - (P - 1.554) / 0.028 * 5.0)
    img[cav] = (0.02, 0.02, 0.02)                                                       # cavidad nasal
    zl = 1.531
    img[(ad < 21) & (np.abs(P - zl) < 0.012)] = (0.06, 0.05, 0.04)
    gaps = (np.abs(np.round(d / 4.2) * 4.2 - d) < 0.9)
    upper = (ad < 19) & (P > zl + 0.0010) & (P < zl + 0.0095)
    lower = (ad < 17) & (P < zl - 0.0020) & (P > zl - 0.0095)
    img[(upper | lower) & ~gaps] = bone * 1.08
    mix(img, (ad < 40) & (np.abs(P - 1.507) < 0.0025), (0, 0, 0), 0.45)                # mandibula
    walk_lines(img, lambda r, c: True, 3, 14, (0.25, 0.22, 0.16), 0.8, rs)            # grietas


def paint_cloth_marks(img, s, rs, T, P):
    h, w, _ = img.shape
    if s == 2:
        mix(img, noise(h, w, 4, 8) > 0.68, (0.10, 0.05, 0.04), 0.35)   # mojado
    if s == 3:
        st = noise(h, w, 5, 9) * 0.6 + noise(h, w, 11, 19) * 0.4
        mix(img, st > 0.55, (0.12, 0.08, 0.04), 0.6)
        mix(img, rs.random((h, w)) > 0.985, (0.55, 0.60, 0.45), 0.8)   # moho
    if s == 4:
        img *= 0.85
        mix(img, np.ones((h, w), bool), (0.25, 0.20, 0.15), 0.3)
        holes = (noise(h, w, 6, 12) * 0.7 + noise(h, w, 15, 27) * 0.3) > 0.66
        rim = (np.roll(holes, 1, 0) | np.roll(holes, 1, 1)) & ~holes
        mix(img, rim, (0.6, 0.5, 0.4), 0.4)
        img[holes] = (0.02, 0.02, 0.02)


def paint_torso(A, s, pal, rs):
    img = view(A, "torso")
    T, P = cyl("torso")
    d = dang(T, 90.0)
    ad = np.abs(d)
    h, w, _ = img.shape
    img[:] = pal["hood"] * (0.88 + 0.12 * noise(h, w, 8, 16))[:, :, None]
    img *= (1.0 - 0.12 * np.clip((ad - 70) / 60, 0, 1))[:, :, None]
    dark = pal["hood"] * 0.62
    img[(P > 1.432) & (ad < 38)] = pal["tee"]                              # camiseta blanca
    img[(P > 1.424) & (P <= 1.432) & (ad < 40)] = dark                     # borde del cuello
    hood = (P > 1.385) & (ad > 115)                                        # capucha caida
    img[hood] = pal["hood"] * 0.78
    mix(img, hood & (np.abs(P - 1.405) < 0.004), (0, 0, 0), 0.35)
    for sg in (-1, 1):                                                      # cordones
        cord = (np.abs(d - 7 * sg) < 1.5) & (P > 1.30) & (P < 1.43)
        img[cord] = pal["tee"] * 0.95
        img[(np.abs(d - 7 * sg) < 1.8) & (P > 1.295) & (P <= 1.31)] = (0.45, 0.45, 0.45)
    pocket_top = (ad < 30) & (np.abs(P - 1.13) < 0.004)
    slant = (ad >= 30) & (ad < 42) & (np.abs(P - (1.13 - (ad - 30) / 12 * 0.09)) < 0.005)
    sides = (np.abs(ad - 42) < 1.5) & (P > 1.00) & (P < 1.04)
    img[pocket_top | slant | sides] = dark                                 # bolsillo canguro
    mix(img, (ad < 42) & (P > 1.0) & (P < 1.13) & ~(pocket_top | slant), (0, 0, 0), 0.08)
    rib = P < 0.985
    img[rib] = dark * (0.9 + 0.2 * ((np.round(T / 2.8) % 2) == 0))[rib][:, None]
    seams = (np.abs(dang(T, 0)) < 1.5) | (np.abs(dang(T, 180)) < 1.5)
    mix(img, seams, (0, 0, 0), 0.25)
    logo = np.abs(np.sqrt((dang(T, 70) / 6.0) ** 2 + ((P - 1.29) / 0.012) ** 2) - 1.0) < 0.28
    mix(img, logo | ell(T, P, 70, 1.29, 1.6, 0.003), (0.85, 0.82, 0.75), 0.6 if s < 3 else 0.3)
    mix(img, (ad < 50) & (np.abs(P - 1.03) < 0.003), (0, 0, 0), 0.15)      # arrugas de la cintura
    if s == 2:
        mix(img, ell(T, P, 95, 1.40, 18, 0.05), (0.10, 0.04, 0.03), 0.35)  # babas y espuma en el cuello
        mix(img, ell(T, P, 100, 1.425, 6, 0.006) & (rs.random(P.shape) > 0.4), (0.85, 0.85, 0.80), 0.8)
    paint_cloth_marks(img, s, rs, T, P)


def paint_arm(A, s, pal, rs):
    img = view(A, "arm")
    T, P = cyl("arm")
    d = dang(T, 90.0)
    h, w, _ = img.shape
    img[:] = pal["hood"] * (0.88 + 0.12 * noise(h, w, 10, 6))[:, :, None]
    dark = pal["hood"] * 0.62
    mix(img, (np.abs(d) < 45) & (np.abs(P - 0.45) < 0.03) & (np.round(P / 0.012) % 2 == 0), (0, 0, 0), 0.25)
    cuff = P > 0.69
    img[cuff] = dark * (0.9 + 0.2 * ((np.round(T / 6) % 2) == 0))[cuff][:, None]
    mix(img, np.abs(P - 0.20) < 0.004, (0, 0, 0), 0.25)
    mix(img, np.abs(dang(T, 180)) < 3, (0, 0, 0), 0.2)
    paint_cloth_marks(img, s, rs, T, P)


def paint_pelvis(A, s, pal, rs):
    img = view(A, "pelvis")
    T, P = cyl("pelvis")
    d = dang(T, 90.0)
    h, w, _ = img.shape
    img[:] = pal["denim"] * (0.82 + 0.18 * noise(h, w, 16, 8))[:, :, None]
    img[P > 0.955] = pal["denim"] * 0.8
    mix(img, (np.abs(d) < 1.5) & (P > 0.84), pal["stitch"], 0.3)
    for sg in (-1, 1):
        mix(img, np.abs(np.sqrt(((d - 40 * sg) / 14) ** 2 + ((P - 0.955) / 0.05) ** 2) - 1) < 0.12, pal["stitch"], 0.25)
        back = np.abs(dang(T, 270 + 32 * sg))
        mix(img, ((np.abs(back - 13) < 1.4) & (P > 0.83) & (P < 0.92)) | ((back < 13) & (np.abs(P - 0.92) < 0.003)),
            pal["stitch"], 0.5)
    paint_cloth_marks(img, s, rs, T, P)


def paint_leg(A, s, pal, rs):
    img = view(A, "leg")
    T, P = cyl("leg")
    d = dang(T, 90.0)
    h, w, _ = img.shape
    img[:] = pal["denim"] * (0.82 + 0.18 * noise(h, w, 60, 8))[:, :, None]
    fade = ((np.abs(d) < 45) & (P > 0.60) & (P < 0.85)) | ((np.abs(d) < 35) & (P > 0.46) & (P < 0.55))
    img[fade] *= 1.25
    mix(img, (np.abs(dang(T, 0)) < 2.5) | (np.abs(dang(T, 180)) < 2.5), pal["stitch"], 0.35)
    img[P < 0.13] *= 0.75
    mix(img, np.abs(P - 0.13) < 0.004, (0, 0, 0), 0.3)
    if s >= 2:
        mix(img, (P < 0.30) & (noise(h, w, 8, 6) > 0.5), (0.20, 0.16, 0.10), 0.35)  # tierra
    paint_cloth_marks(img, s, rs, T, P)


def paint_hand(A, s, pal, rs):
    img = view(A, "hand")
    h, w, _ = img.shape
    rr = np.arange(h)[:, None] + 0 * np.arange(w)[None, :]
    cc = 0 * np.arange(h)[:, None] + np.arange(w)[None, :]
    x = 0.70 + (cc % 32) / 31 * 0.185      # a lo largo de la mano
    y = -0.05 + rr / 63 * 0.10             # de lado a lado (arriba = pulgar)
    top = cc < 32                          # dorso
    if s == 4:
        img[:] = (0.10, 0.08, 0.06)
        for yc in (-0.026, -0.009, 0.008, 0.025):
            img[(np.abs(y - yc) < 0.0055) & (x > 0.74)] = pal["skin"] * (0.95 + 0.1 * rs.random())
            img[(np.abs(y - yc) < 0.0065) & (np.abs(x - 0.81) < 0.004)] = pal["skin"] * 0.7
        img[(y < -0.035) & (x < 0.80)] = pal["skin"]
        img[(x < 0.74) & (np.abs(y) < 0.03)] = pal["skin"] * 0.85
        return
    img[:] = pal["skin"] * (0.92 + 0.08 * noise(h, w, 6, 6))[:, :, None]
    if s == 3:
        mix(img, noise(h, w, 4, 6) > 0.55, (0.22, 0.25, 0.18), 0.5)
    for yc in (-0.017, 0.0, 0.017):                       # separacion de los dedos
        mix(img, (np.abs(y - yc) < 0.0016) & (x > 0.815), (0, 0, 0), 0.45)
    for yc in (-0.026, -0.009, 0.008, 0.025):
        mix(img, top & (np.abs(y - yc) < 0.004) & (np.abs(x - 0.81) < 0.003), (0, 0, 0), 0.25)   # nudillos
        nail = top & (np.abs(y - yc) < 0.0045) & (x > 0.862)
        img[nail] = [(0.78, 0.60, 0.52), (0.70, 0.58, 0.52), (0.40, 0.32, 0.50), (0.15, 0.12, 0.10)][s]
    mix(img, ~top & (np.abs(x - 0.77 - (y + 0.03) * 0.4) < 0.002), (0, 0, 0), 0.3)          # lineas de la palma
    if s in (1, 2):
        mix(img, top & (np.abs(y + 0.004 - (x - 0.7) * 0.15) < 0.0012) & (x < 0.80), (0.30, 0.30, 0.45), 0.4)  # venas


def paint_foot(A, s, pal, rs):
    img = view(A, "foot")
    h, w, _ = img.shape
    rr = np.arange(h)[:, None] + 0 * np.arange(w)[None, :]
    u = (0 * np.arange(h)[:, None] + np.arange(w)[None, :]) / (w - 1)
    img[:] = pal["shoe"] * (0.92 + 0.08 * noise(h, w, 6, 6))[:, :, None]
    sole = (u < 0.14) | (u > 0.86)
    img[sole] = (0.30, 0.29, 0.28)
    img[((u >= 0.14) & (u < 0.18)) | ((u > 0.82) & (u <= 0.86))] = pal["shoe"] * 0.8
    laces = (np.abs(u - 0.5) < 0.06) & (rr > 18) & (rr < 42)
    img[laces] = pal["shoe"] * 0.7
    mix(img, laces & ((rr + np.round(u * 60)) % 4 == 0), (0, 0, 0), 0.4)
    img[(rr < 6) & (np.abs(u - 0.5) < 0.1)] = pal["hood"]       # taloncito rojo
    if s >= 1:
        mix(img, noise(h, w, 5, 5) > 0.5 - 0.08 * s, (0.30, 0.25, 0.18), 0.25 + 0.1 * s)


def paint_neck(A, s, pal, rs):
    img = view(A, "neck")
    T, P = cyl("neck")
    paint_skin_region(img, s, pal, T, P, rs)
    mix(img, P > 1.50, (0, 0, 0), 0.15)
    if s == 4:
        img[:] = (0.20, 0.16, 0.12)
        img[np.abs(dang(T, 270)) < 25] = pal["skin"] * 0.9   # vertebras


def build_texture(s):
    rs = np.random.default_rng(100 + s)
    A = np.zeros((TEX, TEX, 3))
    pal = palette(s)
    paint_head(A, s, pal, rs)
    paint_torso(A, s, pal, rs)
    paint_arm(A, s, pal, rs)
    paint_pelvis(A, s, pal, rs)
    paint_leg(A, s, pal, rs)
    paint_hand(A, s, pal, rs)
    paint_foot(A, s, pal, rs)
    paint_neck(A, s, pal, rs)
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
# Materiales y estados
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


def mat_tomas(image):
    m, nt, out = _new_material("Tomas")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.name = "BSDF"
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = "Textura"
    tex.image = image
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    for n in ("Specular IOR Level", "Specular"):
        if n in b.inputs:
            b.inputs[n].default_value = 0.35
            break
    return m


def set_state(body, polaroid, s):
    L = LOOK[s]
    nt = body.data.materials[0].node_tree
    nt.nodes["Textura"].image = get_image(f"tomas_estado{s}")
    nt.nodes["BSDF"].inputs["Roughness"].default_value = L["rough"]
    kb = body.data.shape_keys.key_blocks
    kb["descompuesto"].value = L["desc"]
    kb["calavera"].value = L["skull"]
    polaroid.hide_render = not L["polaroid"]
    polaroid.hide_viewport = not L["polaroid"]


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
    p = {"_hips": (0, 0, 0.95), "Hips": ((0, 0, 1), FRONT), "Spine": ((0, 0.02, 1), FRONT),
         "Spine1": ((0, 0, 1), FRONT), "Spine2": ((0, -0.03, 1), FRONT), "Neck": ((0, -0.08, 1), FRONT),
         "Head": ((0, -0.02, 1), FRONT)}
    for s, nm in ((1, "Left"), (-1, "Right")):
        p[nm + "Shoulder"] = ((s, 0.02, -0.08), FRONT)
        p[nm + "Arm"] = ((0.17 * s, 0.03, -1), FRONT)
        p[nm + "ForeArm"] = ((0.10 * s, -0.12, -1), FRONT)
        p[nm + "Hand"] = ((0.05 * s, -0.04, -1), FRONT)
        p[nm + "UpLeg"] = ((0.03 * s, 0, -1), FRONT)
        p[nm + "Leg"] = ((0, 0.02, -1), FRONT)
        p[nm + "Foot"] = ((0.08 * s, -1, -0.55), UP)
        p[nm + "ToeBase"] = ((0.08 * s, -1, 0), UP)
    return p


def pose_muerto():
    """Encorvado, hombros caidos, brazos colgando, la cabeza ladeada hacia abajo."""
    p = {"_hips": (0, 0.03, 0.925), "Hips": ((0, 0.08, 1), FRONT), "Spine": ((0, -0.05, 1), FRONT),
         "Spine1": ((0, -0.18, 1), FRONT), "Spine2": ((0, -0.32, 1), FRONT), "Neck": ((0.06, -0.60, 1), FRONT),
         "Head": ((0.30, -0.50, 0.80), (0.15, -0.60, -0.75))}
    p["LeftShoulder"] = ((1, -0.15, -0.35), FRONT)
    p["RightShoulder"] = ((-1, -0.15, -0.30), FRONT)
    p["LeftArm"] = ((0.06, -0.12, -1), FRONT)
    p["RightArm"] = ((-0.07, -0.10, -1), FRONT)
    p["LeftForeArm"] = ((0.02, -0.05, -1), FRONT)
    p["RightForeArm"] = ((-0.01, -0.06, -1), FRONT)
    p["LeftHand"] = ((0.0, 0.05, -1), (0.3, -0.9, 0))
    p["RightHand"] = ((0.0, 0.04, -1), (-0.4, -0.9, 0))
    p["LeftUpLeg"] = ((0.08, 0.02, -1), FRONT)
    p["RightUpLeg"] = ((-0.02, 0.0, -1), FRONT)
    p["LeftLeg"] = ((0.0, 0.04, -1), FRONT)
    p["RightLeg"] = ((0.02, 0.03, -1), FRONT)
    p["LeftFoot"] = ((0.35, -1, -0.5), UP)
    p["RightFoot"] = ((0.25, -1, -0.5), UP)
    p["LeftToeBase"] = ((0.35, -1, 0), UP)
    p["RightToeBase"] = ((0.25, -1, 0), UP)
    return p


def pose_sentado(look=(0.37, -0.93, 0.08)):
    """Sentado en el sofa, echado hacia atras, un brazo en el apoyabrazos y la otra mano
    sobre el muslo; mira hacia 'look' (Elias, en la entrada). El origen va en el piso,
    bajo la cadera; el apoyabrazos queda a 0.30-0.50 m a su izquierda (+X)."""
    p = {"_hips": (0, 0.02, 0.62), "Hips": ((0, 0.35, 1), (0, -1, 0.35)), "Spine": ((0, 0.35, 1), FRONT),
         "Spine1": ((0, 0.25, 1), FRONT), "Spine2": ((0, 0.05, 1), FRONT), "Neck": ((0.03, -0.12, 1), FRONT),
         "Head": ((0.05, -0.05, 1), look)}
    p["LeftShoulder"] = ((1, 0.05, -0.20), FRONT)
    p["LeftArm"] = ((0, 0, -1), FRONT)
    p["LeftForeArm"] = ((0, -1, 0), (-1, 0, 0))
    p["LeftHand"] = ((0.10, -1, -0.50), (-1, 0, 0))
    p["RightShoulder"] = ((-1, 0.05, -0.15), FRONT)
    p["RightArm"] = ((0, 0, -1), FRONT)
    p["RightForeArm"] = ((0, -1, 0), (1, 0, 0))
    p["RightHand"] = ((0.20, -1, -0.35), (1, 0, 0))
    p["LeftUpLeg"] = ((0, -1, 0), UP)
    p["LeftLeg"] = ((0, 0, -1), FRONT)
    p["LeftFoot"] = ((0.15, -1, -0.35), UP)
    p["LeftToeBase"] = ((0.15, -1, 0), UP)
    p["RightUpLeg"] = ((0, -1, 0), UP)
    p["RightLeg"] = ((0, 0, -1), FRONT)
    p["RightFoot"] = ((-0.10, -1, -0.30), UP)
    p["RightToeBase"] = ((-0.10, -1, 0), UP)
    p["_ik"] = {
        "LeftArm": ((0.33, -0.16, 0.70), (0.5, 0.6, -0.4)),       # mano sobre el apoyabrazos
        "RightArm": ((-0.05, -0.27, 0.67), (-0.5, 0.4, -0.5)),    # mano sobre el muslo
        "LeftUpLeg": ((0.17, -0.47, 0.09), (0.1, -1, 0.6)),
        "RightUpLeg": ((-0.16, -0.55, 0.09), (-0.1, -1, 0.5)),
    }
    return p


def pose_sentado_muerto():
    """La misma postura, pero sin vida: la cabeza caida hacia el apoyabrazos, las manos sueltas."""
    p = pose_sentado()
    p["Spine2"] = ((0.08, 0.0, 1), FRONT)
    p["Neck"] = ((0.15, -0.35, 1), FRONT)
    p["Head"] = ((0.50, -0.50, 0.65), (0.25, -0.45, -0.85))
    p["RightHand"] = ((-0.10, -1, -0.20), (-1, 0, 0))     # palma arriba
    p["LeftHand"] = ((0.30, -0.30, -1), (-1, 0, 0))       # colgando del apoyabrazos
    p["_ik"] = {
        "LeftArm": ((0.36, -0.08, 0.69), (0.5, 0.6, -0.4)),
        "RightArm": ((-0.22, -0.12, 0.58), (-0.6, 0.3, -0.3)),
        "LeftUpLeg": ((0.24, -0.45, 0.09), (0.2, -1, 0.6)),
        "RightUpLeg": ((-0.20, -0.50, 0.09), (-0.2, -1, 0.5)),
    }
    return p


POSES = {"de_pie": pose_de_pie, "muerto_de_pie": pose_muerto, "sentado": pose_sentado,
         "sentado_muerto": pose_sentado_muerto}


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


# ---------------------------------------------------------------------------
# Render y post-proceso PS1
# ---------------------------------------------------------------------------
BAYER4 = np.array([[0, 8, 2, 10],
                   [12, 4, 14, 6],
                   [3, 11, 1, 9],
                   [15, 7, 13, 5]], dtype=np.float32) / 16.0 - 0.5 + 1.0 / 32.0


def ps1_quantize(src):
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


def render_to(cam, res, name):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    raw = os.path.join(RENDER_DIR, f"_{name}_raw.png")
    sc.render.filepath = raw
    bpy.ops.render.render(write_still=True)
    q = ps1_quantize(raw)
    os.remove(raw)
    return q


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
        sc.eevee.taa_render_samples = 16


def look_at(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()


def studio_sheet(rig, body, pol):
    """Hoja de estados: cuerpo entero (camara ortografica) y cara de cada estado."""
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

    light("clave", "AREA", (-1.6, -2.2, 2.4), (0, 0, 1.2), 260, (1.0, 0.86, 0.72), 1.2)
    light("contra", "SPOT", (1.3, 1.6, 2.3), (0, 0, 1.2), 420, (0.62, 0.75, 1.0))
    light("relleno", "POINT", (1.8, -1.6, 1.0), (0, 0, 1), 25, (0.7, 0.75, 0.85))

    cd = bpy.data.cameras.new("cam_cuerpo")
    cd.type = "ORTHO"
    cd.ortho_scale = 2.0
    cam_body = bpy.data.objects.new("cam_cuerpo", cd)
    col.objects.link(cam_body)
    a = R(22)
    cam_body.location = (math.sin(a) * 4, -math.cos(a) * 4, 0.93)
    look_at(cam_body, (0, 0, 0.93))

    cf = bpy.data.cameras.new("cam_cara")
    cf.lens = 85
    cf.clip_start = 0.05
    cam_face = bpy.data.objects.new("cam_cara", cf)
    col.objects.link(cam_face)
    a = R(18)
    cam_face.location = (math.sin(a) * 0.78, -0.02 - math.cos(a) * 0.78, 1.62)
    look_at(cam_face, (0, -0.02, 1.61))

    bodies, faces = [], []
    for s in STATES:
        set_state(body, pol, s)
        apply_pose(rig, pose_de_pie() if s < 2 else pose_muerto())
        bodies.append(render_to(cam_body, (192, 360), f"cuerpo{s}"))
        apply_pose(rig, pose_de_pie())
        faces.append(render_to(cam_face, (192, 192), f"cara{s}"))
        print(f"[hoja] estado {s}")
    top = np.concatenate(bodies, axis=1)
    bottom = np.concatenate(faces, axis=1)
    sheet = np.concatenate([bottom, top], axis=0)  # fila 0 = abajo
    for i in range(1, len(STATES)):
        sheet[:, i * 192 - 1:i * 192 + 1] = 0.0
    sheet[191:193, :] = 0.0
    save_png(sheet, os.path.join(RENDER_DIR, "tomas_estados.png"), 2)


def append_tomas(path):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = ["Tomas_Rig", "Tomas", "Tomas_Polaroid"]
    col = bpy.data.collections.new("Tomas")
    bpy.context.scene.collection.children.link(col)
    for ob in dst.objects:
        col.objects.link(ob)
    rig, body, pol = dst.objects
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return rig, body, pol


def render_in_4b(asset):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(SCENE_DIR, "departamento_4b.blend"))
    rig, body, pol = append_tomas(asset)
    rig.location = (2.10, 3.70, 0.0)
    clothes = bpy.data.objects.get("ropa_sofa")
    if clothes:
        clothes.hide_render = True  # Tomas aparece justo donde quedo tirada la ropa
    cam = bpy.data.objects["Cam_sala"]
    for name, pose, s in (("tomas_sofa", pose_sentado(), 1), ("tomas_sofa_muerto", pose_sentado_muerto(), 2)):
        set_state(body, pol, s)
        apply_pose(rig, pose)
        q = render_to(cam, (RES_X, RES_Y), name)
        save_png(q, os.path.join(RENDER_DIR, name + ".png"), 4)
        print(f"[render] {name}")


def render_in_hallway(asset):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(SCENE_DIR, "prueba_estilo_pasillo.blend"))
    sil = bpy.data.objects.get("Tomas_silueta")
    if sil:
        for ob in [sil] + list(sil.children_recursive):
            ob.hide_render = True
    rig, body, pol = append_tomas(asset)
    rig.location = (-0.12, 13.3, 0.0)
    rig.rotation_euler = (0, 0, R(-8))
    set_state(body, pol, 2)
    apply_pose(rig, pose_muerto())
    q = render_to(bpy.data.objects["Camara"], (RES_X, RES_Y), "tomas_pasillo")
    save_png(q, os.path.join(RENDER_DIR, "tomas_pasillo.png"), 4)
    print("[render] tomas_pasillo")


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    for d in (TEX_DIR, SCENE_DIR, RENDER_DIR):
        os.makedirs(d, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    for s in STATES:
        save_texture(f"tomas_estado{s}", build_texture(s))
    mat = mat_tomas(get_image("tomas_estado1"))

    rig = build_rig()
    body = build_mesh(mat)
    scene.collection.objects.link(body)
    body.parent = rig
    mod = body.modifiers.new("Armature", "ARMATURE")
    mod.object = rig
    pol = build_polaroid()
    scene.collection.objects.link(pol)
    bpy.context.view_layer.update()
    world = pol.matrix_world.copy()
    pol.parent = rig
    pol.parent_type = "BONE"
    pol.parent_bone = "Spine2"
    bpy.context.view_layer.update()
    pol.matrix_world = world

    tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
    ptris = sum(len(p.vertices) - 2 for p in pol.data.polygons)
    print(f"[info] Tomas: {len(body.data.vertices)} vertices, {tris} triangulos (+{ptris} la Polaroid), "
          f"{len(rig.data.bones)} huesos")

    key_poses(rig)
    set_state(body, pol, 1)
    asset = os.path.join(SCENE_DIR, "tomas.blend")
    bpy.ops.wm.save_as_mainfile(filepath=asset)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print(f"[aviso] rutas relativas: {e}")
    for f in (asset + "1",):
        if os.path.exists(f):
            os.remove(f)

    studio_sheet(rig, body, pol)
    if not SHEET_ONLY:
        render_in_4b(asset)
        render_in_hallway(asset)
    print(f"[info] listo en {time.time() - t0:.0f} s")


main()
