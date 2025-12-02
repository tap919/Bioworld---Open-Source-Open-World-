/**
 * Bioworld Website - Learning Center JavaScript
 * Handles classroom management, lesson creation, and science demonstrations
 * 
 * Dependencies: main.js (provides showToast, formatDate utility functions)
 */

// ============================================================================
// Utility Functions (defined at top for clarity)
// ============================================================================

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text safe for HTML insertion
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadDemonstrations();
    
    // Set up event listeners
    setupEventListeners();
});

/**
 * Set up event listeners for the learning page
 */
function setupEventListeners() {
    // Teacher controls
    const createClassroomBtn = document.getElementById('create-classroom');
    if (createClassroomBtn) {
        createClassroomBtn.addEventListener('click', toggleClassroomForm);
    }

    const viewClassroomsBtn = document.getElementById('view-my-classrooms');
    if (viewClassroomsBtn) {
        viewClassroomsBtn.addEventListener('click', toggleMyClassrooms);
    }

    const submitClassroomBtn = document.getElementById('submit-classroom');
    if (submitClassroomBtn) {
        submitClassroomBtn.addEventListener('click', createClassroom);
    }

    // Student controls
    const joinClassroomBtn = document.getElementById('join-classroom');
    if (joinClassroomBtn) {
        joinClassroomBtn.addEventListener('click', joinClassroom);
    }

    const viewProgressBtn = document.getElementById('view-progress');
    if (viewProgressBtn) {
        viewProgressBtn.addEventListener('click', viewStudentProgress);
    }

    // Demo filters
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterDemonstrations(this.dataset.category);
        });
    });

    // Simulator controls
    const closeSimBtn = document.getElementById('close-simulator');
    if (closeSimBtn) {
        closeSimBtn.addEventListener('click', closeSimulator);
    }

    const runSimBtn = document.getElementById('run-simulation');
    if (runSimBtn) {
        runSimBtn.addEventListener('click', runSimulation);
    }

    // Lesson controls
    const createLessonBtn = document.getElementById('create-lesson');
    if (createLessonBtn) {
        createLessonBtn.addEventListener('click', createLesson);
    }

    const browseLessonsBtn = document.getElementById('browse-lessons');
    if (browseLessonsBtn) {
        browseLessonsBtn.addEventListener('click', browseLessons);
    }
}

// ============================================================================
// Classroom Management
// ============================================================================

function toggleClassroomForm() {
    const form = document.getElementById('classroom-form');
    if (form) {
        form.classList.toggle('hidden');
    }
}

function toggleMyClassrooms() {
    const container = document.getElementById('my-classrooms');
    if (container) {
        container.classList.toggle('hidden');
        if (!container.classList.contains('hidden')) {
            loadClassrooms();
        }
    }
}

async function loadClassrooms() {
    const container = document.getElementById('classrooms-container');
    if (!container) return;

    container.innerHTML = '<p class="loading">Loading classrooms...</p>';

    try {
        const response = await fetch('/api/classrooms');
        const data = await response.json();

        if (data.classrooms && data.classrooms.length > 0) {
            container.innerHTML = data.classrooms.map(classroom => `
                <div class="classroom-item">
                    <div class="classroom-header">
                        <h4>${escapeHtml(classroom.name)}</h4>
                        <span class="class-code">Code: ${escapeHtml(classroom.class_code)}</span>
                    </div>
                    <div class="classroom-meta">
                        <span>Subject: ${escapeHtml(classroom.subject)}</span> |
                        <span>Students: ${classroom.current_students}/${classroom.max_students}</span> |
                        <span>Status: ${classroom.is_active ? 'Active' : 'Inactive'}</span>
                    </div>
                    ${classroom.description ? `<p class="classroom-desc">${escapeHtml(classroom.description)}</p>` : ''}
                    <div class="classroom-actions">
                        <button class="btn btn-secondary view-details-btn" data-classroom-id="${escapeHtml(classroom.id)}">View Details</button>
                        <button class="btn btn-secondary copy-code-btn" data-class-code="${escapeHtml(classroom.class_code)}">Copy Code</button>
                    </div>
                </div>
            `).join('');

            // Add event listeners for classroom action buttons (avoiding inline handlers for XSS safety)
            container.querySelectorAll('.view-details-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    viewClassroomDetails(this.dataset.classroomId);
                });
            });
            container.querySelectorAll('.copy-code-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    copyClassCode(this.dataset.classCode);
                });
            });
        } else {
            container.innerHTML = '<p class="empty-message">No classrooms found. Create your first classroom!</p>';
        }
    } catch (error) {
        container.innerHTML = '<p class="error">Failed to load classrooms. API may be offline.</p>';
        console.error('Failed to load classrooms:', error);
    }
}

