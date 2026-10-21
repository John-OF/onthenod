using System.IO;
using UnityEditor;
using UnityEditor.AssetImporters;
using UnityEngine;

/// <summary>
/// Importa con el estilo PS1 todo lo que los scripts de Blender exportan a Assets/Art/
/// (ver blender/scripts/exportar_unity.py), sin configurar nada a mano:
///   - Texturas: filtro Point, sin compresión, sin mipmaps y sin reescalar
///     (Non-Power of 2 en None; algunas no miden potencias de 2).
///   - Modelos: sin luces ni cámaras, con el giro de Blender corregido. Lo que en Blender no
///     proyecta sombra (propiedad sin_sombra) tampoco la proyecta en Unity.
///   - Materiales: shader OnTheNod/PS1, con el color, la textura y la emisión de Blender.
///   - Clips: los que dice el JSON del modelo (&lt;nombre&gt;_escena.json), con su nombre, en
///     bucle si corresponde y, los aditivos, con su cuadro de reposo como referencia. Sin
///     compresión: el temblor es de pocos grados.
///   - Personajes (el JSON dice "humanoide"): esqueleto Humanoid con su propio Avatar, para
///     usar animaciones de Mixamo. Sus clips son poses: quedan donde las dejó Blender, sin
///     mover ni girar el personaje.
///   - Escenarios (sin clips): colisión en todo lo que mide al menos 25 cm por algún lado
///     (paredes, pisos, muebles, bolsas de basura), para no atravesarlo al caminar. Lo chico
///     (jeringas, botellas) no la lleva, ni lo que está tirado en el piso, mide menos de 20 cm
///     de alto y menos de 1 m de largo (ropa, cojines caídos, papeles): se pisa sin subirse.
///   - Escenarios, para la luz precalculada: coordenadas para el mapa de luz y todo marcado
///     como fijo (Contribute GI). Lo chico (menos de 25 cm) toma la luz de las sondas en vez
///     del mapa de luz. Lo que se mueve en una escena (la puerta que se abre) se desmarca ahí.
/// Volver a correr un script de Blender reimporta su carpeta con estas reglas.
/// </summary>
public class ImportadorArte : AssetPostprocessor
{
    const string CarpetaArte = "Assets/Art/";
    const string ShaderPS1 = "OnTheNod/PS1";
    const float TamanoConColision = 0.25f; // metros

    // Subir este número hace que Unity reimporte Assets/Art con las reglas nuevas.
    public override uint GetVersion() => 12;

    static bool EsArte(string ruta) => ruta.StartsWith(CarpetaArte);

    void OnPreprocessTexture()
    {
        if (!EsArte(assetPath))
            return;

        var importador = (TextureImporter)assetImporter;
        importador.textureType = TextureImporterType.Default;
        importador.sRGBTexture = true;
        importador.filterMode = FilterMode.Point;
        importador.anisoLevel = 0;
        importador.mipmapEnabled = false;
        importador.npotScale = TextureImporterNPOTScale.None;
        importador.textureCompression = TextureImporterCompression.Uncompressed;
        importador.wrapMode = TextureWrapMode.Repeat;
    }

    void OnPreprocessModel()
    {
        if (!EsArte(assetPath))
            return;

        var importador = (ModelImporter)assetImporter;
        importador.bakeAxisConversion = true; // sin esto, Blender llega girado -90° en X
        // Siempre una raíz propia, aunque el FBX tenga un solo objeto arriba (una sola
        // colección): así todos los modelos son archivo > colecciones > objetos.
        importador.preserveHierarchy = true;
        importador.importCameras = false;
        importador.importLights = false;
        importador.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
        importador.materialLocation = ModelImporterMaterialLocation.InPrefab;
        importador.animationCompression = ModelImporterAnimationCompression.Off;

        // Personajes: Humanoid (Unity reconoce los huesos por sus nombres de Mixamo). Otros
        // modelos con clips (el JSON lo dice): esqueleto genérico. Los dos, con su propio Avatar.
        var json = Path.ChangeExtension(assetPath, null) + "_escena.json";
        if (File.Exists(json))
            context.DependsOnSourceAsset(json);
        var escena = EscenaBlender.DelModelo(assetPath);
        if (escena != null && escena.humanoide)
        {
            importador.animationType = ModelImporterAnimationType.Human;
            importador.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            // Unity guarda en el .meta qué hueso es cuál y la pose de referencia (la T) de la
            // primera importación, y no los vuelve a calcular. Se borran para que los saque
            // otra vez del modelo: si el esqueleto cambia en Blender, el Avatar también.
            var descripcion = importador.humanDescription;
            descripcion.human = new HumanBone[0];
            descripcion.skeleton = new SkeletonBone[0];
            importador.humanDescription = descripcion;
        }
        else if (escena?.animaciones?.Length > 0)
        {
            importador.animationType = ModelImporterAnimationType.Generic;
            importador.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
        }
        else if (escena != null)
        {
            importador.generateSecondaryUV = true; // escenario: coordenadas para el mapa de luz
        }
    }

