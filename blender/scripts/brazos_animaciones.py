r"""
Animaciones de los brazos de Elias en primera persona, probadas dentro del 4B.

Todas las animaciones son relativas a la camara (el esqueleto cuelga de la
cabeza), igual que en Unity, donde los brazos van como hijos de la camara.

Clips (30 cuadros por segundo):
  reposo              loop 2 s: brazos abajo, fuera de cuadro, respirando
  temblor             loop 2 s, ADITIVO: el temblor de la abstinencia. Se suma
                      encima de cualquier otro clip (en Unity, una capa aditiva
                      cuyo peso puede seguir al nivel de abstinencia)
  mirar_manos         3.8 s: levanta las manos, las mira, gira las palmas (Noche 1)
  abrir_puerta        2.8 s: agarra la perilla, la gira y empuja la puerta
  telefono_contestar  2.4 s: levanta el auricular y se lo lleva al oido
  telefono_colgar     1.8 s: devuelve el auricular y baja la mano

Requiere scenes/departamento_4b.blend y scenes/brazos_primera_persona.blend
(se generan con departamento_4b.py y brazos_primera_persona.py).

Uso (PowerShell, desde la carpeta del proyecto):
  & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup `
      -P blender\scripts\brazos_animaciones.py -- blender
  Solo algunos clips:                 ... -- blender abrir_puerta,mirar_manos
  Solo 6 cuadros por clip (rapido):   ... -- blender --claves

Salidas (dentro de la carpeta blender/):
  scenes/brazos_animaciones.blend      el 4B con Elias y todos los clips
  renders/anim_<clip>.mp4              vista previa PS1 (con el temblor sumado)
  renders/anim_<clip>_claves.png       seis cuadros del clip
  renders/anim_todas.mp4               todas las vistas previas seguidas

Y en el proyecto de Unity (ver exportar_unity.py):
  unity/Assets/Art/BrazosElias/brazos_elias.fbx          esqueleto, malla, forma "consumido"
                                                         y los siete clips (con mirar_brazos)
  unity/Assets/Art/BrazosElias/brazos_elias_escena.json  luz de los brazos, camara, los cuatro
                                                         estados, los clips y, por clip, el
                                                         movimiento de la cabeza, la puerta y
                                                         el auricular
  unity/Assets/Art/BrazosElias/Textures/brazos_estado0..3.png
  Para exportar sin renderizar las vistas previas: ... -- blender reposo
"""
import math
import os
import shutil
import subprocess
import sys
import time

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exportar_unity  # noqa: E402

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = os.path.abspath(ARGS[0]) if ARGS else os.getcwd()
FLAGS = [a for a in ARGS[1:] if a.startswith("--")]
PICK = [a for a in ARGS[1:] if not a.startswith("--")]
ONLY = PICK[0].split(",") if PICK else None
KEYS_ONLY = "--claves" in FLAGS

SCENE_DIR = os.path.join(ROOT, "scenes")
RENDER_DIR = os.path.join(ROOT, "renders")

FPS = 30
RES_X, RES_Y = 480, 270
COLOR_LEVELS = 32
R = math.radians

# Medidas del esqueleto (ver brazos_primera_persona.py)
S_REST = {1: Vector((0.17, -0.06, -0.24)), -1: Vector((-0.17, -0.06, -0.24))}
LU, LF = 0.30, 0.26               # brazo y antebrazo
GRIP_FWD, GRIP_PALM = 0.075, 0.03  # punto de agarre: delante de la muneca, hacia la palma
SFX = {1: ".R", -1: ".L"}
# Los brazos van un poco adelantados respecto del ojo (como en todo juego en
# primera persona), para que las manos entren en cuadro sin estirarse de mas.
VM = Vector((0.0, 0.05, 0.02))

# Dedos: angulos de flexion de las tres falanges (grados)
def curls(index, middle, ring, pinky, thumb):
    return {"index": index, "middle": middle, "ring": ring, "pinky": pinky, "thumb": thumb}


RELAX = curls((12, 20, 12), (16, 26, 14), (22, 30, 16), (28, 32, 18), (0, 12, 14))
OPEN = curls((4, 6, 4), (4, 6, 4), (6, 8, 6), (8, 10, 6), (-5, 5, 5))
SPREAD = curls((3, 6, 4), (2, 5, 3), (5, 7, 5), (8, 10, 6), (-8, 2, 6))
GRIP_KNOB = curls((55, 70, 40), (60, 75, 45), (62, 75, 45), (65, 70, 40), (20, 25, 20))
GRIP_PHONE = curls((50, 60, 35), (55, 65, 40), (58, 65, 40), (60, 60, 35), (25, 20, 15))

scene = bpy.context.scene


# ---------------------------------------------------------------------------
# Matematica
# ---------------------------------------------------------------------------
def clamp01(u):
    return min(max(u, 0.0), 1.0)


