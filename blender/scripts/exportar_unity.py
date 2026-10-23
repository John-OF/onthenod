r"""
Exporta la escena de Blender a Unity: un FBX, las texturas que usa y un JSON con
lo que el FBX no guarda (luces, camaras, estados, animaciones).

No se corre solo: lo importan los scripts de assets y lo llaman al final, despues
de guardar el .blend y renderizar.

    import exportar_unity
    exportar_unity.exportar(ROOT, "PruebaEstiloPasillo", "prueba_estilo_pasillo")

Si la escena tiene estados (abstinencia, efecto...), el script los fotografia antes:

    estados = {}
    for estado in ("abstinencia", "efecto"):
        poner_estado(estado)
        estados[estado] = exportar_unity.foto_estado()
    poner_estado("abstinencia")              # lo que queda en el FBX
    exportar_unity.exportar(ROOT, "Departamento4B", "departamento_4b",
                            excluir=("Plano",), estados=estados)

Para un personaje animado se le dan los objetos y la lista de clips (ver
brazos_animaciones.py):

    exportar_unity.exportar(ROOT, "BrazosElias", "brazos_elias", objetos=[rig, malla],
                            animaciones=[{"nombre": "reposo", "loop": True}, ...])

Un personaje de cuerpo entero con esqueleto de nombres de Mixamo va con humanoide=True
(ver tomas.py): Unity lo importa como Humanoid y le sirven las animaciones de Mixamo. Lo
que lleve en alguna pose va en accesorios (el plato de Carmen, ver dona_carmen.py).

Salidas (ROOT es la carpeta blender/; el proyecto de Unity esta al lado):
  unity/Assets/Art/<carpeta>/<nombre>.fbx          mallas, empties, esqueletos y clips
  unity/Assets/Art/<carpeta>/<nombre>_escena.json  luces, camaras, estados, clips y extras
  unity/Assets/Art/<carpeta>/Textures/*.png        las texturas de blender/textures que usa
                                                   (tambien las de los otros estados)

Que cambia en el FBX respecto del .blend:
  - Cada coleccion es un objeto vacio con su nombre, padre de sus objetos: en Unity se
    muestra u oculta entera (por ejemplo, Efecto). Las de `excluir` no se exportan.
  - Los objetos que no proyectan sombra (Visibilidad > Sombra apagada) llevan la propiedad
    sin_sombra; Unity la lee al importar.
  - Los materiales de pura emision pasan a Principled (el FBX solo entiende ese).
  - Con `animaciones`: solo esas acciones, cada una como un clip; a las aditivas se les
    agrega un cuadro de reposo antes del primero, que Unity usa de referencia.
  - Con `humanoide`: el personaje se gira 180 grados. En Blender los personajes miran hacia
    -Y, que en Unity es -Z; un Humanoid tiene que mirar hacia +Z, como las animaciones de
    Mixamo. El giro va en el objeto del esqueleto (en Unity, Tomas_Rig queda girado 180
    grados en Y), no en las poses: lo que se mida relativo al esqueleto no cambia. Ademas
    se agrega la accion _pose_t (el esqueleto en reposo), para que Unity tome la pose en T
    como pose inicial del modelo y como referencia del Avatar.
Las luces y las camaras van en el JSON, no en el FBX. Las posiciones del JSON estan en
coordenadas de Blender (Z arriba); en Unity, (x, y, z) de Blender es (x, z, y).
Unity importa todo solo (Assets/Editor/ImportadorArte.cs y EscenaBlender.cs).
"""
import filecmp
import json
import math
import os
import shutil

import bpy
from mathutils import Matrix, Vector

# Tipos de objeto que van al FBX (FONT, CURVE...: como malla).
TIPOS = {"MESH", "EMPTY", "ARMATURE", "FONT", "CURVE", "SURFACE", "META"}


def _r(v, n=5):
    return [round(float(x), n) for x in v]


def _emision(mat):
    """(color, fuerza) de la emision del material, o None si no emite nada."""
    if not mat or not mat.node_tree:
        return None
    for node in mat.node_tree.nodes:
        if node.type == "EMISSION":
            return tuple(node.inputs["Color"].default_value)[:3], node.inputs["Strength"].default_value
        if node.type == "BSDF_PRINCIPLED" and node.inputs["Emission Strength"].default_value > 0:
            return (tuple(node.inputs["Emission Color"].default_value)[:3],
                    node.inputs["Emission Strength"].default_value)
    return None


