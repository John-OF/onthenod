using System.Collections;
using UnityEngine;

/// <summary>
/// La Noche 2 en el pasillo del 4º piso (sección 5). Por ahora, el comienzo: al final de la
/// Noche 1, Elías abre la puerta del 4B (PuertaDeEntrada) y, mientras la pantalla está a
/// oscuras, la puerta queda abierta (el 4B sigue siendo el refugio), se van los pies de abajo de
/// la puerta y Elías aparece en el umbral, mirando el pasillo. Es la vuelta 0. La vuelta (bajar
/// por la escalera y volver a empezar) y lo que cambia en cada una todavía no están.
/// Va en un objeto de la escena.
/// </summary>
public class NocheDos : MonoBehaviour
{
    public Elias elias;
    [Tooltip("La puerta de entrada del 4B (el objeto con el origen en la bisagra).")]
    public Transform puerta4B;
    [Tooltip("La mirilla de esa puerta: con la puerta abierta ya no se usa.")]
    public MirillaInteractiva mirilla;
    public GolpesEnLaPuerta golpes;
    public Pensamientos pensamientos;

    [Header("Al abrir la puerta")]
    [Tooltip("Dónde quedan los ojos de Elías, en coordenadas de Blender: en la puerta del 4B, del lado del pasillo.")]
    public Vector3 ojos = new Vector3(3.45f, -0.45f, 1.6f);
    [Tooltip("Hacia dónde mira, en coordenadas de Blender: el pasillo largo, hacia el elevador.")]
    public Vector3 mira = new Vector3(12f, -1.25f, 1.4f);
    [Tooltip("Cuánto queda abierta la puerta del 4B, en grados (se abre hacia adentro).")]
    public float apertura = 100f;
    [Tooltip("Segundos a oscuras antes de que aclare.")]
    public float aOscuras = 0.8f;
    [Tooltip("Segundos que tarda en aclarar.")]
    public float aclarar = 2.5f;
    [Tooltip("Lo que piensa Elías al ver el pasillo vacío.")]
    public string pensamiento = "No hay nadie.";

    /// <summary>Si ya empezó (Elías salió del 4B).</summary>
    public bool Empezo { get; private set; }

    /// <summary>
    /// Corre con la pantalla a oscuras, dentro del uso de la puerta (Elías no responde). Al
    /// terminar, Elías queda donde quedó la cámara.
    /// </summary>
    public IEnumerator Empezar()
    {
        Empezo = true;
        Partida.EmpezarNoche(2);
        if (golpes != null)
            golpes.Terminar();
        if (mirilla != null)
            mirilla.enabled = false;
        // Se abre hacia adentro: en Blender, un giro positivo alrededor de Z; en Unity, negativo alrededor de Y.
        puerta4B.rotation = Quaternion.AngleAxis(-apertura, Vector3.up) * puerta4B.rotation;

        var p = EscenaBlender.DeBlender(new[] { ojos.x, ojos.y, ojos.z });
        var m = EscenaBlender.DeBlender(new[] { mira.x, mira.y, mira.z });
        elias.camara.SetPositionAndRotation(p, Quaternion.LookRotation(m - p, Vector3.up));

        yield return new WaitForSeconds(aOscuras);
        yield return Fundido.A(0f, aclarar);
        if (pensamientos != null && !string.IsNullOrEmpty(pensamiento))
            pensamientos.Pensar(pensamiento);
    }
}
