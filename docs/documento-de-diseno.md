# On the Nod — Documento de diseño

> Título: ***On the Nod*** (ver sección 14).
> Versión 0.3 · 18 de octubre de 2026

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
4. **Solo textos de dominio público**, en español y en inglés: la Biblia Reina-Valera 1909 y la King James, y poemas publicados antes de 1929 (Vallejo, Bécquer, Dickinson, Poe). Antes de usarlos en el juego, verificar cada cita contra una edición confiable.

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
> «Y deseando morirse, dijo: Baste ya, oh Jehová, quita mi alma…» … «Levántate y come, porque gran camino te resta.»
> *"He requested for himself that he might die…" … "Arise and eat; because the journey is too great for thee."*

Es el pasaje bíblico más directo sobre querer morir, y la respuesta no es un reproche: es pan, agua y descanso. Así funciona la comida que Doña Carmen le deja en la puerta (ver 6.10). Y el protagonista lleva el nombre del profeta: es su misma historia.

**El buen samaritano** — Lucas 10:29
> «¿Y quién es mi prójimo?»
> *"And who is my neighbour?"*

Doña Carmen es la que se detiene cuando nadie más lo hace. En inglés el juego de palabras es directo: *neighbor* significa vecino y prójimo a la vez.

**El hijo pródigo** — Lucas 15:20-24
> «Y como aún estuviese lejos, lo vio su padre, y fue movido a misericordia, y corrió…» … «Este mi hijo muerto era, y ha revivido; se había perdido, y es hallado.»
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
- Elías despierta en el suelo, temblando. Tutorial integrado: buscar agua, ordenar el cuarto, escribir en el cuaderno.
- El teléfono suena; al contestar solo hay estática. (Es su madre; el jugador aún no lo sabe.)
- Tomás vivo aparece en el sofá: *«¿Otra vez sin dormir?»*. Al voltear, ya no está.
- Hay droga escondida en el departamento. Primera oportunidad de consumir.
- Golpes en la puerta. Por la mirilla no hay nadie. Una voz: *«Eli, ábreme»*. Al abrir, el pasillo.

### Noche 2 — El pasillo
- Estilo P.T.: el pasillo del 4º piso se repite. En cada vuelta algo cambia (una puerta de más, un número distinto, una mancha que crece). Para avanzar hay que notar la diferencia.
- Elías encuentra la cámara Polaroid de Tomás. La primera foto muestra una puerta que a simple vista no existe.
- Primera aparición de Tomás muerto al fondo del pasillo, a contraluz del elevador. Primera persecución: huir y esconderse.
- El elevador lleva a pisos que no deberían existir.

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
| En Unity | URP, shader con vertex snapping (el "temblor" de los vértices de PS1), niebla, post-proceso de dithering |

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
| `abrir_puerta` | 2,8 s | Agarra la perilla, la gira y empuja la puerta. |
| `telefono_contestar` | 2,4 s | Levanta el auricular y se lo lleva al oído. Al terminar, Elías mira hacia el pasillo y la puerta del baño. |
| `telefono_colgar` | 1,8 s | Devuelve el auricular a la base y baja la mano. |

- **Cámara de interacción:** abrir una puerta o contestar el teléfono mueve la cámara a un punto fijo frente al objeto (inclinado sobre la mesita, frente a la perilla), y desde ahí corre la animación. Así la mano siempre llega al objeto.
- **Luz de los brazos:** una luz tenue pegada a la cámara, que solo ilumina los brazos, para que se lean en los cuartos oscuros.

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
| `4b_plano` | Vista desde arriba, sin techo. |

**Detalles que cuentan la historia** (nunca se explican):
- **La silla en la puerta del baño.** Falta una de las dos sillas del comedor: Elías la usó para trabar la puerta del baño, que abre hacia el pasillo. Bajo el efecto, la silla vuelve a la mesa.
- **La luz bajo la puerta del baño.** Por debajo sale una línea de luz fría, aunque nadie abre esa puerta desde hace ocho meses.
- **La marca de la foto.** En la sala hay un rectángulo de papel tapiz menos gastado y un clavo: ahí colgaba la foto familiar. Bajo el efecto, la foto está.
- **El calendario** de la cocina quedó en el mes en que murió Tomás, con un día marcado en rojo.
- **La contestadora** tiene la luz roja encendida: hay mensajes sin escuchar.
- **Los pies bajo la puerta.** Cuando tocan (Noche 1), la luz del pasillo que entra por debajo de la puerta se corta en dos sombras. Por la mirilla no hay nadie.
- **El cuaderno** (donde se guarda la partida) está en la mesa de centro, junto a la cuchara quemada, la jeringa y el cinturón.

