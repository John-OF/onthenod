r"""
Sonidos del juego, generados con Python (numpy), como los assets de Blender: para cambiar un
sonido se cambia el script y se vuelve a correr. Todo a 22.050 Hz y en mono, como en la PS1.

Sonidos (se sintetizan):
  telefono_timbre      un ciclo del timbre de un telefono fijo viejo (dos campanas que un
                       martillo golpea 20 veces por segundo): suena 1,2 s y calla hasta los
                       5 s. En Unity va en bucle.
  telefono_descolgar   el auricular que se levanta: el golpe del plastico y el clic del gancho
  telefono_colgar      el auricular que vuelve a la base: el golpe y un "tin" de las campanas
  telefono_estatica    la linea sin nadie (6.5): ruido en la banda del telefono, chasquidos y
                       un zumbido de la red electrica. En bucle, sin saltos.
  golpes_puerta        tres golpes con los nudillos en la puerta de entrada, oidos desde adentro
  llave_manija         la manija de la llave del fregadero al girar: chirrido de metal
  agua_taza            el agua que cae en la taza (1,75 s, lo que corre en el clip tomar_agua):
                       el tono sube a medida que la taza se llena; al cerrar, dos gotas
  taza_loza            la taza de loza contra el fregadero de metal (al tomarla y al dejarla)
  beber                tres tragos y el aire que sale despues

Voces PROVISIONALES (sintesis de voz de Windows, bajada de tono para que suene masculina).
Hay que reemplazarlas por voces grabadas:
  voz_tomas_otra_vez_sin_dormir   Tomas en el sofa (Noche 1): "¿Otra vez sin dormir?"
  voz_eli_abreme                  una voz detras de la puerta (Noche 1): "Eli, abreme"

Uso (desde la carpeta del proyecto):
  python audio\scripts\sonidos.py            todo
  python audio\scripts\sonidos.py --sin-voces   sin regenerar las voces provisionales

Salidas: unity/Assets/Audio/<nombre>.wav
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

SR = 22050
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESTINO = os.path.join(RAIZ, "unity", "Assets", "Audio")
rng = np.random.default_rng(4)


# ---------------------------------------------------------------------------
# Herramientas
# ---------------------------------------------------------------------------
def tiempo(segundos):
    return np.arange(int(round(segundos * SR))) / SR


def filtro(x, bajo=None, alto=None, orden=2):
    """Filtro por FFT con la forma de un Butterworth: deja pasar entre 'bajo' y 'alto' (Hz).
    Es circular: si la senal da la vuelta (un bucle), el resultado tambien."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if alto is not None:
        g /= np.sqrt(1 + (f / alto) ** (2 * orden))
    if bajo is not None:
        g /= np.sqrt(1 + (bajo / np.maximum(f, 1e-6)) ** (2 * orden))
    return np.fft.irfft(np.fft.rfft(x) * g, len(x))


def eco(x, cola=0.35, mezcla=0.18, brillo=4000):
    """Reverberacion de un cuarto chico: la senal convolucionada con ruido que se apaga."""
    t = tiempo(cola)
    ir = rng.standard_normal(len(t)) * np.exp(-t * 6.9 / cola)  # -60 dB al final de la cola
    ir = filtro(ir, alto=brillo)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    humedo = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
    return x + mezcla * humedo


def golpe(f, decae, largo, fase=0.0):
    """Un modo que suena y se apaga: seno amortiguado. Termina en cero de a poco (los
    ultimos 50 ms), para que cortarlo no haga un clic."""
    t = tiempo(largo)
    s = np.sin(2 * np.pi * f * t + fase) * np.exp(-t / decae)
    n = min(len(s), int(0.05 * SR))
    s[-n:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, n))
    return s


def mezclar(destino, senal, en):
    i = int(round(en * SR))
    if i < 0:
        senal, i = senal[-i:], 0
    j = min(len(destino), i + len(senal))
    destino[i:j] += senal[:j - i]


