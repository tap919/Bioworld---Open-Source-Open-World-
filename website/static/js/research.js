/**
 * Bioworld Website - Research Page JavaScript
 * Handles protein folding, design, research packets, simulation adapters, and AI analysis
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadResearchPackets();
    loadSimAdapters();
    loadProteins();

    // Set up event listeners
    setupEventListeners();
});

/**
 * Set up event listeners for the research page
 */
function setupEventListeners() {
    // Refresh packets button
    const refreshBtn = document.getElementById('refresh-packets');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadResearchPackets);
    }

    // Create packet button
    const createBtn = document.getElementById('create-packet');
    if (createBtn) {
        createBtn.addEventListener('click', showCreatePacketModal);
    }

    // Run analysis button
    const analyzeBtn = document.getElementById('run-analysis');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', runAnalysis);
    }

    // Protein folding prediction
    const predictBtn = document.getElementById('predict-structure');
    if (predictBtn) {
        predictBtn.addEventListener('click', predictProteinStructure);
    }

    // Protein design
    const designBtn = document.getElementById('design-protein');
    if (designBtn) {
        designBtn.addEventListener('click', designProtein);
    }
}

/**
 * Predict protein structure from amino acid sequence
 */
async function predictProteinStructure() {
    const nameEl = document.getElementById('protein-name');
    const sequenceEl = document.getElementById('amino-sequence');
    const playerIdEl = document.getElementById('player-id');
    const resultEl = document.getElementById('protein-result');

    if (!nameEl || !sequenceEl || !resultEl) return;

    const name = nameEl.value.trim();
    const sequence = sequenceEl.value.trim().toUpperCase();
    const playerId = playerIdEl ? playerIdEl.value.trim() : 'anonymous';

    if (!name || !sequence) {
        showToast('Please enter protein name and amino acid sequence', 'error');
        return;
    }

    // Validate sequence
    const validAminoAcids = new Set('ACDEFGHIKLMNPQRSTVWY');
    for (const aa of sequence) {
        if (!validAminoAcids.has(aa)) {
            showToast(`Invalid amino acid: ${aa}. Valid amino acids: ${[...validAminoAcids].join('')}`, 'error');
            return;
        }
    }

    resultEl.classList.remove('hidden');
    resultEl.innerHTML = '<p class="loading">Predicting protein structure using AlphaFold-inspired AI...</p>';

    try {
        const response = await fetch('/api/proteins', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                amino_acid_sequence: sequence,
                player_id: playerId
            })
        });

        const data = await response.json();

        if (response.ok) {
            resultEl.innerHTML = `
                <h4>✅ Structure Predicted Successfully</h4>
                <div class="result-details">
                    <p><strong>Protein ID:</strong> ${escapeHtml(data.id)}</p>
                    <p><strong>Confidence Score:</strong> ${(data.confidence_score * 100).toFixed(1)}%</p>
                    <p><strong>Validation Required:</strong> ${data.validation_required ? 'Yes - Schedule wet lab validation' : 'No - High confidence'}</p>
                </div>
                ${data.validation_required ? `
                    <button class="btn btn-secondary" onclick="validateProtein('${data.id}')">Run Wet Lab Validation</button>
                ` : ''}
            `;
            showToast('Protein structure predicted!', 'success');
            loadProteins();
        } else {
            resultEl.innerHTML = `<p class="error">Error: ${escapeHtml(data.error)}</p>`;
        }
    } catch (error) {
        resultEl.innerHTML = '<p class="error">Failed to predict structure. API may be offline.</p>';
        console.error('Prediction failed:', error);
    }
}

/**
 * Validate a protein prediction with wet lab simulation
 */
