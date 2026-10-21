using System;
#if UNITY_EDITOR
using UnityEditor;
#endif
using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// Lo que blender/scripts/exportar_unity.py deja junto al FBX en &lt;nombre&gt;_escena.json:
/// las luces, las cámaras y los estados del mundo (abstinencia, efecto...), que el FBX no guarda.
/// Las posiciones están en coordenadas de Blender (Z arriba) y se pasan a Unity con DeBlender.
/// Las luces se convierten como explica la sección 10 del documento de diseño
/// (Estilo PS1 en Unity).
///
/// Lo usan el importador (Assets/Editor) y el juego: por ejemplo, Elías lee del JSON de sus
/// brazos cómo se mueven la cabeza, la puerta y el auricular en cada clip.
///
/// On the Nod > Crear luces desde Blender: con el JSON seleccionado, pone sus luces en la escena
/// abierta, en el primer estado (por ejemplo, abstinencia).
/// </summary>
[Serializable]
public class EscenaBlender
{
    public Luz[] luces;
    public Camara[] camaras;
    public Estado[] estados;
    public Animacion[] animaciones;
    public Pista[] pistas;
    public Accesorio[] accesorios;
    public bool humanoide; // personaje con esqueleto de Mixamo: se importa como Humanoid

    [Serializable]
    public class Luz
    {
        public string nombre;
        public string tipo; // POINT, SPOT, AREA o SUN
        public float[] posicion;
        public float[] direccion; // hacia dónde apunta
        public float radio;
        public float[] tamano; // luces de área, en metros
        public float cono; // spots: ángulo completo, en grados
        public float suavizado; // spots: borde suave, de 0 a 1
        public bool sombras;
        public string truco; // "rebote", "fuga" o vacío: ver el apartado del asset en la sección 10
    }

    [Serializable]
    public class Camara
    {
        public string nombre;
        public float[] posicion;
        public float[] direccion;
        public float[] arriba;
        public float lente; // mm
        public float sensor; // mm de ancho
        public float orto; // ancho de la vista ortográfica en metros; 0 si es en perspectiva
        public float cerca;
        public float lejos;
    }

    [Serializable]
    public class Estado
    {
        public string nombre;
        public LuzEstado[] luces;
        public MaterialEstado[] materiales;
        public Forma[] formas;
        public string[] colecciones_ocultas;
        public string[] objetos_ocultos; // por ejemplo, la Polaroid de Tomás fuera del estado 0
        public Mundo mundo;
    }

    [Serializable]
    public class Forma
    {
        public string objeto;
        public string forma; // shape key de Blender = blendshape de Unity
        public float valor; // de 0 a 1 (en Unity, de 0 a 100)
    }

    /// <summary>Un clip del FBX. Lo usa el importador para el bucle y la capa aditiva.</summary>
    [Serializable]
    public class Animacion
    {
        public string nombre;
        public int cuadros;
        public float fps;
        public bool loop;
        public bool aditivo; // va en una capa aditiva; su referencia es un cuadro de reposo
    }

    /// <summary>
    /// Cómo se mueve un objeto durante un clip, cuadro a cuadro: la cabeza (en Unity, la
    /// cámara), una puerta, el auricular... Las matrices son las de Blender en el mundo
    /// (12 números por cuadro); se pasan a Unity con MatrizDeBlender. Si hay reposo, la pista
    /// se aplica como cambio desde esa posición (el objeto de Unity puede tener otro origen).
    /// </summary>
    [Serializable]
    public class Pista
    {
        public string clip;
        public string objeto;
        public float[] reposo;
        public float[] matrices;
        public int Cuadros => matrices.Length / 12;

        /// <summary>
        /// Dónde está el objeto a los <paramref name="tiempo"/> segundos del clip (entre dos
        /// cuadros, interpola). En coordenadas de Unity, relativas al espacio de Blender (en el
        /// 4B, a su raíz).
        /// </summary>
        public Matrix4x4 EnTiempo(float tiempo, float fps)
        {
            float f = Mathf.Clamp(tiempo * fps, 0f, Cuadros - 1);
            int i0 = Mathf.FloorToInt(f);
            int i1 = Mathf.Min(i0 + 1, Cuadros - 1);
            var a = MatrizDeBlender(matrices, i0 * 12);
            var b = MatrizDeBlender(matrices, i1 * 12);
            return Matrix4x4.TRS(Vector3.Lerp(a.GetPosition(), b.GetPosition(), f - i0),
                                 Quaternion.Slerp(a.rotation, b.rotation, f - i0), Vector3.one);
        }

