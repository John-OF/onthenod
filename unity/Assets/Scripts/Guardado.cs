using System;
using System.IO;
using UnityEngine;

/// <summary>
/// La partida guardada (6.8): se escribe cada vez que Elías escribe en el cuaderno
/// (CuadernoInteractivo). Guarda la noche, la abstinencia y lo que lleva Partida, en un JSON
/// (partida.json) en la carpeta de datos del juego (Application.persistentDataPath).
///
/// Por ahora solo se guarda: la partida se cargará desde el menú, cuando exista.
/// </summary>
public static class Guardado
{
    /// <summary>Lo que se guarda. Los nombres son las claves del JSON: no cambiarlos.</summary>
    [Serializable]
    public class Datos
    {
        public int version = 1;
        public string fecha;            // cuándo se guardó (ISO 8601, hora local)
        public int noche;
        public float abstinencia;       // de 0 a 100 (6.2)
        public bool bajoElEfecto;       // si escribió bajo el efecto de una dosis (6.3)
        public int diasLimpio;
        public int dosis;
        public int dependencia;
        public int llamadasContestadas;
        public int llamadasPerdidas;
    }

    public static string Ruta => Path.Combine(Application.persistentDataPath, "partida.json");

    /// <summary>Guarda la partida como está ahora.</summary>
    public static void Escribir(Abstinencia abstinencia)
    {
        var datos = new Datos
        {
            fecha = DateTime.Now.ToString("s"),
            noche = Partida.Noche,
            abstinencia = abstinencia.nivel,
            bajoElEfecto = abstinencia.BajoElEfecto,
            diasLimpio = Partida.DiasLimpio,
            dosis = Partida.Dosis,
            dependencia = Partida.Dependencia,
            llamadasContestadas = Partida.LlamadasContestadas,
            llamadasPerdidas = Partida.LlamadasPerdidas,
        };

        // Primero a un archivo aparte y después se cambia por el anterior: si el juego se cierra
        // a mitad de camino, la partida de antes queda entera.
        var ruta = Ruta;
        var temporal = ruta + ".tmp";
        File.WriteAllText(temporal, JsonUtility.ToJson(datos, true));
        if (File.Exists(ruta))
            File.Replace(temporal, ruta, null);
        else
            File.Move(temporal, ruta);
        Debug.Log($"Partida guardada en {ruta}");
    }
}
