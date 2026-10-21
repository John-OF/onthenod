using System.Collections;
using UnityEngine;

/// <summary>
/// La abstinencia (6.2): un valor oculto de 0 a 100 que nunca se muestra. Sube con el tiempo
/// (más adelante, también con los sustos). Consumir (6.3) la baja a cero y pone el mundo del
/// efecto por un rato; después viene el bajón: vuelve la abstinencia, más alta que antes.
///
/// Por ahora se nota en el temblor de las manos (el peso de la capa del temblor de los brazos)
/// y, con el nivel alto, en un temblor leve de la cámara. Bajo el efecto no hay temblor: es la
/// mentira de la droga. Va en Elías.
/// </summary>
public class Abstinencia : MonoBehaviour
{
    [Tooltip("De 0 a 100. La Noche 1 es el primer día sin consumir.")]
    [Range(0f, 100f)] public float nivel = 35f;
    [Tooltip("Cuánto sube por minuto mientras no consume.")]
    public float subePorMinuto = 1.5f;

    [Header("Temblor")]
    [Tooltip("Por debajo de este nivel, las manos no tiemblan.")]
    public float manosDesde = 10f;
    [Tooltip("Desde este nivel, las manos tiemblan como en las vistas previas de Blender.")]
    public float manosEntero = 60f;
    [Tooltip("Desde este nivel tiembla también la cámara.")]
    public float camaraDesde = 70f;
    [Tooltip("Cuánto tiembla la cámara con la abstinencia en 100, en grados.")]
    public float camaraMaxima = 0.6f;

    [Header("La dosis")]
    [Tooltip("Cuántos segundos dura el efecto.")]
    public float duracionEfecto = 180f;
    [Tooltip("Cuánto más alta que antes de consumir vuelve la abstinencia en el bajón.")]
    public float bajon = 15f;

    [Header("Partes")]
    public Elias elias;
    public EstadosDelMundo mundo;

    /// <summary>Si está bajo el efecto de una dosis.</summary>
    public bool BajoElEfecto { get; private set; }

    float antesDeConsumir;

    void Update()
    {
        if (!BajoElEfecto)
            nivel = Mathf.Min(100f, nivel + subePorMinuto * Time.deltaTime / 60f);
        elias.brazos.pesoTemblor = BajoElEfecto ? 0f : Mathf.InverseLerp(manosDesde, manosEntero, nivel);
        elias.temblorCamara = BajoElEfecto ? 0f : camaraMaxima * Mathf.InverseLerp(camaraDesde, 100f, nivel);
    }

    /// <summary>
    /// La dosis: la abstinencia baja a cero, el mundo pasa al efecto y, al terminar el efecto,
    /// viene el bajón. Lo llama la dosis (DosisInteractiva) con la pantalla a oscuras.
    /// </summary>
    public void Consumir()
    {
        antesDeConsumir = nivel;
        nivel = 0f;
        BajoElEfecto = true;
        Partida.Consumio();
        mundo.Poner("efecto");
        StopAllCoroutines();
        StartCoroutine(Efecto());
    }

    IEnumerator Efecto()
    {
        yield return new WaitForSeconds(duracionEfecto);
        // El bajón: de golpe, sin aviso.
        yield return Fundido.A(1f, 0.25f);
        BajoElEfecto = false;
        nivel = Mathf.Min(100f, antesDeConsumir + bajon);
        mundo.Poner(mundo.Nombres()[0]);
        yield return new WaitForSeconds(0.5f);
        yield return Fundido.A(0f, 0.8f);
    }
}
