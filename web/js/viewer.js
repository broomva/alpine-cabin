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
  scene.background = new THREE.Color(0x0a0a0a);
  scene.fog = new THREE.Fog(0x0a0a0a, 30000, 80000);

  // ----- Camera -----
  camera = new THREE.PerspectiveCamera(40, w / h, 100, 200000);
  camera.position.set(15000, -12000, 8000);
  camera.up.set(0, 0, 1);

  // ----- Renderer -----
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(w, h);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  // ----- Lights -----
  const ambient = new THREE.AmbientLight(0xffffff, 0.45);
  scene.add(ambient);

  const sun = new THREE.DirectionalLight(0xfff0d8, 1.2);
  sun.position.set(15000, -15000, 20000);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -15000;
  sun.shadow.camera.right = 15000;
  sun.shadow.camera.top = 15000;
  sun.shadow.camera.bottom = -15000;
  sun.shadow.camera.near = 1000;
  sun.shadow.camera.far = 50000;
  scene.add(sun);

  const rim = new THREE.DirectionalLight(0xd18948, 0.4);
  rim.position.set(-10000, 8000, 5000);
  scene.add(rim);

  // ----- Ground -----
  const groundGeom = new THREE.PlaneGeometry(60000, 60000);
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0x1f2410,
    roughness: 0.9,
    metalness: 0.0,
  });
  const ground = new THREE.Mesh(groundGeom, groundMat);
  ground.rotation.x = 0;
  ground.position.z = -1;
  ground.receiveShadow = true;
  scene.add(ground);

  // ----- Grid helper -----
  gridHelper = new THREE.GridHelper(20000, 20, 0x2a2a2a, 0x1f1f1f);
  gridHelper.rotation.x = Math.PI / 2;
  gridHelper.position.z = 0.5;
  scene.add(gridHelper);

  // ----- Controls -----
  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(3000, 3500, 3000);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxDistance = 60000;
  controls.minDistance = 3000;
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
              color: 0x1a1a1a,
              metalness: 0.85,
              roughness: 0.38,
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
    camera.position.set(15000, -12000, 8000);
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    controls.target.copy(center);
    controls.update();
  });

  document.getElementById("btn-toggle-grid").addEventListener("click", () => {
    gridHelper.visible = !gridHelper.visible;
  });
}
