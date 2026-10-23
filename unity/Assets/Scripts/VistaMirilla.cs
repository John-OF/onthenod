using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// La vista por la mirilla (sección 10, Doña Carmen): una cámara muy abierta (170°) del lado del
/// pasillo, cuya imagen pasa por el shader de ojo de pez (OnTheNod/Mirilla) a la imagen del juego
/// de 480×270. Mientras se mira, la cámara del juego no dibuja.
///
/// Va en una cámara apagada, en la cara de afuera de la puerta, a la altura de la mirilla y
/// mirando hacia el pasillo.
/// </summary>
[RequireComponent(typeof(Camera))]
public class VistaMirilla : MonoBehaviour
{
    [Tooltip("La cámara del juego (la de Elías).")]
    public Camera juego;
    [Tooltip("Lo que dibuja la cámara del juego: PS1_Imagen.")]
    public RenderTexture imagen;
    [Tooltip("Material con el shader OnTheNod/Mirilla.")]
    public Material ojoDePez;
    [Tooltip("Lado de la imagen cuadrada que se dibuja antes del ojo de pez: el centro del círculo usa una parte chica.")]
    public int resolucion = 1536;

    Camera vista;
    RenderTexture cuadrada;

    void Awake()
    {
        vista = GetComponent<Camera>();
        vista.enabled = false;
    }

    public void Encender()
    {
        cuadrada = new RenderTexture(resolucion, resolucion, 24) { name = "Mirilla" };
        vista.targetTexture = cuadrada;
        vista.fieldOfView = 170f;
        vista.aspect = 1f;
        vista.enabled = true;
        juego.enabled = false;
        RenderPipelineManager.endCameraRendering += Pasar;
    }

    public void Apagar()
    {
        RenderPipelineManager.endCameraRendering -= Pasar;
        vista.enabled = false;
        vista.targetTexture = null;
        juego.enabled = true;
        if (cuadrada != null)
        {
            cuadrada.Release();
            Destroy(cuadrada);
        }
    }

    void OnDisable()
    {
        if (vista != null && vista.enabled)
            Apagar();
    }

    void Pasar(ScriptableRenderContext contexto, Camera camara)
    {
        if (camara != vista)
            return;
        // El tamaño de la imagen de destino: acá _ScreenParams es el de la cámara de la mirilla.
        ojoDePez.SetVector("_Destino", new Vector4(imagen.width, imagen.height, 0f, 0f));
        Graphics.Blit(cuadrada, imagen, ojoDePez);
    }
}