def smooth(u):
    u = clamp01(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp01(u)
    return 1 - (1 - u) ** 3


def hand_rot(fingers, palm, side):
    """Rotacion de la mano a partir de hacia donde apuntan los dedos y hacia donde mira la palma.
    Ejes del hueso: Y = dedos, Z = pulgar; X = dorso (mano derecha) o palma (izquierda)."""
    y = Vector(fingers).normalized()
    n = Vector(palm)
    n = (n - n.dot(y) * y).normalized()
    x = -n if side > 0 else n
    z = x.cross(y)
    return Matrix((x, y, z)).transposed()


def hand_rot_thumb(thumb, palm, side):
    """Igual, pero a partir de hacia donde apunta el pulgar."""
    z = Vector(thumb).normalized()
    n = Vector(palm)
    n = (n - n.dot(z) * z).normalized()
    x = -n if side > 0 else n
    y = z.cross(x)
    return Matrix((x, y, z)).transposed()


def col(m, i):
    return Vector((m[0][i], m[1][i], m[2][i]))


def palm_of(m, side):
    return -col(m, 0) if side > 0 else col(m, 0)


def frame(y_axis, z_hint, pos):
    """Matriz con el eje Y del hueso en y_axis y el eje Z lo mas cerca de z_hint."""
    y = y_axis.normalized()
    z = (z_hint - z_hint.dot(y) * y).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = pos
    return m


def head_matrix(pos, yaw, pitch):
    """Cabeza en el mundo: mira hacia su +Y; yaw gira a la izquierda, pitch negativo mira abajo."""
    return (Matrix.Translation(Vector(pos)) @ Matrix.Rotation(R(yaw), 4, "Z")
            @ Matrix.Rotation(R(pitch), 4, "X"))


def vec_at(keys, t):
    """keys: [(tiempo, (x, y, z))] -> vector interpolado con suavizado."""
    if not keys:
        return Vector()
    if t <= keys[0][0]:
        return Vector(keys[0][1])
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t <= t1:
            return Vector(a).lerp(Vector(b), smooth((t - t0) / (t1 - t0)))
    return Vector(keys[-1][1])


def breath(t, period=2.0, amp=0.006):
    return amp * math.sin(2 * math.pi * t / period)


# ---------------------------------------------------------------------------
# Poses: cada una es una funcion (ctx) -> dict(G, R, pole, curls), en el
# espacio del esqueleto (= la cabeza). G es el punto de agarre de la mano.
# ---------------------------------------------------------------------------
class Ctx:
    def __init__(self, t, head_w, root):
        self.t, self.root = t, root
        self.hinv = head_w.inverted()
        self.hrot = self.hinv.to_3x3()


def pose_rig(G, rot, pole, cur):
    def f(ctx):
        return dict(G=Vector(G), R=rot.copy(), pole=Vector(pole).normalized(), curls=cur)
    return f


def pose_world(G_fn, rot_fn, pole, cur):
    """Pose anclada a un objeto del mundo (perilla, auricular): se convierte cada cuadro."""
    def f(ctx):
        return dict(G=ctx.hinv @ G_fn(ctx.t), R=ctx.hrot @ rot_fn(ctx.t),
                    pole=Vector(pole).normalized(), curls=cur)
    return f


def pose_hang(side):
    """Brazo colgando junto al cuerpo, fuera de cuadro."""
    rot = hand_rot((0.05 * side, 0.15, -1.0), (-side, 0, 0), side)

    def f(ctx):
        G = S_REST[side] + ctx.root + Vector((0.03 * side, 0.11, -0.58))
        return dict(G=G, R=rot.copy(), pole=Vector((0.25 * side, -1, 0.1)).normalized(), curls=RELAX)
    return f


def blend(a, b, u):
    qa, qb = a["R"].to_quaternion(), b["R"].to_quaternion()
    if qa.dot(qb) < 0:
        qb.negate()
    cur = {k: tuple(x + (y - x) * u for x, y in zip(a["curls"][k], b["curls"][k])) for k in a["curls"]}
    return dict(G=a["G"].lerp(b["G"], u), R=qa.slerp(qb, u).to_matrix(),
                pole=a["pole"].lerp(b["pole"], u).normalized(), curls=cur)


def track_at(keys, ctx):
    """keys: [(tiempo, pose)]. Interpola con suavizado entre poses vecinas."""
    if ctx.t <= keys[0][0]:
        return keys[0][1](ctx)
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if ctx.t <= t1:
            return blend(p0(ctx), p1(ctx), smooth((ctx.t - t0) / (t1 - t0)))
    return keys[-1][1](ctx)


def head_at(keys, t):
    """keys: [(tiempo, posicion, yaw, pitch)]."""
    if t <= keys[0][0]:
        k = keys[0]
        return head_matrix(k[1], k[2], k[3])
    for k0, k1 in zip(keys, keys[1:]):
        if t <= k1[0]:
            u = smooth((t - k0[0]) / (k1[0] - k0[0]))
            pos = Vector(k0[1]).lerp(Vector(k1[1]), u)
            return head_matrix(pos, k0[2] + (k1[2] - k0[2]) * u, k0[3] + (k1[3] - k0[3]) * u)
    k = keys[-1]
    return head_matrix(k[1], k[2], k[3])


# ---------------------------------------------------------------------------
# Esqueleto: resolver el brazo (IK de dos huesos) y ponerlo en pose
# ---------------------------------------------------------------------------
REACH = {"max": -1.0}  # cuanto le falto al brazo mas estirado (positivo = no alcanzo)


def set_matrix(rig, name, m):
    rig.pose.bones[name].matrix = m
    bpy.context.view_layer.update()


def solve_arm(rig, side, root, pose):
    sfx = SFX[side]
    S = S_REST[side] + root
    rot = pose["R"]
    y_h, z_h = col(rot, 1), col(rot, 2)
    W = pose["G"] - y_h * GRIP_FWD - palm_of(rot, side) * GRIP_PALM

    v = W - S
    REACH["max"] = max(REACH["max"], v.length - (LU + LF))
    n = v.normalized()
    d = min(max(v.length, abs(LU - LF) + 1e-3), LU + LF - 1e-3)
    W = S + n * d
    a = (LU * LU - LF * LF + d * d) / (2 * d)
    h = math.sqrt(max(LU * LU - a * a, 0.0))
    p = pose["pole"] - pose["pole"].dot(n) * n
    if p.length < 1e-6:
        p = Vector((0, 0, -1)) - n.z * n
    p.normalize()
    E = S + n * a + p * h
    d_u = (E - S).normalized()
    d_f = (W - E).normalized()

    z_u = d_f - d_f.dot(d_u) * d_u          # hacia donde se dobla el codo
    if z_u.length < 1e-4:
        z_u = -p - (-p).dot(d_u) * d_u
    z_u.normalize()
    x_u = d_u.cross(z_u)
    z_f = x_u.cross(d_f).normalized()       # pliegue del codo

    set_matrix(rig, "upperarm" + sfx, frame(d_u, z_u, S))
    set_matrix(rig, "forearm" + sfx, frame(d_f, z_f, E))
    # La torsion del antebrazo se reparte en dos huesos (mitad y entera)
    zp = z_h - z_h.dot(d_f) * d_f
    theta = 0.0
    if zp.length > 1e-6:
        zp.normalize()
        theta = math.atan2(z_f.cross(zp).dot(d_f), z_f.dot(zp))
    set_matrix(rig, "forearm_twist.01" + sfx, frame(d_f, Matrix.Rotation(theta * 0.5, 3, d_f) @ z_f, E + d_f * 0.06))
    set_matrix(rig, "forearm_twist.02" + sfx, frame(d_f, Matrix.Rotation(theta, 3, d_f) @ z_f, E + d_f * 0.16))
    set_matrix(rig, "hand" + sfx, frame(y_h, z_h, W))


def set_fingers(rig, side, cur):
    for f, angs in cur.items():
        for i, a in enumerate(angs):
            pb = rig.pose.bones[f"{f}.0{i + 1}{SFX[side]}"]
            pb.rotation_quaternion = Matrix.Rotation(R(a) * side, 3, "Z").to_quaternion()


def reset_pose(rig):
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)


