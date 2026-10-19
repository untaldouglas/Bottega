# Resumen ejecutivo — Bottega

**Qué es:** un método gobernado de desarrollo de software asistido por IA, apoyado en un grupo de Bots especializados que trabajan por etapas, bajo aprobación humana y con evidencia verificable en cada paso.

**Propósito de este documento:** dar contexto suficiente para que una coordinación de desarrollo evalúe, en minutos, si le interesa participar en una prueba de concepto (PoC) controlada y medida.

---

## 1. El problema

Los equipos de desarrollo acumulan solicitudes pequeñas y oportunidades de mejora que no siempre justifican un proyecto formal. Sin un flujo claro, eso produce:

- requisitos ambiguos que se descubren tarde;
- retrabajo por decisiones no registradas;
- documentación incompleta o desactualizada;
- dificultad para explicar *por qué* se tomó cada decisión;
- poco tiempo del equipo para lo que realmente aporta valor.

## 2. La propuesta

Bottega no "automatiza el desarrollo". **Asiste el proceso** con roles especializados y un flujo con puertas de revisión, de modo que la persona siga conduciendo y decidiendo.

La promesa es de **método, no de magia**:

| Sin Bottega | Con Bottega |
|---|---|
| Requisitos en correos o conversaciones | Requisitos escritos, con criterios observables |
| Diseño implícito | Alternativas evaluadas y decisión registrada |
| Código sin contrato | Arquitectura y estrategia de pruebas antes de implementar |
| "Funciona en mi máquina" | Evidencia reproducible (comandos y resultados reales) |
| Revisión informal | Revisión independiente con `PASS` / `NEEDS_WORK` / `BLOCKED` |
| Historia que se pierde | Trazabilidad por SHA y manifiesto de evidencia |

## 3. Cómo funciona

Seis roles especializados, uno por etapa, nunca mezclados:

```text
1. Andrea del Verrocchio   → requisitos y criterios de aceptación
2. Leonardo da Vinci       → alternativas y plan de solución
3. Donatello (UX)          → experiencia de usuario y diseño
4. Filippo Brunelleschi    → arquitectura y estrategia de pruebas
5. Michelangelo Buonarroti → implementación con TDD y evidencia
6. Raffaello Sanzio        → revisión independiente (no aprueba su propio trabajo)
```

Cada etapa termina en un **gate** que solo una persona autoriza. El producto no avanza a la siguiente etapa hasta que la anterior queda aprobada. La implementación se autoriza únicamente después de aprobar requisitos, UX y arquitectura.

## 4. Qué está demostrado hoy — y qué no

Hoy existe **un caso demostrativo** (Idea Prioritizer, `PRODUCTO-001`), construido con el método, con datos sintéticos, sin producción:

- validación técnica independiente: `PASS`;
- fidelidad UX: `PASS`;
- revisión de aceptación por agente: 14/14 comprobaciones;
- evidencia reproducible y trazable por hash.

**Lo que eso NO demuestra:**

- que el beneficio se repita en otro dominio o equipo;
- ahorro de tiempo, costo o productividad institucional;
- satisfacción o aceptación de personas usuarias (`USER_ACCEPTANCE=PENDING`);
- que esté listo para producción, release o publicación.

En otras palabras: **la factibilidad técnica está demostrada; el beneficio organizacional es todavía una hipótesis.** Eso es, precisamente, lo que la PoC busca medir.

## 5. La oportunidad: una PoC controlada y medida

Proponemos comparar, durante seis semanas, dos trabajos pequeños y comparables:

- **Caso A** — desarrollado con Bottega (gates, evidencia, revisión independiente).
- **Caso B** — desarrollado con el proceso habitual del equipo.

Ambos sobre un problema de baja criticidad, reversible, con datos sintéticos, en repositorio privado, **sin producción, sin integraciones institucionales y sin datos reales**.

### Qué se mediría (descriptivo, no ROI)

- tiempo de ciclo y horas humanas registradas;
- retrabajo por etapa;
- defectos encontrados por gate y defectos escapados;
- cobertura de criterios con prueba y evidencia;
- completitud de documentación;
- incidentes de privacidad/seguridad (objetivo: cero);
- aceptación humana del resultado y percepción del equipo.

Los resultados se presentarían con denominadores, reintentos y limitaciones declaradas. No se haría inferencia causal fuerte ni se afirmaría retorno de inversión con dos casos.

## 6. Límites y no-claims

Bottega **no** se presenta como:

- "completamente autónomo";
- "sin errores";
- "reemplaza al equipo";
- "listo para mercado";
- con ROI o impacto institucional ya demostrado.

La IA asiste; las personas definen alcance, revisan y deciden. Un `PASS` técnico no es aceptación humana, ni autorización de release o publicación.

## 7. Decisión solicitada

Evaluar la propuesta y, si hay interés, designar un caso candidato y un responsable para una PoC de seis semanas. La decisión de adoptar, adaptar o detener Bottega se tomaría **al final**, con evidencia sobre la mesa.

> Participar en una PoC no compromete a adoptar la herramienta, no autoriza producción ni publicación, y no implica costo de herramientas.