def _imagenes(mat):
    """Nombres de archivo (sin extension) de las texturas del material."""
    if not mat or not mat.node_tree:
        return []
    return [os.path.splitext(os.path.basename(bpy.path.abspath(n.image.filepath)))[0]
            for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and n.image.filepath]


def _mundo():
    w = bpy.context.scene.world
    datos = {"fondo": [0.0, 0.0, 0.0], "niebla_densidad": 0.0, "niebla_color": [1.0, 1.0, 1.0]}
    if w and w.node_tree:
        for node in w.node_tree.nodes:
            if node.type == "BACKGROUND":
                fuerza = node.inputs["Strength"].default_value
                datos["fondo"] = _r(v * fuerza for v in tuple(node.inputs["Color"].default_value)[:3])
            elif node.type == "PRINCIPLED_VOLUME":
                datos["niebla_densidad"] = round(node.inputs["Density"].default_value, 5)
                datos["niebla_color"] = _r(tuple(node.inputs["Color"].default_value)[:3])
    return datos


def foto_estado(objetos=None):
    """Lo que puede cambiar de un estado a otro: que luces estan encendidas y con que color
    y potencia, la emision y la textura de cada material, el valor de cada forma (shape key),
    las colecciones y los objetos ocultos (como la Polaroid de Tomas) y el mundo (fondo y
    niebla). Se llama con la escena ya puesta en ese estado. objetos: solo esas luces, y los
    materiales, formas y objetos ocultos de esas mallas (por defecto, todo)."""
    todos = objetos if objetos is not None else list(bpy.context.scene.objects)
    luces = [{"nombre": ob.name, "encendida": not ob.hide_render,
              "color": _r(ob.data.color), "potencia": round(ob.data.energy, 5)}
             for ob in todos if ob.type == "LIGHT"]
    if objetos is None:
        mats = list(bpy.data.materials)
    else:
        mats = list({s.material for ob in todos if ob.type == "MESH" for s in ob.material_slots if s.material})
    materiales = []
    for mat in sorted(mats, key=lambda m: m.name):
        em = _emision(mat)
        tex = _imagenes(mat)
        if em is None and not tex:
            continue
        color, fuerza = em if em else ((0.0, 0.0, 0.0), 0.0)
        materiales.append({"nombre": mat.name, "emision": _r(color), "fuerza": round(fuerza, 5),
                           "textura": tex[0] if tex else ""})
    formas = [{"objeto": ob.name, "forma": kb.name, "valor": round(kb.value, 5)}
              for ob in todos if ob.type == "MESH" and ob.data.shape_keys
              for kb in ob.data.shape_keys.key_blocks[1:]]
    ocultas = [c.name for c in bpy.data.collections if c.hide_render]
    objetos_ocultos = [ob.name for ob in todos if ob.type in TIPOS and ob.hide_render]
    return {"luces": luces, "materiales": materiales, "formas": formas,
            "colecciones_ocultas": ocultas, "objetos_ocultos": objetos_ocultos, "mundo": _mundo()}


