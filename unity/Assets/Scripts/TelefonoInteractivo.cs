using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// El teléfono del 4B (6.5). Puede sonar (Sonar); Elías contesta (levanta el auricular y se lo
/// lleva a la oreja), escucha hasta que se vuelve a apretar Interactuar, y cuelga. Al contestar
/// queda mirando hacia el pasillo y la puerta del baño, como en Blender. En la Noche 1, al
/// contestar solo hay estática. Si suena y nadie contesta, es una llamada perdida: las dos
/// cosas cuentan para el final (Partida).
///
/// Va en la base del teléfono, con una colisión para que la mirada de Elías lo encuentre.
/// Los sonidos salen de Assets/Audio (audio/scripts/sonidos.py).
/// </summary>
public class TelefonoInteractivo : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas de los clips están en sus coordenadas.")]
    public Transform espacio;
    [Tooltip("El auricular: su nombre es el de su pista en el JSON de los brazos.")]
    public Transform auricular;

    [Header("Sonidos")]
    public AudioClip timbre;
    public AudioClip descolgar;
    public AudioClip colgar;
    [Tooltip("Lo que se oye en la oreja al contestar (en la Noche 1, la estática).")]
    public AudioClip linea;

    [Tooltip("Cuántas veces suena antes de cortarse.")]
    public int vueltas = 8;

    /// <summary>Si está sonando ahora.</summary>
    public bool Sonando { get; private set; }

    /// <summary>Avisa al terminar una llamada: true si la contestó, false si la dejó sonar.</summary>
    public event Action<bool> Termino;

    // Cuándo la mano agarra y suelta el auricular en cada clip (segundos, ver brazos_animaciones.py).
    const float AgarraAlContestar = 0.75f, SueltaAlColgar = 0.95f;

    AudioSource parlante, oreja;
    bool llamadaEnCurso;

    void Awake()
    {
        // El timbre y los golpes del auricular salen del teléfono; la línea, de la oreja.
        parlante = gameObject.AddComponent<AudioSource>();
        parlante.spatialBlend = 1f;
        parlante.rolloffMode = AudioRolloffMode.Linear;
        parlante.minDistance = 1f;
        parlante.maxDistance = 14f;
        parlante.playOnAwake = false;
        oreja = gameObject.AddComponent<AudioSource>();
        oreja.spatialBlend = 0f;
        oreja.loop = true;
        oreja.volume = 0.45f;
        oreja.playOnAwake = false;
    }

    /// <summary>Empieza a sonar. Si nadie contesta en <see cref="vueltas"/> timbres, se corta.</summary>
    public void Sonar()
    {
        if (Sonando)
            return;
        Sonando = true;
        llamadaEnCurso = true;
        parlante.clip = timbre;
        parlante.loop = true;
        parlante.Play();
        StartCoroutine(Cortarse());
    }

    IEnumerator Cortarse()
    {
        // El clip del timbre es un ciclo entero: suena y calla.
        yield return new WaitForSeconds(timbre.length * vueltas);
        if (!Sonando)
            yield break;
        Sonando = false;
        parlante.Stop();
        llamadaEnCurso = false;
        Partida.Llamada(false);
        Termino?.Invoke(false);
    }

    public override bool PuedeUsar(Elias elias) => elias.LlegaAlInicio("telefono_contestar", espacio, transform);

    public override IEnumerator Usar(Elias elias)
    {
        bool contesta = Sonando;
        bool agarro = false, solto = false;
        yield return elias.Reproducir("telefono_contestar", espacio, false, t =>
        {
            if (agarro || t < AgarraAlContestar)
                return;
            agarro = true;
            if (Sonando)
            {
                Sonando = false;
                parlante.Stop();
            }
            parlante.PlayOneShot(descolgar);
        }, (auricular.name, auricular));
        oreja.clip = linea;
        oreja.Play();

        yield return elias.EsperarInteraccion();

        yield return elias.Reproducir("telefono_colgar", espacio, true, t =>
        {
            if (!solto && t >= SueltaAlColgar * 0.8f)
                oreja.Stop(); // se aparta de la oreja
            if (solto || t < SueltaAlColgar)
                return;
            solto = true;
            parlante.PlayOneShot(colgar);
        }, (auricular.name, auricular));

        if (contesta && llamadaEnCurso)
        {
            llamadaEnCurso = false;
            Partida.Llamada(true);
            Termino?.Invoke(true);
        }
    }
}
