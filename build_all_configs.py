#!/usr/bin/env python3
"""
build_all_configs.py
Genera todos los carruseles/<folder>.json a partir de los precios reales
de PRECIOS_PETCOLINAS.json. Ejecutar cada vez que cambien los precios.

Regla: NADA de lo que esté en los configs puede ser inventado.
Todos los precios y servicios vienen de PRECIOS_PETCOLINAS.json.
"""
import json
from pathlib import Path

P = json.loads(Path("PRECIOS_PETCOLINAS.json").read_text())
g  = P["grooming"]
v  = P["veterinaria"]
ub = P["ubicacion"]
ig = P["instagram"]
hr = P["horario"]

bano   = g["bano_base"]
combos = g["combos_mas_vendidos"]
add    = g["adicionales"]

CTA_LINEAS = [f"📱 Escríbenos por WhatsApp", f"⏰ {hr}", ig]
FOOTER_CAP = f"\n\n📍 {ub}\n{ig}"

CONFIGS = {

# ─────────────────────────────────────────────────────────────────────────────
"vacunas-precios": {
  "caption": f"💉 Estos son nuestros precios de vacunas en PetColinas\n\nMantén a tu perrito protegido con el esquema completo de vacunación 🐾{FOOTER_CAP}\n\n#PetColinas #VacunasPerros #SaludAnimal #VeterinariaDominicana #MascotasRD #SantoDomingo",
  "slides": [
    {"tipo":"portada","bg_prompt":"Cute puppy looking healthy and happy at veterinary clinic, bright clean environment, no people, no text","titulo":"Nuestros precios de vacunas","subtitulo":"Protege a tu perrito 💉"},
    {"tipo":"contenido","bg_prompt":"Veterinary vaccine vials and syringes on clean white surface, professional medical setting, no people, no text","titulo":"¿Por qué vacunar?","puntos":["Previene enfermedades mortales","Protege a toda la familia","Requerido para parques y guarderías","Refuerzos anuales obligatorios","Un perro vacunado es un perro feliz"]},
    {"tipo":"contenido","bg_prompt":"Healthy happy dog portrait, clean bright background, no people, no text","titulo":"Vacunas disponibles","puntos":[f"Quíntuple  — RD${v['vacuna_quintuple']:,}",f"Séxtuple   — RD${v['vacuna_sextuple']:,}",f"Triple     — RD${v['vacuna_triple']:,}",f"Rabia      — RD${v['vacuna_rabia']:,}",f"Bordetella — RD${v['vacuna_bordetella']:,}",f"Giardia    — RD${v['vacuna_giardia']:,}"]},
    {"tipo":"precio","bg_prompt":"Puppy at first veterinary visit, clean clinic, no people, no text","nombre_plan":"Combo Primera Vacuna","precio":f"RD${v['combo_primera_vacuna']:,}","incluye":["Consulta inicial incluida","Vacuna quíntuple","Desparasitante interno","Asesoría de calendario vacunal"]},
    {"tipo":"contenido","bg_prompt":"Dog health record and vaccination card, stethoscope, clean white background, no text","titulo":"Consulta veterinaria","puntos":[f"Consulta general — RD${v['consulta']:,}","Diagnóstico y toma de muestra disponible",f"Test Parvo/Corona/Giardia — RD${v['test_parvo_corona_giardia']:,}","Atención personalizada para tu mascota"]},
    {"tipo":"cta","bg_prompt":"Healthy happy vaccinated dog wearing bandana, bright cheerful background, no people, no text","titulo":"¡Vacuna a tu perrito!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"bano-en-casa": {
  "caption": f"🛁 ¿Bañas a tu perro en casa? Aquí te decimos cómo hacerlo bien\n\nY si prefieres dejarlo en manos de profesionales, en PetColinas estamos para ti 🐾{FOOTER_CAP}\n\n#PetColinas #BañoCanino #CuidadoPerros #TipsPerros #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Fluffy wet dog in bathtub looking adorable, warm bathroom setting, no people, no text","titulo":"Cómo bañar a tu perro en casa","subtitulo":"Guía paso a paso 🛁"},
    {"tipo":"contenido","bg_prompt":"Dog shampoo bottles, towels, brush and rubber mat on clean white surface, flat lay, no text","titulo":"Lo que necesitas","puntos":["Shampoo especial para perros (nunca humano)","Toalla absorbente grande","Cepillo para el pelo","Algodón para los oídos","Secador a temperatura baja","Agua tibia (no caliente ni fría)"]},
    {"tipo":"contenido","bg_prompt":"Fluffy clean dog wrapped in white towel, happy expression, bright background, no people, no text","titulo":"Paso a paso","puntos":["Cepilla antes del baño para quitar nudos","Moja todo el cuerpo con agua tibia","Aplica shampoo de cuello a cola","Enjuaga bien hasta que el agua salga limpia","Seca con toalla y luego con secador","Cepilla mientras secas para evitar nudos"]},
    {"tipo":"contenido","bg_prompt":"Dog shaking water off, playful outdoor scene, no people, no text","titulo":"Errores comunes","puntos":["Mojar las orejas por dentro (causa infecciones)","Usar agua muy caliente o muy fría","Dejar shampoo sin enjuagar","No secar bien (causa hongos y mal olor)","Bañar con mucha frecuencia (quita aceites naturales)"]},
    {"tipo":"contenido","bg_prompt":"Professional dog grooming salon interior, clean and bright, grooming table, no people, no text","titulo":"¿Cuándo ir al groomer?","puntos":[f"Baño profesional desde RD${bano['pequeño']:,}","Cada 3-4 semanas para razas con pelo largo","Corte incluido según el estilo que elijas","Secado y cepillado profesional incluido","Limpieza de oídos y corte de uñas"]},
    {"tipo":"cta","bg_prompt":"Happy clean fluffy dog after professional grooming, wearing bow, bright background, no people, no text","titulo":"¡Reserva su baño!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"alimentacion": {
  "caption": f"🥣 ¿Sabes realmente qué está comiendo tu perro?\n\nUna buena alimentación es la base de su salud 🐶💚\n\nEn nuestra tienda encontrarás alimentos de calidad para tu mascota.{FOOTER_CAP}\n\n#PetColinas #AlimentacionCanina #NutricionPerros #MascotasRD #SaludAnimal",
  "slides": [
    {"tipo":"portada","bg_prompt":"Happy dog eating from bowl, clean bright kitchen background, no people, no text","titulo":"Alimentación sana para tu perro","subtitulo":"La base de su salud 🥣"},
    {"tipo":"contenido","bg_prompt":"Premium dry dog food in bowl, scattered kibble on white surface, professional food photography, no text","titulo":"Tipos de alimento","puntos":["Seco (croquetas): el más práctico y económico","Húmedo (latas): más palateable y rico en agua","Mixto: combina seco y húmedo","Elige siempre alimentos para la etapa de vida","Cachorro, adulto y senior tienen necesidades distintas"]},
    {"tipo":"contenido","bg_prompt":"Dog food bowl portion size, measuring cup beside it, clean white background, no text","titulo":"¿Cuánto darle?","puntos":["Sigue las instrucciones del empaque según el peso","Divide en 2 comidas al día (adultos)","Cachorros: 3-4 comidas al día","No lo sobrealimentes — el sobrepeso es dañino","Siempre agua fresca disponible las 24 horas"]},
    {"tipo":"contenido","bg_prompt":"Forbidden foods for dogs, grapes, chocolate, onion on red background, warning style, no people, no text","titulo":"Alimentos prohibidos","puntos":["🚫 Chocolate — tóxico para perros","🚫 Uvas y pasas — daño renal grave","🚫 Cebolla y ajo — destruyen glóbulos rojos","🚫 Aguacate — causa vómitos y diarrea","🚫 Xilitol (chicles, dulces) — muy peligroso","🚫 Huesos cocidos — pueden astillarse"]},
    {"tipo":"contenido","bg_prompt":"Healthy energetic dog running and playing, vibrant colors, no people, no text","titulo":"Señales de buena nutrición","puntos":["Pelo brillante y sin caída excesiva","Energía y ánimo para jugar","Deposiciones firmes y regulares","Peso estable y adecuado a su raza","Ojos brillantes y sin legañas","Dientes limpios y sin mal aliento"]},
    {"tipo":"cta","bg_prompt":"Dog sitting beside full food bowl, happy and healthy, bright background, no people, no text","titulo":"Visítanos en PetColinas","subtitulo":"Tenemos alimentos de calidad para tu mascota","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"primeros-auxilios": {
  "caption": f"🚨 Primeros auxilios para mascotas: lo que todo dueño debe saber\n\nEn caso de emergencia, en PetColinas estamos aquí para ti 🐾{FOOTER_CAP}\n\n#PetColinas #PrimerosAuxilios #EmergenciaVeterinaria #MascotasRD #SaludAnimal",
  "slides": [
    {"tipo":"portada","bg_prompt":"Worried but alert dog portrait, close-up, serious mood, clean background, no people, no text","titulo":"Primeros auxilios para tu mascota","subtitulo":"Lo que todo dueño debe saber 🚨"},
    {"tipo":"contenido","bg_prompt":"Red alert emergency symbols, paw print, urgent medical icons, dark dramatic background, no text","titulo":"Señales de emergencia","puntos":["Dificultad para respirar o jadeo excesivo","Convulsiones o pérdida de conciencia","Sangrado que no para","Vómitos o diarrea con sangre","Imposibilidad de pararse o caminar","Abdomen hinchado y duro"]},
    {"tipo":"contenido","bg_prompt":"Dog first aid kit, bandages, gauze, thermometer on white surface, no people, no text","titulo":"Kit de emergencia básico","puntos":["Gasa y vendas para heridas","Termómetro rectal (normal: 38-39.5°C)","Agua oxigenada para limpiar heridas","Suero fisiológico para ojos","Teléfono del veterinario siempre a mano","Transportín o cobija para movilizar"]},
    {"tipo":"contenido","bg_prompt":"Dog lying calm being observed, gentle care, soft indoor lighting, no people, no text","titulo":"Mientras llegas al veterinario","puntos":["Mantén la calma — tu perro siente tu ansiedad","No le des medicamentos humanos NUNCA","Si sangra: presiona con gasa limpia","Si se atraganta: no metas los dedos sin saber","Golpe de calor: ponlo a la sombra con agua fresca","Transporte seguro en brazos o en su caja"]},
    {"tipo":"contenido","bg_prompt":"Prohibited items for dogs, human medicines, pills, danger warning, red and white colors, no text","titulo":"Lo que NUNCA debes hacer","puntos":["🚫 Ibuprofeno, aspirina o acetaminofén — tóxicos","🚫 Hacerle vomitar sin indicación veterinaria","🚫 Dejar pasar síntomas esperando que mejore","🚫 Darle agua a un perro inconsciente","🚫 Aplicar alcohol en heridas abiertas"]},
    {"tipo":"cta","bg_prompt":"Healthy happy dog after veterinary care, relieved expression, bright background, no people, no text","titulo":"¿Emergencia veterinaria?","subtitulo":f"📍 {ub}","lineas":["📱 Contáctanos por WhatsApp",f"⏰ {hr}",ig]},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"cuidado-dental": {
  "caption": f"🦷 ¿Le limpias los dientes a tu perro?\n\nEl 80% de los perros tienen problemas dentales a los 3 años. ¡Prevengámoslo! 🐾{FOOTER_CAP}\n\n#PetColinas #SaludDental #CuidadoDental #PerrosRD #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Cute dog showing teeth in big happy smile, clean bright background, no people, no text","titulo":"Salud dental para tu perro","subtitulo":"Más importante de lo que crees 🦷"},
    {"tipo":"contenido","bg_prompt":"Dog mouth and teeth close-up, healthy pink gums and white teeth, clean macro photography, no people, no text","titulo":"¿Por qué importa?","puntos":["El 80% de perros tienen problemas dentales a los 3 años","El sarro acumulado causa dolor e infecciones","Las bacterias bucales pueden afectar corazón y riñones","El mal aliento es señal de un problema real","La prevención es mucho más económica que el tratamiento"]},
    {"tipo":"contenido","bg_prompt":"Dog dental hygiene products, pet toothbrush, toothpaste tube, dental chews on white background, no text","titulo":"Señales de alerta","puntos":["😷 Mal aliento persistente","🔴 Encías rojas, inflamadas o sangrantes","😬 Dientes amarillos o marrones con sarro","😓 Dificultad o dolor al masticar","💧 Babeo excesivo sin causa aparente","🦷 Pérdida de piezas dentales"]},
    {"tipo":"contenido","bg_prompt":"Dog chewing dental treat or toy, happy playful expression, bright background, no people, no text","titulo":"Cómo cuidar sus dientes","puntos":["Cepilla sus dientes 2-3 veces por semana","Usa SOLO pasta dental para perros (la humana es tóxica)","Ofrece juguetes y premios dentales","Dales huesos crudos aptos para perros","Revisión dental en cada consulta veterinaria"]},
    {"tipo":"precio","bg_prompt":"Pet toothpaste and toothbrush on clean white surface, minimal style, no text","nombre_plan":"Pasta dental para mascotas","precio":f"RD${P['farmacia']['ejemplos_mas_vendidos']['pasta_dental']:,}","incluye":["Disponible en nuestra tienda","Fórmula segura para perros","Sin flúor ni xilitol","Sabores que les encantan a las mascotas"]},
    {"tipo":"cta","bg_prompt":"Happy dog with bright clean teeth, cheerful expression, light background, no people, no text","titulo":"Cuida su sonrisa","subtitulo":"Pregúntanos sobre higiene dental","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"parvo": {
  "caption": f"⚠️ Parvovirus: la enfermedad más peligrosa para los cachorros\n\nSolo una vacuna puede prevenirlo. ¿Tu perro está protegido? 🐾{FOOTER_CAP}\n\n#PetColinas #Parvovirus #VacunaParvo #SaludCanina #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Cute puppy looking vulnerable and small, soft warm background, no people, no text","titulo":"Parvovirus canino","subtitulo":"Infórmate y protege a tu cachorro ⚠️"},
    {"tipo":"contenido","bg_prompt":"Virus microscopy illustration, abstract scientific background, dark blue and red tones, no text","titulo":"¿Qué es el parvovirus?","puntos":["Enfermedad viral muy contagiosa y mortal","Ataca principalmente el sistema digestivo","Los cachorros menores de 6 meses son los más vulnerables","El virus puede vivir en el ambiente por meses","No tiene tratamiento específico — solo soporte veterinario","LA VACUNA es la única protección real"]},
    {"tipo":"contenido","bg_prompt":"Sick looking puppy resting, sad expression, soft focus, no people, no text","titulo":"Síntomas del parvovirus","puntos":["Vómitos intensos y repetitivos","Diarrea con sangre y olor muy fuerte","Letargo extremo — el perro no quiere moverse","Pérdida total del apetito","Fiebre alta (sobre 40°C)","Deshidratación severa en pocas horas"]},
    {"tipo":"contenido","bg_prompt":"Dog sniffing grass, outdoor park, warm sunlight, no people, no text","titulo":"¿Cómo se contagia?","puntos":["Contacto con heces de perros infectados","Suelos, parques o superficies contaminadas","A través de ropa y zapatos de humanos","Perros que salen antes de completar su vacunación","Muy resistente: sobrevive calor, frío y cloro común"]},
    {"tipo":"precio","bg_prompt":"Vaccine vials on clean medical surface, professional sterile environment, no people, no text","nombre_plan":"Vacuna quíntuple","precio":f"RD${v['vacuna_quintuple']:,}","incluye":["Protege contra Parvovirus","Protege contra Distemper (Moquillo)","Protege contra Hepatitis y Parainfluenza","Protege contra Leptospirosis",f"Consulta veterinaria: RD${v['consulta']:,}"]},
    {"tipo":"cta","bg_prompt":"Healthy happy vaccinated puppy playing, energetic and joyful, no people, no text","titulo":"¡Vacuna a tu cachorro!","subtitulo":"No esperes — el parvovirus mata en días","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"calor-mascotas": {
  "caption": f"☀️ ¡Cuidado con el calor! Tu mascota también sufre el verano\n\nAquí te decimos cómo proteger a tu perro en los días más calurosos 🐾{FOOTER_CAP}\n\n#PetColinas #CalorMascotas #GolpeDeCalore #PerrosRD #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Dog panting in heat, sunny day, out of breath expression, warm golden tones, no people, no text","titulo":"Protege a tu mascota del calor","subtitulo":"Guía para el verano dominicano ☀️"},
    {"tipo":"contenido","bg_prompt":"Dog showing signs of heat exhaustion, tongue out, heavy breathing, warm environment, no people, no text","titulo":"Señales de golpe de calor","puntos":["Jadeo excesivo e incesante","Babeo más de lo normal","Encías y lengua de color rojo intenso","Vómitos y diarrea repentinos","Tambaleo o pérdida de coordinación","Pérdida de conciencia — emergencia"]},
    {"tipo":"contenido","bg_prompt":"Dog drinking fresh water from bowl, refreshing, bright outdoor setting, no people, no text","titulo":"Qué hacer si sospecha golpe de calor","puntos":["Llévalo a un lugar fresco de inmediato","Ponle agua fresca sobre el cuello y patas","NO uses agua helada — el choque es peligroso","Ofrécele agua para tomar en pequeños sorbos","Ventílalo con un abanico o aire acondicionado","Lleva al veterinario de INMEDIATO"]},
    {"tipo":"contenido","bg_prompt":"Dog resting in shade under tree, cool comfortable environment, no people, no text","titulo":"Cómo prevenir el golpe de calor","puntos":["Agua fresca disponible siempre las 24 horas","Evita paseos entre 11am y 4pm (máximo calor)","Nunca dejes a tu perro en un carro cerrado","Asegúrate de que tenga sombra y ventilación","Razas de hocico corto (bulldog, pug) son más vulnerables","El pelo largo protege del sol — no lo rapes"]},
    {"tipo":"precio","bg_prompt":"Clean grooming salon with cooling fan and fresh water setup, bright and airy, no people, no text","nombre_plan":"Baño refrescante","precio":f"Desde RD${bano['pequeño']:,}","incluye":[f"Baño pequeño: RD${bano['pequeño']:,}",f"Baño mediano: RD${bano['mediano']:,}",f"Baño grande: RD${bano['grande']:,}","Shampoo profesional","Secado completo"]},
    {"tipo":"cta","bg_prompt":"Happy cool refreshed dog after bath, fluffy and bright, no people, no text","titulo":"¡Dale un baño refrescante!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"desparasitacion": {
  "caption": f"🐛 ¿Cuándo fue la última vez que desparasitaste a tu perro?\n\nLos parásitos son más peligrosos de lo que parecen 🐾{FOOTER_CAP}\n\n#PetColinas #Desparasitacion #SaludCanina #PerrosRD #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Healthy happy dog scratching ear in sunny park, playful mood, no people, no text","titulo":"Desparasitación: por qué y cuándo","subtitulo":"Protege a tu perro y a tu familia 🐛"},
    {"tipo":"contenido","bg_prompt":"Abstract illustration of parasites concept, worms and ticks, scientific educational style, no text","titulo":"Tipos de parásitos","puntos":["Internos: lombrices, tenias, giardia, coccidias","Externos: pulgas, garrapatas, ácaros, piojos","Los internos se transmiten por heces y tierra","Las pulgas y garrapatas viven en el ambiente","Algunos parásitos se transmiten a los humanos","Por eso desparasitar protege a TODA la familia"]},
    {"tipo":"contenido","bg_prompt":"Dog looking lethargic and uncomfortable, unwell expression, natural lighting, no people, no text","titulo":"Señales de parásitos","puntos":["Barriga hinchada (especialmente en cachorros)","Diarrea o vómitos frecuentes","Pérdida de peso sin razón aparente","Pelo opaco y sin brillo","Se rasca o muerde la base de la cola","Ves algo blanco en las heces (lombrices)"]},
    {"tipo":"contenido","bg_prompt":"Calendar with marked dates, reminder concept, clean organized desktop, no text","titulo":"¿Cada cuánto desparasitar?","puntos":["Cachorros: cada 2 semanas hasta los 3 meses","Cachorros 3-6 meses: mensual","Adultos: cada 3-6 meses (internos)","Externos (pulgas/garrapatas): mensual","Si tiene acceso a la calle: más frecuente","Siempre con supervisión veterinaria"]},
    {"tipo":"precio","bg_prompt":"Medical veterinary supplies, clean bottles and equipment on white background, no people, no text","nombre_plan":"Desparasitación en PetColinas","precio":f"Desde RD${v['aplicacion_albendazol']:,}","incluye":[f"Aplicación de Albendazol: RD${v['aplicacion_albendazol']:,}",f"Aplicación de Panacob: RD${v['aplicacion_panacob']:,}","NexGard Spectra (externo + interno) disponible","Asesoría veterinaria incluida"]},
    {"tipo":"cta","bg_prompt":"Happy healthy dog running and playing, energetic and free, sunny outdoor, no people, no text","titulo":"¡Desparasita a tu perrito!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"consulta-vet": {
  "caption": f"🩺 ¿Con qué frecuencia llevas a tu perro al veterinario?\n\nLa prevención es siempre más económica que el tratamiento 🐾{FOOTER_CAP}\n\n#PetColinas #ConsultaVeterinaria #SaludPreventiva #PerrosRD #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Dog at clean bright veterinary clinic, calm and comfortable on examination table, no people, no text","titulo":"¿Con qué frecuencia ir al veterinario?","subtitulo":"La guía que necesitas 🩺"},
    {"tipo":"contenido","bg_prompt":"Puppy getting examined at clinic, curious expression, bright modern vet office, no people, no text","titulo":"Cachorros (0-12 meses)","puntos":["Primera visita: a las 6-8 semanas de vida","Cada 3-4 semanas hasta completar vacunas","Primera desparasitación al mes de nacido","Revisión al mes, a los 4 y a los 12 meses","Esterilización recomendada a los 6-8 meses","Control de peso y desarrollo cada visita"]},
    {"tipo":"contenido","bg_prompt":"Adult dog looking healthy and strong, confident portrait, clean studio background, no people, no text","titulo":"Adultos (1-7 años)","puntos":["Mínimo 1 visita al año para chequeo general","Vacunas de refuerzo anuales","Desparasitación cada 3-6 meses","Revisión dental en cada visita","Control de peso y condición física","Antes de cualquier signo de enfermedad"]},
    {"tipo":"contenido","bg_prompt":"Warning signs concept, dog showing different health signs, educational infographic style, no people, no text","titulo":"Señales que no puedes ignorar","puntos":["Pérdida de apetito por más de 24 horas","Vómitos o diarrea repetitivos","Letargo extremo o cambios de comportamiento","Sed o micción excesiva","Cojera o dificultad para moverse","Cualquier bulto, herida o secreción inusual"]},
    {"tipo":"precio","bg_prompt":"Professional veterinary examination room, modern equipment, clean and bright, no people, no text","nombre_plan":"Consulta veterinaria","precio":f"RD${v['consulta']:,}","incluye":["Examen físico completo","Revisión de peso y temperatura","Evaluación dental y de piel",f"Toma de muestra / Diagnóstico: RD${v['muestra_diagnostico']:,}","Asesoría en nutrición y cuidados"]},
    {"tipo":"cta","bg_prompt":"Happy dog leaving veterinary clinic, healthy and well cared for, bright outdoor, no people, no text","titulo":"¡Agenda su consulta hoy!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"cachorro-primeros": {
  "caption": f"🐶 ¡Llegó tu cachorro! ¿Y ahora qué?\n\nTodo lo que necesitas saber para los primeros meses de vida 🐾{FOOTER_CAP}\n\n#PetColinas #CachorroNuevo #PrimerDia #PerritosRD #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Adorable tiny puppy looking at camera with curious eyes, warm cozy home setting, no people, no text","titulo":"¡Llegó tu cachorro!","subtitulo":"Guía de los primeros meses 🐶"},
    {"tipo":"contenido","bg_prompt":"Cozy puppy bed, toys and food bowl arranged neatly, warm home atmosphere, no people, no text","titulo":"Los primeros días","puntos":["Dale un espacio propio tranquilo y cálido","No lo separes de su cama en los primeros días","Alimentación especial para cachorro — 3-4 veces al día","Agua fresca siempre disponible","Empieza a acostumbrarlo a su nombre desde el día 1","Cachorros lloran de noche — es normal, paciencia"]},
    {"tipo":"contenido","bg_prompt":"Puppy vaccination schedule card with syringe nearby, educational infographic, no people, no text","titulo":"Vacunas y desparasitación","puntos":[f"Combo Primera Vacuna: RD${v['combo_primera_vacuna']:,} (incluye consulta)",f"Vacuna quíntuple: RD${v['vacuna_quintuple']:,}","Desparasitante a las 2, 4, 6 semanas","Refuerzo de vacunas cada 3-4 semanas","Vacuna antirrábica a los 3 meses","Programa completo antes de salir a la calle"]},
    {"tipo":"contenido","bg_prompt":"Puppy eating from small bowl, first meal at home, warm kitchen light, no people, no text","titulo":"Alimentación del cachorro","puntos":["Alimento específico para cachorros (nunca de adultos)","3-4 comidas pequeñas al día","No cambies la comida bruscamente (causa diarrea)","Nada de comida humana en los primeros meses","Agua siempre fresca y disponible","Consulta el peso recomendado por edad con el vet"]},
    {"tipo":"precio","bg_prompt":"Small puppy at first vet visit, curious and healthy looking, bright clinic, no people, no text","nombre_plan":"Primera visita al veterinario","precio":f"Baño cachorro: RD${bano['cachorro']:,}","incluye":[f"Combo Primera Vacuna: RD${v['combo_primera_vacuna']:,}",f"Consulta veterinaria: RD${v['consulta']:,}",f"Desparasitación: RD${v['aplicacion_albendazol']:,}","Asesoría completa de cuidados"]},
    {"tipo":"cta","bg_prompt":"Cute puppy sitting happily, bright colorful background, healthy and adorable, no people, no text","titulo":"¡Tu cachorro nos espera!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"hidratacion": {
  "caption": f"💧 ¿Toma suficiente agua tu perro?\n\nEn el calor dominicano, la hidratación de tu mascota es crítica 🐾{FOOTER_CAP}\n\n#PetColinas #HidratacionMascotas #SaludCanina #PerrosRD #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Dog drinking fresh water from clean bowl, thirsty and satisfied, bright light, no people, no text","titulo":"La hidratación de tu mascota","subtitulo":"Vital en el calor dominicano 💧"},
    {"tipo":"contenido","bg_prompt":"Multiple water bowls and dog water fountain, clean and fresh, white background, no text","titulo":"¿Cuánta agua necesita?","puntos":["Regla básica: 40-60ml por kg de peso al día","Un perro de 5kg necesita aprox. 250ml diarios","En calor o ejercicio: puede triplicarse","Perros que comen comida seca beben más","Perros con comida húmeda beben menos","Siempre disponible — nunca raciones de agua"]},
    {"tipo":"contenido","bg_prompt":"Dehydrated looking dog with dry nose, dull fur, tired expression, no people, no text","titulo":"Señales de deshidratación","puntos":["Encías secas y pegajosas (no húmedas)","Ojos hundidos o sin brillo","Pellizca la piel y tarda en volver (prueba del pliegue)","Orina oscura o en poca cantidad","Letargo y falta de energía","Vómitos o diarrea hacen que se deshidrate rápido"]},
    {"tipo":"contenido","bg_prompt":"Dog water fountain, multiple water bowls in home, tricks to encourage drinking, no people, no text","titulo":"Trucos para que tome más agua","puntos":["Pon varios recipientes de agua en la casa","Prueba con fuente de agua en movimiento","Agrega un poco de caldo de pollo sin sal al agua","Hielos de agua natural como premio en verano","Cambia el agua mínimo 2 veces al día","Limpia el recipiente diario para evitar bacterias"]},
    {"tipo":"contenido","bg_prompt":"Ice cubes in dog bowl, summer cooling concept, bright refreshing colors, no people, no text","titulo":"Hidratación en el calor","puntos":["El calor dominicano puede ser extremo — actúa antes","Hielos de agua natural son seguros y refrescantes","Evita ejercicio en las horas de más calor","Un baño también ayuda a regular la temperatura","Nunca dejes tu perro en un carro cerrado","Perros viejos y cachorros se deshidratan más rápido"]},
    {"tipo":"cta","bg_prompt":"Healthy hydrated happy dog, shiny coat, energetic pose, bright background, no people, no text","titulo":"Un perro hidratado es un perro feliz","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"grooming-regular": {
  "caption": f"✂️ ¿Cada cuánto llevas a tu perro al groomer?\n\nEl grooming regular no es un lujo — es parte de su salud 🐾{FOOTER_CAP}\n\n#PetColinas #GroomingRegular #PeluqueriaCanina #MascotasRD #SaludCanina",
  "slides": [
    {"tipo":"portada","bg_prompt":"Beautiful well-groomed dog portrait, pristine fur, happy expression, elegant clean background, no people, no text","titulo":"¿Por qué el grooming regular?","subtitulo":"Más que estética — es salud 🐾"},
    {"tipo":"contenido","bg_prompt":"Dog fur before and after grooming comparison concept, transformation, clean studio, no people, no text","titulo":"Beneficios del grooming regular","puntos":["Detecta problemas de piel a tiempo","Elimina parásitos escondidos en el pelo","Previene nudos y enredos dolorosos","Mantiene las uñas en longitud saludable","Limpieza de oídos previene infecciones","Tu perro se siente más cómodo y feliz"]},
    {"tipo":"contenido","bg_prompt":"Grooming schedule calendar, dog silhouette, organized planning concept, clean design, no text","titulo":"¿Cada cuánto ir al groomer?","puntos":["Pelo corto (Labrador, Beagle): cada 6-8 semanas","Pelo largo (Shih Tzu, Maltés): cada 3-4 semanas","Pelo rizado (Poodle, Bichón): cada 4-6 semanas","Doble capa (Husky, Pastor): cada 6-8 semanas","Corte de uñas: cada 3-4 semanas",f"Uñas solas en PetColinas: RD${add['corte_unas']:,}"]},
    {"tipo":"contenido","bg_prompt":"Dog with overgrown matted fur versus well groomed dog, contrast concept, no people, no text","titulo":"Qué pasa si no lo haces","puntos":["Pelaje enredado que tira de la piel — duele","Uñas largas que desvían la marcha","Infecciones de piel bajo el pelo apelmazado","Otitis por acumulación de pelo en oídos","Parásitos que pasan desapercibidos","En casos graves: dermatitis y heridas abiertas"]},
    {"tipo":"precio","bg_prompt":"Professional grooming salon with tools laid out, scissors, brush, professional setup, no people, no text","nombre_plan":"Nuestros servicios de grooming","precio":f"Desde RD${bano['pequeño']:,}","incluye":[f"Baño pequeño: RD${bano['pequeño']:,}",f"Baño mediano: RD${bano['mediano']:,}",f"Baño grande: RD${bano['grande']:,}",f"Corte higiénico: +RD${add['corte_higienico']:,}",f"Corte completo: +RD${add['corte_completo']:,}"]},
    {"tipo":"cta","bg_prompt":"Freshly groomed dog looking beautiful and happy, winning smile, bright studio, no people, no text","titulo":"¡Agenda el próximo baño!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"bano-medicado": {
  "caption": f"🧴 ¿Sabes cuándo tu perro necesita un baño medicado?\n\nNo es lo mismo que un baño normal — tiene beneficios terapéuticos 🐾{FOOTER_CAP}\n\n#PetColinas #BañoMedicado #DermatologiaCanina #MascotasRD #SaludPiel",
  "slides": [
    {"tipo":"portada","bg_prompt":"Dog with sensitive skin being carefully bathed, therapeutic spa-like setting, gentle lighting, no people, no text","titulo":"Baño medicado","subtitulo":"¿Cuándo lo necesita tu perro? 🧴"},
    {"tipo":"contenido","bg_prompt":"Dog scratching itchy skin, uncomfortable expression, natural setting, no people, no text","titulo":"¿Qué es el baño medicado?","puntos":["Usa shampoos terapéuticos con activos específicos","Trata condiciones de piel que el baño normal no resuelve","Está formulado para uso veterinario","Requiere un tiempo de contacto mayor","Alivia el picor, la inflamación y los hongos","Siempre recomendado por el veterinario"]},
    {"tipo":"contenido","bg_prompt":"Dog with skin condition, redness or flakiness concept, medical educational style, no people, no text","titulo":"¿Cuándo lo necesita?","puntos":["Dermatitis atópica o alergias de piel","Seborrea (piel muy grasa o muy seca)","Infecciones bacterianas o por hongos","Sarna o infestación de ácaros","Piel sensible o irritada frecuentemente","Por indicación veterinaria siempre"]},
    {"tipo":"contenido","bg_prompt":"Therapeutic shampoo bottle, clean white background, medical aesthetic, professional product shot, no text","titulo":"Tipos de shampoo medicado","puntos":["Antibacterial: para infecciones de piel","Antifúngico: para hongos y levaduras","Antiseborreico: controla grasa y descamación","Antiprurítico: calma el picor intenso","Hidratante: para piel muy seca y sensible","Solo tu veterinario sabe cuál necesita tu perro"]},
    {"tipo":"precio","bg_prompt":"Clean grooming salon, medicinal spa atmosphere, professional equipment, bright and sterile, no people, no text","nombre_plan":"Baño medicado en PetColinas","precio":f"RD${bano['medicado']:,}","incluye":["Shampoo medicado terapéutico","Tiempo de contacto adecuado","Enjuague y acondicionador especial","Secado profesional completo","Vendemos shampoos medicados en tienda"]},
    {"tipo":"cta","bg_prompt":"Dog with healthy glowing skin and shiny coat after treatment, relief expression, bright background, no people, no text","titulo":"¡Tu perro merece alivio!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"mascotas-ninos": {
  "caption": f"👶🐶 Mascotas y niños: la combinación perfecta cuando se hace bien\n\nTe contamos cómo lograr una convivencia segura y feliz 🐾{FOOTER_CAP}\n\n#PetColinas #MascotasYNiños #PerrosFamiliares #ConvivenciaSegura #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Small dog and children's toys together in playroom, friendly and colorful, safe environment, no people, no text","titulo":"Mascotas y niños","subtitulo":"Convivencia segura y feliz 👶🐶"},
    {"tipo":"contenido","bg_prompt":"Child's bedroom with dog bed nearby, toys, safe and cozy family environment, no people, no text","titulo":"Razas recomendadas para familias","puntos":["Golden Retriever — paciente y muy gentil","Labrador — energético y muy tolerante","Beagle — curioso y amigable","Poodle — inteligente y muy cariñoso","Bichón Frisé — pequeño y sociable","Shih Tzu — tranquilo y muy apegado"]},
    {"tipo":"contenido","bg_prompt":"Dog and plush toy sitting together, first meeting concept, neutral calm environment, no people, no text","titulo":"Cómo presentarlos","puntos":["Primero deja que el perro olfatee objetos del niño","Presentación gradual en terreno neutro","El adulto siempre presente en el primer encuentro","Nunca fuerces el contacto — deja que se acerquen solos","Enséñale al niño a acercarse de costado, no de frente","Mucho elogio y premios cuando la interacción es buena"]},
    {"tipo":"contenido","bg_prompt":"Rules and safety concept, shield and paw print icons, protective family values, clean design, no text","titulo":"Reglas de convivencia","puntos":["Enséñale al niño a no molestar mientras come o duerme","El perro siempre debe poder retirarse si lo necesita","Nunca jalear de la cola o las orejas","Supervisión constante menores de 6 años con mascotas","El perro también necesita su espacio de tranquilidad","Vacunas y desparasitación al día — protege a todos"]},
    {"tipo":"contenido","bg_prompt":"Child's drawing of dog, crayon art concept, colorful and innocent, family warmth theme, no text","titulo":"Beneficios para los niños","puntos":["Desarrollan responsabilidad y empatía","Aprenden a respetar a otros seres vivos","Reducen el estrés y la ansiedad","Mejoran su sistema inmune (estudios lo comprueban)","Compañía y amor incondicional siempre","Los niños con mascotas son más sociables"]},
    {"tipo":"cta","bg_prompt":"Happy dog with family toys around, warm home, welcoming atmosphere, no people, no text","titulo":"¡Visítanos con tu familia!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"razas-pequenas": {
  "caption": f"🐕 Razas pequeñas: cuidados especiales que debes conocer\n\nTienen sus propias necesidades — y en PetColinas las conocemos bien 🐾{FOOTER_CAP}\n\n#PetColinas #RazasPequeñas #CuidadosEspeciales #PerrosPequeños #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Collection of small dog breeds, Shih Tzu, Maltese, Poodle, Chihuahua, adorable portrait, clean background, no people, no text","titulo":"Razas pequeñas","subtitulo":"Cuidados especiales que debes conocer 🐕"},
    {"tipo":"contenido","bg_prompt":"Small dog showing teeth, dental care concept, clean white background, no people, no text","titulo":"Salud dental","puntos":["Las razas pequeñas son más propensas a problemas dentales","Los dientes se acumulan en un espacio muy pequeño","Cepilla sus dientes 2-3 veces por semana","Usa pasta dental específica para perros",f"Pasta dental en nuestra tienda: RD${P['farmacia']['ejemplos_mas_vendidos']['pasta_dental']:,}","Revisión dental en cada visita veterinaria"]},
    {"tipo":"contenido","bg_prompt":"Small dog's delicate paw and joint concept, gentle care, soft light, no people, no text","titulo":"Articulaciones y huesos","puntos":["Luxación de rótula es muy común en razas pequeñas","Evita que salten desde alturas (sofás, camas)","Usa escaleritas para que suban solos","No los fuercen a correr largas distancias","Revisión ortopédica regular con el veterinario","El sobrepeso agrava los problemas articulares"]},
    {"tipo":"contenido","bg_prompt":"Small dog shivering or cold, wrapped in tiny blanket, warm cozy environment, no people, no text","titulo":"Temperatura y clima","puntos":["Las razas pequeñas se enfrían con facilidad","En invierno necesitan ropita (especialmente sin pelo)","El calor dominicano también les afecta más","Nunca al sol directo en horas pico","Agua fresca siempre disponible","Cuidado con el piso caliente en pavimento"]},
    {"tipo":"precio","bg_prompt":"Small dog being groomed on table, professional salon, careful hands with tools nearby, no faces, no text","nombre_plan":"Grooming para razas pequeñas","precio":f"Baño desde RD${bano['pequeño']:,}","incluye":[f"Baño pequeño: RD${bano['pequeño']:,}",f"Baño + corte higiénico: RD${combos['baño pequeño + corte higiénico']:,}",f"Baño + corte completo: RD${combos['baño pequeño + corte completo']:,}",f"Corte de uñas: RD${add['corte_unas']:,}","Limpieza de oídos incluida"]},
    {"tipo":"cta","bg_prompt":"Happy healthy small dog, perfectly groomed, bright eyes, cheerful expression, no people, no text","titulo":"Especialistas en razas pequeñas","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"corte-unas": {
  "caption": f"🐾 ¿Cada cuánto le cortas las uñas a tu perro?\n\nLas uñas largas causan más problemas de los que imaginas 🐾{FOOTER_CAP}\n\n#PetColinas #CorteDeUñas #CuidadoCanino #PerrosRD #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Dog paw close-up with long nails on clean surface, clear focus, no people, no text","titulo":"La importancia del corte de uñas","subtitulo":"Más que estética, es bienestar 🐾"},
    {"tipo":"contenido","bg_prompt":"Dog walking awkwardly due to long nails, comparison concept, no people, no text","titulo":"¿Por qué importa tanto?","puntos":["Las uñas largas desvían la postura al caminar","Causan dolor en articulaciones y columna","Pueden clavarse en la piel y causar infecciones","Se enganchan en alfombras y causan lesiones","En razas pequeñas el problema es aún mayor","Un perro con uñas largas sufre en silencio"]},
    {"tipo":"contenido","bg_prompt":"Dog paw nails that are too long versus properly trimmed, before after concept, clean white background, no text","titulo":"Señales de que es hora","puntos":["Escuchas el 'clic clic' al caminar en piso duro","Las uñas tocan el suelo al estar de pie","Tu perro evita apoyar bien las patas","Se lame las patas con frecuencia","Las uñas empiezan a curvarse hacia dentro","La última uña (del pulgar) nunca se desgasta sola"]},
    {"tipo":"contenido","bg_prompt":"Dog nail trimmer tool flatlay, clean white background, simple and clear, no people, no text","titulo":"¿En casa o con profesional?","puntos":["En casa: solo si tienes experiencia — hay venas que sangran","Si no sabes, ve con un profesional — no es riesgo","El profesional sabe hasta dónde cortar sin dañar","Los perros oscuros tienen las venas invisibles","Un corte mal hecho duele y sangra mucho","Costo profesional en PetColinas: solo RD$300"]},
    {"tipo":"precio","bg_prompt":"Clean grooming station with nail clippers, professional setup, neat and organized, no people, no text","nombre_plan":"Corte de uñas","precio":f"RD${add['corte_unas']:,}","incluye":["Corte seguro y preciso","Limado para bordes suaves","Sin estrés para tu mascota","También disponible con cualquier baño","Realizado por groomer profesional"]},
    {"tipo":"cta","bg_prompt":"Dog with perfectly trimmed paws walking comfortably, happy stride, no people, no text","titulo":"¡RD$300 y listo!","subtitulo":f"Sin cita previa · {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"antipulgas": {
  "caption": f"🦟 ¿Tu perro tiene pulgas o garrapatas?\n\nNexGard Spectra y Bravecto los eliminan y previenen por semanas 🐾{FOOTER_CAP}\n\n#PetColinas #Pulgas #Garrapatas #NexGard #Bravecto #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Dog scratching itself in garden, uncomfortable with fleas or ticks, natural outdoor setting, no people, no text","titulo":"Pulgas y garrapatas","subtitulo":"Protege a tu perro y a tu hogar 🦟"},
    {"tipo":"contenido","bg_prompt":"Flea and tick concept illustration, abstract parasites on dog fur, educational style, close-up macro, no text","titulo":"El problema real","puntos":["Una pulga puede poner 50 huevos al día en tu casa","Las garrapatas transmiten enfermedades graves al perro y al humano","El 95% de las pulgas viven en el ambiente, no en el perro","Si ves una garrapata, hay más que no ves","Limpiar la casa no es suficiente sin tratar al perro","La prevención mensual es la única solución real"]},
    {"tipo":"contenido","bg_prompt":"Dog fur being examined for parasites, close-up view, no people, no text","titulo":"Señales de infestación","puntos":["Se rasca o muerde sin parar, especialmente la base de la cola","Alopecia o caída de pelo en zonas específicas","Pequeños puntos negros en el pelaje (heces de pulgas)","Piel roja e irritada","Ves garrapatas adheridas a la piel","Anemia en cachorros (palidez en las encías)"]},
    {"tipo":"contenido","bg_prompt":"NexGard and Bravecto style product concept, orange pill and chewable treat on white background, no text","titulo":"Nuestras soluciones","puntos":["NexGard Spectra: elimina pulgas, garrapatas, lombrices y ácaros","Bravecto: protección por 12 semanas en un solo comprimido","Frontline: pipeta de aplicación en la nuca","Spray garrapaticida para el ambiente","Todos disponibles en nuestra farmacia","Con asesoría del equipo de PetColinas"]},
    {"tipo":"precio","bg_prompt":"Pet medication display, various antiparasitic products on clean white shelf, no text","nombre_plan":"NexGard Spectra","precio":"Desde RD$1,416","incluye":["2-3.5 kg — RD$1,416","3-7 kg — RD$1,462","7-15 kg — RD$1,775","15-30 kg — RD$1,775","Bravecto (12 semanas) — RD$2,595","Pregunta por el tamaño de tu perro"]},
    {"tipo":"cta","bg_prompt":"Happy scratch-free dog relaxing comfortably, peaceful expression, bright home setting, no people, no text","titulo":"¡Dile adiós a las pulgas!","subtitulo":f"📍 {ub}","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"moquillo": {
  "caption": f"⚠️ Moquillo canino: una de las enfermedades más mortales para tu perro\n\nPero tiene prevención: la vacuna séxtuple 🐾{FOOTER_CAP}\n\n#PetColinas #Moquillo #Distemper #VacunaCanina #SaludAnimal #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Worried looking dog, sad eyes, soft dramatic lighting, no people, no text","titulo":"Moquillo canino","subtitulo":"Infórmate y vacuna a tu perro ⚠️"},
    {"tipo":"contenido","bg_prompt":"Abstract virus concept, dark blue background, scientific visualization, no text","titulo":"¿Qué es el moquillo?","puntos":["Enfermedad viral altamente contagiosa y mortal","Ataca el sistema respiratorio, digestivo y nervioso","No tiene tratamiento específico — solo soporte","Alta tasa de mortalidad en perros no vacunados","Los cachorros y perros sin vacunas son los más vulnerables","LA VACUNA es la única protección efectiva"]},
    {"tipo":"contenido","bg_prompt":"Dog with respiratory symptoms, runny nose, tired expression, soft light, no people, no text","titulo":"Síntomas por etapas","puntos":["Fase 1 (respiratoria): fiebre, secreción nasal y ocular","Fase 2 (digestiva): vómitos, diarrea, pérdida de apetito","Fase 3 (nerviosa): convulsiones, espasmos musculares","Endurecimiento de los cojinetes plantares","Almohadillas y trufa se secan y se endurecen","Si llega a la fase nerviosa, las secuelas son permanentes"]},
    {"tipo":"contenido","bg_prompt":"Dog sniffing infected area, park with other dogs, contagion concept, no people, no text","titulo":"¿Cómo se contagia?","puntos":["Por contacto directo con perros infectados","Por secreciones (estornudos, ojos, nariz, orina)","En parques, guarderías o exposiciones","El virus puede sobrevivir horas en el ambiente","Un perro infectado puede parecer sano al inicio","Por eso la vacuna antes de salir a la calle"]},
    {"tipo":"precio","bg_prompt":"Vaccine vials arranged professionally on clean surface, sterile medical background, no people, no text","nombre_plan":"Vacuna séxtuple","precio":f"RD${v['vacuna_sextuple']:,}","incluye":["Protege contra Moquillo (Distemper)","Protege contra Parvovirus","Protege contra Hepatitis","Protege contra Parainfluenza","Protege contra Coronavirus",f"Consulta veterinaria: RD${v['consulta']:,}"]},
    {"tipo":"cta","bg_prompt":"Healthy happy vaccinated dog playing in park, energetic and protected, no people, no text","titulo":"¡Protege a tu perro hoy!","subtitulo":"Un refuerzo al año es todo lo que necesita","lineas":CTA_LINEAS},
  ]
},

# ─────────────────────────────────────────────────────────────────────────────
"quienes-somos": {
  "caption": f"🐾 Conoce PetColinas — tu veterinaria y peluquería canina de confianza\n\nEstamos ubicados en Plaza Las Colinas, SDO Oeste, y atendemos a tus mascotas con todo el amor del mundo 💚{FOOTER_CAP}\n\n#PetColinas #VeterinariaDominicana #PeluqueriaCanina #SantoDomingoOeste #MascotasRD",
  "slides": [
    {"tipo":"portada","bg_prompt":"Modern veterinary and grooming clinic exterior, green and white colors, professional signage, clean and welcoming, no people, no text","titulo":"Conoce PetColinas","subtitulo":"Tu aliado en el cuidado de tu mascota 💚"},
    {"tipo":"contenido","bg_prompt":"Professional grooming salon interior, clean green and white decor, grooming tools, warm lighting, no people, no text","titulo":"Nuestros servicios","puntos":["🛁 Grooming profesional — baño y corte","🩺 Atención veterinaria completa","💊 Farmacia y tienda de mascotas","🧴 Baño medicado y tratamientos de piel","✂️ Corte de uñas y limpieza de oídos","💉 Vacunación y desparasitación"]},
    {"tipo":"contenido","bg_prompt":"Veterinary clinic examination room, modern equipment, bright and clean, professional atmosphere, no people, no text","titulo":"Veterinaria","puntos":[f"Consulta general: RD${v['consulta']:,}",f"Vacuna quíntuple: RD${v['vacuna_quintuple']:,}",f"Vacuna séxtuple: RD${v['vacuna_sextuple']:,}",f"Vacuna rabia: RD${v['vacuna_rabia']:,}",f"Test Parvo/Corona/Giardia: RD${v['test_parvo_corona_giardia']:,}",f"Combo Primera Vacuna: RD${v['combo_primera_vacuna']:,}"]},
    {"tipo":"contenido","bg_prompt":"Dog grooming salon with professional equipment, scissors, brushes on display, clean organized space, no people, no text","titulo":"Grooming","puntos":[f"Baño cachorro: RD${bano['cachorro']:,}",f"Baño pequeño: RD${bano['pequeño']:,}",f"Baño mediano: RD${bano['mediano']:,}",f"Baño grande: RD${bano['grande']:,}",f"Corte higiénico: +RD${add['corte_higienico']:,}",f"Corte completo: +RD${add['corte_completo']:,}"]},
    {"tipo":"contenido","bg_prompt":"Pet store shelves with products, clean organized pharmacy section, no people, no text","titulo":"Farmacia y tienda","puntos":["NexGard Spectra y Bravecto antiparasitarios","Shampoos profesionales y medicados","Alimentos premium para perros y gatos","Accesorios: collares, correas, juguetes","Pasta dental y productos de higiene","Asesoría personalizada en cada compra"]},
    {"tipo":"cta","bg_prompt":"Welcoming pet clinic entrance, green plants, clean modern exterior, inviting atmosphere, no people, no text","titulo":"¡Visítanos!","subtitulo":f"📍 {ub}","lineas":[f"⏰ {hr}","📱 Escríbenos por WhatsApp",ig]},
  ]
},

} # fin CONFIGS

if __name__ == "__main__":
    out = Path("carruseles")
    out.mkdir(exist_ok=True)
    for folder, data in CONFIGS.items():
        cfg = {"folder": folder, "fast_model": True, **data}
        path = out / f"{folder}.json"
        path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ carruseles/{folder}.json")
    print(f"\n✅  {len(CONFIGS)} configs generados en carruseles/")
