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
    if "--sin-voces" not in sys.argv:
        voz("voz_tomas_otra_vez_sin_dormir", "¿Otra vez sin dormir?")
        voz("voz_eli_abreme", "Eli... ábreme.", detras_de_puerta=True)


main()
