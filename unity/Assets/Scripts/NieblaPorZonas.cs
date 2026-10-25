using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// La niebla iluminada (NieblaPS1) no sabe de paredes: una luz del 4B haría brillar la niebla
/// del pasillo a través del muro. Esto cambia las luces que la iluminan según dónde está la
/// cámara: en el 4B, las del 4B; en el pasillo, las del pasillo; en cada escalera, las suyas.
///
/// Cada zona es una caja en el mundo. Se usa la primera que contiene a la cámara, así que las
/// chicas (la cabina, el cuarto de limpieza) van antes que las grandes. Fuera de todas, quedan
/// las de la última. Va en un objeto de la escena.
/// </summary>
public class NieblaPorZonas : MonoBehaviour
{
    public NieblaPS1 niebla;
    [Tooltip("La cámara del juego.")]
    public Transform camara;
    public List<Zona> zonas = new List<Zona>();

    [Serializable]
    public class Zona
    {
        public string nombre;
        [Tooltip("La caja, en coordenadas de Unity.")]
        public Vector3 centro;
        public Vector3 tamano;
        [Tooltip("Las luces de esta zona que iluminan la niebla (como máximo 8).")]
        public List<Light> luces = new List<Light>();

        public bool Contiene(Vector3 punto) => new Bounds(centro, tamano).Contains(punto);
    }

    /// <summary>La zona donde está la cámara (o donde estuvo por última vez).</summary>
    public string Actual => actual?.nombre;

    Zona actual;

    void LateUpdate()
    {
        if (niebla == null || camara == null)
            return;
        var zona = zonas.Find(z => z.Contiene(camara.position));
        if (zona == null || zona == actual)
            return;
        actual = zona;
        niebla.luces = new List<Light>(zona.luces);
    }

    void OnDrawGizmosSelected()
    {
        Gizmos.color = new Color(0.4f, 0.9f, 0.6f, 0.6f);
        foreach (var z in zonas)
            Gizmos.DrawWireCube(z.centro, z.tamano);
    }
}
