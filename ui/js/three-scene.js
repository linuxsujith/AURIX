/**
 * AURIX — Three.js Background Scene
 * Animated particle field with connecting lines
 */

(function() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x030a1a, 1);

    camera.position.z = 30;

    // --- Particle System ---
    const PARTICLE_COUNT = 200;
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const velocities = [];
    const spread = 50;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        positions[i * 3] = (Math.random() - 0.5) * spread;
        positions[i * 3 + 1] = (Math.random() - 0.5) * spread;
        positions[i * 3 + 2] = (Math.random() - 0.5) * spread;
        velocities.push({
            x: (Math.random() - 0.5) * 0.02,
            y: (Math.random() - 0.5) * 0.02,
            z: (Math.random() - 0.5) * 0.02,
        });
    }

    const particleGeometry = new THREE.BufferGeometry();
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const particleMaterial = new THREE.PointsMaterial({
        color: 0x00d4ff,
        size: 0.15,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending,
        sizeAttenuation: true,
    });

    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    // --- Connection Lines ---
    const lineGeometry = new THREE.BufferGeometry();
    const MAX_LINES = 300;
    const linePositions = new Float32Array(MAX_LINES * 6);
    lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));

    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x00d4ff,
        transparent: true,
        opacity: 0.08,
        blending: THREE.AdditiveBlending,
    });

    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    // --- Hexagonal Grid (far background) ---
    const gridGeometry = new THREE.BufferGeometry();
    const gridPositions = [];
    const gridSize = 40;
    const hexSpacing = 4;

    for (let x = -gridSize; x <= gridSize; x += hexSpacing) {
        for (let y = -gridSize; y <= gridSize; y += hexSpacing) {
            const offset = (Math.floor(y / hexSpacing) % 2) * (hexSpacing / 2);
            gridPositions.push(x + offset, y, -20);
        }
    }

    gridGeometry.setAttribute('position', new THREE.Float32BufferAttribute(gridPositions, 3));

    const gridMaterial = new THREE.PointsMaterial({
        color: 0x00d4ff,
        size: 0.05,
        transparent: true,
        opacity: 0.15,
    });

    const grid = new THREE.Points(gridGeometry, gridMaterial);
    scene.add(grid);

    // --- Animation Loop ---
    let mouseX = 0, mouseY = 0;
    let frame = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
        mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    function animate() {
        requestAnimationFrame(animate);
        frame++;

        // Update particles
        const posArray = particles.geometry.attributes.position.array;
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            posArray[i * 3] += velocities[i].x;
            posArray[i * 3 + 1] += velocities[i].y;
            posArray[i * 3 + 2] += velocities[i].z;

            // Boundary wrapping
            for (let j = 0; j < 3; j++) {
                if (posArray[i * 3 + j] > spread / 2) posArray[i * 3 + j] = -spread / 2;
                if (posArray[i * 3 + j] < -spread / 2) posArray[i * 3 + j] = spread / 2;
            }
        }
        particles.geometry.attributes.position.needsUpdate = true;

        // Update connection lines
        let lineIndex = 0;
        const linePos = lines.geometry.attributes.position.array;
        const connectDist = 8;

        for (let i = 0; i < PARTICLE_COUNT && lineIndex < MAX_LINES * 6; i++) {
            for (let j = i + 1; j < PARTICLE_COUNT && lineIndex < MAX_LINES * 6; j++) {
                const dx = posArray[i * 3] - posArray[j * 3];
                const dy = posArray[i * 3 + 1] - posArray[j * 3 + 1];
                const dz = posArray[i * 3 + 2] - posArray[j * 3 + 2];
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

                if (dist < connectDist) {
                    linePos[lineIndex++] = posArray[i * 3];
                    linePos[lineIndex++] = posArray[i * 3 + 1];
                    linePos[lineIndex++] = posArray[i * 3 + 2];
                    linePos[lineIndex++] = posArray[j * 3];
                    linePos[lineIndex++] = posArray[j * 3 + 1];
                    linePos[lineIndex++] = posArray[j * 3 + 2];
                }
            }
        }

        // Clear remaining lines
        for (let i = lineIndex; i < MAX_LINES * 6; i++) {
            linePos[i] = 0;
        }
        lines.geometry.attributes.position.needsUpdate = true;

        // Camera follows mouse subtly
        camera.position.x += (mouseX * 3 - camera.position.x) * 0.02;
        camera.position.y += (-mouseY * 3 - camera.position.y) * 0.02;
        camera.lookAt(scene.position);

        // Slow rotation
        particles.rotation.y += 0.0003;
        grid.rotation.z += 0.0001;

        renderer.render(scene, camera);
    }

    animate();

    // Handle resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
})();
