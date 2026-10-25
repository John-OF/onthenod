# On the Nod — Documento de diseño

> Título: ***On the Nod*** (ver sección 14).
> Versión 0.4 · 19 de octubre de 2026

---

## 1. Resumen

Elías es adicto a la heroína y está intentando dejarla solo, encerrado en su departamento: el 4B de un edificio viejo. Hace ocho meses, su hermano menor, Tomás, murió de una sobredosis en ese mismo departamento. Elías tenía el teléfono en la mano y no llamó a nadie.

Durante cinco noches de abstinencia, el edificio se deforma con su culpa. Tomás aparece vivo, como si nada hubiera pasado, y de pronto aparece muerto. Elías tiene que distinguir qué es real, resistir la tentación de consumir y, al final, decidir si hace la llamada que no hizo aquella noche.

| | |
|---|---|
| **Género** | Terror psicológico: exploración, puzzles y huida. Sin combate. |
| **Estilo** | 3D low poly con estética de PlayStation 1. |
| **Cámara** | Primera persona. |
| **Referencias** | Silent Hill 2, P.T., Layers of Fear, Amnesia, Hellblade. |
| **Herramientas** | Unity 6 y Blender 5.2. |
| **Duración** | 2–3 horas la primera partida; 4–5 horas con todos los finales. |

---

## 2. Pilares de diseño

Toda decisión del juego debe servir al menos a uno de estos pilares.

1. **No puedes confiar en lo que ves.** La paranoia es una mecánica, no decoración.
2. **El camino fácil destruye; el difícil salva.** Consumir alivia ahora y cobra después.
3. **Estás indefenso.** No hay combate: solo huir, esconderse y enfrentar la verdad.
4. **Todo gira alrededor de una llamada.** El teléfono es el hilo de la historia, de las mecánicas y del sonido.

---

## 3. Historia

### 3.1 Lo que pasó (la verdad)

- **Infancia.** Elías le lleva seis años a Tomás. Su madre es enfermera de turno nocturno y su padre es taxista; casi nunca están. Elías cuida a Tomás: lo lleva a la escuela, le hace la comida, lo defiende. La frase de su madre: *«Cuida a tu hermano»*.
- **Elías, 19 años.** Empieza con pastillas en fiestas. A los 21 ya se inyecta heroína.
- **Tomás, 17 años.** Elías le da su primera dosis: *«Pruébala, no pasa nada»*. Desde entonces consumen juntos. Tomás lo admira y lo sigue en todo.
- **La familia se rompe.** Elías roba en casa para consumir: las joyas de su madre, la tele, el dinero del taxi. Su padre lo echa. Tomás se va con él.
- **Tomás intenta salir.** Pasa tres meses limpio y vuelve a casa de sus padres. Es la única buena noticia que la familia ha tenido en años.
- **La noche.** Tomás llama a Elías, orgulloso: *«Tres meses, Eli»*. Elías lo invita al 4B a celebrar y le ofrece: *«Una más, como antes»*. Después de tres meses limpio, el cuerpo de Tomás ya no la tolera. Se desploma en el baño y casi no respira. Elías, drogado y con miedo a la policía (tiene antecedentes y droga en el departamento), toma el teléfono… y no llama. Doña Carmen, la vecina, oye algo y toca la puerta; Elías no abre. Se convence de que Tomás solo está "durmiéndola". Se queda dormido. En la mañana suena el teléfono: es su madre. *«¿Dónde está tu hermano? No llegó a dormir.»* Con Tomás muerto en el baño, Elías responde: *«No sé.»*
- **Después.** Elías cuenta otra versión: Tomás llegó ya drogado, él dormía, lo encontró en la mañana y llamó a la ambulancia. Su padre no le cree. Su madre no sabe qué creer, pero lo sigue llamando cada noche. Elías nunca contesta.

### 3.2 Lo que Elías se cuenta (la mentira)

El juego empieza creyendo la versión de Elías. Sus primeros recuerdos lo muestran llamando a la ambulancia. Poco a poco aparecen detalles que no cuadran, hasta que en la Noche 5 el registro del teléfono lo confirma: esa noche no hubo ninguna llamada saliente.

**El giro:** a lo largo del juego, Tomás vivo le repite a Elías *«Una más, como antes»*, como si la tentación viniera de él. En la Noche 5 se revela que esa frase nunca fue de Tomás: es lo que Elías le dijo a él.

### 3.3 El presente

Ocho meses después. Elías vive solo en el 4B. Ha decidido dejar la droga por su cuenta, sin pedir ayuda, porque pedir ayuda significaría contar la verdad. El juego cubre sus primeras cinco noches de abstinencia.

Desde aquella noche, la puerta del baño está cerrada. Elías nunca la abre.

### 3.4 Capas ocultas: referencias bíblicas y poéticas

Debajo de la historia hay una segunda capa para quien la quiera encontrar. El juego no es religioso ni poético: las referencias están escondidas en el mundo como huevos de pascua.

**Reglas**
1. **Funcionan sin conocerlas.** Cada referencia se lee como una frase u objeto normal. Quien la reconoce encuentra un segundo sentido; quien no, no pierde nada.
2. **Viven en el mundo y nunca se explican.** Una Biblia subrayada en casa de la madre, un poema copiado en un cuaderno escolar, algo escrito a mano en el elevador, una frase en un diálogo. Nadie las recita ni las comenta.
3. **Con moderación.** Como mucho una cita explícita por noche; el resto, escondido.
4. **Solo textos de dominio público**, en español y en inglés: la Biblia Reina-Valera 1909 y la King James, y poemas publicados antes de 1929 (Vallejo, Bécquer, Dickinson, Poe). Antes de usarlos en el juego, verificar cada cita contra una edición confiable. Las citas bíblicas de esta sección se verificaron el 19 de octubre de 2026 contra la Reina-Valera Antigua (1909) y la King James de BibleGateway. Falta verificar los poemas.

#### La Biblia

**Caín y Abel: la pregunta** — Génesis 4:9
> «¿Dónde está Abel tu hermano? Y él respondió: No sé; ¿soy yo guarda de mi hermano?»
> *"Where is Abel thy brother? And he said, I know not: Am I my brother's keeper?"*

Es el centro de todo: un hermano muerto y otro que responde "no sé". "No sé" es la frase con la que Elías se defiende durante todo el juego, y es lo que le contesta a su madre la mañana en que Tomás amaneció muerto (ver 3.1). En la casa de los padres hay una Biblia abierta en Génesis 4.

**La sangre que clama** — Génesis 4:10
> «La voz de la sangre de tu hermano clama a mí desde la tierra.»
> *"The voice of thy brother's blood crieth unto me from the ground."*

Es el teléfono que suena cada noche. En la Noche 5, el timbre suena desde debajo del piso del baño.

**La marca y la tierra de Nod** — Génesis 4:12-16
> «Errante y extranjero serás en la tierra.» … «Y habitó en tierra de Nod, al oriente de Edén.»
> *"A fugitive and a vagabond shalt thou be in the earth." … "And dwelt in the land of Nod, on the east of Eden."*

Caín queda marcado y condenado a vagar; Elías tiene los brazos marcados y no puede salir del edificio. *Nod* significa "errante", y en inglés *to nod* es cabecear bajo el efecto de la heroína. En el elevador hay un botón sin número, con una sola letra: **N**. De aquí sale el título del juego.

**Tomás el incrédulo** — Juan 20:25
> «Si no viere en sus manos la señal de los clavos… no creeré.»
> *"Except I shall see in his hands the print of the nails… I will not believe."*

Tomás necesitaba ver para creer: por eso su cámara muestra la verdad. En la correa de la Polaroid escribió *«Si no hay foto, no pasó»*. Y pedía ver las marcas en las manos, como las que Elías tiene en los brazos.

**Elías bajo el enebro** — 1 Reyes 19:4-7
> «Y deseando morirse, dijo: Baste ya, oh Jehová, quita mi alma…» … «Levántate, come: porque gran camino te resta.»
> *"He requested for himself that he might die…" … "Arise and eat; because the journey is too great for thee."*

Es el pasaje bíblico más directo sobre querer morir, y la respuesta no es un reproche: es pan, agua y descanso. Así funciona la comida que Doña Carmen le deja en la puerta (ver 6.10). Y el protagonista lleva el nombre del profeta: es su misma historia.

**El buen samaritano** — Lucas 10:29
> «¿Y quién es mi prójimo?»
> *"And who is my neighbour?"*

Doña Carmen es la que se detiene cuando nadie más lo hace. En inglés el juego de palabras es directo: *neighbor* significa vecino y prójimo a la vez.

**El hijo pródigo** — Lucas 15:20-24
> «Y como aún estuviese lejos, viólo su padre, y fue movido a misericordia, y corrió…» … «Este mi hijo muerto era, y ha revivido; habíase perdido, y es hallado.»
> *"When he was yet a great way off, his father saw him, and had compassion, and ran…" … "This my son was dead, and is alive again; he was lost, and is found."*

El hijo que despilfarró lo de su familia y vuelve. Es el arco del padre: en todo el juego nunca mira a Elías, y en el final bueno sí (ver 4.1).

**Lázaro** (opcional) — Juan 11:39
> «Quitad la piedra.» … «Señor, hiede ya, que es de cuatro días.»
> *"Take ye away the stone." … "Lord, by this time he stinketh: for he hath been dead four days."*

Abrir la puerta del baño en la Noche 5 es quitar la piedra. Lo que hay detrás ya no es Tomás vivo.

#### Poesía

**César Vallejo, «A mi hermano Miguel»** (1918). Vallejo le escribe a su hermano muerto como si siguieran jugando a las escondidas:
> «Ahora yo me escondo, / como antes, todas estas oraciones / vespertinas, y espero que tú no des conmigo.»
> «Miguel, tú te escondiste / una noche de agosto, al alborear; / pero, en vez de ocultarte riendo, estabas triste.»
> «Oye, hermano, no tardes / en salir. Bueno? Puede inquietarse mamá.»

Es la referencia más importante. Elías y Tomás jugaban a las escondidas de niños (ver 4.1), y el poema dice "como antes", la misma frase de la tentación. En el juego, el poema está copiado en un cuaderno escolar de Tomás; cuando Tomás muerto persigue a Elías, cuenta como en el juego de niños; y en la Noche 5, frente a la puerta del baño, Elías dice: *«No tardes en salir. Puede inquietarse mamá.»*

**César Vallejo, «Los heraldos negros»** (1918)
> «Hay golpes en la vida, tan fuertes… ¡Yo no sé!»

Son los golpes en la puerta de la Noche 1. Y otra vez "yo no sé", como Caín y como Elías.

**Emily Dickinson, «I felt a Funeral, in my Brain»** (c. 1861)
> *"And then a Plank in Reason, broke, / And I dropped down, and down –"*

Un poema sobre la mente que se rompe. Aparece escrito a mano dentro del elevador que baja a pisos que no existen (Noche 2). Es un guiño para el público angloparlante.

**Edgar Allan Poe, «The Tell-Tale Heart»** (1843)
Un hombre insiste en que no está loco mientras oye latir, bajo el piso, el corazón del muerto, hasta que confiesa. En la Noche 5, el latido de la abstinencia se mezcla con otro que viene de debajo del baño y no se detiene hasta que Elías dice la verdad.

**Gustavo Adolfo Bécquer, Rima LXXIII** (1871)
> «¡Dios mío, qué solos se quedan los muertos!»

Lo dice la madre frente a la tumba de Tomás, en el epílogo del final bueno.

---

## 4. Personajes

**Elías (27)** — Protagonista. Flaco, ojeroso, con los brazos destrozados por las inyecciones. Inteligente, irónico y muy bueno para mentirse a sí mismo. Quiere dejar la droga, pero no quiere pedir ayuda.

**Tomás (murió a los 20)** — El hermano menor. Tiene dos versiones:
- **Vivo: la negación y la tentación.** Simpático, bromista, igual que antes. Aparece en el sofá, en el pasillo, en los recuerdos. Ofrece dosis: *«Una más, como antes»*. El jugador nunca sabe si está ahí.
- **Muerto: la culpa.** Aparece de golpe donde estaba el vivo. Empeora a lo largo del juego: recién muerto (piel gris, labios morados, espuma en la boca), luego en descomposición y al final hecho calavera. En algunas secuencias persigue a Elías. No se le puede vencer, solo evitar.

**Eva, la madre** — Enfermera. Es la voz del teléfono: llama cada noche. Representa la salida.

**José, el padre** — Taxista. Ira y silencio. En los recuerdos aparece siempre de espaldas: nunca mira a Elías.

**Doña Carmen, la vecina del 4A** — Viuda, mayor. Toca la puerta, le deja comida, le dice *«te escuché anoche»*. Elías cree que lo espía y que lo va a denunciar, y el jugador sospecha que es una alucinación. **Giro:** es lo único completamente real del juego. Siempre estuvo ahí para ayudar.

### 4.1 Relaciones

**Elías y Tomás: el guardián**
- Elías lo crió más que sus padres. Tomás lo imitaba en todo: la música, la forma de hablar y, al final, la droga.
- **Las escondidas.** Su juego de niños. Elías contaba hasta diez (*«…ocho, nueve, diez. ¡Listo o no, ahí voy!»*) y Tomás siempre se escondía en el mismo lugar: el baño. Elías fingía no encontrarlo para que ganara.
- **La Polaroid.** Elías se la regaló cuando Tomás cumplió 12, antes de la droga. Es lo último que le regaló sin dinero robado. Tomás lo fotografiaba todo: *«Si no hay foto, no pasó»*.
- **Apodos:** Tomás le dice "Eli"; Elías le dice "enano" (en inglés, *kid*).
- **Lo pendiente:** la última llamada. Tomás lo llamó orgulloso: *«Tres meses, Eli»*. Elías le contestó: *«Ven a celebrar»*.
- **En el juego:** cuando Tomás muerto persigue a Elías, cuenta como en las escondidas. Los escondites del juego son los de su infancia. Y el baño cerrado del 4B es el último lugar donde Tomás se escondió.

