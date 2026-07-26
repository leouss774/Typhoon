import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';


// ====== Time mode (before/after) ======

type TimeMode = 'current' | 'projected';
let timeMode: TimeMode = 'current';
let onTimeModeChangeCallback: ((mode: TimeMode) => void) | null = null;

// Dynamic part data store (from merged assessment)
let partDataStore: Record<string, HousePartData> | null = null;

// Default fallback footprint (rectangle) when no BDNB data
let pendingFootprint: FootprintGeometry | null = null;

function generateDefaultFootprint(): FootprintGeometry {
  const hw = 0.9, hd = 1.1;
  return {
    type: 'Polygon',
    coordinates: [[
      [-hw, -hd], [hw, -hd], [hw, hd], [-hw, hd], [-hw, -hd]
    ]],
  };
}

// ====== State ======

let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let renderer: THREE.WebGLRenderer | null = null;

let composer: EffectComposer | null = null;
let controls: OrbitControls | null = null;
let animationId: number | null = null;

interface InteractivePart {
  mesh: THREE.Mesh;
  originalPos: THREE.Vector3;
  originalColor: THREE.Color;
  data: HousePartData;
  isFloating: boolean;

}

interface PartMap {
  [id: string]: InteractivePart;
}

const parts: PartMap = {};
let raycaster: THREE.Raycaster;
let mouse: THREE.Vector2;
let containerEl: HTMLElement | null = null;
let selectedPartId: string | null = null;
let animationTime = 0;
let groundMesh: THREE.Mesh | null = null;

let onPartSelectCallback: ((data: HousePartData) => void) | null = null;

// Auto-rotation: stop when user interacts, resume after idle
let autoRotateTimeout: ReturnType<typeof setTimeout> | null = null;
const AUTO_ROTATE_IDLE = 3000; // 3 seconds idle before resuming

// ====== Public types ======

export interface HousePartData {
  id: string;
  label: string;
  risk: 'critical' | 'high' | 'medium' | 'low';
  score: number;
  description: string;
  cost: string;
  annualSavings: string;
  works: string[];
  premiumAfter: string;
  // Extended fields from merged assessment
  alea_principal?: string;
  niveau?: 'faible' | 'moyen' | 'eleve' | 'critique';
  triggered_rules?: Array<{
    rule_id: string;
    peril: string;
    points: number;
    justification: string;
    source_fields: string[];
    activated_by_llm: boolean;
  }>;
  recommandations?: Array<{
    travaux: string;
    cout_estime: string;
    gain_resilience: number;
  }>;
  test_vulnerabilite?: {
    verdict: string;
    explication: string;
  };
}

// ====== Part Data ======

export const housePartData: Record<string, HousePartData> = {
  roof: {
    id: 'roof',
    label: 'Toiture',
    risk: 'high',
    score: 72,
    description: "Isolation vétuste et tuiles fissurées. Risque de fuite et de déperdition calorifique en cas d'épisode climatique extrême.",
    cost: '1 000 €',
    annualSavings: '-100 €/an',
    works: ["Remplacement de l'isolation (laine de roche)", 'Réparation des tuiles endommagées', 'Installation de chéneaux renforcés'],
    premiumAfter: '−12% sur la prime habitation',
  },
  walls: {
    id: 'walls',
    label: 'Façade & Murs',
    risk: 'medium',
    score: 48,
    description: 'Fissures capillaires sur la façade exposée sud. Risque de dégradation accélérée par les cycles gel-dégel.',
    cost: '2 500 €',
    annualSavings: '-60 €/an',
    works: ['Rebouchage des fissures', "Application d'un revêtement hydrofuge", 'Isolation thermique par extérieur (ITE)'],
    premiumAfter: '−8% sur la prime habitation',
  },
  ground: {
    id: 'ground',
    label: 'Fondations & Sol',
    risk: 'high',
    score: 78,
    description: 'Zone à risque de retrait-gonflement des argiles. Les fondations sont vulnérables en cas de sécheresse prolongée.',
    cost: '8 000 €',
    annualSavings: '-200 €/an',
    works: ['Étude géotechnique préalable', 'Reprise des fondations par micro-pieux', 'Drainage périphérique renforcé'],
    premiumAfter: '−20% sur la prime habitation',
  },
  windows: {
    id: 'windows',
    label: 'Menuiseries',
    risk: 'low',
    score: 22,
    description: 'Double vitrage récent (2022). Bonne isolation thermique et acoustique. Aucun risque structurel identifié.',
    cost: '800 €',
    annualSavings: '-150 €/an',
    works: ["Remplacement des joints d'étanchéité", 'Installation de volets roulants isolants', 'Survitrage anti-tempête'],
    premiumAfter: '−5% sur la prime habitation',
  },
  chimney: {
    id: 'chimney',
    label: 'Conduits & Cheminée',
    risk: 'medium',
    score: 45,
    description: 'Conduit partiellement obstrué par des résidus de combustion. Risque de refoulement de fumées et de tirage insuffisant.',
    cost: '600 €',
    annualSavings: '-40 €/an',
    works: ['Ramonage complet du conduit', "Installation d'un extracteur statique", 'Mise aux normes du tubage'],
    premiumAfter: '−6% sur la prime habitation',
  },
};