async function createClassroom() {
    const nameEl = document.getElementById('classroom-name');
    const teacherIdEl = document.getElementById('teacher-id');
    const subjectEl = document.getElementById('classroom-subject');
    const maxStudentsEl = document.getElementById('max-students');
    const descriptionEl = document.getElementById('classroom-description');

    const name = nameEl ? nameEl.value.trim() : '';
    const teacherId = teacherIdEl ? teacherIdEl.value.trim() : '';
    const subject = subjectEl ? subjectEl.value : '';
    const maxStudents = maxStudentsEl ? parseInt(maxStudentsEl.value) || 30 : 30;
    const description = descriptionEl ? descriptionEl.value.trim() : '';

    if (!name || !teacherId || !subject) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    try {
        const response = await fetch('/api/classrooms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                teacher_id: teacherId,
                subject: subject,
                max_students: maxStudents,
                description: description
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast(`Classroom created! Class code: ${data.class_code}`, 'success');
            // Clear form
            if (nameEl) nameEl.value = '';
            if (descriptionEl) descriptionEl.value = '';
            // Reload classrooms
            loadClassrooms();
            // Show classrooms section
            const container = document.getElementById('my-classrooms');
            if (container) container.classList.remove('hidden');
        } else {
            showToast(data.error || 'Failed to create classroom', 'error');
        }
    } catch (error) {
        showToast('Failed to create classroom', 'error');
        console.error('Create classroom error:', error);
    }
}

async function viewClassroomDetails(classroomId) {
    try {
        const response = await fetch(`/api/classrooms/${classroomId}`);
        const data = await response.json();

        if (response.ok) {
            // Show classroom details using a toast with detailed info (better than alert for accessibility)
            showClassroomModal(data);
        } else {
            showToast(data.error || 'Failed to load classroom details', 'error');
        }
    } catch (error) {
        showToast('Failed to load classroom details', 'error');
        console.error('View classroom error:', error);
    }
}

/**
 * Display classroom details in a modal dialog (more accessible than alert)
 */