**Elías y su madre: la que cuida**
- Enfermera de turno nocturno: cuidaba a desconocidos mientras sus hijos se cuidaban solos. Ella también carga culpa, porque fue ella quien le pidió a un niño que cuidara de otro.
- **La contestadora** del 4B guarda sus mensajes. Cada noche hay nuevos y escucharlos es opcional (suma Verdad). Cambian con el tiempo: enojo, súplica, ternura… y silencio, si Elías consume mucho.
- **El joyero** que Elías vendió tenía una cajita musical. Esa melodía es el tema de la madre en la banda sonora.
- **Lo pendiente:** nunca le dijo que lo culpa. Elías lo da por hecho.
- **En el final bueno**, ella le dice lo que él nunca esperó oír: *«Nunca debí pedirte que lo cuidaras. Eras un niño.»*

**Elías y su padre: el silencio**
- Taxista. Los domingos le enseñaba a manejar en el taxi vacío.
- Elías le robó la recaudación de una semana y vendió la radio del taxi. Desde entonces, el padre no le habla.
- En los recuerdos aparece de espaldas y nunca mira a Elías.
- **Lo pendiente:** él también se culpa. Echó a Elías de la casa, y Tomás se fue con él.
- **En el final bueno** (el hijo pródigo): un taxi espera frente al edificio. El padre baja la ventanilla y, por primera vez en todo el juego, mira a Elías. No dice nada. No hace falta.

**Elías y Doña Carmen: el prójimo**
- Viuda. Su único hijo se fue a Estados Unidos hace años y casi nunca llama: ella también sabe lo que es esperar junto a un teléfono.
- Cada noche le deja comida en la puerta. Elías cree que lo vigila.
- **Lo pendiente:** la noche de la muerte, ella oyó algo y tocó la puerta del 4B. Elías no abrió. Los golpes de la Noche 1 son esos golpes, repitiéndose en su memoria. Ella todavía se pregunta si debió llamar a alguien.
- Su frase *«Te escuché anoche»* sirve para cualquier noche, pero sobre todo para aquella.

**El patrón:** todos cargan un pedazo de la culpa: la madre, el padre, la vecina. Elías cree que es solo suya, y esa creencia lo aísla. Descubrir que no está solo con ella es parte de lo que le permite pedir ayuda.

### 4.2 Los nombres

Decididos el 18 de octubre de 2026. Se pronuncian bien en español y en inglés, suenan naturales para una familia latina y cada uno esconde un significado (nunca se explica en el juego).

| Personaje | Apodo | Significado escondido |
|---|---|---|
| **Elías** | Eli | El profeta que pidió morir y fue levantado con pan y agua (ver 3.4). |
| **Tomás** | Tomi (su madre), enano (Elías) | El incrédulo, que necesitaba ver para creer: la cámara. |
| **Eva** | — | La madre de Caín y Abel. |
| **José** | — | El padre que en toda la Biblia no dice una sola palabra. |
| **Doña Carmen** | — | Viene del Monte Carmelo, el monte del profeta Elías. |

*Abel* quedó descartado para el hermano: revelaría el giro de golpe.

---

## 5. Estructura: el edificio y las cinco noches

El edificio es viejo, de seis pisos, en el centro de una ciudad latinoamericana sin nombre. Elías vive en el 4B. Su departamento es el refugio (ahí se guarda la partida) y el elevador lleva a pisos que se transforman en recuerdos.

Cada capítulo es una noche. Entre noches, Elías despierta en el 4B y escribe en su cuaderno.

| Noche | Lugar | Qué cuenta | Introduce | Duración |
|---|---|---|---|---|
| 1 | El 4B | Primer día sin consumir. El teléfono suena y nadie habla. El baño cerrado. Tomás vivo en el sofá. Alguien toca la puerta. | Moverse, examinar, cuaderno, teléfono, primera dosis | 20–30 min |
| 2 | El pasillo del 4º piso | El pasillo se repite y cambia en cada vuelta. Primera aparición de Tomás muerto. | Cámara Polaroid, persecución, escondites | 30–40 min |
| 3 | La casa de sus padres | Un piso se convierte en la casa de su infancia: lo que robó, lo que rompió. | Llamadas de la madre (contestar o no) | 40–50 min |
| 4 | Donde empezó | Un piso se convierte en la fiesta donde Elías le dio a Tomás su primera dosis. | Tomás vivo como guía que miente | 40–50 min |
| 5 | La noche | De vuelta en el 4B, el baño se abre. Elías revive aquella noche. | El registro de llamadas | 30–40 min |
| Final | El 4B | El teléfono. | — | ~10 min |

### Noche 1 — El 4B
- Elías despierta en el suelo, temblando. Tutorial integrado: buscar agua, ordenar el cuarto (limpiar los rastros del consumo: las jeringas, la cuchara quemada, el cenicero con las colillas, el cinturón y el encendedor) y escribir en el cuaderno. Lo guían sus pensamientos, sin indicadores (6.9).
- El teléfono suena; al contestar solo hay estática. (Es su madre; el jugador aún no lo sabe.)
- Tomás vivo aparece en el sofá: *«¿Otra vez sin dormir?»*. Al voltear, ya no está.
- Hay droga escondida en el departamento: bajo el colchón, envuelta en una media. Elías la escondió de sí mismo. Primera oportunidad de consumir.
- Golpes en la puerta. Por la mirilla no hay nadie. Una voz: *«Eli, ábreme»*. Al abrir, el pasillo.

### Noche 2 — El pasillo
- Estilo P.T.: el pasillo del 4º piso se repite. En cada vuelta algo cambia (una puerta de más, un número distinto, una mancha que crece). Para avanzar hay que notar la diferencia.
- Elías encuentra la cámara Polaroid de Tomás. La primera foto muestra una puerta que a simple vista no existe.
- Primera aparición de Tomás muerto al fondo del pasillo, a contraluz del elevador. Primera persecución: huir y esconderse.
- El elevador lleva a pisos que no deberían existir.

**Cómo se juega** (decidido el 24 de octubre de 2026; el plano está en `blender/renders/pasillo4_plano.png` y el pasillo, en *Pasillo del 4º piso*, sección 10):
- **En L, como en P.T.** El pasillo largo empieza junto a la escalera, pasa frente al 4B y al 4A y termina en el elevador; ahí dobla en un tramo corto que acaba en otra puerta de la escalera. Elías baja un piso por esa escalera y sale otra vez al comienzo del pasillo largo: es el 4º piso de nuevo. El teléfono público está junto al elevador. Lo que hay a la vuelta de la esquina no se ve desde el pasillo largo: ahí puede cambiar algo sin que el jugador lo vea.
- **La regla.** En cada vuelta cambia una sola cosa. Cuando Elías la encuentra y la mira, dice algo (un pensamiento), y recién entonces la escalera lleva a la vuelta siguiente. Si baja sin haberla visto, se repite la misma vuelta, con la diferencia un poco más notoria cada vez, para que nadie se quede trabado.
- **Las vueltas:**
  0. Todo normal. El plato de Doña Carmen frente al 4B (6.10). El elevador no viene: solo queda la escalera.
  1. Un número distinto: la puerta del 4D, la segunda después de la suya, también dice «4B».
  2. Una mancha de humedad en el techo, sobre la puerta del 4B, que gotea.
  3. Suena el teléfono público (contestar o no cuenta para el final, 6.5). En su repisa está la Polaroid de Tomás.
  4. La puerta de la escalera desapareció: el tramo corto termina en una pared. La primera foto (6.4) muestra la puerta; cuando la foto termina de revelarse, la puerta está ahí.
  5. Los focos apagados y el elevador abierto, con luz adentro. Tomás muerto, frente al elevador y de espaldas, cuenta hasta diez (6.7): la primera persecución. Elías se esconde en el 4C, que está entreabierto y vacío, o en el cuarto de limpieza del tramo corto. Cuando Tomás se va, el elevador sigue abierto, esperando: lleva a pisos que no deberían existir.
- **El 4B sigue siendo el refugio:** queda abierto toda la noche para guardar en el cuaderno, menos en la vuelta 5, cuando la puerta no abre.

### Noche 3 — La casa
- El 3er piso se convierte en la casa donde creció. Todo está como era, pero faltan cosas: la tele, el joyero de su madre, la foto familiar.
- Puzzle: reconstruir la foto familiar. Las piezas que faltan son las cosas que Elías vendió (las boletas de la casa de empeño son las pistas).
- El teléfono de la casa suena: es su madre. Por primera vez se oye su voz. Contestar o no cuenta para el final.
- En el espejo del baño, Elías ve sus brazos tal como están.
- El padre, de espaldas en la cocina. Si Elías se acerca, la figura se aleja.

### Noche 4 — Donde empezó
- Un piso se convierte en la fiesta donde Elías le dio a Tomás su primera dosis. Música, luces, gente sin cara.
- Tomás vivo, en su versión más fuerte, guía a Elías. Pero miente: la cámara muestra que el camino que él indica no lleva a ninguna parte.
- La fiesta se pudre a medida que avanzas: la gente sin cara se queda quieta, la música se arrastra.
- Persecución larga de Tomás muerto, ya en descomposición.

### Noche 5 — La noche
- De vuelta en el 4B. Por primera vez, la puerta del baño se abre.
- Elías revive aquella noche como un recuerdo jugable. No se puede cambiar: cada intento de marcar falla.
- El registro de llamadas del teléfono: 0 llamadas salientes. La mentira se cae.
- La mañana siguiente, jugable: suena el teléfono y es su madre. *«¿Dónde está tu hermano?»* La única respuesta posible es *«No sé.»*
- La frase *«Una más, como antes»*, ahora en boca de Elías.

### Final — El teléfono
Elías está en el 4B, en el presente, con el teléfono en la mano. Lo que pasa depende de todo lo anterior (ver sección 7).

---

## 6. Mecánicas

### 6.1 Exploración e interacción
- Caminar, correr (poco y con cansancio), agacharse, examinar, recoger, abrir.
- Inventario mínimo: llaves, rollos de película, dosis y objetos de puzzle.
- Sin mapa fijo: el edificio cambia, así que un mapa mentiría. Idea: Elías dibuja uno en su cuaderno, y a veces está mal.

### 6.2 Abstinencia (sistema oculto)
Un valor interno de 0 a 100 que nunca se muestra.
- Sube con el tiempo y con los sustos. Consumir lo baja a cero, pero por poco tiempo.
- Efectos según el nivel: temblor de manos y cámara, sudor (visión borrosa en los bordes), latidos y respiración más fuertes, más alucinaciones, más apariciones de Tomás muerto.
- **Sigue la curva real de la abstinencia:** si Elías no consume, el nivel base sube hasta la Noche 2 o 3 y luego baja. El camino difícil se vuelve físicamente más llevadero hacia el final, justo cuando lo emocional pega más fuerte.

### 6.3 La dosis
- Hay dosis escondidas en el mundo, muchas veces en lugares tentadores: junto a un puzzle difícil, en manos de Tomás vivo, en momentos de mucho miedo.
- **Al consumir:** la abstinencia baja a cero, el mundo pasa a su versión "bonita" (ver sección 10), Tomás aparece vivo y amable, los brazos de Elías se ven sanos (es la mentira de la droga) y se abren algunos atajos que solo existen bajo el efecto.
- **Lo que cuesta:**
  - El contador de días limpio vuelve a cero.
  - El bajón posterior es peor que antes.
  - Los brazos de Elías empeoran (se ven en primera persona y en los espejos; ver "Brazos de Elías" en la sección 10).
  - El 4B se deteriora más entre noches.
  - La madre llama menos.
  - Suma Dependencia (ver sección 7).
- El consumo nunca se muestra paso a paso: se ve la jeringa en la mano, corte a negro, y luego el efecto.

### 6.4 La cámara de Tomás (Polaroid)
- Era de Tomás. Las fotos muestran lo que es real: puertas ocultas, el estado verdadero de un cuarto, figuras que no estaban, pasillos que en realidad están bloqueados.
- **Recurso limitado:** pocos rollos en todo el juego. Usarla bien es parte del puzzle.
- Las fotos se guardan en un álbum que también tiene fotos viejas de la familia (coleccionables con historia).
- **Duda final:** en la Noche 5, una foto muestra algo imposible. ¿La cámara también mentía?

### 6.5 El teléfono
- Suena en momentos clave: en el 4B, en la casa de los padres, en el teléfono público del pasillo.
- Contestar o no contestar es una decisión que cuenta para el final.
- Al principio solo hay estática o silencio; con el tiempo se oye la voz de la madre. Cuanto más contestas, más claro se escucha.
- **La contestadora** del 4B acumula los mensajes de la madre cada noche. Escucharlos es opcional (ver 4.1).

### 6.6 El mundo cambia cuando no miras
- Objetos que se mueven al darte la vuelta, puertas que aparecen o desaparecen, números que cambian, pasillos que se repiten.
- **Paranoia:** golpes en la puerta, sirenas de policía, sombras bajo la puerta, ojos detrás de las mirillas, voces de vecinos a través de las paredes.

### 6.7 Huida y escondites
- Tomás muerto persigue solo en secuencias concretas, no todo el tiempo, para que no pierda fuerza.
- Mientras busca, cuenta en voz alta como en las escondidas de niños: *«…ocho, nueve, diez. ¡Listo o no, ahí voy!»* (en inglés: *"Ready or not, here I come!"*). Al llegar a diez, sale a buscarte.
- Esconderse en clósets, bajo la cama o detrás de puertas; contener la respiración (más difícil con abstinencia alta).
- Si te atrapa: un destello del recuerdo de aquella noche y vuelves al último punto de guardado.

