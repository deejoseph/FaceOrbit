// PolyView V2 前端主逻辑
let currentMode = 'Pet';
let currentViews = [];
let currentJobId = null;
let pollInterval = null;
let currentImageData = null;

// 模式显示名称映射
const modeDisplayNames = {
    'Celadon': '🍵 青瓷 Celadon',
    'Pet': '🐕 宠物 Pet',
    'Human': '👤 人物 Human',
    'Industrial': '🏭 工业 Industrial',
    'Architecture': '🏛️ 建筑 Architecture'
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('PolyView V2 初始化...');
    loadModes();
    initEventListeners();
    // 初始化时隐藏所有图片占位符
    hideAllPreviews();
});

// 隐藏所有预览占位符
function hideAllPreviews() {
    const totalImg = document.getElementById('totalPreview');
    const sheetImg = document.getElementById('sheetPreview');
    const totalEmpty = document.getElementById('totalEmpty');
    const sheetEmpty = document.getElementById('sheetEmpty');
    const singleEmpty = document.getElementById('singleEmpty');
    const singleGallery = document.getElementById('singleGallery');
    
    if (totalImg) totalImg.style.display = 'none';
    if (sheetImg) sheetImg.style.display = 'none';
    if (totalEmpty) totalEmpty.style.display = 'block';
    if (sheetEmpty) sheetEmpty.style.display = 'block';
    if (singleEmpty) singleEmpty.style.display = 'block';
    if (singleGallery) singleGallery.innerHTML = '';
}

// 从后端加载模式预设
async function loadModes() {
    try {
        const response = await fetch('/api/modes');
        if (!response.ok) throw new Error('Failed to load modes');
        const data = await response.json();
        
        const modeSelect = document.getElementById('mode');
        if (modeSelect) {
            modeSelect.innerHTML = '';
            
            for (const [modeKey, modeData] of Object.entries(data.modes)) {
                const option = document.createElement('option');
                option.value = modeKey;
                option.textContent = modeDisplayNames[modeKey] || modeKey;
                modeSelect.appendChild(option);
            }
            
            if (data.modes['Pet']) {
                modeSelect.value = 'Pet';
                currentMode = 'Pet';
            } else if (Object.keys(data.modes).length > 0) {
                modeSelect.value = Object.keys(data.modes)[0];
                currentMode = modeSelect.value;
            }
            
            updateModeBadge();
            loadModePrompts();
            updateViewsForMode();
        }
    } catch (error) {
        console.error('加载模式失败:', error);
        useDefaultPresets();
    }
}

function useDefaultPresets() {
    const defaultModes = {
        'Celadon': {
            views: [
                {name: '正面主视', zoom: 1.5, steps: 24, cfg: 2.2},
                {name: '背面视图', zoom: 1.35, steps: 36, cfg: 2.4},
                {name: '顶视图', zoom: 1.5, steps: 20, cfg: 1.8},
                {name: '四分之三视图', zoom: 2.2, steps: 28, cfg: 2.0},
                {name: '侧视图', zoom: 1.5, steps: 24, cfg: 2.2}
            ]
        },
        'Pet': {
            views: [
                {name: '正面', zoom: 1.2, steps: 28, cfg: 2.8},
                {name: '左前', zoom: 1.2, steps: 28, cfg: 2.8},
                {name: '右前', zoom: 1.2, steps: 28, cfg: 2.8},
                {name: '侧面', zoom: 1.1, steps: 28, cfg: 2.6},
                {name: '背面', zoom: 1.0, steps: 28, cfg: 2.5},
                {name: '俯视', zoom: 1.1, steps: 28, cfg: 2.6}
            ]
        },
        'Human': {
            views: [
                {name: '正面', zoom: 0.85, steps: 40, cfg: 3.2},
                {name: '左前', zoom: 1.3, steps: 35, cfg: 3.0},
                {name: '右前', zoom: 1.3, steps: 35, cfg: 3.0},
                {name: '侧面', zoom: 1.2, steps: 32, cfg: 3.0},
                {name: '背面', zoom: 1.2, steps: 32, cfg: 3.0},
                {name: '俯视', zoom: 1.1, steps: 28, cfg: 3.0}
            ]
        },
        'Industrial': {
            views: [
                {name: '正面', zoom: 0.9, steps: 40, cfg: 1.8},
                {name: '左前', zoom: 0.9, steps: 35, cfg: 1.8},
                {name: '右前', zoom: 0.9, steps: 35, cfg: 1.8},
                {name: '侧面', zoom: 0.85, steps: 35, cfg: 1.8},
                {name: '背面', zoom: 0.85, steps: 35, cfg: 1.8},
                {name: '俯视', zoom: 0.8, steps: 30, cfg: 1.8}
            ]
        },
        'Architecture': {
            views: [
                {name: '正立面', zoom: 0.9, steps: 32, cfg: 2.2},
                {name: '左前', zoom: 0.85, steps: 32, cfg: 2.2},
                {name: '右前', zoom: 0.85, steps: 32, cfg: 2.2},
                {name: '侧立面', zoom: 0.9, steps: 32, cfg: 2.2},
                {name: '背立面', zoom: 0.9, steps: 32, cfg: 2.2},
                {name: '鸟瞰', zoom: 0.8, steps: 32, cfg: 2.2}
            ]
        }
    };
    
    const modeSelect = document.getElementById('mode');
    if (modeSelect) {
        modeSelect.innerHTML = '';
        for (const modeKey of Object.keys(defaultModes)) {
            const option = document.createElement('option');
            option.value = modeKey;
            option.textContent = modeDisplayNames[modeKey] || modeKey;
            modeSelect.appendChild(option);
        }
        modeSelect.value = 'Pet';
        currentMode = 'Pet';
        updateModeBadge();
        currentViews = [...defaultModes[currentMode].views];
        renderViewControls();
    }
}

