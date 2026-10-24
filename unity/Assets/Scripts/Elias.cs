using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Elías en primera persona: camina, mira y usa lo que tiene cerca (una puerta, el teléfono).
///
/// Al usar algo, deja de responder a los controles y corre una animación de sus brazos con la
/// cámara de interacción (sección 10 del documento de diseño, Brazos de Elías): la cámara va al
/// punto donde empieza el clip (inclinado sobre la mesita, frente a la perilla) y desde ahí sigue
/// a la cabeza de Blender, cuadro a cuadro, mientras la puerta o el auricular siguen sus propias
/// pistas. Todo eso viene en el JSON de los brazos (brazos_elias_escena.json). Al terminar,
/// Elías queda donde terminó la cabeza y vuelve a responder.
///
/// La cámara es hija de Elías, a la altura de los ojos, y los brazos cuelgan de ella.
/// </summary>
[RequireComponent(typeof(CharacterController))]
public class Elias : MonoBehaviour
{
    const string Cabeza = "Elias_Cabeza"; // la pista de la cabeza en el JSON de los brazos

    [Header("Partes")]
    [Tooltip("La cámara del juego: hija de Elías, a la altura de los ojos.")]
    public Transform camara;
    public BrazosElias brazos;
    [Tooltip("brazos_elias_escena.json: cómo se mueven la cabeza, la puerta y el auricular en cada clip.")]
    public TextAsset datosBrazos;

    [Header("Controles")]
    [Tooltip("InputSystem_Actions: usa Move, Look e Interact del mapa Player.")]
    public InputActionAsset controles;

    [Header("Caminar y mirar")]
    [Tooltip("Metros por segundo.")]
    public float velocidad = 1.3f;
    [Tooltip("Altura de los ojos: la de la cabeza en las animaciones de Blender.")]
    public float alturaOjos = 1.6f;
    [Tooltip("Grados por píxel que se mueve el mouse.")]
    public float sensibilidadMouse = 0.08f;
    [Tooltip("Grados por segundo con la palanca del control a fondo.")]
    public float velocidadPalanca = 120f;
    [Tooltip("Cuánto puede mirar hacia arriba o hacia abajo, en grados.")]
    public float limiteVertical = 80f;

    [Header("Usar")]
    [Tooltip("Hasta qué distancia, en metros, alcanza a usar algo que está mirando (salvo que el objeto diga otra).")]
    public float alcance = 1.4f;

    [Header("Los brazos según el mundo")]
    [Tooltip("Los mundos del escenario (abstinencia y efecto).")]
    public EstadosDelMundo mundo;
    [Tooltip("Cómo están los brazos en la abstinencia (estado0 a estado3 del JSON de los brazos): en la Noche 1, estado1. " +
             "Bajo el efecto se ven sanos (estado0): es la mentira de la droga (6.3).")]
    public string estadoBrazos = "estado1";

    /// <summary>Responde a los controles (no está usando nada).</summary>
    public bool Libre { get; private set; } = true;

    /// <summary>Cuánto tiembla la cámara, en grados. Lo pone la abstinencia.</summary>
    [System.NonSerialized] public float temblorCamara;

    CharacterController cuerpo;
    InputActionMap mapa;
    InputAction mover, mirar, interactuar;
    [System.NonSerialized] EscenaBlender datos; // se lee del JSON al empezar
    float inclinacion, caida;
    readonly Dictionary<Transform, Matrix4x4> reposos = new Dictionary<Transform, Matrix4x4>();

    void Awake()
    {
        cuerpo = GetComponent<CharacterController>();
        mapa = controles.FindActionMap("Player", true);
        mover = mapa.FindAction("Move", true);
        mirar = mapa.FindAction("Look", true);
        interactuar = mapa.FindAction("Interact", true);
        datos = JsonUtility.FromJson<EscenaBlender>(datosBrazos.text);
        inclinacion = Mathf.DeltaAngle(0f, camara.localEulerAngles.x);
    }

    void OnEnable()
    {
        mapa.Enable();
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
        if (mundo != null)
            mundo.Cambio += CambioDeMundo;
    }

    void OnDisable()
    {
        mapa.Disable();
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
        if (mundo != null)
            mundo.Cambio -= CambioDeMundo;
    }

    void CambioDeMundo(string nuevo)
    {
        var estado = datos.BuscarEstado(nuevo == "efecto" ? "estado0" : estadoBrazos);
        if (estado != null)
            brazos.PonerEstado(estado);
    }

    void Update()
    {
        if (!Libre)
            return;
        Mirar();
        Caminar();
        // Después de usar algo, la cámara vuelve sola a la altura de los ojos.
        camara.localPosition = Vector3.MoveTowards(camara.localPosition, new Vector3(0f, alturaOjos, 0f), 0.6f * Time.deltaTime);
        if (interactuar.WasPressedThisFrame())
            TratarDeUsar();
    }