function showClassroomModal(data) {
    // Create modal element if it doesn't exist
    let modal = document.getElementById('classroom-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'classroom-modal';
        modal.className = 'modal-overlay';
        document.body.appendChild(modal);
        
        // Add overlay click handler once (on the persistent modal element)
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${escapeHtml(data.name)}</h3>
                <button class="modal-close-btn" aria-label="Close modal">&times;</button>
            </div>
            <div class="modal-body">
                <p><strong>Class Code:</strong> <span class="class-code">${escapeHtml(data.class_code)}</span></p>
                <p><strong>Subject:</strong> ${escapeHtml(data.subject)}</p>
                <p><strong>Students:</strong> ${data.current_students}/${data.max_students}</p>
                <p><strong>Lessons:</strong> ${data.lessons ? data.lessons.length : 0}</p>
                ${data.description ? `<p><strong>Description:</strong> ${escapeHtml(data.description)}</p>` : ''}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary modal-close-btn">Close</button>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
    
    // Add event listeners for close buttons (fresh each time since innerHTML replaces content)
    modal.querySelectorAll('.modal-close-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    });
}

function copyClassCode(code) {
    navigator.clipboard.writeText(code).then(() => {
        showToast('Class code copied to clipboard!', 'success');
    }).catch((err) => {
        console.error('Clipboard error:', err);
        showToast('Failed to copy class code', 'error');
    });
}

// ============================================================================
// Student Functions
// ============================================================================

async function joinClassroom() {
    const classCodeEl = document.getElementById('join-class-code');
    const studentIdEl = document.getElementById('student-id');

    const classCode = classCodeEl ? classCodeEl.value.trim().toUpperCase() : '';
    const studentId = studentIdEl ? studentIdEl.value.trim() : '';

    if (!classCode || !studentId) {
        showToast('Please enter class code and student ID', 'error');
        return;
    }

    try {
        const response = await fetch('/api/classrooms/join', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                class_code: classCode,
                student_id: studentId
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast(`Successfully joined ${data.classroom_name}!`, 'success');
            if (classCodeEl) classCodeEl.value = '';
        } else {
            showToast(data.error || 'Failed to join classroom', 'error');
        }
    } catch (error) {
        showToast('Failed to join classroom', 'error');
        console.error('Join classroom error:', error);
    }
}

async function viewStudentProgress() {
    const studentIdEl = document.getElementById('progress-student-id');
    const container = document.getElementById('progress-container');

    const studentId = studentIdEl ? studentIdEl.value.trim() : '';

    if (!studentId) {
        showToast('Please enter your student ID', 'error');
        return;
    }

    if (container) {
        container.classList.remove('hidden');
        container.innerHTML = '<p class="loading">Loading progress...</p>';
    }

    try {
        const response = await fetch(`/api/students/${studentId}/progress`);
        const data = await response.json();

        if (response.ok && container) {
            if (data.progress && data.progress.length > 0) {
                container.innerHTML = `
                    <div class="progress-summary">
                        <h4>Progress Summary</h4>
                        <p>Total lessons: ${data.progress.length}</p>
                        <p>Completed: ${data.progress.filter(p => p.status === 'completed').length}</p>
                    </div>
                    <div class="progress-list">
                        ${data.progress.map(p => `
                            <div class="progress-item ${p.status}">
                                <h5>${escapeHtml(p.lesson_title)}</h5>
                                <div class="progress-meta">
                                    <span>Subject: ${escapeHtml(p.subject_area)}</span> |
                                    <span>Status: ${escapeHtml(p.status)}</span>
                                    ${p.score !== null ? `| <span>Score: ${p.score}%</span>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                container.innerHTML = '<p class="empty-message">No progress recorded yet. Join a classroom and start learning!</p>';
            }
        }
    } catch (error) {
        if (container) {
            container.innerHTML = '<p class="error">Failed to load progress. API may be offline.</p>';
        }
        console.error('View progress error:', error);
    }
}

// ============================================================================
// Science Demonstrations
// ============================================================================

let currentDemonstrations = [];
let selectedDemo = null;

async function loadDemonstrations(category = null) {
    const container = document.getElementById('demonstrations-list');
    if (!container) return;

    container.innerHTML = '<p class="loading">Loading demonstrations...</p>';

    try {
        let url = '/api/demonstrations';
        if (category && category !== 'all') {
            url += `?category=${category}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        currentDemonstrations = data.demonstrations || [];
        renderDemonstrations(currentDemonstrations);
    } catch (error) {
        container.innerHTML = '<p class="error">Failed to load demonstrations. API may be offline.</p>';
        console.error('Load demonstrations error:', error);
    }
}

function filterDemonstrations(category) {
    if (category === 'all') {
        loadDemonstrations();
    } else {
        loadDemonstrations(category);
    }
}

function renderDemonstrations(demonstrations) {
    const container = document.getElementById('demonstrations-list');
    if (!container) return;

    if (demonstrations.length > 0) {
        container.innerHTML = demonstrations.map(demo => `
            <div class="demo-card" data-id="${escapeHtml(demo.id)}">
                <div class="demo-icon">${getCategoryIcon(demo.category)}</div>
                <div class="demo-content">
                    <h4>${escapeHtml(demo.name)}</h4>
                    <span class="demo-category">${escapeHtml(demo.category)}</span>
                    <p>${escapeHtml(demo.description || 'Interactive science demonstration')}</p>
                </div>
                <button class="btn btn-primary launch-demo-btn" data-demo-id="${escapeHtml(demo.id)}">Launch Demo</button>
            </div>
        `).join('');

        // Add event listeners for demo launch buttons (avoiding inline handlers for XSS safety)
        container.querySelectorAll('.launch-demo-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                openSimulator(this.dataset.demoId);
            });
        });
    } else {
        container.innerHTML = '<p class="empty-message">No demonstrations found.</p>';
    }
}

function getCategoryIcon(category) {
    const icons = {
        'chemistry': '⚗️',
        'physics': '⚡',
        'biology': '🧬',
        'earth_science': '🌍',
        'default': '🔬'
    };
    return icons[category] || icons.default;
}

function openSimulator(demoId) {
    selectedDemo = currentDemonstrations.find(d => d.id === demoId);
    if (!selectedDemo) return;

    const section = document.getElementById('simulator-section');
    const nameEl = document.getElementById('sim-demo-name');
    const vizEl = document.getElementById('sim-visualization');
    const paramsEl = document.getElementById('sim-parameters');
    const eduNotesEl = document.getElementById('sim-educational-notes');
    const safetyNotesEl = document.getElementById('sim-safety-notes');

    if (section) section.classList.remove('hidden');
    if (nameEl) nameEl.textContent = selectedDemo.name;
    if (eduNotesEl) eduNotesEl.textContent = selectedDemo.educational_notes || 'No notes available';
    if (safetyNotesEl) safetyNotesEl.textContent = selectedDemo.safety_notes || 'None';
    if (vizEl) vizEl.innerHTML = '<p>Click "Run Simulation" to start the demonstration</p>';

    // Build parameters form based on demo type
    if (paramsEl) {
        paramsEl.innerHTML = buildParameterForm(selectedDemo);
    }

    // Scroll to simulator
    section.scrollIntoView({ behavior: 'smooth' });
}

function buildParameterForm(demo) {
    const params = demo.parameters || {};
    let html = '';

    if (demo.visualization_type === 'combustion') {
        html = `
            <label>Fuel Type:</label>
            <select id="param-fuel">
                <option value="methane" ${params.fuel === 'methane' ? 'selected' : ''}>Methane (CH4)</option>
                <option value="propane" ${params.fuel === 'propane' ? 'selected' : ''}>Propane (C3H8)</option>
                <option value="wood" ${params.fuel === 'wood' ? 'selected' : ''}>Wood (Cellulose)</option>
                <option value="hydrogen" ${params.fuel === 'hydrogen' ? 'selected' : ''}>Hydrogen (H2)</option>
            </select>
            <label>Initial Temperature (°C):</label>
            <input type="number" id="param-temperature" value="${params.initial_temperature || 25}" min="0" max="100" />
        `;
    } else if (demo.visualization_type === 'molecular_structure') {
        html = `
            <label>Molecule:</label>
            <select id="param-molecule">
                <option value="H2O" ${params.molecule === 'H2O' ? 'selected' : ''}>Water (H2O)</option>
                <option value="CO2" ${params.molecule === 'CO2' ? 'selected' : ''}>Carbon Dioxide (CO2)</option>
                <option value="CH4" ${params.molecule === 'CH4' ? 'selected' : ''}>Methane (CH4)</option>
            </select>
        `;
    } else if (demo.visualization_type === 'particle') {
        html = `
            <label>Particle Count:</label>
            <input type="number" id="param-particle-count" value="${params.particle_count || 50}" min="10" max="100" />
            <label>Temperature (K):</label>
            <input type="number" id="param-temp-k" value="${params.temperature || 300}" min="100" max="1000" />
        `;
    } else if (demo.visualization_type === 'cell_division') {
        html = `
            <label>Division Type:</label>
            <select id="param-division">
                <option value="mitosis" ${params.division_type === 'mitosis' ? 'selected' : ''}>Mitosis</option>
                <option value="meiosis" ${params.division_type === 'meiosis' ? 'selected' : ''}>Meiosis</option>
            </select>
        `;
    } else {
        html = '<p>No adjustable parameters for this demonstration</p>';
    }

    return html;
}

function closeSimulator() {
    const section = document.getElementById('simulator-section');
    if (section) section.classList.add('hidden');
    selectedDemo = null;
}

async function runSimulation() {
    if (!selectedDemo) {
        showToast('Please select a demonstration first', 'error');
        return;
    }

    const vizEl = document.getElementById('sim-visualization');
    if (vizEl) vizEl.innerHTML = '<p class="loading">Running simulation...</p>';

    // Collect simulation parameters from form inputs
    const customParams = collectSimulationParameters();

    try {
        const response = await fetch(`/api/demonstrations/${selectedDemo.id}/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ custom_parameters: customParams })
        });

        const data = await response.json();

        if (response.ok && vizEl) {
            renderSimulationResult(data, vizEl);
        } else {
            vizEl.innerHTML = `<p class="error">Simulation failed: ${data.error || 'Unknown error'}</p>`;
        }
    } catch (error) {
        if (vizEl) vizEl.innerHTML = '<p class="error">Simulation failed. API may be offline.</p>';
        console.error('Simulation error:', error);
    }
}

/**
 * Collect simulation input values from DOM form elements
 */
function collectSimulationParameters() {
    const params = {};

    // Combustion params
    const fuelEl = document.getElementById('param-fuel');
    if (fuelEl) params.fuel = fuelEl.value;

    const tempEl = document.getElementById('param-temperature');
    if (tempEl) params.initial_temperature = parseFloat(tempEl.value);

    // Molecular params
    const moleculeEl = document.getElementById('param-molecule');
    if (moleculeEl) params.molecule = moleculeEl.value;

    // Particle params - particle count should be integer, temperature can be decimal
    const particleEl = document.getElementById('param-particle-count');
    if (particleEl) params.particle_count = parseInt(particleEl.value);

    const tempKEl = document.getElementById('param-temp-k');
    if (tempKEl) params.temperature = parseFloat(tempKEl.value);

    // Cell division params
    const divisionEl = document.getElementById('param-division');
    if (divisionEl) params.division_type = divisionEl.value;

    return params;
}

function renderSimulationResult(data, container) {
    const result = data.simulation_result;
    let html = `<div class="simulation-result">`;

    if (result.type === 'combustion') {
        html += `
            <h4>🔥 Combustion Simulation</h4>
            <div class="result-grid">
                <div class="result-item">
                    <label>Fuel:</label>
                    <span>${escapeHtml(result.fuel)}</span>
                </div>
                <div class="result-item">
                    <label>Chemical Equation:</label>
                    <span class="equation">${escapeHtml(result.chemical_equation)}</span>
                </div>
                <div class="result-item">
                    <label>Energy Released:</label>
                    <span>${result.energy_released_kj} kJ/mol</span>
                </div>
                <div class="result-item">
                    <label>Flame Color:</label>
                    <span class="flame-color" style="color: ${getFlameColor(result.flame_color)}">${escapeHtml(result.flame_color)}</span>
                </div>
                <div class="result-item">
                    <label>Temperature Change:</label>
                    <span>${result.initial_temperature_c}°C → ${result.final_temperature_c}°C</span>
                </div>
                <div class="result-item">
                    <label>Products:</label>
                    <span>${result.products.join(' + ')}</span>
                </div>
            </div>
            <div class="learning-points">
                <h5>Key Learning Points:</h5>
                <ul>
                    ${result.learning_points.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
                </ul>
            </div>
            <div class="flame-animation">
                ${renderFlameAnimation(result.visualization_frames)}
            </div>
        `;
    } else if (result.type === 'molecular_structure') {
        html += `
            <h4>🔬 Molecular Structure: ${escapeHtml(result.molecule)}</h4>
            <div class="molecule-view">
                <p>Bond Angle: ${result.structure.angle}°</p>
                <div class="atom-list">
                    ${result.structure.atoms.map(a => `
                        <span class="atom atom-${a.type}">${a.type}</span>
                    `).join('')}
                </div>
            </div>
        `;
    } else if (result.type === 'cell_division') {
        html += `
            <h4>🧬 ${escapeHtml(result.division_type.charAt(0).toUpperCase() + result.division_type.slice(1))}</h4>
            <div class="phases-list">
                ${result.phases.map((phase, i) => `
                    <div class="phase-item">
                        <span class="phase-number">${i + 1}</span>
                        <div class="phase-content">
                            <strong>${escapeHtml(phase.name)}</strong>
                            <p>${escapeHtml(phase.description)}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
            <p class="result-note">Result: ${result.result_cells} cells with ${result.chromosome_count} chromosomes each</p>
        `;
    } else if (result.type === 'dna_replication') {
        html += `
            <h4>🧬 DNA Replication</h4>
            <div class="steps-list">
                ${result.steps.map((step, i) => `
                    <div class="step-item">
                        <span class="step-number">${i + 1}</span>
                        <div class="step-content">
                            <strong>${escapeHtml(step.name)}</strong>
                            <p>${escapeHtml(step.action)}</p>
                        </div>
                    </div>
                `).join('')}
            </div>
            <p class="result-note">Direction: ${escapeHtml(result.direction)}</p>
        `;
    } else if (result.type === 'particle_motion') {
        html += `
            <h4>⚡ Gas Particle Motion</h4>
            <div class="result-grid">
                <div class="result-item">
                    <label>Particles:</label>
                    <span>${result.particle_count}</span>
                </div>
                <div class="result-item">
                    <label>Temperature:</label>
                    <span>${result.temperature_k} K</span>
                </div>
                <div class="result-item">
                    <label>Average Velocity:</label>
                    <span>${result.average_velocity.toExponential(2)} m/s</span>
                </div>
            </div>
            <div class="particle-canvas" id="particle-canvas">
                ${renderParticleVisualization(result.particles)}
            </div>
        `;
    } else {
        // Generic result display
        html += `
            <h4>Simulation Complete</h4>
            <pre>${JSON.stringify(result, null, 2)}</pre>
        `;
    }

    html += `</div>`;
    container.innerHTML = html;
}

function getFlameColor(colorName) {
    const colors = {
        'blue': '#1E90FF',
        'blue-yellow': '#FFD700',
        'orange-yellow': '#FFA500',
        'pale-blue': '#ADD8E6',
        'yellow': '#FFFF00'
    };
    return colors[colorName] || '#FF6600';
}

function renderFlameAnimation(frames) {
    if (!frames || frames.length === 0) return '';
    
    return `
        <div class="flame-frames">
            ${frames.map(f => `
                <div class="flame-frame" style="opacity: ${f.flame_intensity}; background: ${getFlameColor(f.color)}">
                    🔥
                </div>
            `).join('')}
        </div>
    `;
}

function renderParticleVisualization(particles) {
    if (!particles || particles.length === 0) return '<p>No particles to display</p>';
    
    // Limit to 50 particles for SVG rendering performance
    const MAX_SVG_PARTICLES = 50;
    return `
        <svg viewBox="0 0 100 100" class="particle-svg">
            ${particles.slice(0, MAX_SVG_PARTICLES).map(p => `
                <circle cx="${p.x * 100}" cy="${p.y * 100}" r="2" fill="#00BFFF" />
            `).join('')}
        </svg>
    `;
}

// ============================================================================
// Lesson Management
// ============================================================================

async function createLesson() {
    const classroomIdEl = document.getElementById('lesson-classroom-id');
    const titleEl = document.getElementById('lesson-title');
    const subjectEl = document.getElementById('lesson-subject');
    const descriptionEl = document.getElementById('lesson-description');
    const durationEl = document.getElementById('lesson-duration');
    const objectivesEl = document.getElementById('lesson-objectives');
    const materialsEl = document.getElementById('lesson-materials');

    const classroomId = classroomIdEl ? classroomIdEl.value.trim() : '';
    const title = titleEl ? titleEl.value.trim() : '';
    const subject = subjectEl ? subjectEl.value : '';
    const description = descriptionEl ? descriptionEl.value.trim() : '';
    const duration = durationEl ? parseInt(durationEl.value) || 45 : 45;
    const objectives = objectivesEl ? objectivesEl.value.split('\n').filter(o => o.trim()) : [];
    const materials = materialsEl ? materialsEl.value.split('\n').filter(m => m.trim()) : [];

    if (!classroomId || !title || !subject) {
        showToast('Please fill in classroom ID, title, and subject', 'error');
        return;
    }

    try {
        const response = await fetch('/api/lessons', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                classroom_id: classroomId,
                title: title,
                subject_area: subject,
                description: description,
                estimated_duration: duration,
                objectives: objectives,
                materials: materials
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Lesson created successfully!', 'success');
            // Clear form
            if (titleEl) titleEl.value = '';
            if (descriptionEl) descriptionEl.value = '';
            if (objectivesEl) objectivesEl.value = '';
            if (materialsEl) materialsEl.value = '';
        } else {
            showToast(data.error || 'Failed to create lesson', 'error');
        }
    } catch (error) {
        showToast('Failed to create lesson', 'error');
        console.error('Create lesson error:', error);
    }
}

async function browseLessons() {
    const classroomIdEl = document.getElementById('browse-classroom-id');
    const container = document.getElementById('lessons-container');

    const classroomId = classroomIdEl ? classroomIdEl.value.trim() : '';

    if (!classroomId) {
        showToast('Please enter a classroom ID', 'error');
        return;
    }

    if (container) {
        container.classList.remove('hidden');
        container.innerHTML = '<p class="loading">Loading lessons...</p>';
    }

    try {
        const response = await fetch(`/api/lessons?classroom_id=${encodeURIComponent(classroomId)}`);
        const data = await response.json();

        if (response.ok && container) {
            if (data.lessons && data.lessons.length > 0) {
                container.innerHTML = data.lessons.map(lesson => `
                    <div class="lesson-item">
                        <div class="lesson-header">
                            <h4>${escapeHtml(lesson.title)}</h4>
                            <span class="lesson-order">Lesson ${lesson.lesson_order}</span>
                        </div>
                        <div class="lesson-meta">
                            <span>Subject: ${escapeHtml(lesson.subject_area)}</span> |
                            <span>Duration: ${lesson.estimated_duration} min</span>
                        </div>
                        ${lesson.description ? `<p class="lesson-desc">${escapeHtml(lesson.description)}</p>` : ''}
                        ${lesson.objectives && lesson.objectives.length > 0 ? `
                            <div class="lesson-objectives">
                                <strong>Objectives:</strong>
                                <ul>
                                    ${lesson.objectives.map(o => `<li>${escapeHtml(o)}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        <button class="btn btn-secondary start-lesson-btn" data-lesson-id="${escapeHtml(lesson.id)}">Start Lesson</button>
                    </div>
                `).join('');

                // Add event listeners for start lesson buttons (avoiding inline handlers for XSS safety)
                container.querySelectorAll('.start-lesson-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        startLesson(this.dataset.lessonId);
                    });
                });
            } else {
                container.innerHTML = '<p class="empty-message">No lessons found for this classroom.</p>';
            }
        }
    } catch (error) {
        if (container) {
            container.innerHTML = '<p class="error">Failed to load lessons. API may be offline.</p>';
        }
        console.error('Browse lessons error:', error);
    }
}

function startLesson(lessonId) {
    showToast('Lesson started! In the full game, this would launch the in-game lesson experience.', 'info');
    // In a full implementation, this would communicate with the game client
}