**Las dos versiones en una escena.** Los objetos están en colecciones: `Estructura` y `Muebles` (siempre), `Deterioro` (abstinencia) y `Efecto` (bajo el efecto). Paredes, pisos, techo y sofá tienen dos texturas, la sucia y la limpia (`*_limpio.png`). En Unity, cambiar de mundo es mostrar u ocultar un grupo de objetos y cambiar esas texturas.

**Técnica:** unos 6.800 triángulos en 258 objetos. Las puertas tienen el origen en la bisagra, listas para animar. Algunas luces son trucos para Blender (las que se cuelan bajo las puertas y las de "rebote"); en Unity se resuelven con luz precalculada (*baked*).

---

## 11. Sonido

- **El teléfono** es el motivo sonoro principal. Su timbre debe reconocerse al instante y dar cada vez más miedo.
- **El tema de la madre:** la melodía de la cajita musical de su joyero (ver 4.1).
- **Ambiente:** zumbido de fluorescentes, tuberías, el elevador, vecinos a través de las paredes, una tele lejana, la ciudad de noche.
- **Elías:** respiración, latidos y voz temblorosa según la abstinencia.
- **Música:** mínima, industrial y ambiental (referencia: Akira Yamaoka en Silent Hill). Durante el efecto, una canción cálida que se distorsiona al pasar.
- **Silencio:** usarlo. Los momentos sin nada son los que más tensan.

---

## 12. Alcance y plan de producción

### Fases
1. **Preproducción** (ahora): este documento, prueba de estilo en Blender y decisiones pendientes (sección 13).
2. **Demo — Noches 1 y 2** (20–40 min): el 4B, el pasillo y el elevador. Mecánicas principales: movimiento, interacción, abstinencia, dosis, cámara, teléfono y una persecución. Si la demo funciona y la motivación sigue, se continúa.
3. **Noches 3 a 5.**
4. **Finales, Nueva partida+, pulido y sonido.**

### Assets de la demo

**Escenarios**
- Departamento 4B: sala, cocina, dormitorio y baño (**hecho**: primera versión, ver sección 10). El interior del baño ya está modelado; falta su versión para la Noche 5.
- Pasillo modular: tramos de pared, piso y techo, puertas con marco, focos, fluorescentes, tuberías.
- Elevador: exterior e interior.

**Objetos**
- Teléfono fijo, teléfono público del pasillo, cuaderno, Polaroid, fotos.
- Jeringas, cucharas, cinturón, dosis.
- Sofá, cama, mesa, sillas, refrigerador, tele vieja, ventanas tapadas con cartón y periódicos, basura, botellas.

**Personajes**
- Elías: brazos en primera persona (**hecho**: cuatro estados, ver sección 10) y cuerpo completo para espejos y cinemáticas.
- Tomás vivo y muerto (**hecho**: un modelo con cinco estados, del vivo sonriente a la calavera; ver sección 10).
- Doña Carmen y su plato tapado (**hecho**: dos vestuarios y las vistas por la mirilla; ver sección 10). En la demo solo se ve por la mirilla.

**Animaciones**
- Brazos de Elías: abrir puertas, contestar y colgar el teléfono, temblor y mirarse las manos (**hecho**, ver sección 10). Faltan: tomar objetos y usar la cámara.
- Tomás vivo: sentado, de pie, caminar, gestos. (Ya tiene las poses sentado y de pie; el resto, con Mixamo en Unity.)
- Tomás muerto: quieto, aparecer de golpe, caminar, perseguir. (Ya tiene las poses de pie y sentado; el resto, con Mixamo en Unity.)
- Doña Carmen: tocar la puerta, dejar el plato e irse. (Ya tiene las poses; el resto, con Mixamo en Unity.)
- Escenario: puertas, elevador, luces que parpadean, objetos que se mueven.

### Herramientas y flujo
- **Blender 5.2:** modelado y texturas. Los escenarios y objetos se generan con scripts de Python que después se pueden retocar a mano.
- **Mixamo:** rig y animaciones base de los personajes.
- **Unity 6:** el juego. Se exporta desde Blender en FBX.

### Estructura de carpetas
```
C:\Dev\Personal\OnTheNod\
├── docs/                  documentos de diseño
├── blender/
│   ├── scripts/           scripts que generan escenarios y objetos
│   ├── textures/          texturas pixeladas (PNG)
│   ├── scenes/            archivos .blend
│   └── renders/           pruebas y renders
└── unity/                 proyecto de Unity (los FBX exportados van en Assets/)
```

---

## 13. Decisiones pendientes

1. ~~Cámara~~ **Decidido: primera persona.** Es más inmersiva, ahorra mucha animación y el jugador ve cómo se deterioran sus propios brazos.
2. **¿A quién llama Elías en el final bueno?** Recomendado: a su madre. Alternativa: a una línea de ayuda, o las dos cosas (primero la línea y, en el epílogo, la madre).
3. **Ambientación.** Recomendado: una ciudad latinoamericana sin nombre. Es poco común en el género y le da identidad propia.
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