def _luces_y_camaras(objetos):
    luces, camaras = [], []
    for ob in objetos:
        mw = ob.matrix_world
        pos = mw.translation
        direccion = (mw.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()  # luces y camaras miran a su -Z
        if ob.type == "LIGHT":
            d = ob.data
            luz = {"nombre": ob.name, "tipo": d.type, "posicion": _r(pos), "direccion": _r(direccion),
                   "radio": 0.0, "tamano": [0.0, 0.0], "cono": 0.0, "suavizado": 0.0,
                   "sombras": bool(d.use_shadow),
                   # luces que solo existen para imitar algo que EEVEE no calcula: "rebote", "fuga"
                   "truco": str(ob.get("truco", "")),
                   # luces que en Unity van enteras en la luz precalculada (no mixtas)
                   "precalculada": bool(ob.get("precalculada", False))}
            if d.type in ("POINT", "SPOT"):
                luz["radio"] = round(d.shadow_soft_size, 5)
            if d.type == "SPOT":
                luz["cono"] = round(d.spot_size * 57.29578, 4)  # en grados, el angulo completo
                luz["suavizado"] = round(d.spot_blend, 4)
            if d.type == "AREA":
                luz["tamano"] = _r((d.size, d.size_y if d.shape in ("RECTANGLE", "ELLIPSE") else d.size))
            luces.append(luz)
        elif ob.type == "CAMERA":
            c = ob.data
            arriba = (mw.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
            camaras.append({"nombre": ob.name, "posicion": _r(pos), "direccion": _r(direccion),
                            "arriba": _r(arriba), "lente": round(c.lens, 4), "sensor": round(c.sensor_width, 4),
                            "orto": round(c.ortho_scale, 4) if c.type == "ORTHO" else 0.0,
                            "cerca": round(c.clip_start, 5), "lejos": round(c.clip_end, 5)})
    return luces, camaras


def matriz(ob):
    """Matriz del objeto en el mundo (o la matriz que se le de), en 12 numeros (3 filas x 4
    columnas), para el JSON."""
    m = ob if isinstance(ob, Matrix) else ob.matrix_world
    return [round(m[r][c], 5) for r in range(3) for c in range(4)]


def _emision_pura(mat):
    """Si el material es solo un nodo Emission, devuelve ese nodo."""
    if not mat or not mat.node_tree:
        return None
    for out in mat.node_tree.nodes:
        if out.type == "OUTPUT_MATERIAL" and out.inputs["Surface"].is_linked:
            node = out.inputs["Surface"].links[0].from_node
            return node if node.type == "EMISSION" else None
    return None


def _emision_a_principled(mat, em):
    """El FBX solo entiende el Principled BSDF: un material de pura emision llegaria gris
    a Unity. Se cambia por un Principled negro con la misma emision. Solo afecta al FBX:
    el .blend ya esta guardado y el render ya esta hecho."""
    color = tuple(em.inputs["Color"].default_value)
    strength = em.inputs["Strength"].default_value
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    bsdf.inputs["Emission Color"].default_value = color
    bsdf.inputs["Emission Strength"].default_value = strength
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    nt.nodes.remove(em)


def _copiar_texturas(tex_dir, destino, nombres):
    """Copia de blender/textures las texturas con esos nombres. Las que no cambiaron no se
    tocan, para que Unity no las vuelva a importar."""
    os.makedirs(destino, exist_ok=True)
    copiadas = 0
    for nombre in sorted(nombres):
        src = os.path.join(tex_dir, nombre + ".png")
        if not os.path.isfile(src):
            continue
        dst = os.path.join(destino, nombre + ".png")
        if os.path.isfile(dst) and filecmp.cmp(src, dst, shallow=False):
            continue
        shutil.copy2(src, dst)
        copiadas += 1
    return copiadas


def _excluido(ob, excluir):
    return bool(ob.users_collection) and all(c.name in excluir for c in ob.users_collection)


def _agrupar(objetos, excluir):
    """Agrupa los objetos de cada coleccion bajo un vacio con su nombre. Devuelve los vacios."""
    grupos = []
    for col in list(bpy.data.collections):
        if col.name in excluir:
            continue
        sueltos = [ob for ob in col.objects if ob in objetos and ob.parent is None]
        if not sueltos:
            continue
        grupo = bpy.data.objects.new(col.name, None)
        col.objects.link(grupo)
        for ob in sueltos:
            ob.parent = grupo  # el grupo esta en el origen: nada se mueve
        grupos.append(grupo)
    return grupos


def _preparar_animaciones(objetos, animaciones):
    """Deja solo las acciones de la lista, sin NLA ni accion activa, y agrega el cuadro de
    reposo a las aditivas. Devuelve los datos de cada clip para el JSON."""
    por_nombre = {a["nombre"]: a for a in animaciones}
    for act in list(bpy.data.actions):
        if act.name not in por_nombre:
            bpy.data.actions.remove(act)
    for ob in objetos:
        if ob.animation_data:
            ob.animation_data.action = None
            for pista in list(ob.animation_data.nla_tracks):
                ob.animation_data.nla_tracks.remove(pista)
        if ob.type == "ARMATURE":
            for pb in ob.pose.bones:
                pb.location = (0.0, 0.0, 0.0)
                pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
                pb.rotation_euler = (0.0, 0.0, 0.0)
                pb.scale = (1.0, 1.0, 1.0)

    datos = []
    fps = bpy.context.scene.render.fps
    for nombre, a in por_nombre.items():
        act = bpy.data.actions.get(nombre)
        if act is None:
            print(f"[aviso] no existe la accion {nombre}")
            continue
        act.use_fake_user = True
        inicio, fin = (int(round(x)) for x in act.frame_range)
        if fin == inicio:
            # Una pose de un solo cuadro: Unity la dejaria vacia. Se repite en el cuadro siguiente.
            for fc in _curvas(act):
                fc.keyframe_points.insert(fin + 1, fc.evaluate(inicio), options={"FAST"})
        if a.get("aditivo"):
            # Reposo un cuadro antes del primero: la referencia de la capa aditiva en Unity.
            reposo = {"rotation_quaternion": (1.0, 0.0, 0.0, 0.0), "scale": (1.0, 1.0, 1.0)}
            for fc in _curvas(act):
                prop = fc.data_path.rsplit(".", 1)[-1]
                valor = reposo.get(prop, (0.0, 0.0, 0.0, 0.0))[fc.array_index]
                fc.keyframe_points.insert(inicio - 1, valor, options={"FAST"})
        datos.append({"nombre": nombre, "cuadros": fin - inicio + 1, "fps": fps,
                      "loop": bool(a.get("loop")), "aditivo": bool(a.get("aditivo"))})
    return datos


def _accion_pose_t(objetos):
    """Agrega una accion con el esqueleto en reposo (la pose en T), llamada _pose_t para que
    quede primera en la lista de acciones. El FBX no dice cual es su toma principal: Unity
    pone el modelo en el primer cuadro de la primera, y de ahi saca la cadera de la
    referencia del Avatar. Sin esto, la cadera de Carmen quedaba como en su primera pose
    (con_plato): mas baja e inclinada. Unity no la importa como clip."""
    for rig in (ob for ob in objetos if ob.type == "ARMATURE"):
        rig.animation_data_create()
        act = bpy.data.actions.new("_pose_t")
        act.use_fake_user = True
        rig.animation_data.action = act
        for pb in rig.pose.bones:  # _preparar_animaciones ya los dejo en reposo
            rot = {"QUATERNION": "rotation_quaternion", "AXIS_ANGLE": "rotation_axis_angle"}.get(
                pb.rotation_mode, "rotation_euler")
            for f in (1, 2):
                pb.keyframe_insert("location", frame=f, group=pb.name)
                pb.keyframe_insert(rot, frame=f, group=pb.name)
        rig.animation_data.action = None


def _curvas(act):
    """Las curvas de una accion (Blender 5 las guarda por capas y canales)."""
    if hasattr(act, "fcurves") and len(act.fcurves):
        return list(act.fcurves)
    curvas = []
    for capa in getattr(act, "layers", []):
        for tira in capa.strips:
            for canal in tira.channelbags:
                curvas += list(canal.fcurves)
    return curvas


def _girar_humanoide(objetos):
    """Gira 180 grados alrededor del eje vertical los objetos de arriba de la jerarquia (el
    esqueleto, y los sueltos como el plato de Carmen): en Unity, el personaje mira hacia +Z."""
    giro = Matrix.Rotation(math.pi, 4, "Z")
    for ob in objetos:
        if ob.parent is None or ob.parent not in objetos:
            ob.matrix_world = giro @ ob.matrix_world
    bpy.context.view_layer.update()


def _accesorios(objetos, accesorios):
    """Para el JSON: donde va cada accesorio en su pose y donde esta en el FBX (su reposo),
    los dos en el mundo de Blender tal como se exporta (ya girado si es humanoide). En
    Unity se aplica como cambio desde el reposo, porque el objeto llega con otro giro
    interno (ver EscenaBlender.EnPose)."""
    rig = next(ob for ob in objetos if ob.type == "ARMATURE")
    return [{"objeto": a["objeto"].name, "pose": a["pose"], "reposo": matriz(a["objeto"]),
             "matriz": matriz(rig.matrix_world @ a["matriz"])} for a in accesorios]


def exportar(root, carpeta, nombre, animaciones=None, excluir=(), estados=None, objetos=None, extra=None,
             humanoide=False, accesorios=None):
    """root: carpeta blender/. carpeta: subcarpeta en Assets/Art. nombre: nombre del FBX.
    animaciones: [{"nombre", "loop", "aditivo"}], las acciones que van como clips.
    excluir: colecciones que no van a Unity. estados: {nombre: foto_estado()}; si no se da,
    se toma el estado actual como 'base'. objetos: solo esos (y las luces y camaras de sus
    colecciones); por defecto, todo. extra: datos que se agregan tal cual al JSON.
    humanoide: un personaje con esqueleto de nombres de Mixamo; se gira para que mire
    hacia +Z en Unity, que lo importa como Humanoid (y sus clips, como poses fijas).
    accesorios: [{"objeto", "pose", "matriz"}], un objeto suelto que el personaje lleva en
    una pose (el plato de Carmen); la matriz es relativa al esqueleto."""
    escena = bpy.context.scene
    proyecto = os.path.dirname(os.path.abspath(root))
    destino = os.path.join(proyecto, "unity", "Assets", "Art", carpeta)
    os.makedirs(destino, exist_ok=True)
    excluir = set(excluir)
    todo = objetos is None

    if todo:
        objetos = [ob for ob in escena.objects if ob.type in TIPOS and not _excluido(ob, excluir)]
        otros = [ob for ob in escena.objects if ob.type in ("LIGHT", "CAMERA")]
    else:
        objetos = list(objetos)
        cols = {c for ob in objetos for c in ob.users_collection}
        otros = [ob for ob in escena.objects if ob.type in ("LIGHT", "CAMERA") and cols & set(ob.users_collection)]

    if not estados:
        estados = {"base": foto_estado(None if todo else otros + objetos)}
    if humanoide:
        _girar_humanoide(objetos + otros)
    luces, camaras = _luces_y_camaras(otros)
    lleva = _accesorios(objetos, accesorios) if accesorios else []

    clips = _preparar_animaciones(objetos, animaciones) if animaciones else []
    if humanoide:
        _accion_pose_t(objetos)

    datos = {"version": 1, "luces": luces, "camaras": camaras,
             "estados": [dict(nombre=k, **v) for k, v in estados.items()], "animaciones": clips,
             "humanoide": bool(humanoide), "accesorios": lleva}
    datos.update(extra or {})
    with open(os.path.join(destino, nombre + "_escena.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=1, ensure_ascii=False)

    mats = {s.material for ob in objetos if ob.type == "MESH" for s in ob.material_slots if s.material}
    texturas = {t for m in mats for t in _imagenes(m)}
    texturas |= {m["textura"] for e in estados.values() for m in e["materiales"] if m["textura"]}

    for mat in mats:
        em = _emision_pura(mat)
        if em is not None:
            _emision_a_principled(mat, em)

    copiadas = _copiar_texturas(os.path.join(root, "textures"), os.path.join(destino, "Textures"), texturas)

    objetos += _agrupar(objetos, excluir)
    for ob in objetos:
        if not ob.visible_shadow:
            ob["sin_sombra"] = 1
    for ob in bpy.context.view_layer.objects:
        ob.select_set(ob in objetos)

    fbx = os.path.join(destino, nombre + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx,
        use_selection=True,
        object_types={"MESH", "EMPTY", "ARMATURE", "OTHER"},  # OTHER: textos y curvas, como malla
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",  # 1 m en Blender = 1 unidad en Unity, escala 1
        axis_forward="-Z",
        axis_up="Y",  # Unity corrige el giro con "Bake Axis Conversion"
        mesh_smooth_type="OFF",
        use_custom_props=True,  # sin_sombra
        add_leaf_bones=False,
        bake_anim=bool(clips),
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=True,  # cada accion, un clip
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,  # sin simplificar: el temblor es de pocos grados
        path_mode="STRIP",  # solo el nombre del archivo: Unity la busca en Textures/
        embed_textures=False,
    )
    print(f"[unity] {fbx}: {len(objetos)} objetos, {len(luces)} luces, {len(camaras)} camaras, "
          f"estados {list(estados)}, {len(clips)} clips, {len(texturas)} texturas ({copiadas} copiadas)")
    return fbx
