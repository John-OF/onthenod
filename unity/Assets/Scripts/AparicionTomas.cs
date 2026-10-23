using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

/// <summary>
/// Tomás aparece (Noche 1): sentado en el sofá, vivo. Aparece mientras Elías no mira hacia ahí;
/// cuando lo ve, dice su línea («¿Otra vez sin dormir?»), y en cuanto Elías deja de mirarlo, ya
/// no está («al voltear, ya no está», sección 5).
///
/// Va en el modelo de Tomás (Assets/Art/Tomas/tomas.fbx) puesto en la escena donde se sienta.
/// Su aspecto sale del JSON de Tomás: el estado del mundo de la abstinencia es "vivo, mal"
/// (estado1); bajo el efecto, "vivo, sonriente" (estado0).
/// </summary>
[RequireComponent(typeof(Animator))]
public class AparicionTomas : MonoBehaviour
{
    public Elias elias;
    public EstadosDelMundo mundo;
    [Tooltip("tomas_escena.json: los estados (textura, formas, la Polaroid).")]
    public TextAsset datos;
    [Tooltip("Las texturas de los estados (tomas_estado0 a tomas_estado4).")]
    public Texture2D[] texturas;
    [Tooltip("La pose (un clip del FBX de Tomás).")]
    public AnimationClip pose;
    public AudioClip voz;
    [Tooltip("Lo que se esconde mientras él está (la ropa tirada en el sofá, donde se sienta).")]
    public GameObject[] esconder;

    [Tooltip("Cuánto espera, desde que Elías lo ve, para hablar.")]
    public float esperaParaHablar = 0.8f;

    /// <summary>Si ya apareció y se fue.</summary>
    public bool SeFue { get; private set; }

    [NonSerialized] EscenaBlender escena; // se lee del JSON al empezar
    PlayableGraph grafo;
    AudioSource boca;
    Transform cabeza;

    void Awake()
    {
        escena = JsonUtility.FromJson<EscenaBlender>(datos.text);
        cabeza = Array.Find(GetComponentsInChildren<Transform>(true), t => t.name == "Head");
        boca = cabeza.gameObject.AddComponent<AudioSource>();
        boca.spatialBlend = 1f;
        boca.minDistance = 1.5f;
        boca.maxDistance = 12f;
        boca.playOnAwake = false;
        gameObject.SetActive(false);
    }

    void OnDisable()
    {
        if (grafo.IsValid())
            grafo.Destroy();
    }

    /// <summary>Espera a que Elías no mire hacia el sofá, aparece, y sigue solo hasta irse.</summary>
    public void Empezar() => elias.StartCoroutine(Aparicion());

    IEnumerator Aparicion()
    {
        // Aparece cuando no se lo ve: ni su cabeza ni el sofá a la vista.
        while (elias.Ve(PuntoCabeza(), 0f))
            yield return null;
        Mostrar();

        // Cuando Elías lo ve, habla.
        while (!elias.Ve(cabeza.position))
            yield return null;
        yield return new WaitForSeconds(esperaParaHablar);
        boca.PlayOneShot(voz);
        yield return new WaitForSeconds(voz.length);

        // Al voltear, ya no está.
        float sinVerlo = 0f;
        while (sinVerlo < 0.15f)
        {
            sinVerlo = elias.Ve(cabeza.position, 0f) ? 0f : sinVerlo + Time.deltaTime;
            yield return null;
        }
        Ocultar();
        SeFue = true;
    }

    Vector3 PuntoCabeza() => transform.position + Vector3.up * 1.1f;

    void Mostrar()
    {
        gameObject.SetActive(true);
        foreach (var o in esconder)
            o.SetActive(false);

        // Su aspecto: el estado según el mundo.
        var estado = escena.BuscarEstado(mundo != null && mundo.Actual == "efecto" ? "estado0" : "estado1");
        foreach (var r in GetComponentsInChildren<Renderer>(true))
        {
            var m = Array.Find(estado.materiales, x => x.nombre == r.sharedMaterial.name);
            var tex = m == null ? null : Array.Find(texturas, t => t != null && t.name == m.textura);
            if (tex != null)
                r.material.SetTexture("_BaseMap", tex);
            if (r is SkinnedMeshRenderer piel && estado.formas != null)
                foreach (var f in estado.formas)
                {
                    int i = piel.sharedMesh.GetBlendShapeIndex(f.forma);
                    if (i >= 0)
                        piel.SetBlendShapeWeight(i, f.valor * 100f);
                }
            if (estado.objetos_ocultos != null)
                r.gameObject.SetActive(Array.IndexOf(estado.objetos_ocultos, r.name) < 0);
        }

        // La pose: el clip quieto, para siempre.
        var animator = GetComponent<Animator>();
        animator.applyRootMotion = false;
        animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
        grafo = PlayableGraph.Create("Tomás");
        var clip = AnimationClipPlayable.Create(grafo, pose);
        clip.Pause();
        AnimationPlayableOutput.Create(grafo, "Pose", animator).SetSourcePlayable(clip);
        grafo.Play();
        grafo.Evaluate(0f);
    }

    void Ocultar()
    {
        gameObject.SetActive(false);
        foreach (var o in esconder)
            o.SetActive(true);
    }
}
