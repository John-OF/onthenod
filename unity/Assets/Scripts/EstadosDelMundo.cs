using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Los mundos de un escenario de Blender (sección 10, Las dos versiones del mundo): en el 4B, la
/// abstinencia y el efecto. Pasar de uno a otro es lo que dice el JSON del escenario: qué grupos
/// se ven (Deterioro o Efecto), las texturas sucias o limpias y la emisión de cada material, las
/// luces, el ambiente y la niebla. Cada mundo tiene además su propia luz precalculada (los mapas
/// de luz, la máscara de sombras y las sondas), que calcula On the Nod > Precalcular la luz de
/// los mundos (Assets/Editor/LuzDeLosMundos.cs).
///
/// El primer estado del JSON es el del FBX (en el 4B, la abstinencia): en ese, los materiales son
/// los del modelo tal cual. En los otros se usan copias, para no tocar el modelo.
///
/// Lo cambia la dosis (Abstinencia.Consumir) y, al terminar el efecto, el bajón.
/// </summary>
public class EstadosDelMundo : MonoBehaviour
{
    [Tooltip("El JSON del escenario (por ejemplo, departamento_4b_escena.json).")]
    public TextAsset datos;
    [Tooltip("El escenario en la escena (el FBX).")]
    public Transform modelo;
    [Tooltip("De donde cuelgan las luces creadas desde el JSON.")]
    public Transform luces;
    public NieblaPS1 niebla;
    [Tooltip("Las texturas que nombran los estados (las sucias y las limpias).")]
    public Texture2D[] texturas;

    [Tooltip("La luz precalculada de cada mundo. La llena On the Nod > Precalcular la luz de los mundos.")]
    public List<LuzPrecalculada> precalculadas = new List<LuzPrecalculada>();

    /// <summary>El mundo de ahora.</summary>
    public string Actual { get; private set; }

    /// <summary>Avisa con el nombre del mundo nuevo (por ejemplo, para los brazos de Elías).</summary>
    public event Action<string> Cambio;

    // Que Unity no lo guarde al recompilar: lo restauraría vacío y no se volvería a leer.
    [NonSerialized] EscenaBlender escena;
    readonly Dictionary<Renderer, Material[]> originales = new Dictionary<Renderer, Material[]>();
    readonly Dictionary<Material, Material> copias = new Dictionary<Material, Material>();

    [Serializable]
    public class LuzPrecalculada
    {
        public string estado;
        public Texture2D[] luz;     // un mapa de luz por índice
        public Texture2D[] mascara; // su máscara de sombras
        public LightProbes sondas;
        public Renderer[] renderers;
        public int[] indices;
        public Vector4[] escalas;
        public Light[] luces;
        public SalidaLuz[] salidas;
    }

    /// <summary>Lo que el cálculo de la luz dejó en cada luz (Light.bakingOutput), que cambia de un mundo a otro.</summary>
    [Serializable]
    public struct SalidaLuz
    {
        public bool calculada;
        public LightmapBakeType tipo;
        public MixedLightingMode modo;
        public int canal;
        public int canalSondas;

        public static SalidaLuz De(LightBakingOutput s) => new SalidaLuz
        {
            calculada = s.isBaked, tipo = s.lightmapBakeType, modo = s.mixedLightingMode,
            canal = s.occlusionMaskChannel, canalSondas = s.probeOcclusionLightIndex
        };

        public LightBakingOutput Salida() => new LightBakingOutput
        {
            isBaked = calculada, lightmapBakeType = tipo, mixedLightingMode = modo,
            occlusionMaskChannel = canal, probeOcclusionLightIndex = canalSondas
        };
    }

    EscenaBlender Escena => escena ??= JsonUtility.FromJson<EscenaBlender>(datos.text);

    /// <summary>Los nombres de los mundos, en el orden del JSON: el primero es el del FBX.</summary>
    public string[] Nombres() => Array.ConvertAll(Escena.estados, e => e.nombre);

    void Start() => Poner(Nombres()[0]);

    /// <summary>Pasa al mundo siguiente (en el 4B, de la abstinencia al efecto y de vuelta).</summary>
    public void Alternar()
    {
        var nombres = Nombres();
        Poner(nombres[(Array.IndexOf(nombres, Actual) + 1) % nombres.Length]);
    }