### 6.8 Guardar: el cuaderno
- Se guarda escribiendo en el cuaderno de Elías, en el 4B y en algunos puntos seguros.
- La pantalla de guardado muestra los días limpio: *«Día 3. No consumí.»* Si consumiste: *«Día 0.»*
- Lo que Elías escribe cambia según lo que el jugador ha hecho y descubierto.

### 6.9 Sin barra de cordura
No hay indicadores en pantalla. El jugador tampoco debe saber qué tan mal está Elías: lo nota por cómo se ve y se escucha el mundo.

### 6.10 La comida de Doña Carmen
- Cada noche hay un plato tapado frente a la puerta del 4B.
- Comer baja un poco la abstinencia: es el alivio pequeño y sano frente al alivio grande y destructivo de la dosis.
- Comer suma Verdad y cambia lo que Doña Carmen dice después.
- Si Elías no toca los platos, se acumulan en el pasillo.

---

## 7. Finales

Dos valores ocultos deciden el final:

- **Dependencia:** sube con cada dosis.
- **Verdad:** sube al contestar las llamadas de la madre, escuchar sus mensajes, comer lo que deja Doña Carmen, tomar fotos en los momentos clave y enfrentar los recuerdos importantes en vez de huir de ellos.

En la escena final, Elías tiene el teléfono en la mano. Con Dependencia alta le tiemblan las manos, los números se mueven y Tomás vivo le susurra que no llame. Con Verdad alta y Dependencia baja, puede marcar.

| Final | Condición (a balancear) | Qué pasa |
|---|---|---|
| **Bueno — «La llamada»** | Dependencia baja y Verdad alta | Elías marca. Contesta su madre. Le dice la verdad. Epílogo meses después: una reunión de apoyo, y Elías con su madre frente a la tumba de Tomás. No es un final feliz; es un final posible. |
| **Neutral — «Recaída»** | Todo lo demás | Elías no marca y sale del edificio sin enfrentar nada. Corte. Despierta en el suelo del 4B: Noche 1, otra vez. Desbloquea la Nueva partida+. |
| **Malo — «Nadie contesta»** | Dependencia muy alta y Verdad baja | La culpa gana. No se muestra nada. Días después: el 4B vacío y el teléfono sonando. Es su madre. Nadie contesta. |

> El final malo es una tragedia, no un castigo ni una cobardía. Nunca se muestra el método ni el acto, solo la ausencia (ver sección 9).

---

## 8. Rejugabilidad

- **Tres finales**, más uno secreto.
- **Nueva partida+ («el ciclo»):** el edificio recuerda. Hay notas nuevas en el cuaderno, Tomás vivo sabe que ya estuviste ahí (*«¿Otra vez tú?»*), se abren cuartos que antes estaban cerrados y aparecen fotos nuevas.
- **Alucinaciones al azar:** un grupo de eventos (sustos, cambios, voces) del que cada partida usa una parte distinta.
- **Coleccionables con historia:** fotos del álbum, páginas del cuaderno y objetos de Tomás.
- **Final secreto «Despedida»** (idea): en Nueva partida+, con el final bueno y todas las fotos, una última escena en el pasillo. Tomás vivo ya no ofrece nada. Solo se despide.

---

## 9. Tono y contenido gráfico

El juego es crudo con las consecuencias de la adicción. No suaviza nada, pero tampoco hace espectáculo del suicidio.

**Sí se muestra:**
- Jeringas usadas, cucharas quemadas, cinturones usados como torniquete, basura de consumo.
- Los brazos de Elías: marcas de pinchazos, moretones, venas oscuras, abscesos e infecciones que empeoran con cada dosis.
- La abstinencia en el cuerpo: sudor, temblores, vómito, insomnio.
- Tomás muerto en todos sus estados: recién muerto (piel gris, labios morados, espuma), descomposición, calavera.

**No se muestra:**
- Cómo preparar o inyectarse paso a paso: el consumo se corta a negro.
- El método del suicidio ni el acto. No es por pudor: está comprobado que mostrar el método aumenta el riesgo de imitación en personas vulnerables (el llamado efecto Werther). Además, la ausencia asusta más.

**Además:**
- El efecto de la droga se ve hermoso, porque así engaña. Pero siempre viene seguido de su costo.
- Aviso de contenido al iniciar el juego: adicción, muerte, suicidio, autolesiones, imágenes gráficas.
- Recursos de ayuda en los créditos y en el menú principal: líneas de prevención del suicidio y de adicciones por país.

---

## 10. Dirección de arte

### Estilo
Low poly con estética de PlayStation 1: pocos polígonos, texturas pixeladas, color limitado con dithering, niebla y mucha oscuridad. La baja resolución esconde detalles y obliga a la imaginación a completar lo que no se ve.

### Especificaciones técnicas
| | |
|---|---|
| Resolución interna | 480×270, escalada sin suavizado a la pantalla |
| Color | 15 bits (32 niveles por canal) con dithering Bayer 4×4 |
| Texturas | 64–256 px, filtro Point (sin suavizado) |
| Personajes | 500–1.500 triángulos |
| Objetos | 20–300 triángulos |
| Escenarios | Modulares: paredes, puertas, marcos y luces reutilizables |
| En Unity | URP, shader con vertex snapping (el "temblor" de los vértices de PS1), niebla, post-proceso de dithering (ver *Estilo PS1 en Unity*) |

### Las dos versiones del mundo
| | Abstinencia (normal) | Efecto (tras consumir) |
|---|---|---|
| Paleta | Verde enfermizo, crema sucio, rojo óxido, negro azulado | Dorado cálido, colores limpios y saturados |
| Luz | Focos amarillos aislados, fluorescentes que parpadean, zonas negras | Todo iluminado, suave, acogedor |
| Estado | Manchas, humedad, basura, deterioro | Limpio, como era antes |
| Tomás | Muerto, o vivo pero "mal" | Vivo, sonriente |
| Sonido | Zumbidos, tuberías, respiración | Música suave, risas lejanas |

### Luz
La luz es el recurso de miedo más importante: focos incandescentes aislados con zonas de oscuridad entre ellos, fluorescentes fríos que parpadean y contraluces (figuras recortadas contra la luz del fondo).

### Prueba de estilo
Aprobada el 18 de octubre de 2026: `blender/renders/pasillo_ps1.png`, generada con `blender/scripts/prueba_estilo_pasillo.py`. Es la referencia visual para el resto del juego.

### Estilo PS1 en Unity
Hecho el 19 de octubre de 2026. La prueba de estilo está recreada en Unity, en `Assets/Scenes/PruebaEstiloPasillo.unity`, con el FBX que exporta el mismo script. Comparada con `pasillo_ps1.png`, cada píxel difiere en promedio 3 niveles de 255.

| Pieza | Qué hace | Dónde (en `unity/Assets/`) |
|---|---|---|
| Imagen de 480×270 | La cámara del juego no dibuja en la pantalla sino en esta imagen chica (sin suavizado ni antialiasing). | `Rendering/PS1_Imagen.renderTexture` |
| Pantalla | Amplía la imagen a la pantalla con píxeles duros (con barras negras si la ventana no es 16:9) y le aplica el color de 15 bits con dithering Bayer 4×4. Usa la misma fórmula que el post-proceso de Blender. También hace el sudor de la abstinencia: la imagen borrosa y más oscura en los bordes. | prefab `Rendering/PS1_Pantalla`, shader `OnTheNod/PS1 Pantalla` |
| Shader PS1 | El de todos los objetos: luz difusa sin brillos, temblor de vértices (cada vértice salta de píxel en píxel de la imagen chica) y niebla. | `Rendering/PS1.shader` (`OnTheNod/PS1`) |
| Niebla iluminada | Las luces iluminan la niebla que tienen cerca: el halo de los focos y la bruma fría del fondo. Imita la niebla volumétrica de Blender. | componente `NieblaPS1` |
| Máscara de foco | Corta la luz que sale hacia arriba de los focos colgantes: en Blender la tapa la bombilla y el techo encima del foco queda negro. | `Rendering/Foco_Mascara.cubemap` (menú *On the Nod > Crear máscara de foco*) |
| Texto | Letreros sobre la imagen chica: la pantalla de guardado del cuaderno, al centro, y los pensamientos de Elías, abajo como subtítulos. Se dibujan a 480×270 con una sombra de un píxel, y la pantalla los pone encima del corte a negro, antes de los 15 bits: salen con los mismos píxeles duros y el mismo dithering. | `Scripts/TextoPS1.cs` |
| Importación | Lo que llega a `Art/` se configura solo: texturas con filtro Point, sin compresión, sin mipmaps y sin reescalar; materiales con el shader PS1 y los colores y la emisión de Blender; los personajes (Tomás, Doña Carmen), como *Humanoid*. En los escenarios, colisión en lo que mide al menos 25 cm, salvo lo que está tirado en el piso y mide menos de 20 cm de alto y 1 m de largo (ropa, cojines caídos, papeles), y todo listo para la luz precalculada. | `Editor/ImportadorArte.cs` |

**Para darle el estilo a una escena nueva:**
1. Poner el prefab `PS1_Pantalla`.
2. En la cámara del juego: *Output Texture* = `PS1_Imagen`, sin HDR, sin MSAA y sin post-proceso.
3. Niebla de la escena (*Lighting > Environment*): exponencial, con la densidad de la niebla de Blender (0,022 en el pasillo) y casi negra (el color del mundo por el de la niebla).
4. Un objeto con el componente `NieblaPS1`, con el color de la niebla de Blender.

**Luces de Blender a Unity** (URP, sin unidades físicas):
- Intensidad de una luz puntual: vatios / (4π²). Un foco de 22 W queda en 0,56.
- Luz de área: se pone un spot que apunta hacia el mismo lado, con intensidad vatios / π².
- Alcance (*Range*): √(vatios × el canal más brillante del color). Es donde EEVEE corta la luz (su umbral es 0,01) y es lo que deja zonas negras entre foco y foco; sin esto, la luz llega mucho más lejos que en Blender.
- Color: el mismo de Blender. Por código, hay que pasarlo con `.gamma`, porque Unity guarda los colores en sRGB.
- Todo esto lo hace `Assets/Editor/EscenaBlender.cs` a partir del JSON que cada script deja junto a su FBX (`<nombre>_escena.json`): menú *On the Nod > Crear luces desde Blender*, con el JSON seleccionado. También pone la cámara de Blender y el ambiente y la niebla de cada estado.
- La niebla iluminada no sabe de paredes: una luz de afuera o de un cuarto cerrado haría brillar la niebla a través del muro. En `NieblaPS1` se ponen solo las luces de los espacios que se ven.

**Diferencias que quedan:** las puertas se ven algo más rojas en Unity, porque los materiales de Blender tienen un brillo especular suave que el shader PS1 no tiene (la PS1 tampoco lo tenía). La bruma del fluorescente sobre las puertas del ascensor es un poco más fuerte.

**Capturas:** *On the Nod > Capturar pantalla PS1* guarda lo que ve la cámara del juego a 1920×1080, igual que los renders de Blender, sin tener que darle a Play.

### Brazos de Elías
Primer asset del juego (18 de octubre de 2026). Se generan con `blender/scripts/brazos_primera_persona.py`; la hoja de estados está en `blender/renders/brazos_estados.png`.

| Estado | Cuándo se ve | Cómo se ve |
|---|---|---|
| 0 · Limpio | Bajo el efecto y en los recuerdos | Piel sana y cálida, camiseta blanca. La mentira de la droga. |
| 1 · Noche 1 | Al empezar el juego (8 años de consumo) | Marcas viejas y un moretón en el pliegue del codo, venas visibles. |
| 2 · Recaídas | Tras consumir varias veces | Marcas por todo el antebrazo, moretones, venas oscuras, piel amarillenta. |
| 3 · Consumido | Dependencia muy alta | Venas quemadas, abscesos, marcas en las manos, uñas sucias, más delgado y sudoroso. |

- **El brazo izquierdo está peor:** Elías es diestro y se inyecta sobre todo en el izquierdo.
- **Técnica:** 848 triángulos y 41 huesos para los dos brazos. El antebrazo gira con dos huesos de torsión, para que la muñeca no se aplaste al girar la palma.
- **Una sola textura** de 256×256 por estado: en Unity, cambiar de estado es cambiar la textura.
- **Forma "consumido":** un *shape key* que adelgaza los brazos; en Unity es un *blendshape*.
- **Pose incluida:** "mirar_brazos" (brazos extendidos, palmas arriba).

**Animaciones** (18 de octubre de 2026). Se generan con `blender/scripts/brazos_animaciones.py` y se prueban dentro del 4B; las vistas previas están en `blender/renders/anim_*.mp4`. Van a 30 cuadros por segundo y son relativas a la cámara: en Unity, los brazos cuelgan de la cámara.

