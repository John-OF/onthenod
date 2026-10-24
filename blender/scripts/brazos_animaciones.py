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
  abrir_puerta        2.8 s: agarra la perilla, la gira y empuja la puerta (una puerta cerrada)
  empujar_puerta      2.6 s: la puerta del dormitorio, entreabierta: apoya la mano en la perilla y
                      la empuja
  telefono_contestar  2.4 s: levanta el auricular y se lo lleva al oido
  telefono_colgar     1.8 s: devuelve el auricular y baja la mano
  tomar_jeringa       3.4 s: se agacha frente a la mesa de centro, toma la jeringa y la
                      levanta frente a la cara (para una dosis sobre una mesa)
  sacar_dosis         4.0 s: se arrodilla junto al colchon, apoya la izquierda, saca de abajo
                      la media con la jeringa y la levanta frente a la cara (la dosis de la
                      Noche 1; en Unity sigue un corte a negro)
  tomar_agua          8.6 s: en el fregadero de la cocina, toma con la izquierda la taza sucia,
                      la pone bajo la llave, abre el agua con la derecha (la manija en cruz), la
                      cierra, bebe y deja la taza donde estaba (Noche 1, el tutorial)
  tomar_cuaderno      3.6 s: se agacha frente a la mesa de centro, toma el cuaderno por el borde
                      y lo levanta frente a la cara (en Unity sigue un corte a negro: escribe y
                      se guarda la partida)
  recoger_mesa        3.0 s: se agacha, recoge algo chico de la mesa de centro y lo guarda (la
                      mano baja fuera de cuadro). Hecho con la jeringa de la mesa; en Unity sirve
                      para cualquier rastro sobre la mesa (Noche 1: limpiar)
  recoger_piso        3.4 s: igual, de rodillas, del piso. Hecho con la jeringa del piso de la sala

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
                                                         y los catorce clips (con mirar_brazos)
  unity/Assets/Art/BrazosElias/brazos_elias_escena.json  luz de los brazos, camara, los cuatro
                                                         estados, los clips y, por clip, el
                                                         movimiento de la cabeza, la puerta,
                                                         el auricular, la jeringa, la dosis,
                                                         la taza, la manija de la llave y el
                                                         cuaderno
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
GRIP_SMALL = curls((38, 45, 30), (60, 70, 45), (68, 75, 45), (72, 72, 45), (20, 18, 15))  # pinza: algo chico
GRIP_CUP = curls((40, 50, 30), (45, 55, 35), (48, 55, 35), (50, 50, 30), (20, 20, 15))     # rodea una taza
GRIP_EDGE = curls((20, 30, 20), (25, 35, 20), (30, 40, 25), (35, 40, 25), (35, 25, 15))    # el borde del cuaderno

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


def pose_hang_holding(side, cur):
    """Brazo colgando, fuera de cuadro, con algo en la mano (lo guarda en el bolsillo)."""
    base = pose_hang(side)

    def f(ctx):
        pose = base(ctx)
        pose["curls"] = cur
        return pose
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
    if v.length - (LU + LF) > REACH["max"]:
        REACH["max"], REACH["lado"] = v.length - (LU + LF), side
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
# Lo que la mano toma en un clip (la jeringa de la mesa de centro, la dosis bajo el colchon, la
# taza del fregadero, el cuaderno): el punto por donde lo agarra y su matriz en reposo.
AGARRABLES = {}
# La llave del fregadero: la manija en cruz (gira para abrir) y el chorro (ver departamento_4b.py)
MANIJA, CHORRO = "llave_agua_manija", "chorro_agua"
PICO = Vector((7.012, 0.92, 1.075))         # por donde sale el agua


def knob_at(angle):
    rz = Matrix.Rotation(R(angle), 3, "Z")
    return HINGE + rz @ KNOB_REL, rz @ Vector((1, 0, 0)), rz


def superficie(x, y):
    """Altura de lo que hay en (x, y) bajo un metro (el colchon, la manta...)."""
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, *_ = scene.ray_cast(dg, Vector((x, y, 1.0)), Vector((0, 0, -1)))
    return loc.z if hit else 0.0


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


