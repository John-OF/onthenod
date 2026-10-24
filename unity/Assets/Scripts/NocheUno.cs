using System.Collections;
using UnityEngine;

/// <summary>
/// La Noche 1 en el 4B (sección 5), en orden:
///   1. Elías despierta en el suelo, mirándose las manos, y se levanta (la imagen aclara desde negro).
///   2. El tutorial integrado: buscar agua (el fregadero), limpiar los rastros del consumo
///      (RastroInteractivo) y escribir en el cuaderno. Lo guían los pensamientos de Elías, sin
///      indicadores (6.9). Si el jugador no lo termina, la noche sigue igual pasado un rato.
///   3. Un rato después suena el teléfono; al contestar, solo hay estática.
///   4. Después, Tomás vivo aparece en el sofá; al voltear, ya no está.
///   5. Golpes en la puerta (GolpesEnLaPuerta).
/// Los tiempos y las frases se cambian en el inspector. Va en un objeto de la escena.
/// </summary>
public class NocheUno : MonoBehaviour
{
    public Elias elias;
    [Tooltip("La raíz del 4B: las pistas de los clips están en sus coordenadas.")]
    public Transform espacio;
    public TelefonoInteractivo telefono;
    public AparicionTomas tomas;
    public GolpesEnLaPuerta golpes;

    [Header("Tutorial")]
    public AguaInteractiva agua;
    public CuadernoInteractivo cuaderno;
    [Tooltip("Los rastros del consumo que hay que limpiar.")]
    public RastroInteractivo[] rastros;
    public Pensamientos pensamientos;

    [Header("Pensamientos del tutorial")]
    public string sed = "Tengo la boca seca.";
    [Tooltip("Si pasa un rato y no tomó agua.")]
    public string sedOtraVez = "Agua. En la cocina tiene que haber agua.";
    public string limpiar = "Tengo que sacar todo esto de aquí. Las jeringas, todo.";
    [Tooltip("Si pasa un rato sin recoger nada y todavía quedan rastros.")]
    public string quedan = "Todavía queda algo.";
    public string escribir = "Ya está. Lo voy a escribir.";

    [Header("Tiempos (segundos)")]
    [Tooltip("Cuánto espera un pensamiento que insiste (si el jugador no avanza).")]
    public float insistir = 60f;
    [Tooltip("Si el tutorial no termina en este tiempo desde que Elías se levanta, la noche sigue igual.")]
    public float tutorialMaximo = 360f;
    [Tooltip("Desde que termina el tutorial (o se levanta, sin tutorial) hasta que suena el teléfono.")]
    public float esperaTelefono = 20f;
    [Tooltip("Desde que termina la llamada hasta que puede aparecer Tomás.")]
    public float esperaTomas = 15f;
    [Tooltip("Desde que Tomás se va hasta que tocan la puerta.")]
    public float esperaGolpes = 40f;

    [Tooltip("Empezar con el despertar (apagarlo sirve para probar otra cosa más rápido).")]
    public bool despertar = true;
    [Tooltip("Hacer el tutorial antes del teléfono (apagarlo sirve para probar lo que sigue).")]
    public bool tutorial = true;

    IEnumerator Start()
    {
        if (despertar)
        {
            Fundido.Poner(1f);
            StartCoroutine(Fundido.A(0f, 3f));
            yield return elias.Escena(elias.Despertar("mirar_manos", espacio));
        }

        if (tutorial)
            yield return Tutorial();

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

    int Quedan()
    {
        int n = 0;
        foreach (var r in rastros)
            if (r != null && !r.Recogido)
                n++;
        return n;
    }

    /// <summary>
    /// Buscar agua, limpiar y escribir. No obliga a seguir el orden: cada pensamiento aparece
    /// solo si todavía hace falta. Termina cuando escribe en el cuaderno con todo hecho.
    /// </summary>
    IEnumerator Tutorial()
    {
        float inicio = Time.time;
        bool Vencido() => Time.time - inicio > tutorialMaximo;

        // El agua
        yield return new WaitForSeconds(1.5f);
        if (!agua.Bebio)
            pensamientos.Pensar(sed);
        float desde = Time.time;
        bool insistio = false;
        while (!agua.Bebio && !Vencido())
        {
            if (!insistio && Time.time - desde > insistir)
            {
                pensamientos.Pensar(sedOtraVez);
                insistio = true;
            }
            yield return null;
        }

        // Los rastros
        if (Quedan() > 0 && !Vencido())
        {
            yield return new WaitForSeconds(2f);
            if (Quedan() > 0)
                pensamientos.Pensar(limpiar);
        }
        int antes = Quedan();
        desde = Time.time;
        while (Quedan() > 0 && !Vencido())
        {
            if (Quedan() != antes)
            {
                antes = Quedan();
                desde = Time.time;
            }
            else if (Time.time - desde > insistir)
            {
                pensamientos.Pensar(quedan);
                desde = Time.time;
            }
            yield return null;
        }

        // El cuaderno: hay que escribir después de haber hecho todo
        if (Vencido())
            yield break;
        int escrituras = cuaderno.Escrituras;
        while (!elias.Libre)
            yield return null;
        if (cuaderno.Escrituras == escrituras) // si justo estaba escribiendo, ya está
            pensamientos.Pensar(escribir);
        while (cuaderno.Escrituras == escrituras && !Vencido())
            yield return null;
        while (!elias.Libre)
            yield return null;
    }
}
