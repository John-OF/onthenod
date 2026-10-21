using System.Collections;
using UnityEngine;

/// <summary>
/// El teléfono del 4B: Elías contesta (levanta el auricular y se lo lleva a la oreja), escucha
/// hasta que se vuelve a apretar Interactuar, y cuelga. Al contestar queda mirando hacia el
/// pasillo y la puerta del baño, como en Blender.
///
/// Va en la base del teléfono, con una colisión para que la mirada de Elías lo encuentre. Más
/// adelante: que suene, la estática y la voz de la madre (sección 6.5).
/// </summary>
public class TelefonoInteractivo : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas de los clips están en sus coordenadas.")]
    public Transform espacio;
    [Tooltip("El auricular: su nombre es el de su pista en el JSON de los brazos.")]
    public Transform auricular;

    public override bool PuedeUsar(Elias elias) => elias.LlegaAlInicio("telefono_contestar", espacio, transform);

    public override IEnumerator Usar(Elias elias)
    {
        yield return elias.Reproducir("telefono_contestar", espacio, false, (auricular.name, auricular));
        yield return elias.EsperarInteraccion();
        yield return elias.Reproducir("telefono_colgar", espacio, true, (auricular.name, auricular));
    }
}
