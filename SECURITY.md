# Política de Seguridad

Este es un proyecto open source de **diseño constructivo**, no un producto de software únicamente. Por tanto, hay dos clases distintas de problemas de seguridad:

## A. Riesgo estructural en el diseño físico

Si encontrás un error en `SPEC.md`, `BOM.md`, `cad/params.toml`, o cualquier documento técnico que **podría llevar a una falla estructural** si alguien construyera siguiendo el repo tal como está, repórtalo así:

### Reporte rápido (riesgo alto)

1. **Abre un issue inmediatamente** con la etiqueta `risk:high` (no esperes a tener todos los detalles).
2. Cita exactamente: archivo + líneas + qué crees que está mal + por qué.
3. Si conocés la solución, propónela. Si no, decilo.
4. Cualquier persona con permisos cerrará el issue cuando se aplique la corrección.

### Reporte privado (si involucra a un usuario actual)

Si sabés que alguien YA está construyendo siguiendo el repo y querés alertarlos antes de hacer pública la corrección, envia un correo a **carlos@broomva.tech** con asunto `[alpine-cabin SECURITY]` y los detalles. Se publicará la corrección coordinada cuando los usuarios afectados estén notificados.

### Aviso explícito

El repo lleva en su `LICENSE` y `README.md` el siguiente disclaimer:

> Nada en este repositorio sustituye planos firmados por un ingeniero matriculado, un estudio geotécnico ni una licencia de construcción que cumpla la normativa local. Quien construya a partir de estos documentos lo hace bajo su propio riesgo.

Por tanto, **mantener actualizado y veraz el contenido es responsabilidad colectiva**. Si lo construís, contratá un ingeniero matriculado que revise.

## B. Vulnerabilidades de software (digital twin, scripts, HTML)

El digital twin (`cad/`, `web/`) usa Python + JavaScript + dependencias open source. Si encontrás:

* Una vulnerabilidad en una dependencia que usamos (`build123d`, `playwright`, Three.js, etc.)
* Un XSS, una inyección, una mala validación de entrada en `cad/apply_experiment.py`, `web/js/state.js`, etc.
* Un secreto accidentalmente commiteado

Reportá por **correo privado a carlos@broomva.tech** con asunto `[alpine-cabin SECURITY]`. NO abras un issue público.

Responderemos en menos de 7 días con (a) confirmación de recepción, (b) plan de mitigación o explicación de por qué no es vulnerabilidad, (c) ETA si aplica.

### Lo que NO calificamos como vulnerabilidad

* Que el HTML lea params.json desde el repo (es público, ese es el diseño).
* Que el `apply_experiment.py` necesite confirmación humana antes de escribir — esa es una feature de seguridad, no un bug.
* CVEs en dependencias que NO usamos en producción (solo desarrollo) y que no afectan el código publicado.

## Versiones soportadas

Como proyecto pre-release (v0.x), solo la rama `main` recibe correcciones. No mantenemos ramas LTS.

## Disclosures previas

Ninguna a la fecha de creación de este documento. Cuando ocurran, se listarán aquí con fecha + naturaleza + commit de corrección + reportante (con consentimiento).