function updateModeBadge() {
    const badge = document.getElementById('modeBadge');
    if (badge) {
        badge.textContent = currentMode;
        badge.className = `badge mode-${currentMode.toLowerCase()}`;
    }
}

async function loadModePrompts() {
    try {
        const response = await fetch(`/api/mode/${currentMode}`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById('promptText').value = data.prompt || '';
            document.getElementById('negativePromptText').value = data.negative || '';
        }
    } catch (error) {
        console.error('加载 prompt 失败:', error);
    }
}

function updateViewsForMode() {
    const modeSelect = document.getElementById('mode');
    currentMode = modeSelect.value;
    updateModeBadge();
    loadModePrompts();
    
    fetch(`/api/mode/${currentMode}`)
        .then(res => res.json())
        .then(data => {
            if (data.views) {
                currentViews = data.views.map(v => ({...v}));
                renderViewControls();
            } else {
                throw new Error('No views');
            }
        })
        .catch(() => {
            const defaultPresets = {
                'Celadon': [
                    {name: '正面主视', zoom: 1.5, steps: 24, cfg: 2.2},
                    {name: '背面视图', zoom: 1.35, steps: 36, cfg: 2.4},
                    {name: '顶视图', zoom: 1.5, steps: 20, cfg: 1.8},
                    {name: '四分之三视图', zoom: 2.2, steps: 28, cfg: 2.0},
                    {name: '侧视图', zoom: 1.5, steps: 24, cfg: 2.2}
                ],
                'Pet': [
                    {name: '正面', zoom: 1.2, steps: 28, cfg: 2.8},
                    {name: '左前', zoom: 1.2, steps: 28, cfg: 2.8},
                    {name: '右前', zoom: 1.2, steps: 28, cfg: 2.8},
                    {name: '侧面', zoom: 1.1, steps: 28, cfg: 2.6},
                    {name: '背面', zoom: 1.0, steps: 28, cfg: 2.5},
                    {name: '俯视', zoom: 1.1, steps: 28, cfg: 2.6}
                ],
                'Human': [
                    {name: '正面', zoom: 0.85, steps: 40, cfg: 3.2},
                    {name: '左前', zoom: 1.3, steps: 35, cfg: 3.0},
                    {name: '右前', zoom: 1.3, steps: 35, cfg: 3.0},
                    {name: '侧面', zoom: 1.2, steps: 32, cfg: 3.0},
                    {name: '背面', zoom: 1.2, steps: 32, cfg: 3.0},
                    {name: '俯视', zoom: 1.1, steps: 28, cfg: 3.0}
                ],
                'Industrial': [
                    {name: '正面', zoom: 0.9, steps: 40, cfg: 1.8},
                    {name: '左前', zoom: 0.9, steps: 35, cfg: 1.8},
                    {name: '右前', zoom: 0.9, steps: 35, cfg: 1.8},
                    {name: '侧面', zoom: 0.85, steps: 35, cfg: 1.8},
                    {name: '背面', zoom: 0.85, steps: 35, cfg: 1.8},
                    {name: '俯视', zoom: 0.8, steps: 30, cfg: 1.8}
                ],
                'Architecture': [
                    {name: '正立面', zoom: 0.9, steps: 32, cfg: 2.2},
                    {name: '左前', zoom: 0.85, steps: 32, cfg: 2.2},
                    {name: '右前', zoom: 0.85, steps: 32, cfg: 2.2},
                    {name: '侧立面', zoom: 0.9, steps: 32, cfg: 2.2},
                    {name: '背立面', zoom: 0.9, steps: 32, cfg: 2.2},
                    {name: '鸟瞰', zoom: 0.8, steps: 32, cfg: 2.2}
                ]
            };
            currentViews = defaultPresets[currentMode] || defaultPresets['Pet'];
            renderViewControls();
        });
}

