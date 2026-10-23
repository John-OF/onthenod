using System.Collections;
using UnityEngine;

/// <summary>
/// La Noche 1 en el 4B (sección 5), en orden:
///   1. Elías despierta en el suelo, mirándose las manos, y se levanta (la imagen aclara desde negro).
///   2. Un rato después suena el teléfono; al contestar, solo hay estática.
///   3. Después, Tomás vivo aparece en el sofá; al voltear, ya no está.
///   4. Golpes en la puerta (GolpesEnLaPuerta).
/// Los tiempos se ajustan en el inspector. Va en un objeto de la escena.
/// </summary>
public class NocheUno : MonoBehaviour
{
    public Elias elias;
    [Tooltip("La raíz del 4B: las pistas de los clips están en sus coordenadas.")]
    public Transform espacio;
    public TelefonoInteractivo telefono;
    public AparicionTomas tomas;
    public GolpesEnLaPuerta golpes;

    [Header("Tiempos (segundos)")]
    [Tooltip("Desde que se levanta hasta que suena el teléfono.")]
    public float esperaTelefono = 40f;
    [Tooltip("Desde que termina la llamada hasta que puede aparecer Tomás.")]
    public float esperaTomas = 15f;
    [Tooltip("Desde que Tomás se va hasta que tocan la puerta.")]
    public float esperaGolpes = 40f;

    [Tooltip("Empezar con el despertar (apagarlo sirve para probar otra cosa más rápido).")]
    public bool despertar = true;

    IEnumerator Start()
    {
        if (despertar)
        {
            Fundido.Poner(1f);
            StartCoroutine(Fundido.A(0f, 3f));
            yield return elias.Escena(elias.Despertar("mirar_manos", espacio));
        }

        yield return new WaitForSeconds(esperaTelefono);
        bool termino = false;
        telefono.Termino += _ => termino = true;
        telefono.Sonar();
        while (!termino)
            yield return null;

        yield return new WaitForSeconds(esperaTomas);
        tomas.Empezar();
        while (!tomas.SeFue)
            yield return null;

        yield return new WaitForSeconds(esperaGolpes);
        if (golpes != null)
            golpes.Empezar();
    }
}
