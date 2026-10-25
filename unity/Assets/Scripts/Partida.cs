using UnityEngine;

/// <summary>
/// Lo que la partida va acumulando. Se guarda al escribir en el cuaderno (6.8, ver Guardado) y
/// cuenta para el final (sección 7).
/// </summary>
public static class Partida
{
    /// <summary>La noche que se está jugando: la Noche 1 en el 4B y la Noche 2 en el pasillo.</summary>
    public static int Noche { get; private set; } = 1;

    /// <summary>Días sin consumir. La Noche 1 es el primero.</summary>
    public static int DiasLimpio { get; private set; } = 1;

    /// <summary>Cuántas veces consumió.</summary>
    public static int Dosis { get; private set; }

    /// <summary>La Dependencia de la sección 7: sube con cada dosis.</summary>
    public static int Dependencia { get; private set; }

    /// <summary>Llamadas que contestó y que dejó sonar (6.5): cuenta para el final.</summary>
    public static int LlamadasContestadas { get; private set; }
    public static int LlamadasPerdidas { get; private set; }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
    public static void Reiniciar()
    {
        Noche = 1;
        DiasLimpio = 1;
        Dosis = 0;
        Dependencia = 0;
        LlamadasContestadas = 0;
        LlamadasPerdidas = 0;
    }

    /// <summary>Pasa a la noche <paramref name="noche"/> (al abrir la puerta del 4B, la Noche 2).</summary>
    public static void EmpezarNoche(int noche) => Noche = noche;

    public static void Llamada(bool contesto)
    {
        if (contesto)
            LlamadasContestadas++;
        else
            LlamadasPerdidas++;
    }

    /// <summary>Lo que cuesta una dosis (6.3): el contador de días limpio vuelve a cero y suma Dependencia.</summary>
    public static void Consumio()
    {
        DiasLimpio = 0;
        Dosis++;
        Dependencia++;
    }
}
