using System.Collections;
using UnityEngine;

/// <summary>
/// Una puerta que Elías abre con un clip de sus brazos: abrir_puerta (agarra la perilla, la gira
/// y empuja; para una puerta cerrada) o empujar_puerta (apoya la mano en la perilla y empuja;
/// para la puerta del dormitorio, que está entreabierta). Después queda abierta. Va en la puerta
/// (el objeto con el origen en la bisagra), y su nombre es el de su pista en el JSON de los brazos.
///
/// Por ahora los clips están hechos para la puerta del dormitorio del 4B y desde el pasillo: desde
/// el dormitorio no se puede abrir (Elias.LlegaAlInicio).
/// </summary>
public class PuertaInteractiva : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public string clip = "abrir_puerta";
    public bool abierta;

    void Awake()
    {
        // Para que su colisión se mueva con ella al abrirse.
        if (!TryGetComponent<Rigidbody>(out var cuerpo))
            cuerpo = gameObject.AddComponent<Rigidbody>();
        cuerpo.isKinematic = true;
    }

    public override bool PuedeUsar(Elias elias) => !abierta && elias.LlegaAlInicio(clip, espacio, transform);

    public override IEnumerator Usar(Elias elias)
    {
        yield return elias.Reproducir(clip, espacio, true, (name, transform));
        abierta = true;
    }
}