| Clip | Duración | Qué hace |
|---|---|---|
| `reposo` | 2 s, loop | Brazos abajo, fuera de cuadro, respirando. Todos los demás clips empiezan y terminan aquí. |
| `temblor` | 2 s, loop | El temblor de la abstinencia. Es **aditivo**: se suma encima de cualquier otro clip. En Unity va en una capa aditiva cuyo peso sigue al nivel de abstinencia (ver 6.2). |
| `mirar_manos` | 3,8 s | Levanta las manos, las mira y gira las palmas hacia arriba: se ven las marcas. Es el despertar de la Noche 1. |
| `abrir_puerta` | 2,8 s | Agarra la perilla, la gira y empuja la puerta. Es para una puerta cerrada (la de entrada lo usa hasta girar la perilla). |
| `empujar_puerta` | 2,6 s | La puerta del dormitorio, que está entreabierta (24 de octubre de 2026): apoya la mano en la perilla y la empuja, sin girarla; la puerta sigue abriéndose sola. Elías se acerca más al marco que en `abrir_puerta`, porque la perilla queda 33 cm más adentro. |
| `telefono_contestar` | 2,4 s | Levanta el auricular y se lo lleva al oído. Al terminar, Elías mira hacia el pasillo y la puerta del baño. |
| `telefono_colgar` | 1,8 s | Devuelve el auricular a la base y baja la mano. |
| `tomar_jeringa` | 3,4 s | Una dosis sobre una mesa (20 de octubre de 2026): se agacha frente a la mesa de centro, toma la jeringa con la derecha y la levanta frente a la cara. Ya no es la dosis de la Noche 1; queda para las dosis que estén sobre una mesa. |
| `sacar_dosis` | 4 s | La dosis de la Noche 1 (23 de octubre de 2026): se arrodilla junto al colchón del dormitorio, apoya la izquierda en el borde, saca de abajo la media con la jeringa y la levanta frente a la cara: por la boca de la media asoma la jeringa. En el juego sigue un corte a negro. |
| `tomar_agua` | 8,6 s | El agua de la Noche 1 (23 de octubre de 2026). Frente al fregadero de la cocina, toma con la izquierda la taza sucia que está en el fregadero, la pone bajo la llave y abre el agua con la derecha (la manija en cruz gira 70°). Cuando la taza se llena, cierra, se endereza y bebe echando la cabeza atrás. Después se vuelve a inclinar y deja la taza donde estaba. |
| `tomar_cuaderno` | 3,6 s | El cuaderno (23 de octubre de 2026): se agacha frente a la mesa de centro, toma el cuaderno por el borde de adelante y lo levanta frente a la cara, con la tapa hacia él. En el juego sigue un corte a negro: Elías escribe y se guarda la partida. |
| `recoger_mesa` | 3 s | Limpiar los rastros del consumo (23 de octubre de 2026): se agacha frente a la mesa de centro, recoge algo chico con la derecha y lo guarda (la mano baja fuera de cuadro). Se hizo con la jeringa de la mesa; en el juego sirve para cualquier rastro de la mesa. |
| `recoger_piso` | 3,4 s | Igual, de rodillas y del piso. Se hizo con la jeringa del piso de la sala. |

- **Tomar algo chico:** la mano lo agarra con una pinza y, desde ese momento, lo lleva. Como los brazos van pegados a la cabeza, al mirar hacia abajo los hombros se van hacia atrás: para llegar a la mesa de centro, la cabeza se inclina sobre el borde, y para llegar abajo del colchón, que está en el piso, baja hasta 62 cm (de rodillas e inclinado).
- **La media en la mano:** se agarra por la punta, con los dedos a lo largo de la media. Al levantarla, los dedos apuntan hacia arriba y la palma hacia la cara, así que la media queda parada y se ve de costado, con la jeringa arriba.
- **La taza:** la izquierda la rodea por su costado, con el pulgar arriba. La llave está al fondo del fregadero: para alcanzar la manija, Elías se inclina sobre el borde de la encimera, con los ojos a 1,32 m. Para beber, la taza se ve un poco más adelante de la boca que en la realidad (si no, quedaría fuera de cuadro) y se inclina hacia la cara mientras la cabeza se echa atrás. La mano la suelta en el mismo lugar donde la tomó, así que la taza vuelve exacta a su lugar.
- **El chorro:** solo se ve mientras corre el agua (de 2,45 a 4,2 s). En las vistas previas se prende y apaga con el clip; en Unity lo prende el fregadero.
- **El cuaderno en la mano:** la mano lo toma desde arriba, con la palma sobre la tapa. Al levantarlo, los dedos apuntan hacia arriba y el dorso hacia la cara: se ve la tapa, con la mano abajo, sobre el borde.
- **Cámara de interacción:** abrir una puerta o contestar el teléfono mueve la cámara a un punto fijo frente al objeto (inclinado sobre la mesita, frente a la perilla), y desde ahí corre la animación. Así la mano siempre llega al objeto.
- **Luz de los brazos:** una luz tenue pegada a la cámara, que solo ilumina los brazos, para que se lean en los cuartos oscuros.

**En Unity** (19 de octubre de 2026). Los exporta `brazos_animaciones.py` (no `brazos_primera_persona.py`), porque es el que junta el modelo con los clips: `Assets/Art/BrazosElias/` tiene `brazos_elias.fbx`, las cuatro texturas y `brazos_elias_escena.json`. La escena de prueba es `Assets/Scenes/PruebaBrazosElias.unity`: el 4B con los brazos colgando de la cámara.
- **El FBX:** esqueleto genérico con su *Avatar*, la malla con la forma `consumido` y los catorce clips (`reposo`, `temblor`, `mirar_manos`, `abrir_puerta`, `telefono_contestar`, `telefono_colgar`, `tomar_jeringa`, `sacar_dosis`, `tomar_agua`, `tomar_cuaderno`, `recoger_mesa`, `recoger_piso`, `empujar_puerta` y la pose `mirar_brazos`). `reposo` y `temblor` van en bucle. Cuando se agrega un clip, hay que sumarlo a la lista `clips` del componente `BrazosElias` de la escena.
- **El temblor:** va en una capa aditiva. El clip trae un cuadro de reposo antes del primero, y Unity lo usa como referencia de la capa; así el temblor se suma sin mover la pose de base.
- **Los cuatro estados** están en el JSON: la textura de cada uno y el valor de `consumido` (0, 0, 0,45 y 1; en Unity el *blendshape* va de 0 a 100). Los define `brazos_primera_persona.py`, que los guarda en el `.blend`.
- **La cámara de interacción:** el JSON trae, para cada clip y cuadro a cuadro, dónde está la cabeza (la cámara de Unity), y cómo se mueven la puerta del dormitorio, la manija de la llave, el auricular, la jeringa de la mesa, la dosis bajo el colchón, la taza y el cuaderno. La cabeza está en las coordenadas del 4B. La luz de los brazos y la cámara van relativas a la cabeza. La pista de lo que la mano agarra dice además con qué mano se agarra (la taza va en la izquierda), desde qué segundo y, si la suelta, hasta cuál: mientras tanto, Unity lo pega a esa mano, para que tiemble con ella; después vuelve a seguir su pista. El chorro de agua no va en el JSON: lo prende el fregadero de Unity.
- **Comparación con Blender:** cuatro cuadros de las vistas previas (`anim_*_claves.png`), con la cámara, la puerta y el auricular siguiendo esas pistas y el temblor sumado. Cada píxel difiere en promedio entre 4 y 6 niveles de 255; las manos y los dedos coinciden, y lo único distinto es la luz que falta en el fondo del pasillo (la precalculada del 4B).

### Tomás
Tercer asset (18 de octubre de 2026). Se genera con `blender/scripts/tomas.py`; los cinco estados están en `blender/renders/tomas_estados.png`.

**Cómo se ve:** 20 años, flaco, pelo corto oscuro. Sudadera roja con capucha (con un logo desteñido en el pecho y los cordones blancos), camiseta blanca debajo, jeans y zapatillas blancas con el talón rojo. Es la ropa con la que llegó al 4B aquella noche. El rojo lo distingue a lo lejos, incluso a contraluz.

| Estado | Cuándo se ve | Cómo se ve |
|---|---|---|
| 0 · Vivo, sonriente | Bajo el efecto y en los recuerdos | Sonríe; lleva la Polaroid colgada del cuello. |
| 1 · Vivo, "mal" | En abstinencia (Noche 1) | Pálido, ojeroso, sin sonrisa. |
| 2 · Recién muerto | Primeras apariciones (Noche 2) | Piel gris azulada, labios morados, párpados a medio cerrar, espuma en la boca que le cae por el mentón y el cuello. |
| 3 · Descomposición | Noches 3 y 4 | Piel verdosa con vetas, ojos hundidos y nublados, labios retraídos que dejan ver los dientes, ropa manchada. |
| 4 · Calavera | Noche 5 y final | Cráneo, mechones sueltos, manos de hueso, ropa podrida y agujereada. |

- **Técnica:** 1.014 triángulos (más 172 de la Polaroid) y 22 huesos con nombres de Mixamo (`Hips`, `Spine`, `LeftArm`…), para que Unity lo reconozca como *Humanoid* y se le puedan pasar animaciones de Mixamo sin volver a riggearlo.
- **Piezas rígidas, como en la PS1:** cada parte del cuerpo se mueve con su hueso; solo codos, rodillas y columna mezclan dos huesos para doblarse sin quebrarse.
- **Una textura de 256×256 por estado**, y dos *blendshapes*: `descompuesto` (adelgaza el cuerpo y hunde las mejillas) y `calavera` (hunde las cuencas y la nariz). En Unity, cambiar de estado es cambiar la textura y mover esos dos valores.
- **La Polaroid** es un objeto aparte, pegado al pecho: se muestra solo en el estado 0.
- **Poses incluidas:** `de_pie`, `muerto_de_pie` (encorvado, hombros caídos, la cabeza ladeada), `sentado` y `sentado_muerto`.
- **Pruebas en escena:** `tomas_sofa.png` y `tomas_sofa_muerto.png` son la misma toma del 4B, vivo y muerto en el mismo lugar ("al voltear, ya no está"). `tomas_pasillo.png` es la prueba de estilo del pasillo con Tomás muerto en lugar de la silueta.

**En Unity** (20 de octubre de 2026). `tomas.py` lo exporta al final (o solo eso, sin rehacer texturas ni renders, con `-- blender --solo-unity`): `Assets/Art/Tomas/` tiene `tomas.fbx`, las cinco texturas y `tomas_escena.json`.
- **Humanoid:** Unity reconoce los 22 huesos por sus nombres de Mixamo y arma el *Avatar* con la pose en T del esqueleto de Blender, así que las animaciones de Mixamo le sirven tal cual. En Blender, Tomás mira hacia −Y, que en Unity es −Z; el exportador lo gira 180° para que mire hacia +Z, como pide Unity.
- **Las cuatro poses** son clips de un cuadro (`de_pie`, `muerto_de_pie`, `sentado` y `sentado_muerto`) y quedan fijas: el cuerpo queda a la altura y en el lugar de Blender (sentado, la cadera baja hasta el sofá).
- **Los cinco estados** (`estado0` a `estado4`) están en el JSON: la textura, el valor de `descompuesto` y de `calavera` (en Unity, de 0 a 100) y, en `objetos_ocultos`, la Polaroid, que solo se ve en el estado 0. El FBX queda en el estado 1, con la Polaroid incluida.
- **Comparación con Blender:** las tres pruebas en escena, recreadas en las escenas de prueba del 4B y del pasillo, con Tomás en el mismo lugar, pose y estado. La cadera, las manos y los pies quedan en los mismos puntos que en Blender. En el sofá, vivo y muerto, la zona de Tomás difiere en promedio 2 niveles de 255. En el pasillo difiere 11, pero esa zona ya difería 10,5 sin él: es la bruma del fluorescente del fondo (ver *Estilo PS1 en Unity*).

### Doña Carmen
Cuarto asset (18 de octubre de 2026). Se genera con `blender/scripts/dona_carmen.py`; la hoja está en `blender/renders/carmen_hoja.png` y las vistas por la mirilla en `blender/renders/carmen_mirilla_*.png`.

**Cómo se ve:** unos 70 años, bajita (1,55 m), robusta y un poco encorvada. Pelo canoso recogido en un moño, lentes de leer con marco de carey y aretes chiquitos. Vestido oscuro de viuda, chaleco de lana con botones, delantal celeste de florcitas, medias enrolladas bajo la rodilla y pantuflas de felpa. Lleva el escapulario de la Virgen del Carmen, el del Monte Carmelo de su nombre (nunca se explica).

| Vestuario | Cuándo se ve | Cómo se ve |
|---|---|---|
| `dia` | Cada noche, cuando deja la comida | Chaleco, delantal y vestido oscuro. |
| `noche` | La noche en que murió Tomás (Noche 5) | Bata rosada acolchada sobre el camisón y redecilla en el pelo: oyó algo y salió a tocar. |

- **No cambia con la abstinencia ni con el efecto.** Es lo único real del juego, así que siempre se ve igual.
- **Técnica:** 1.054 triángulos y los mismos 22 huesos con nombres de Mixamo que Tomás. Piezas rígidas; la falda se mueve con la cadera y, abajo, se reparte con los muslos para que pueda caminar. Una textura de 256×256 por vestuario: en Unity, cambiar de vestuario es cambiar la textura.
- **El plato tapado** es un objeto aparte (128 triángulos, textura propia de 64×64): plato de peltre blanco con borde azul, tapado con una servilleta bordada.
- **Poses incluidas:** `de_pie`, `con_plato`, `tocando` (con el plato o con la mano en el pecho), `mirilla` (se acerca a la puerta y levanta la cara: la mirilla le queda alta) y `preocupada` (la mano en el pecho).

**Por la mirilla.** Pruebas en el pasillo de la prueba de estilo, vistas desde la puerta del 4B con un ojo de pez de 170°. En la prueba, el 4B es la primera puerta de la izquierda del pasillo y el 4A, la de Doña Carmen, queda en diagonal enfrente.

| Vista | Qué muestra |
|---|---|
| `carmen_mirilla_plato` | Espera con el plato. Atrás, su puerta entreabierta con luz tibia. |
| `carmen_mirilla_cerca` | Se acerca a mirar: la cara deformada por el lente, mirando hacia arriba. |
| `carmen_mirilla_noche` | Aquella noche: en bata, tocando. |
| `carmen_mirilla_vacio` | Nadie. Solo los platos sin tocar, que se acumulan (ver 6.10). |

- **Dos lecturas de la misma mujer:** por la mirilla, deformada y a contraluz, da miedo; en la hoja, con buena luz, es una abuela con un plato de comida. Es el giro del personaje (ver sección 4).
- **En Unity:** la mirilla es una cámara muy abierta cuya imagen pasa por un shader de ojo de pez, con los bordes oscuros y borrosos.

