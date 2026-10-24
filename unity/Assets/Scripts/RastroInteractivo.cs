using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// Un rastro del consumo (Noche 1, el tutorial: «ordenar el cuarto»): una jeringa, la cuchara
/// quemada, el cenicero con las colillas, el cinturón o el encendedor. Elías se agacha (o se
/// arrodilla, si está en el piso), lo recoge y lo guarda: la mano baja fuera de cuadro y el
/// rastro ya no está. Al terminar, vuelve a donde estaba.
///
/// Hay dos clips para todos, recoger_mesa y recoger_piso, hechos con las jeringas de la mesa de
/// centro y del piso de la sala: el clip se lleva a este rastro, girado hacia el lado desde donde
/// lo mira Elías. Solo en la abstinencia: bajo el efecto el 4B está limpio (los rastros son del
/// deterioro).
///
/// Va en el rastro (el objeto que agrupa sus piezas, con el origen en su base). Si no tiene
/// colisión, se le pone una caja que cubre sus piezas, para que la mirada de Elías lo encuentre.
/// Elías no choca con ella.
/// </summary>
public class RastroInteractivo : Interactuable
{
    [Tooltip("La raíz del escenario de Blender (el 4B): las pistas del clip están en sus coordenadas.")]
    public Transform espacio;
    public Abstinencia abstinencia;
    [Tooltip("recoger_mesa (sobre la mesa de centro) o recoger_piso (en el piso).")]
    public string clip = "recoger_mesa";
    [Tooltip("La pista del objeto con el que se hizo el clip: jeringa_mesa (recoger_mesa) o jeringa_piso (recoger_piso).")]
    public string pista = "jeringa_mesa";
    [Tooltip("Cuánto más grande que sus piezas es la caja que la mirada tiene que tocar, en metros.")]
    public float margen = 0.03f;

    /// <summary>Si ya lo recogió.</summary>
    public bool Recogido { get; private set; }

    void Reset() => alcance = 1.8f; // está sobre la mesa o en el piso, lejos de los ojos

    void Awake()
    {
        if (GetComponent<Collider>() == null)
            PonerCaja();
    }

    void Start()
    {
        var cuerpo = abstinencia.GetComponentInParent<CharacterController>();
        if (cuerpo != null)
            foreach (var colision in GetComponentsInChildren<Collider>())
                Physics.IgnoreCollision(cuerpo, colision);
    }

    /// <summary>Una caja que cubre todas sus piezas, un poco más grande.</summary>
    void PonerCaja()
    {
        Bounds? caja = null;
        foreach (var r in GetComponentsInChildren<Renderer>(true))
        {
            var b = r.bounds;
            for (int i = 0; i < 8; i++)
            {
                var esquina = transform.InverseTransformPoint(b.center + Vector3.Scale(b.extents,
                    new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                if (caja is Bounds c)
                {
                    c.Encapsulate(esquina);
                    caja = c;
                }
                else
                    caja = new Bounds(esquina, Vector3.zero);
            }
        }
        var colision = gameObject.AddComponent<BoxCollider>();
        colision.center = caja?.center ?? Vector3.zero;
        colision.size = (caja?.size ?? Vector3.zero) + Vector3.one * (2f * margen);
    }

    /// <summary>
    /// Lleva el clip de su objeto a este rastro: lo gira alrededor del eje vertical para que Elías
    /// llegue desde donde está, y lo mueve hasta aquí (en las coordenadas del escenario).
    /// </summary>
    Matrix4x4 Reubicar(Elias elias)
    {
        var delClip = elias.ReposoDePista(clip, pista).GetPosition();
        var cabeza = elias.CabezaAlEmpezar(clip).GetPosition();
        var aqui = espacio.InverseTransformPoint(transform.position);
        var ojos = espacio.InverseTransformPoint(elias.camara.position);
        var antes = Vector3.ProjectOnPlane(delClip - cabeza, Vector3.up);
        var ahora = Vector3.ProjectOnPlane(aqui - ojos, Vector3.up);
        float giro = Vector3.SignedAngle(antes, ahora, Vector3.up);
        return Matrix4x4.Translate(aqui) * Matrix4x4.Rotate(Quaternion.Euler(0f, giro, 0f)) * Matrix4x4.Translate(-delClip);
    }

    public override bool PuedeUsar(Elias elias) =>
        !Recogido && !abstinencia.BajoElEfecto && elias.LlegaAlInicio(clip, espacio, transform, Reubicar(elias));

    public override IEnumerator Usar(Elias elias)
    {
        var antes = elias.camara;
        var volver = Matrix4x4.TRS(antes.position, antes.rotation, Vector3.one);
        yield return elias.Reproducir(clip, espacio, true, new Elias.OpcionesClip { reubicar = Reubicar(elias) }, (pista, transform));
        Recogido = true;
        gameObject.SetActive(false);
        // Vuelve a donde estaba: así no queda parado adentro de un mueble
        yield return elias.Acercarse(volver);
    }
}
