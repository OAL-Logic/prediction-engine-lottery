import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { useResonanceStore } from '../stores/useResonanceStore';

// Custom shaders for high-performance GPU-driven Riemannian Manifold morphing
const ManifoldShader = {
  uniforms: {
    uTime: { value: 0 },
    uFrequency: { value: 0.25 },
    uDeviation: { value: 0.25 },
    uCosmic: { value: 0.25 },
    uMl: { value: 0.25 },
    uResonating: { value: 1.0 },
    uActiveArcano: { value: 0 },
    uIsArcano78Active: { value: 0.0 },
    uShowEsotericFilters: { value: 0.0 },
    uMuonStrikeTime: { value: 0.0 },
    uMuonStrikeOrigin: { value: new THREE.Vector3(0, 0, 0) },
    uMuonStrikeActive: { value: 0.0 },
  },
  vertexShader: `
    uniform float uTime;
    uniform float uFrequency;
    uniform float uDeviation;
    uniform float uCosmic;
    uniform float uMl;
    uniform float uResonating;
    uniform float uMuonStrikeTime;
    uniform vec3 uMuonStrikeOrigin;
    uniform float uMuonStrikeActive;

    attribute float aPhi;
    attribute float aTheta;
    attribute float aIsGold;
    attribute float aIsRed;

    varying vec3 vPosition;
    varying float vIsGold;
    varying float vIsRed;
    varying float vShockwaveColorFactor;

    void main() {
      float t = uResonating > 0.5 ? uTime : 0.0;

      // Mathematical definition of the curved Riemannian probability density
      float R = 7.0 + 1.8 * (
        uFrequency * sin(3.0 * aPhi + t) * cos(3.0 * aTheta) +
        uDeviation * cos(5.0 * aPhi - t) * sin(2.0 * aTheta) +
        uCosmic * sin(7.0 * aPhi + 1.5 * t) * cos(aTheta) +
        uMl * cos(2.0 * aPhi) * sin(5.0 * aTheta - 0.8 * t)
      );

      // Sphere mapping
      vec3 localPos = vec3(
        R * sin(aPhi) * cos(aTheta),
        R * sin(aPhi) * sin(aTheta),
        R * cos(aPhi)
      );

      // Cosmic Ray Muon Strike Single-Event Upset Radial Shockwave Simulation
      float dist = distance(localPos, uMuonStrikeOrigin);
      float shockwave = 0.0;
      if (uMuonStrikeActive > 0.5) {
        float waveRadius = uMuonStrikeTime * 15.0; // Wave expands radially
        float width = 2.0;
        float waveDist = abs(dist - waveRadius);
        if (waveDist < width) {
          // Dynamic sine ripple that decays in time and distance
          shockwave = cos(waveDist * (3.14159 / width)) * (1.0 - waveDist / width) * exp(-uMuonStrikeTime * 1.8);
        }
      }

      // Perturb local position outward along standard normal
      vec3 localPosWithShock = localPos + normalize(localPos) * shockwave * 1.2;

      // Position instances (each instanced point is a low-poly quad or box offset)
      vec3 transformed = localPosWithShock + position * 0.08;

      vPosition = localPosWithShock;
      vIsGold = aIsGold;
      vIsRed = aIsRed;
      vShockwaveColorFactor = shockwave;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
    }
  `,
  fragmentShader: `
    varying vec3 vPosition;
    varying float vIsGold;
    varying float vIsRed;
    varying float vShockwaveColorFactor;

    uniform float uShowEsotericFilters;
    uniform float uIsArcano78Active;

    void main() {
      // Forensic Neon palette styling: mix Matrix Green (#00FF66) with Astro Violet (#8A2BE2)
      vec3 matrixGreen = vec3(0.0, 1.0, 0.4);
      vec3 astroViolet = vec3(0.54, 0.17, 0.89);

      // Gradient based on coordinate depth
      float factor = clamp((vPosition.z + 8.0) / 16.0, 0.0, 1.0);
      vec3 finalColor = mix(matrixGreen, astroViolet, factor * 0.65);
      
      float finalAlpha = 0.9;

      if (uShowEsotericFilters > 0.5) {
        if (vIsRed > 0.5) {
          finalColor = vec3(1.0, 0.2, 0.2); // Red (#FF3333)
        } else if (vIsGold > 0.5) {
          finalColor = vec3(1.0, 0.84, 0.0); // Gold (#FFD700)
          if (uIsArcano78Active > 0.5) {
            finalColor += vec3(0.2, 0.15, 0.0); // Extra gold glow boost
            finalAlpha = 1.0;
          }
        }
      }

      // Blend color to shockwave Red on the wavefront path
      if (vShockwaveColorFactor > 0.05) {
        vec3 shockwaveColor = vec3(1.0, 0.1, 0.1); // Bright red (#FF1A1A)
        finalColor = mix(finalColor, shockwaveColor, vShockwaveColorFactor * 1.3);
        finalAlpha = mix(finalAlpha, 1.0, vShockwaveColorFactor);
      }

      // Glowing circular point look
      gl_FragColor = vec4(finalColor, finalAlpha);
    }
  `
};

