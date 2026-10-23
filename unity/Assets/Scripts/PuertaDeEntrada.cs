using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// La puerta de entrada del 4B en la Noche 1: después de los golpes y de la voz («Eli, ábreme»),
/// Elías la abre y aparece el pasillo. Por ahora, la Noche 2 todavía no existe: agarra la
/// perilla, la gira y corte a negro (sección 5).
///
/// No hay un clip para esta puerta: se usa el comienzo de abrir_puerta (hecho para la puerta del
/// dormitorio), movido para que la perilla de aquella caiga en la de esta. Va en la puerta.
/// </summary>
public class PuertaDeEntrada : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public string clip = "abrir_puerta";
    [Tooltip("Hasta qué segundo del clip: la mano ya giró la perilla y todavía no empujó.")]
    public float hasta = 1.0f;

    [Header("De una puerta a la otra (coordenadas de Blender)")]
    [Tooltip("La perilla de la puerta del dormitorio, cerrada, del lado del pasillo: HINGE + KNOB_REL en brazos_animaciones.py.")]
    public Vector3 perillaDelClip = new Vector3(3.465f, 4.60f, 1.01f);
    [Tooltip("La perilla de esta puerta, del lado de adentro (puerta_entrada_herraje_0).")]
    public Vector3 perilla = new Vector3(3.81f, 0.03f, 1.01f);
    [Tooltip("Cuánto hay que girar la otra puerta (alrededor del eje vertical de Blender) para que quede como esta.")]
    public float giro = 90f;

    /// <summary>Solo se puede abrir cuando la noche lo permite (después de los golpes).</summary>
    public bool habilitada;

    /// <summary>Avisa cuando la pantalla ya está a oscuras.</summary>
    public event Action Abrio;

    Matrix4x4 Reubicar()
    {
        // En Blender: llevar la perilla del clip al origen, girar y llevarla a esta perilla. En
        // Unity, un giro de Blender alrededor de Z es uno alrededor de Y con el signo cambiado.
        var de = EscenaBlender.DeBlender(new[] { perillaDelClip.x, perillaDelClip.y, perillaDelClip.z });
        var a = EscenaBlender.DeBlender(new[] { perilla.x, perilla.y, perilla.z });
        return Matrix4x4.Translate(a) * Matrix4x4.Rotate(Quaternion.Euler(0f, -giro, 0f)) * Matrix4x4.Translate(-de);
    }

    public override bool PuedeUsar(Elias elias) => habilitada && elias.LlegaAlInicio(clip, espacio, transform, Reubicar());

    public override IEnumerator Usar(Elias elias)
    {
        yield return elias.Reproducir(clip, espacio, false, new Elias.OpcionesClip { hasta = hasta, reubicar = Reubicar() });
        yield return Fundido.A(1f, 0.6f);
        Abrio?.Invoke();
        // Fin de la Noche 1 por ahora: se queda a oscuras, sin volver a responder.
        while (true)
            yield return null;
    }
}
