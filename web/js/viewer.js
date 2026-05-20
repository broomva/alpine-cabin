// viewer.js — Three.js viewer con geometría procedural (sliders → realtime).
//
// La cabaña se construye en JS vía CabinBuilder en lugar de cargar cabin.glb.
// El GLB sigue exportándose desde build123d como autoridad para STEP/STL y
// para validación CAD, pero el web ya no lo descarga — render en tiempo real
// de los sliders del dock/overview.

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CabinBuilder } from "./cabin-builder.js";

// Paleta de la escena por tema. theme.js dispatches `theme-change` y el
// viewer aplica estos valores a scene.background/fog/grid/hemisphere.
const SCENE_COLORS = {
  dark:  { bg: 0x141820, fogNear: 30000, fogFar: 80000, gridA: 0x4a4a4a, gridB: 0x2a2a2a, hemiSky: 0xb0c8e8, hemiGround: 0x3a4228 },
  light: { bg: 0xeae6dc, fogNear: 30000, fogFar: 80000, gridA: 0xb8b3a4, gridB: 0xd6d2c6, hemiSky: 0xdde8f8, hemiGround: 0xc8c1ad },
};

function currentTheme() {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export async function mountViewer(container, params, onLoaded, opts = {}) {
  let scene, camera, renderer, controls, gridHelper, builder, hemi;
  const w = container.clientWidth || 800;
  const h = container.clientHeight || 540;

  // ----- Scene (color inicial según tema activo) -----
  const initial = SCENE_COLORS[currentTheme()];
  scene = new THREE.Scene();
  scene.background = new THREE.Color(initial.bg);
  scene.fog = new THREE.Fog(initial.bg, initial.fogNear, initial.fogFar);

  // ----- Camera -----
  camera = new THREE.PerspectiveCamera(38, w / h, 0.1, 500);
  camera.position.set(18, 10, 16);

  // ----- Renderer -----
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(w, h);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  // ----- Lights -----
  scene.add(new THREE.AmbientLight(0xffffff, 0.55));

  const sun = new THREE.DirectionalLight(0xfff0d8, 1.4);
  sun.position.set(20, 30, 15);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -20;
  sun.shadow.camera.right = 20;
  sun.shadow.camera.top = 20;
  sun.shadow.camera.bottom = -20;
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 80;
  scene.add(sun);

  const rim = new THREE.DirectionalLight(0xd18948, 0.5);
  rim.position.set(-15, 8, -10);
  scene.add(rim);

  hemi = new THREE.HemisphereLight(initial.hemiSky, initial.hemiGround, 0.35);
  scene.add(hemi);

  // ----- Grid (toggle opcional, oculto por default) -----
  gridHelper = new THREE.GridHelper(40, 40, initial.gridA, initial.gridB);
  gridHelper.position.set(3, -1.5, -3.5);
  gridHelper.visible = false;
  scene.add(gridHelper);

  // ----- Controls -----
  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(3, 2, -3.5);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxDistance = 80;
  controls.minDistance = 4;
  controls.update();

  // ----- Procedural cabin -----
  builder = new CabinBuilder(scene);
  builder.rebuild(params);

  // Centrar target en la cabaña
  const box = new THREE.Box3().setFromObject(builder.group);
  controls.target.copy(box.getCenter(new THREE.Vector3()));
  controls.update();

  if (onLoaded) onLoaded();

  // ----- Animate -----
  function loop() {
    requestAnimationFrame(loop);
    controls.update();
    renderer.render(scene, camera);
  }
  loop();

  // ----- Resize -----
  const onResize = () => {
    const w2 = container.clientWidth;
    const h2 = container.clientHeight;
    if (w2 === 0 || h2 === 0) return;
    camera.aspect = w2 / h2;
    camera.updateProjectionMatrix();
    renderer.setSize(w2, h2);
  };
  window.addEventListener("resize", onResize);
  if (typeof ResizeObserver !== "undefined") {
    new ResizeObserver(onResize).observe(container);
  }

  // ----- Buttons -----
  const controlsRoot = opts.controlsRoot
    ? (typeof opts.controlsRoot === "string"
        ? document.querySelector(opts.controlsRoot)
        : opts.controlsRoot)
    : container.parentElement || document;

  const btnReset = controlsRoot?.querySelector('[data-action="reset-camera"]');
  const btnGrid  = controlsRoot?.querySelector('[data-action="toggle-grid"]');
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      camera.position.set(18, 10, 16);
      const b = new THREE.Box3().setFromObject(builder.group);
      controls.target.copy(b.getCenter(new THREE.Vector3()));
      controls.update();
    });
  }
  if (btnGrid) {
    btnGrid.addEventListener("click", () => {
      gridHelper.visible = !gridHelper.visible;
    });
  }

  if (!window.__cabinCamera) {
    window.__cabinCamera = camera;
    window.__cabinControls = controls;
    window.__cabinScene = scene;
  }

  // ----- Theme sync — recolor existentes (no recreate) -----
  const applySceneTheme = (theme) => {
    const c = SCENE_COLORS[theme] || SCENE_COLORS.dark;
    scene.background = new THREE.Color(c.bg);
    scene.fog = new THREE.Fog(c.bg, c.fogNear, c.fogFar);
    if (gridHelper?.material) {
      // GridHelper has two LineBasicMaterials: [center+axes color, grid color]
      const mats = Array.isArray(gridHelper.material) ? gridHelper.material : [gridHelper.material];
      if (mats[0]) mats[0].color.setHex(c.gridA);
      if (mats[1]) mats[1].color.setHex(c.gridB);
    }
    if (hemi) {
      hemi.color.setHex(c.hemiSky);
      hemi.groundColor.setHex(c.hemiGround);
    }
  };
  window.addEventListener("theme-change", (ev) => applySceneTheme(ev.detail?.theme || currentTheme()));

  return {
    scene, camera, controls, gridHelper, builder, resize: onResize,
    update(newParams) {
      builder.rebuild(newParams);
    },
  };
}
