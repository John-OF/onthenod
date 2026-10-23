using System.Collections;
using UnityEngine;

/// <summary>
/// Una dosis (6.3). La de la Noche 1 es la que Elías escondió de sí mismo bajo el colchón del
/// dormitorio, envuelta en una media (sección 5): por el costado del colchón asoma la punta.
/// Elías se arrodilla, la saca y la mira en la mano (el clip sacar_dosis); corte a negro; y al
/// volver, el efecto. El consumo nunca se muestra paso a paso. Se usa una sola vez: a oscuras,
/// la dosis desaparece.
///
/// Va en la dosis (el objeto que agrupa sus piezas), con una colisión para que la mirada de
/// Elías la encuentre. Su nombre es el de su pista en el JSON de los brazos.
/// </summary>
public class DosisInteractiva : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public Abstinencia abstinencia;
    [Tooltip("El clip de los brazos: sacar_dosis (bajo el colchón) o tomar_jeringa (sobre la mesa de centro).")]
    public string clip = "sacar_dosis";
    public bool usada;

    void Reset() => alcance = 2f; // está en el piso: Elías la alcanza parado al lado del colchón

    void Start()
    {
        // La colisión es para que la mirada la encuentre. Elías no se tropieza con ella: está
        // tirada en el piso, como la ropa.
        var cuerpo = abstinencia.GetComponentInParent<CharacterController>();
        if (cuerpo != null)
            foreach (var colision in GetComponentsInChildren<Collider>())
                Physics.IgnoreCollision(cuerpo, colision);
    }

    public override bool PuedeUsar(Elias elias) =>
        !usada && !abstinencia.BajoElEfecto && elias.LlegaAlInicio(clip, espacio, transform);

    public override IEnumerator Usar(Elias elias)
    {
        yield return elias.Reproducir(clip, espacio, false, (name, transform));
        yield return new WaitForSeconds(0.6f); // la dosis en la mano
        yield return Fundido.A(1f, 0.4f);

        // A oscuras: la dosis se gasta, Elías se para y empieza el efecto.
        usada = true;
        gameObject.SetActive(false);
        elias.brazos.Reposo();
        elias.Pararse();
        abstinencia.Consumir();
        yield return new WaitForSeconds(1.5f);
        yield return Fundido.A(0f, 2f);
    }
}