    void LateUpdate()
    {
        // El temblor de la abstinencia: un vaivén chico e irregular, encima de donde esté la
        // cámara (caminando o usando algo). Si nada movió la cámara desde el cuadro anterior
        // (por ejemplo, con el auricular en la oreja), se parte de donde estaba sin temblor,
        // para que no se acumule.
        var base_ = camara.localRotation == conTemblor ? sinTemblor : camara.localRotation;
        sinTemblor = base_;
        if (temblorCamara > 0f)
        {
            float t = Time.time * 6f;
            base_ *= Quaternion.Euler((Mathf.PerlinNoise(t, 0.3f) - 0.5f) * 2f * temblorCamara,
                                      (Mathf.PerlinNoise(0.7f, t) - 0.5f) * 2f * temblorCamara, 0f);
        }
        camara.localRotation = conTemblor = base_;
    }

    Quaternion sinTemblor = Quaternion.identity, conTemblor = Quaternion.identity;

    void Mirar()
    {
        var valor = mirar.ReadValue<Vector2>();
        // El mouse da píxeles por cuadro; la palanca, cuánto está inclinada.
        var grados = mirar.activeControl?.device is Pointer ? valor * sensibilidadMouse : valor * (velocidadPalanca * Time.deltaTime);
        transform.Rotate(0f, grados.x, 0f);
        inclinacion = Mathf.Clamp(inclinacion - grados.y, -limiteVertical, limiteVertical);
        camara.localRotation = Quaternion.Euler(inclinacion, 0f, 0f);
    }

    void Caminar()
    {
        var entrada = Vector2.ClampMagnitude(mover.ReadValue<Vector2>(), 1f);
        var paso = (transform.right * entrada.x + transform.forward * entrada.y) * velocidad;
        caida = cuerpo.isGrounded ? -1f : caida + Physics.gravity.y * Time.deltaTime;
        cuerpo.Move((paso + Vector3.up * caida) * Time.deltaTime);
    }

    void TratarDeUsar()
    {
        // Se mira hasta lejos y después se compara con el alcance de lo que se miró: lo que está
        // en el piso (la dosis bajo el colchón) se alcanza desde más lejos.
        if (!Physics.Raycast(camara.position, camara.forward, out var golpe, 3f, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore))
            return;
        var objeto = golpe.collider.GetComponentInParent<Interactuable>();
        if (objeto != null && objeto.isActiveAndEnabled && golpe.distance <= (objeto.alcance > 0f ? objeto.alcance : alcance)
            && objeto.PuedeUsar(this))
            StartCoroutine(Usar(objeto));
    }

    IEnumerator Usar(Interactuable objeto)
    {
        Libre = false;
        yield return objeto.Usar(this);
        Soltar();
    }

    // ------------------------------------------------------------------------------------
    // Para los objetos que se usan (Interactuable)
    // ------------------------------------------------------------------------------------

    /// <summary>
    /// Si Elías puede ir al punto donde empieza el clip sin atravesar nada (por ejemplo, no está
    /// del otro lado de la puerta). <paramref name="espacio"/>: la raíz del escenario de Blender
    /// (las pistas están en sus coordenadas); <paramref name="propio"/>: el objeto que se usa,
    /// que puede estar en el camino.
    /// </summary>
    public bool LlegaAlInicio(string clip, Transform espacio, Transform propio, Matrix4x4? reubicar = null)
    {
        var inicio = (espacio.localToWorldMatrix * (reubicar ?? Matrix4x4.identity) * PistaCabeza(clip).EnTiempo(0f, Fps(clip))).GetPosition();
        return !Physics.Linecast(camara.position, inicio, out var golpe, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)
               || golpe.collider.transform.IsChildOf(propio);
    }

    /// <summary>
    /// Corre algo que no empezó el jugador (el despertar, un susto): mientras dura, Elías no
    /// responde a los controles. Al terminar, queda donde quedó la cabeza.
    /// </summary>
    public IEnumerator Escena(IEnumerator contenido)
    {
        Libre = false;
        yield return contenido;
        Soltar();
    }

    /// <summary>
    /// El despertar (Noche 1): Elías está en el suelo, corre el clip (por ejemplo, mirar_manos)
    /// desde su primer cuadro, sin llevar la cámara, y se levanta despacio. Va dentro de Escena.
    /// </summary>
    public IEnumerator Despertar(string clip, Transform espacio, float levantarse = 1.6f)
    {
        Poner(camara, espacio.localToWorldMatrix * PistaCabeza(clip).EnTiempo(0f, Fps(clip)));
        yield return Reproducir(clip, espacio, true);
        Ubicar();
        var desde = camara.localPosition;
        var ojos = new Vector3(0f, alturaOjos, 0f);
        for (float t = 0f; t < levantarse; t += Time.deltaTime)
        {
            camara.localPosition = Vector3.Lerp(desde, ojos, Mathf.SmoothStep(0f, 1f, t / levantarse));
            yield return null;
        }
        camara.localPosition = ojos;
    }

