// cabin-builder.js — Construye la cabaña procedural en Three.js a partir de
// los params (espejo en JS de cad/cabin.py + cad/envelope.py). Permite
// rebuilds en realtime: los sliders actualizan la geometría sin recargar GLB.
//
// Coordenadas: Three.js Y-up.
//   X = ancho frontal (0 → widthM)
//   Y = vertical (0 = nivel terreno bajo el extremo más bajo, sube hasta apex)
//   Z = profundidad (0 = frente con deck, -depthM = trasero con muro)
//
// build123d coord en cad/cabin.py:
//   X = ancho frontal, Y = profundidad (0=frente, +depthM=trasero), Z = vertical
//   → Three.js: (x, z, -y).
//
// La matriz heights_m[row][col] tiene row=0 en build123d y=0 (frente) y
// row=last en y=depthM (trasero). Las columnas se alinean para que su TOPE
// quede en platform_y = max(heights); su base sube cuando son más cortas.

import * as THREE from "three";

const MATERIALS = {
  steel:     () => new THREE.MeshStandardMaterial({ color: 0x4a4d57, metalness: 0.78, roughness: 0.32 }),
  platform:  () => new THREE.MeshStandardMaterial({ color: 0x2a2c33, metalness: 0.55, roughness: 0.55 }),
  roof:      () => new THREE.MeshStandardMaterial({ color: 0x161616, metalness: 0.62, roughness: 0.42, side: THREE.DoubleSide }),
  glass:     () => new THREE.MeshPhysicalMaterial({
    color: 0x88aaff, metalness: 0.0, roughness: 0.05,
    transmission: 0.85, transparent: true, opacity: 0.35,
    ior: 1.5, thickness: 0.012,
  }),
  wood_deck: () => new THREE.MeshStandardMaterial({ color: 0x8c5e3f, metalness: 0.05, roughness: 0.78 }),
  wood_wall: () => new THREE.MeshStandardMaterial({ color: 0x6b4a30, metalness: 0.05, roughness: 0.85 }),
  terrain:   () => new THREE.MeshStandardMaterial({ color: 0x4a5a2a, metalness: 0.0, roughness: 0.95 }),
  rock:      () => new THREE.MeshStandardMaterial({ color: 0x8a8678, metalness: 0.05, roughness: 0.88, flatShading: true }),
};

// PRNG determinístico (LCG mulberry32) — las rocas quedan fijas entre rebuilds.
function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const DEFAULT_PROFILE = { width_mm: 100, height_mm: 100 };

function profileMeters(profiles, name) {
  const p = profiles?.[name] || DEFAULT_PROFILE;
  return {
    w: (p.width_mm || 100) / 1000,
    h: (p.height_mm || 100) / 1000,
  };
}

export class CabinBuilder {
  constructor(scene) {
    this.scene = scene;
    this.group = null;
    // Materiales compartidos entre rebuilds — se crean una vez, se reusan.
    this.mats = Object.fromEntries(
      Object.entries(MATERIALS).map(([k, f]) => [k, f()])
    );
  }

  rebuild(params) {
    this._disposeGroup();
    this.group = new THREE.Group();
    this.group.name = "cabin_procedural";

    this._terrain(params);
    this._rocks(params);
    this._columns(params);
    this._platform(params);
    this._aframe(params);
    this._roofPanels(params);
    this._frontGlass(params);
    this._rearWall(params);
    this._deck(params);

    // Sombras
    this.group.traverse((obj) => {
      if (obj.isMesh) {
        obj.castShadow = true;
        obj.receiveShadow = true;
      }
    });

    this.scene.add(this.group);
    return this.group;
  }

  dispose() {
    this._disposeGroup();
    Object.values(this.mats).forEach((m) => m.dispose());
  }

