using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// La mirilla de la puerta de entrada del 4B: Elías se acerca, mira por ella (VistaMirilla) hasta
/// que se vuelve a apretar Interactuar, y se aparta. En la Noche 1, cuando tocan, por la mirilla
/// no hay nadie (sección 5).
///
/// Va en la mirilla (una pieza de la puerta), con una colisión para que la mirada de Elías la
/// encuentre.
/// </summary>
public class MirillaInteractiva : Interactuable
{
    public VistaMirilla vista;
    [Tooltip("A cuántos metros de la puerta queda el ojo.")]
    public float distancia = 0.05f;

    /// <summary>Avisa cada vez que Elías deja de mirar por la mirilla.</summary>
    public event Action Miro;

    public override bool PuedeUsar(Elias elias) => true;

    public override IEnumerator Usar(Elias elias)
    {
        // El ojo, pegado a la mirilla del lado de adentro, mirando hacia afuera (como la cámara de la vista).
        var afuera = vista.transform.forward;
        var ojo = transform.position - afuera * distancia;
        yield return elias.Acercarse(Matrix4x4.TRS(ojo, Quaternion.LookRotation(afuera, Vector3.up), Vector3.one));
        vista.Encender();
        yield return elias.EsperarInteraccion();
        vista.Apagar();
        Miro?.Invoke();
    }
}