        /// <summary>
        /// Cuánto se movió el objeto desde su reposo a los <paramref name="tiempo"/> segundos (la
        /// puerta, el auricular). Se aplica al objeto de Unity como cambio, porque llega con otro
        /// giro interno que en Blender.
        /// </summary>
        public Matrix4x4 CambioEnTiempo(float tiempo, float fps) => EnTiempo(tiempo, fps) * MatrizDeBlender(reposo).inverse;
    }

    /// <summary>
    /// Un objeto suelto que el personaje lleva en una pose (el plato de Carmen): dónde va en
    /// esa pose y dónde está en el FBX (su reposo), las dos en el espacio del modelo con
    /// coordenadas de Blender (12 números). Se aplica como cambio desde el reposo, con
    /// <see cref="EnPose"/>. Si una pose no lo nombra, en esa pose no lo lleva.
    /// </summary>
    [Serializable]
    public class Accesorio
    {
        public string objeto;
        public string pose;
        public float[] reposo;
        public float[] matriz;
    }

    [Serializable]
    public class LuzEstado
    {
        public string nombre;
        public bool encendida;
        public float[] color; // lineal
        public float potencia; // vatios (el sol: W/m²)
    }

    [Serializable]
    public class MaterialEstado
    {
        public string nombre;
        public float[] emision; // lineal
        public float fuerza;
        public string textura; // nombre del PNG en Textures/, sin extensión
    }

    [Serializable]
    public class Mundo
    {
        public float[] fondo; // la luz del cielo, lineal
        public float niebla_densidad;
        public float[] niebla_color;
    }

    public static EscenaBlender Leer(TextAsset json) => JsonUtility.FromJson<EscenaBlender>(json.text);

    /// <summary>Lee el JSON que acompaña a un FBX (&lt;nombre&gt;_escena.json), o null si no hay.</summary>
    public static EscenaBlender DelModelo(string rutaFbx)
    {
        var ruta = System.IO.Path.ChangeExtension(rutaFbx, null) + "_escena.json";
        return System.IO.File.Exists(ruta) ? JsonUtility.FromJson<EscenaBlender>(System.IO.File.ReadAllText(ruta)) : null;
    }

    /// <summary>Blender (x, y, z) con Z arriba → Unity (x, z, y) con Y arriba.</summary>
    public static Vector3 DeBlender(float[] v) => new Vector3(v[0], v[2], v[1]);

    /// <summary>
    /// Matriz de Blender (12 números por filas, desde <paramref name="inicio"/>) → matriz de
    /// Unity. Para una cabeza o una cámara, su +Z de Unity es hacia donde mira en Blender (+Y).
    /// </summary>
    public static Matrix4x4 MatrizDeBlender(float[] m, int inicio = 0)
    {
        var b = Matrix4x4.identity;
        for (int fila = 0; fila < 3; fila++)
            for (int col = 0; col < 4; col++)
                b[fila, col] = m[inicio + fila * 4 + col];
        // Cambiar Y por Z antes y después: la misma conversión que DeBlender.
        var p = new Matrix4x4(new Vector4(1, 0, 0, 0), new Vector4(0, 0, 1, 0), new Vector4(0, 1, 0, 0), new Vector4(0, 0, 0, 1));
        return p * b * p;
    }

    public Animacion BuscarAnimacion(string nombre) => animaciones == null ? null : Array.Find(animaciones, a => a.nombre == nombre);

    public Pista BuscarPista(string clip, string objeto) =>
        pistas == null ? null : Array.Find(pistas, p => p.clip == clip && p.objeto == objeto);

    public Accesorio BuscarAccesorio(string pose, string objeto) =>
        accesorios == null ? null : Array.Find(accesorios, a => a.pose == pose && a.objeto == objeto);

