using System.Collections;
using UnityEngine;

/// <summary>
/// El agua del fregadero de la cocina (Noche 1: «buscar agua», sección 5). Elías toma con la
/// izquierda la taza sucia del fregadero, la pone bajo la llave, abre el agua con la derecha, la
/// cierra, bebe y deja la taza donde estaba (el clip tomar_agua). La manija gira con su pista, el
/// chorro se ve mientras corre el agua y la taza vuelve a su lugar al soltarla.
///
/// Solo en la abstinencia: la taza es parte del deterioro (bajo el efecto no está) y bajo el
/// efecto Elías no tiene sed: es la mentira de la droga.
///
/// Va en la llave del agua, con una colisión que cubre la llave y el fregadero, para que la mirada
/// de Elías la encuentre. Los sonidos salen de Assets/Audio (audio/scripts/sonidos.py).
/// </summary>
public class AguaInteractiva : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public Abstinencia abstinencia;

    [Header("Objetos del 4B")]
    [Tooltip("La taza sucia del fregadero (taza_1): su nombre es el de su pista en el JSON de los brazos.")]
    public Transform taza;
    [Tooltip("La manija en cruz de la llave (llave_agua_manija).")]
    public Transform manija;
    [Tooltip("El chorro de agua (chorro_agua): apagado mientras no corre el agua.")]
    public GameObject chorro;

    [Header("Sonidos")]
    public AudioClip sonidoManija;
    public AudioClip sonidoAgua;
    public AudioClip sonidoTaza;
    [Tooltip("Los tragos: suenan en la cabeza de Elías, no en el fregadero.")]
    public AudioClip sonidoBeber;

    // Cuándo pasa cada cosa en el clip (segundos; ver tomar_agua, AGUA y manija_angulo en
    // brazos_animaciones.py)
    const float Agarra = 1.25f, AbreManija = 2.15f, AguaDesde = 2.45f, CierraManija = 3.95f,
                AguaHasta = 4.20f, Bebe = 5.65f, Deja = 7.45f;

    /// <summary>Si ya tomó agua (para el tutorial de la Noche 1).</summary>
    public bool Bebio { get; private set; }

    AudioSource fregadero, boca;

    void Awake()
    {
        fregadero = gameObject.AddComponent<AudioSource>();
        fregadero.spatialBlend = 1f;
        fregadero.rolloffMode = AudioRolloffMode.Linear;
        fregadero.minDistance = 1f;
        fregadero.maxDistance = 10f;
        fregadero.playOnAwake = false;
        boca = gameObject.AddComponent<AudioSource>();
        boca.spatialBlend = 0f;
        boca.playOnAwake = false;
        chorro.SetActive(false);
    }

    public override bool PuedeUsar(Elias elias) =>
        !abstinencia.BajoElEfecto && taza.gameObject.activeInHierarchy && elias.LlegaAlInicio("tomar_agua", espacio, transform);

    public override IEnumerator Usar(Elias elias)
    {
        float antes = -1f;
        yield return elias.Reproducir("tomar_agua", espacio, true, t =>
        {
            if (Paso(antes, t, Agarra))
                fregadero.PlayOneShot(sonidoTaza, 0.5f);
            if (Paso(antes, t, AbreManija) || Paso(antes, t, CierraManija))
                fregadero.PlayOneShot(sonidoManija);
            if (Paso(antes, t, AguaDesde))
            {
                chorro.SetActive(true);
                fregadero.PlayOneShot(sonidoAgua);
            }
            if (Paso(antes, t, AguaHasta))
                chorro.SetActive(false);
            if (Paso(antes, t, Bebe))
                boca.PlayOneShot(sonidoBeber);
            if (Paso(antes, t, Deja))
                fregadero.PlayOneShot(sonidoTaza);
            antes = t;
        }, (taza.name, taza), (manija.name, manija));
        chorro.SetActive(false);
        Bebio = true;
    }

    /// <summary>Si entre el cuadro anterior y este el clip pasó por <paramref name="momento"/>.</summary>
    static bool Paso(float antes, float ahora, float momento) => antes < momento && ahora >= momento;
}
