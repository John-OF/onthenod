#ifndef ON_THE_NOD_PS1_NIEBLA_INCLUDED
#define ON_THE_NOD_PS1_NIEBLA_INCLUDED

// Niebla iluminada: la luz que la niebla desvía hacia la cámara cerca de cada luz.
// Da el halo de los focos y la bruma del fondo, como la niebla volumétrica de Blender.
// La pérdida de luz con la distancia la pone la niebla normal de la escena
// (Lighting > Environment > Fog, exponencial); esto solo suma el brillo.
// Los datos los carga el componente NieblaPS1 (NieblaPS1.cs).

#define PS1_NIEBLA_MAX_LUCES 8

float4 _PS1NieblaLuces;                              // x: cuántas luces hay
float4 _PS1NieblaDispersion;                         // rgb: luz desviada por metro (densidad × color)
float4 _PS1NieblaPosicion[PS1_NIEBLA_MAX_LUCES];     // xyz: posición; w: 1 / alcance²
float4 _PS1NieblaColor[PS1_NIEBLA_MAX_LUCES];        // rgb: color × intensidad, en lineal
float4 _PS1NieblaFoco[PS1_NIEBLA_MAX_LUCES];         // xyz: hacia dónde apunta un spot; w: 1 si es spot
float4 _PS1NieblaCono[PS1_NIEBLA_MAX_LUCES];         // xy: caída del cono, como la calcula URP

half3 PS1NieblaIluminada(float3 positionWS)
{
    int cantidad = (int)_PS1NieblaLuces.x;
    if (cantidad <= 0)
        return half3(0, 0, 0);

    float3 camara = GetCameraPositionWS();
    float3 rayo = positionWS - camara;
    float largo = length(rayo);
    float3 dir = rayo / max(largo, 1e-4);

    float3 total = 0;
    [loop]
    for (int i = 0; i < min(cantidad, PS1_NIEBLA_MAX_LUCES); i++)
    {
        float3 luz = _PS1NieblaPosicion[i].xyz;

        // Punto del rayo más cercano a la luz (a t0 de la cámara) y su distancia h a la luz.
        float t0 = dot(luz - camara, dir);
        float h = max(length(camara + dir * t0 - luz), 0.05);

        // La luz cae con el cuadrado de la distancia. Sumada a lo largo del rayo, desde la
        // cámara (t = 0) hasta la superficie (t = largo), la integral tiene forma exacta:
        //   ∫ dt / (h² + (t - t0)²) = (atan((largo - t0) / h) + atan(t0 / h)) / h
        float integral = (atan((largo - t0) / h) + atan(t0 / h)) / h;

        // Alcance de la luz y cono del spot, medidos en ese punto más cercano.
        float3 punto = camara + dir * clamp(t0, 0.0, largo);
        float3 desdeLuz = punto - luz;
        float d2 = dot(desdeLuz, desdeLuz);
        float alcance = saturate(1.0 - pow(d2 * _PS1NieblaPosicion[i].w, 2.0));
        alcance *= alcance;

        float cono = 1.0;
        if (_PS1NieblaFoco[i].w > 0.5)
        {
            float coseno = dot(desdeLuz * rsqrt(max(d2, 1e-6)), _PS1NieblaFoco[i].xyz);
            cono = saturate(coseno * _PS1NieblaCono[i].x + _PS1NieblaCono[i].y);
            cono *= cono;
        }

        total += _PS1NieblaColor[i].rgb * (integral * alcance * cono);
    }

    // Dispersión pareja en todas direcciones: (dispersión / 4π) por la intensidad de Blender,
    // que es π veces la de URP. Queda dispersión / 4.
    return (half3)(total * _PS1NieblaDispersion.rgb * 0.25);
}

#endif