    /// <summary>
    /// Dónde va el accesorio en su pose, respecto de la raíz del modelo. <paramref name="reposo"/>:
    /// dónde está en el modelo recién importado, respecto de la misma raíz (el plato cuelga de
    /// ella: es su matriz local). Se usa el cambio y no la matriz tal cual porque en Unity el
    /// objeto tiene otro giro interno que en Blender.
    /// </summary>
    public static Matrix4x4 EnPose(Accesorio a, Matrix4x4 reposo) =>
        MatrizDeBlender(a.matriz) * MatrizDeBlender(a.reposo).inverse * reposo;

    public static Color Lineal(float[] c) => new Color(c[0], c[1], c[2]);

    public Estado BuscarEstado(string nombre) => Array.Find(estados, e => e.nombre == nombre);

    public Camara BuscarCamara(string nombre) => Array.Find(camaras, c => c.nombre == nombre);

    // Conversión de luces de Blender (vatios) a URP sin unidades físicas: ver la sección 10.
    public static float IntensidadPuntual(float vatios) => vatios / (4f * Mathf.PI * Mathf.PI);
    public static float IntensidadArea(float vatios) => vatios / (Mathf.PI * Mathf.PI);
    public static float IntensidadSol(float fuerza) => fuerza / Mathf.PI;

    /// <summary>Distancia donde EEVEE corta la luz (umbral 0,01).</summary>
    public static float Alcance(float vatios, Color lineal) => Mathf.Sqrt(Mathf.Max(lineal.maxColorComponent * vatios, 0f));

    /// <summary>Crea las luces encendidas en <paramref name="estado"/> como hijas de <paramref name="padre"/>.</summary>
    public void CrearLuces(string estado, Transform padre)
    {
        var datos = BuscarEstado(estado);
        foreach (var luz in luces)
        {
            var e = Array.Find(datos.luces, x => x.nombre == luz.nombre);
            if (e == null || !e.encendida)
                continue;
            // Relativas al padre: en el 4B el padre está en el origen; la luz de los brazos
            // cuelga de la cámara.
            var objeto = new GameObject(luz.nombre);
            objeto.transform.SetParent(padre, false);
            objeto.transform.localPosition = DeBlender(luz.posicion);
            var dir = DeBlender(luz.direccion);
            objeto.transform.localRotation = Quaternion.LookRotation(dir, Mathf.Abs(dir.y) > 0.99f ? Vector3.forward : Vector3.up);
            Configurar(objeto.AddComponent<Light>(), luz, e);
            if (luz.truco == "rebote")
                SepararDeAbajo(objeto.transform, luz.radio);
        }
    }

    /// <summary>
    /// Las de "rebote" son esferas de 30 a 50 cm en Blender, que iluminan parejo lo que tienen
    /// pegado (la de rebote_bano está a 6 cm del piso). En Unity son un punto y quemarían esa
    /// superficie: se suben hasta que lo que tienen abajo quede a medio radio. Con el radio
    /// entero, la puerta del baño se iluminaba demasiado alto (comparado con 4b_bano.png). Usa
    /// las colisiones de la escena.
    /// </summary>
    public static void SepararDeAbajo(Transform luz, float radio)
    {
        float distancia = radio * 0.5f;
        Physics.SyncTransforms();
        if (Physics.Raycast(luz.position + Vector3.up * distancia, Vector3.down, out var abajo, 2f * distancia, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore))
            luz.position = abajo.point + Vector3.up * distancia;
    }

