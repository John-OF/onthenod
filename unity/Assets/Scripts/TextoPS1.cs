using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// Un texto sobre la imagen del juego, como los letreros de la PS1: la pantalla de guardado del
/// cuaderno («Día 1. No consumí.», al centro) y los pensamientos de Elías (abajo, como
/// subtítulos). Se dibuja en una imagen del mismo tamaño que la del juego (480×270), y la
/// pantalla PS1 (Assets/Rendering/PS1Pantalla.shader) lo pone encima, después del fundido y antes
/// de pasar a 15 bits: sale con los mismos píxeles duros y el mismo dithering, y se lee aunque la
/// pantalla esté a negro. Lleva una sombra de un píxel, para que se lea sobre lo claro.
///
/// Hay un solo texto a la vez. Se escribe con Escribir, que devuelve su turno, y se muestra
/// subiendo la opacidad (A), como el Fundido. Si otro texto lo reemplaza, el A del turno
/// anterior deja de tocar la opacidad.
/// </summary>
public static class TextoPS1
{
    const int Ancho = 480, Alto = 270; // el tamaño de PS1_Imagen
    const int Margen = 24;             // píxeles libres a cada lado antes de cortar la línea
    const int MargenAbajo = 16;        // los subtítulos, desde el borde de abajo

    static readonly int IdTexto = Shader.PropertyToID("_PS1Texto");
    static readonly int IdOpacidad = Shader.PropertyToID("_PS1TextoOpacidad");
    static readonly int IdColor = Shader.PropertyToID("_PS1TextoColor");

    /// <summary>La letra. Sin poner, la que trae Unity.</summary>
    public static Font fuente;
    /// <summary>Alto de la letra, en píxeles de la imagen chica: al centro y abajo.</summary>
    public static int tamano = 16, tamanoAbajo = 12;
    /// <summary>El color de la letra (sRGB).</summary>
    public static Color color = new Color(0.80f, 0.77f, 0.68f);

    /// <summary>0, no se ve; 1, se ve entero.</summary>
    public static float Opacidad { get; private set; }

    /// <summary>El turno del texto que está escrito ahora (sube con cada Escribir).</summary>
    public static int Turno { get; private set; }

    static RenderTexture imagen;
    static Mesh letras, sombra;
    static readonly TextGenerator generador = new TextGenerator();

    [RuntimeInitializeOnLoadMethod]
    static void AlEmpezar()
    {
        Poner(0f);
        Application.quitting += () => Poner(0f);
    }

    public static void Poner(float opacidad)
    {
        Opacidad = Mathf.Clamp01(opacidad);
        Shader.SetGlobalFloat(IdOpacidad, Opacidad);
        Shader.SetGlobalVector(IdColor, color); // como vector, para que Unity no lo pase a lineal
    }

    /// <summary>
    /// Lleva la opacidad a <paramref name="destino"/> en <paramref name="duracion"/> segundos. Con
    /// <paramref name="turno"/>, se detiene si mientras tanto se escribió otro texto.
    /// </summary>
    public static IEnumerator A(float destino, float duracion, int turno = 0)
    {
        float inicio = Opacidad;
        for (float t = 0f; t < duracion; t += Time.deltaTime)
        {
            if (turno != 0 && turno != Turno)
                yield break;
            Poner(Mathf.Lerp(inicio, destino, t / duracion));
            yield return null;
        }
        if (turno == 0 || turno == Turno)
            Poner(destino);
    }

    /// <summary>
    /// Escribe <paramref name="texto"/> al centro de la imagen o, con <paramref name="abajo"/>,
    /// abajo como subtítulo (no cambia la opacidad). Devuelve su turno.
    /// </summary>
    public static int Escribir(string texto, bool abajo = false)
    {
        if (fuente == null)
            fuente = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        if (imagen == null)
        {
            // Solo hace falta saber cuánto tapa la letra en cada píxel (canal rojo) y cuánto su
            // sombra (canal verde)
            imagen = new RenderTexture(Ancho, Alto, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear)
            {
                name = "PS1_Texto",
                filterMode = FilterMode.Point,
            };
            imagen.Create();
            Shader.SetGlobalTexture(IdTexto, imagen);
        }
        if (letras == null)
        {
            letras = new Mesh { name = "PS1_Texto" };
            sombra = new Mesh { name = "PS1_Texto_Sombra" };
        }

        var ajustes = new TextGenerationSettings
        {
            font = fuente,
            fontSize = abajo ? tamanoAbajo : tamano,
            fontStyle = FontStyle.Normal,
            color = Color.white,
            lineSpacing = 1f,
            richText = false,
            scaleFactor = 1f,
            textAnchor = abajo ? TextAnchor.LowerCenter : TextAnchor.MiddleCenter,
            generationExtents = new Vector2(Ancho - 2 * Margen, Alto - 2 * Margen),
            pivot = abajo ? new Vector2(0.5f, 0f) : new Vector2(0.5f, 0.5f),
            horizontalOverflow = HorizontalWrapMode.Wrap,
            verticalOverflow = VerticalWrapMode.Overflow,
            generateOutOfBounds = true,
        };
        generador.Populate(texto, ajustes);

        // El centro de la imagen es el (0, 0); los subtítulos se apoyan cerca del borde de abajo
        var donde = abajo ? new Vector2(0f, -Alto / 2f + MargenAbajo) : Vector2.zero;
        Armar(letras, donde, new Color32(255, 0, 0, 255));
        Armar(sombra, donde + new Vector2(1f, -1f), new Color32(0, 255, 0, 255));

        var dibujo = new CommandBuffer { name = "TextoPS1" };
        dibujo.SetRenderTarget(imagen);
        dibujo.ClearRenderTarget(false, true, Color.clear);
        dibujo.SetViewProjectionMatrices(Matrix4x4.identity,
            Matrix4x4.Ortho(-Ancho / 2f, Ancho / 2f, -Alto / 2f, Alto / 2f, -1f, 1f));
        dibujo.DrawMesh(sombra, Matrix4x4.identity, fuente.material, 0, 0);
        dibujo.DrawMesh(letras, Matrix4x4.identity, fuente.material, 0, 0);
        Graphics.ExecuteCommandBuffer(dibujo);
        dibujo.Release();
        return ++Turno;
    }

    /// <summary>Una caja por letra, corrida <paramref name="donde"/>. Las esquinas van a píxeles enteros para que la letra no se borronee.</summary>
    static void Armar(Mesh malla, Vector2 donde, Color32 canal)
    {
        var verts = generador.verts;
        var vertices = new Vector3[verts.Count];
        var uvs = new Vector2[verts.Count];
        var colores = new Color32[verts.Count];
        var triangulos = new int[verts.Count / 4 * 6];
        for (int i = 0; i < verts.Count; i++)
        {
            var p = verts[i].position;
            vertices[i] = new Vector3(Mathf.Round(p.x + donde.x), Mathf.Round(p.y + donde.y), 0f);
            uvs[i] = verts[i].uv0;
            colores[i] = canal;
        }
        for (int q = 0; q < verts.Count / 4; q++)
        {
            int v = q * 4, t = q * 6;
            triangulos[t] = v; triangulos[t + 1] = v + 1; triangulos[t + 2] = v + 2;
            triangulos[t + 3] = v + 2; triangulos[t + 4] = v + 3; triangulos[t + 5] = v;
        }
        malla.Clear();
        malla.vertices = vertices;
        malla.uv = uvs;
        malla.colors32 = colores;
        malla.triangles = triangulos;
    }
}