**En Unity** (20 de octubre de 2026). `dona_carmen.py` la exporta al final (o solo eso, con `-- blender --solo-unity`): `Assets/Art/DonaCarmen/` tiene `dona_carmen.fbx` (esqueleto, cuerpo y plato), las tres texturas y `dona_carmen_escena.json`.
- **Humanoid**, como Tomás y girada igual que él. Sus cinco poses son clips fijos.
- **Los vestuarios** son dos estados del JSON, `dia` y `noche`: solo cambia la textura. El FBX queda con `dia`.
- **El plato:** en el JSON, `accesorios` dice dónde va en las poses que lo llevan: `con_plato` (en las dos manos) y `tocando` (en la palma izquierda). En las demás poses no lo lleva. Se aplica como un cambio desde donde está el plato en el FBX (`EscenaBlender.EnPose`), porque en Unity el plato llega con otro giro interno que en Blender.
- **Comparación con Blender:** sus renders son por la mirilla, y cuando se importó Unity todavía no tenía el ojo de pez (ahora sí, ver *La Noche 1* en *El 4B jugable*). Se comparó con tres tomas de prueba en el pasillo, desde la cámara de la prueba de estilo: de frente con el plato, tocando la puerta del 4B y en bata mirando por la mirilla. La zona de Carmen difiere en promedio entre 3,5 y 4,7 niveles de 255, y el plato queda en sus manos. Lo único distinto es la luz ambiente: en Unity llega pareja a todas partes, también bajo el plato, así que el delantal y el plato se ven algo más claros en la sombra. Es lo mismo que pasa en el 4B y se resuelve con la luz precalculada, que a los personajes les llega por sondas de luz (*light probes*).

### Departamento 4B
Segundo asset (18 de octubre de 2026). Se genera con `blender/scripts/departamento_4b.py`; las vistas están juntas en `blender/renders/4b_hoja.png` y el plano en `blender/renders/4b_plano.png`.

**Distribución** (7,2 × 7,4 m, techo de 2,6 m como el pasillo): la puerta de entrada da a la sala; a la derecha está la cocina; al fondo de la sala, un pasillo corto termina en la puerta del baño, y el dormitorio abre a ese pasillo. Desde la entrada se ven, de una sola mirada, el sofá, el teléfono y la puerta del baño.

| Vista | Qué muestra |
|---|---|
| `4b_sala` | Desde la entrada: el sofá donde aparece Tomás, el teléfono con la contestadora y, al fondo del pasillo, la puerta del baño. |
| `4b_sala_efecto` | La misma vista bajo el efecto: papel tapiz limpio, luz dorada, la foto familiar en su lugar. |
| `4b_bano` | La puerta del baño, trabada con una silla. |
| `4b_entrada` | La puerta de entrada, con cadena y cerrojos, en el momento en que tocan. |
| `4b_cocina` | Fluorescente frío, ventana tapada con periódicos, el calendario. |
| `4b_dormitorio` | El colchón en el piso, bajo la ventana tapada con cartón. |
| `4b_dormitorio_efecto` | El dormitorio bajo el efecto: cortinas, el foco prendido y el atardecer que cae sobre el colchón. No va en la hoja. |
| `4b_dosis` | Junto al colchón: por el costado asoma la punta de la media donde está la droga. No va en la hoja. |
| `4b_plano` | Vista desde arriba, sin techo. |

**Detalles que cuentan la historia** (nunca se explican):
- **La silla en la puerta del baño.** Falta una de las dos sillas del comedor: Elías la usó para trabar la puerta del baño, que abre hacia el pasillo. Bajo el efecto, la silla vuelve a la mesa.
- **La luz bajo la puerta del baño.** Por debajo sale una línea de luz fría, aunque nadie abre esa puerta desde hace ocho meses.
- **La marca de la foto.** En la sala hay un rectángulo de papel tapiz menos gastado y un clavo: ahí colgaba la foto familiar. Bajo el efecto, la foto está.
- **El calendario** de la cocina quedó en el mes en que murió Tomás, con un día marcado en rojo.
- **La contestadora** tiene la luz roja encendida: hay mensajes sin escuchar.
- **Los pies bajo la puerta.** Cuando tocan (Noche 1), la luz del pasillo que entra por debajo de la puerta se corta en dos sombras. Por la mirilla no hay nadie. Para Unity, donde esa luz está precalculada y los pies no la tapan, el 4B trae también las sombras ya hechas (`sombra_pie_izq` y `sombra_pie_der`, 24 de octubre de 2026): cada pie proyectado desde la luz-truco `pasillo_edificio` sobre el piso de adentro, hasta los 22 cm donde termina la franja de luz. No salen en los renders.
- **La puerta de entrada por fuera** (24 de octubre de 2026): la placa con el «4B» y el lente de la mirilla, del lado del pasillo. La vuelta 1 de la Noche 2 depende de que se vea ese número (el 4D también dirá «4B»).
- **El cuaderno** (donde se guarda la partida) está en la mesa de centro, junto a la cuchara quemada, la jeringa y el cinturón. Esa jeringa está vacía: es parte del desorden.
- **Los rastros del consumo** (23 de octubre de 2026): la jeringa, la cuchara quemada, el cenicero con las colillas, el cinturón y el encendedor de la mesa de centro, la jeringa del piso de la sala y la que está junto al colchón. Cada uno es un solo objeto con el origen en su base: la cuchara, el cenicero y el cinturón juntan sus piezas bajo un vacío. Así Elías los recoge de una vez en el tutorial de la Noche 1 (ver *El 4B jugable*).
- **La llave del fregadero** (23 de octubre de 2026). Tiene una manija en cruz que gira para abrir el agua, y un chorro que sale del pico y cae dentro de la taza que se pone abajo. El chorro no se ve en las vistas del 4B: aparece solo mientras Elías llena la taza (ver `tomar_agua` en *Brazos de Elías*). En el fregadero, entre los platos sucios, está la taza que usa.
- **La dosis bajo el colchón** (23 de octubre de 2026). Elías la escondió de sí mismo: una media blanca de franjas rojas con una jeringa adentro, metida bajo el borde del colchón que da al cuarto, cerca de la almohada. Solo asoma la punta de la media (6 cm, pálida contra el piso oscuro); la jeringa sale por la boca de la media, del lado de abajo del colchón, y no se ve hasta sacarla. Junto al colchón ya había una jeringa usada tirada.

**Las dos versiones en una escena.** Los objetos están en colecciones: `Estructura` y `Muebles` (siempre), `Deterioro` (abstinencia) y `Efecto` (bajo el efecto). Paredes, pisos, techo y sofá tienen dos texturas, la sucia y la limpia (`*_limpio.png`). En Unity, cambiar de mundo es mostrar u ocultar un grupo de objetos y cambiar esas texturas.

**El dormitorio bajo el efecto** (23 de octubre de 2026). Como la dosis de la Noche 1 se toma ahí, es lo primero que se ve del efecto. Antes no tenía ninguna luz en ese mundo (el sol y la lámpara de pie están en la sala) y quedaba negro, con la ventana sin cartones en blanco. Ahora, como la sala: cortinas a los costados de la ventana, el foco del techo prendido (`luz_dormitorio`; en la abstinencia la bombilla está quemada) y el sol del atardecer (`sol_dormitorio`), que entra por la ventana a 35° y cae sobre el colchón con la sombra de la cruz del marco. La ventana se sigue viendo blanca, como la de la sala: afuera es el atardecer.

**Técnica:** unos 7.000 triángulos en 271 objetos. Las puertas tienen el origen en la bisagra, listas para animar. Algunas luces son trucos para Blender (las que se cuelan bajo las puertas y las de "rebote"); en Unity se resuelven con luz precalculada (*baked*).

**En Unity** (19 de octubre de 2026). El script exporta `Assets/Art/Departamento4B/`: el FBX en el estado abstinencia, las 22 texturas (sucias y limpias) y `departamento_4b_escena.json` con las luces, las cámaras y los dos estados. La escena de prueba `Assets/Scenes/PruebaDepartamento4B.unity` es la vista `4b_sala`, armada desde ese JSON.
- **Colecciones:** llegan como grupos (`Estructura`, `Muebles`, `Deterioro`, `Efecto`, `Eventos`); `Plano` no se exporta. Cambiar de mundo es activar o desactivar `Deterioro` y `Efecto`, poner las texturas limpias, cambiar la emisión de los focos y los resplandores, y las luces y la niebla del otro estado. El JSON dice qué cambia en cada uno.
- **Luces-truco:** en el JSON, las de rebote llevan `truco: rebote` y las que se cuelan bajo las puertas, `truco: fuga`. En Unity van solo en la luz precalculada (ver *El 4B jugable*). Las del dormitorio bajo el efecto no son trucos, pero también van enteras en la luz precalculada: llevan `precalculada` (ver *Luz precalculada*).
- **Comparación con Blender** (la escena de prueba, sin luz precalculada): en abstinencia, cada píxel difiere en promedio 3 niveles de 255. Falta la luz que sale bajo la puerta del baño: la rendija es demasiado fina para las sombras en tiempo real y sin el rebote la puerta queda oscura. En el efecto la diferencia es de 13: Unity sale algo más claro porque su luz ambiente no se oscurece en los rincones, y faltan los rayos del atardecer en la niebla. La luz bajo la puerta del baño y los rincones del efecto se resolvieron con la luz precalculada de la escena jugable (ver *El 4B jugable*); los rayos en la niebla siguen faltando.

### El 4B jugable
Primer recorrido jugable (20 de octubre de 2026): `Assets/Scenes/Departamento4B.unity`. Elías empieza en la entrada, mirando hacia la sala (la vista `4b_sala`).

| | Teclado y mouse | Control |
|---|---|---|
| Caminar | W, A, S, D o las flechas | palanca izquierda |
| Mirar | mouse | palanca derecha |
| Usar | E | botón de arriba |

- **Caminar:** a 1,3 m/s, con los ojos a 1,6 m, la altura de la cabeza en las animaciones de Blender. Elías choca con paredes y muebles, y pisa la ropa, los cojines caídos y los papeles del piso sin subirse a ellos (ver *Importación* en *Estilo PS1 en Unity*). Todavía no corre ni se agacha (6.1).
- **Usar:** se mira algo a menos de 1,4 m y se aprieta Usar. Lo que está en el piso se alcanza desde más lejos, porque los ojos están a 1,6 m: la dosis bajo el colchón, desde 2 m (el campo `alcance` de `Interactuable`). Por ahora:
  - la puerta del dormitorio, desde el pasillo: como está entreabierta, Elías apoya la mano en la perilla y la empuja (`empujar_puerta`); queda abierta;
  - el teléfono: contesta, escucha hasta que se vuelve a apretar Usar, y cuelga;
  - la dosis escondida bajo el colchón del dormitorio (ver abajo);
  - el cuaderno de la mesa de centro: guarda la partida, desde 1,8 m (ver *El cuaderno*);
  - la llave del fregadero de la cocina: llena una taza y bebe (ver *El agua*);
  - los rastros del consumo: los de la mesa de centro desde 1,8 m y los del piso desde 2 m (ver *El tutorial*);
  - la mirilla de la puerta de entrada: mira por ella hasta que se vuelve a apretar Usar;
  - la puerta de entrada, solo al final de la Noche 1 (ver *La Noche 1*);
  - en el pasillo del 4º piso, la puerta entreabierta del 4C, la de arriba de la escalera B, la de abajo de la escalera A y la del cuarto de limpieza (ver *Pasillo del 4º piso*).

  Todos menos la mirilla corren con la cámara de interacción de los brazos (ver *Brazos de Elías*): la cámara va al punto donde empieza el clip y desde ahí sigue a la cabeza de Blender, mientras la puerta, el auricular, la dosis, la taza, la manija o el cuaderno siguen sus pistas. Comparadas en cámara lenta con las hojas de cuadros de Blender (`anim_*_claves.png`) y con las vistas previas, la mano agarra la perilla, el auricular, la jeringa, la media, la taza, la manija y el cuaderno igual que en Blender.
- **Los brazos** cuelgan de la cámara, con el temblor sumado según la abstinencia. Su luz ilumina solo la capa de luz `Brazos`, y tampoco la niebla. Unity los anima aunque no se vean: si no, en reposo (fuera de cuadro) quedaban congelados y al empezar un clip nunca entraban en cuadro.
- **El código** está en `Assets/Scripts/`:
  - `Elias`: caminar, mirar, usar y la cámara de interacción;
  - `BrazosElias`: el clip de turno, el temblor encima y el estado de los brazos;
  - `PuertaInteractiva`, `TelefonoInteractivo`, `DosisInteractiva`, `CuadernoInteractivo` y `AguaInteractiva`: derivan de `Interactuable`, que es lo que hay que heredar para agregar algo que se pueda usar;
  - `Abstinencia` (con la respiración, los latidos y el sudor), `AmbienteSonoro`, `Partida` (lo que la partida va acumulando), `Guardado` (el archivo de la partida), `Fundido` (el corte a negro) y `TextoPS1` (el texto sobre la imagen);
  - `EstadosDelMundo`: los dos mundos;
  - `NocheUno`: el orden de la Noche 1, con el tutorial (`RastroInteractivo` y `Pensamientos`) y sus eventos en `AparicionTomas`, `GolpesEnLaPuerta`, `MirillaInteractiva`, `VistaMirilla` (la cámara con ojo de pez) y `PuertaDeEntrada`;
  - `NocheDos`: el comienzo de la Noche 2, al abrir la puerta del 4B;
  - `NieblaPorZonas`: qué luces iluminan la niebla según dónde está Elías.

