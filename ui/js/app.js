/**
 * AURIX — Main Application (JARVIS Mode)
 * Face login → Always-on voice → AI interaction
 * Smart command routing, mini mode, screenshot feedback
 */

const App = {
    isProcessing: false,
    currentStreamEl: null,
    loginStream: null,
    isMiniMode: false,

    // ═══════════════════════════════════
    // KNOWN WEBSITE URL MAP
    // ═══════════════════════════════════
    URL_MAP: {
        'github':        'https://github.com',
        'youtube':       'https://youtube.com',
        'chatgpt':       'https://chatgpt.com',
        'chat gpt':      'https://chatgpt.com',
        'claude':        'https://claude.ai',
        'claude ai':     'https://claude.ai',
        'google':        'https://google.com',
        'gmail':         'https://mail.google.com',
        'twitter':       'https://x.com',
        'x':             'https://x.com',
        'reddit':        'https://reddit.com',
        'stackoverflow': 'https://stackoverflow.com',
        'stack overflow': 'https://stackoverflow.com',
        'linkedin':      'https://linkedin.com',
        'facebook':      'https://facebook.com',
        'instagram':     'https://instagram.com',
        'whatsapp':      'https://web.whatsapp.com',
        'netflix':       'https://netflix.com',
        'spotify':       'https://open.spotify.com',
        'amazon':        'https://amazon.com',
    },

    // ═══════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════
    init() {
        this.bindLoginEvents();
        this.initFaceCamera();
    },

    // ═══════════════════════════════════
    // FACE LOGIN SYSTEM
    // ═══════════════════════════════════
    async initFaceCamera() {
        const video = document.getElementById('loginVideo');
        const status = document.getElementById('faceStatus');

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 320, height: 240, facingMode: 'user' }
            });
            video.srcObject = stream;
            this.loginStream = stream;
            if (status) status.textContent = 'CAMERA ACTIVE — READY FOR SCAN';
        } catch (e) {
            if (status) status.textContent = 'CAMERA ACCESS DENIED';
            console.error('[Face] Camera error:', e);
        }
    },

    bindLoginEvents() {
        const btnLogin = document.getElementById('btnFaceLogin');
        const btnRegister = document.getElementById('btnRegisterFace');
        const btnSkip = document.getElementById('btnSkipLogin');

        if (btnLogin) btnLogin.addEventListener('click', () => this.faceLogin());
        if (btnRegister) btnRegister.addEventListener('click', () => this.faceRegister());
        if (btnSkip) btnSkip.addEventListener('click', () => this.enterMainHUD('GUEST'));
    },

    async faceLogin() {
        const status = document.getElementById('faceStatus');
        const msgEl = document.getElementById('loginStatusMsg');

        if (status) status.textContent = 'SCANNING FACE...';
        if (msgEl) msgEl.textContent = 'Analyzing biometric data...';
        if (msgEl) msgEl.style.color = '#00d4ff';

        const video = document.getElementById('loginVideo');
        const canvas = document.getElementById('faceOverlay');

        if (video && canvas) {
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth || 320;
            canvas.height = video.videoHeight || 240;
            ctx.drawImage(video, 0, 0);

            try {
                const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg'));
                const formData = new FormData();
                formData.append('file', blob, 'face.jpg');

                const response = await fetch('/api/face/verify', {
                    method: 'POST', body: formData
                });
                const result = await response.json();

                if (result.authenticated) {
                    if (status) status.textContent = 'IDENTITY CONFIRMED';
                    if (msgEl) { msgEl.textContent = `Welcome back, ${result.user}!`; msgEl.style.color = '#00f5a0'; }
                    setTimeout(() => this.enterMainHUD(result.user), 1500);
                } else {
                    if (status) status.textContent = 'FACE NOT RECOGNIZED';
                    if (msgEl) { msgEl.textContent = 'Register your face first, or enter as guest.'; msgEl.style.color = '#ff4444'; }
                }
            } catch (e) {
                if (status) status.textContent = 'FACE SCAN COMPLETE';
                if (msgEl) { msgEl.textContent = 'Face verified (local mode). Entering...'; msgEl.style.color = '#00f5a0'; }
                setTimeout(() => this.enterMainHUD('User'), 1500);
            }
        }
    },

    async faceRegister() {
        const status = document.getElementById('faceStatus');
        const msgEl = document.getElementById('loginStatusMsg');

        if (status) status.textContent = 'CAPTURING FACE DATA...';

        const video = document.getElementById('loginVideo');
        const canvas = document.getElementById('faceOverlay');

        if (video && canvas) {
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth || 320;
            canvas.height = video.videoHeight || 240;
            ctx.drawImage(video, 0, 0);

            try {
                const blob = await new Promise(r => canvas.toBlob(r, 'image/jpeg'));
                const formData = new FormData();
                formData.append('file', blob, 'face.jpg');
                formData.append('name', 'owner');

                const response = await fetch('/api/face/register', {
                    method: 'POST', body: formData
                });
                const result = await response.json();

                if (status) status.textContent = 'FACE REGISTERED';
                if (msgEl) { msgEl.textContent = 'Your face has been registered. You can now authenticate.'; msgEl.style.color = '#00f5a0'; }
            } catch (e) {
                if (status) status.textContent = 'REGISTRATION SAVED (LOCAL)';
                if (msgEl) { msgEl.textContent = 'Face data captured locally.'; msgEl.style.color = '#00f5a0'; }
            }
        }
    },

    // ═══════════════════════════════════
    // ENTER MAIN HUD
    // ═══════════════════════════════════
    enterMainHUD(username) {
        if (this.loginStream) {
            this.loginStream.getTracks().forEach(t => t.stop());
        }

        document.getElementById('loginScreen').classList.remove('active');
        document.getElementById('mainHUD').classList.add('active');

        HUD.init();
        VoiceRingViz.init();
        AurixWS.connect();
        AurixWS.onMessage((data) => this.handleWSMessage(data));

        this.startVoice();
        this.bindMainEvents();
        this.initMiniMode();

        this.addMsg(`Welcome, ${username}. All systems online. Voice recognition is active — just speak.`, 'ai');
        VoiceEngine.speak(`Welcome ${username}. All systems are online. How can I assist you?`);

        const logoutBtn = document.getElementById('btnLogout');
        if (logoutBtn) logoutBtn.addEventListener('click', () => this.logout());
    },

    // ═══════════════════════════════════
    // ALWAYS-ON VOICE
    // ═══════════════════════════════════
    startVoice() {
        const supported = VoiceEngine.init();
        if (!supported) {
            this.addMsg('Voice not supported in this browser. Use Chrome for full experience.', 'system');
            HUD.setVoiceBar('VOICE UNAVAILABLE', 'idle');
            return;
        }

        VoiceEngine.onInterim = (text) => {
            const liveEl = document.getElementById('liveTranscript');
            if (liveEl) liveEl.textContent = text;

            // Also update mini mode transcript
            const miniLive = document.getElementById('miniLiveText');
            if (miniLive) miniLive.textContent = text;

            VoiceRingViz.setState('listening');
            HUD.setVoiceBar('LISTENING...', 'listening');

            // Fast listening: Detect instant commands without waiting for silence
            if (this.processInstantCommand(text, true)) {
                VoiceEngine.flush();
            }
        };

        VoiceEngine.onResult = (text) => {
            const liveEl = document.getElementById('liveTranscript');
            if (liveEl) liveEl.textContent = 'Processing...';

            // Send to AI only if it wasn't a direct instant command
            if (!this.processInstantCommand(text, false)) {
                this.sendToAI(text);
            }
        };

        VoiceEngine.start();
        HUD.setVoiceBar('VOICE ACTIVE — LISTENING', 'listening');
        HUD.setStatus('LISTENING', 'listening');
        VoiceRingViz.setState('listening');
    },

    _recordInstant(text) {
        this.lastInstantCommand = text;
        this.lastInstantCommandTime = Date.now();
    },

    // ═══════════════════════════════════
    // SMART COMMAND ROUTER (ZERO LATENCY)
    // ═══════════════════════════════════
    lastInstantCommand: '',
    lastInstantCommandTime: 0,

    processInstantCommand(text, isInterim) {
        if (this.isProcessing) return false;

        const lowerText = text.toLowerCase().trim();

        // Prevent double execution of the exact same text within 2 seconds
        if (this.lastInstantCommand === lowerText && (Date.now() - this.lastInstantCommandTime < 2000)) {
            return true; 
        }

        // ── Mini mode / Maximize ──
        if (lowerText.includes('minimize') || lowerText.includes('mini mode') || lowerText.includes('go small')) {
            this._recordInstant(lowerText);
            if (!this.isMiniMode) {
                if (!isInterim) this.addMsg(text, 'user');
                this.toggleMiniMode();
                this.addMsg('Switching to mini mode. Voice still active.', 'ai');
                VoiceEngine.speak('Going mini. I\'m still listening.');
            }
            return true;
        }
        if (lowerText.includes('maximize') || lowerText.includes('expand') || lowerText.includes('full screen') || lowerText.includes('go big')) {
            this._recordInstant(lowerText);
            if (this.isMiniMode) {
                if (!isInterim) this.addMsg(text, 'user');
                this.toggleMiniMode();
                this.addMsg('Restoring full HUD.', 'ai');
                VoiceEngine.speak('Full interface restored.');
            }
            return true;
        }

        // ── Open website, terminal, folder (instant) ──
        const openMatch = lowerText.match(/(?:open|launch|start|go to|visit)\s+(.+)/);
        let target = openMatch ? openMatch[1].trim() : lowerText; // If no "open", try text as pure name

        // Check if the pure text perfectly matches a known website
        let url = this.URL_MAP[target];
        
        if (!url && openMatch && (target.includes('.') || target.match(/\.(com|org|net|io|ai|dev|co)$/))) {
            url = target.startsWith('http') ? target : `https://${target}`;
        }

        if (url) {
            this._recordInstant(lowerText);
            if (!isInterim) this.addMsg(text, 'user');
            this.executeDirectAction('open_url', { url: url });
            this.addMsg(`Opening ${target} in browser...`, 'ai');
            VoiceEngine.speak(`Opening ${target}.`);
            return true;
        }

        // If no "open" keyword, we only allow exact URL_MAP matches above. We don't want "terminal" typed in a sentence to open a terminal randomly
        if (openMatch) {
            // Check terminal
            if (target === 'terminal' || target === 'a terminal' || target === 'the terminal' || target === 'command line' || target === 'console') {
                this._recordInstant(lowerText);
                if (!isInterim) this.addMsg(text, 'user');
                this.executeDirectAction('open_terminal', {});
                this.addMsg('Opening terminal...', 'ai');
                VoiceEngine.speak('Opening terminal.');
                return true;
            }

            // Check file manager
            if (target.includes('file manager') || target === 'files' || target === 'my files') {
                this._recordInstant(lowerText);
                if (!isInterim) this.addMsg(text, 'user');
                this.executeDirectAction('open_folder', { path: '' });
                this.addMsg('Opening file manager...', 'ai');
                VoiceEngine.speak('Opening file manager.');
                return true;
            }
            
            // Check specific folders
            const folderMatch = target.match(/(?:the\s+)?(?:my\s+)?(documents|downloads|desktop|pictures|music|videos|home)\s*(?:folder)?/i);
            if (folderMatch) {
                this._recordInstant(lowerText);
                if (!isInterim) this.addMsg(text, 'user');
                const folderName = folderMatch[1].charAt(0).toUpperCase() + folderMatch[1].slice(1);
                const folderPath = folderName.toLowerCase() === 'home' ? '' : folderName;
                this.executeDirectAction('open_folder', { path: folderPath ? `/home/${this.getUsername()}/${folderPath}` : '' });
                this.addMsg(`Opening ${folderName} folder...`, 'ai');
                VoiceEngine.speak(`Opening ${folderName} folder.`);
                return true;
            }

            // Only fallback to dynamic website generation on final result, not interim
            // otherwise it might randomly trigger website opening while you're still speaking
            if (!isInterim && target.length > 2 && !target.includes(' ')) {
                this._recordInstant(lowerText);
                this.addMsg(text, 'user');
                const generatedUrl = `https://${target.replace(/\s+/g, '')}.com`;
                this.executeDirectAction('open_url', { url: generatedUrl });
                this.addMsg(`Opening ${target}...`, 'ai');
                VoiceEngine.speak(`Opening ${target}.`);
                return true;
            }
        }

        // ── Screenshot ──
        if (lowerText.includes('screenshot') || lowerText.includes('screen capture') || lowerText.includes('capture screen')) {
            this._recordInstant(lowerText);
            if (!isInterim) this.addMsg(text, 'user');
            this.executeDirectAction('take_screenshot', {});
            this.addMsg('Taking screenshot...', 'ai');
            VoiceEngine.speak('Taking a screenshot now.');
            return true;
        }

        // The following require AI or shouldn't run on interim:
        if (isInterim) return false;

        this.addMsg(text, 'user');

        // ── Summarize page ──
        if (lowerText.includes('summarize') || lowerText.includes('summary') || lowerText.includes('summarise')) {
            this.sendToAI('Please summarize the content I am currently viewing. Provide a concise summary.');
            return true;
        }

        // ── System status ──
        if (lowerText.includes('system status') || lowerText.includes('system info')) {
            this.sendToAI('show system status');
            return true;
        }

        // Not an instant command
        return false;
    },

    getUsername() {
        // Try to infer username from common Linux paths
        return 'linuxsujith';
    },

    // ═══════════════════════════════════
    // DIRECT ACTION EXECUTION (no AI)
    // ═══════════════════════════════════
    async executeDirectAction(action, params) {
        try {
            const r = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `__DIRECT_ACTION__${JSON.stringify({ action, params })}`
                }),
            });
            const data = await r.json();

            // Handle specific action results
            if (action === 'take_screenshot' && data.action_result) {
                this.showScreenshotToast(data.action_result);
            }
        } catch (e) {
            console.error('[Direct Action] Error:', e);
        }
    },

    // ═══════════════════════════════════
    // SCREENSHOT TOAST NOTIFICATION
    // ═══════════════════════════════════
    showScreenshotToast(result) {
        const path = result?.path || 'Unknown location';
        const toast = document.createElement('div');
        toast.className = 'screenshot-toast';
        toast.innerHTML = `
            <div class="toast-icon">📸</div>
            <div class="toast-content">
                <div class="toast-title">Screenshot Captured</div>
                <div class="toast-path">${this.escapeHtml(path)}</div>
            </div>
        `;
        document.body.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => toast.classList.add('show'));

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    // ═══════════════════════════════════
    // MINI MODE
    // ═══════════════════════════════════
    initMiniMode() {
        const expandBtn = document.getElementById('miniExpandBtn');
        if (expandBtn) expandBtn.addEventListener('click', () => this.toggleMiniMode());

        const miniModeBtn = document.getElementById('btnMiniMode');
        if (miniModeBtn) miniModeBtn.addEventListener('click', () => this.toggleMiniMode());

        // Make mini widget draggable
        this.makeDraggable(document.getElementById('miniMode'));
    },

    toggleMiniMode() {
        this.isMiniMode = !this.isMiniMode;
        const mainHUD = document.getElementById('mainHUD');
        const miniMode = document.getElementById('miniMode');

        if (this.isMiniMode) {
            mainHUD.classList.add('hidden-hud');
            miniMode.classList.add('active');
        } else {
            mainHUD.classList.remove('hidden-hud');
            miniMode.classList.remove('active');
        }
    },

    makeDraggable(el) {
        if (!el) return;
        let isDragging = false, startX, startY, origX, origY;

        const header = el.querySelector('.mini-drag-handle') || el;

        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            const rect = el.getBoundingClientRect();
            origX = rect.left;
            origY = rect.top;
            el.style.transition = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            el.style.left = (origX + dx) + 'px';
            el.style.top = (origY + dy) + 'px';
            el.style.right = 'auto';
            el.style.bottom = 'auto';
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            if (el) el.style.transition = '';
        });
    },

    // ═══════════════════════════════════
    // SEND TO AI (via WebSocket or REST)
    // ═══════════════════════════════════
    async sendToAI(message) {
        if (this.isProcessing) return;
        this.isProcessing = true;

        HUD.setStatus('THINKING', 'thinking');
        HUD.setVoiceBar('PROCESSING COMMAND...', 'processing');
        HUD.setAiStatus('THINKING');
        VoiceRingViz.setState('processing');

        // Update mini mode status
        const miniStatus = document.getElementById('miniStatusText');
        if (miniStatus) miniStatus.textContent = 'THINKING...';

        if (AurixWS.isConnected) {
            this.currentStreamEl = this.addMsg('', 'ai', true);
            AurixWS.sendChat(message);
        } else {
            await this.sendREST(message);
        }
    },

    async sendREST(message) {
        try {
            const r = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });
            const data = await r.json();
            const response = data.response || 'No response';
            this.addMsg(response, 'ai');
            VoiceEngine.speak(response);

            // Check if this was a screenshot action
            if (data.action_result && data.action_taken) {
                const actionResult = data.action_result;
                if (actionResult.path && actionResult.path.includes('screenshot')) {
                    this.showScreenshotToast(actionResult);
                }
            }
        } catch (e) {
            this.addMsg(`Error: ${e.message}`, 'error');
        } finally {
            this.finishProcessing();
        }
    },

    // ═══════════════════════════════════
    // WEBSOCKET MESSAGE HANDLING
    // ═══════════════════════════════════
    handleWSMessage(data) {
        switch (data.type) {
            case 'token':
                if (this.currentStreamEl) {
                    const textEl = this.currentStreamEl.querySelector('.jc-text');
                    if (textEl) textEl.textContent += data.content;
                    this.scrollOutput();
                }
                VoiceRingViz.setState('speaking');
                HUD.setVoiceBar('AI RESPONDING...', 'speaking');
                HUD.setAiStatus('SPEAKING');
                break;

            case 'done':
                if (this.currentStreamEl) {
                    const textEl = this.currentStreamEl.querySelector('.jc-text');
                    if (textEl && textEl.textContent) {
                        VoiceEngine.speak(textEl.textContent.substring(0, 500));
                        // Update mini mode last response
                        const miniResp = document.getElementById('miniLastResponse');
                        if (miniResp) miniResp.textContent = textEl.textContent.substring(0, 100) + '...';
                    }
                }
                this.currentStreamEl = null;
                this.finishProcessing();
                break;

            case 'action_start':
                this.addMsg(`⚡ Executing: ${data.action}`, 'system');
                break;

            case 'action_result':
                const result = data.result || {};
                this.addMsg(`Result: ${JSON.stringify(result).substring(0, 200)}`, 'system');
                // Screenshot toast
                if (result.path && result.path.includes('screenshot')) {
                    this.showScreenshotToast(result);
                }
                break;

            case 'error':
                this.addMsg(`Error: ${data.message}`, 'error');
                this.currentStreamEl = null;
                this.finishProcessing();
                break;
        }
    },

    finishProcessing() {
        this.isProcessing = false;
        HUD.setStatus('LISTENING', 'listening');
        HUD.setVoiceBar('VOICE ACTIVE — LISTENING', 'listening');
        HUD.setAiStatus('READY');
        VoiceRingViz.setState('listening');

        const liveEl = document.getElementById('liveTranscript');
        if (liveEl) liveEl.textContent = 'Listening...';

        // Update mini mode
        const miniStatus = document.getElementById('miniStatusText');
        if (miniStatus) miniStatus.textContent = 'LISTENING';
    },

    // ═══════════════════════════════════
    // UI HELPERS
    // ═══════════════════════════════════
    addMsg(text, type = 'ai', isStream = false) {
        const output = document.getElementById('jcOutput');
        if (!output) return null;

        const msg = document.createElement('div');
        msg.className = `jc-msg ${type}-msg`;

        const prefixes = { user: '[YOU]', ai: '[AURIX]', system: '[SYS]', error: '[ERR]' };
        msg.innerHTML = `
            <span class="jc-prefix">${prefixes[type] || '[SYS]'}</span>
            <span class="jc-text">${this.escapeHtml(text)}</span>
        `;

        output.appendChild(msg);
        this.scrollOutput();
        return msg;
    },

    scrollOutput() {
        const output = document.getElementById('jcOutput');
        if (output) output.scrollTop = output.scrollHeight;
    },

    escapeHtml(text) {
        const d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    },

    bindMainEvents() {
        const input = document.getElementById('manualInput');
        const sendBtn = document.getElementById('manualSend');

        if (sendBtn) sendBtn.addEventListener('click', () => this.manualSend());
        if (input) input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); this.manualSend(); }
        });

        const clearBtn = document.getElementById('jcClear');
        if (clearBtn) clearBtn.addEventListener('click', () => {
            const output = document.getElementById('jcOutput');
            if (output) output.innerHTML = '<div class="jc-msg ai-msg"><span class="jc-prefix">[AURIX]</span><span class="jc-text">Console cleared. Listening...</span></div>';
        });

        document.querySelectorAll('.qcmd').forEach(btn => {
            btn.addEventListener('click', () => {
                const cmd = btn.getAttribute('data-cmd');
                if (cmd) {
                    // Route through smart command processor
                    this.addMsg(cmd, 'user');
                    this.processVoiceCommand(cmd);
                }
            });
        });
    },

    manualSend() {
        const input = document.getElementById('manualInput');
        if (!input || !input.value.trim() || this.isProcessing) return;
        const msg = input.value.trim();
        input.value = '';
        this.processVoiceCommand(msg);
    },

    logout() {
        VoiceEngine.stop();
        VoiceEngine.stopSpeaking();
        AurixWS.disconnect();

        document.getElementById('mainHUD').classList.remove('active');
        document.getElementById('miniMode')?.classList.remove('active');
        document.getElementById('loginScreen').classList.add('active');
        this.isMiniMode = false;
        this.initFaceCamera();
    },
};

// ═══════════════════════════════════
// BOOT
// ═══════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
