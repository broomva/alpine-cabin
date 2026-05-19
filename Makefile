# Makefile — orquestación del digital twin
# Uso: make all (regenera todo desde params.toml)

PYTHON := .venv/bin/python
PIP    := .venv/bin/pip

.PHONY: help all setup bom cad web kpis serve validate render dogfood clean

help:
	@echo "Targets disponibles:"
	@echo "  make setup     Crear venv + instalar build123d + jinja2"
	@echo "  make all       Regenerar BOM + CAD + datos web desde params.toml"
	@echo "  make bom       Regenerar solo BOM.md"
	@echo "  make cad       Regenerar solo cad/exports/{cabin.step,cabin.stl} + web/data/cabin.glb"
	@echo "  make web       Regenerar solo web/data/{params,prices,kpis}.json"
	@echo "  make kpis      Imprimir KPIs en consola"
	@echo "  make validate  Validar GLB vs params.toml (regression test)"
	@echo "  make render    Generar 4 vistas PNG en assets/renders/ (requiere playwright)"
	@echo "  make dogfood   Playwright recorre 7 tabs + captura screenshots"
	@echo "  make serve     Servir web/ en http://localhost:8765"
	@echo "  make clean     Limpiar cad/exports/ y web/data/cabin.glb"

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install build123d jinja2 rich

all: bom budget cad web

bom:
	$(PYTHON) cad/bom_generator.py

budget:
	$(PYTHON) cad/budget_generator.py

cad:
	$(PYTHON) cad/cabin.py

web:
	$(PYTHON) cad/export_web_data.py

kpis:
	$(PYTHON) cad/kpis.py

validate:
	$(PYTHON) cad/validate_cad.py

render:
	$(PYTHON) cad/render_views.py

dogfood:
	$(PYTHON) cad/dogfood.py

serve:
	cd web && python3 -m http.server 8765

clean:
	rm -rf cad/exports/*.step cad/exports/*.stl
	rm -f web/data/cabin.glb
