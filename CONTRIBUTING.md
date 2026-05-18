# Cómo contribuir a alpine-cabin

Gracias por considerar contribuir a este proyecto. Este es un repositorio de **diseño constructivo open source** — no es solo código sino también planos, cálculos, BOM, presupuesto y guías. Lo que aprendamos colectivamente queda en el dominio público bajo CC-BY-SA-4.0.

## Tipos de contribuciones bienvenidas

| Tipo | Cómo |
|---|---|
| **Revisión de ingeniería** — encontraste un error en el BOM, una asunción dudosa en el SPEC, una cantidad mal calculada | Abre un issue con la etiqueta `engineering` describiendo el error + cómo deberías hacerse. PRs con corrección + justificación bienvenidos. |
| **Build log** — replicaste esta cabaña (o algo parecido) en otro sitio | Issue con etiqueta `build-log` + fotos + lo que cambió respecto al diseño base. Te ayudamos a mergeear el log a `docs/builds/<tu-build>.md`. |
| **Datos de costo local** — cuánto cuesta el acero en tu país, qué proveedores conoces | Issue con etiqueta `pricing`. Datos georeferenciados ayudan a quien construya cerca de ti. |
| **Sustituciones de materiales** — en tu clima funciona X mejor que Y | Issue con etiqueta `materials` + justificación + fuente. |
| **Mejoras al digital twin** — bugs en el HTML, ideas para el viewer, mejoras al pipeline build123d | PR directo o issue. Etiqueta `digital-twin`. |
| **Traducciones** — el repo está en español; portugués, francés, otros idiomas son bienvenidos | Issue con etiqueta `i18n` indicando el idioma. |
| **Documentación** — un párrafo confuso, un diagrama que ayudaría | PR directo a la rama `main` con la mejora. |

## Cómo abrir un issue

1. Busca primero si ya existe un issue parecido.
2. Usa la plantilla apropiada (`.github/ISSUE_TEMPLATE/`).
3. Sé específico: cita archivos y números de línea (`SPEC.md:42`), cantidades, precios.
4. Si reportas un riesgo estructural: marca con `risk:high` y explica el escenario de falla.

## Cómo abrir un Pull Request

1. Fork → branch (`feature/lo-que-haces` o `fix/lo-que-arreglas`).
2. **Si tu PR cambia cantidades del BOM**: actualiza `cad/params.toml` (la fuente de verdad), no el `BOM.md` directamente — `BOM.md` se regenera con `make bom`.
3. **Si cambias el modelo CAD**: corre `make all` localmente para regenerar STEP/STL/GLB.
4. **Si tu cambio afecta el HTML interactivo**: corre `python cad/dogfood.py` para validar que no rompió nada.
5. Commit con mensaje [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, etc.
6. Abre el PR contra `main`. Usa la plantilla (`.github/PULL_REQUEST_TEMPLATE.md`).
7. Espera CI (Pages build se valida). Responde a comentarios.
8. Merge requiere al menos 1 aprobación (auto-merge cuando aplique).

## Cómo correr localmente

```bash
git clone https://github.com/broomva/alpine-cabin.git
cd alpine-cabin
make setup       # venv + build123d + jinja2
make all         # regenera BOM + CAD + datos web
make serve       # http://localhost:8765
make dogfood     # opcional — Playwright smoke test del HTML
```

Requisitos:
- **Python 3.12** (build123d aún no tiene wheels para 3.13+)
- **Make** (para `make all` y demás targets)
- Para `dogfood`: `python -m playwright install chromium` (~150 MB)

## Estilo de código

- **Python**: PEP 8, type hints donde ayuden a la claridad, `from __future__ import annotations` en archivos nuevos.
- **JavaScript (web/)**: ES modules, sin frameworks, vanilla. Funciones pequeñas, comentarios sobre el *por qué* no el *qué*.
- **Markdown**: oraciones cortas, tablas para datos densos, sin HTML inline salvo necesidad.
- **TOML**: comentarios en español para `params.toml` y `prices.toml` (orientado a constructores hispanohablantes).

## Disciplina bstack

Este repo sigue las [primitivas bstack](https://github.com/broomva/bstack). Lo más relevante para contribuyentes externos:

- **P3 Tickets** — work no trivial vive en un issue antes de PR
- **P14 Dep-Chain** — PRs que tocan múltiples archivos enumeran *qué* depende de *qué*
- **P18 Audience** — markdown para repo, HTML para humanos consumidores finales
- **P20 Cross-Review** — PRs sustantivos pasan revisión cruzada (no auto-merge sin review)

Ver `AGENTS.md` para el contrato completo (relevante si automatizas con agentes IA).

## Aviso de seguridad estructural

Esta es **información de referencia, no un proyecto estructural firmado**. Si encontrás un error que pueda llevar a fallas estructurales en una obra real, **abre un issue con etiqueta `risk:high` inmediatamente** y, si construirías, contrata un ingeniero matriculado que revise antes de proceder. Ver `SECURITY.md`.

## Código de conducta

Este proyecto se rige por el [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Trato respetuoso. Reportes a carlos@broomva.tech.

## Licencia

Tus contribuciones quedan bajo CC-BY-SA-4.0 (igual que el resto del repo). Al abrir un PR confirmas que tienes derecho a contribuir el contenido bajo esa licencia.

## Preguntas

Abre una *Discussion* (cuando esté habilitada) o un issue con etiqueta `question`.

¡Gracias por hacer este proyecto más útil para todos!