function renderViewControls() {
    const container = document.getElementById('viewControls');
    if (!container) return;
    
    container.innerHTML = '';
    
    currentViews.forEach((view, index) => {
        const card = document.createElement('div');
        card.className = 'view-card';
        card.innerHTML = `
            <div class="view-header">
                <h3>${view.name}</h3>
                <span class="view-badge">视角 ${index + 1}</span>
            </div>
            <div class="view-params">
                <div class="param-group">
                    <label>Zoom</label>
                    <input type="number" step="0.05" value="${view.zoom}" data-index="${index}" data-field="zoom" class="param-input">
                </div>
                <div class="param-group">
                    <label>Steps</label>
                    <input type="number" step="1" value="${view.steps}" data-index="${index}" data-field="steps" class="param-input">
                </div>
                <div class="param-group">
                    <label>CFG</label>
                    <input type="number" step="0.1" value="${view.cfg}" data-index="${index}" data-field="cfg" class="param-input">
                </div>
            </div>
            <button class="single-generate" data-view-name="${view.name}" data-view-index="${index}">单独生成此视角</button>
        `;
        container.appendChild(card);
    });
    
    document.querySelectorAll('.param-input').forEach(input => {
        input.addEventListener('change', (e) => {
            const index = parseInt(input.dataset.index);
            const field = input.dataset.field;
            const value = parseFloat(input.value);
            if (currentViews[index]) {
                currentViews[index][field] = value;
                updatePayloadPreview();
            }
        });
    });
    
    document.querySelectorAll('.single-generate').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const viewIndex = parseInt(btn.dataset.viewIndex);
            generateSingleView(viewIndex);
        });
    });
    
    updatePayloadPreview();
}

function updatePayloadPreview() {
    const preview = document.getElementById('payloadPreview');
    if (preview) {
        const payload = {
            mode: currentMode,
            views: currentViews,
            prompt: document.getElementById('promptText').value,
            negative_prompt: document.getElementById('negativePromptText').value
        };
        preview.textContent = JSON.stringify(payload, null, 2);
    }
}

// 生成所有视图
async function generateAll() {
    if (!currentImageData) {
        showStatus('请先上传参考图', 'error');
        return;
    }
    
    showStatus('正在提交任务...', 'loading');
    
    const payload = {
        imageData: currentImageData,
        mode: currentMode,
        views: currentViews.map(v => ({
            name: v.name,
            zoom: v.zoom,
            steps: v.steps,
            cfg: v.cfg
        }))
    };
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        if (data.job_id) {
            currentJobId = data.job_id;
            startPolling();
            showStatus('任务已提交，生成中...', 'running');
        } else {
            showStatus('提交失败: ' + JSON.stringify(data), 'error');
        }
    } catch (error) {
        showStatus('网络错误: ' + error.message, 'error');
    }
}

// 生成单个视图
async function generateSingleView(viewIndex) {
    if (!currentImageData) {
        showStatus('请先上传参考图', 'error');
        return;
    }
    
    const singleView = currentViews[viewIndex];
    showStatus(`正在生成 ${singleView.name}...`, 'loading');
    
    const payload = {
        imageData: currentImageData,
        mode: currentMode,
        views: [singleView]
    };
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        if (data.job_id) {
            currentJobId = data.job_id;
            startPolling();
            showStatus(`正在生成 ${singleView.name}...`, 'running');
        } else {
            showStatus('提交失败: ' + JSON.stringify(data), 'error');
        }
    } catch (error) {
        showStatus('网络错误: ' + error.message, 'error');
    }
}

// 开始轮询任务状态
function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    
    pollInterval = setInterval(async () => {
        if (!currentJobId) return;
        
        try {
            const response = await fetch(`/api/jobs/${currentJobId}`);
            const job = await response.json();
            
            if (job.status === 'completed') {
                clearInterval(pollInterval);
                pollInterval = null;
                showStatus('生成完成！', 'success');
                displayResults(job);
            } else if (job.status === 'error') {
                clearInterval(pollInterval);
                pollInterval = null;
                showStatus('生成失败: ' + (job.error || '未知错误'), 'error');
            }
        } catch (error) {
            console.error('轮询错误:', error);
        }
    }, 2000);
}

