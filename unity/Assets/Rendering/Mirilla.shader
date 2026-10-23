// La vista por la mirilla de la puerta del 4B: pasa una imagen rectilínea muy abierta (170°) a
// ojo de pez equidistante, dentro de un círculo, con los bordes borrosos (el vidrio) y oscuros.
// Es la misma cuenta que fisheye() en blender/scripts/dona_carmen.py, así que se ve como las
// vistas carmen_mirilla_*.png. La usa VistaMirilla (Assets/Scripts) para escribir en la imagen
// del juego de 480×270; el color de 15 bits y el dithering los pone después la pantalla PS1.
Shader "OnTheNod/Mirilla"
{
    Properties
    {
        _MainTex("Vista rectilínea", 2D) = "black" {}
        _MitadAngulo("Mitad del ángulo (grados)", Float) = 85
        _Diametro("Diámetro del círculo (fracción del alto)", Float) = 0.97
    }

    SubShader
    {
        Cull Off ZWrite Off ZTest Always

        Pass
        {
            CGPROGRAM
            #pragma vertex vert_img
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            float4 _MainTex_TexelSize;
            float _MitadAngulo;
            float _Diametro;
            float4 _Destino; // ancho y alto de la imagen de destino (lo pone VistaMirilla)

            float3 Muestra(float2 d)
            {
                // d: el punto en el círculo (radio 1). Equidistante: el ángulo crece parejo con el radio.
                float tmax = radians(_MitadAngulo);
                float rho = length(d);
                float th = min(rho, 1.0) * tmax;
                float k = rho > 1e-5 ? tan(th) / (tan(tmax) * rho) : tmax / tan(tmax);
                float2 uv = (d * k + 1.0) * 0.5;
                return tex2D(_MainTex, uv).rgb;
            }

            float4 frag(v2f_img i) : SV_Target
            {
                // Del píxel de la imagen (480×270) al círculo, que mide _Diametro del alto.
                float2 tam = _Destino.xy;
                float2 pix = i.uv * tam;
                float radio = tam.y * _Diametro * 0.5;
                float2 d = (pix - tam * 0.5) / radio;
                float rho = length(d);

                float3 c = Muestra(d);
                // Bordes borrosos, como el vidrio de una mirilla.
                float paso = 1.5 / radio;
                float3 borroso = (c + Muestra(d + float2(paso, 0)) + Muestra(d - float2(paso, 0))
                                  + Muestra(d + float2(0, paso)) + Muestra(d - float2(0, paso))) / 5.0;
                c = lerp(c, borroso, saturate((rho - 0.55) / 0.35));
                // Oscuro hacia el borde y negro afuera del círculo, con un tinte del vidrio.
                float vineta = pow(saturate((1.0 - rho) / 0.10), 0.8) * (1.0 - 0.30 * min(rho, 1.0) * min(rho, 1.0));
                c *= vineta * float3(0.96, 1.0, 0.90);
                return float4(c, 1.0);
            }
            ENDCG
        }
    }
}