// ====== Part registration ======

function registerPart(pid: string, mesh: THREE.Mesh, color: number) {
  const pos = mesh.position.clone();
  const data = partDataStore?.[pid] || housePartData[pid] || housePartData.roof;

  parts[pid] = {
    mesh,
    originalPos: pos,
    originalColor: new THREE.Color(color),
    data,
    isFloating: false,
  };
}

function getInteractiveMeshes(): THREE.Mesh[] {
  return Object.values(parts).map(p => p.mesh);
}



// ====== Public callback setter ======

export function onHousePartSelect(callback: (data: HousePartData) => void): void {
  onPartSelectCallback = callback;
}

/** Subscribe to time mode changes (before/after toggle) */
export function onTimeModeChange(callback: (mode: TimeMode) => void): void {
  onTimeModeChangeCallback = callback;
}

/** Get current time mode */
export function getTimeMode(): TimeMode {
  return timeMode;
}

/**
 * Set dynamic part data from merged assessment.
 * Updates all part colors and data immediately.
 */
export function setHousePartData(data: Record<string, HousePartData>): void {
  partDataStore = data;
  // Update all registered parts with the new data
  for (const [partId, partData] of Object.entries(data)) {
    if (parts[partId]) {
      parts[partId].data = partData;
    }
  }
  updatePartColors();
}

/**
 * Toggle between 'current' (2025) and 'projected' (2050) time mode.
 * Animates color transitions on all house parts.
 */
export function setTimeMode(mode: TimeMode): void {
  if (mode === timeMode) return;
  timeMode = mode;
  updatePartColors();
  if (onTimeModeChangeCallback) {
    onTimeModeChangeCallback(mode);
  }
}

/** Recalculate all part colors based on current time mode and data */
function updatePartColors(): void {
  for (const part of Object.values(parts)) {
    const data = part.data;
    const color = scoreToHex(data.score);
    part.originalColor.setHex(color);
    const mat = part.mesh.material;
    if ('emissive' in mat) {
      const stdMat = mat as THREE.MeshStandardMaterial;
      stdMat.color.setHex(color);
      stdMat.emissive.setHex(color);
      stdMat.emissiveIntensity = 0.15;
    }
  }
}

/** Map a score (0-100) to a hex color */
function scoreToHex(score: number): number {
  if (score >= 80) return 0xdc2626;  // critique
  if (score >= 60) return 0xef4444;  // élevé
  if (score >= 45) return 0xf59e0b;  // moyen
  if (score >= 25) return 0x3b82f6;  // faible
  return 0x10b981;                    // très faible
}

/* ═══════════════════════════════════════════════════════════════
   Footprint Geometry — Real building contour from BDNB
   ═══════════════════════════════════════════════════════════════ */

/**
 * Set pending footprint geometry to use instead of OBJ/fallback.
 * Call BEFORE initHouse() — the geometry is consumed at init time.
 */