    /// <summary>
    /// Pone el mundo <paramref name="nombre"/>. Sin <paramref name="conLuzPrecalculada"/>, deja la luz
    /// precalculada como está: es para calcularla (LuzDeLosMundos).
    /// </summary>
    public void Poner(string nombre, bool conLuzPrecalculada = true)
    {
        var estado = Escena.BuscarEstado(nombre);
        if (estado == null)
        {
            Debug.LogError($"{name}: el JSON no tiene el estado {nombre}.");
            return;
        }
        bool esDelModelo = nombre == Nombres()[0];

        // Grupos (las colecciones de Blender).
        foreach (Transform grupo in modelo)
            grupo.gameObject.SetActive(Array.IndexOf(estado.colecciones_ocultas, grupo.name) < 0);

        // Materiales: los del modelo, o copias con la textura y la emisión de este estado.
        foreach (var r in modelo.GetComponentsInChildren<Renderer>(true))
        {
            if (!originales.TryGetValue(r, out var mats))
                originales[r] = mats = r.sharedMaterials;
            var nuevos = new Material[mats.Length];
            for (int i = 0; i < mats.Length; i++)
            {
                var m = mats[i];
                var e = esDelModelo || m == null ? null : Array.Find(estado.materiales, x => x.nombre == m.name);
                nuevos[i] = e == null ? m : Copia(m, e);
            }
            r.sharedMaterials = nuevos;
        }

        // Luces: cuáles se ven, con qué color y potencia.
        foreach (var luz in Escena.luces)
        {
            var objeto = luces.Find(luz.nombre);
            var e = Array.Find(estado.luces, x => x.nombre == luz.nombre);
            if (objeto == null || e == null || !objeto.TryGetComponent<Light>(out var l))
                continue;
            l.enabled = e.encendida;
            if (e.encendida)
                EscenaBlender.PonerPotencia(l, luz, e);
        }

        // Ambiente y niebla.
        var colorNiebla = EscenaBlender.AplicarMundo(estado.mundo);
        if (niebla != null)
            niebla.color = colorNiebla;

        // La luz precalculada de este mundo.
        var p = precalculadas.Find(x => x.estado == nombre);
        if (conLuzPrecalculada && p != null)
        {
            var mapas = new LightmapData[p.luz.Length];
            for (int i = 0; i < mapas.Length; i++)
                mapas[i] = new LightmapData { lightmapColor = p.luz[i], shadowMask = p.mascara[i] };
            LightmapSettings.lightmaps = mapas;
            for (int i = 0; i < p.renderers.Length; i++)
                if (p.renderers[i] != null)
                {
                    p.renderers[i].lightmapIndex = p.indices[i];
                    p.renderers[i].lightmapScaleOffset = p.escalas[i];
                }
            if (p.sondas != null)
                LightmapSettings.lightProbes = p.sondas;
            for (int i = 0; i < p.luces.Length; i++)
                if (p.luces[i] != null)
                    p.luces[i].bakingOutput = p.salidas[i].Salida();
        }
        else if (conLuzPrecalculada && precalculadas.Count > 0)
        {
            Debug.LogWarning($"{name}: no hay luz precalculada para {nombre} (On the Nod > Precalcular la luz de los mundos).");
        }

        Actual = nombre;
        Cambio?.Invoke(nombre);
    }

    Material Copia(Material original, EscenaBlender.MaterialEstado e)
    {
        if (!copias.TryGetValue(original, out var copia))
            copias[original] = copia = new Material(original) { name = original.name, hideFlags = HideFlags.DontSave };
        if (!string.IsNullOrEmpty(e.textura))
        {
            var t = Array.Find(texturas, x => x != null && x.name == e.textura);
            if (t != null)
                copia.SetTexture("_BaseMap", t);
            else
                Debug.LogWarning($"{name}: falta la textura {e.textura} en la lista.");
        }
        // Como el importador (ImportadorArte.cs): la emisión lineal, guardada en sRGB.
        var emision = new Color(e.emision[0] * e.fuerza, e.emision[1] * e.fuerza, e.emision[2] * e.fuerza);
        if (emision.maxColorComponent > 0f)
        {
            copia.SetFloat("_Emision", 1f);
            copia.EnableKeyword("_EMISSION");
            copia.SetColor("_EmissionColor", emision.gamma);
            copia.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
        }
        else if (copia.IsKeywordEnabled("_EMISSION"))
        {
            copia.SetFloat("_Emision", 0f);
            copia.DisableKeyword("_EMISSION");
            copia.SetColor("_EmissionColor", Color.black);
        }
        return copia;
    }
}
