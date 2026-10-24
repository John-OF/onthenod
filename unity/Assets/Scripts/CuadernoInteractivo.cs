using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// El cuaderno de Elías, en la mesa de centro del 4B: escribir en él guarda la partida (6.8, ver
/// Guardado). Elías se agacha, toma el cuaderno y lo mira en la mano (el clip tomar_cuaderno);
/// corte a negro; en la pantalla, lo que escribe: los días limpio («Día 1. No consumí.», o
/// «Día 0.» si consumió). A oscuras, el cuaderno vuelve a la mesa y Elías se para. La escritura
/// no se ve, como el consumo. Se puede usar todas las veces que se quiera, también bajo el efecto.
///
/// Va en el cuaderno, que ya trae su colisión (la pone el importador). Su nombre es el de su
/// pista en el JSON de los brazos.
/// </summary>
public class CuadernoInteractivo : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public Abstinencia abstinencia;

    [Header("Tiempos (segundos)")]
    [Tooltip("Cuánto lo mira en la mano antes del corte a negro.")]
    public float mirar = 0.6f;
    public float aNegro = 0.5f;
    public float aparecerTexto = 1f;
    [Tooltip("Cuánto se queda el texto en pantalla.")]
    public float leer = 3f;
    public float volver = 1.2f;

    /// <summary>Cuántas veces escribió en el cuaderno (para el tutorial de la Noche 1).</summary>
    public int Escrituras { get; private set; }

    void Reset() => alcance = 1.8f; // está sobre la mesa de centro, a 42 cm del piso

    public override bool PuedeUsar(Elias elias) => elias.LlegaAlInicio("tomar_cuaderno", espacio, transform);

    public override IEnumerator Usar(Elias elias)
    {
        var posicion = transform.localPosition;
        var rotacion = transform.localRotation;
        yield return elias.Reproducir("tomar_cuaderno", espacio, false, (name, transform));
        yield return new WaitForSeconds(mirar);
        yield return Fundido.A(1f, aNegro);

        // A oscuras: el cuaderno vuelve a la mesa, Elías se para y escribe
        transform.localPosition = posicion;
        transform.localRotation = rotacion;
        elias.brazos.Reposo();
        elias.Pararse();
        string texto;
        try
        {
            Guardado.Escribir(abstinencia);
            texto = LoQueEscribe();
        }
        catch (Exception error)
        {
            Debug.LogException(error);
            texto = "No se pudo guardar la partida.";
        }
        int turno = TextoPS1.Escribir(texto);
        yield return TextoPS1.A(1f, aparecerTexto, turno);
        yield return new WaitForSeconds(leer);
        yield return TextoPS1.A(0f, aparecerTexto, turno);
        yield return new WaitForSeconds(0.4f);
        yield return Fundido.A(0f, volver);
        Escrituras++;
    }

    /// <summary>Lo que Elías escribe: los días que lleva sin consumir.</summary>
    public static string LoQueEscribe() =>
        Partida.DiasLimpio > 0 ? $"Día {Partida.DiasLimpio}. No consumí." : "Día 0.";
}