export function setFootprintGeometry(geom: { type: string; coordinates: any } | null | undefined): void {
  if (!geom || (geom.type !== 'MultiPolygon' && geom.type !== 'Polygon')) {
    pendingFootprint = null;
    return;
  }
  pendingFootprint = geom as FootprintGeometry;
}

interface FootprintGeometry {
  type: 'MultiPolygon' | 'Polygon';
  coordinates: number[][][][] | number[][][];
}

/**
 * Build a 3D house model from BDNB footprint geometry (Lambert-93 MultiPolygon).
 * If geometry is invalid (shouldn't happen — generateDefaultFootprint() always
 * produces a valid rectangle), the function gracefully returns early.
 */
function createBuildingFromFootprint(geom: FootprintGeometry): void {
  if (!scene) return;

  const group = new THREE.Group();

  // --- Extract polygon rings from MultiPolygon ---
  let coordsToProcess: number[][][] = [];

  if (geom.type === 'MultiPolygon') {
    const mp = geom as { type: 'MultiPolygon'; coordinates: number[][][][] };
    for (const polygon of mp.coordinates) {
      coordsToProcess.push(...polygon);
    }
  } else if (geom.type === 'Polygon') {
    coordsToProcess = (geom as { type: 'Polygon'; coordinates: number[][][] }).coordinates;
  }

  // Keep only the outer ring (first ring) of the largest polygon
  if (coordsToProcess.length === 0) return;

  // Convert Lambert-93 (X,Y in meters) to local Three.js (X,Z) centered at centroid
  const allPts: { x: number; z: number }[] = [];
  for (const ring of coordsToProcess) {
    for (const pt of ring) {
      if (pt.length >= 2) allPts.push({ x: pt[0], z: pt[1] });
    }
  }

  if (allPts.length < 3) return;

  // Compute centroid
  let cx = 0, cz = 0;
  for (const p of allPts) { cx += p.x; cz += p.z; }
  cx /= allPts.length; cz /= allPts.length;

  // Center points and scale to fit Three.js scene
  const centered: { x: number; z: number }[] = allPts.map(p => ({
    x: (p.x - cx),
    z: (p.z - cz),
  }));

  // Find bounding box to compute scale
  let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
  for (const p of centered) {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.z < minZ) minZ = p.z;
    if (p.z > maxZ) maxZ = p.z;
  }
  const footprintWidth = maxX - minX || 1;
  const footprintDepth = maxZ - minZ || 1;
  const longestSide = Math.max(footprintWidth, footprintDepth);
  const scale = 1.8 / longestSide;

  // --- Dimensions & Geometry ---
  const width = Math.max(1.4, Math.min(2.4, footprintWidth * scale * 1.2));
  const depth = Math.max(1.2, Math.min(2.0, footprintDepth * scale * 1.2));
  const wallH = 0.85;
  const roofH = 0.55;

  // 1. Main House Walls (PBR Stucco plaster)
  const wallGeo = new THREE.BoxGeometry(width, wallH, depth);
  const wallMat = new THREE.MeshStandardMaterial({
    color: 0xf4eee8,
    roughness: 0.7,
    metalness: 0.05,
  });
  const walls = new THREE.Mesh(wallGeo, wallMat);
  walls.position.set(0, wallH / 2, 0);
  walls.castShadow = true;
  walls.receiveShadow = true;
  walls.userData = { isPart: true, partId: 'walls' };
  group.add(walls);

  // 2. Concrete Foundation Base
  const baseGeo = new THREE.BoxGeometry(width + 0.1, 0.08, depth + 0.1);
  const baseMat = new THREE.MeshStandardMaterial({ color: 0x7a7267, roughness: 0.9 });
  const baseMesh = new THREE.Mesh(baseGeo, baseMat);
  baseMesh.position.set(0, 0.04, 0);
  baseMesh.receiveShadow = true;
  baseMesh.userData = { isPart: true, partId: 'ground' };
  group.add(baseMesh);

  // 3. Pitched Tile Roof (Realistic 4-sided pyramid / hip roof)
  const roofGeo = new THREE.ConeGeometry(Math.max(width, depth) * 0.78, roofH, 4);
  roofGeo.rotateY(Math.PI / 4); // Align flat faces with box walls
  const roofMat = new THREE.MeshStandardMaterial({
    color: 0x9b3a2b, // Terracotta red clay tiles
    roughness: 0.5,
    metalness: 0.1,
  });
  const roof = new THREE.Mesh(roofGeo, roofMat);
  roof.position.set(0, wallH + roofH / 2, 0);
  roof.scale.set(width / (Math.max(width, depth) * 0.75), 1, depth / (Math.max(width, depth) * 0.75));
  roof.castShadow = true;
  roof.receiveShadow = true;
  roof.userData = { isPart: true, partId: 'roof' };
  group.add(roof);

  // 4. Windows (Front & Back Façades with glass + frames)
  const windowGroup = new THREE.Group();
  const winFrameMat = new THREE.MeshStandardMaterial({ color: 0x2b2b2b, roughness: 0.3 });
  const winGlassMat = new THREE.MeshStandardMaterial({
    color: 0x88ccff,
    roughness: 0.1,
    metalness: 0.8,
    transparent: true,
    opacity: 0.7,
  });

  const winW = 0.26, winH = 0.32;
  const createWindow = (x: number, y: number, z: number, rotY: number) => {
    const wWin = new THREE.Group();
    // Frame
    const frameMesh = new THREE.Mesh(new THREE.BoxGeometry(winW + 0.04, winH + 0.04, 0.04), winFrameMat);
    // Glass
    const glassMesh = new THREE.Mesh(new THREE.BoxGeometry(winW, winH, 0.03), winGlassMat);
    wWin.add(frameMesh);
    wWin.add(glassMesh);
    wWin.position.set(x, y, z);
    wWin.rotation.y = rotY;
    return wWin;
  };

  // Front Windows (2 floors / 4 windows)
  windowGroup.add(createWindow(-width * 0.28, wallH * 0.7, depth / 2 + 0.01, 0));
  windowGroup.add(createWindow(width * 0.28, wallH * 0.7, depth / 2 + 0.01, 0));
  windowGroup.add(createWindow(width * 0.28, wallH * 0.28, depth / 2 + 0.01, 0));

  // Back Windows
  windowGroup.add(createWindow(-width * 0.28, wallH * 0.7, -depth / 2 - 0.01, Math.PI));
  windowGroup.add(createWindow(width * 0.28, wallH * 0.7, -depth / 2 - 0.01, Math.PI));

  // Side Windows
  windowGroup.add(createWindow(width / 2 + 0.01, wallH * 0.6, 0, Math.PI / 2));
  windowGroup.add(createWindow(-width / 2 - 0.01, wallH * 0.6, 0, -Math.PI / 2));

  windowGroup.userData = { isPart: true, partId: 'windows' };
  group.add(windowGroup);

  // 5. Entrance Door
  const doorW = 0.24, doorH = 0.42;
  const doorGeo = new THREE.BoxGeometry(doorW, doorH, 0.04);
  const doorMat = new THREE.MeshStandardMaterial({ color: 0x4a2c11, roughness: 0.6 });
  const door = new THREE.Mesh(doorGeo, doorMat);
  door.position.set(-width * 0.22, doorH / 2, depth / 2 + 0.01);
  door.castShadow = true;
  group.add(door);

  // 6. Brick Chimney
  const chimW = 0.16, chimH = 0.5;
  const chimGeo = new THREE.BoxGeometry(chimW, chimH, chimW);
  const chimMat = new THREE.MeshStandardMaterial({ color: 0x7c3a27, roughness: 0.8 });
  const chimney = new THREE.Mesh(chimGeo, chimMat);
  chimney.position.set(width * 0.28, wallH + chimH * 0.4, -depth * 0.15);
  chimney.castShadow = true;
  chimney.userData = { isPart: true, partId: 'chimney' };
  group.add(chimney);

  // --- Register meshes ---
  const wallColor = partDataStore?.walls?.score != null ? scoreToHex(partDataStore.walls.score) : 0xf4eee8;
  registerPart('walls', walls, wallColor);

  const roofColor = partDataStore?.roof?.score != null ? scoreToHex(partDataStore.roof.score) : 0x9b3a2b;
  registerPart('roof', roof, roofColor);

  const groundColor = partDataStore?.ground?.score != null ? scoreToHex(partDataStore.ground.score) : 0x7a7267;
  registerPart('ground', baseMesh, groundColor);

  const winColor = partDataStore?.windows?.score != null ? scoreToHex(partDataStore.windows.score) : 0x88ccff;
  // Register main glass panels for window clicking
  windowGroup.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.userData = { isPart: true, partId: 'windows' };
    }
  });
  registerPart('windows', windowGroup.children[0]?.children[0] as THREE.Mesh || walls, winColor);

  const chimColor = partDataStore?.chimney?.score != null ? scoreToHex(partDataStore.chimney.score) : 0x7c3a27;
  registerPart('chimney', chimney, chimColor);

  scene.add(group);
  console.log(`🏠 Realistic 3D House model constructed (${width.toFixed(2)}m x ${depth.toFixed(2)}m)`);
}