    public static void Configurar(Light l, Luz luz, LuzEstado estado)
    {
        var color = Lineal(estado.color);
        l.color = color.gamma; // Unity guarda el color de la luz en sRGB
        // Mixta: la luz directa se calcula en tiempo real; el rebote y las sombras de lo que no
        // se mueve, en la luz precalculada (Generate Lighting). Las luces-truco van enteras en la
        // luz precalculada: las de "fuga" (la que se cuela bajo una puerta), porque la rendija es
        // demasiado fina para las sombras en tiempo real; las de "rebote" (imitan la luz que
        // rebota, sin sombra), porque solo iluminan lo que no se mueve. Sin precalcular la
        // escena, las luces-truco no iluminan. Una luz que se mueve (la de los brazos, que cuelga
        // de la cámara) se pasa a Realtime en la escena.
        l.lightmapBakeType = string.IsNullOrEmpty(luz.truco) ? LightmapBakeType.Mixed : LightmapBakeType.Baked;
        l.shadows = luz.sombras ? LightShadows.Soft : LightShadows.None;
        switch (luz.tipo)
        {
            case "SUN":
                l.type = LightType.Directional;
                l.intensity = IntensidadSol(estado.potencia);
                break;
            case "SPOT":
                // En Blender, la potencia de un spot se mide como si alumbrara para todos lados.
                l.type = LightType.Spot;
                l.intensity = IntensidadPuntual(estado.potencia);
                l.range = Alcance(estado.potencia, color);
                l.spotAngle = Mathf.Min(luz.cono, 179f);
                l.innerSpotAngle = l.spotAngle * (1f - luz.suavizado);
                break;
            case "AREA":
                // URP no tiene luces de área en tiempo real: un spot ancho que apunta igual.
                l.type = LightType.Spot;
                l.intensity = IntensidadArea(estado.potencia);
                l.range = Alcance(estado.potencia, color);
                l.spotAngle = 170f;
                l.innerSpotAngle = 60f;
                break;
            default:
                l.type = LightType.Point;
                l.intensity = IntensidadPuntual(estado.potencia);
                l.range = Alcance(estado.potencia, color);
                break;
        }
    }

    /// <summary>Pone la cámara donde está la de Blender, con el mismo lente.</summary>
    public static void ConfigurarCamara(Camera camara, Camara c, float aspecto = 16f / 9f)
    {
        camara.transform.SetPositionAndRotation(DeBlender(c.posicion),
            Quaternion.LookRotation(DeBlender(c.direccion), DeBlender(c.arriba)));
        camara.nearClipPlane = c.cerca;
        camara.farClipPlane = c.lejos;
        // El sensor de Blender se ajusta al lado más largo de la imagen.
        if (c.orto > 0f)
        {
            camara.orthographic = true;
            camara.orthographicSize = c.orto * 0.5f / Mathf.Max(aspecto, 1f);
        }
        else
        {
            camara.orthographic = false;
            float angulo = 2f * Mathf.Atan(c.sensor * 0.5f / c.lente) * Mathf.Rad2Deg;
            camara.fieldOfView = aspecto >= 1f ? Camera.HorizontalToVerticalFieldOfView(angulo, aspecto) : angulo;
        }
    }

    /// <summary>
    /// Ambiente y niebla de la escena (Lighting > Environment) según el mundo de Blender.
    /// Devuelve el color de la niebla, que va en el componente NieblaPS1.
    /// </summary>
    public static Color AplicarMundo(Mundo mundo)
    {
        var fondo = Lineal(mundo.fondo);
        var niebla = Lineal(mundo.niebla_color);
        RenderSettings.skybox = null;
        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientLight = fondo.gamma;
        RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
        RenderSettings.customReflectionTexture = null;
        RenderSettings.reflectionIntensity = 0f;
        RenderSettings.fog = mundo.niebla_densidad > 0f;
        RenderSettings.fogMode = FogMode.Exponential;
        RenderSettings.fogDensity = mundo.niebla_densidad;
        // Lo que la niebla devuelve de la luz del cielo.
        RenderSettings.fogColor = (fondo * niebla).gamma;
        return niebla;
    }

#if UNITY_EDITOR
    [MenuItem("On the Nod/Crear luces desde Blender")]
    static void CrearLucesDelSeleccionado()
    {
        var json = Selection.activeObject as TextAsset;
        var escena = json != null ? Leer(json) : null;
        if (escena == null || escena.estados == null || escena.estados.Length == 0)
        {
            Debug.LogError("Selecciona un archivo _escena.json de Assets/Art.");
            return;
        }
        var estado = escena.estados[0].nombre;
        var raiz = new GameObject($"Luces ({estado})");
        escena.CrearLuces(estado, raiz.transform);
        Undo.RegisterCreatedObjectUndo(raiz, "Crear luces desde Blender");
        Selection.activeGameObject = raiz;
    }

    [MenuItem("On the Nod/Crear luces desde Blender", true)]
    static bool HayJsonSeleccionado() =>
        Selection.activeObject is TextAsset t && AssetDatabase.GetAssetPath(t).EndsWith("_escena.json");
#endif
}
