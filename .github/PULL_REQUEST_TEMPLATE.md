<!-- Gracias por contribuir. Por favor llena lo siguiente. -->

## Resumen

<!-- 1-3 oraciones: qué cambia y por qué -->

## Tipo de cambio

- [ ] 🐛 Bug fix (corrección no rompe nada existente)
- [ ] ✨ Feature (funcionalidad nueva, sin breaking changes)
- [ ] ♻ Refactor (no cambia comportamiento)
- [ ] 📝 Documentación
- [ ] 🏗 Cambio al diseño constructivo (SPEC, BOM, params, perfiles)
- [ ] 🤖 Digital twin (HTML, CAD pipeline, plantillas)
- [ ] 🔒 Seguridad / governance
- [ ] 💥 Breaking change (requiere ajuste en consumidores)

## Validación

- [ ] Corrí `make all` localmente (regeneré BOM + CAD + datos web).
- [ ] Si tocó el HTML: corrí `python cad/dogfood.py` sin errores.
- [ ] Si tocó cantidades del BOM: actualicé `cad/params.toml` (no el `BOM.md` directamente).
- [ ] Si tocó precios: actualicé `cad/prices.toml`.
- [ ] El commit message sigue [Conventional Commits](https://www.conventionalcommits.org/).
- [ ] Actualicé `CHANGELOG.md` bajo `[Unreleased]` si aplica.

## Dep-chain (P14)

<!-- Si tu cambio toca múltiples archivos, lista upstream/downstream concreto.
     Ejemplo:
     Upstream: cad/params.toml (apex_height_m: 6.2 → 6.5)
     Downstream:
       - cad/cabin.py:38 (rafter angle se recalcula)
       - templates/BOM.md.j2 (longitudes de pares cambian)
       - web/data/cabin.glb (regenerado)
       - assets/renders/* (regenerados)
-->

## Cambios estructurales

<!-- ¿Tu cambio puede afectar la integridad estructural? Si SÍ:
     - ¿Pasaste por un ingeniero estructural?
     - ¿Citaste norma (NSR-10, ASCE, etc.)?
     Si no aplica, dejá: "no afecta integridad estructural"
-->

## Capturas / evidencia

<!-- Para cambios visuales o renders: pegá un screenshot o link al render.
     Para cambios en KPIs: pegá la salida de `make kpis` antes y después.
-->

## Referencias

<!-- Issues que cierra, PRs relacionados, link a discusión externa -->

Closes #