def guardar(nombre, x, pico=0.89):
    """Normaliza al pico (-1 dB) y guarda en 16 bits."""
    os.makedirs(DESTINO, exist_ok=True)
    x = x / max(np.max(np.abs(x)), 1e-9) * pico
    datos = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    ruta = os.path.join(DESTINO, nombre + ".wav")
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())
    print(f"[sonido] {nombre}: {len(x) / SR:.2f} s")


# ---------------------------------------------------------------------------
# El telefono
# ---------------------------------------------------------------------------
# Dos campanas de bronce de distinto tono; cada una suena con varios parciales que se apagan.
CAMPANAS = [
    [(1120, 1.0, 0.70), (2470, 0.55, 0.35), (3460, 0.30, 0.22), (5480, 0.16, 0.12)],
    [(1255, 1.0, 0.65), (2760, 0.50, 0.32), (3900, 0.28, 0.20), (6150, 0.14, 0.10)],
]


def campanazo(cual, fuerza=1.0, largo=1.2):
    s = np.zeros(int(largo * SR))
    for f, a, d in CAMPANAS[cual]:
        s += a * golpe(f * rng.uniform(0.998, 1.002), d, largo, rng.uniform(0, 2 * np.pi))
    # el martillo contra el metal: un clic corto
    clic = filtro(rng.standard_normal(int(0.004 * SR)), bajo=2500) * np.linspace(1, 0, int(0.004 * SR))
    s[:len(clic)] += 0.6 * clic
    return s * fuerza


def telefono_timbre():
    ciclo, suena, hz = 5.0, 1.2, 20.0
    x = np.zeros(int(ciclo * SR))
    n = int(suena * hz)
    for k in range(n):
        # el martillo va y viene: golpea una campana y la otra; al final pierde fuerza
        fuerza = 0.75 + 0.25 * np.sin(np.pi * min(1, k / 4)) * (1 - 0.3 * (k / n) ** 4)
        mezclar(x, campanazo(k % 2, fuerza, largo=2.0), k / hz + rng.uniform(-0.002, 0.002))
    # la caja del telefono vibra con el martillo
    zumbido = filtro(rng.standard_normal(len(x)), bajo=150, alto=900) * 0.08
    zumbido[int(suena * SR):] = 0
    x += zumbido
    guardar("telefono_timbre", eco(x, cola=0.4, mezcla=0.22))


def golpe_plastico(grave=180, decae=0.05, largo=0.3, fuerza=1.0):
    t = tiempo(largo)
    cuerpo = filtro(rng.standard_normal(len(t)), bajo=grave, alto=grave * 5) * np.exp(-t / decae)
    clac = filtro(rng.standard_normal(len(t)), bajo=1800, alto=6000) * np.exp(-t / 0.006)
    return (cuerpo + 0.8 * clac) * fuerza


def telefono_descolgar():
    x = np.zeros(int(0.5 * SR))
    mezclar(x, golpe_plastico(220, 0.03, 0.3, 0.6), 0.0)           # el auricular se despega
    t = tiempo(0.05)
    gancho = np.sign(np.sin(2 * np.pi * 900 * t)) * np.exp(-t / 0.004)  # el clic del gancho
    mezclar(x, filtro(gancho, alto=5000) * 0.5, 0.06)
    mezclar(x, golpe_plastico(300, 0.02, 0.2, 0.25), 0.13)         # roce al levantarlo
    guardar("telefono_descolgar", eco(x, cola=0.25, mezcla=0.15))


def telefono_colgar():
    x = np.zeros(int(1.0 * SR))
    mezclar(x, golpe_plastico(140, 0.07, 0.4, 1.0), 0.0)           # el auricular cae en la base
    t = tiempo(0.05)
    gancho = np.sign(np.sin(2 * np.pi * 800 * t)) * np.exp(-t / 0.004)
    mezclar(x, filtro(gancho, alto=5000) * 0.4, 0.008)
    mezclar(x, campanazo(0, 0.12, largo=0.9), 0.01)                # el "tin" de la campana
    guardar("telefono_colgar", eco(x, cola=0.3, mezcla=0.18))


