using UnityEngine;

/// <summary>
/// Lo que la partida va acumulando. Más adelante se guarda en el cuaderno (6.8) y cuenta para
/// el final (sección 7).
/// </summary>
public static class Partida
{
    /// <summary>Días sin consumir. La Noche 1 es el primero.</summary>
    public static int DiasLimpio { get; private set; } = 1;

    /// <summary>Cuántas veces consumió.</summary>
    public static int Dosis { get; private set; }

    /// <summary>La Dependencia de la sección 7: sube con cada dosis.</summary>
    public static int Dependencia { get; private set; }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
    public static void Reiniciar()
    {
        DiasLimpio = 1;
        Dosis = 0;
        Dependencia = 0;
    }

    /// <summary>Lo que cuesta una dosis (6.3): el contador de días limpio vuelve a cero y suma Dependencia.</summary>
    public static void Consumio()
    {
        DiasLimpio = 0;
        Dosis++;
        Dependencia++;
    }
}