/** Programmatically select a house part (used by card clicks) */
export function selectHousePart(partId: string): void {
  if (!parts[partId]) return;
  const part = parts[partId];

  // Deselect previous
  if (selectedPartId && parts[selectedPartId]) {
    parts[selectedPartId].isFloating = false;
  }

  // Toggle selection
  if (selectedPartId === partId) {
    selectedPartId = null;
    part.isFloating = false;
  } else {
    selectedPartId = partId;
    part.isFloating = true;
    if (controls) {
      controls.target.copy(part.originalPos);
    }
  }

  if (onPartSelectCallback) {
    onPartSelectCallback(part.isFloating ? part.data : housePartData.roof);
  }
}

// ====== Init ======

export function initHouse(containerId: string): void {
  containerEl = document.getElementById(containerId);
  if (!containerEl || scene) return;

  const rect = containerEl.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) {
    requestAnimationFrame(() => initHouse(containerId));
    return;
  }

  const w = rect.width;
  const h = rect.height;

  // --- Scene ---
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf2ebe3); // warm cream

  // --- Camera ---
  camera = new THREE.PerspectiveCamera(28, w / h, 0.1, 50);
  camera.position.set(4.5, 3.0, 5.0);
  camera.lookAt(0, 0.5, 0);

  // --- WebGL Renderer ---
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: false,
    powerPreference: 'high-performance',
  });
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  containerEl.appendChild(renderer.domElement);



  // --- Post-processing ---
  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(w, h),
    0.04,   // strength — very subtle (was 0.15, caused foggy look)
    0.3,    // radius
    0.4     // threshold — only bloom very bright areas
  );
  composer.addPass(bloomPass);
  composer.addPass(new OutputPass());

  // --- Warm custom environment for rich PBR reflections ---
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  pmremGenerator.compileEquirectangularShader();
  const envScene = new THREE.Scene();
  // Use neutral warm-cream background so reflections don't tint the model orange
  envScene.background = new THREE.Color(0xece6dd);
  const envLight = new THREE.DirectionalLight(0xffe8d0, 1.5);
  envLight.position.set(1, 1, 0.5);
  envScene.add(envLight);
  const envFill = new THREE.DirectionalLight(0x8fc5e8, 0.3);
  envFill.position.set(-0.5, 0.3, -0.5);
  envScene.add(envFill);
  const envTexture = pmremGenerator.fromScene(envScene, 0).texture;
  scene.environment = envTexture;
  pmremGenerator.dispose();

  // --- Lights ---
  const ambient = new THREE.AmbientLight(0xffffff, 0.4);
  scene.add(ambient);

  // Key light — warm, from upper-right
  const keyLight = new THREE.DirectionalLight(0xffe8d0, 4.0);
  keyLight.position.set(6, 10, 4);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(2048, 2048);
  keyLight.shadow.camera.near = 1;
  keyLight.shadow.camera.far = 20;
  keyLight.shadow.camera.left = -5;
  keyLight.shadow.camera.right = 5;
  keyLight.shadow.camera.top = 5;
  keyLight.shadow.camera.bottom = -5;
  keyLight.shadow.bias = -0.001;
  scene.add(keyLight);

  // Fill light — warm, from left
  const fillLight = new THREE.DirectionalLight(0xffccaa, 0.8);
  fillLight.position.set(-3, 2, 1);
  scene.add(fillLight);

  // Rim light — warm, from behind
  const rimLight = new THREE.DirectionalLight(0xffdbb8, 0.5);
  rimLight.position.set(0, 2, -5);
  scene.add(rimLight);

  // Warm accent from below (terracotta glow)
  const accentLight = new THREE.DirectionalLight(0xc56a3d, 0.5);
  accentLight.position.set(0.5, -1.5, 0.5);
  scene.add(accentLight);

  // Hemisphere for sky/ground color bleed
  const hemi = new THREE.HemisphereLight(0xffeedd, 0xc56a3d, 0.4);
  scene.add(hemi);

  // --- Ground Plane (matte warm base) ---
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0xd4ccc4,
    roughness: 0.9,
    metalness: 0,
    envMapIntensity: 0.05, // barely visible reflection
  });
  const groundGeo = new THREE.CircleGeometry(4.0, 48);
  groundMesh = new THREE.Mesh(groundGeo, groundMat);
  groundMesh.rotation.x = -Math.PI / 2;
  groundMesh.position.y = -0.01;
  groundMesh.receiveShadow = true;
  scene.add(groundMesh);

  // --- OrbitControls ---
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 2.5;
  controls.maxDistance = 12;
  controls.maxPolarAngle = Math.PI / 2.1;
  controls.target.set(0, 0.5, 0);
  controls.autoRotate = false;
  controls.update();

  // Stop auto-rotation on user interaction via CSS2D overlay
  renderer.domElement.addEventListener('pointerdown', onUserInteract);
  renderer.domElement.addEventListener('wheel', onUserInteract);

  // --- Interaction ---
  raycaster = new THREE.Raycaster();
  mouse = new THREE.Vector2();
  containerEl.addEventListener('mousemove', onMouseMove);
  containerEl.addEventListener('click', onMouseClick);

  // --- Resize ---
  new ResizeObserver(() => {
    if (!containerEl || !camera || !renderer || !composer) return;
    const r = containerEl.getBoundingClientRect();
    camera.aspect = r.width / r.height;
    camera.updateProjectionMatrix();
    renderer.setSize(r.width, r.height);
    composer.setSize(r.width, r.height);
  }).observe(containerEl);

  // Build house from footprint (BDNB or default rectangle)
  const footprint = pendingFootprint || generateDefaultFootprint();
  pendingFootprint = null;
  createBuildingFromFootprint(footprint);
  animate();
}

