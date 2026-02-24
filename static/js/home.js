/**
 * home.js — Three.js WebGL scene for the Yurt Tech home page.
 * Spinning metallic bouba shape with vintage colored lighting and bloom.
 */

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { FilmPass } from 'three/addons/postprocessing/FilmPass.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

// ==================== RENDERER ====================

const canvas = document.getElementById('home-canvas');

const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: false,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;

// ==================== SCENE & CAMERA ====================

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0d0d0d);

const camera = new THREE.PerspectiveCamera(
    50,
    window.innerWidth / window.innerHeight,
    0.1,
    200
);
camera.position.set(0, 0, 38);

// =================== background ====================

const video = document.createElement('video');
video.controls = false;
video.playsInline = true;
video.muted = true;
video.autoplay = true;

video.src = 'static/resources/radar.mp4';
video.loop = true;

video.play()

const videoTexture = new THREE.VideoTexture(video);
// You may need to adjust the texture encoding based on your scene setup
// videoTexture.encoding = THREE.sRGBEncoding;

const radar = new THREE.MeshBasicMaterial({ map: videoTexture });
const radarGeometry = new THREE.PlaneGeometry(75, 38); // Example geometry
const radarMesh = new THREE.Mesh(radarGeometry, radar);
scene.add(radarMesh);


// ==================== GEOMETRY & MATERIAL ====================

// TorusKnot: organic, rounded, twisted — the "bouba" shape
const geometry = new THREE.TorusKnotGeometry(4, 0.6, 640, 180, 2, 3);

const material = new THREE.MeshStandardMaterial({
    color: 0xf1ff64,
    metalness: 1,
    roughness: 0.26,
    emissive: 0x684902,
    emissiveIntensity: 0.1,
    fog: true,
    depthTest: false
});

const mesh = new THREE.Mesh(geometry, material);

const pos = geometry.attributes.position;
const arr = pos.array;

let minY = Infinity;
let maxY = -Infinity;

// first pass: find bounds
for (let i = 1; i < arr.length; i += 3) {
  const y = arr[i];
  if (y < minY) minY = y;
  if (y > maxY) maxY = y;
}

const height = maxY - minY;
const twistAmount = Math.PI * 2; // 1 full rotation over height

// second pass: twist
for (let i = 0; i < arr.length; i += 3) {
  const x = arr[i];
  const y = arr[i + 1];
  const z = arr[i + 2];

  const t = (y - minY) / height;   // normalize 0 → 1
  const angle = t * twistAmount;

  const cos = Math.cos(angle);
  const sin = Math.sin(angle);

  arr[i]     = x * cos - z * sin;
  arr[i + 2] = x * sin + z * cos;
}

pos.needsUpdate = true;
geometry.computeVertexNormals();

geometry.translate(0, -8, 0)
//scene.add(mesh);

// =================== TEXT ===================

const map = new THREE.TextureLoader().load( 'static/resources/yt_sword.png' );
const spriteMaterial = new THREE.SpriteMaterial( { map: map } );
const sprite = new THREE.Sprite( spriteMaterial );
sprite.scale.set( 13, 4, 10 ); // Adjust scale as needed
sprite.translateY(-15)
scene.add( sprite );

// ==================== LIGHTING ====================

// Dim ambient — keeps shadow areas from going pure black
const ambient = new THREE.AmbientLight(0x404040, 0.6);
scene.add(ambient);

// White directional light at half intensity shining from the top.
const directionalLight = new THREE.DirectionalLight( 0xffffff, 1 );
scene.add( directionalLight );

// Warm amber — upper left front — primary highlight
const warmLight = new THREE.PointLight(0xff8800, 120, 90);
warmLight.position.set(-20, 16, 22);
scene.add(warmLight);

// Cool blue — lower right front — complementary fill
const coolLight = new THREE.PointLight(0x0044ff, 100, 90);
coolLight.position.set(20, -16, 22);
scene.add(coolLight);

// Subtle magenta — rear — adds depth to the silhouette
const fillLight = new THREE.PointLight(0xaa0055, 45, 70);
fillLight.position.set(0, 5, -25);
scene.add(fillLight);

scene.fog = new THREE.Fog(0x3f7b9d, 1, 1000)

// ==================== POST-PROCESSING ====================

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.21,   // strength — subtle, not overwhelming
    0.2,   // radius
    0.71   // threshold — only brightest surface highlights bloom
);
composer.addPass(bloomPass);

const filmPass = new FilmPass(0.51);

composer.addPass(filmPass);

// ==================== ANIMATION LOOP ====================

function animate() {
    requestAnimationFrame(animate);
    //mesh.rotation.x += 0.001;
    mesh.rotation.y += 0.0018; // very slow y drift for visual interest
    composer.render();
}

animate();

// ==================== RESIZE HANDLER ====================

window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    composer.setSize(w, h);
    bloomPass.resolution.set(w, h);
});
