using System.Collections;
using UnityEngine;

/// <summary>
/// Una puerta que Elías abre con un clip de sus brazos: abrir_puerta (agarra la perilla, la gira
/// y empuja; para una puerta cerrada) o empujar_puerta (apoya la mano en la perilla y empuja;
/// para una entreabierta). Después queda abierta. Va en la puerta (el objeto con el origen en la
/// bisagra).
///
/// Los dos clips se hicieron con la puerta del dormitorio del 4B, desde el pasillo: desde el
/// dormitorio no se puede abrir (Elias.LlegaAlInicio). Para otra puerta (las del pasillo del 4º
/// piso), el clip se lleva a esta: la bisagra del clip a la de esta, girada lo que diga giro. Sirve
/// si la puerta es como la del dormitorio: se abre empujando, con la bisagra a la derecha de Elías
/// y la perilla a 69 cm de la bisagra (PERILLA_CLIP en pasillo_piso4.py). Esas solo se abren desde
/// ese lado.
/// </summary>
public class PuertaInteractiva : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public string clip = "abrir_puerta";
    public bool abierta;

    [Header("Otra puerta con el clip de la del dormitorio")]
    [Tooltip("La pista de la puerta en el clip (puerta_dormitorio). Vacío: la de este objeto, que es la del clip.")]
    public string pista;
    [Tooltip("Cuánto se gira la puerta del clip alrededor del eje vertical de Blender, en grados, para que quede " +
             "como esta: 90 si la del dormitorio cierra hacia -Y y esta hacia +X.")]
    public float giro;

    [Tooltip("Ponerle una caja que la cubre entera: en una puerta de celosía, la mirada de Elías pasa entre las tablillas.")]
    public bool cubrir;

    bool Llevada => !string.IsNullOrEmpty(pista);

    void Awake()
    {
        // Para que su colisión se mueva con ella al abrirse.
        if (!TryGetComponent<Rigidbody>(out var cuerpo))
            cuerpo = gameObject.AddComponent<Rigidbody>();
        cuerpo.isKinematic = true;
        if (cubrir && TryGetComponent<MeshFilter>(out var malla) && malla.sharedMesh != null)
        {
            var caja = gameObject.AddComponent<BoxCollider>();
            caja.center = malla.sharedMesh.bounds.center;
            caja.size = malla.sharedMesh.bounds.size;
        }
    }

    /// <summary>Lleva el clip de la puerta del dormitorio a esta: de bisagra a bisagra, girado.</summary>
    Matrix4x4 Reubicar(Elias elias)
    {
        if (!Llevada)
            return Matrix4x4.identity;
        var delClip = elias.ReposoDePista(clip, pista).GetPosition();
        var aqui = espacio.InverseTransformPoint(transform.position);
        // Un giro de Blender alrededor de Z es uno de Unity alrededor de Y con el signo cambiado.
        return Matrix4x4.Translate(aqui) * Matrix4x4.Rotate(Quaternion.Euler(0f, -giro, 0f)) * Matrix4x4.Translate(-delClip);
    }

    public override bool PuedeUsar(Elias elias)
    {
        if (abierta)
            return false;
        var reubicar = Reubicar(elias);
        if (!elias.LlegaAlInicio(clip, espacio, transform, reubicar))
            return false;
        if (!Llevada)
            return true;
        // Solo desde el lado del clip: para llegar a donde empieza, no se atraviesa la puerta.
        var inicio = (espacio.localToWorldMatrix * reubicar * elias.CabezaAlEmpezar(clip)).GetPosition();
        return !(Physics.Linecast(elias.camara.position, inicio, out var golpe, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)
                 && golpe.collider.transform.IsChildOf(transform));
    }

    public override IEnumerator Usar(Elias elias)
    {
        var opciones = new Elias.OpcionesClip { reubicar = Reubicar(elias), desdeElInicio = Llevada };
        yield return elias.Reproducir(clip, espacio, true, opciones, (Llevada ? pista : name, transform));
        abierta = true;
    }
}
