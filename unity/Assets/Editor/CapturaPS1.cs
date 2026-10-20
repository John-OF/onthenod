using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

/// <summary>
/// On the Nod > Capturar pantalla PS1: guarda en un PNG lo que se ve en el juego, a 1920×1080
/// (la imagen de 480×270 ampliada ×4 sin suavizado), con los 15 bits y el dithering.
/// Sirve para comparar con los renders de Blender, que salen al mismo tamaño.
/// No hace falta darle a Play: dibuja la cámara del juego en ese momento.
/// </summary>
public static class CapturaPS1
{
    const string ShaderPantalla = "OnTheNod/PS1 Pantalla";

    [MenuItem("On the Nod/Capturar pantalla PS1")]
    static void Capturar()
    {
        var ruta = EditorUtility.SaveFilePanel("Guardar la captura", "", "captura_ps1.png", "png");
        if (string.IsNullOrEmpty(ruta) || Guardar(ruta) || !ShaderUtil.anythingCompiling)
            return;

        // Había shaders compilando: se espera a que terminen, sin trabar el editor, y se repite.
        double limite = EditorApplication.timeSinceStartup + 60;
        EditorApplication.CallbackFunction esperar = null;
        esperar = () =>
        {
            if (ShaderUtil.anythingCompiling && EditorApplication.timeSinceStartup < limite)
                return;
            EditorApplication.update -= esperar;
            if (!Guardar(ruta))
                Debug.LogError("Captura PS1: no se pudo guardar; vuelve a intentarlo en unos segundos.");
        };
        EditorApplication.update += esperar;
    }

    /// <summary>
    /// Guarda la captura en <paramref name="ruta"/>. Devuelve false si la escena no tiene pantalla
    /// PS1, o si había shaders compilando: esos objetos no se dibujan y la imagen saldría
    /// incompleta (pasa justo después de cambiar un shader), así que no se guarda.
    /// </summary>
    public static bool Guardar(string ruta, int escala = 4)
    {
        RawImage pantalla = null;
        foreach (var imagen in Object.FindObjectsByType<RawImage>(FindObjectsSortMode.None))
            if (imagen.material != null && imagen.material.shader.name == ShaderPantalla)
                pantalla = imagen;
        var imagenJuego = pantalla != null ? pantalla.texture as RenderTexture : null;
        if (imagenJuego == null)
        {
            Debug.LogError("Captura PS1: la escena no tiene la pantalla PS1 (prefab Assets/Rendering/PS1_Pantalla).");
            return false;
        }

        // Justo después de importar un shader, el primer dibujo sale sin esos objetos (aunque
        // Unity no avise que está compilando): se dibuja dos veces.
        Dibujar(imagenJuego);
        Dibujar(imagenJuego);

        int ancho = imagenJuego.width, alto = imagenJuego.height;
        var final = RenderTexture.GetTemporary(ancho, alto, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
        Graphics.Blit(imagenJuego, final, pantalla.material);

        var anterior = RenderTexture.active;
        RenderTexture.active = final;
        var chica = new Texture2D(ancho, alto, TextureFormat.RGBA32, false, false);
        chica.ReadPixels(new Rect(0, 0, ancho, alto), 0, 0);
        chica.Apply();
        RenderTexture.active = anterior;
        RenderTexture.ReleaseTemporary(final);

        // Leer la imagen obliga a esperar a que se termine de dibujar; recién ahí se sabe si
        // algún shader quedó compilándose (y sus objetos sin dibujar).
        if (ShaderUtil.anythingCompiling)
        {
            Object.DestroyImmediate(chica);
            return false;
        }

        // Ampliación sin suavizado: cada píxel se repite en un bloque de escala × escala.
        var origen = chica.GetPixels32();
        int anchoGrande = ancho * escala, altoGrande = alto * escala;
        var destino = new Color32[anchoGrande * altoGrande];
        for (int y = 0; y < altoGrande; y++)
            for (int x = 0; x < anchoGrande; x++)
            {
                var p = origen[(y / escala) * ancho + x / escala];
                p.a = 255;
                destino[y * anchoGrande + x] = p;
            }

        var grande = new Texture2D(anchoGrande, altoGrande, TextureFormat.RGBA32, false, false);
        grande.SetPixels32(destino);
        grande.Apply();
        File.WriteAllBytes(ruta, grande.EncodeToPNG());
        Object.DestroyImmediate(chica);
        Object.DestroyImmediate(grande);
        Debug.Log($"Captura PS1 guardada en {ruta}");
        return true;
    }

    static void Dibujar(RenderTexture imagenJuego)
    {
        foreach (var camara in Object.FindObjectsByType<Camera>(FindObjectsSortMode.None))
        {
            if (camara.targetTexture != imagenJuego || !camara.isActiveAndEnabled)
                continue;
            var pedido = new RenderPipeline.StandardRequest { destination = imagenJuego };
            if (RenderPipeline.SupportsRenderRequest(camara, pedido))
                RenderPipeline.SubmitRenderRequest(camara, pedido);
            else
                camara.Render();
        }
    }
}
