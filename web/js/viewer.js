// viewer.js — Three.js viewer cargando cabin.glb.

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

let scene, camera, renderer, controls, gridHelper;
let model = null;
let onResize = null;

export async function mountViewer(container, glbUrl, onLoaded) {
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

  // ----- Ground (XZ plane en Y-up, en metros) -----
  const groundGeom = new THREE.PlaneGeometry(60, 60);
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0x3a4228,
    roughness: 0.95,
    metalness: 0.0,
  });
  const ground = new THREE.Mesh(groundGeom, groundMat);
  ground.rotation.x = -Math.PI / 2; // de XY a XZ (horizontal en Y-up)
  ground.position.y = -4.01;         // justo bajo la base del modelo
  ground.position.x = 3;
  ground.position.z = -3.5;
  ground.receiveShadow = true;
  scene.add(ground);

  // ----- Grid helper -----
  gridHelper = new THREE.GridHelper(30, 30, 0x4a4a4a, 0x2a2a2a);
  gridHelper.position.set(3, -3.99, -3.5);
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
            // Material por defecto plano — sobreescribir con un material steel-like
            node.material = new THREE.MeshStandardMaterial({
              color: 0x4a4d57,
              metalness: 0.78,
              roughness: 0.32,
              envMapIntensity: 0.8,
            });
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
  onResize = () => {
    const w2 = container.clientWidth;
    const h2 = container.clientHeight;
    camera.aspect = w2 / h2;
    camera.updateProjectionMatrix();
    renderer.setSize(w2, h2);
  };
  window.addEventListener("resize", onResize);

  // ----- Buttons -----
  document.getElementById("btn-reset-camera").addEventListener("click", () => {
    camera.position.set(18, 10, 16);
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    controls.target.copy(center);
    controls.update();
  });

  document.getElementById("btn-toggle-grid").addEventListener("click", () => {
    gridHelper.visible = !gridHelper.visible;
  });

  // Exponer camera/controls para scripts externos (ej. cad/render_views.py).
  window.__cabinCamera = camera;
  window.__cabinControls = controls;
  window.__cabinScene = scene;
}