**La abstinencia** (6.2) es un valor oculto que empieza en 35 (la Noche 1 es el primer día sin consumir) y sube 1,5 por minuto. Se nota en el cuerpo de Elías, cada vez más:
- **El temblor de las manos:** no hay por debajo de 10, y llega al de las vistas previas de Blender en 60.
- **La respiración** (24 de octubre de 2026): se oye desde 25, apenas al empezar la noche; en 100 suena fuerte y 1,4 veces más rápida. Suena en la cabeza de Elías.
- **Los latidos:** desde 55, de 80 a 125 pulsaciones por minuto, cada vez más fuertes.
- **El sudor:** desde 60 la imagen se pone borrosa y algo más oscura en los bordes, cada vez más hacia el centro (la pantalla PS1, ver *Estilo PS1 en Unity*). En 100 los bordes se mezclan con los píxeles de hasta 3 píxeles de distancia.
- **El temblor de la cámara:** desde 70 tiembla también la vista, hasta 0,6° en 100.

Bajo el efecto no hay nada de eso: la respiración se calma de a poco y el sudor se va. Probado en Play con la abstinencia en 35 y en 85, y después de la dosis.

**La dosis** (6.3) está escondida bajo el colchón del dormitorio (23 de octubre de 2026; ver *Departamento 4B*). Se puede tomar en cualquier momento de la noche, mirando la punta de la media que asoma:
1. Elías se arrodilla junto al colchón, apoya la izquierda en el borde, saca la media de abajo y la mira en la mano, con la jeringa asomando por la boca (el clip `sacar_dosis`).
2. Corte a negro, con el mismo dithering de 15 bits, como un fundido de la PS1. A oscuras, la dosis desaparece y Elías se para.
3. Al volver, el efecto. La abstinencia baja a 0 y no hay temblor.
4. A los 3 minutos llega el bajón, de golpe: la abstinencia vuelve 15 puntos más alta que antes de consumir.

Lo que cuesta queda registrado en `Partida`: los días limpio vuelven a 0 y suman la dosis y la Dependencia (sección 7); se guarda con el cuaderno (ver *El cuaderno*). La dosis se usa una sola vez. La jeringa de la mesa de centro ya no se usa: está vacía.

- **Para encontrarla:** la colisión de la dosis (lo que la mirada de Elías tiene que tocar) cubre la punta de la media y un poco de piso alrededor, de 18 × 16 cm y 8 cm de alto. Elías no choca con ella: está tirada en el piso, como la ropa.
- **Comparación con Blender:** probada en *Play* con la E, en cámara lenta, y capturada en los mismos seis segundos que `anim_sacar_dosis_claves.png`. La mano, la media y la jeringa quedan en el mismo lugar que en Blender. Cada píxel difiere en promedio entre 7 y 12 niveles de 255, y es la luz: en Unity el colchón y la pared del fondo salen más claros, y faltan los granos de la niebla de Blender.
- **Al volver del negro:** Elías está parado junto al colchón, en el dormitorio bajo el efecto: cálido, con el foco prendido y el atardecer sobre la cama (ver *Departamento 4B*).

**El cuaderno** (6.8; 23 de octubre de 2026) está en la mesa de centro de la sala. Escribir en él guarda la partida. Se puede usar en cualquier momento de la noche y todas las veces que se quiera, también bajo el efecto:
1. Elías se agacha frente a la mesa de centro, toma el cuaderno y lo levanta frente a la cara (el clip `tomar_cuaderno`).
2. Corte a negro. A oscuras, el cuaderno vuelve a la mesa, Elías se para y se guarda la partida.
3. Sobre el negro aparece lo que Elías escribe, los días limpio: «Día 1. No consumí.», o «Día 0.» si consumió. Se queda 3 segundos.
4. La imagen vuelve: Elías está parado frente a la mesa de centro.