def push_angle(t):
    """La puerta del dormitorio entreabierta (DOOR_REST): la mano la empuja hasta -50 y despues
    sigue abriendose sola."""
    if t < 0.80:
        return DOOR_REST
    if t < 1.30:
        return DOOR_REST + (-50.0 - DOOR_REST) * smooth((t - 0.80) / 0.5)
    return -50.0 - 40.0 * ease_out((t - 1.30) / 1.0)


def clip_empujar_puerta():
    """La puerta del dormitorio, que en el 4B quedo entreabierta: Elias apoya la mano en la
    perilla y la empuja (no hace falta girarla). abrir_puerta queda para las puertas cerradas."""
    def grip(back=0.0, cur=GRIP_KNOB, frozen=None):
        def g_fn(t):
            k, axis, _ = knob_at(push_angle(frozen if frozen is not None else t))
            return k + axis * back

        def r_fn(t):
            _, axis, rz = knob_at(push_angle(frozen if frozen is not None else t))
            return hand_rot(-axis + Vector((0, 0, -0.2)), rz @ Vector((0, -1, 0)), 1)
        return pose_world(g_fn, r_fn, (0.45, -0.1, -1.0), cur)

    right = [
        (0.0, pose_hang(1)),
        (0.55, grip(back=0.09, cur=OPEN)),
        (0.75, grip()),                                        # la mano en la perilla
        (1.30, grip()),                                        # empuja: la mano sigue a la perilla
        (1.50, grip(back=0.07, cur=OPEN, frozen=1.30)),        # suelta
        (2.10, pose_hang(1)),
        (2.60, pose_hang(1)),
    ]
    # La perilla de la puerta entreabierta queda 33 cm mas adentro que la de la puerta cerrada:
    # Elias se acerca mas al marco que en abrir_puerta
    head = [(0.0, (4.10, 4.66, 1.58), 90.0, -20.0), (0.55, (3.59, 4.66, 1.52), 90.0, -40.0),
            (0.80, (3.59, 4.66, 1.52), 90.0, -40.0), (1.30, (3.48, 4.67, 1.53), 90.0, -30.0),
            (2.60, (3.55, 4.68, 1.56), 92.0, -10.0)]
    lean = [(0.0, (0, 0, 0)), (0.5, (0, 0.18, -0.03)), (1.4, (0, 0.18, -0.03)), (2.1, (0, 0, 0))]
    return dict(dur=2.6, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]}, door=push_angle)


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


def clip_tomar_jeringa():
    """Una dosis sobre una mesa (6.3): se agacha frente a la mesa de centro, toma la jeringa con
    la derecha y la levanta frente a la cara. En Unity seguiria un corte a negro y el efecto.
    La jeringa de la mesa ya no es la dosis de la Noche 1 (ver sacar_dosis): el clip queda para
    las dosis que esten sobre una mesa."""
    c = AGARRABLES["jeringa_mesa"]["agarre"]

    def on_table(up=0.0, cur=OPEN):
        rot = hand_rot((0.15, 0.75, -0.65), (0, 0, -1), 1)  # dedos hacia la mesa, palma abajo
        return pose_world(lambda t: c + Vector((0, 0, up)), lambda t: rot.copy(), (0.6, -0.3, -1.0), cur)

    def in_view(dx=0.0):
        rot = hand_rot((-0.35, 0.85, 0.25), (-0.5, -0.2, 0.85), 1)  # palma arriba: se ve la jeringa
        return pose_rig((0.03 + dx, 0.30, -0.07), rot, (0.6, -0.4, -1.0), GRIP_SMALL)

    right = [
        (0.0, pose_hang(1)),
        (0.85, on_table(up=0.07)),
        (1.05, on_table(up=0.012)),
        (1.30, on_table(up=0.012, cur=GRIP_SMALL)),   # la agarra
        (1.45, on_table(up=0.03, cur=GRIP_SMALL)),
        (2.35, in_view()),
        (3.40, in_view(dx=-0.01)),
    ]
    # Agachado e inclinado sobre el borde de la mesa: al mirar hacia abajo los hombros se van
    # hacia atras, asi que la cabeza se acerca a la mesa para que la mano llegue.
    head = [(0.0, (1.86, 1.98, 1.58), 0.0, -32.0), (0.80, (1.84, 2.18, 1.00), -2.0, -62.0),
            (1.45, (1.84, 2.22, 0.98), -2.0, -60.0), (2.35, (1.84, 2.12, 1.06), 2.0, -24.0),
            (3.40, (1.84, 2.12, 1.07), 3.0, -22.0)]
    lean = [(0.0, (0, 0, 0)), (0.8, (0, 0.18, -0.04)), (1.45, (0, 0.18, -0.04)), (2.35, (0, 0.03, 0))]
    return dict(dur=3.4, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]},
                objeto=dict(nombre="jeringa_mesa", agarre=1.30))


