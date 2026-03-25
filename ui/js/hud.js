/**
 * AURIX — HUD Components (JARVIS Style)
 * Clock, system rings, and status updates
 */

const HUD = {
    sessionStartTime: Date.now(),

    init() {
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
        setInterval(() => this.updateSessionTime(), 1000);
        this.startStatsPoller();
    },

    updateClock() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');

        const clockEl = document.getElementById('jClock');
        const dateEl = document.getElementById('jDate');

        if (clockEl) clockEl.textContent = `${h}:${m}:${s}`;
        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: '2-digit'
            }).toUpperCase();
        }
    },

    updateSessionTime() {
        const elapsed = Math.floor((Date.now() - this.sessionStartTime) / 1000);
        const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const secs = String(elapsed % 60).padStart(2, '0');
        const el = document.getElementById('sessionTime');
        if (el) el.textContent = `${mins}:${secs}`;
    },

    updateCpuRing(percent) {
        const ring = document.getElementById('cpuRing');
        const val = document.getElementById('cpuVal');
        if (ring) {
            const circ = 2 * Math.PI * 130; // r=130
            ring.style.strokeDashoffset = circ - (percent / 100) * circ;
            if (percent > 80) ring.style.stroke = '#ff4444';
            else if (percent > 60) ring.style.stroke = '#ffbe0b';
            else ring.style.stroke = '#00d4ff';
        }
        if (val) val.textContent = `${Math.round(percent)}%`;
    },

    updateStats(stats) {
        if (stats.cpu_percent !== undefined) this.updateCpuRing(stats.cpu_percent);

        const ramEl = document.getElementById('ramVal');
        if (ramEl && stats.memory_percent !== undefined) ramEl.textContent = `${Math.round(stats.memory_percent)}%`;

        const diskEl = document.getElementById('diskVal');
        if (diskEl && stats.disk_percent !== undefined) diskEl.textContent = `${Math.round(stats.disk_percent)}%`;

        const netUpEl = document.getElementById('netUpVal');
        if (netUpEl && stats.net_sent_mb !== undefined) netUpEl.textContent = `${stats.net_sent_mb}M`;

        const netDownEl = document.getElementById('netDownVal');
        if (netDownEl && stats.net_recv_mb !== undefined) netDownEl.textContent = `${stats.net_recv_mb}M`;
    },

    setStatus(text, type = 'online') {
        const dot = document.querySelector('.j-status-dot');
        const textEl = document.getElementById('jStatusText');
        if (textEl) textEl.textContent = text;
        if (dot) {
            const colors = { online: '#00f5a0', thinking: '#00d4ff', listening: '#00f5a0', error: '#ff4444', speaking: '#ffa726' };
            dot.style.background = colors[type] || colors.online;
            dot.style.boxShadow = `0 0 8px ${colors[type] || colors.online}`;
        }
    },

    setVoiceBar(text, state = 'listening') {
        const bar = document.getElementById('voiceStatusBar');
        const textEl = document.getElementById('vsbText');
        const iconEl = document.getElementById('vsbIcon');

        if (bar) { bar.className = 'voice-status-bar ' + state; }
        if (textEl) textEl.textContent = text;
        if (iconEl) {
            const icons = { listening: '🎤', processing: '⚡', speaking: '🔊', idle: '⏸️' };
            iconEl.textContent = icons[state] || '🎤';
        }
    },

    setAiStatus(text) {
        const el = document.getElementById('aiVal');
        if (el) el.textContent = text;
    },

    async fetchStats() {
        try {
            const r = await fetch('/api/system/stats');
            const stats = await r.json();
            this.updateStats(stats);
        } catch (e) {}
    },

    startStatsPoller() {
        this.fetchStats();
        setInterval(() => this.fetchStats(), 3000);
    },
};