def telefono_estatica():
    largo = 8.0
    n = int(largo * SR)
    t = np.arange(n) / SR
    # ruido de la linea en la banda del telefono (300 a 3400 Hz), que respira despacio
    soplido = filtro(rng.standard_normal(n), bajo=300, alto=3400, orden=3)
    soplido *= 0.55 + 0.25 * np.sin(2 * np.pi * t / 4.0) + 0.15 * np.sin(2 * np.pi * t / largo * 3 + 1.0)
    # zumbido de la red electrica (60 Hz en Mexico y gran parte de Latinoamerica) y sus armonicos
    zumbido = sum(a * np.sin(2 * np.pi * 60 * k * t) for k, a in ((1, 0.25), (3, 0.12), (5, 0.06)))
    zumbido = filtro(zumbido, bajo=300, alto=3400)
    # chasquidos: impulsos al azar que la linea deja pasar
    chasq = np.zeros(n)
    for _ in range(70):
        i = rng.integers(0, n)
        chasq[i] = rng.uniform(-1, 1) * rng.uniform(3, 12)
    chasq = filtro(chasq, bajo=400, alto=3000)
    x = soplido + zumbido + chasq
    # cortes cortos de la senal, como si la linea se fuera un instante
    for c in (1.7, 5.3):
        i, j = int(c * SR), int((c + 0.18) * SR)
        x[i:j] *= np.linspace(1, 0.15, j - i) ** 0.5
    guardar("telefono_estatica", x, pico=0.7)


# ---------------------------------------------------------------------------
# La puerta de entrada
# ---------------------------------------------------------------------------
# Modos de una puerta de madera golpeada (frecuencia, amplitud, cuanto tarda en apagarse)
PUERTA = [(85, 1.0, 0.09), (128, 0.8, 0.07), (196, 0.6, 0.05), (310, 0.45, 0.035),
          (470, 0.3, 0.025), (720, 0.22, 0.018), (1150, 0.15, 0.010)]


def nudillo(fuerza=1.0):
    largo = 0.35
    s = np.zeros(int(largo * SR))
    for f, a, d in PUERTA:
        s += a * golpe(f * rng.uniform(0.97, 1.03), d, largo, rng.uniform(0, 2 * np.pi))
    t = tiempo(largo)
    contacto = filtro(rng.standard_normal(len(t)), bajo=600, alto=4000) * np.exp(-t / 0.004)
    return (s + 0.5 * contacto) * fuerza


def golpes_puerta():
    x = np.zeros(int(1.6 * SR))
    for en, fuerza in ((0.0, 1.0), (0.31, 0.85), (0.60, 1.0)):
        mezclar(x, nudillo(fuerza), en + rng.uniform(-0.01, 0.01))
    guardar("golpes_puerta", eco(x, cola=0.45, mezcla=0.25, brillo=2500))


# ---------------------------------------------------------------------------
# El agua del fregadero (el clip tomar_agua de brazos_animaciones.py)
# ---------------------------------------------------------------------------
AGUA_CORRE = 1.75  # cuanto corre el agua en el clip (AGUA en brazos_animaciones.py)


def filtro_que_cambia(x, centro, ancho=0.3):
    """Resonancia que se mueve en el tiempo: centro(t) es su frecuencia (Hz) a los t segundos.
    Se filtra por ventanas que se solapan; ancho es su ancho, en octavas naturales."""
    n, salto = 1024, 256
    ventana = np.hanning(n)
    f = np.maximum(np.fft.rfftfreq(n, 1 / SR), 1.0)
    largo = np.concatenate([x, np.zeros(n)])
    y, peso = np.zeros(len(largo)), np.zeros(len(largo))
    for i in range(0, len(x), salto):
        g = np.exp(-0.5 * (np.log(f / centro((i + n / 2) / SR)) / ancho) ** 2)
        y[i:i + n] += np.fft.irfft(np.fft.rfft(largo[i:i + n] * ventana) * g, n) * ventana
        peso[i:i + n] += ventana ** 2
    return y[:len(x)] / np.maximum(peso[:len(x)], 1e-3)