// ====== User interaction resets auto-rotation timer ======

function onUserInteract() {
  if (!controls) return;
  controls.autoRotate = false;
  if (autoRotateTimeout) clearTimeout(autoRotateTimeout);
  autoRotateTimeout = setTimeout(() => {
    if (controls) controls.autoRotate = true;
  }, AUTO_ROTATE_IDLE);
}



// ====== Interaction ======

function onMouseMove(e: MouseEvent) {
  if (!containerEl || !camera || !scene) return;
  const rect = containerEl.getBoundingClientRect();
  mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(getInteractiveMeshes(), false);

  // Reset all highlights except selected (guard for non-MeshStandardMaterial)
  Object.values(parts).forEach(p => {
    if (!p.isFloating) {
      const mat = p.mesh.material;
      if ('emissive' in mat) {
        (mat as THREE.MeshStandardMaterial).emissive.setHex(0x000000);
        (mat as THREE.MeshStandardMaterial).emissiveIntensity = 0;
      }
    }
  });
  if (selectedPartId && parts[selectedPartId]) {
    const mat = parts[selectedPartId].mesh.material;
    if ('emissive' in mat) {
      (mat as THREE.MeshStandardMaterial).emissive.setHex(0xc56a3d);
      (mat as THREE.MeshStandardMaterial).emissiveIntensity = 0.25;
    }
  }
  containerEl!.style.cursor = 'grab';

  if (intersects.length > 0) {
    const hitId = Object.keys(parts).find(id => {
      const p = parts[id];
      return p.mesh === intersects[0].object ||
        (intersects[0].object as THREE.Mesh).userData?.partId === id;
    });
    if (hitId && parts[hitId]) {
      const mat = parts[hitId].mesh.material;
      if ('emissive' in mat) {
        (mat as THREE.MeshStandardMaterial).emissive.setHex(0xc56a3d);
        (mat as THREE.MeshStandardMaterial).emissiveIntensity = 0.12;
      }
      containerEl!.style.cursor = 'pointer';
    }
  }
}