def clip_sacar_dosis():
    """La dosis de la Noche 1 (secciones 5 y 6.3): se arrodilla junto al colchon del dormitorio,
    apoya la izquierda en el borde, saca de abajo la media con la jeringa (la punta de la media
    asoma por el costado) y la levanta frente a la cara: por la boca de la media sale la jeringa.
    En Unity sigue un corte a negro y despues, el efecto."""
    g = AGARRABLES["dosis_colchon"]["agarre"]
    apoyo = Vector((1.645, 6.40, 0.0))
    apoyo.z = superficie(apoyo.x, apoyo.y) + 0.005

    def at_sock(dx=0.0, up=0.0, cur=OPEN):
        # Pellizca la punta de la media: los dedos hacia el colchon (a lo largo de la media) y
        # hacia abajo, la palma abajo. Asi, en la mano, la jeringa queda del lado de los dedos.
        rot = hand_rot((-0.80, 0.05, -0.60), (0, 0, -1), 1)
        return pose_world(lambda t: g + Vector((dx, 0, up)), lambda t: rot.copy(), (0.6, -0.3, -1.0), cur)

    def on_mattress(up=0.0):
        rot = hand_rot((-0.95, -0.2, -0.12), (0, 0, -1), -1)  # la palma sobre el borde del colchon
        return pose_world(lambda t: apoyo + Vector((0, 0, up)), lambda t: rot.copy(), (-0.6, -0.3, -1.0), OPEN)

    def in_view(dx=0.0):
        # Los dedos hacia arriba y la palma hacia la cara: la media queda parada en la mano,
        # vista de costado, con la jeringa arriba
        rot = hand_rot((-0.25, -0.15, 1.0), (-0.3, -1.0, 0.1), 1)
        return pose_rig((0.05 + dx, 0.32, -0.11), rot, (0.6, -0.4, -1.0), GRIP_SMALL)

    right = [
        (0.0, pose_hang(1)),
        (0.95, at_sock(dx=0.04, up=0.07)),
        (1.20, at_sock(up=0.01)),
        (1.40, at_sock(up=0.01, cur=GRIP_SMALL)),            # la agarra
        (2.00, at_sock(dx=0.20, up=0.03, cur=GRIP_SMALL)),   # la saca de abajo del colchon
        (2.90, in_view()),
        (4.00, in_view(dx=-0.01)),
    ]
    left = [
        (0.0, pose_hang(-1)),
        (0.80, on_mattress(up=0.06)),
        (1.00, on_mattress()),                               # se apoya
        (1.50, on_mattress()),
        (1.70, on_mattress(up=0.05)),                        # la suelta cuando la otra tira
        (2.55, pose_hang(-1)),
        (4.00, pose_hang(-1)),
    ]
    # De rodillas e inclinado sobre el borde del colchon, que esta en el piso: la cabeza baja
    # hasta 62 cm para que la mano llegue abajo del colchon. Despues se endereza, de rodillas.
    head = [(0.0, (2.32, 6.54, 1.58), 90.0, -36.0), (0.80, (2.07, 6.54, 0.64), 88.0, -58.0),
            (1.40, (2.06, 6.54, 0.62), 88.0, -58.0), (2.00, (2.15, 6.54, 0.66), 89.0, -60.0),
            (2.90, (2.15, 6.54, 0.92), 92.0, -24.0), (4.00, (2.15, 6.54, 0.93), 93.0, -22.0)]
    lean = [(0.0, (0, 0, 0)), (0.8, (0, 0.18, -0.04)), (2.0, (0, 0.18, -0.04)), (2.9, (0, 0.03, 0))]
    return dict(dur=4.0, head=head, lean=lean, arms={1: right, -1: left},
                objeto=dict(nombre="dosis_colchon", agarre=1.40))


def manija_angulo(t):
    """La manija de la llave: un cuarto de vuelta (70 grados) para abrir y de vuelta para cerrar."""
    if t < 2.15:
        return 0.0
    if t < 3.95:
        return 70.0 * smooth((t - 2.15) / 0.4)
    return 70.0 * (1.0 - smooth((t - 3.95) / 0.4))


