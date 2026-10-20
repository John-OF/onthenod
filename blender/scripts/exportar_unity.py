r"""
Exporta la escena de Blender a Unity: un FBX, las texturas que usa y un JSON con
lo que el FBX no guarda (luces, camaras y estados del mundo).

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

Salidas (ROOT es la carpeta blender/; el proyecto de Unity esta al lado):
  unity/Assets/Art/<carpeta>/<nombre>.fbx          mallas, empties y esqueletos
  unity/Assets/Art/<carpeta>/<nombre>_escena.json  luces, camaras y estados
  unity/Assets/Art/<carpeta>/Textures/*.png        las texturas de blender/textures que estan cargadas

Que cambia en el FBX respecto del .blend:
  - Cada coleccion es un objeto vacio con su nombre, padre de sus objetos: en Unity se
    muestra u oculta entera (por ejemplo, Efecto). Las de `excluir` no se exportan.
  - Los objetos que no proyectan sombra (Visibilidad > Sombra apagada) llevan la propiedad
    sin_sombra; Unity la lee al importar.
  - Los materiales de pura emision pasan a Principled (el FBX solo entiende ese).
Las luces y las camaras van en el JSON, no en el FBX. Las posiciones del JSON estan en
coordenadas de Blender (Z arriba); en Unity, (x, y, z) de Blender es (x, z, y).
Unity importa todo solo (Assets/Editor/ImportadorArte.cs y EscenaBlender.cs).
"""
import filecmp
import json
import os
import shutil

import bpy
from mathutils import Vector

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


def _textura(mat):
    """Nombre del archivo de la textura del color (sin extension), o ''."""
    if not mat or not mat.node_tree:
        return ""
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image and node.image.filepath:
            return os.path.splitext(os.path.basename(bpy.path.abspath(node.image.filepath)))[0]
    return ""


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


def foto_estado():
    """Lo que puede cambiar de un estado del mundo a otro: que luces estan encendidas y con que
    color y potencia, la emision y la textura de cada material, las colecciones ocultas y el
    mundo (fondo y niebla). Se llama con la escena ya puesta en ese estado."""
    luces = [{"nombre": ob.name, "encendida": not ob.hide_render,
              "color": _r(ob.data.color), "potencia": round(ob.data.energy, 5)}
             for ob in bpy.context.scene.objects if ob.type == "LIGHT"]
    materiales = []
    for mat in bpy.data.materials:
        em = _emision(mat)
        tex = _textura(mat)
        if em is None and not tex:
            continue
        color, fuerza = em if em else ((0.0, 0.0, 0.0), 0.0)
        materiales.append({"nombre": mat.name, "emision": _r(color), "fuerza": round(fuerza, 5), "textura": tex})
    ocultas = [c.name for c in bpy.data.collections if c.hide_render]
    return {"luces": luces, "materiales": materiales, "colecciones_ocultas": ocultas, "mundo": _mundo()}


def _luces_y_camaras():
    luces, camaras = [], []
    for ob in bpy.context.scene.objects:
        mw = ob.matrix_world
        pos = mw.translation
        direccion = (mw.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()  # luces y camaras miran a su -Z
        if ob.type == "LIGHT":
            d = ob.data
            luz = {"nombre": ob.name, "tipo": d.type, "posicion": _r(pos), "direccion": _r(direccion),
                   "radio": 0.0, "tamano": [0.0, 0.0], "cono": 0.0, "suavizado": 0.0,
                   "sombras": bool(d.use_shadow),
                   # luces que solo existen para imitar algo que EEVEE no calcula: "rebote", "fuga"
                   "truco": str(ob.get("truco", ""))}
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


def _copiar_texturas(tex_dir, destino):
    """Copia las imagenes cargadas que vienen de blender/textures (tambien las de otros
    estados, como las limpias del efecto). Las que no cambiaron no se tocan, para que
    Unity no las vuelva a importar."""
    os.makedirs(destino, exist_ok=True)
    tex_dir = os.path.normcase(os.path.abspath(tex_dir))
    copiadas = 0
    for img in bpy.data.images:
        if img.source != "FILE" or not img.filepath:
            continue
        src = os.path.abspath(bpy.path.abspath(img.filepath))
        if os.path.normcase(os.path.dirname(src)) != tex_dir or not os.path.isfile(src):
            continue
        dst = os.path.join(destino, os.path.basename(src))
        if os.path.isfile(dst) and filecmp.cmp(src, dst, shallow=False):
            continue
        shutil.copy2(src, dst)
        copiadas += 1
    return copiadas


def _preparar_objetos(excluir):
    """Agrupa cada coleccion bajo un vacio con su nombre y devuelve los objetos a exportar."""
    def excluido(ob):
        return bool(ob.users_collection) and all(c.name in excluir for c in ob.users_collection)

    for col in list(bpy.data.collections):
        if col.name in excluir:
            continue
        sueltos = [ob for ob in col.objects if ob.type in TIPOS and ob.parent is None]
        if not sueltos:
            continue
        grupo = bpy.data.objects.new(col.name, None)
        col.objects.link(grupo)
        for ob in sueltos:
            ob.parent = grupo  # el grupo esta en el origen: nada se mueve

    objetos = [ob for ob in bpy.context.scene.objects if ob.type in TIPOS and not excluido(ob)]
    for ob in objetos:
        if not ob.visible_shadow:
            ob["sin_sombra"] = 1
    return objetos


def exportar(root, carpeta, nombre, animaciones=False, excluir=(), estados=None):
    """root: carpeta blender/. carpeta: subcarpeta en Assets/Art. nombre: nombre del FBX.
    excluir: colecciones que no van a Unity. estados: {nombre: foto_estado()}; si no se da,
    se toma el estado actual como 'base'."""
    proyecto = os.path.dirname(os.path.abspath(root))
    destino = os.path.join(proyecto, "unity", "Assets", "Art", carpeta)
    os.makedirs(destino, exist_ok=True)

    if not estados:
        estados = {"base": foto_estado()}
    luces, camaras = _luces_y_camaras()
    datos = {"version": 1, "luces": luces, "camaras": camaras,
             "estados": [dict(nombre=k, **v) for k, v in estados.items()]}
    with open(os.path.join(destino, nombre + "_escena.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=1, ensure_ascii=False)

    for mat in bpy.data.materials:
        em = _emision_pura(mat)
        if em is not None:
            _emision_a_principled(mat, em)

    copiadas = _copiar_texturas(os.path.join(root, "textures"), os.path.join(destino, "Textures"))

    objetos = _preparar_objetos(set(excluir))
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
        bake_anim=animaciones,
        path_mode="STRIP",  # solo el nombre del archivo: Unity la busca en Textures/
        embed_textures=False,
    )
    print(f"[unity] {fbx}: {len(objetos)} objetos, {len(luces)} luces, {len(camaras)} camaras, "
          f"estados {list(estados)}, {copiadas} texturas copiadas")
    return fbx