    /// <summary>
    /// Corre un clip de los brazos con la cámara de interacción. <paramref name="objetos"/>: los
    /// que se mueven con el clip (la puerta, el auricular), con el nombre de su pista en el JSON.
    /// Si <paramref name="volverAlReposo"/> es falso, los brazos se quedan en el último cuadro
    /// (por ejemplo, con el auricular en la oreja).
    /// </summary>
    public IEnumerator Reproducir(string clip, Transform espacio, bool volverAlReposo, params (string pista, Transform objeto)[] objetos) =>
        Reproducir(clip, espacio, volverAlReposo, new OpcionesClip(), objetos);

    /// <summary>
    /// Igual, y además avisa en cada cuadro en qué segundo del clip va (<paramref name="cadaCuadro"/>):
    /// para que un sonido caiga justo cuando la mano toma el auricular.
    /// </summary>
    public IEnumerator Reproducir(string clip, Transform espacio, bool volverAlReposo, System.Action<float> cadaCuadro,
                                  params (string pista, Transform objeto)[] objetos) =>
        Reproducir(clip, espacio, volverAlReposo, new OpcionesClip { cadaCuadro = cadaCuadro }, objetos);

    /// <summary>Lo que se puede cambiar al correr un clip.</summary>
    public class OpcionesClip
    {
        /// <summary>Se llama en cada cuadro con el segundo del clip.</summary>
        public System.Action<float> cadaCuadro;
        /// <summary>Corta el clip en este segundo (por ejemplo, para un corte a negro).</summary>
        public float hasta = float.PositiveInfinity;
        /// <summary>
        /// Mueve la cabeza del clip (en las coordenadas del escenario): para usar con otra puerta
        /// el clip que se hizo para una (ver PuertaDeEntrada).
        /// </summary>
        public Matrix4x4 reubicar = Matrix4x4.identity;
    }

    public IEnumerator Reproducir(string clip, Transform espacio, bool volverAlReposo, OpcionesClip opciones,
                                  params (string pista, Transform objeto)[] objetos)
    {
        var animacion = brazos.Clip(clip);
        float fps = Fps(clip);
        float duracion = Mathf.Min((datos.BuscarAnimacion(clip).cuadros - 1) / fps, opciones.hasta);
        var cabeza = PistaCabeza(clip);
        var espacioCabeza = espacio.localToWorldMatrix * opciones.reubicar;
        var cadaCuadro = opciones.cadaCuadro;
        var pistas = new EscenaBlender.Pista[objetos.Length];
        for (int i = 0; i < objetos.Length; i++)
        {
            pistas[i] = datos.BuscarPista(clip, objetos[i].pista);
            if (!reposos.ContainsKey(objetos[i].objeto)) // la primera vez que se usa está en reposo
                reposos[objetos[i].objeto] = objetos[i].objeto.localToWorldMatrix;
        }

        yield return LlevarCamara(espacioCabeza * cabeza.EnTiempo(0f, fps));

        // Lo que la mano agarra (la pista dice con qué mano, desde cuándo y, si lo suelta, hasta
        // cuándo) la sigue mientras la tiene: así tiembla con ella. Antes y después, sigue su
        // pista como la puerta (la taza vuelve a su lugar en el fregadero).
        var enLaMano = new Matrix4x4?[objetos.Length];
        bool hayManos = System.Array.Exists(pistas, p => p != null && !string.IsNullOrEmpty(p.mano));
        for (float t = 0f; ; t += Time.deltaTime)
        {
            float tc = Mathf.Min(t, duracion);
            brazos.Mostrar(animacion, tc);
            Poner(camara, espacioCabeza * cabeza.EnTiempo(tc, fps));
            if (hayManos)
                brazos.Evaluar(); // la pose de este cuadro, para saber dónde está la mano ahora
            for (int i = 0; i < objetos.Length; i++)
            {
                var p = pistas[i];
                if (p == null)
                    continue;
                var objeto = objetos[i].objeto;
                var cambio = espacio.localToWorldMatrix * p.CambioEnTiempo(tc, fps) * espacio.worldToLocalMatrix;
                var segunPista = cambio * reposos[objeto];
                if (!p.LoTiene(tc))
                {
                    Poner(objeto, segunPista);
                    continue;
                }
                var mano = brazos.Hueso(p.mano);
                enLaMano[i] ??= mano.worldToLocalMatrix * segunPista;
                Poner(objeto, mano.localToWorldMatrix * enLaMano[i].Value);
            }
            cadaCuadro?.Invoke(tc);
            if (t >= duracion)
                break;
            yield return null;
        }
        if (volverAlReposo)
            brazos.Reposo();
    }