AGUA = (2.45, 4.20)  # cuando corre el agua en tomar_agua (segundos)


def clip_tomar_agua():
    """El agua de la Noche 1 (el tutorial, seccion 5): parado frente al fregadero de la cocina,
    toma con la izquierda la taza sucia que esta en el fregadero, la pone bajo el pico de la llave,
    abre el agua con la derecha (la manija en cruz, un cuarto de vuelta), la cierra cuando la taza
    se llena, se endereza y bebe echando la cabeza atras. Despues deja la taza donde estaba."""
    taza = AGARRABLES["taza_1"]["agarre"]          # el centro de la taza en el fregadero
    bajo_pico = Vector((PICO.x, PICO.y, 0.975))    # la taza bajo el chorro
    manija = bpy.data.objects[MANIJA].matrix_world.translation + Vector((0, 0, 0.02))

    # La izquierda rodea la taza por su lado izquierdo: la palma hacia la taza (hacia la derecha
    # de Elias, que mira hacia +X), los dedos hacia adelante y el pulgar arriba.
    rot_taza = hand_rot((1.0, -0.15, 0.0), (0.0, -1.0, 0.0), -1)

    def cup(centro, up=0.0, cur=GRIP_CUP):
        g = centro + Vector((0.0, 0.025, 0.005 + up))
        return pose_world(lambda t: g, lambda t: rot_taza.copy(), (-0.6, -0.3, -1.0), cur)

    def at_mouth(tilt, centro):
        # Frente a la cara (un poco adelantada, para que se vea), inclinada hacia la boca
        rx = Matrix.Rotation(R(tilt), 3, "X")
        rot = rx @ hand_rot((0.0, 1.0, 0.0), (1.0, 0.0, 0.0), -1)
        return pose_rig(Vector(centro) + rx @ Vector((-0.025, 0.0, 0.005)), rot, (-0.6, -0.4, -1.0), GRIP_CUP)

    # La derecha agarra la manija desde arriba, la palma abajo, y la gira con ella
    def handle(up=0.0, cur=GRIP_KNOB):
        base = hand_rot((math.cos(R(-40)), math.sin(R(-40)), -0.35), (0, 0, -1), 1)

        def r_fn(t):
            return Matrix.Rotation(R(manija_angulo(t)), 3, "Z") @ base
        return pose_world(lambda t: manija + Vector((0, 0, up)), r_fn, (0.6, -0.2, -1.0), cur)

    left = [
        (0.0, pose_hang(-1)),
        (0.85, cup(taza, up=0.06, cur=OPEN)),
        (1.05, cup(taza, cur=OPEN)),
        (1.25, cup(taza)),                          # la agarra
        (1.45, cup(taza, up=0.06)),
        (2.05, cup(bajo_pico)),                     # bajo el chorro
        (4.40, cup(bajo_pico)),
        (4.65, cup(bajo_pico + Vector((-0.12, 0.02, 0.0)))),   # la saca de abajo del pico
        (5.15, at_mouth(10.0, (0.0, 0.25, -0.08))),            # la mira: llena
        (5.60, at_mouth(50.0, (0.0, 0.16, -0.075))),
        (6.25, at_mouth(85.0, (0.0, 0.14, -0.065))),           # bebe
        (6.60, at_mouth(30.0, (0.0, 0.18, -0.11))),
        (7.30, cup(taza, up=0.04)),
        (7.45, cup(taza)),                          # la deja
        (7.60, cup(taza, cur=OPEN)),
        (7.80, cup(taza, up=0.05, cur=OPEN)),
        (8.60, pose_hang(-1)),
    ]
    right = [
        (0.0, pose_hang(1)),
        (1.45, pose_hang(1)),
        (1.95, handle(up=0.07, cur=OPEN)),
        (2.08, handle(cur=OPEN)),
        (2.15, handle()),                           # agarra la manija y abre (manija_angulo)
        (4.35, handle()),                           # ya la cerro
        (4.45, handle(up=0.05, cur=OPEN)),
        (5.10, pose_hang(1)),
        (8.60, pose_hang(1)),
    ]
    # Inclinado sobre el fregadero (la llave queda al fondo: para alcanzarla se inclina mas); se
    # endereza para beber y se vuelve a inclinar para dejar la taza
    head = [(0.0, (6.25, 0.98, 1.58), -90.0, -30.0), (0.80, (6.45, 1.00, 1.38), -80.0, -58.0),
            (1.30, (6.45, 1.00, 1.38), -80.0, -56.0), (2.00, (6.60, 0.98, 1.32), -92.0, -34.0),
            (4.45, (6.60, 0.98, 1.32), -92.0, -33.0), (5.20, (6.30, 0.98, 1.56), -90.0, -4.0),
            (6.25, (6.29, 0.98, 1.57), -90.0, 18.0), (6.70, (6.30, 0.98, 1.56), -88.0, -10.0),
            (7.40, (6.43, 1.00, 1.40), -80.0, -55.0), (7.80, (6.43, 1.00, 1.40), -80.0, -52.0),
            (8.60, (6.27, 0.98, 1.57), -88.0, -25.0)]
    lean = [(0.0, (0, 0, 0)), (0.8, (0, 0.16, -0.04)), (1.3, (0, 0.16, -0.04)), (2.0, (0, 0.20, -0.04)),
            (4.45, (0, 0.20, -0.04)), (5.2, (0, 0.02, 0)), (6.7, (0, 0.02, 0)), (7.4, (0, 0.16, -0.04)),
            (7.8, (0, 0.16, -0.04)), (8.6, (0, 0, 0))]
    return dict(dur=8.6, head=head, lean=lean, arms={1: right, -1: left},
                objeto=dict(nombre="taza_1", agarre=1.25, mano="hand.L", suelta=7.45),
                manija=manija_angulo, agua=AGUA)