def arm_bone_names():
    names = []
    for side in (1, -1):
        s = SFX[side]
        names += [n + s for n in ("upperarm", "forearm", "forearm_twist.01", "forearm_twist.02", "hand")]
        for f in ("index", "middle", "ring", "pinky", "thumb"):
            names += [f"{f}.0{i}{s}" for i in (1, 2, 3)]
    return names


# ---------------------------------------------------------------------------
# Objetos del 4B que usan las animaciones
# ---------------------------------------------------------------------------
HINGE = Vector((3.40, 5.29, 0.0))           # bisagra de la puerta del dormitorio
KNOB_REL = Vector((0.065, -0.69, 1.01))     # perilla (lado del pasillo) respecto de la bisagra
DOOR_REST = -28.0                           # asi quedo entreabierta en el 4B
HS = {}                                     # auricular: centro y matriz en reposo


def knob_at(angle):
    rz = Matrix.Rotation(R(angle), 3, "Z")
    return HINGE + rz @ KNOB_REL, rz @ Vector((1, 0, 0)), rz


# ---------------------------------------------------------------------------
# Los clips
# ---------------------------------------------------------------------------
def clip_reposo():
    return dict(dur=2.0, loop=True, head=[(0.0, (2.2, 1.0, 1.6), 0.0, 0.0)],
                arms={1: [(0.0, pose_hang(1))], -1: [(0.0, pose_hang(-1))]})


