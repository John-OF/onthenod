using System;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

/// <summary>
/// Las animaciones de los brazos de Elías (Assets/Art/BrazosElias), en dos capas:
///   - la de abajo: el reposo en bucle, o el clip que pide Elías (abrir_puerta,
///     telefono_contestar...). El tiempo de ese clip lo pone Elías en cada cuadro, para que
///     vaya junto con la cámara, la puerta y el auricular;
///   - la de encima: el temblor de la abstinencia, en bucle, sumado a lo que haya abajo.
/// Todos los clips empiezan y terminan en el reposo, así que se pasa de uno a otro sin mezclar.
/// Va en el modelo de los brazos (el objeto con el Animator), que cuelga de la cámara.
/// </summary>
[RequireComponent(typeof(Animator))]
public class BrazosElias : MonoBehaviour
{
    [Tooltip("Los clips del FBX de los brazos (reposo, temblor, abrir_puerta...).")]
    public AnimationClip[] clips;

    [Tooltip("Cuánto se nota el temblor: 0, nada; 1, como en las vistas previas de Blender. " +
             "Más adelante lo moverá el nivel de abstinencia.")]
    [Range(0f, 1f)] public float pesoTemblor = 1f;

    [Tooltip("Las texturas de los cuatro estados de los brazos (brazos_estado0 a brazos_estado3).")]
    public Texture2D[] texturas;

    PlayableGraph grafo;
    AnimationMixerPlayable capaBase;
    AnimationLayerMixerPlayable capas;
    AnimationClipPlayable accion;
    SkinnedMeshRenderer piel;
    string nombreMaterial;

    public AnimationClip Clip(string nombre) => Array.Find(clips, c => c != null && c.name == nombre);

    /// <summary>
    /// Pone un estado de los brazos (del JSON de los brazos): su textura y cuánto se adelgazan
    /// (la forma "consumido"). Ver Brazos de Elías en la sección 10.
    /// </summary>
    public void PonerEstado(EscenaBlender.Estado estado)
    {
        if (piel == null)
        {
            piel = GetComponentInChildren<SkinnedMeshRenderer>();
            nombreMaterial = piel.sharedMaterial.name;
        }
        var m = Array.Find(estado.materiales, x => x.nombre == nombreMaterial);
        var textura = m == null ? null : Array.Find(texturas, t => t != null && t.name == m.textura);
        if (textura != null)
            piel.material.SetTexture("_BaseMap", textura); // la primera vez, Unity hace una copia del material
        if (estado.formas != null)
            foreach (var f in estado.formas)
            {
                int i = piel.sharedMesh.GetBlendShapeIndex(f.forma);
                if (i >= 0)
                    piel.SetBlendShapeWeight(i, f.valor * 100f);
            }
    }

    void OnEnable()
    {
        var animator = GetComponent<Animator>();
        animator.applyRootMotion = false;
        grafo = PlayableGraph.Create("Brazos de Elías");
        grafo.SetTimeUpdateMode(DirectorUpdateMode.GameTime);

        capaBase = AnimationMixerPlayable.Create(grafo, 2);
        grafo.Connect(AnimationClipPlayable.Create(grafo, Clip("reposo")), 0, capaBase, 0);
        capaBase.SetInputWeight(0, 1f);

        // El temblor es aditivo: Unity lo resta de su cuadro de reposo (ver ImportadorArte.cs)
        // y suma lo que queda.
        capas = AnimationLayerMixerPlayable.Create(grafo, 2);
        grafo.Connect(capaBase, 0, capas, 0);
        grafo.Connect(AnimationClipPlayable.Create(grafo, Clip("temblor")), 0, capas, 1);
        capas.SetInputWeight(0, 1f);
        capas.SetLayerAdditive(1, true);

        AnimationPlayableOutput.Create(grafo, "Brazos", animator).SetSourcePlayable(capas);
        grafo.Play();
    }

    void OnDisable()
    {
        if (grafo.IsValid())
            grafo.Destroy();
    }

    void Update() => capas.SetInputWeight(1, pesoTemblor);

    /// <summary>Muestra el clip quieto en el segundo <paramref name="tiempo"/>. Elías lo llama en cada cuadro.</summary>
    public void Mostrar(AnimationClip clip, float tiempo)
    {
        if (!accion.IsValid() || accion.GetAnimationClip() != clip)
        {
            Soltar();
            accion = AnimationClipPlayable.Create(grafo, clip);
            accion.Pause(); // su tiempo no avanza solo: lo pone Elías
            grafo.Connect(accion, 0, capaBase, 1);
        }
        accion.SetTime(tiempo);
        capaBase.SetInputWeight(0, 0f);
        capaBase.SetInputWeight(1, 1f);
    }

    /// <summary>Vuelve al reposo.</summary>
    public void Reposo()
    {
        Soltar();
        capaBase.SetInputWeight(0, 1f);
    }

    void Soltar()
    {
        if (!accion.IsValid())
            return;
        grafo.Disconnect(capaBase, 1);
        accion.Destroy();
        accion = default;
    }
}