def clip_tomar_cuaderno():
    """El cuaderno (6.8): se agacha frente a la mesa de centro, toma el cuaderno por el borde de
    adelante y lo levanta frente a la cara, con la tapa hacia el. En Unity sigue un corte a negro:
    Elias escribe y se guarda la partida."""
    c = AGARRABLES["cuaderno"]["agarre"]
    yaw = bpy.data.objects["cuaderno"].matrix_world.to_euler().z

    def on_table(up=0.0, cur=OPEN):
        # La mano sobre el borde, la palma abajo y los dedos hacia el otro lado del cuaderno
        rot = hand_rot((-math.sin(yaw) * 0.8, math.cos(yaw) * 0.8, -0.55), (0, 0, -1), 1)
        return pose_world(lambda t: c + Vector((0, 0, up)), lambda t: rot.copy(), (0.6, -0.3, -1.0), cur)

    def in_view(dx=0.0):
        # Los dedos hacia arriba y el dorso hacia la cara: el cuaderno queda parado frente a
        # los ojos, con la tapa hacia Elias, un poco echado hacia atras
        rot = hand_rot((-0.15, 0.6, 1.0), (0.1, 1.0, -0.6), 1)
        return pose_rig((0.05 + dx, 0.42, -0.15), rot, (0.6, -0.4, -1.0), GRIP_EDGE)

    right = [
        (0.0, pose_hang(1)),
        (0.85, on_table(up=0.07)),
        (1.05, on_table(up=0.01)),
        (1.30, on_table(up=0.01, cur=GRIP_EDGE)),   # lo agarra
        (1.45, on_table(up=0.04, cur=GRIP_EDGE)),
        (2.40, in_view()),
        (3.60, in_view(dx=-0.01)),
    ]
    head = [(0.0, (1.19, 1.98, 1.58), 0.0, -34.0), (0.80, (1.19, 2.20, 0.99), -2.0, -62.0),
            (1.45, (1.19, 2.24, 0.97), -2.0, -60.0), (2.40, (1.19, 2.12, 1.08), 1.0, -16.0),
            (3.60, (1.19, 2.12, 1.09), 2.0, -14.0)]
    lean = [(0.0, (0, 0, 0)), (0.8, (0, 0.18, -0.04)), (1.45, (0, 0.18, -0.04)), (2.4, (0, 0.03, 0))]
    return dict(dur=3.6, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]},
                objeto=dict(nombre="cuaderno", agarre=1.30))