    /// <summary>Espera a que el jugador vuelva a apretar Interactuar (por ejemplo, para colgar).</summary>
    public IEnumerator EsperarInteraccion()
    {
        do
            yield return null;
        while (!interactuar.WasPressedThisFrame());
    }

    EscenaBlender.Pista PistaCabeza(string clip) => datos.BuscarPista(clip, Cabeza);

    /// <summary>Dónde empieza la cabeza en el clip (en las coordenadas del escenario de Blender).</summary>
    public Matrix4x4 CabezaAlEmpezar(string clip) => PistaCabeza(clip).EnTiempo(0f, Fps(clip));

    /// <summary>
    /// Dónde está en reposo el objeto de la pista <paramref name="pista"/> del clip (en las
    /// coordenadas del escenario): para llevar el clip a otro objeto (ver RastroInteractivo).
    /// </summary>
    public Matrix4x4 ReposoDePista(string clip, string pista) => EscenaBlender.MatrizDeBlender(datos.BuscarPista(clip, pista).reposo);

    float Fps(string clip) => datos.BuscarAnimacion(clip).fps;

    /// <summary>
    /// Lleva la cámara, con suavidad, a <paramref name="destino"/> (en el mundo) y la deja ahí:
    /// para mirar por la mirilla. Va dentro de un Interactuable o de Escena.
    /// </summary>
    public IEnumerator Acercarse(Matrix4x4 destino) => LlevarCamara(destino);

    /// <summary>Lleva la cámara, con suavidad, de donde está a <paramref name="destino"/>.</summary>
    IEnumerator LlevarCamara(Matrix4x4 destino)
    {
        Vector3 p0 = camara.position, p1 = destino.GetPosition();
        Quaternion r0 = camara.rotation, r1 = destino.rotation;
        // Más lejos o más girada, más tarda (entre 0,3 y 0,8 s).
        float duracion = Mathf.Clamp(Vector3.Distance(p0, p1) / 1.5f + Quaternion.Angle(r0, r1) / 200f, 0.3f, 0.8f);
        for (float t = 0f; t < duracion; t += Time.deltaTime)
        {
            float u = Mathf.SmoothStep(0f, 1f, t / duracion);
            camara.SetPositionAndRotation(Vector3.Lerp(p0, p1, u), Quaternion.Slerp(r0, r1, u));
            yield return null;
        }
        Poner(camara, destino);
    }

    /// <summary>
    /// Elías queda donde terminó la cabeza, mirando hacia el mismo lado, y vuelve a responder.
    /// La cámara se queda donde está y vuelve sola a la altura de los ojos.
    /// </summary>
    void Soltar()
    {
        Ubicar();
        Libre = true;
    }

    /// <summary>
    /// Elías se para donde está la cabeza, con los ojos a su altura, sin volver a responder
    /// todavía. Para cuando la pantalla está a oscuras (la dosis), así no se lo ve levantarse.
    /// </summary>
    public void Pararse()
    {
        Ubicar();
        camara.localPosition = new Vector3(0f, alturaOjos, 0f);
    }

    void Ubicar()
    {
        Vector3 ojos = camara.position, frente = camara.forward;
        var plano = Vector3.ProjectOnPlane(frente, Vector3.up);
        cuerpo.enabled = false;
        transform.SetPositionAndRotation(new Vector3(ojos.x, transform.position.y, ojos.z),
                                         plano.sqrMagnitude > 1e-6f ? Quaternion.LookRotation(plano) : transform.rotation);
        cuerpo.enabled = true;
        inclinacion = Mathf.Clamp(-Mathf.Asin(Mathf.Clamp(frente.y, -1f, 1f)) * Mathf.Rad2Deg, -limiteVertical, limiteVertical);
        camara.SetPositionAndRotation(ojos, transform.rotation * Quaternion.Euler(inclinacion, 0f, 0f));
    }

    /// <summary>
    /// Si Elías ve <paramref name="punto"/>: está dentro de la imagen, a más de
    /// <paramref name="margen"/> del borde (en fracción de la imagen), y nada lo tapa.
    /// </summary>
    public bool Ve(Vector3 punto, float margen = 0.05f)
    {
        var cam = camara.GetComponent<Camera>();
        var v = cam.WorldToViewportPoint(punto);
        if (v.z <= 0f || v.x < margen || v.x > 1f - margen || v.y < margen || v.y > 1f - margen)
            return false;
        return !Physics.Linecast(camara.position, punto, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore);
    }

    static void Poner(Transform t, Matrix4x4 m) => t.SetPositionAndRotation(m.GetPosition(), m.rotation);
}
