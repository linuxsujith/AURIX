/**
 * AURIX — Always-On Voice Engine
 * Uses Web Speech API for continuous speech recognition
 * and Speech Synthesis for voice responses
 */

const VoiceEngine = {
    recognition: null,
    synthesis: window.speechSynthesis,
    isListening: false,
    isSpeaking: false,
    onResult: null,
    onInterim: null,
    restartTimeout: null,

    init() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn('[Voice] Speech Recognition not supported');
            return false;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Show live interim text
            if (interimTranscript && this.onInterim) {
                this.onInterim(interimTranscript);
            }

            // Process final result
            if (finalTranscript.trim() && this.onResult) {
                this.onResult(finalTranscript.trim());
            }
        };

        this.recognition.onerror = (event) => {
            console.log('[Voice] Error:', event.error);
            if (event.error === 'no-speech' || event.error === 'aborted') {
                // Auto restart
                this._scheduleRestart();
            }
        };

        this.recognition.onend = () => {
            // Auto restart if still supposed to be listening
            if (this.isListening) {
                this._scheduleRestart();
            }
        };

        return true;
    },

    start() {
        if (!this.recognition) {
            if (!this.init()) return false;
        }

        try {
            this.isListening = true;
            this.recognition.start();
            console.log('[Voice] Listening started');
            return true;
        } catch (e) {
            console.log('[Voice] Start error (may already be running):', e.message);
            return false;
        }
    },

    stop() {
        this.isListening = false;
        if (this.restartTimeout) clearTimeout(this.restartTimeout);
        try {
            this.recognition.stop();
        } catch (e) {}
        console.log('[Voice] Listening stopped');
    },

    flush() {
        if (!this.recognition) return;
        try {
            this.recognition.stop(); // Stop gracefully to avoid breaking the Chrome web speech engine
        } catch (e) {}
        this._scheduleRestart();
    },

    _scheduleRestart() {
        if (!this.isListening) return;
        if (this.restartTimeout) clearTimeout(this.restartTimeout);
        this.restartTimeout = setTimeout(() => {
            try {
                this.recognition.start();
            } catch (e) {
                // If already running, ignore
            }
        }, 300);
    },

    speak(text) {
        return new Promise((resolve) => {
            if (!this.synthesis) { resolve(); return; }

            // Stop any current speech
            this.synthesis.cancel();
            this.isSpeaking = true;

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 0.9;
            utterance.volume = 1.0;

            // Try to find a good English voice
            const voices = this.synthesis.getVoices();
            const preferred = voices.find(v => v.name.includes('Google') && v.lang.startsWith('en')) ||
                            voices.find(v => v.lang.startsWith('en-'));
            if (preferred) utterance.voice = preferred;

            utterance.onend = () => { this.isSpeaking = false; resolve(); };
            utterance.onerror = () => { this.isSpeaking = false; resolve(); };

            this.synthesis.speak(utterance);
        });
    },

    stopSpeaking() {
        if (this.synthesis) this.synthesis.cancel();
        this.isSpeaking = false;
    }
};

/* Voice Ring Visualizer (around arc reactor) */
const VoiceRingViz = {
    canvas: null, ctx: null, state: 'idle',

    init() {
        this.canvas = document.getElementById('voiceRingCanvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.animate();
    },

    resize() {
        if (!this.canvas) return;
        const size = this.canvas.parentElement ? 280 : 280;
        this.canvas.width = size * window.devicePixelRatio;
        this.canvas.height = size * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        this.w = size; this.h = size;
    },

    setState(s) { this.state = s; },

    animate() {
        if (!this.ctx) return;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.w, this.h);

        const cx = this.w / 2, cy = this.h / 2;
        const time = Date.now() * 0.001;
        const baseR = 100;
        const points = 60;

        ctx.beginPath();
        for (let i = 0; i <= points; i++) {
            const angle = (i / points) * Math.PI * 2;
            let amp = 0;

            switch (this.state) {
                case 'listening':
                    amp = Math.sin(time * 5 + i * 0.5) * 8 + Math.random() * 4;
                    break;
                case 'speaking':
                    amp = Math.abs(Math.sin(time * 4 + i * 0.3)) * 15 + Math.sin(time * 8 + i) * 5;
                    break;
                case 'processing':
                    const wave = Math.sin(time * 6 + i * 0.12) * 0.5 + 0.5;
                    amp = wave * 20;
                    break;
                default:
                    amp = Math.sin(time * 1.5 + i * 0.3) * 2;
            }

            const r = baseR + amp;
            const x = cx + Math.cos(angle) * r;
            const y = cy + Math.sin(angle) * r;

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();

        const colors = {
            idle: 'rgba(0, 212, 255, 0.15)',
            listening: 'rgba(0, 245, 160, 0.25)',
            speaking: 'rgba(0, 212, 255, 0.3)',
            processing: 'rgba(255, 167, 38, 0.25)',
        };

        ctx.strokeStyle = colors[this.state] || colors.idle;
        ctx.lineWidth = 2;
        ctx.shadowColor = ctx.strokeStyle;
        ctx.shadowBlur = 10;
        ctx.stroke();

        requestAnimationFrame(() => this.animate());
    }
};
