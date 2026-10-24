// Muestra en pantalla la imagen del juego (480×270) con el acabado de la PS1:
//   - se amplía sin suavizado: cada píxel de la imagen es un bloque de píxeles duros;
//   - color de 15 bits: 32 niveles por canal, con dithering Bayer 4×4.
// Es la misma fórmula que ps1_post() en blender/scripts/prueba_estilo_pasillo.py, así que
// Unity y los renders de Blender dan el mismo resultado. El dithering se calcula por píxel
// de la imagen chica, no de la pantalla: el patrón crece con la imagen.
//
// Lo usa el RawImage del prefab PS1_Pantalla, y también la captura del editor
// (On the Nod > Capturar pantalla PS1).
//
// El corte a negro (Assets/Scripts/Fundido.cs) oscurece la imagen antes de cuantizarla, así que
// el fundido sale con el mismo dithering, como en la PS1. Es un valor global (_PS1Oscuridad):
// 0 se ve normal, 1 todo negro.
//
// El sudor de la abstinencia (Assets/Scripts/Abstinencia.cs, 6.2) pone la imagen borrosa y un
// poco más oscura en los bordes, cada vez más hacia el centro. Es otro valor global
// (_PS1Sudor): 0 nada, 1 del todo.
//
// Encima del fundido va el texto de TextoPS1 (la pantalla de guardado del cuaderno, los
// pensamientos de Elías), con su sombra: se ve aunque todo esté a negro, y también se cuantiza
// con dithering.
Shader "OnTheNod/PS1 Pantalla"
{
    Properties
    {
        [PerRendererData] _MainTex("Imagen", 2D) = "black" {}
        _Niveles("Niveles por canal", Float) = 32
        [ToggleUI] _Dithering("Dithering", Float) = 1

        // Los usa el sistema de UI (máscaras); no se tocan.
        [HideInInspector] _StencilComp("Stencil Comparison", Float) = 8
        [HideInInspector] _Stencil("Stencil ID", Float) = 0
        [HideInInspector] _StencilOp("Stencil Operation", Float) = 0
        [HideInInspector] _StencilWriteMask("Stencil Write Mask", Float) = 255
        [HideInInspector] _StencilReadMask("Stencil Read Mask", Float) = 255
        [HideInInspector] _ColorMask("Color Mask", Float) = 15
    }

    SubShader
    {
        Tags
        {
            "Queue" = "Transparent"
            "IgnoreProjector" = "True"
            "RenderType" = "Transparent"
            "PreviewType" = "Plane"
        }

        Stencil
        {
            Ref [_Stencil]
            Comp [_StencilComp]
            Pass [_StencilOp]
            ReadMask [_StencilReadMask]
            WriteMask [_StencilWriteMask]
        }

        Cull Off
        Lighting Off
        ZWrite Off
        ZTest [unity_GUIZTestMode]
        Blend Off
        ColorMask [_ColorMask]

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 4.5
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            // Se lee como Texture2D para saber su tamaño (GetDimensions) y leer píxeles exactos
            // (Load): el sistema de UI no siempre entrega _MainTex_TexelSize.
            Texture2D _MainTex;
            float _Niveles;
            float _Dithering;
            float _PS1Oscuridad; // global; sin poner vale 0
            float _PS1Sudor;     // global; sin poner vale 0

            // El texto (TextoPS1), del mismo tamaño que la imagen: cuánto tapa la letra cada
            // píxel, en el canal rojo, y su sombra, en el verde. Globales; sin poner, la
            // opacidad vale 0 y no se lee.
            Texture2D _PS1Texto;
            float _PS1TextoOpacidad;
            float4 _PS1TextoColor; // sRGB

            static const float kBayer[16] =
            {
                 0,  8,  2, 10,
                12,  4, 14,  6,
                 3, 11,  1,  9,
                15,  7, 13,  5
            };

            // Conversiones sRGB exactas (las de UnityCG son aproximadas y correrían los niveles).
            float3 LinealASrgb(float3 c)
            {
                c = max(c, 0.0);
                return c <= 0.0031308 ? c * 12.92 : 1.055 * pow(c, 1.0 / 2.4) - 0.055;
            }

            float3 SrgbALineal(float3 c)
            {
                return c <= 0.04045 ? c / 12.92 : pow((c + 0.055) / 1.055, 2.4);
            }

            v2f vert(appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            float4 frag(v2f i) : SV_Target
            {
                // Píxel de la imagen chica que cae aquí, leído tal cual: píxeles duros.
                uint ancho, alto;
                _MainTex.GetDimensions(ancho, alto);
                float2 tamano = float2(ancho, alto);
                float2 texel = clamp(floor(i.uv * tamano), 0.0, tamano - 1.0);
                float3 c = _MainTex.Load(int3(texel, 0)).rgb;

                // El sudor: hacia los bordes, el píxel se mezcla con los de alrededor (hasta 3
                // píxeles de la imagen chica) y se oscurece un poco
                if (_PS1Sudor > 0.0)
                {
                    float2 p = (texel + 0.5) / tamano * 2.0 - 1.0;
                    float borde = saturate((length(p * float2(1.0, 0.8)) - 0.5) / 0.7) * saturate(_PS1Sudor);
                    float radio = 3.0 * borde;
                    if (radio > 0.3)
                    {
                        float3 suma = c;
                        for (int k = 0; k < 8; k++)
                        {
                            float a = k * 0.7853982;
                            float2 d = float2(cos(a), sin(a)) * radio;
                            suma += _MainTex.Load(int3(clamp(texel + d, 0.0, tamano - 1.0), 0)).rgb;
                            suma += _MainTex.Load(int3(clamp(texel + d * 0.5, 0.0, tamano - 1.0), 0)).rgb;
                        }
                        c = suma / 17.0;
                    }
                    c *= 1.0 - 0.3 * borde;
                }

                // Se cuantiza el color como se guarda en un PNG (sRGB), igual que en Blender.
                #ifndef UNITY_COLORSPACE_GAMMA
                    c = LinealASrgb(c);
                #endif
                c *= 1.0 - saturate(_PS1Oscuridad);
                if (_PS1TextoOpacidad > 0.0)
                {
                    float2 letra = _PS1Texto.Load(int3(texel, 0)).rg;
                    float opacidad = saturate(_PS1TextoOpacidad);
                    c *= 1.0 - letra.g * opacidad;
                    c = lerp(c, _PS1TextoColor.rgb, letra.r * opacidad);
                }

                uint indice = ((uint)texel.y & 3u) * 4u + ((uint)texel.x & 3u);
                float umbral = (kBayer[indice] / 16.0 - 0.5 + 1.0 / 32.0) * _Dithering;
                float pasos = _Niveles - 1.0;
                c = saturate(floor(c * pasos + 0.5 + umbral) / pasos);

                #ifndef UNITY_COLORSPACE_GAMMA
                    c = SrgbALineal(c);
                #endif
                return float4(c, 1.0);
            }
            ENDCG
        }
    }
}