async function validateProtein(proteinId) {
    try {
        const response = await fetch(`/api/proteins/${proteinId}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.validation_result === 'success') {
            showToast('Wet lab validation successful! Structure confirmed.', 'success');
        } else {
            showToast('Validation failed - consider redesigning the protein.', 'error');
        }
        loadProteins();
    } catch (error) {
        showToast('Validation request failed', 'error');
        console.error('Validation failed:', error);
    }
}

/**
 * Design a new protein using generative AI
 */
async function designProtein() {
    const purposeEl = document.getElementById('design-purpose');
    const lengthEl = document.getElementById('design-length');
    const resultEl = document.getElementById('design-result');

    if (!purposeEl || !resultEl) return;

    const purpose = purposeEl.value;
    const length = lengthEl ? parseInt(lengthEl.value) || 200 : 200;

    if (!purpose) {
        showToast('Please select a design purpose', 'error');
        return;
    }

    resultEl.classList.remove('hidden');
    resultEl.innerHTML = '<p class="loading">Designing protein using RF Diffusion-inspired AI...</p>';

    try {
        const response = await fetch('/api/proteins/design', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                purpose: purpose,
                constraints: { length: length }
            })
        });

        const data = await response.json();

        if (response.ok) {
            resultEl.innerHTML = `
                <h4>🧬 Protein Designed Successfully</h4>
                <div class="result-details">
                    <p><strong>Design ID:</strong> ${escapeHtml(data.id)}</p>
                    <p><strong>Purpose:</strong> ${escapeHtml(data.purpose)}</p>
                    <p><strong>Sequence Length:</strong> ${data.sequence_length} amino acids</p>
                    <p><strong>Estimated Stability:</strong> ${(data.estimated_stability * 100).toFixed(1)}%</p>
                    <p><strong>Design Model:</strong> ${escapeHtml(data.design_model)}</p>
                </div>
                <div class="sequence-display">
                    <h5>Designed Sequence:</h5>
                    <code>${escapeHtml(data.designed_sequence)}</code>
                </div>
                <div class="applications">
                    <h5>Suggested Applications:</h5>
                    <ul>
                        ${data.suggested_applications.map(app => `<li>${escapeHtml(app)}</li>`).join('')}
                    </ul>
                </div>
            `;
            showToast('Protein designed successfully!', 'success');
        } else {
            resultEl.innerHTML = `<p class="error">Error: ${escapeHtml(data.error)}</p>`;
        }
    } catch (error) {
        resultEl.innerHTML = '<p class="error">Failed to design protein. API may be offline.</p>';
        console.error('Design failed:', error);
    }
}

/**
 * Load discovered proteins
 */
async function loadProteins() {
    const container = document.getElementById('proteins-list');
    if (!container) return;

    container.innerHTML = '<p class="loading">Loading proteins...</p>';

    try {
        const response = await fetch('/api/proteins');
        const data = await response.json();

        if (data.proteins && data.proteins.length > 0) {
            container.innerHTML = data.proteins.map(protein => `
                <div class="protein-item">
                    <h4>${escapeHtml(protein.name)}</h4>
                    <div class="protein-meta">
                        <span>ID: ${escapeHtml(protein.id)}</span> |
                        <span>Length: ${protein.amino_acid_sequence.length} aa</span> |
                        <span>Confidence: ${(protein.confidence_score * 100).toFixed(1)}%</span> |
                        <span class="status-${protein.validation_status}">${escapeHtml(protein.validation_status)}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="empty-message">No proteins discovered yet. Start predicting!</p>';
        }
    } catch (error) {
        container.innerHTML = '<p class="empty-message">Failed to load proteins. API may be offline.</p>';
        console.error('Failed to load proteins:', error);
    }
}

/**
 * Load research packets from the API
 */
