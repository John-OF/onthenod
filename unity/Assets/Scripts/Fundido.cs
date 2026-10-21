using System.Collections;
using UnityEngine;

/// <summary>
/// El corte a negro y la vuelta. Oscurece la imagen del juego en la pantalla PS1 antes de
/// pasarla a 15 bits, así que el fundido sale con el mismo dithering, como en la PS1 (ver
/// Assets/Rendering/PS1Pantalla.shader).
/// </summary>
public static class Fundido
{
    static readonly int Id = Shader.PropertyToID("_PS1Oscuridad");

    /// <summary>0, se ve normal; 1, todo negro.</summary>
    public static float Oscuridad { get; private set; }

    [RuntimeInitializeOnLoadMethod]
    static void AlEmpezar()
    {
        Poner(0f);
        // Que el editor no quede a oscuras si se para el juego en medio de un fundido.
        Application.quitting += () => Poner(0f);
    }

    public static void Poner(float oscuridad)
    {
        Oscuridad = Mathf.Clamp01(oscuridad);
        Shader.SetGlobalFloat(Id, Oscuridad);
    }

    /// <summary>Lleva la oscuridad a <paramref name="destino"/> en <paramref name="duracion"/> segundos.</summary>
    public static IEnumerator A(float destino, float duracion)
    {
        float inicio = Oscuridad;
        for (float t = 0f; t < duracion; t += Time.deltaTime)
        {
            Poner(Mathf.Lerp(inicio, destino, t / duracion));
            yield return null;
        }
        Poner(destino);
    }
}
