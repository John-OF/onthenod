using System.Collections;
using UnityEngine;

/// <summary>
/// Golpes en la puerta (Noche 1, sección 5): tocan la puerta de entrada varias veces. Por la
/// mirilla no hay nadie, pero bajo la puerta, la luz del pasillo se corta en dos sombras: unos
/// pies. Cuando Elías deja de mirar (o si nunca mira, después del último golpe), una voz detrás
/// de la puerta: «Eli, ábreme». Desde ahí la puerta se puede abrir.
///
/// Las sombras de los pies vienen hechas del 4B (la luz bajo la puerta está precalculada y los
/// pies no la tapan): aparecen un poco antes del primer golpe y se quedan hasta el final de la
/// noche, solo en la abstinencia (bajo el efecto no entra luz bajo la puerta). Los pies no se
/// muestran: se verían por la mirilla.
///
/// Va del lado de afuera de la puerta de entrada: de ahí salen los golpes y la voz.
/// </summary>
public class GolpesEnLaPuerta : MonoBehaviour
{
    public AudioClip golpes;
    public AudioClip voz;
    public MirillaInteractiva mirilla;
    public PuertaDeEntrada puerta;

    [Header("Los pies bajo la puerta")]
    [Tooltip("sombra_pie_izq y sombra_pie_der, del grupo Eventos del 4B.")]
    public GameObject[] sombras;
    [Tooltip("pie_izq y pie_der: los pies que hacen las sombras en Blender. En Unity no se muestran.")]
    public GameObject[] pies;
    [Tooltip("Los mundos: bajo el efecto no hay sombras.")]
    public EstadosDelMundo mundo;
    [Tooltip("Cuántos segundos antes del primer golpe aparecen las sombras (alguien llega).")]
    public float llegada = 1.5f;

    [Tooltip("Segundos entre una tanda de golpes y la siguiente.")]
    public float entreGolpes = 7f;
    [Tooltip("Cuántas tandas de golpes, como mucho.")]
    public int veces = 5;
    [Tooltip("Cuánto espera la voz después de que Elías deja de mirar.")]
    public float esperaVoz = 1.5f;

    AudioSource afuera;
    bool alguien; // hay alguien detrás de la puerta: desde que llega hasta el final de la noche

    void Awake()
    {
        afuera = gameObject.AddComponent<AudioSource>();
        afuera.spatialBlend = 1f;
        afuera.minDistance = 1.5f;
        afuera.maxDistance = 16f;
        afuera.playOnAwake = false;
    }

    void OnEnable()
    {
        if (mundo != null)
            mundo.Cambio += AlCambiarDeMundo;
    }

    void OnDisable()
    {
        if (mundo != null)
            mundo.Cambio -= AlCambiarDeMundo;
    }

    void AlCambiarDeMundo(string nuevo)
    {
        if (alguien)
            Sombras();
    }

    /// <summary>
    /// Muestra las sombras si hay alguien y Elías está en la abstinencia. Su grupo (Eventos) está
    /// oculto en los dos mundos: se prende, pero con los pies apagados.
    /// </summary>
    void Sombras()
    {
        if (sombras == null || sombras.Length == 0)
            return;
        bool ver = alguien && (mundo == null || string.IsNullOrEmpty(mundo.Actual) || mundo.Actual == mundo.Nombres()[0]);
        foreach (var pie in pies)
            pie.SetActive(false);
        foreach (var sombra in sombras)
            sombra.SetActive(true);
        sombras[0].transform.parent.gameObject.SetActive(ver);
    }

    public void Empezar() => StartCoroutine(Tocar());

    IEnumerator Tocar()
    {
        alguien = true;
        Sombras();
        yield return new WaitForSeconds(llegada);

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
