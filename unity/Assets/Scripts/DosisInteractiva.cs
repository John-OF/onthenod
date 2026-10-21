using System.Collections;
using UnityEngine;

/// <summary>
/// Una dosis (6.3): la jeringa de la mesa de centro del 4B. Elías se agacha, la toma y la mira
/// en la mano (el clip tomar_jeringa); corte a negro; y al volver, el efecto. El consumo nunca se
/// muestra paso a paso. Se usa una sola vez.
///
/// Va en la jeringa (el objeto que agrupa sus piezas), con una colisión para que la mirada de
/// Elías la encuentre. Su nombre es el de su pista en el JSON de los brazos.
/// </summary>
public class DosisInteractiva : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public Abstinencia abstinencia;
    public string clip = "tomar_jeringa";
    public bool usada;

    public override bool PuedeUsar(Elias elias) =>
        !usada && !abstinencia.BajoElEfecto && elias.LlegaAlInicio(clip, espacio, transform);

    public override IEnumerator Usar(Elias elias)
    {
        yield return elias.Reproducir(clip, espacio, false, (name, transform));
        yield return new WaitForSeconds(0.6f); // la jeringa en la mano
        yield return Fundido.A(1f, 0.4f);

        // A oscuras: la jeringa vuelve a la mesa, Elías se para y empieza el efecto.
        usada = true;
        elias.DevolverAlReposo(transform);
        elias.brazos.Reposo();
        elias.Pararse();
        abstinencia.Consumir();
        yield return new WaitForSeconds(1.5f);
        yield return Fundido.A(0f, 2f);
    }
}
