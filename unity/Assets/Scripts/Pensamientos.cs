using System.Collections;
using UnityEngine;

/// <summary>
/// Lo que piensa Elías: una frase corta abajo en la pantalla, como un subtítulo (con TextoPS1).
/// Guía al jugador sin indicadores (6.9): en la Noche 1, el tutorial (ver NocheUno). Por ahora
/// solo se lee; cuando haya voz, la frase sonará con ella.
///
/// Espera a que Elías esté libre y la pantalla no esté a oscuras: no aparece en medio de un
/// corte a negro ni de la pantalla de guardado. Va en un objeto de la escena (el de la Noche 1).
/// </summary>
public class Pensamientos : MonoBehaviour
{
    public Elias elias;
    [Tooltip("Cuántos segundos queda la frase en pantalla.")]
    public float duracion = 4f;

    Coroutine actual;

    /// <summary>Muestra <paramref name="texto"/> (si había otra frase, la reemplaza).</summary>
    public void Pensar(string texto)
    {
        if (actual != null)
            StopCoroutine(actual);
        actual = StartCoroutine(Decir(texto));
    }

    IEnumerator Decir(string texto)
    {
        while (!elias.Libre || Fundido.Oscuridad > 0f)
            yield return null;
        int turno = TextoPS1.Escribir(texto, abajo: true);
        yield return TextoPS1.A(1f, 0.4f, turno);
        yield return new WaitForSeconds(duracion);
        yield return TextoPS1.A(0f, 0.8f, turno);
        actual = null;
    }
}