- **Lo que se guarda:** la noche, la abstinencia (y si estaba bajo el efecto) y lo que lleva `Partida`: días limpio, dosis, Dependencia y llamadas contestadas y perdidas. Va en `partida.json`, en la carpeta de datos del juego (en Windows, `AppData\LocalLow\Junipshade\On the Nod\`, dentro de la carpeta del usuario). Se escribe primero en un archivo aparte y después se cambia por el anterior: si el juego se cierra a mitad de camino, la partida de antes queda entera. Por ahora solo se guarda; se cargará desde el menú, cuando exista.
- **El texto** lo dibuja `TextoPS1` (ver *Estilo PS1 en Unity*): 16 píxeles de alto en la imagen de 480×270, color crema sucio. La letra es provisional: la que trae Unity.
- **Para encontrarlo:** se alcanza desde 1,8 m, porque está a 42 cm del piso; basta con pararse junto a la mesa de centro.
- **Probado en Play** con la E, por los dos caminos: sin consumir («Día 1. No consumí.») y después de la dosis («Día 0.»). El archivo quedó con los valores de cada momento, también al sobrescribirse. Con el clip, el cuaderno sigue a la mano como en Blender y vuelve a la mesa.
- **Falta:** cargar la partida y que lo que Elías escribe cambie según lo que hizo y descubrió (6.8).

**El agua** (sección 5; 23 de octubre de 2026) sale de la llave del fregadero de la cocina: es el «buscar agua» del tutorial de la Noche 1. Se usa mirando la llave o el fregadero:
1. Elías toma con la izquierda la taza sucia del fregadero y la pone bajo la llave (el clip `tomar_agua`).
2. Abre el agua con la derecha: la manija chirría al girar y el chorro cae en la taza. El agua suena más aguda a medida que la taza se llena, y al cerrar caen dos gotas.
3. Se endereza y bebe: se oyen tres tragos y el aire que sale después.
4. Deja la taza donde estaba.

- **Solo en la abstinencia:** la taza es parte del deterioro (bajo el efecto no hay platos ni tazas en el fregadero) y bajo el efecto Elías no tiene sed.
- **Para encontrarla:** la llave es demasiado fina para que la mirada la encuentre, así que una caja invisible cubre la llave y el fregadero (53 × 60 cm y 43 cm de alto).
- **El chorro y los sonidos** los maneja `AguaInteractiva`, con los segundos del clip (los mismos que en `brazos_animaciones.py`). La manija, el agua y la taza suenan en el fregadero; los tragos, en la cabeza de Elías.
- **Probado en Play** con la E, en cámara lenta: la taza sigue a la mano izquierda como en las vistas previas, el chorro aparece solo mientras corre el agua, la manija gira y vuelve, y al final la taza queda exacta en su lugar y Elías parado frente al fregadero.
- Beber es el primer paso del tutorial (ver *El tutorial*).

**Los dos mundos.** La dosis pasa de la abstinencia al efecto y el bajón lo devuelve. El cambio lo hace el componente `EstadosDelMundo` (el objeto `Mundos` de la escena), que lee el JSON del 4B:
- muestra `Deterioro` o `Efecto`;
- pone las texturas limpias y la emisión de cada material;
- enciende las luces de cada mundo (solo en el efecto: el sol del atardecer en la sala y en el dormitorio, la lámpara de pie y el foco del dormitorio);
- cambia el ambiente, la niebla y la luz precalculada.

Elías se entera del cambio: bajo el efecto sus brazos se ven sanos (estado 0, la mentira de la droga); en la abstinencia, como en la Noche 1 (estado 1).

**La Noche 1** (sección 5). La lleva el componente `NocheUno` (el objeto `Noche 1` de la escena), en este orden:
1. **El despertar.** La imagen aclara desde negro en 3 segundos mientras Elías, en el suelo de la sala, se mira las manos (`mirar_manos`) y se levanta.
2. **El tutorial:** buscar agua, limpiar los rastros del consumo y escribir en el cuaderno (ver *El tutorial*).
3. **El teléfono.** 20 segundos después del tutorial, suena. Si Elías contesta, el timbre se corta al levantar el auricular y en la oreja solo hay estática hasta que cuelga. Si no, se corta solo después de 8 timbres (40 segundos). `Partida` cuenta las llamadas contestadas y las perdidas.
4. **Tomás.** 15 segundos después de la llamada aparece sentado en el sofá, pero solo mientras Elías no mira hacia ahí; la ropa tirada en el sofá se esconde mientras él está. Cuando Elías lo ve, a los 0,8 segundos dice: «¿Otra vez sin dormir?». En cuanto Elías deja de mirarlo, ya no está. Se ve según el mundo: «vivo, mal» en la abstinencia y sonriente bajo el efecto.
5. **Los golpes.** 40 segundos después tocan la puerta de entrada: tres golpes cada 7 segundos, hasta 5 veces o hasta que Elías mira por la mirilla. Un segundo y medio antes del primer golpe, la franja de luz bajo la puerta se corta en dos sombras: unos pies. Se quedan hasta el final de la noche, solo en la abstinencia (bajo el efecto no entra luz bajo la puerta). Por la mirilla, el pasillo vacío: los pies no se muestran, solo sus sombras. Cuando deja de mirar (o después del último golpe), una voz detrás de la puerta: «Eli, ábreme».
6. **La puerta.** Desde ahí se puede usar la puerta de entrada: Elías agarra la perilla (el clip `abrir_puerta`, llevado de la puerta del dormitorio a esta) y, al primer segundo, corte a negro. Ahí empieza la Noche 2 (ver *La Noche 2* en *Pasillo del 4º piso*).

Los tiempos y los pensamientos se cambian en el inspector de `Noche 1`; para probar lo que viene después del tutorial, se apaga `tutorial`. Se probó entera en *Play*, por los dos caminos del teléfono.

**El tutorial** (sección 5; 23 de octubre de 2026). Elías tiene que tomar agua, limpiar los rastros del consumo y escribir en el cuaderno. No hay indicadores (6.9): lo guían sus pensamientos, frases cortas abajo en la pantalla, como subtítulos (todavía sin voz; las dice el componente `Pensamientos`). Cada pensamiento aparece solo si todavía hace falta, así que el orden no es obligatorio:

| Cuándo | Pensamiento |
|---|---|
| Al levantarse | «Tengo la boca seca.» |
| Si al minuto no tomó agua | «Agua. En la cocina tiene que haber agua.» |
| Después de tomar agua, si quedan rastros | «Tengo que sacar todo esto de aquí. Las jeringas, todo.» |
| Si pasa un minuto sin recoger nada | «Todavía queda algo.» |
| Al recoger el último | «Ya está. Lo voy a escribir.» |

- **Los rastros** son siete: la jeringa, la cuchara quemada, el cenicero con las colillas, el cinturón y el encendedor de la mesa de centro; la jeringa del piso de la sala y la que está junto al colchón, a pasos de la dosis escondida. Elías se agacha (o se arrodilla, en el piso), lo recoge, lo guarda y vuelve a donde estaba. Solo existen en la abstinencia: bajo el efecto, el 4B está limpio.
- **Dos clips para todos:** `recoger_mesa` y `recoger_piso` (ver *Brazos de Elías*) se hicieron con las jeringas de la mesa y del piso; `RastroInteractivo` los lleva a cada rastro, girados hacia el lado desde donde lo mira Elías. Al terminar, la cámara vuelve a donde estaba Elías, para que no quede parado adentro de un mueble.
- **Para encontrarlos:** cada rastro lleva una caja invisible un poco más grande que sus piezas (3 cm de margen). Elías no choca con ellas.
- **Termina** cuando escribe en el cuaderno después de haber hecho todo; 20 segundos después suena el teléfono. Si en 6 minutos no lo terminó, la noche sigue igual.
- **Probado en Play** entero, con la E: los cinco rastros de la mesa desde distintos lados (por el sur, por el norte entre la mesa y el sofá, por el este), los dos del piso, los pensamientos en su momento y el teléfono a los 20 segundos de escribir. También el pensamiento que insiste, con la espera acortada.

- **La mirilla** es una cámara del lado de afuera de la puerta, a la altura de la mirilla y con 170° de campo. Su imagen pasa por el shader `OnTheNod/Mirilla` (`Assets/Rendering/`), que hace el mismo ojo de pez que `fisheye()` en `dona_carmen.py`: un círculo del 97 % del alto, con los bordes borrosos y oscuros. Mientras se mira, la cámara de Elías no dibuja. Comparada con `carmen_mirilla_vacio.png`, la imagen de Unity sale un 19 % más clara: la pared casi igual, el techo un 30 % y el piso un 57 % (en Blender el piso tiene un brillo que el shader PS1 no copia igual).
- **El pasillo de afuera** es, desde el 24 de octubre de 2026, el pasillo del 4º piso de la Noche 2 (ver *Pasillo del 4º piso*). Antes era el de la prueba de estilo, puesto contra la puerta de entrada.
- **El pasillo no entra en la luz precalculada.** La luz-truco `pasillo_edificio` del 4B (la que entra bajo la puerta) queda dentro del pasillo, a 40 cm de la pared de enfrente, y le dejaba una mancha de luz en el zócalo y en el piso. Unity no deja que una luz precalculada ignore objetos (la máscara de capas de la luz no cuenta en el cálculo), así que el pasillo lo iluminan solo sus lámparas, en tiempo real (las del pasillo de la Noche 2 también). Tampoco usa sondas de luz: las del 4B quedan del otro lado de la pared y le tapaban la lámpara. Sus cuatro lámparas están en *Realtime* en la escena (23 de octubre de 2026): como mixtas ocupaban canales de la máscara de sombras y Unity dejaba entera en la luz precalculada a `luz_sala` (ver *Límite* en *Luz precalculada*). Comparadas antes y después, no se cuelan al 4B: la vista de la entrada no cambia y el pasillo se ve igual.
- **Los sonidos** (sección 11): el timbre y el auricular suenan en el teléfono; la estática, en la oreja; los golpes y la voz, detrás de la puerta; la voz de Tomás, en su cabeza.
- **El ambiente** (24 de octubre de 2026), en el objeto `Ambiente` de la escena (`AmbienteSonoro`): de fondo, la ciudad de noche; en la cocina, el zumbido del fluorescente; y, cada 25 a 70 segundos, un ruido del edificio desde su lugar: las cañerías (en la pared del baño o detrás del fregadero), un golpe arriba (sobre la sala o el dormitorio) o los vecinos a través de la pared (al oeste de la sala o detrás del dormitorio), nunca el mismo dos veces seguidas. El zumbido y los ruidos del edificio son de la abstinencia: bajo el efecto se callan y queda la ciudad.
- **Los pies bajo la puerta** (24 de octubre de 2026): `GolpesEnLaPuerta` prende el grupo `Eventos` del 4B con las dos sombras y los pies apagados. Comparadas en Play, antes y durante los golpes, la franja de luz bajo la puerta queda cortada en dos, como en `4b_entrada.png`.
- **Arreglado** (24 de octubre de 2026): la puerta del dormitorio saltaba a cerrada al empezar su clip, porque en reposo está entreabierta 28° y `abrir_puerta` empieza con la puerta cerrada. Ahora usa `empujar_puerta`, que empieza con la puerta como está.

**Luz precalculada** (una por mundo):
- **Luces mixtas:** la luz directa se calcula en tiempo real, para que ilumine a Elías, a los personajes y a la puerta que se abre. La luz del ambiente (que se oscurece en los rincones) y las sombras de lo que no se mueve quedan precalculadas (*shadowmask*). Así salen exactas las sombras de los cartones de las ventanas, del sol que entra en el efecto y de la rendija bajo la puerta del baño. En tiempo real quedaban demasiado gruesas: Unity tenía que achicar los 29 mapas de sombra para que entraran.
- **Sin rebote:** Blender (EEVEE sin trazado de rayos) no calcula la luz que rebota. Su look se arma con la luz directa, la del ambiente y las luces-truco. Con 3 rebotes, Unity salía más claro que Blender, y en el efecto mucho más: los rincones y el frente del sofá quedaban iluminados (13 niveles de diferencia en la sala, contra 6 sin rebote). Por eso se precalcula sin rebote.
- **Luces-truco:** van solo en la luz precalculada, las de fuga y también las de rebote, que hacen de rebote como en Blender. La mancha cálida del colchón no viene de la farola, porque los cartones tapan casi toda la ventana: viene de `rebote_dormitorio`. Y la silla del baño iluminada desde abajo es `rebote_bano`. En Blender son esferas de 30 a 50 cm; en Unity son puntos y quemarían lo que tienen pegado, así que se separan medio radio de la superficie de abajo.
- **Sondas de luz:** lo que se mueve (Elías, los personajes, la puerta, el auricular) y lo chico (menos de 25 cm) toma la luz de 595 sondas, en una grilla de 50 cm, ubicadas lejos de los muebles de los dos mundos.
- **Cálculo:** con *On the Nod > Precalcular la luz de los mundos* (`Assets/Editor/LuzDeLosMundos.cs`). Primero calcula el efecto y lo copia a `Assets/Scenes/Departamento4B/efecto/`; al final, la abstinencia, que queda como la luz normal de la escena. Un mapa de luz de 1024×1024 por mundo (40 puntos por metro), unos 20 segundos en total. Guarda dónde cae en el mapa cada objeto de la escena, no solo los del 4B. Hay que recalcularla con ese menú cada vez que se vuelve a exportar el 4B; *Generate Lighting* calcula solo el mundo que está puesto y desarma el cambio.
- **Límite:** la máscara de sombras admite 4 luces mixtas por punto. Donde se juntaban más, Unity dejó enteras en la luz precalculada a `luz_cocina` (en los dos mundos) y a `luna_bano`: a lo que se mueve en la cocina y en el baño, su luz le llega por las sondas.
  - Cuando se agregó el pasillo de afuera, con sus lámparas mixtas, Unity dejó entera también a `luz_sala`, y el foco de la sala dejó de iluminar en tiempo real lo que se mueve (Elías, Tomás, la puerta del dormitorio). Por eso esas lámparas van en tiempo real (ver *El pasillo no entra en la luz precalculada*). Hay que tenerlo en cuenta al agregar una luz mixta: si Unity deja entera una que hace falta, se nota en Tomás y en los brazos.
  - Las dos luces del dormitorio bajo el efecto (`luz_dormitorio` y `sol_dormitorio`) van enteras en la luz precalculada a propósito: en el JSON llevan `precalculada`, y `EscenaBlender.Configurar` las pone *Baked*. Probadas como mixtas (también con el pasillo en tiempo real), Unity dejaba enteras además la de la sala y la del patio de la cocina. En el dormitorio, bajo el efecto, lo único que se mueve son los brazos, que tienen su propia luz.

**Comparación con Blender** (diferencia promedio de cada píxel, en niveles de 255):

| Vista | Sin luz precalculada | Con luz precalculada |
|---|---|---|
| `4b_sala` | 3,1 | 2,6 |
| `4b_entrada` | 3,5 | 1,4 |
| `4b_bano` | 7,3 | 3,8 |
| `4b_dormitorio` | 7,5 | 3,7 |
| `4b_cocina` | 8,0 | 7,9 |
| `4b_sala_efecto` | 13 | 6,2 |
| `4b_dormitorio_efecto` | — | 4,6 |

Lo que queda distinto:
- En la cocina, el fluorescente es una luz de área en Blender y en Unity un foco muy abierto, que ilumina de más los frentes de los muebles; además, su bruma es más fuerte.
- Faltan los haces de luz en la niebla: el del sol en el efecto y el de la farola en el dormitorio. La niebla iluminada de Unity no tiene sombras.
- A los costados de la puerta del baño se ven hilos de luz: el temblor de vértices abre rendijas de un píxel entre la puerta y el marco, y por ahí se ve el baño iluminado. Lo mismo pasa bajo el efecto en el dormitorio: debajo de la cortina izquierda se ve una línea punteada de luz, por la rendija entre el muro de abajo de la ventana y el de al lado, porque detrás está el resplandor de afuera.

### Pasillo del 4º piso
Tercer escenario (24 de octubre de 2026) y el primero de la Noche 2. Se genera con `blender/scripts/pasillo_piso4.py`; las vistas están juntas en `blender/renders/pasillo4_hoja.png` y el plano en `blender/renders/pasillo4_plano.png`. Cómo se juega: *Noche 2*, sección 5.

**Distribución** (en L, techo de 2,6 m, con las texturas de la prueba de estilo):
- **El pasillo largo** (17 × 1,8 m) empieza en la puerta de la escalera A y pasa frente a los departamentos: de un lado el 4B, el 4D y el 4F; del otro, el 4A (Doña Carmen, con una estampita de la Virgen en la puerta), el 4C y el 4E. Los focos se alternan, uno prendido y otro quemado, como en la prueba de estilo.
- **El vestíbulo del elevador**, al fondo: el elevador de frente, bajo un fluorescente frío y con un papel pegado que dice «NO FUNCIONA»; a la izquierda, el teléfono público con su repisa y el «PISO 4» pintado en rojo.
- **El tramo corto** (6 m) dobla a la derecha y termina en la puerta de la escalera B, con un cartel verde encima. A mitad de camino está el cuarto de limpieza, con puerta de celosía.
- **Las dos escaleras** son iguales: una U de dos tramos con un descanso y un muro en el medio, un foco en cada rellano, una lámpara con jaula en el descanso, el «PISO 4» pintado junto a la puerta de arriba y junto a la de abajo, y un 4 grande en el descanso. Elías baja por la B y sale por la A.
- **Los escondites.** El 4C, un departamento vacío detrás de la puerta entreabierta: un ropero hueco con una puerta entreabierta, muebles tapados con sábanas, cajas y la ventana clavada con tablas, por donde entra la luz naranja de la calle. Y el cuarto de limpieza (1,2 × 1,2 m): repisas con latas y botellas, el balde con el trapeador, una escoba y la caja de fusibles, todo fuera del recorrido de la puerta, que se abre hacia adentro; desde adentro, con la puerta cerrada, se ve el pasillo entre las tablillas.
- **El elevador por dentro:** cabina de acero rayado con piso de goma, pasamanos, un panel de luz en el techo y la botonera, del 6 al 1, PB y un botón sin número: el piso que no debería existir.

Está en las coordenadas del 4B: su puerta de entrada (x 3,0–3,9) da a este pasillo, y el 4B y el 4A quedan donde estaban en la prueba de estilo, así que la mirilla y las vistas de Doña Carmen siguen valiendo. La puerta del 4D se corrió 1,4 m, porque en la prueba caía encima de la cocina del 4B. Del lado del 4B, el muro del pasillo es una piel de 4 cm delante del muro del 4B: en Unity tapa el papel tapiz del 4B, que hoy se ve desde el pasillo.

| Vista | Qué muestra |
|---|---|
| `pasillo4_comienzo` | Recién salido de la escalera A: el pasillo largo con el elevador al fondo (la composición de la prueba de estilo). |
| `pasillo4_efecto` | La misma vista bajo el efecto. |
| `pasillo4_esquina` | El tramo corto desde el vestíbulo: el cuarto de limpieza y la puerta de la escalera B. |
| `pasillo4_escalera` | Bajando por la escalera B, desde el descanso: abajo, la puerta y el «PISO 4». |
| `pasillo4_vuelta1` … `pasillo4_vuelta5` | Lo que cambia en cada vuelta (ver abajo). |
| `pasillo4_vuelta4_foto` | La Polaroid de la vuelta 4: la misma vista, pero con la puerta. No va en la hoja. |
| `pasillo4_escondite` | Desde el cuarto de limpieza, entre las tablillas. |
| `pasillo4_4c` | El 4C por dentro, desde la puerta. No va en la hoja. |
| `pasillo4_ascensor` | La cabina abierta, en la vuelta 5. No va en la hoja. |
| `pasillo4_plano` | Vista desde arriba, sin techo. |

**Las vueltas.** Lo que aparece en una vuelta está en la colección `VueltaN`; lo que desaparece, en `VueltaN_Fuera`.

| Vuelta | Qué cambia en el modelo |
|---|---|
| 1 | El número del 4D dice «4B» (`Vuelta1`) en lugar de «4D» (`Vuelta1_Fuera`). |
| 2 | Una mancha de humedad en el techo, sobre la puerta del 4B, con el borde amarillento que deja el agua; baja por el muro hasta el marco. Abajo, un charco y tres gotas. |
| 3 | La Polaroid de Tomás en la repisa del teléfono: la misma cámara que lleva Tomás vivo. |
| 4 | Desaparecen la puerta de la escalera B, su marco y su cartel (`Vuelta4_Fuera`), y el vano queda tapado con muro (`Vuelta4`). Se apaga la luz del cartel. |
| 5 | Se apagan los focos y el fluorescente del vestíbulo, y el del tramo corto queda débil. El elevador se abre (en Unity hay que animarlo: cada hoja se corre 56 cm) y se prende la luz de la cabina. En el render, Tomás es una silueta (`SoloRender`). |

**Las dos versiones.** Como en el 4B: `Deterioro` (focos quemados, bolsas de basura, periódicos, manchas, colillas, la planta seca del vestíbulo) y `Efecto` (los cuatro focos prendidos, la planta viva, tapetes frente al 4A y al 4D, y un cuadro entre el 4D y el 4F, del que en la abstinencia solo queda el clavo). El piso, las paredes y el techo del pasillo y de las escaleras tienen su textura limpia (`*_limpio.png`).

**La vuelta en Unity** (falta armarla). Las dos escaleras son copias exactas, con las texturas pegadas a cada escalera y no al mundo, para que no se corran. Al pasar por el descanso de la B, Elías se mueve lo que separa `EscaleraB_ancla` de `EscaleraA_ancla` (en el JSON, `anclas_escalera`), sin girar: las dos escaleras miran hacia el mismo lado. Desde el descanso no se ven las puertas, así que el salto no se nota.

**Las puertas que se abren** (24 de octubre de 2026): la del 4C, la de arriba de la escalera B (desde el tramo corto), la de abajo de la escalera A (desde la escalera, para salir al pasillo largo) y la del cuarto de limpieza. Están hechas como la del dormitorio del 4B, para usar sus clips: se abren empujando, con la bisagra a la derecha de Elías y la perilla a 69 cm de la bisagra (`PERILLA_CLIP`); la del 4C está entreabierta 28°, como aquella. Por eso la vuelta va en un solo sentido: bajando por la B y saliendo por la A. Las otras dos puertas de las escaleras no se abren.

**Las rampas:** sobre cada tramo de escalera hay una rampa invisible que va por las puntas de los escalones. En Blender llevan la propiedad `solo_colision`; en Unity, `ImportadorArte` les deja la colisión y les saca el dibujo. Así Elías sube y baja sin saltos.

**Técnica:** unos 7.800 triángulos en 334 objetos, sin contar lo que es solo para los renders. Los pisos, techos y muros del pasillo van por tramos de unos 4 m, para que ninguna pieza tenga demasiadas luces cerca. Las puertas que se abren (el 4C, las de las escaleras, la del cuarto de limpieza y las del ropero) tienen el origen en la bisagra; las hojas del elevador, en su centro. Quedan fuera de Unity, porque son solo para los renders: la puerta del 4B vista desde afuera (`Fachada4B`; en Unity va la del 4B), la silueta de Tomás y las etiquetas del plano. Con `-- blender --sin-unity`, el script renderiza sin exportar.

**En Unity.** El script exporta `Assets/Art/PasilloPiso4/`: el FBX en la vuelta 0, las 16 texturas y `pasillo_piso4_escena.json` con 19 luces, las cámaras de las vistas y siete estados (`abstinencia`, que es la vuelta 0, `efecto` y `vuelta1` a `vuelta5`). Va en el origen, sin girar, como el 4B. Se importa con las reglas de `ImportadorArte`: un grupo por colección, el shader PS1 y colisión en las piezas que se chocan.

**En la escena jugable** (24 de octubre de 2026, `Departamento4B.unity`): el objeto `Pasillo` reemplaza al pasillo de la prueba de estilo. Tiene el FBX, sus 18 luces (salen del JSON, cada una con el primer estado en que está prendida) y su propio `EstadosDelMundo`, que sigue al del 4B (`sigue`): cuando la dosis cambia el mundo, cambia todo. No tiene luz precalculada (`tieneLuzPrecalculada` apagado, para que *Precalcular la luz de los mundos* use la del 4B).
- **Fuera de la luz precalculada**, como el de la prueba: sus piezas no son fijas, no usan sondas y sus luces van en tiempo real.
- **Sombras de calidad baja** (256 px, la primera de las tres del proyecto): una luz puntual con sombra ocupa seis mapas, y con las del pasillo Unity tenía que achicar todas para que entraran 31 en el espacio de sombras. A 480×270 no se nota. El indicador del elevador y los carteles de las escaleras no tienen sombra.
- **La niebla por zonas:** la niebla iluminada no sabe de paredes, así que `NieblaPorZonas` cambia las luces que la iluminan según dónde está Elías: en el 4B, las del 4B; en el pasillo largo y el tramo corto, las ocho del pasillo; en cada escalera, en el 4C, en el cuarto de limpieza y en la cabina, las suyas.
- **Las puertas** llevan `PuertaInteractiva` con el clip de la del dormitorio llevado a cada una (`pista`: `puerta_dormitorio`, y `giro`, cuánto se gira esa puerta para que quede como esta: 90° el 4C y la escalera B, −90° la escalera A y 180° el cuarto de limpieza). El movimiento de la puerta se cuenta desde el primer cuadro del clip (`desdeElInicio`): la del dormitorio descansa entreabierta y estas, cerradas. La de celosía lleva una caja invisible (`cubrir`): si no, la mirada de Elías pasaba entre las tablillas.
- **Probado en Play:** la salida del 4B al final de la Noche 1, las cuatro puertas en cámara lenta (la mano agarra la perilla y la puerta gira alrededor de su bisagra), bajar las dos escaleras por las rampas, salir al pasillo largo por la escalera A y el cambio al efecto y de vuelta.
- **Comparado con Blender** (diferencia promedio de cada píxel, en niveles de 255): `pasillo4_comienzo`, 4,4; `pasillo4_esquina`, 8,7. En el tramo corto Unity sale más oscuro: el fluorescente es una luz de área en Blender y en Unity un foco muy abierto, como en la cocina del 4B.

**La Noche 2** empieza al abrir la puerta del 4B al final de la Noche 1 (`NocheDos`): a oscuras, la puerta queda abierta (el 4B sigue siendo el refugio), se van los pies de abajo de la puerta y la mirilla deja de usarse; la imagen aclara con Elías en el umbral, mirando el pasillo hacia el elevador, y piensa: «No hay nadie.». Es la vuelta 0. Todavía faltan la vuelta (el salto de una escalera a otra) y lo que cambia en cada una.

---

## 11. Sonido

- **El teléfono** es el motivo sonoro principal. Su timbre debe reconocerse al instante y dar cada vez más miedo.
- **El tema de la madre:** la melodía de la cajita musical de su joyero (ver 4.1).
- **Ambiente:** zumbido de fluorescentes, tuberías, el elevador, vecinos a través de las paredes, una tele lejana, la ciudad de noche.
- **Elías:** respiración, latidos y voz temblorosa según la abstinencia.
- **Música:** mínima, industrial y ambiental (referencia: Akira Yamaoka en Silent Hill). Durante el efecto, una canción cálida que se distorsiona al pasar.
- **Silencio:** usarlo. Los momentos sin nada son los que más tensan.

**Lo que ya hay** (20 de octubre de 2026): los sonidos de la Noche 1. Se generan con `audio/scripts/sonidos.py` (Python con numpy), como los assets de Blender: para cambiar un sonido se cambia el script y se vuelve a correr. Todo a 22.050 Hz y en mono, como en la PS1. Quedan en `unity/Assets/Audio/`.

| Sonido | Qué es |
|---|---|
| `telefono_timbre` | Un ciclo del timbre de un teléfono fijo viejo: dos campanas golpeadas 20 veces por segundo durante 1,2 segundos, y silencio hasta los 5. Va en bucle. |
| `telefono_descolgar` | El auricular que se levanta: el golpe del plástico y el clic del gancho. |
| `telefono_colgar` | El auricular que vuelve a la base: el golpe y un «tin» de las campanas. |
| `telefono_estatica` | La línea sin nadie (6.5): ruido con el sonido apagado de un teléfono, chasquidos, el zumbido de la corriente y dos cortes. 8 segundos en bucle, sin saltos. |
| `golpes_puerta` | Tres golpes de nudillos en la puerta de entrada, oídos desde adentro. |
| `voz_tomas_otra_vez_sin_dormir` | Tomás en el sofá: «¿Otra vez sin dormir?». **Provisional.** |
| `voz_eli_abreme` | La voz detrás de la puerta: «Eli, ábreme», apagada por la puerta. **Provisional.** |
| `llave_manija` | La manija de la llave del fregadero al girar: el chirrido del metal que se pega y se suelta. |
| `agua_taza` | El agua que cae en la taza mientras corre (1,75 s): burbujas y un tono que sube a medida que la taza se llena, con las cañerías viejas abajo. Al cerrar, dos gotas. |
| `taza_loza` | La taza de loza contra el fregadero de metal, al tomarla y al dejarla. |
| `beber` | Tres tragos y el aire que sale por la nariz después. |
| `ambiente_ciudad` | La ciudad de noche, lejos: un rumor grave y dos autos que pasan. 40 s en bucle, sin saltos. |
| `zumbido_fluorescente` | El fluorescente de la cocina: el zumbido de 120 Hz del balasto y unos chasquidos del tubo. 4 s en bucle. |
| `canerias` | Las cañerías viejas del edificio: dos golpes de metal y el agua que corre, a través de la pared. |
| `vecino_golpe` | Algo pesado que cae en el departamento de arriba. |
| `vecinos_murmullo` | Dos voces apagadas a través de la pared, que se turnan. No se entiende nada. |
| `respiracion` | Un ciclo de la respiración de Elías, temblorosa. 3,6 s en bucle; el juego la acelera y la sube con la abstinencia. |
| `latido` | Un latido: los dos golpes del corazón. El juego lo repite a un ritmo que sube con la abstinencia. |

- **Las voces son provisionales:** son la voz sintética de Windows (la única en español es de mujer), con el tono bajado para que suene a hombre. Hay que grabarlas y reemplazar los archivos con el mismo nombre.

---

## 12. Alcance y plan de producción

### Fases
1. **Preproducción** (ahora): este documento, prueba de estilo en Blender y decisiones pendientes (sección 13).
2. **Demo — Noches 1 y 2** (20–40 min): el 4B, el pasillo y el elevador. Mecánicas principales: movimiento, interacción, abstinencia, dosis, cámara, teléfono y una persecución. Si la demo funciona y la motivación sigue, se continúa.
3. **Noches 3 a 5.**
4. **Finales, Nueva partida+, pulido y sonido.**

### Assets de la demo

**Escenarios**
- Departamento 4B: sala, cocina, dormitorio y baño (**hecho**: primera versión, ya exportada a Unity; ver sección 10). El interior del baño ya está modelado; falta su versión para la Noche 5.
- Pasillo modular: tramos de pared, piso y techo, puertas con marco, focos, fluorescentes, tuberías (**hecho**: el pasillo del 4º piso, en L, con las dos escaleras, el 4C vacío y el cuarto de limpieza; jugable en la escena del 4B desde el final de la Noche 1; ver *Pasillo del 4º piso*, sección 10).
- Elevador: exterior e interior (**hecho**: primera versión, en el pasillo del 4º piso).

**Objetos**
- Teléfono fijo, teléfono público del pasillo, cuaderno, Polaroid, fotos. El teléfono público (**hecho**, en el pasillo del 4º piso). La Polaroid ya existe como objeto (colgada del cuello de Tomás vivo y en la repisa del teléfono, en la vuelta 3); falta poder sacar fotos. El cuaderno de la mesa de centro (**hecho**: guarda la partida, jugable en el 4B; ver *El cuaderno* en *El 4B jugable*, sección 10).
- Jeringas, cucharas, cinturón, dosis. La dosis de la Noche 1 (**hecho**: la media con la jeringa bajo el colchón, jugable en el 4B; ver *Departamento 4B* y *El 4B jugable* en la sección 10). Los rastros del consumo del 4B (**hecho**: se recogen en el tutorial de la Noche 1; ver *El tutorial* en la sección 10).
- Sofá, cama, mesa, sillas, refrigerador, tele vieja, ventanas tapadas con cartón y periódicos, basura, botellas.

**Personajes**
- Elías: brazos en primera persona (**hecho**: cuatro estados, ya exportados a Unity con sus clips; ver sección 10) y cuerpo completo para espejos y cinemáticas.
- Tomás vivo y muerto (**hecho**: un modelo con cinco estados, del vivo sonriente a la calavera, ya exportado a Unity como *Humanoid*; ver sección 10).
- Doña Carmen y su plato tapado (**hecho**: dos vestuarios y las vistas por la mirilla, ya exportada a Unity como *Humanoid*; ver sección 10). En la demo solo se ve por la mirilla.

**Animaciones**
- Brazos de Elías: abrir puertas, contestar y colgar el teléfono, temblor, mirarse las manos, tomar la jeringa, sacar la dosis de abajo del colchón, llenar una taza en el fregadero y beber, tomar el cuaderno y recoger algo de la mesa o del piso (**hecho**, ver sección 10). Falta: usar la cámara.
- Tomás vivo: sentado, de pie, caminar, gestos. (Ya tiene las poses sentado y de pie; el resto, con Mixamo en Unity.)
- Tomás muerto: quieto, aparecer de golpe, caminar, perseguir. (Ya tiene las poses de pie y sentado; el resto, con Mixamo en Unity.)
- Doña Carmen: tocar la puerta, dejar el plato e irse. (Ya tiene las poses; el resto, con Mixamo en Unity.)
- Escenario: puertas, elevador, luces que parpadean, objetos que se mueven.

**Sonido**
- La Noche 1: el teléfono (timbre, auricular y estática), los golpes en la puerta, el agua del fregadero (la manija, el chorro, la taza y los tragos) y las dos voces (**hecho**, con las voces provisionales; ver sección 11).
- El ambiente del 4B y el cuerpo de Elías (la respiración y los latidos, que siguen a la abstinencia) (**hecho**: ver sección 11 y *El 4B jugable* en la sección 10).
- Falta: la música (también la del efecto), la voz temblorosa de Elías y el resto de las noches.

### Herramientas y flujo
- **Blender 5.2:** modelado y texturas. Los escenarios y objetos se generan con scripts de Python que después se pueden retocar a mano.
- **Mixamo:** rig y animaciones base de los personajes.
- **Unity 6:** el juego. Se exporta desde Blender en FBX: cada script llama al final a `blender/scripts/exportar_unity.py`, que deja en `unity/Assets/Art/<asset>/` el FBX, sus texturas y un JSON con las luces, las cámaras y los estados del mundo.

### Estructura de carpetas
```
C:\Dev\Personal\OnTheNod\
├── docs/                  documentos de diseño
├── blender/
│   ├── scripts/           scripts que generan escenarios y objetos
│   ├── textures/          texturas pixeladas (PNG)
│   ├── scenes/            archivos .blend
│   └── renders/           pruebas y renders
├── audio/
│   └── scripts/           scripts que generan los sonidos (los dejan en unity/Assets/Audio/)
└── unity/                 proyecto de Unity
    └── Assets/
        ├── Art/           lo que exportan los scripts de Blender: una carpeta por asset (FBX y Textures/)
        ├── Audio/         los sonidos (WAV)
        ├── Rendering/     estilo PS1: shaders, imagen de 480×270, pantalla, niebla iluminada, ojo de pez de la mirilla
        ├── Scripts/       el juego: Elías, sus brazos, lo que se usa y los datos de Blender
        ├── Editor/        herramientas del editor: importación automática, capturas, máscara de foco
        ├── Scenes/        escenas (y la luz precalculada de cada una, en una carpeta con su nombre)
        └── Settings/      configuración de URP
```

---

## 13. Decisiones pendientes

1. ~~Cámara~~ **Decidido: primera persona.** Es más inmersiva, ahorra mucha animación y el jugador ve cómo se deterioran sus propios brazos.
2. ~~A quién llama Elías en el final bueno~~ **Decidido:** a su madre (ver sección 7).
3. ~~Ambientación~~ **Decidido:** una ciudad latinoamericana sin nombre (ver sección 5). Es poco común en el género y le da identidad propia.
4. **Idioma.** Recomendado: textos y voces en español, con subtítulos en inglés.
5. ~~Nombres~~ **Decidido:** Elías, Tomás, Eva, José y Doña Carmen (ver 4.2).
6. ~~Título~~ **Decidido:** *On the Nod* (ver sección 14).

---

## 14. Título: *On the Nod*

Decidido el 18 de octubre de 2026.

**Por qué funciona:**
- **Calle:** *on the nod* es como se dice en inglés al estado de cabecear, medio dormido, bajo el efecto de la heroína.
- **Biblia:** *Nod* es la tierra donde Caín vagó después de matar a su hermano (Génesis 4:16; ver 3.4). En el elevador, el botón **N** lleva ahí.
- Se usa el mismo título en todos los países, sin traducir, como *Silent Hill*. Para el público latino el significado no se pierde: se descubre dentro del juego.

**En Steam** (revisado el 18 de octubre de 2026): no hay ningún juego llamado *On the Nod*. *Nod* a secas no está tomado, pero se confunde con *Land of Nod* (anunciado) y con la Hermandad de Nod de *Command & Conquer*, y es difícil de encontrar en buscadores. Por eso el título completo es *On the Nod*.

**Logo:** "on the" en pequeño y **NOD** grande, para que en la práctica se lea y se recuerde como *Nod*.

**Descartados:** *Como antes / Like Before* (libre en Steam; la frase sigue siendo central dentro del juego), *Una más / One More* (demasiados "One More…" en Steam) y *4B* (queda como el lugar).