    static bool EsEscenario(EscenaBlender escena) =>
        escena != null && !escena.humanoide && (escena.animaciones == null || escena.animaciones.Length == 0);

    void OnPreprocessAnimation()
    {
        if (!EsArte(assetPath))
            return;

        var json = Path.ChangeExtension(assetPath, null) + "_escena.json";
        if (File.Exists(json))
            context.DependsOnSourceAsset(json);
        var escena = EscenaBlender.DelModelo(assetPath);
        if (escena?.animaciones == null || escena.animaciones.Length == 0)
            return;

        // Blender nombra cada clip "Esqueleto|accion"; quedan solo los de la lista, con el nombre de la acción.
        var importador = (ModelImporter)assetImporter;
        var clips = new System.Collections.Generic.List<ModelImporterClipAnimation>();
        foreach (var clip in importador.defaultClipAnimations)
        {
            var nombre = clip.takeName.Substring(clip.takeName.LastIndexOf('|') + 1);
            var datos = escena.BuscarAnimacion(nombre);
            if (datos == null)
                continue;
            clip.name = nombre;
            clip.loopTime = datos.loop;
            if (escena.humanoide)
            {
                // Pose fija: el cuerpo queda a la altura, en el lugar y hacia el lado de Blender
                // (sentado, la cadera baja). Si no, Unity saca de la pose un movimiento de la
                // raíz y puede correr, girar o subir al personaje.
                clip.lockRootRotation = clip.keepOriginalOrientation = true;
                clip.lockRootHeightY = clip.keepOriginalPositionY = true;
                clip.lockRootPositionXZ = clip.keepOriginalPositionXZ = true;
            }
            if (datos.aditivo)
            {
                // El primer cuadro es el reposo que agregó exportar_unity.py: referencia, no parte del clip.
                clip.hasAdditiveReferencePose = true;
                clip.additiveReferencePoseFrame = clip.firstFrame;
                clip.firstFrame += 1;
            }
            clips.Add(clip);
        }
        importador.clipAnimations = clips.ToArray();
    }

    readonly System.Collections.Generic.List<GameObject> sinSombra = new System.Collections.Generic.List<GameObject>();

    void OnPostprocessGameObjectWithUserProperties(GameObject objeto, string[] nombres, object[] valores)
    {
        if (EsArte(assetPath) && System.Array.IndexOf(nombres, "sin_sombra") >= 0)
            sinSombra.Add(objeto);
    }

    void OnPostprocessModel(GameObject modelo)
    {
        if (!EsArte(assetPath))
            return;

        foreach (var objeto in sinSombra)
            if (objeto != null && objeto.TryGetComponent<Renderer>(out var renderer))
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

        // La caja que Unity usa para saber si una malla animada está a la vista se calcula en
        // la pose de reposo; si una animación lleva las manos fuera de esa caja (los brazos en
        // primera persona lo hacen siempre), Unity deja de dibujarlas. Se recalcula cada cuadro.
        foreach (var piel in modelo.GetComponentsInChildren<SkinnedMeshRenderer>(true))
            piel.updateWhenOffscreen = true;

        // Escenarios: colisión en lo que se choca al caminar y luz precalculada (ver arriba).
        if (!EsEscenario(EscenaBlender.DelModelo(assetPath)))
            return;
        foreach (var t in modelo.GetComponentsInChildren<Transform>(true))
            GameObjectUtility.SetStaticEditorFlags(t.gameObject, StaticEditorFlags.ContributeGI);
        foreach (var malla in modelo.GetComponentsInChildren<MeshFilter>(true))
        {
            if (malla.sharedMesh == null)
                continue;
            var caja = CajaEnElModelo(malla, modelo.transform);
            if (EsChico(caja) && malla.TryGetComponent<MeshRenderer>(out var r))
                r.receiveGI = ReceiveGI.LightProbes;
            if (SeChoca(caja))
                malla.gameObject.AddComponent<MeshCollider>().sharedMesh = malla.sharedMesh;
        }
    }