def clip_recoger_mesa():
    """Limpiar los rastros del consumo (Noche 1, el tutorial): se agacha frente a la mesa de
    centro, recoge algo chico con la derecha y lo guarda (la mano baja fuera de cuadro). Se hizo
    con la jeringa de la mesa, tomada por su origen; en Unity se lleva a cualquier rastro de la
    mesa (la cuchara, el cenicero, el cinturon...), girado hacia el lado desde donde viene Elias."""
    c = AGARRABLES["jeringa_mesa"]["reposo"].translation + Vector((0, 0, 0.004))

    def on_table(up=0.0, cur=OPEN):
        rot = hand_rot((0.15, 0.75, -0.65), (0, 0, -1), 1)  # dedos hacia la mesa, palma abajo
        return pose_world(lambda t: c + Vector((0, 0, up)), lambda t: rot.copy(), (0.6, -0.3, -1.0), cur)

    right = [
        (0.0, pose_hang(1)),
        (0.80, on_table(up=0.07)),
        (1.00, on_table(up=0.012)),
        (1.20, on_table(up=0.012, cur=GRIP_SMALL)),   # lo agarra
        (1.40, on_table(up=0.05, cur=GRIP_SMALL)),
        (2.20, pose_hang_holding(1, GRIP_SMALL)),     # al bolsillo
        (3.00, pose_hang(1)),
    ]
    head = [(0.0, (1.86, 1.98, 1.58), 0.0, -32.0), (0.80, (1.84, 2.18, 1.00), -2.0, -62.0),
            (1.40, (1.84, 2.20, 0.99), -2.0, -60.0), (2.20, (1.85, 2.06, 1.40), 0.0, -35.0),
            (3.00, (1.86, 1.98, 1.58), 0.0, -28.0)]
    lean = [(0.0, (0, 0, 0)), (0.8, (0, 0.18, -0.04)), (1.4, (0, 0.18, -0.04)), (2.2, (0, 0.03, 0)), (3.0, (0, 0, 0))]
    return dict(dur=3.0, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]},
                objeto=dict(nombre="jeringa_mesa", agarre=1.20))


def clip_recoger_piso():
    """Como recoger_mesa, pero del piso: se arrodilla, recoge algo chico y lo guarda. Se hizo con
    la jeringa del piso de la sala; en Unity se lleva a cualquier rastro del piso (la jeringa
    junto al colchon)."""
    c = AGARRABLES["jeringa_piso"]["reposo"].translation + Vector((0, 0, 0.004))

    def on_floor(up=0.0, cur=OPEN):
        rot = hand_rot((0.1, 0.6, -0.8), (0, 0, -1), 1)
        return pose_world(lambda t: c + Vector((0, 0, up)), lambda t: rot.copy(), (0.6, -0.3, -1.0), cur)

    right = [
        (0.0, pose_hang(1)),
        (0.95, on_floor(up=0.07)),
        (1.15, on_floor(up=0.01)),
        (1.35, on_floor(up=0.01, cur=GRIP_SMALL)),    # lo agarra
        (1.55, on_floor(up=0.05, cur=GRIP_SMALL)),
        (2.40, pose_hang_holding(1, GRIP_SMALL)),     # al bolsillo
        (3.40, pose_hang(1)),
    ]
    # De rodillas: la cabeza baja hasta 66 cm, como al sacar la dosis de abajo del colchon
    head = [(0.0, (2.35, 2.02, 1.58), 0.0, -42.0), (0.90, (2.35, 2.30, 0.66), -2.0, -62.0),
            (1.55, (2.35, 2.31, 0.66), -2.0, -60.0), (2.40, (2.35, 2.16, 1.05), 0.0, -35.0),
            (3.40, (2.35, 2.02, 1.57), 0.0, -28.0)]
    lean = [(0.0, (0, 0, 0)), (0.9, (0, 0.18, -0.04)), (1.55, (0, 0.18, -0.04)), (2.4, (0, 0.03, 0)), (3.4, (0, 0, 0))]
    return dict(dur=3.4, head=head, lean=lean, arms={1: right, -1: [(0.0, pose_hang(-1))]},
                objeto=dict(nombre="jeringa_piso", agarre=1.35))