def clip_mirar_manos():
    def show(side, palm, lift=0.0, cur=SPREAD):
        G = (0.085 * side, 0.43, -0.115 + lift)
        return pose_rig(G, hand_rot((-0.12 * side, 1.0, 0.05), palm, side), (0.6 * side, -0.3, -1.0), cur)

    arms = {}
    for side in (1, -1):
        dt = 0.0 if side > 0 else 0.08  # la izquierda va un poco atrasada
        arms[side] = [
            (0.0, pose_hang(side)),
            (0.9 + dt, show(side, (0, 0, -1))),                       # dorso arriba
            (1.7 + dt, show(side, (0, 0, -1), 0.01)),
            (2.15 + dt, show(side, (-side, 0, 0), 0.01, RELAX)),      # de canto
            (2.6 + dt, show(side, (0, 0, 1), 0.015)),                 # palmas arriba: se ven las marcas
            (3.1 + dt, show(side, (0, 0, 1), 0.01)),
            (3.8, pose_hang(side)),
        ]
    head = [(0.0, (2.2, 0.95, 0.85), 0.0, -18.0), (0.9, (2.2, 0.97, 0.84), 1.0, -27.0),
            (2.6, (2.2, 0.98, 0.83), -1.0, -29.0), (3.8, (2.2, 0.96, 0.85), 0.0, -20.0)]
    return dict(dur=3.8, head=head, arms=arms)


def door_angle(t):
    if t < 1.0:
        return 0.0
    if t < 1.55:
        return -22.0 * smooth((t - 1.0) / 0.55)
    return -22.0 - 60.0 * ease_out((t - 1.55) / 1.0)   # sigue abriendose sola


def clip_abrir_puerta():
    def grip(back=0.0, turn=0.0, cur=GRIP_KNOB, frozen=None):
        def g_fn(t):
            k, axis, _ = knob_at(door_angle(frozen if frozen is not None else t))
            return k + axis * back

        def r_fn(t):
            _, axis, rz = knob_at(door_angle(frozen if frozen is not None else t))
            rot = hand_rot(-axis + Vector((0, 0, -0.2)), rz @ Vector((0, -1, 0)), 1)
            return Matrix.Rotation(R(turn), 3, col(rot, 1)) @ rot
        return pose_world(g_fn, r_fn, (0.45, -0.1, -1.0), cur)

    right = [
        (0.0, pose_hang(1)),
        (0.50, grip(back=0.09, cur=OPEN)),
        (0.72, grip()),
        (1.00, grip(turn=40)),                                       # gira la perilla
        (1.55, grip(turn=40)),                                       # empuja: la mano sigue a la perilla
        (1.75, grip(back=0.07, turn=10, cur=OPEN, frozen=1.55)),     # suelta
        (2.30, pose_hang(1)),
        (2.80, pose_hang(1)),
    ]
    head = [(0.0, (4.10, 4.64, 1.58), 90.0, -20.0), (0.55, (3.945, 4.64, 1.52), 90.0, -32.0),
            (1.00, (3.945, 4.64, 1.52), 90.0, -32.0), (1.55, (3.685, 4.65, 1.52), 90.0, -26.0),
            (2.80, (3.55, 4.68, 1.56), 90.0, -10.0)]
    lean = [(0.0, (0, 0, 0)), (0.5, (0, 0.18, -0.03)), (1.6, (0, 0.18, -0.03)), (2.3, (0, 0, 0))]
    return dict(dur=2.8, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]}, door=door_angle)


def phone_grip(up=0.0, cur=GRIP_PHONE):
    rot = hand_rot((-0.25, 1, -0.55), (0, 0, -1), 1)  # palma abajo, dedos siguiendo al antebrazo
    return pose_world(lambda t: HS["center"] + Vector((0, 0, up)), lambda t: rot.copy(),
                      (0.6, -0.2, -1.0), cur)


def phone_ear():
    """Auricular en la oreja derecha (espacio de la cabeza): la punta del pulgar arriba."""
    ear, mouth = Vector((0.075, -0.06, -0.02)), Vector((0.035, 0.07, -0.15))
    rot = hand_rot_thumb(ear - mouth, (-1, 0, 0), 1)
    return pose_rig((ear + mouth) / 2, rot, (0.35, 0.6, -1.0), GRIP_PHONE)


def clip_telefono_contestar():
    right = [
        (0.0, pose_hang(1)),
        (0.55, phone_grip(up=0.07, cur=OPEN)),
        (0.75, phone_grip()),                  # agarra
        (0.95, phone_grip(up=0.06)),
        (1.85, phone_ear()),
        (2.40, phone_ear()),
    ]
    head = [(0.0, (3.00, 3.36, 1.45), 10.0, -38.0), (0.55, (2.98, 3.50, 1.22), 14.0, -50.0),
            (0.95, (2.99, 3.48, 1.25), 12.0, -46.0), (1.85, (3.27, 3.32, 1.56), -20.0, -14.0),
            (2.40, (3.30, 3.30, 1.57), -22.0, -16.0)]
    lean = [(0.0, (0, 0, 0)), (0.55, (0, 0.15, -0.05)), (0.95, (0, 0.15, -0.05)), (1.85, (0, 0, 0))]
    return dict(dur=2.4, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]},
                handset=(0.75, None))