export const SpatialRetina = () => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const groupRef = useRef<THREE.Group>(null);

  // Bind Zustand store weights and esoteric states
  const { frequency, deviation, cosmic, ml } = useResonanceStore((state) => state.weights);
  const isResonating = useResonanceStore((state) => state.isResonating);
  const particleCount = useResonanceStore((state) => state.particleCount);

  const personalProfile = useResonanceStore((state) => state.personalProfile);
  const arcanos = useResonanceStore((state) => state.arcanos);
  const negativeSequences = useResonanceStore((state) => state.negativeSequences);
  const currentArcano = useResonanceStore((state) => state.currentArcano);
  const lastMuonStrike = useResonanceStore((state) => state.lastMuonStrike);

  // Favorable and warning constant sets for Node Index Mapping
  const FAVORABLE_ARCANOS = useMemo(() => new Set([32, 64, 65, 69, 70, 78]), []);
  const WARNING_ARCANOS = useMemo(() => new Set([13, 14, 16]), []);

  // Shared line material for high-performance great circle interaction
  const lineMaterial = useMemo(() => new THREE.LineBasicMaterial({
    color: new THREE.Color('#8A2BE2'),
    linewidth: 2,
    transparent: true,
    opacity: 0.65
  }), []);

  // Continuous automatic rotation speed modifiers
  const rotationSpeeds = useRef({ x: 0.15, y: 0.3 });

  // Refs for tracking cosmic ray muon strikes shockwave animation
  const lastStrikeRef = useRef<string | null>(null);
  const strikeTimeRef = useRef<number>(0);
  const strikeOriginRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 0, 0));

  // 1. Fibonacci Sphere distribution for uniform node placement on the manifold
  const { geometry, phis, thetas } = useMemo(() => {
    // Low-poly base geometry for instances (box is extremely lightweight)
    const baseGeom = new THREE.BoxGeometry(0.1, 0.1, 0.1);
    const instGeom = new THREE.InstancedBufferGeometry().copy(baseGeom);

    const phiArray = new Float32Array(particleCount);
    const thetaArray = new Float32Array(particleCount);
    const isGoldArray = new Float32Array(particleCount);
    const isRedArray = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;
      phiArray[i] = phi;
      thetaArray[i] = theta;
    }

    instGeom.setAttribute('aPhi', new THREE.InstancedBufferAttribute(phiArray, 1));
    instGeom.setAttribute('aTheta', new THREE.InstancedBufferAttribute(thetaArray, 1));
    instGeom.setAttribute('aIsGold', new THREE.InstancedBufferAttribute(isGoldArray, 1));
    instGeom.setAttribute('aIsRed', new THREE.InstancedBufferAttribute(isRedArray, 1));

    return { geometry: instGeom, phis: phiArray, thetas: thetaArray };
  }, [particleCount]);

  // Update instanced attributes on store changes (High performance: zero recreate/re-render overhead)
  useEffect(() => {
    if (!geometry) return;

    const aIsGold = geometry.getAttribute('aIsGold') as THREE.InstancedBufferAttribute;
    const aIsRed = geometry.getAttribute('aIsRed') as THREE.InstancedBufferAttribute;
    if (!aIsGold || !aIsRed) return;

    const goldArray = aIsGold.array as Float32Array;
    const redArray = aIsRed.array as Float32Array;
    const hasFilters = !!personalProfile;

    const coreNumbers = personalProfile 
      ? new Set([
          personalProfile.motivation,
          personalProfile.impression,
          personalProfile.expression,
          personalProfile.destiny,
          personalProfile.mission
        ])
      : new Set<number>();

    const negSeqSet = new Set(negativeSequences || []);

    for (let i = 0; i < particleCount; i++) {
      if (!hasFilters) {
        goldArray[i] = 0.0;
        redArray[i] = 0.0;
        continue;
      }

      // Node Index Mapping Algorithm:
      // - Node index maps to a root vibration digit via (i % 9) + 1
      // - Node index maps to an Arcano coordinate via (i % 78) + 1
      const digit = (i % 9) + 1;
      const arcano = (i % 78) + 1;

      const isGold = FAVORABLE_ARCANOS.has(arcano) || coreNumbers.has(digit);
      const isRed = WARNING_ARCANOS.has(arcano) || negSeqSet.has(digit);

      goldArray[i] = isGold ? 1.0 : 0.0;
      redArray[i] = isRed ? 1.0 : 0.0;
    }

    aIsGold.needsUpdate = true;
    aIsRed.needsUpdate = true;
  }, [geometry, particleCount, personalProfile, negativeSequences, FAVORABLE_ARCANOS, WARNING_ARCANOS]);

  // 2. Geodesic Rings (Great Circles) in Astro Violet
  const ringGeometries = useMemo(() => {
    const rings = [];
    const segments = 100;

    // Define 3 orthocentric geodesic great circles
    const orientations = [
      { axisX: 1, axisY: 0, axisZ: 0 },
      { axisX: 0, axisY: 1, axisZ: 0 },
      { axisX: 0, axisY: 0, axisZ: 1 },
    ];

    for (const orient of orientations) {
      const positions = new Float32Array((segments + 1) * 3);
      for (let j = 0; j <= segments; j++) {
        // We preallocate space; coordinates will be computed in useFrame to bend with the weights
        positions[j * 3] = 0;
        positions[j * 3 + 1] = 0;
        positions[j * 3 + 2] = 0;
      }

      const geom = new THREE.BufferGeometry();
      geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      rings.push({ geom, orient });
    }

    return rings;
  }, []);

  // Update shader uniforms and handle interactive keyboard-based navigation (hjkl)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();
      if (key === 'h') {
        rotationSpeeds.current.y -= 0.15; // Pan/Rotate left
      } else if (key === 'l') {
        rotationSpeeds.current.y += 0.15; // Pan/Rotate right
      } else if (key === 'k') {
        rotationSpeeds.current.x -= 0.15; // Pan/Rotate up
      } else if (key === 'j') {
        rotationSpeeds.current.x += 0.15; // Pan/Rotate down
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    // 0. Cosmic Ray Muon Strike trigger check
    if (lastMuonStrike && lastMuonStrike.timestamp !== lastStrikeRef.current) {
      lastStrikeRef.current = lastMuonStrike.timestamp;
      strikeTimeRef.current = 0.001; // start shockwave delta timer

      // Resolve golden spiral coordinates on Fibonacci sphere matching mutated index
      const idx = lastMuonStrike.mutatedIndex % particleCount;
      const phi = Math.acos(-1 + (2 * idx) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;
      const R = 7.0; // base radius
      strikeOriginRef.current.set(
        R * Math.sin(phi) * Math.cos(theta),
        R * Math.sin(phi) * Math.sin(theta),
        R * Math.cos(phi)
      );
    }

    if (strikeTimeRef.current > 0.0) {
      strikeTimeRef.current += state.delta;
      if (strikeTimeRef.current > 1.5) {
        strikeTimeRef.current = 0.0; // end animation after 1.5s
      }
    }

    // 1. Sync shader uniforms
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = t;
      materialRef.current.uniforms.uFrequency.value = frequency;
      materialRef.current.uniforms.uDeviation.value = deviation;
      materialRef.current.uniforms.uCosmic.value = cosmic;
      materialRef.current.uniforms.uMl.value = ml;
      materialRef.current.uniforms.uResonating.value = isResonating ? 1.0 : 0.0;
      materialRef.current.uniforms.uActiveArcano.value = currentArcano || 0;
      materialRef.current.uniforms.uIsArcano78Active.value = currentArcano === 78 ? 1.0 : 0.0;
      materialRef.current.uniforms.uShowEsotericFilters.value = personalProfile ? 1.0 : 0.0;
      materialRef.current.uniforms.uMuonStrikeTime.value = strikeTimeRef.current;
      materialRef.current.uniforms.uMuonStrikeOrigin.value.copy(strikeOriginRef.current);
      materialRef.current.uniforms.uMuonStrikeActive.value = strikeTimeRef.current > 0.0 ? 1.0 : 0.0;
    }

    // 2. Slow spin with keyboard-induced inertia
    if (groupRef.current) {
      groupRef.current.rotation.y += state.delta * rotationSpeeds.current.y;
      groupRef.current.rotation.x += state.delta * rotationSpeeds.current.x;

      // Smooth decay of user input torque towards base automatic rotation
      rotationSpeeds.current.y += (0.2 - rotationSpeeds.current.y) * state.delta;
      rotationSpeeds.current.x += (0.08 - rotationSpeeds.current.x) * state.delta;
    }

    // 3. Dynamically deform Geodesic Great Circles on CPU to match shader coordinates
    const timeVal = isResonating ? t : 0.0;
    for (const ring of ringGeometries) {
      const attr = ring.geom.getAttribute('position') as THREE.BufferAttribute;
      const count = attr.count;
      const positions = attr.array as Float32Array;

      for (let j = 0; j < count; j++) {
        let phi = 0;
        let theta = 0;
        const angle = (j / (count - 1)) * Math.PI * 2;

        if (ring.orient.axisZ === 1) {
          phi = Math.PI / 2;
          theta = angle;
        } else if (ring.orient.axisY === 1) {
          phi = angle;
          theta = 0;
        } else {
          phi = angle;
          theta = Math.PI / 2;
        }

        // Apply curved Riemannian manifold metrics
        const R = 7.0 + 1.8 * (
          frequency * Math.sin(3.0 * phi + timeVal) * Math.cos(3.0 * theta) +
          deviation * Math.cos(5.0 * phi - timeVal) * Math.sin(2.0 * theta) +
          cosmic * Math.sin(7.0 * phi + 1.5 * timeVal) * Math.cos(theta) +
          ml * Math.cos(2.0 * phi) * Math.sin(5.0 * theta - 0.8 * timeVal)
        );

        positions[j * 3] = R * Math.sin(phi) * Math.cos(theta);
        positions[j * 3 + 1] = R * Math.sin(phi) * Math.sin(theta);
        positions[j * 3 + 2] = R * Math.cos(phi);
      }
      attr.needsUpdate = true;
    }

    // 4. Update great circle material appearance dynamically based on esoteric active Arcano
    if (lineMaterial) {
      if (personalProfile) {
        if (currentArcano === 78) {
          // Extra pulsing glow boost during Arcano 78: gold color pulsing
          lineMaterial.color.setHex(0xFFD700);
          lineMaterial.opacity = 0.92 + 0.08 * Math.sin(t * 12.0);
        } else if (currentArcano && FAVORABLE_ARCANOS.has(currentArcano)) {
          lineMaterial.color.setHex(0xFFD700); // Gold for favorable
          lineMaterial.opacity = 0.8;
        } else if (currentArcano && WARNING_ARCANOS.has(currentArcano)) {
          lineMaterial.color.setHex(0xFF3333); // Red for warning
          lineMaterial.opacity = 0.8;
        } else {
          lineMaterial.color.setHex(0x8A2BE2); // Standard Astro Violet when esoteric filter active but no active arcanum
          lineMaterial.opacity = 0.75;
        }
      } else {
        lineMaterial.color.setHex(0x8A2BE2); // Default Astro Violet
        lineMaterial.opacity = 0.65;
      }
    }
  });

  return (
    <group ref={groupRef}>
      {/* Dynamic 100k+ instanced point manifold */}
      <instancedMesh ref={meshRef} args={[geometry, null, particleCount]}>
        <shaderMaterial
          ref={materialRef}
          vertexShader={ManifoldShader.vertexShader}
          fragmentShader={ManifoldShader.fragmentShader}
          uniforms={ManifoldShader.uniforms}
          transparent={true}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </instancedMesh>

      {/* Geodesic rings outlining great circles on the manifold */}
      {ringGeometries.map((ring, idx) => (
        <lineLoop key={idx} geometry={ring.geom} material={lineMaterial} />
      ))}

      {/* OrbitControls for elegant touch/mouse navigation */}
      <OrbitControls enableZoom={true} enablePan={true} enableRotate={true} />
    </group>
  );
};
