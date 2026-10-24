using System.Collections;
using UnityEngine;

/// <summary>
/// La abstinencia (6.2): un valor oculto de 0 a 100 que nunca se muestra. Sube con el tiempo
/// (más adelante, también con los sustos). Consumir (6.3) la baja a cero y pone el mundo del
/// efecto por un rato; después viene el bajón: vuelve la abstinencia, más alta que antes.
///
/// Se nota en el cuerpo de Elías, cada vez más con el nivel: el temblor de las manos (el peso
/// de la capa del temblor de los brazos), la respiración (más fuerte y más rápida), los latidos
/// (desde un nivel alto), el temblor de la cámara y el sudor (la imagen borrosa en los bordes,
/// con el valor global _PS1Sudor de la pantalla PS1). Bajo el efecto no hay nada de eso: es la
/// mentira de la droga. Va en Elías.
/// </summary>
public class Abstinencia : MonoBehaviour
{
    static readonly int IdSudor = Shader.PropertyToID("_PS1Sudor");

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

    [Header("Respiración y latidos (suenan en la cabeza de Elías)")]
    [Tooltip("Un ciclo de respiración (respiracion): va en bucle.")]
    public AudioClip respiracion;
    [Tooltip("Un latido (latido).")]
    public AudioClip latido;
    [Tooltip("Desde este nivel se oye la respiración; en 100, fuerte y más rápida.")]
    public float respiracionDesde = 25f;
    [Tooltip("Cuántas veces más rápido respira con la abstinencia en 100.")]
    public float respiracionRapida = 1.4f;
    [Range(0f, 1f)] public float volumenRespiracion = 0.45f;
    [Tooltip("Desde este nivel se oyen los latidos.")]
    public float latidosDesde = 55f;
    [Tooltip("Pulsaciones por minuto: cuando se empiezan a oír y con la abstinencia en 100.")]
    public Vector2 pulsaciones = new Vector2(80f, 125f);

    [Header("Sudor")]
    [Tooltip("Desde este nivel la imagen se pone borrosa en los bordes; en 100, del todo.")]
    public float sudorDesde = 60f;

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
    AudioSource aire, corazon;
    Coroutine efecto;

    void Awake()
    {
        aire = gameObject.AddComponent<AudioSource>();
        aire.spatialBlend = 0f;
        aire.loop = true;
        aire.playOnAwake = false;
        aire.volume = 0f;
        corazon = gameObject.AddComponent<AudioSource>();
        corazon.spatialBlend = 0f;
        corazon.playOnAwake = false;
    }

    void Start()
    {
        if (respiracion != null)
        {
            aire.clip = respiracion;
            aire.Play();
        }
        if (latido != null)
            StartCoroutine(Latir());
    }

    void OnDisable() => Shader.SetGlobalFloat(IdSudor, 0f);

    void Update()
    {
        if (!BajoElEfecto)
            nivel = Mathf.Min(100f, nivel + subePorMinuto * Time.deltaTime / 60f);
        elias.brazos.pesoTemblor = BajoElEfecto ? 0f : Mathf.InverseLerp(manosDesde, manosEntero, nivel);
        elias.temblorCamara = BajoElEfecto ? 0f : camaraMaxima * Mathf.InverseLerp(camaraDesde, 100f, nivel);

        // La respiración cambia de a poco (por ejemplo, al empezar el efecto se va calmando)
        float r = BajoElEfecto ? 0f : Mathf.InverseLerp(respiracionDesde, 100f, nivel);
        aire.volume = Mathf.MoveTowards(aire.volume, volumenRespiracion * r, 0.1f * Time.deltaTime);
        aire.pitch = Mathf.MoveTowards(aire.pitch, Mathf.Lerp(1f, respiracionRapida, r), 0.2f * Time.deltaTime);
        Shader.SetGlobalFloat(IdSudor, BajoElEfecto ? 0f : Mathf.InverseLerp(sudorDesde, 100f, nivel));
    }

    /// <summary>Los latidos: desde latidosDesde, cada vez más fuertes y más seguidos.</summary>
    IEnumerator Latir()
    {
        while (true)
        {
            float u = BajoElEfecto ? 0f : Mathf.InverseLerp(latidosDesde, 100f, nivel);
            if (u > 0f)
                corazon.PlayOneShot(latido, Mathf.Lerp(0.25f, 0.85f, u));
            yield return new WaitForSeconds(60f / Mathf.Lerp(pulsaciones.x, pulsaciones.y, u));
        }
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
        if (efecto != null)
            StopCoroutine(efecto);
        efecto = StartCoroutine(Efecto());
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
