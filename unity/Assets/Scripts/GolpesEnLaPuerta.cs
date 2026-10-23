using System.Collections;
using UnityEngine;

/// <summary>
/// Golpes en la puerta (Noche 1, sección 5): tocan la puerta de entrada varias veces. Por la
/// mirilla no hay nadie. Cuando Elías deja de mirar (o si nunca mira, después del último golpe),
/// una voz detrás de la puerta: «Eli, ábreme». Desde ahí la puerta se puede abrir.
///
/// Va del lado de afuera de la puerta de entrada: de ahí salen los golpes y la voz.
/// </summary>
public class GolpesEnLaPuerta : MonoBehaviour
{
    public AudioClip golpes;
    public AudioClip voz;
    public MirillaInteractiva mirilla;
    public PuertaDeEntrada puerta;

    [Tooltip("Segundos entre una tanda de golpes y la siguiente.")]
    public float entreGolpes = 7f;
    [Tooltip("Cuántas tandas de golpes, como mucho.")]
    public int veces = 5;
    [Tooltip("Cuánto espera la voz después de que Elías deja de mirar.")]
    public float esperaVoz = 1.5f;

    AudioSource afuera;

    void Awake()
    {
        afuera = gameObject.AddComponent<AudioSource>();
        afuera.spatialBlend = 1f;
        afuera.minDistance = 1.5f;
        afuera.maxDistance = 16f;
        afuera.playOnAwake = false;
    }

    public void Empezar() => StartCoroutine(Tocar());

    IEnumerator Tocar()
    {
        bool miro = false;
        mirilla.Miro += () => miro = true;
        for (int n = 0; n < veces && !miro; n++)
        {
            afuera.PlayOneShot(golpes);
            for (float t = 0f; t < entreGolpes && !miro; t += Time.deltaTime)
                yield return null;
        }
        yield return new WaitForSeconds(esperaVoz);
        afuera.PlayOneShot(voz);
        puerta.habilitada = true;
    }
}