    static bool EsChico(Bounds caja) => Mathf.Max(caja.size.x, caja.size.y, caja.size.z) < TamanoConColision;

    static bool SeChoca(Bounds caja)
    {
        var tamano = caja.size;
        if (EsChico(caja))
            return false;
        bool tiradoEnElPiso = caja.min.y < 0.05f && caja.max.y < 0.2f && Mathf.Max(tamano.x, tamano.z) < 1f;
        return !tiradoEnElPiso;
    }

    /// <summary>La caja que ocupa la malla, en las coordenadas del modelo (el piso del escenario está en y = 0).</summary>
    static Bounds CajaEnElModelo(MeshFilter malla, Transform raiz)
    {
        var local = malla.sharedMesh.bounds;
        var aModelo = raiz.worldToLocalMatrix * malla.transform.localToWorldMatrix;
        var caja = new Bounds(aModelo.MultiplyPoint3x4(local.center), Vector3.zero);
        for (int i = 0; i < 8; i++)
            caja.Encapsulate(aModelo.MultiplyPoint3x4(local.center + Vector3.Scale(local.extents,
                new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1))));
        return caja;
    }

    void OnPreprocessMaterialDescription(MaterialDescription descripcion, Material material, AnimationClip[] animaciones)
    {
        if (!EsArte(assetPath))
            return;

        var shader = Shader.Find(ShaderPS1);
        if (shader == null)
        {
            Debug.LogError($"No se encontró el shader {ShaderPS1}: {assetPath} queda con los materiales por defecto.");
            return;
        }
        material.shader = shader;

        // Blender guarda los colores en lineal. Unity guarda los de los materiales en sRGB y
        // los pasa a lineal al dibujar, así que se entregan con .gamma.
        var color = Color.white;
        if (descripcion.TryGetProperty("DiffuseColor", out TexturePropertyDescription textura))
        {
            var tex = BuscarTextura(textura);
            if (tex != null)
                material.SetTexture("_BaseMap", tex);
            else
                Debug.LogWarning($"{assetPath}: no se encontró la textura {textura.path} del material {descripcion.materialName}.");
        }
        else if (descripcion.TryGetProperty("DiffuseColor", out Vector4 difuso))
        {
            color = new Color(difuso.x, difuso.y, difuso.z).gamma;
        }
        material.SetColor("_BaseColor", color);

        if (descripcion.TryGetProperty("EmissiveColor", out Vector4 emision))
        {
            float fuerza = descripcion.TryGetProperty("EmissiveFactor", out float factor) ? factor : 1f;
            var lineal = new Color(emision.x * fuerza, emision.y * fuerza, emision.z * fuerza);
            if (lineal.maxColorComponent > 0f)
            {
                material.SetFloat("_Emision", 1f);
                material.EnableKeyword("_EMISSION");
                material.SetColor("_EmissionColor", lineal.gamma);
                material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
            }
        }
    }

    Texture BuscarTextura(TexturePropertyDescription textura)
    {
        if (textura.texture != null)
            return textura.texture;

        // Unity no la encontró (por ejemplo, si el modelo se importó antes que la textura):
        // se busca en la carpeta Textures que está junto al FBX.
        var nombre = Path.GetFileName(textura.path ?? "");
        if (string.IsNullOrEmpty(nombre))
            return null;
        var ruta = Path.GetDirectoryName(assetPath).Replace('\\', '/') + "/Textures/" + nombre;
        context.DependsOnSourceAsset(ruta);
        return AssetDatabase.LoadAssetAtPath<Texture2D>(ruta);
    }
}