def clip_telefono_colgar():
    right = [
        (0.0, phone_ear()),
        (0.80, phone_grip(up=0.06)),
        (0.95, phone_grip()),                  # lo deja en la base
        (1.10, phone_grip(up=0.07, cur=OPEN)),
        (1.80, pose_hang(1)),
    ]
    head = [(0.0, (3.30, 3.30, 1.57), -22.0, -16.0), (0.80, (2.99, 3.48, 1.25), 12.0, -46.0),
            (1.10, (2.98, 3.50, 1.22), 14.0, -50.0), (1.80, (3.00, 3.38, 1.42), 10.0, -36.0)]
    lean = [(0.0, (0, 0, 0)), (0.80, (0, 0.15, -0.05)), (1.10, (0, 0.15, -0.05)), (1.80, (0, 0, 0))]
    return dict(dur=1.8, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]},
                handset=(None, 0.95))


CLIPS = {
    "reposo": clip_reposo,
    "mirar_manos": clip_mirar_manos,
    "abrir_puerta": clip_abrir_puerta,
    "telefono_contestar": clip_telefono_contestar,
    "telefono_colgar": clip_telefono_colgar,
}
PREVIEW = ["mirar_manos", "abrir_puerta", "telefono_contestar", "telefono_colgar"]


def nframes(dur):
    return int(round(dur * FPS)) + 1


# ---------------------------------------------------------------------------
# Hornear los clips en acciones
# ---------------------------------------------------------------------------
def bake_clip(rig, head, door, name, clip):
    """Calcula la pose de cada cuadro y la guarda como accion del esqueleto.
    Tambien guarda la accion de la cabeza (y de la puerta) para la vista previa."""
    n = nframes(clip["dur"])
    REACH["max"] = -1.0
    rig.animation_data_create()
    rig.animation_data.action = None
    names = arm_bone_names()
    frames, prev, up_loc = [], {}, 0.0
    for f in range(1, n + 1):
        t = (f - 1) / FPS
        if clip.get("loop"):
            t = t % clip["dur"]
        hw = head_at(clip["head"], t)
        root = (VM + vec_at(clip.get("lean"), t)
                + Vector((0, 0, breath(t, period=clip["dur"] if clip.get("loop") else 2.5))))
        ctx = Ctx(t, hw, root)
        reset_pose(rig)
        rig.pose.bones["root"].location = root
        bpy.context.view_layer.update()
        for side in (1, -1):
            pose = track_at(clip["arms"][side], ctx)
            solve_arm(rig, side, root, pose)
            set_fingers(rig, side, pose["curls"])
        bpy.context.view_layer.update()
        up_loc = max([up_loc] + [rig.pose.bones["upperarm" + s].location.length for s in (".R", ".L")])
        rec = {"root": rig.pose.bones["root"].location.copy()}
        for bn in names:
            q = rig.pose.bones[bn].rotation_quaternion.copy()
            if bn in prev and prev[bn].dot(q) < 0:  # evita saltos de signo entre cuadros
                q.negate()
            prev[bn] = q
            rec[bn] = q
        frames.append((f, hw, rec))

    # Llaves del esqueleto (sin evaluar la animacion entre medio)
    reset_pose(rig)
    root_pb = rig.pose.bones["root"]
    for f, _, rec in frames:
        root_pb.location = rec["root"]
        root_pb.keyframe_insert("location", frame=f, group="root")
        for bn in names:
            pb = rig.pose.bones[bn]
            pb.rotation_quaternion = rec[bn]
            pb.keyframe_insert("rotation_quaternion", frame=f, group=bn)
    act = rig.animation_data.action
    act.name = name
    act.use_fake_user = True
    rig.animation_data.action = None

    # Cabeza (y puerta) para la vista previa
    head.animation_data_create()
    head.animation_data.action = None
    for f, hw, _ in frames:
        loc, rot, _s = hw.decompose()
        head.location = loc
        head.rotation_euler = rot.to_euler("XYZ")
        head.keyframe_insert("location", frame=f)
        head.keyframe_insert("rotation_euler", frame=f)
    head_act = head.animation_data.action
    head_act.name = "cabeza_" + name
    head_act.use_fake_user = True
    head.animation_data.action = None

    door_act = None
    if clip.get("door"):
        door.animation_data_create()
        door.animation_data.action = None
        for f in range(1, n + 1):
            door.rotation_euler.z = R(clip["door"]((f - 1) / FPS))
            door.keyframe_insert("rotation_euler", index=2, frame=f)
        door_act = door.animation_data.action
        door_act.name = "puerta_" + name
        door_act.use_fake_user = True
        door.animation_data.action = None
        door.rotation_euler.z = R(DOOR_REST)
    print(f"[clip] {name}: {n} cuadros; alcance sobrante {-REACH['max'] * 100:.1f} cm; "
          f"desfase del hombro {up_loc * 1000:.2f} mm")
    return dict(action=act, head=head_act, door=door_act, frames=n)