CLIPS = {
    "reposo": clip_reposo,
    "mirar_manos": clip_mirar_manos,
    "abrir_puerta": clip_abrir_puerta,
    "empujar_puerta": clip_empujar_puerta,
    "telefono_contestar": clip_telefono_contestar,
    "telefono_colgar": clip_telefono_colgar,
    "tomar_jeringa": clip_tomar_jeringa,
    "sacar_dosis": clip_sacar_dosis,
    "tomar_agua": clip_tomar_agua,
    "tomar_cuaderno": clip_tomar_cuaderno,
    "recoger_mesa": clip_recoger_mesa,
    "recoger_piso": clip_recoger_piso,
}
PREVIEW = ["mirar_manos", "abrir_puerta", "empujar_puerta", "telefono_contestar", "telefono_colgar", "tomar_jeringa", "sacar_dosis",
           "tomar_agua", "tomar_cuaderno", "recoger_mesa", "recoger_piso"]


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

    # La manija de la llave gira; el chorro se ve mientras corre el agua
    manija_act = chorro_act = None
    if clip.get("manija"):
        manija = bpy.data.objects[MANIJA]
        manija.animation_data_create()
        manija.animation_data.action = None
        for f in range(1, n + 1):
            manija.rotation_euler.z = R(clip["manija"]((f - 1) / FPS))
            manija.keyframe_insert("rotation_euler", index=2, frame=f)
        manija_act = manija.animation_data.action
        manija_act.name = "manija_" + name
        manija_act.use_fake_user = True
        manija.animation_data.action = None
        manija.rotation_euler.z = 0.0
    if clip.get("agua"):
        chorro = bpy.data.objects[CHORRO]
        chorro.animation_data_create()
        chorro.animation_data.action = None
        desde, hasta = clip["agua"]
        for f in range(1, n + 1):
            chorro.hide_render = not desde <= (f - 1) / FPS < hasta
            chorro.keyframe_insert("hide_render", frame=f)
        chorro_act = chorro.animation_data.action
        chorro_act.name = "chorro_" + name
        chorro_act.use_fake_user = True
        chorro.animation_data.action = None
        chorro.hide_render = True
    lado = "derecho" if REACH.get("lado", 1) > 0 else "izquierdo"
    print(f"[clip] {name}: {n} cuadros; alcance sobrante {-REACH['max'] * 100:.1f} cm (brazo {lado}); "
          f"desfase del hombro {up_loc * 1000:.2f} mm")
    return dict(action=act, head=head_act, door=door_act, manija=manija_act, chorro=chorro_act, frames=n)


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
    for nombre, a in AGARRABLES.items():
        ob = bpy.data.objects[nombre]
        if ob.animation_data:
            ob.animation_data.action = None
        ob.matrix_world = a["reposo"]
    for nombre, clave in ((MANIJA, "manija"), (CHORRO, "chorro")):
        ob = bpy.data.objects[nombre]
        ob.animation_data_create()
        ob.animation_data.action = info[clave]
        if info[clave] is None:
            ob.rotation_euler.z = 0.0
            ob.hide_render = nombre == CHORRO
    scene.frame_start, scene.frame_end = 1, info["frames"]


def bake_handset(rig, handset, info, clip, store):
    """El auricular sigue a la mano mientras esta agarrado."""
    grab, release = clip["handset"]
    return bake_follow(rig, handset, HS["rest"], info, grab, release, store)