def suavizar_bordes(x, entra=0.005, sale=0.05):
    a, b = int(entra * SR), int(sale * SR)
    x[:a] *= np.linspace(0, 1, a)
    x[-b:] *= np.linspace(1, 0, b)
    return x


def llave_manija():
    # El metal se pega y se suelta muchas veces por segundo (stick-slip): un tren de pulsos
    # que acelera mientras gira, con las resonancias de la llave
    largo = 0.45
    t = tiempo(largo)
    f0 = 150 + 110 * t / largo + 20 * np.sin(2 * np.pi * 6 * t)
    pulsos = np.maximum(np.sin(2 * np.pi * np.cumsum(f0) / SR), 0) ** 14
    chirrido = filtro(pulsos, bajo=900, alto=3400, orden=3)
    roce = filtro(rng.standard_normal(len(t)), bajo=1500, alto=6000) * 0.12
    temblor = filtro(rng.standard_normal(len(t)), alto=25)
    temblor = 0.7 + 0.3 * temblor / np.max(np.abs(temblor))
    x = (chirrido / np.max(np.abs(chirrido)) + roce) * np.sin(np.pi * t / largo) ** 0.6 * temblor
    guardar("llave_manija", eco(suavizar_bordes(x), cola=0.3, mezcla=0.2))


def gota(f=2100):
    t = tiempo(0.12)
    barrido = f * (1 + 0.6 * np.exp(-t / 0.01))  # la gota "plink": el tono cae al principio
    return np.sin(2 * np.pi * np.cumsum(barrido) / SR) * np.exp(-t / 0.025)


def agua_taza():
    largo = AGUA_CORRE + 0.5
    n = int(largo * SR)
    t = np.arange(n) / SR
    corre = t < AGUA_CORRE
    # el chorro: ruido que borbotea al azar, sin los agudos (si no, suena a estatica)
    borboteo = filtro(rng.standard_normal(n), alto=35)
    borboteo /= np.max(np.abs(borboteo))
    chorro = filtro(rng.standard_normal(n), bajo=400, alto=2500, orden=3) * (0.7 + 0.3 * borboteo)
    # la taza se llena: su resonancia sube de 380 a 1500 Hz
    subida = lambda s: 380 * (1500 / 380) ** min(s / AGUA_CORRE, 1.0)  # noqa: E731
    llena = filtro_que_cambia(rng.standard_normal(n), subida)
    # burbujas: cada una es un "plip" corto cuyo tono sube, cerca de la resonancia de la taza
    burbujas = np.zeros(n)
    for _ in range(int(AGUA_CORRE * 45)):
        en = rng.uniform(0.0, AGUA_CORRE - 0.03)
        f = subida(en) * rng.uniform(1.2, 2.2)
        tb = tiempo(rng.uniform(0.012, 0.03))
        plip = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.5 * tb / tb[-1])) / SR) * np.exp(-tb / (tb[-1] / 3))
        mezclar(burbujas, plip * rng.uniform(0.3, 1.0), en)
    # las canerias viejas del edificio
    canerias = filtro(rng.standard_normal(n), bajo=60, alto=180)
    x = (0.25 * chorro / np.max(np.abs(chorro)) + llena / np.max(np.abs(llena))
         + 0.6 * burbujas / np.max(np.abs(burbujas)) + 0.2 * canerias / np.max(np.abs(canerias)))
    x = filtro(x, alto=4500)
    entra = np.minimum(1.0, t / 0.03)
    sale = np.clip((AGUA_CORRE - t) / 0.12, 0.0, 1.0)  # la llave se cierra
    x *= entra * np.where(corre, 1.0, sale)
    mezclar(x, gota(2300) * 0.35, AGUA_CORRE + 0.12)
    mezclar(x, gota(1900) * 0.25, AGUA_CORRE + 0.31)
    guardar("agua_taza", eco(x, cola=0.35, mezcla=0.2), pico=0.75)


