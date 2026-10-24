using System;
using System.Collections;
using UnityEngine;
using Random = UnityEngine.Random;

/// <summary>
/// El ambiente del 4B (sección 11): la ciudad de noche de fondo, el zumbido del fluorescente de
/// la cocina y, de vez en cuando, algo del edificio: las cañerías, un golpe en el departamento
/// de arriba, los vecinos a través de la pared. El zumbido y los ruidos del edificio son de la
/// abstinencia: bajo el efecto se callan y queda la ciudad.
///
/// Va en un objeto de la escena. Los lugares están en coordenadas de Unity, relativas a la raíz
/// del 4B (espacio). Los sonidos salen de Assets/Audio (audio/scripts/sonidos.py).
/// </summary>
public class AmbienteSonoro : MonoBehaviour
{
    [Tooltip("La raíz del 4B: los lugares de los sonidos están en sus coordenadas.")]
    public Transform espacio;
    public EstadosDelMundo mundo;

    [Header("De fondo")]
    public AudioClip ciudad;
    [Range(0f, 1f)] public float volumenCiudad = 0.25f;

    [Header("El fluorescente de la cocina")]
    public AudioClip zumbido;
    [Tooltip("Dónde está el tubo.")]
    public Vector3 fluorescente = new Vector3(6.0f, 2.53f, 2.1f);
    [Range(0f, 1f)] public float volumenZumbido = 0.35f;

    /// <summary>Un ruido del edificio y de dónde sale.</summary>
    [Serializable]
    public class Suelto
    {
        public AudioClip sonido;
        public Vector3 lugar;
        [Range(0f, 1f)] public float volumen = 0.6f;
    }

    [Header("Los ruidos del edificio, de vez en cuando")]
    public Suelto[] sueltos;
    [Tooltip("Segundos entre uno y otro: al azar entre los dos.")]
    public Vector2 entreSueltos = new Vector2(25f, 70f);

    AudioSource fondo, tubo, edificio;
    int anterior = -1;

    bool EnLaAbstinencia => mundo == null || string.IsNullOrEmpty(mundo.Actual) || mundo.Actual == mundo.Nombres()[0];

    void Start()
    {
        fondo = Fuente("Ciudad", Vector3.zero, false);
        fondo.clip = ciudad;
        fondo.loop = true;
        fondo.volume = volumenCiudad;
        fondo.Play();

        tubo = Fuente("Fluorescente", fluorescente, true, 0.5f, 7f);
        tubo.clip = zumbido;
        tubo.loop = true;
        tubo.volume = volumenZumbido;
        tubo.Play();

        edificio = Fuente("Edificio", Vector3.zero, true, 1f, 15f);
        StartCoroutine(DeVezEnCuando());
    }

    AudioSource Fuente(string nombre, Vector3 lugar, bool enElEspacio, float cerca = 1f, float lejos = 10f)
    {
        var objeto = new GameObject(nombre);
        objeto.transform.SetParent(transform, false);
        objeto.transform.position = espacio.TransformPoint(lugar);
        var fuente = objeto.AddComponent<AudioSource>();
        fuente.playOnAwake = false;
        fuente.spatialBlend = enElEspacio ? 1f : 0f;
        fuente.rolloffMode = AudioRolloffMode.Linear;
        fuente.minDistance = cerca;
        fuente.maxDistance = lejos;
        return fuente;
    }

    void Update()
    {
        // El zumbido se apaga despacio bajo el efecto y vuelve con el bajón
        tubo.volume = Mathf.MoveTowards(tubo.volume, EnLaAbstinencia ? volumenZumbido : 0f, 0.5f * Time.deltaTime);
    }

    IEnumerator DeVezEnCuando()
    {
        while (true)
        {
            yield return new WaitForSeconds(Random.Range(entreSueltos.x, entreSueltos.y));
            if (!EnLaAbstinencia || sueltos == null || sueltos.Length == 0)
                continue;
            // Al azar, pero no el mismo dos veces seguidas
            int i = Random.Range(0, sueltos.Length);
            if (i == anterior && sueltos.Length > 1)
                i = (i + 1) % sueltos.Length;
            anterior = i;
            edificio.transform.position = espacio.TransformPoint(sueltos[i].lugar);
            edificio.PlayOneShot(sueltos[i].sonido, sueltos[i].volumen);
        }
    }
}
