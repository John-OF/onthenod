using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// On the Nod > Precalcular la luz de los mundos: calcula la luz precalculada de cada mundo de la
/// escena abierta (el componente EstadosDelMundo; en el 4B, la abstinencia y el efecto) y la
/// guarda en el componente, para que el juego la cambie junto con el mundo.
///
/// Calcula primero los otros mundos y al final el del FBX (el primero del JSON), que queda como
/// la luz normal de la escena (Assets/Scenes/&lt;escena&gt;/). La de los otros se copia a una
/// carpeta con su nombre (Assets/Scenes/&lt;escena&gt;/&lt;mundo&gt;/), porque el cálculo siguiente
/// pisa los archivos. Tarda unos 20 segundos por mundo; mientras, el editor sigue respondiendo.
/// Al terminar guarda la escena.
/// </summary>
public static class LuzDeLosMundos
{
    static EstadosDelMundo mundo;
    static string[] orden;
    static int paso;

    [MenuItem("On the Nod/Precalcular la luz de los mundos")]
    static void DesdeElMenu() => Debug.Log(Empezar());

    /// <summary>Empieza el cálculo y vuelve enseguida: avisa en la consola al terminar.</summary>
    public static string Empezar()
    {
        if (Lightmapping.isRunning)
            return "Ya se está precalculando la luz.";
        // El escenario con luz precalculada (el 4B); el pasillo del 4º piso tiene sus propios mundos, sin ella.
        mundo = Object.FindObjectsByType<EstadosDelMundo>(FindObjectsSortMode.None).FirstOrDefault(m => m.tieneLuzPrecalculada);
        if (mundo == null)
            return "La escena abierta no tiene un EstadosDelMundo con luz precalculada.";
        var nombres = mundo.Nombres();
        orden = nombres.Skip(1).Append(nombres[0]).ToArray(); // el del FBX, al final
        paso = 0;
        mundo.precalculadas.Clear();
        Calcular();
        return "Precalculando la luz de: " + string.Join(", ", orden);
    }

    static void Calcular()
    {
        mundo.Poner(orden[paso], false);
        Lightmapping.bakeCompleted += Terminado;
        if (!Lightmapping.BakeAsync())
        {
            Lightmapping.bakeCompleted -= Terminado;
            mundo.Poner(orden[orden.Length - 1], false);
            Debug.LogError("No se pudo empezar a precalcular la luz.");
        }
    }

    static void Terminado()
    {
        Lightmapping.bakeCompleted -= Terminado;
        bool ultimo = paso == orden.Length - 1;
        mundo.precalculadas.Add(Guardar(orden[paso], copiar: !ultimo));
        Debug.Log($"Luz precalculada: {orden[paso]}");
        paso++;
        if (!ultimo)
        {
            Calcular();
            return;
        }
        // Queda puesto el mundo del FBX, con su luz.
        mundo.Poner(orden[orden.Length - 1]);
        EditorUtility.SetDirty(mundo);
        var escena = mundo.gameObject.scene;
        EditorSceneManager.MarkSceneDirty(escena);
        EditorSceneManager.SaveScene(escena);
        Debug.Log("Luz de los mundos lista: " + string.Join(", ", orden));
    }

    static EstadosDelMundo.LuzPrecalculada Guardar(string estado, bool copiar)
    {
        var escena = mundo.gameObject.scene.path;
        var carpeta = Path.Combine(Path.GetDirectoryName(escena), Path.GetFileNameWithoutExtension(escena), estado).Replace('\\', '/');
        if (copiar)
        {
            AssetDatabase.DeleteAsset(carpeta);
            Directory.CreateDirectory(carpeta);
            AssetDatabase.Refresh();
        }

        var mapas = LightmapSettings.lightmaps;
        var d = new EstadosDelMundo.LuzPrecalculada
        {
            estado = estado,
            luz = mapas.Select(m => copiar ? Copiar(m.lightmapColor, carpeta) : m.lightmapColor).ToArray(),
            mascara = mapas.Select(m => copiar ? Copiar(m.shadowMask, carpeta) : m.shadowMask).ToArray(),
        };

        var sondas = LightmapSettings.lightProbes;
        if (sondas != null && copiar)
        {
            var copia = Object.Instantiate(sondas);
            AssetDatabase.CreateAsset(copia, carpeta + "/Sondas.asset");
            sondas = copia;
        }
        d.sondas = sondas;

        // Todo lo de la escena, no solo el escenario de los mundos: lo que está alrededor (el
        // pasillo afuera del 4B) también cambia de mapa de luz entre un cálculo y otro.
        var renderers = Object.FindObjectsByType<Renderer>(FindObjectsInactive.Include, FindObjectsSortMode.None)
            .Where(r => r.gameObject.scene == mundo.gameObject.scene).ToArray();
        d.renderers = renderers;
        d.indices = renderers.Select(r => r.lightmapIndex).ToArray();
        d.escalas = renderers.Select(r => r.lightmapScaleOffset).ToArray();

        var luces = Object.FindObjectsByType<Light>(FindObjectsInactive.Include, FindObjectsSortMode.None)
            .Where(l => l.gameObject.scene == mundo.gameObject.scene).ToArray();
        d.luces = luces;
        d.salidas = luces.Select(l => EstadosDelMundo.SalidaLuz.De(l.bakingOutput)).ToArray();
        return d;
    }

    static Texture2D Copiar(Texture2D textura, string carpeta)
    {
        if (textura == null)
            return null;
        var origen = AssetDatabase.GetAssetPath(textura);
        var destino = carpeta + "/" + Path.GetFileName(origen);
        AssetDatabase.CopyAsset(origen, destino);
        return AssetDatabase.LoadAssetAtPath<Texture2D>(destino);
    }
}
