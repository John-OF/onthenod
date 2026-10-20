#ifndef ON_THE_NOD_PS1_VERTICES_INCLUDED
#define ON_THE_NOD_PS1_VERTICES_INCLUDED

// Temblor de vértices de la PS1 (vertex snapping).
// La consola guardaba la posición de cada vértice en pantalla como un número entero de
// píxeles, así que al moverse la cámara los vértices saltan de un píxel al siguiente en
// vez de deslizarse. Aquí se redondea la posición a la cuadrícula de píxeles de la imagen
// que se está dibujando (_ScreenParams): en el juego es la imagen de 480×270; en la vista
// de escena del editor es la ventana entera, y el temblor casi no se nota.
float4 PS1SnapVertex(float4 positionCS)
{
    // Los vértices detrás de la cámara no se tocan (w <= 0 daría divisiones inválidas).
    if (positionCS.w <= 0.0)
        return positionCS;

    float2 grid = _ScreenParams.xy * 0.5; // la pantalla va de -1 a 1: dos mitades
    float2 ndc = positionCS.xy / positionCS.w;
    ndc = round(ndc * grid) / grid;
    positionCS.xy = ndc * positionCS.w;
    return positionCS;
}

#endif
