using UnityEditor;
using UnityEngine;

/// <summary>
/// On the Nod > Crear máscara de foco: genera Assets/Rendering/Foco_Mascara.cubemap, la máscara
/// (cookie) de las luces de los focos colgantes.
///
/// En Blender, la luz de cada foco está 7 cm por debajo del centro de la bombilla y la bombilla
/// tapa la luz que sale hacia arriba: el techo justo encima del foco queda negro (se ve en
/// blender/renders/pasillo_ps1.png). En Unity la bombilla está demasiado cerca de la luz para
/// proyectar sombra, así que ese cono se corta con esta máscara.
/// </summary>
public static class MascaraFoco
{
    const string Ruta = "Assets/Rendering/Foco_Mascara.cubemap";
    // Mitad del cono que tapa la bombilla, medido desde la vertical. La bombilla es un
    // icosaedro de 5,5 cm de radio a 7 cm de la luz: tapa entre 39° (radio interior) y 52°
    // (radio exterior). 45° es el que mejor coincide con pasillo_ps1.png.
    const float Angulo = 45f;
    const float Borde = 8f; // grados de transición entre la sombra y la luz
    const int Lado = 64;

    [MenuItem("On the Nod/Crear máscara de foco")]
    public static Cubemap Crear()
    {
        float angulo = Angulo;

        var cubo = new Cubemap(Lado, TextureFormat.RGBA32, false)
        {
            name = "Foco_Mascara",
            wrapMode = TextureWrapMode.Clamp,
            filterMode = FilterMode.Bilinear,
        };
        var pixeles = new Color[Lado * Lado];
        for (int cara = 0; cara < 6; cara++)
        {
            for (int y = 0; y < Lado; y++)
                for (int x = 0; x < Lado; x++)
                {
                    var dir = Direccion((CubemapFace)cara, x, y);
                    float desdeArriba = Vector3.Angle(dir, Vector3.up);
                    float valor = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(angulo - Borde * 0.5f, angulo + Borde * 0.5f, desdeArriba));
                    pixeles[y * Lado + x] = new Color(valor, valor, valor, valor);
                }
            cubo.SetPixels(pixeles, (CubemapFace)cara);
        }
        cubo.Apply();

        var existente = AssetDatabase.LoadAssetAtPath<Cubemap>(Ruta);
        if (existente != null)
        {
            EditorUtility.CopySerialized(cubo, existente);
            Object.DestroyImmediate(cubo);
            cubo = existente;
            EditorUtility.SetDirty(cubo);
        }
        else
        {
            AssetDatabase.CreateAsset(cubo, Ruta);
        }
        AssetDatabase.SaveAssets();
        Debug.Log($"Máscara de foco guardada en {Ruta} (cono de {angulo:F1}° hacia arriba).");
        return cubo;
    }

    // Dirección de un píxel de una cara del cubemap (convención de Unity/Direct3D; la fila 0 es la de arriba).
    static Vector3 Direccion(CubemapFace cara, int x, int y)
    {
        float u = (x + 0.5f) / Lado * 2f - 1f;
        float v = (y + 0.5f) / Lado * 2f - 1f;
        switch (cara)
        {
            case CubemapFace.PositiveX: return new Vector3(1f, -v, -u).normalized;
            case CubemapFace.NegativeX: return new Vector3(-1f, -v, u).normalized;
            case CubemapFace.PositiveY: return new Vector3(u, 1f, v).normalized;
            case CubemapFace.NegativeY: return new Vector3(u, -1f, -v).normalized;
            case CubemapFace.PositiveZ: return new Vector3(u, -v, 1f).normalized;
            default: return new Vector3(-u, -v, -1f).normalized;
        }
    }
}