def bake_tremor(rig):
    """Temblor de abstinencia: pequenas rotaciones alrededor del reposo de cada hueso.
    Frecuencias de 7, 4.5 y 1.5 Hz: en 2 s caben ciclos enteros, asi el loop no salta."""
    rng = np.random.default_rng(11)
    n = nframes(2.0)
    amp = {"forearm_twist.02": 1.2, "upperarm": 0.5, "forearm": 0.8, "hand": 2.5,
           ".01": 3.0, ".02": 2.0, ".03": 1.5}
    rig.animation_data.action = None
    reset_pose(rig)
    bones = []
    for bn in arm_bone_names():
        if bn.startswith("forearm_twist.01"):
            continue
        key = next(k for k in amp if bn.startswith(k) or (k.startswith(".") and k in bn))
        a = amp[key] * (0.8 if bn.startswith("thumb") else 1.0)
        w = rng.uniform(0.3, 1.0, 3)
        if bn.startswith("forearm_twist"):
            w = np.array([0.0, 1.0, 0.0])  # solo gira sobre su eje (pronacion)
        ph = rng.uniform(0, 2 * math.pi, (3, 3))
        bones.append((bn, a, w, ph))
    for f in range(1, n + 1):
        t = (f - 1) / FPS
        for bn, a, w, ph in bones:
            e = []
            for k in range(3):
                s = (0.6 * math.sin(2 * math.pi * 7.0 * t + ph[k][0])
                     + 0.3 * math.sin(2 * math.pi * 4.5 * t + ph[k][1])
                     + 0.1 * math.sin(2 * math.pi * 1.5 * t + ph[k][2]))
                e.append(R(a) * w[k] * s)
            pb = rig.pose.bones[bn]
            pb.rotation_quaternion = Euler(e).to_quaternion()
            pb.keyframe_insert("rotation_quaternion", frame=f, group=bn)
    act = rig.animation_data.action
    act.name = "temblor"
    act.use_fake_user = True
    rig.animation_data.action = None
    reset_pose(rig)
    print(f"[clip] temblor: {n} cuadros (aditivo)")
    return act


def preview_setup(rig, head, door, handset, info, tremor, clip):
    """Clip base + temblor encima (mezcla 'Combine' del NLA), cabeza y puerta."""
    ad = rig.animation_data
    ad.action = None
    for tr in list(ad.nla_tracks):
        ad.nla_tracks.remove(tr)
    base = ad.nla_tracks.new()
    base.name = "clip"
    base.strips.new(info["action"].name, 1, info["action"])
    top = ad.nla_tracks.new()
    top.name = "temblor"
    s = top.strips.new("temblor", 1, tremor)
    s.blend_type = "COMBINE"
    s.repeat = max(1.0, math.ceil(info["frames"] / (nframes(2.0) - 1)))
    head.animation_data.action = info["head"]
    if info["door"]:
        door.animation_data.action = info["door"]
    else:
        if door.animation_data:
            door.animation_data.action = None
        door.rotation_euler.z = R(DOOR_REST)
    if handset.animation_data:
        handset.animation_data.action = None
    handset.matrix_world = HS["rest"]
    scene.frame_start, scene.frame_end = 1, info["frames"]


def bake_handset(rig, handset, info, clip, store):
    """El auricular sigue a la mano mientras esta agarrado (se hornea con el temblor incluido)."""
    grab, release = clip["handset"]
    pb = rig.pose.bones["hand.R"]
    handset.animation_data_create()
    handset.animation_data.action = None
    handset.rotation_mode = "QUATERNION"
    f_grab = 1 + int(round(grab * FPS)) if grab is not None else None
    f_rel = 1 + int(round(release * FPS)) if release is not None else None
    for f in range(1, info["frames"] + 1):
        scene.frame_set(f)
        hand_w = rig.matrix_world @ pb.matrix
        if f_grab is not None and f == f_grab:
            store["offset"] = hand_w.inverted() @ HS["rest"]
        held = (f_grab is not None and f >= f_grab) or (f_rel is not None and f <= f_rel)
        m = hand_w @ store["offset"] if held else HS["rest"]
        loc, rot, _s = m.decompose()
        handset.location, handset.rotation_quaternion = loc, rot
        handset.keyframe_insert("location", frame=f)
        handset.keyframe_insert("rotation_quaternion", frame=f)
    act = handset.animation_data.action
    act.use_fake_user = True
    return act


