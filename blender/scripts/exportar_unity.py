r"""
Exporta la escena de Blender a Unity: un FBX y las texturas que usa.

No se corre solo: lo importan los scripts de assets y lo llaman al final, despues
de guardar el .blend y renderizar.

    import exportar_unity
    exportar_unity.exportar(ROOT, "PruebaEstiloPasillo", "prueba_estilo_pasillo")

Salidas (ROOT es la carpeta blender/; el proyecto de Unity esta al lado):
  unity/Assets/Art/<carpeta>/<nombre>.fbx     mallas, empties y esqueletos
  unity/Assets/Art/<carpeta>/Textures/*.png   las texturas de blender/textures que estan cargadas

Las luces y la camara no se exportan: en Unity se ponen en la escena.
Unity importa todo solo (Assets/Editor/ImportadorArte.cs): texturas con filtro Point
y materiales con el shader PS1.
"""
import filecmp
import os
import shutil

import bpy


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
    """Copia las imagenes cargadas que vienen de blender/textures. Las que no cambiaron
    no se tocan, para que Unity no las vuelva a importar."""
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


def exportar(root, carpeta, nombre, animaciones=False):
    """root: carpeta blender/. carpeta: subcarpeta en Assets/Art. nombre: nombre del FBX."""
    proyecto = os.path.dirname(os.path.abspath(root))
    destino = os.path.join(proyecto, "unity", "Assets", "Art", carpeta)
    os.makedirs(destino, exist_ok=True)

    for mat in bpy.data.materials:
        em = _emision_pura(mat)
        if em is not None:
            _emision_a_principled(mat, em)

    copiadas = _copiar_texturas(os.path.join(root, "textures"), os.path.join(destino, "Textures"))

    fbx = os.path.join(destino, nombre + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx,
        use_selection=False,
        object_types={"MESH", "EMPTY", "ARMATURE", "OTHER"},  # OTHER: textos y curvas, como malla
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",  # 1 m en Blender = 1 unidad en Unity, escala 1
        axis_forward="-Z",
        axis_up="Y",  # Unity corrige el giro con "Bake Axis Conversion"
        mesh_smooth_type="OFF",
        use_custom_props=False,
        add_leaf_bones=False,
        bake_anim=animaciones,
        path_mode="STRIP",  # solo el nombre del archivo: Unity la busca en Textures/
        embed_textures=False,
    )
    print(f"[unity] {fbx} ({copiadas} texturas copiadas)")
    return fbx