def bake_follow(rig, ob, rest, info, grab, release, store, mano="hand.R"):
    """El objeto sigue a la mano mientras esta agarrado (se hornea con el temblor incluido).
    grab o release en None: lo agarro en otro clip o no lo suelta. Con los dos, lo tiene en la
    mano entre uno y otro, y al soltarlo vuelve a su reposo (la mano lo deja donde lo tomo: la
    taza). store guarda donde lo agarro la mano, para soltarlo en otro clip (el auricular)."""
    pb = rig.pose.bones[mano]
    ob.animation_data_create()
    ob.animation_data.action = None
    ob.rotation_mode = "QUATERNION"
    f_grab = 1 + int(round(grab * FPS)) if grab is not None else None
    f_rel = 1 + int(round(release * FPS)) if release is not None else None
    for f in range(1, info["frames"] + 1):
        scene.frame_set(f)
        hand_w = rig.matrix_world @ pb.matrix
        if f_grab is not None and f == f_grab:
            store["offset"] = hand_w.inverted() @ rest
        if f_grab is not None and f_rel is not None:
            held = f_grab <= f < f_rel
        else:
            held = (f_grab is not None and f >= f_grab) or (f_rel is not None and f <= f_rel)
        m = hand_w @ store["offset"] if held else rest
        loc, rot, _s = m.decompose()
        ob.location, ob.rotation_quaternion = loc, rot
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_quaternion", frame=f)
    act = ob.animation_data.action
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

    # Lo que la mano agarra. La jeringa de la mesa de centro, por el medio del cuerpo; la dosis
    # bajo el colchon, por la parte de la media que asoma (cerca de la punta); la taza del
    # fregadero, por su centro (la mano la rodea); el cuaderno, por el borde de adelante, sobre
    # la tapa.
    body = bpy.data.objects["jeringa_mesa_cuerpo"]
    co = [body.matrix_world @ v.co for v in body.data.vertices]
    agarres = {"jeringa_mesa": Vector([(min(p[i] for p in co) + max(p[i] for p in co)) / 2 for i in range(3)]),
               "dosis_colchon": bpy.data.objects["dosis_colchon"].matrix_world @ Vector((0.0, -0.075, 0.0216)),
               "jeringa_piso": bpy.data.objects["jeringa_piso"].matrix_world.translation.copy(),
               "taza_1": bpy.data.objects["taza_1"].matrix_world @ Vector((0.0, 0.0, 0.045)),
               "cuaderno": bpy.data.objects["cuaderno"].matrix_world @ Vector((0.0, -0.12, 0.015))}
    for nombre, agarre in agarres.items():
        ob = bpy.data.objects[nombre]
        ob.rotation_mode = "QUATERNION"
        bpy.context.view_layer.update()
        AGARRABLES[nombre] = {"agarre": agarre, "reposo": ob.matrix_world.copy()}

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
        if clip.get("objeto"):
            o = clip["objeto"]
            nombre = o["nombre"]
            bake_follow(rig, bpy.data.objects[nombre], AGARRABLES[nombre]["reposo"], info, o["agarre"],
                        o.get("suelta"), {}, o.get("mano", "hand.R")).name = nombre + "_" + name
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
    camara de Unity), de la puerta, de la manija de la llave, del auricular y de lo que se agarra
    en cada clip va en el JSON, cuadro a cuadro: lo usa la camara de interaccion. La pista de lo
    que la mano agarra en el clip (la jeringa, la dosis, la taza, el cuaderno) dice ademas con
    que mano, desde cuando y, si lo suelta, hasta cuando: mientras tanto Unity lo pega a la
    mano, para que tiemble con ella. El chorro de agua no va: Unity lo muestra por su cuenta."""
    arms = bpy.data.objects["Brazos"]
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks):
        rig.animation_data.nla_tracks.remove(tr)
    reset_pose(rig)

    # Puerta, manija de la llave, auricular y lo que se agarra en reposo: las pistas se aplican
    # como cambio desde aqui
    agarrables = [bpy.data.objects[nombre] for nombre in AGARRABLES]
    manija = bpy.data.objects[MANIJA]

    def en_reposo():
        door.rotation_euler.z = R(DOOR_REST)
        manija.rotation_euler.z = 0.0
        handset.matrix_world = HS["rest"]
        for ob in agarrables:
            ob.matrix_world = AGARRABLES[ob.name]["reposo"]
        bpy.context.view_layer.update()

    for ob in [door, manija, handset] + agarrables:
        if ob.animation_data:
            ob.animation_data.action = None
    en_reposo()
    reposo = {ob.name: exportar_unity.matriz(ob) for ob in [door, manija, handset] + agarrables}

    pistas = []
    for name, info in infos.items():
        n = info["frames"]
        pistas.append({"clip": name, "objeto": head.name, "reposo": [], "matrices": muestrear(head, info["head"], n)})
        moviles = [(door, info["door"]), (manija, info["manija"]), (handset, bpy.data.actions.get("auricular_" + name))]
        moviles += [(ob, bpy.data.actions.get(ob.name + "_" + name)) for ob in agarrables]
        for ob, accion in moviles:
            if accion is not None:
                pista = {"clip": name, "objeto": ob.name, "reposo": reposo[ob.name], "matrices": muestrear(ob, accion, n)}
                o = clips[name].get("objeto")
                if o and o["nombre"] == ob.name:
                    pista["mano"], pista["agarre"] = o.get("mano", "hand.R"), o["agarre"]
                    if o.get("suelta") is not None:
                        pista["suelta"] = o["suelta"]
                pistas.append(pista)
    en_reposo()

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
