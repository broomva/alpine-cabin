// viewer.js — Three.js viewer cargando cabin.glb.

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

/**
 * Determina el tipo de componente caminando hacia arriba en el árbol de
 * nodos del GLB, buscando un label de la forma "cabin/<kind>/...". Las
 * etiquetas las pone cad/envelope.py y cad/cabin.py.
 */
function nodeKind(node) {
  let cur = node;
  while (cur) {
    const name = (cur.name || "").toLowerCase();
    if (name.includes("terrain"))     return "terrain";
    if (name.includes("rocks"))       return "rock";
    if (name.includes("roof"))        return "roof";
    if (name.includes("glass"))       return "glass";
    if (name.includes("rear_wall"))   return "wood_wall";
    if (name.includes("deck"))        return "wood_deck";
    if (name.includes("platform"))    return "platform";
    if (name.includes("aframe"))      return "steel";
    if (name.includes("columns"))     return "steel";
    cur = cur.parent;
  }
  return "steel";
}

const MATERIALS = {
  steel:     () => new THREE.MeshStandardMaterial({ color: 0x4a4d57, metalness: 0.78, roughness: 0.32 }),
  platform:  () => new THREE.MeshStandardMaterial({ color: 0x2a2c33, metalness: 0.55, roughness: 0.55 }),
  roof:      () => new THREE.MeshStandardMaterial({ color: 0x161616, metalness: 0.62, roughness: 0.42 }),
  glass:     () => new THREE.MeshPhysicalMaterial({
    color: 0x88aaff,
    metalness: 0.0,
    roughness: 0.05,
    transmission: 0.85,
    transparent: true,
    opacity: 0.35,
    ior: 1.5,
    thickness: 0.012,
  }),
  wood_deck: () => new THREE.MeshStandardMaterial({ color: 0x8c5e3f, metalness: 0.05, roughness: 0.78 }),
  wood_wall: () => new THREE.MeshStandardMaterial({ color: 0x6b4a30, metalness: 0.05, roughness: 0.85 }),
  terrain:   () => new THREE.MeshStandardMaterial({ color: 0x4a5a2a, metalness: 0.0, roughness: 0.95 }),
  rock:      () => new THREE.MeshStandardMaterial({ color: 0x8a8678, metalness: 0.05, roughness: 0.88, flatShading: true }),
};

function materialFor(kind) {
  const fn = MATERIALS[kind] || MATERIALS.steel;
  return fn();
}

export async function mountViewer(container, glbUrl, onLoaded, opts = {}) {
  let scene, camera, renderer, controls, gridHelper;
  let model = null;
  const w = container.clientWidth || 800;
  const h = container.clientHeight || 540;

  // ----- Scene -----
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x141820);
  scene.fog = new THREE.Fog(0x141820, 30000, 80000);

  // ----- Camera (Y-up — build123d exporta gltf con Y como altura) -----
  camera = new THREE.PerspectiveCamera(38, w / h, 0.1, 500);
  camera.position.set(18, 10, 16);

  // ----- Renderer -----
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(w, h);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  // ----- Lights (en METROS, modelo viene escalado de build123d gltf) -----
  const ambient = new THREE.AmbientLight(0xffffff, 0.55);
  scene.add(ambient);

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

  // Hemisphere para llenar sombras
  const hemi = new THREE.HemisphereLight(0xb0c8e8, 0x3a4228, 0.35);
  hemi.position.set(0, 30, 0);
  scene.add(hemi);

  // ----- Grid helper (referencia opcional — el terreno real viene del GLB) -----
  gridHelper = new THREE.GridHelper(40, 40, 0x4a4a4a, 0x2a2a2a);
  gridHelper.position.set(3, -1.5, -3.5);
  gridHelper.visible = false;
  scene.add(gridHelper);

  // ----- Controls (en metros) -----
  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(3, 2, -3.5);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxDistance = 80;
  controls.minDistance = 4;
  controls.update();

  // ----- Load GLB -----
  const loader = new GLTFLoader();
  await new Promise((resolve, reject) => {
    loader.load(
      glbUrl,
      (gltf) => {
        model = gltf.scene;
        // El modelo viene de build123d en mm, con materiales planos.
        // Tintamos los compounds por label.
        model.traverse((node) => {
          if (node.isMesh) {
            node.castShadow = true;
            node.receiveShadow = true;
            node.material = materialFor(nodeKind(node));
          }
        });
        scene.add(model);
        // Centrar control target en la cabaña
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        controls.target.copy(center);
        controls.update();
        if (onLoaded) onLoaded();
        resolve();
      },
      undefined,
      (err) => reject(err),
    );
  });

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
  // Re-poll size when the panel becomes visible (tab switch can change clientWidth/Height from 0)
  if (typeof ResizeObserver !== "undefined") {
    const ro = new ResizeObserver(onResize);
    ro.observe(container);
  }

  // ----- Buttons (scoped al controlsRoot del viewer) -----
  const controlsRoot = opts.controlsRoot
    ? (typeof opts.controlsRoot === "string"
        ? document.querySelector(opts.controlsRoot)
        : opts.controlsRoot)
    : container.parentElement || document;

  const btnReset = controlsRoot?.querySelector('[data-action="reset-camera"]');
  const btnGrid = controlsRoot?.querySelector('[data-action="toggle-grid"]');

  if (btnReset) {
    btnReset.addEventListener("click", () => {
      camera.position.set(18, 10, 16);
      const box = new THREE.Box3().setFromObject(model);
      const center = box.getCenter(new THREE.Vector3());
      controls.target.copy(center);
      controls.update();
    });
  }
  if (btnGrid) {
    btnGrid.addEventListener("click", () => {
      gridHelper.visible = !gridHelper.visible;
    });
  }

  // Exponer camera/controls del primer viewer para scripts externos (ej. cad/render_views.py).
  if (!window.__cabinCamera) {
    window.__cabinCamera = camera;
    window.__cabinControls = controls;
    window.__cabinScene = scene;
  }

  return { scene, camera, controls, gridHelper, resize: onResize };
}