def taza_loza():
    # la loza: parciales agudos que se apagan rapido; el fregadero: un golpe de metal sordo
    largo = 0.45
    s = np.zeros(int(largo * SR))
    for f, a, d in ((2380, 1.0, 0.07), (3950, 0.6, 0.045), (5650, 0.35, 0.03), (430, 0.5, 0.03)):
        s += a * golpe(f * rng.uniform(0.99, 1.01), d, largo, rng.uniform(0, 2 * np.pi))
    t = tiempo(largo)
    s += filtro(rng.standard_normal(len(t)), bajo=1200, alto=7000) * np.exp(-t / 0.003) * 0.6
    guardar("taza_loza", eco(s, cola=0.3, mezcla=0.2))


def trago():
    t = tiempo(0.3)
    garganta = np.sin(2 * np.pi * np.cumsum(260 - 120 * np.minimum(t / 0.08, 1)) / SR) * np.exp(-t / 0.05)
    humedo = filtro(rng.standard_normal(len(t)), bajo=700, alto=3000) * np.exp(-t / 0.012) * 0.5
    return garganta + humedo


def beber():
    x = np.zeros(int(1.4 * SR))
    for en, fuerza in ((0.05, 1.0), (0.42, 0.9), (0.78, 0.8)):
        mezclar(x, trago() * fuerza, en + rng.uniform(-0.02, 0.02))
    # el aire que sale por la nariz despues de beber
    t = tiempo(0.45)
    aire = filtro(rng.standard_normal(len(t)), bajo=300, alto=2500) * np.sin(np.pi * t / 0.45) ** 2 * 0.35
    mezclar(x, aire, 0.95)
    guardar("beber", suavizar_bordes(x), pico=0.8)


# ---------------------------------------------------------------------------
# Voces provisionales
# ---------------------------------------------------------------------------
def voz(nombre, texto, tono=0.8, detras_de_puerta=False):
    """Sintesis de voz de Windows (Sabina, es-MX), bajada de tono con ffmpeg. PROVISIONAL."""
    with tempfile.TemporaryDirectory() as tmp:
        crudo = os.path.join(tmp, "crudo.wav")
        ps = ("Add-Type -AssemblyName System.Speech; "
              "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
              "$s.SelectVoice('Microsoft Sabina Desktop'); $s.Rate = -2; "
              f"$s.SetOutputToWaveFile('{crudo}'); $s.Speak('{texto}'); $s.Dispose()")
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
        filtros = [f"asetrate=22050*{tono}", "aresample=22050", f"atempo={1 / tono:.4f}"]
        if detras_de_puerta:
            filtros += ["lowpass=f=900", "highpass=f=120", "volume=0.8"]
        else:
            filtros += ["highpass=f=90"]
        salida = os.path.join(tmp, "listo.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", crudo, "-af", ",".join(filtros),
                        "-ar", str(SR), "-ac", "1", salida], check=True)
        with wave.open(salida, "rb") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    guardar(nombre, eco(x, cola=0.3, mezcla=0.2 if detras_de_puerta else 0.12))


# ---------------------------------------------------------------------------
def main():
    telefono_timbre()
    telefono_descolgar()
    telefono_colgar()
    telefono_estatica()
    golpes_puerta()
    llave_manija()
    agua_taza()
    taza_loza()
    beber()
    if "--sin-voces" not in sys.argv:
        voz("voz_tomas_otra_vez_sin_dormir", "¿Otra vez sin dormir?")
        voz("voz_eli_abreme", "Eli... ábreme.", detras_de_puerta=True)


main()