function onMouseClick(e: MouseEvent) {
  if (!containerEl || !camera || !scene) return;
  const rect = containerEl.getBoundingClientRect();
  mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(getInteractiveMeshes(), false);

  if (intersects.length > 0) {
    const hitId = Object.keys(parts).find(id => {
      const p = parts[id];
      return p.mesh === intersects[0].object ||
        (intersects[0].object as THREE.Mesh).userData?.partId === id;
    });

    if (hitId && parts[hitId]) {
      const part = parts[hitId];

      if (selectedPartId === hitId) {
        selectedPartId = null;
        part.isFloating = false;
      } else {
        if (selectedPartId && parts[selectedPartId]) {
          parts[selectedPartId].isFloating = false;
        }
        selectedPartId = hitId;
        part.isFloating = true;
        // Move camera to look at the selected part
        if (controls) {
          controls.target.copy(part.originalPos);
        }
      }

      if (onPartSelectCallback && part.isFloating) {
        onPartSelectCallback(part.data);
      } else if (onPartSelectCallback) {
        onPartSelectCallback(housePartData.roof);
      }
    }
  }
}

// ====== Animation ======

function animate() {
  animationId = requestAnimationFrame(animate);
  animationTime += 0.016;

  if (!camera || !renderer || !scene || !composer || !controls) return;

  // Update controls
  controls.update();

    // Animate floating parts + smooth color transitions
  Object.values(parts).forEach(p => {
    const targetY = p.isFloating ? p.originalPos.y + 0.5 : p.originalPos.y;
    p.mesh.position.y += (targetY - p.mesh.position.y) * 0.06;

    // Safe material access — all zone meshes are MeshStandardMaterial
    const mat = p.mesh.material;
    if ('color' in mat) {
      const stdMat = mat as THREE.MeshStandardMaterial;
      const currentColor = stdMat.color.getHex();
      const targetColor = p.originalColor.getHex();
      if (currentColor !== targetColor) {
        const cur = new THREE.Color(currentColor);
        const tgt = new THREE.Color(targetColor);
        cur.lerp(tgt, 0.04);
        stdMat.color.setHex(cur.getHex());
      }

      if (p.isFloating) {
        p.mesh.position.y += Math.sin(animationTime * 2.5) * 0.004;
        stdMat.emissive.setHex(0xc56a3d);
        stdMat.emissiveIntensity = 0.2 + Math.sin(animationTime * 3) * 0.08;
      }
    }
  });

  // Render via composer (post-processing)
  composer.render();


}

// ====== Cleanup ======

export function destroyHouse(): void {
  if (animationId !== null) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
  if (autoRotateTimeout) clearTimeout(autoRotateTimeout);

  if (controls) {
    controls.dispose();
    controls = null;
  }

  const domEl = renderer?.domElement;
  if (containerEl) {
    containerEl.removeEventListener('mousemove', onMouseMove);
    containerEl.removeEventListener('click', onMouseClick);
    if (domEl) containerEl.removeChild(domEl);
  }

  if (composer) {
    composer.dispose();
    composer = null;
  }

  if (scene) {
    scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose();
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.dispose());
        } else {
          child.material.dispose();
        }
      }
    });
  }

  scene = null;
  camera = null;
  renderer = null;
  groundMesh = null;
  Object.keys(parts).forEach(k => delete parts[k]);
  selectedPartId = null;
  onPartSelectCallback = null;
  containerEl = null;
  animationTime = 0;
}
