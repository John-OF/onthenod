using System;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// Lo que blender/scripts/exportar_unity.py deja junto al FBX en &lt;nombre&gt;_escena.json:
/// las luces, las cámaras y los estados del mundo (abstinencia, efecto...), que el FBX no guarda.
/// Las posiciones están en coordenadas de Blender (Z arriba) y se pasan a Unity con DeBlender.
/// Las luces se convierten como explica la sección 10 del documento de diseño
/// (Estilo PS1 en Unity).
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
        public string[] colecciones_ocultas;
        public Mundo mundo;
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

    /// <summary>Blender (x, y, z) con Z arriba → Unity (x, z, y) con Y arriba.</summary>
    public static Vector3 DeBlender(float[] v) => new Vector3(v[0], v[2], v[1]);

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
            // Las de "rebote" imitan en Blender la luz que rebota (EEVEE no la calcula). En Unity
            // ese rebote lo da la luz precalculada, y además, sin tamaño, quemarían lo que tienen cerca.
            if (luz.truco == "rebote")
                continue;
            var objeto = new GameObject(luz.nombre);
            objeto.transform.SetParent(padre, false);
            objeto.transform.position = DeBlender(luz.posicion);
            var dir = DeBlender(luz.direccion);
            objeto.transform.rotation = Quaternion.LookRotation(dir, Mathf.Abs(dir.y) > 0.99f ? Vector3.forward : Vector3.up);
            Configurar(objeto.AddComponent<Light>(), luz, e);
        }
    }

    public static void Configurar(Light l, Luz luz, LuzEstado estado)
    {
        var color = Lineal(estado.color);
        l.color = color.gamma; // Unity guarda el color de la luz en sRGB
        l.lightmapBakeType = LightmapBakeType.Realtime;
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
}
