using System.Collections;
using UnityEngine;

/// <summary>
/// Algo que Elías puede usar: lo mira de cerca (ver Elias.alcance) y se aprieta Interactuar (la E,
/// o el botón de arriba del control). Necesita una colisión, en este objeto o en uno de sus hijos,
/// para que la mirada de Elías lo encuentre.
/// </summary>
public abstract class Interactuable : MonoBehaviour
{
    /// <summary>Si ahora se puede usar (por ejemplo, la puerta no está abierta ya).</summary>
    public abstract bool PuedeUsar(Elias elias);

    /// <summary>Lo que pasa al usarlo. Mientras dura, Elías no responde a los controles.</summary>
    public abstract IEnumerator Usar(Elias elias);
}