# ---------------------------------------------------------------------------
# Escena: el 4B + Elias
# ---------------------------------------------------------------------------
def setup_scene():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(SCENE_DIR, "departamento_4b.blend"))
    global scene
    scene = bpy.context.scene

    with bpy.data.libraries.load(os.path.join(SCENE_DIR, "brazos_primera_persona.blend"), link=False) as (src, dst):
        dst.objects = ["Brazos_Rig", "Brazos"]
    rig, arms = dst.objects
    col_e = bpy.data.collections.new("Elias")
    scene.collection.children.link(col_e)
    for ob in (rig, arms):
        col_e.objects.link(ob)

    head = bpy.data.objects.new("Elias_Cabeza", None)
    head.empty_display_size = 0.1
    col_e.objects.link(head)
    rig.parent = head
    rig.matrix_parent_inverse = Matrix()
    rig.location, rig.rotation_euler = (0, 0, 0), (0, 0, 0)
    if rig.animation_data and rig.animation_data.action:
        rig.animation_data.action.use_fake_user = True  # la pose "mirar_brazos" se conserva
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"

    cd = bpy.data.cameras.new("Cam_Elias")
    cd.lens = 24.0
    cd.clip_start, cd.clip_end = 0.02, 40.0
    cam = bpy.data.objects.new("Cam_Elias", cd)
    col_e.objects.link(cam)
    cam.parent = head
    cam.rotation_euler = (R(90), 0, 0)   # mira hacia el +Y de la cabeza
    scene.camera = cam

    # Luz tenue pegada a la camara para que los brazos se lean en lo oscuro
    # (en Unity se hace igual: una luz solo para los brazos)
    ld = bpy.data.lights.new("luz_brazos", "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = 2.5, (1.0, 0.86, 0.72), 0.15
    ld.use_shadow = False
    lamp = bpy.data.objects.new("luz_brazos", ld)
    col_e.objects.link(lamp)
    lamp.parent = head
    lamp.location = (0.05, 0.12, 0.15)

    # El auricular: origen en su centro, para poder moverlo con la mano
    hs = bpy.data.objects["telefono_auricular"]
    co = [hs.matrix_world @ v.co for v in hs.data.vertices]
    c = Vector([(min(p[i] for p in co) + max(p[i] for p in co)) / 2 for i in range(3)])
    hs.data.transform(Matrix.Translation(-(hs.matrix_world.inverted() @ c)))
    hs.location = c
    hs.rotation_mode = "QUATERNION"
    bpy.context.view_layer.update()
    HS["center"], HS["rest"] = c, hs.matrix_world.copy()

    door = bpy.data.objects["puerta_dormitorio"]
    r = scene.render
    r.fps = FPS
    r.resolution_x, r.resolution_y, r.resolution_percentage = RES_X, RES_Y, 100
    ee = scene.eevee
    for attr, val in (("taa_render_samples", 8), ("volumetric_samples", 32)):
        if hasattr(ee, attr):
            setattr(ee, attr, val)
    return rig, head, door, hs


# ---------------------------------------------------------------------------
# Post-proceso PS1 y videos
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


def key_frames(n):
    return sorted({max(1, min(n, int(round(1 + (n - 1) * u)))) for u in (0.12, 0.28, 0.44, 0.6, 0.76, 0.92)})


def render_preview(name, n, ffmpeg):
    tmp = os.path.join(RENDER_DIR, "_cuadros_" + name)
    os.makedirs(tmp, exist_ok=True)
    raw = os.path.join(RENDER_DIR, "_tmp_raw.png")
    keys = key_frames(n)
    frames = keys if KEYS_ONLY else range(1, n + 1)
    shots = {}
    t0 = time.time()
    for f in frames:
        scene.frame_set(f)
        scene.render.filepath = raw
        bpy.ops.render.render(write_still=True)
        q = ps1_quantize(raw)
        if f in keys:
            shots[f] = q
        if not KEYS_ONLY:
            save_png(q, os.path.join(tmp, f"f_{f:04d}.png"), 1)
    os.remove(raw)
    print(f"[render] {name}: {len(frames)} cuadros en {time.time() - t0:.0f} s")

    # Hoja de seis cuadros (2 columnas x 3 filas)
    rows = []
    ks = list(keys)
    for i in range(0, 6, 2):
        a, b = shots[ks[i]], shots[ks[i + 1]]
        row = np.concatenate([a, b], axis=1)
        row[:, RES_X - 1:RES_X + 1] = 0.0
        rows.append(row)
    sheet = np.concatenate(rows[::-1], axis=0)
    for i in (1, 2):
        sheet[i * RES_Y - 1:i * RES_Y + 1, :] = 0.0
    save_png(sheet, os.path.join(RENDER_DIR, f"anim_{name}_claves.png"), 2)

    video = None
    if not KEYS_ONLY and ffmpeg:
        video = os.path.join(RENDER_DIR, f"anim_{name}.mp4")
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(tmp, "f_%04d.png"),
                        "-vf", "scale=1920:1080:flags=neighbor", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "16", video], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return video


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    rig, head, door, handset = setup_scene()

    infos, clips = {}, {}
    for name, fn in CLIPS.items():
        clips[name] = fn()
        infos[name] = bake_clip(rig, head, door, name, clips[name])
    tremor = bake_tremor(rig)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("[aviso] no se encontro ffmpeg: solo se guardan las hojas de cuadros")
    videos = []
    store = {}
    for name in PREVIEW:
        info, clip = infos[name], clips[name]
        preview_setup(rig, head, door, handset, info, tremor, clip)
        if clip.get("handset"):
            bake_handset(rig, handset, info, clip, store).name = "auricular_" + name
        if ONLY and name not in ONLY:
            continue
        v = render_preview(name, info["frames"], ffmpeg)
        if v:
            videos.append(v)

    if len(videos) > 1 and ffmpeg and not ONLY:
        lst = os.path.join(RENDER_DIR, "_lista.txt")
        with open(lst, "w", encoding="utf-8") as fh:
            for v in videos:
                fh.write("file '" + v.replace("\\", "/") + "'\n")
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", os.path.join(RENDER_DIR, "anim_todas.mp4")], check=True)
        os.remove(lst)

    # Deja la escena lista para darle play: mirar_manos con el temblor
    preview_setup(rig, head, door, handset, infos["mirar_manos"], tremor, clips["mirar_manos"])
    scene.frame_set(1)
    out = os.path.join(SCENE_DIR, "brazos_animaciones.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception as e:
        print(f"[aviso] rutas relativas: {e}")

    exportar_a_unity(rig, head, door, handset, infos, clips)
    print(f"[info] listo en {time.time() - t0:.0f} s")


# ---------------------------------------------------------------------------
# Unity
# ---------------------------------------------------------------------------
def muestrear(ob, accion, n):
    """Matriz del objeto en cada cuadro de la accion (12 numeros por cuadro)."""
    ob.animation_data_create()
    ob.animation_data.action = accion
    datos = []
    for f in range(1, n + 1):
        scene.frame_set(f)
        datos += exportar_unity.matriz(ob)
    ob.animation_data.action = None
    return datos


def cargar_imagen(nombre):
    ruta = os.path.normcase(os.path.join(ROOT, "textures", nombre + ".png"))
    for img in bpy.data.images:
        if img.filepath and os.path.normcase(os.path.abspath(bpy.path.abspath(img.filepath))) == ruta:
            return img
    return bpy.data.images.load(ruta)


def exportar_a_unity(rig, head, door, handset, infos, clips):
    """Un solo FBX con el esqueleto, la malla y los clips. En Unity los brazos cuelgan de la
    camara, asi que se exportan con la cabeza en el origen. El movimiento de la cabeza (la
    camara de Unity), de la puerta y del auricular en cada clip va en el JSON, cuadro a cuadro:
    lo usa la camara de interaccion."""
    arms = bpy.data.objects["Brazos"]
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks):
        rig.animation_data.nla_tracks.remove(tr)
    reset_pose(rig)

    # Puerta y auricular en reposo: las pistas se aplican como cambio desde aqui
    for ob in (door, handset):
        if ob.animation_data:
            ob.animation_data.action = None
    door.rotation_euler.z = R(DOOR_REST)
    handset.matrix_world = HS["rest"]
    bpy.context.view_layer.update()
    reposo = {door.name: exportar_unity.matriz(door), handset.name: exportar_unity.matriz(handset)}

    pistas = []
    for name, info in infos.items():
        n = info["frames"]
        pistas.append({"clip": name, "objeto": head.name, "reposo": [], "matrices": muestrear(head, info["head"], n)})
        moviles = [(door, info["door"]), (handset, bpy.data.actions.get("auricular_" + name))]
        for ob, accion in moviles:
            if accion is not None:
                pistas.append({"clip": name, "objeto": ob.name, "reposo": reposo[ob.name],
                               "matrices": muestrear(ob, accion, n)})
    door.rotation_euler.z = R(DOOR_REST)
    handset.matrix_world = HS["rest"]

    # La cabeza en el origen: la luz y la camara quedan relativas a ella
    head.animation_data.action = None
    head.matrix_world = Matrix()
    rig.parent = None
    rig.matrix_world = Matrix()
    bpy.context.view_layer.update()

    # Los cuatro estados de los brazos (los define brazos_primera_persona.py)
    lamp, cam = bpy.data.objects["luz_brazos"], bpy.data.objects["Cam_Elias"]
    tex = arms.active_material.node_tree.nodes["Textura"]
    forma = arms.data.shape_keys.key_blocks["consumido"]
    cfg = arms["estados"].to_dict()
    estados = {}
    for st in sorted(cfg):
        tex.image = cargar_imagen(cfg[st]["textura"])
        forma.value = cfg[st]["consumido"]
        estados["estado" + st] = exportar_unity.foto_estado([lamp, cam, arms])
    tex.image = cargar_imagen(cfg["1"]["textura"])  # el FBX queda en el estado 1 (Noche 1)
    forma.value = 0.0

    anims = [{"nombre": n, "loop": bool(clips[n].get("loop"))} for n in CLIPS]
    anims += [{"nombre": "temblor", "loop": True, "aditivo": True}, {"nombre": "mirar_brazos"}]
    exportar_unity.exportar(ROOT, "BrazosElias", "brazos_elias", objetos=[rig, arms],
                            animaciones=anims, estados=estados, extra={"pistas": pistas})


main()
