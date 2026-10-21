using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Niebla iluminada: hace que las luces iluminen la niebla que tienen cerca (el halo de los
/// focos, la bruma fría del fluorescente al fondo del pasillo), como la niebla volumétrica de
/// Blender. Va en un objeto de la escena; el cálculo está en PS1Niebla.hlsl.
///
/// La densidad es la de la niebla de la escena (Lighting > Environment > Fog, en modo
/// exponencial), que además oscurece lo lejano. Si esa niebla está apagada, esto no hace nada.
/// </summary>
[ExecuteAlways]
[DisallowMultipleComponent]
public class NieblaPS1 : MonoBehaviour
{
    const int MaxLuces = 8; // igual que PS1_NIEBLA_MAX_LUCES en PS1Niebla.hlsl

    [Tooltip("Color de la niebla: qué parte de la luz devuelve. En Blender es el Color del Principled Volume.")]
    public Color color = new Color(0.88f, 0.91f, 0.87f);

    [Tooltip("Multiplica el brillo de la niebla. 1 = como en Blender.")]
    [Min(0f)] public float intensidad = 1f;

    [Tooltip("Luces que iluminan la niebla. Vacío: las luces puntuales y spots activas de la escena " +
             "(como máximo 8, las más cercanas a la cámara). Nunca las que no iluminan la capa Default.")]
    public List<Light> luces = new List<Light>();

    static readonly int IdLuces = Shader.PropertyToID("_PS1NieblaLuces");
    static readonly int IdDispersion = Shader.PropertyToID("_PS1NieblaDispersion");
    static readonly int IdPosicion = Shader.PropertyToID("_PS1NieblaPosicion");
    static readonly int IdColor = Shader.PropertyToID("_PS1NieblaColor");
    static readonly int IdFoco = Shader.PropertyToID("_PS1NieblaFoco");
    static readonly int IdCono = Shader.PropertyToID("_PS1NieblaCono");

    readonly Vector4[] posicion = new Vector4[MaxLuces];
    readonly Vector4[] colores = new Vector4[MaxLuces];
    readonly Vector4[] foco = new Vector4[MaxLuces];
    readonly Vector4[] cono = new Vector4[MaxLuces];
    readonly List<Light> candidatas = new List<Light>();
    float proximaBusqueda;

    void OnEnable() => Actualizar();

    void OnDisable() => Shader.SetGlobalVector(IdLuces, Vector4.zero);

    void LateUpdate() => Actualizar();

    void OnValidate() => Actualizar();

    void Actualizar()
    {
        if (!isActiveAndEnabled)
            return;

        float densidad = RenderSettings.fog ? RenderSettings.fogDensity : 0f;
        var dispersion = color.linear * (densidad * intensidad);
        Shader.SetGlobalVector(IdDispersion, new Vector4(dispersion.r, dispersion.g, dispersion.b, 0f));

        // En el editor se buscan las luces siempre; jugando, dos veces por segundo.
        if (!Application.isPlaying || Time.unscaledTime >= proximaBusqueda)
        {
            proximaBusqueda = Time.unscaledTime + 0.5f;
            candidatas.Clear();
            if (luces.Count > 0)
                candidatas.AddRange(luces);
            else
                candidatas.AddRange(FindObjectsByType<Light>(FindObjectsSortMode.None));
        }
        // Las luces que no iluminan la capa Default (como la de los brazos de Elías, que solo
        // ilumina la capa Brazos) tampoco iluminan la niebla.
        candidatas.RemoveAll(l => l == null || !l.isActiveAndEnabled || l.intensity <= 0f ||
                                  (l.type != LightType.Point && l.type != LightType.Spot) ||
                                  (l.renderingLayerMask & 1) == 0);

        var camara = Camera.main;
        if (candidatas.Count > MaxLuces && camara != null)
        {
            var origen = camara.transform.position;
            candidatas.Sort((a, b) => (a.transform.position - origen).sqrMagnitude
                .CompareTo((b.transform.position - origen).sqrMagnitude));
        }

        int cantidad = Mathf.Min(candidatas.Count, MaxLuces);
        for (int i = 0; i < MaxLuces; i++)
        {
            if (i >= cantidad)
            {
                posicion[i] = colores[i] = foco[i] = cono[i] = Vector4.zero;
                continue;
            }

            var luz = candidatas[i];
            var p = luz.transform.position;
            posicion[i] = new Vector4(p.x, p.y, p.z, 1f / Mathf.Max(luz.range * luz.range, 1e-4f));
            var c = luz.color.linear * luz.intensity; // como lo hace URP
            colores[i] = new Vector4(c.r, c.g, c.b, 0f);

            if (luz.type == LightType.Spot)
            {
                var f = luz.transform.forward;
                float cosExterior = Mathf.Cos(Mathf.Deg2Rad * luz.spotAngle * 0.5f);
                float cosInterior = Mathf.Cos(Mathf.Deg2Rad * luz.innerSpotAngle * 0.5f);
                float inverso = 1f / Mathf.Max(cosInterior - cosExterior, 0.001f);
                foco[i] = new Vector4(f.x, f.y, f.z, 1f);
                cono[i] = new Vector4(inverso, -cosExterior * inverso, 0f, 0f);
            }
            else
            {
                foco[i] = cono[i] = Vector4.zero;
            }
        }

        Shader.SetGlobalVector(IdLuces, new Vector4(cantidad, 0f, 0f, 0f));
        Shader.SetGlobalVectorArray(IdPosicion, posicion);
        Shader.SetGlobalVectorArray(IdColor, colores);
        Shader.SetGlobalVectorArray(IdFoco, foco);
        Shader.SetGlobalVectorArray(IdCono, cono);
    }
}
