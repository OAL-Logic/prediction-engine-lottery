import { Scene, PerspectiveCamera, DodecahedronGeometry, EdgesGeometry, LineSegments, LineBasicMaterial, Group, Points, PointsMaterial, BufferGeometry, Float32BufferAttribute } from "three";
import { ThreeRenderable, type ThreeRenderableOptions } from "@opentui/three";
import { type RenderContext } from "@opentui/core";

export class SpatialRetina extends ThreeRenderable {
  private group: Group;

  constructor(ctx: RenderContext) {
    const scene = new Scene();
    const camera = new PerspectiveCamera(75, 1.0, 0.1, 1000);
    camera.position.z = 15;

    const options: ThreeRenderableOptions = {
      scene,
      camera,
      flexGrow: 1,
    };

    super(ctx, options);

    this.group = new Group();
    scene.add(this.group);

    // 1. Dodecahedron Wireframe
    const geometry = new DodecahedronGeometry(8);
    const edges = new EdgesGeometry(geometry);
    const material = new LineBasicMaterial({ color: 0x00FF41, transparent: true, opacity: 0.3 });
    const wireframe = new LineSegments(edges, material);
    this.group.add(wireframe);

    // 2. Nodes
    const nodeGeometry = new BufferGeometry();
    const positions: number[] = [];
    for (let i = 0; i < 60; i++) {
      const phi = Math.acos(-1 + (2 * i) / 60);
      const theta = Math.sqrt(60 * Math.PI) * phi;
      const radius = 8.5;
      positions.push(
        radius * Math.cos(theta) * Math.sin(phi),
        radius * Math.sin(theta) * Math.sin(phi),
        radius * Math.cos(phi)
      );
    }
    nodeGeometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
    
    const nodeMaterial = new PointsMaterial({ 
      color: 0x00FF41, 
      size: 0.5,
      transparent: true,
      opacity: 0.8
    });
    const nodes = new Points(nodeGeometry, nodeMaterial);
    this.group.add(nodes);
  }

  protected onUpdate(deltaTime: number): void {
    super.onUpdate(deltaTime);
    if (this.group) {
      this.group.rotation.y += deltaTime * 0.5;
      this.group.rotation.x += deltaTime * 0.2;
    }
  }
}