// 显示生成结果
function displayResults(job) {
    // 显示总图
    const totalImg = document.getElementById('totalPreview');
    const totalEmpty = document.getElementById('totalEmpty');
    if (job.total_url) {
        totalImg.src = job.total_url;
        totalImg.style.display = 'block';
        totalEmpty.style.display = 'none';
    } else {
        totalImg.style.display = 'none';
        totalEmpty.style.display = 'block';
    }
    
    // 显示 contact sheet
    const sheetImg = document.getElementById('sheetPreview');
    const sheetEmpty = document.getElementById('sheetEmpty');
    if (job.sheet_url) {
        sheetImg.src = job.sheet_url;
        sheetImg.style.display = 'block';
        sheetEmpty.style.display = 'none';
    } else {
        sheetImg.style.display = 'none';
        sheetEmpty.style.display = 'block';
    }
    
    // 显示单图 - 使用卡片网格布局
    const gallery = document.getElementById('singleGallery');
    const singleEmpty = document.getElementById('singleEmpty');
    
    if (gallery) {
        if (job.single_paths && job.single_paths.length > 0) {
            gallery.innerHTML = '';
            // 使用网格布局显示每个图片卡片
            job.single_paths.forEach(img => {
                const card = document.createElement('div');
                card.className = 'single-image-card';
                card.innerHTML = `
                    <img src="${img.url}" alt="${img.name}">
                    <div class="single-image-info">
                        <strong>${img.name}</strong>
                        <span>Zoom: ${img.zoom} | Steps: ${img.steps} | CFG: ${img.cfg}</span>
                    </div>
                    <a href="${img.url}" download class="download-btn">下载</a>
                `;
                gallery.appendChild(card);
            });
            gallery.style.display = 'grid';
            singleEmpty.style.display = 'none';
        } else {
            gallery.innerHTML = '';
            gallery.style.display = 'none';
            singleEmpty.style.display = 'block';
        }
    }
}

function showStatus(message, type) {
    const statusBox = document.getElementById('statusBox');
    if (statusBox) {
        statusBox.textContent = message;
        statusBox.className = `status-box status-${type}`;
        if (type === 'success' || type === 'error') {
            setTimeout(() => {
                if (statusBox.className === `status-box status-${type}`) {
                    statusBox.className = 'status-box status-idle';
                    statusBox.textContent = '等待任务';
                }
            }, 3000);
        }
    }
}

function resetToPreset() {
    updateViewsForMode();
    showStatus('已恢复预设参数', 'success');
}

function refreshGallery() {
    if (currentJobId) {
        fetch(`/api/jobs/${currentJobId}`)
            .then(res => res.json())
            .then(job => {
                if (job.status === 'completed') {
                    displayResults(job);
                    showStatus('已刷新结果', 'success');
                }
            })
            .catch(console.error);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showStatus('已复制到剪贴板', 'success');
    });
}

// 初始化事件监听
function initEventListeners() {
    const modeSelect = document.getElementById('mode');
    if (modeSelect) {
        modeSelect.addEventListener('change', () => {
            updateViewsForMode();
        });
    }
    
    const generateBtn = document.getElementById('generateButton');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateAll);
    }
    
    const resetBtn = document.getElementById('resetViews');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetToPreset);
    }
    
    const refreshBtn = document.getElementById('refreshGallery');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshGallery);
    }
    
    const copyPromptBtn = document.getElementById('copyPrompt');
    if (copyPromptBtn) {
        copyPromptBtn.addEventListener('click', () => {
            const prompt = document.getElementById('promptText').value;
            copyToClipboard(prompt);
        });
    }
    
    const copyNegativeBtn = document.getElementById('copyNegative');
    if (copyNegativeBtn) {
        copyNegativeBtn.addEventListener('click', () => {
            const negative = document.getElementById('negativePromptText').value;
            copyToClipboard(negative);
        });
    }
    
    // 图片上传预览
    const imageUpload = document.getElementById('imageUpload');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadEmpty = document.getElementById('uploadEmpty');
    
    if (imageUpload) {
        imageUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    currentImageData = event.target.result;
                    uploadPreview.innerHTML = `<img src="${currentImageData}" alt="预览图" style="max-width:100%; max-height:200px; object-fit:contain;">`;
                    uploadPreview.style.display = 'flex';
                    if (uploadEmpty) uploadEmpty.style.display = 'none';
                    showStatus('图片已加载，可以生成', 'success');
                };
                reader.readAsDataURL(file);
            } else {
                currentImageData = null;
                uploadPreview.innerHTML = '';
                uploadPreview.style.display = 'flex';
                if (uploadEmpty) uploadEmpty.style.display = 'block';
            }
        });
    }
    
    const promptText = document.getElementById('promptText');
    const negativeText = document.getElementById('negativePromptText');
    if (promptText) promptText.addEventListener('input', updatePayloadPreview);
    if (negativeText) negativeText.addEventListener('input', updatePayloadPreview);
}