  _disposeGroup() {
    if (!this.group) return;
    this.scene.remove(this.group);
    this.group.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose();
    });
    this.group = null;
  }

  // ---------------- helpers ----------------

  /** Box "beam" entre dos puntos, longitud a lo largo de la línea start→end. */
  _beam(start, end, profileW, profileH, material) {
    const dir = new THREE.Vector3().subVectors(end, start);
    const length = dir.length();
    if (length < 1e-6) return null;
    const geom = new THREE.BoxGeometry(length, profileH, profileW);
    const mesh = new THREE.Mesh(geom, material);
    mesh.position.copy(start).add(end).multiplyScalar(0.5);
    mesh.quaternion.setFromUnitVectors(
      new THREE.Vector3(1, 0, 0),
      dir.normalize(),
    );
    return mesh;
  }

  _box(w, h, d, x, y, z, material) {
    const geom = new THREE.BoxGeometry(w, h, d);
    const mesh = new THREE.Mesh(geom, material);
    mesh.position.set(x, y, z);
    return mesh;
  }

  // ---------------- component builders ----------------

  _columns(p) {
    const colsN = p.platform.column_grid_cols;
    const rowsN = p.platform.column_grid_rows;
    const widthM = p.platform.width_m;
    const depthM = p.platform.depth_m;
    const heights = p.columns.heights_m;
    const maxH = Math.max(...heights.flat());
    const prof = profileMeters(p.profiles, p.columns.profile);

    for (let row = 0; row < rowsN; row++) {
      for (let col = 0; col < colsN; col++) {
        const x = colsN > 1 ? (col / (colsN - 1)) * widthM : widthM / 2;
        const z = rowsN > 1 ? -(row / (rowsN - 1)) * depthM : -depthM / 2;
        const h = heights[row]?.[col] ?? maxH;
        const yBottom = maxH - h;
        this.group.add(
          this._box(prof.w, h, prof.h, x, yBottom + h / 2, z, this.mats.steel),
        );
      }
    }
  }

  _platform(p) {
    const widthM = p.platform.width_m;
    const depthM = p.platform.depth_m;
    const maxH = Math.max(...p.columns.heights_m.flat());
    const thickness = 0.16;
    this.group.add(this._box(
      widthM, thickness, depthM,
      widthM / 2, maxH - thickness / 2, -depthM / 2,
      this.mats.platform,
    ));
  }

  _aframe(p) {
    const widthM = p.platform.width_m;
    const depthM = p.platform.depth_m;
    const enclosedDepth = p.envelope.enclosed_depth_m;
    const apexM = p.aframe.apex_height_m;
    const nPortals = p.aframe.portal_count;
    const spacingM = p.aframe.portal_spacing_m || 1.0;
    const maxH = Math.max(...p.columns.heights_m.flat());
    const platformY = maxH;
    const yStart = (depthM - enclosedDepth) / 2;

    const rafterP = profileMeters(p.profiles, p.aframe.rafter_profile);
    const tieP    = profileMeters(p.profiles, p.aframe.tie_beam_profile);
    const ridgeP  = profileMeters(p.profiles, p.aframe.ridge_profile);
    const purlinP = profileMeters(p.profiles, p.aframe.purlin_profile);

    for (let i = 0; i < nPortals; i++) {
      const z = -(yStart + i * spacingM);
      const apex    = new THREE.Vector3(widthM / 2, platformY + apexM, z);
      const leftBot = new THREE.Vector3(0, platformY, z);
      const rightBot = new THREE.Vector3(widthM, platformY, z);
      const rafL = this._beam(leftBot,  apex, rafterP.w, rafterP.h, this.mats.steel);
      const rafR = this._beam(rightBot, apex, rafterP.w, rafterP.h, this.mats.steel);
      const tie  = this._beam(leftBot, rightBot, tieP.w, tieP.h, this.mats.steel);
      if (rafL) this.group.add(rafL);
      if (rafR) this.group.add(rafR);
      if (tie)  this.group.add(tie);
    }

    // Cumbrera (ridge)
    const zRidgeStart = -(yStart - 0.2);
    const zRidgeEnd = -(yStart + (nPortals - 1) * spacingM + 0.2);
    const ridge = this._beam(
      new THREE.Vector3(widthM / 2, platformY + apexM, zRidgeStart),
      new THREE.Vector3(widthM / 2, platformY + apexM, zRidgeEnd),
      ridgeP.w, ridgeP.h, this.mats.steel,
    );
    if (ridge) this.group.add(ridge);

    // Correas (purlins)
    const purlinRows = p.aframe.purlin_rows_per_side;
    const halfSpan = widthM / 2;
    for (const side of [-1, 1]) {
      for (let j = 0; j < purlinRows; j++) {
        const frac = (j + 0.5) / purlinRows;
        const xMid = halfSpan - side * (halfSpan * (1 - frac));
        const yMid = platformY + frac * apexM;
        const purlin = this._beam(
          new THREE.Vector3(xMid, yMid, zRidgeStart),
          new THREE.Vector3(xMid, yMid, zRidgeEnd),
          purlinP.w, purlinP.h, this.mats.steel,
        );
        if (purlin) this.group.add(purlin);
      }
    }
  }

  _roofPanels(p) {
    const widthM = p.platform.width_m;
    const depthM = p.platform.depth_m;
    const enclosedDepth = p.envelope.enclosed_depth_m;
    const apexM = p.aframe.apex_height_m;
    const nPortals = p.aframe.portal_count;
    const spacingM = p.aframe.portal_spacing_m || 1.0;
    const overhangM = p.envelope.roof_overhang_m || 0.3;
    const maxH = Math.max(...p.columns.heights_m.flat());
    const platformY = maxH;
    const yStart = (depthM - enclosedDepth) / 2;
    const halfSpan = widthM / 2;
    const rafterLen = Math.hypot(halfSpan, apexM);
    const angle = Math.atan2(apexM, halfSpan);
    const panelDepth = (nPortals - 1) * spacingM + 2 * overhangM;
    const panelThick = 0.06;
    const zCenter = -(yStart + (nPortals - 1) * spacingM / 2);

    for (const side of [-1, 1]) {
      // Posición del centro del panel (mitad entre base y apex)
      const baseX = side === -1 ? 0 : widthM;
      const midX = (baseX + widthM / 2) / 2;
      const midY = platformY + apexM / 2;
      const geom = new THREE.BoxGeometry(rafterLen, panelThick, panelDepth);
      const mesh = new THREE.Mesh(geom, this.mats.roof);
      mesh.position.set(midX, midY, zCenter);
      // Rota el panel alrededor de Z para alinearse con la pendiente del rafter.
      // Side -1 (izquierda): rafter sube hacia +X, rotación positiva alrededor de +Z.
      // Side +1 (derecha):   rafter sube hacia -X, rotación negativa.
      mesh.rotation.z = side === -1 ? angle : -angle;
      this.group.add(mesh);
    }
  }

  _frontGlass(p) {
    const widthM = p.platform.width_m;
    const apexM = p.aframe.apex_height_m;
    const depthM = p.platform.depth_m;
    const enclosedDepth = p.envelope.enclosed_depth_m;
    const maxH = Math.max(...p.columns.heights_m.flat());
    const platformY = maxH;
    const yStart = (depthM - enclosedDepth) / 2;
    const thickness = 0.012;

    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    shape.lineTo(widthM, 0);
    shape.lineTo(widthM / 2, apexM);
    shape.lineTo(0, 0);
    const geom = new THREE.ExtrudeGeometry(shape, { depth: thickness, bevelEnabled: false });
    const mesh = new THREE.Mesh(geom, this.mats.glass);
    // ExtrudeGeometry extruye en +Z local. Posicionamos el origen del shape
    // en (0, platformY, -yStart): el cristal ocupa z=[-yStart, -yStart+thickness].
    mesh.position.set(0, platformY, -yStart);
    this.group.add(mesh);
  }

  _rearWall(p) {
    const widthM = p.platform.width_m;
    const apexM = p.aframe.apex_height_m;
    const depthM = p.platform.depth_m;
    const enclosedDepth = p.envelope.enclosed_depth_m;
    const maxH = Math.max(...p.columns.heights_m.flat());
    const platformY = maxH;
    const yStart = (depthM - enclosedDepth) / 2;
    const yEnd = yStart + enclosedDepth;
    const thickness = 0.12;

    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    shape.lineTo(widthM, 0);
    shape.lineTo(widthM / 2, apexM);
    shape.lineTo(0, 0);
    const geom = new THREE.ExtrudeGeometry(shape, { depth: thickness, bevelEnabled: false });
    const mesh = new THREE.Mesh(geom, this.mats.wood_wall);
    // Muro al fondo de la zona cerrada. Origen en (0, platformY, -yEnd) y
    // grosor extruido en +Z (hacia el interior cerrado).
    mesh.position.set(0, platformY, -yEnd);
    this.group.add(mesh);
  }

  _deck(p) {
    const widthM = p.platform.width_m;
    const depthM = p.platform.depth_m;
    const enclosedDepth = p.envelope.enclosed_depth_m;
    const maxH = Math.max(...p.columns.heights_m.flat());
    const platformY = maxH;
    const yStart = (depthM - enclosedDepth) / 2;
    const thickness = 0.03;
    if (yStart <= 0) return;
    this.group.add(this._box(
      widthM, thickness, yStart,
      widthM / 2, platformY + thickness / 2, -yStart / 2,
      this.mats.wood_deck,
    ));
  }

  _terrain(p) {
    const widthM = p.platform.width_m;
    const depthM = p.platform.depth_m;
    const heights = p.columns.heights_m;
    const rowsN = heights.length;
    const maxH = Math.max(...heights.flat());
    const hBack = heights[0]?.[0] ?? maxH;
    const hFront = heights[rowsN - 1]?.[0] ?? maxH;
    // build123d y=0 → three.js z=0 (deck side); build123d y=depthM → three.js z=-depthM (back side).
    const yAtZ0 = maxH - hBack;
    const yAtZNeg = maxH - hFront;
    const slope = depthM > 0 ? (yAtZNeg - yAtZ0) / depthM : 0;  // dy / d(|z|)

    const marginX = 4;
    const marginZ = 3.5;
    const thickness = 1.0;
    const xMin = -marginX, xMax = widthM + marginX;
    const zMax = marginZ;
    const zMin = -depthM - marginZ;
    // y top extrapolado linealmente fuera del footprint
    const yTopAtZMax = yAtZ0 - slope * marginZ;
    const yTopAtZMin = yAtZNeg + slope * marginZ;
    const yBot = Math.min(yTopAtZMax, yTopAtZMin) - thickness;

    const vertices = new Float32Array([
      xMin, yTopAtZMax, zMax,  // 0
      xMax, yTopAtZMax, zMax,  // 1
      xMax, yTopAtZMin, zMin,  // 2
      xMin, yTopAtZMin, zMin,  // 3
      xMin, yBot, zMax,        // 4
      xMax, yBot, zMax,        // 5
      xMax, yBot, zMin,        // 6
      xMin, yBot, zMin,        // 7
    ]);
    const indices = [
      0, 1, 2,  0, 2, 3,    // top
      4, 6, 5,  4, 7, 6,    // bottom
      0, 4, 5,  0, 5, 1,    // +Z side
      2, 6, 7,  2, 7, 3,    // -Z side
      0, 3, 7,  0, 7, 4,    // -X side
      1, 5, 6,  1, 6, 2,    // +X side
    ];
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
    geom.setIndex(indices);
    geom.computeVertexNormals();
    this.group.add(new THREE.Mesh(geom, this.mats.terrain));
  }

  _rocks(p) {
    const widthM = p.platform.width_m;
    const depthM = p.platform.depth_m;
    const colsN = p.platform.column_grid_cols;
    const rowsN = p.platform.column_grid_rows;
    const heights = p.columns.heights_m;
    const maxH = Math.max(...heights.flat());
    const rng = mulberry32(42);

    for (let row = 0; row < rowsN; row++) {
      for (let col = 0; col < colsN; col++) {
        const x = colsN > 1 ? (col / (colsN - 1)) * widthM : widthM / 2;
        const z = rowsN > 1 ? -(row / (rowsN - 1)) * depthM : -depthM / 2;
        const h = heights[row]?.[col] ?? maxH;
        const yBase = maxH - h;

        // Roca central — más grande donde la columna es más corta.
        const r0 = 0.76 + (1.8 - h) * 0.30;
        const m0 = this._boulder(r0, rng);
        m0.position.set(x, yBase - r0 * 0.1, z);
        this.group.add(m0);

        // 3 boulders satélite.
        for (let k = 0; k < 3; k++) {
          const dx = (rng() - 0.5) * 1.3;
          const dz = (rng() - 0.5) * 1.3;
          const size = 0.38 + rng() * 0.24;
          const m = this._boulder(size, rng);
          m.position.set(x + dx, yBase - size * 0.1, z + dz);
          this.group.add(m);
        }
      }
    }
  }

  _boulder(size, rng) {
    const sx = size * (0.85 + rng() * 0.4);
    const sy = size * (0.6 + rng() * 0.45);
    const sz = size * (0.85 + rng() * 0.4);
    const geom = new THREE.BoxGeometry(sx, sy, sz);
    const mesh = new THREE.Mesh(geom, this.mats.rock);
    mesh.rotation.set(
      (rng() - 0.5) * 0.9,
      rng() * Math.PI * 2,
      (rng() - 0.5) * 0.9,
    );
    return mesh;
  }
}