async function loadResearchPackets() {
    const container = document.getElementById('packets-list');
    if (!container) return;

    container.innerHTML = '<p class="loading">Loading research packets...</p>';

    try {
        const response = await fetch('/api/research-packets');
        const data = await response.json();

        if (data.packets && data.packets.length > 0) {
            container.innerHTML = data.packets.map(packet => `
                <div class="packet-item">
                    <h4>${escapeHtml(packet.title)}</h4>
                    <div class="packet-meta">
                        <span>ID: ${escapeHtml(packet.id)}</span> |
                        <span>Authors: ${escapeHtml(packet.authors || 'Unknown')}</span> |
                        <span>License: ${escapeHtml(packet.license || 'N/A')}</span> |
                        <span>Created: ${formatDate(packet.created_at)}</span>
                    </div>
                    ${packet.tags && packet.tags.length > 0 ? `
                        <div class="packet-tags">
                            ${packet.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="empty-message">No research packets found. Create your first packet!</p>';
        }
    } catch (error) {
        container.innerHTML = '<p class="empty-message">Failed to load research packets. API may be offline.</p>';
        console.error('Failed to load research packets:', error);
    }
}

/**
 * Load simulation adapters from the API
 */
async function loadSimAdapters() {
    const container = document.getElementById('adapters-list');
    if (!container) return;

    container.innerHTML = '<p class="loading">Loading simulation adapters...</p>';

    try {
        const response = await fetch('/api/sim-adapters');
        const data = await response.json();

        if (data.adapters && data.adapters.length > 0) {
            container.innerHTML = data.adapters.map(adapter => `
                <div class="adapter-item">
                    <h4>${escapeHtml(adapter.name)} <small>v${escapeHtml(adapter.version || '1.0.0')}</small></h4>
                    <div class="adapter-meta">
                        <span>ID: ${escapeHtml(adapter.id)}</span> |
                        <span>Entrypoint: ${escapeHtml(adapter.entrypoint || 'main.py')}</span>
                    </div>
                    ${adapter.description ? `<p>${escapeHtml(adapter.description)}</p>` : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="empty-message">No simulation adapters registered yet.</p>';
        }
    } catch (error) {
        container.innerHTML = '<p class="empty-message">Failed to load simulation adapters. API may be offline.</p>';
        console.error('Failed to load simulation adapters:', error);
    }
}

/**
 * Show modal for creating a new research packet
 */
function showCreatePacketModal() {
    // For now, create a simple demo packet
    const packetId = 'packet-' + Date.now();
    const packet = {
        id: packetId,
        title: 'Demo Research Packet',
        authors: 'Bioworld Community',
        license: 'MIT',
        game_version: '0.1.0',
        seed: 'weekly-seed-001',
        tags: ['demo', 'ecology', 'simulation']
    };

    createResearchPacket(packet);
}

/**
 * Create a new research packet via API
 * @param {Object} packet - Packet data
 */
async function createResearchPacket(packet) {
    try {
        const response = await fetch('/api/research-packets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(packet)
        });

        if (response.ok) {
            showToast('Research packet created successfully!', 'success');
            loadResearchPackets();
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to create packet', 'error');
        }
    } catch (error) {
        showToast('Failed to create research packet', 'error');
        console.error('Failed to create research packet:', error);
    }
}

/**
 * Run AI analysis on content
 */
async function runAnalysis() {
    const contentEl = document.getElementById('analysis-content');
    const typeEl = document.getElementById('analysis-type');
    const resultEl = document.getElementById('analysis-result');

    if (!contentEl || !typeEl || !resultEl) return;

    const content = contentEl.value.trim();
    if (!content) {
        showToast('Please enter content to analyze', 'error');
        return;
    }

    resultEl.classList.remove('hidden');
    resultEl.innerHTML = '<p class="loading">Analyzing content...</p>';

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: content,
                type: typeEl.value
            })
        });

        const data = await response.json();

        if (response.ok) {
            resultEl.innerHTML = `
                <h4>Analysis Results</h4>
                <p><strong>Type:</strong> ${escapeHtml(data.analysis_type)}</p>
                <p><strong>Status:</strong> ${escapeHtml(data.status)}</p>
                <p><strong>Content Length:</strong> ${data.result.content_length} characters</p>
                <h5>Suggestions:</h5>
                <ul>
                    ${data.result.suggestions.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
                </ul>
            `;
        } else {
            resultEl.innerHTML = `<p class="error">Error: ${escapeHtml(data.error)}</p>`;
        }
    } catch (error) {
        resultEl.innerHTML = '<p class="error">Failed to analyze content. API may be offline.</p>';
        console.error('Analysis failed:', error);
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
