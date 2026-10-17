<template>
  <div class="app-shell">
    <header class="app-topbar">
      <div class="flex flex-col gap-2.5 xl:flex-row xl:items-center xl:justify-between">
        <div class="flex min-w-0 items-center gap-3">
          <div class="relative h-9 w-9 shrink-0 rounded-xl border border-cyan-400/30 bg-slate-950/90 p-1.5 shadow-[0_0_20px_rgba(0,240,255,0.2)] sm:h-10 sm:w-10 sm:rounded-2xl">
            <PlcBrandMark compact />
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <span class="command-kicker font-black text-cyan-400 text-xs">PLC Diagnostics Bridge</span>
              <span class="badge-v3-pill text-[9px] py-0.5 px-2">v3.0 NEXT-GEN</span>
            </div>
            <div class="text-[0.78rem] font-medium text-slate-400 tracking-wide">
              Industrial Fieldbus &amp; Diagnostics Suite
            </div>
          </div>
        </div>

        <!-- Sleek High-Tech Cockpit Status Bar -->
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Protocol & Endpoint Capsule -->
          <div class="flex items-center gap-2 rounded-xl border border-slate-800/80 bg-slate-900/60 px-3 py-1.5 backdrop-blur-md">
            <span class="vendor-glyph !h-5 !w-5 !rounded-md">
              <PlcTypeIcon :type="store.connectionConfig.plc_type" />
            </span>
            <span class="text-xs font-bold uppercase tracking-wider text-white">
              {{ store.connectionConfig.plc_type }}
            </span>
            <span class="text-slate-600 font-mono">|</span>
            <span class="font-mono text-xs text-slate-300">
              {{ activeIp }}:{{ activePort }}
            </span>
            <span v-if="store.lastDetectedPort" class="rounded px-1.5 py-0.2 text-[8px] font-black uppercase tracking-wider bg-emerald-500/15 border border-emerald-500/30 text-emerald-400">
              MC {{ store.lastDetectedPort }}
            </span>
          </div>

          <!-- Link Telemetry Status Capsule -->
          <div class="flex items-center gap-2 rounded-xl border px-3 py-1.5 backdrop-blur-md transition-all duration-300"
               :class="store.isConnected
                 ? 'border-emerald-500/30 bg-emerald-950/20 shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                 : (store.autoDetectingPort || store.autoConnecting)
                   ? 'border-cyan-500/40 bg-cyan-950/20 shadow-[0_0_15px_rgba(0,240,255,0.15)] animate-pulse'
                   : 'border-slate-800/80 bg-slate-900/60'">
            <span class="relative flex h-2 w-2">
              <span v-if="store.isConnected" class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span v-else-if="store.autoDetectingPort || store.autoConnecting" class="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-75"></span>
              <span class="relative inline-flex h-2 w-2 rounded-full"
                    :class="store.isConnected
                      ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]'
                      : (store.autoDetectingPort || store.autoConnecting)
                        ? 'bg-cyan-400 shadow-[0_0_8px_#00f0ff]'
                        : 'bg-slate-500'"></span>
            </span>
            <span class="text-[10px] font-black tracking-widest uppercase"
                  :class="store.isConnected ? 'text-emerald-300' : (store.autoDetectingPort || store.autoConnecting) ? 'text-cyan-300' : 'text-slate-400'">
              <template v-if="store.isConnected">LIVE LINKED</template>
              <template v-else-if="store.autoDetectingPort">SCANNING MC PORTS...</template>
              <template v-else-if="store.autoConnecting">HANDSHAKING...</template>
              <template v-else-if="store.autoLinkStatus === 'refreshing'">REFRESHED</template>
              <template v-else>STANDBY</template>
            </span>
            <span v-if="store.responseTime && store.isConnected" class="font-mono text-[10px] text-emerald-400/80 border-l border-emerald-500/20 pl-2">
              {{ store.responseTime }}ms
            </span>
          </div>
          <!-- Indian Standard Time (IST) Clock Capsule -->
          <div class="hidden sm:flex items-center gap-2 rounded-xl border border-slate-800/80 bg-slate-900/60 px-3 py-1.5 backdrop-blur-md">
            <i class="pi pi-clock text-[10px] text-cyan-400"></i>
            <span class="font-mono text-xs text-slate-200 font-bold">
              {{ currentIstTime }}
            </span>
            <span class="rounded px-1.5 py-0.2 text-[8px] font-black uppercase tracking-wider bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
              IST
            </span>
          </div>
        </div>
      </div>
    </header>

    <main class="app-main flex-1 px-3 pb-3 pt-2 lg:px-4 lg:pb-4">
      <DashboardView class="h-full w-full" />
    </main>
  </div>
  <Toast />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import DashboardView from './views/DashboardView.vue'
import Toast from 'primevue/toast'
import { usePlcStore } from './stores/plcStore'
import PlcBrandMark from './components/PlcBrandMark.vue'
import PlcTypeIcon from './components/PlcTypeIcon.vue'

const store = usePlcStore()

const activeIp = computed(() => store.connectionConfig.ip || '—')
const activePort = computed(() => `${store.connectionConfig.port ?? '—'}`)

const currentIstTime = ref('')
let clockTimer = null

const updateClock = () => {
  const parts = new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  }).formatToParts(new Date());

  let hour = '', minute = '', second = '', dayPeriod = '';
  for (const p of parts) {
    if (p.type === 'hour') hour = p.value;
    else if (p.type === 'minute') minute = p.value;
    else if (p.type === 'second') second = p.value;
    else if (p.type === 'dayPeriod') dayPeriod = p.value.toUpperCase();
  }
  currentIstTime.value = `${hour.padStart(2, '0')}:${minute}:${second} ${dayPeriod}`;
}

onMounted(() => {
  updateClock();
  clockTimer = setInterval(updateClock, 1000);

  window.addEventListener('beforeunload', () => {
    if (store.isConnected) {
      const payload = JSON.stringify({
        plc_type: store.connectionConfig.plc_type,
        ip: store.connectionConfig.ip,
        port: store.connectionConfig.port
      });
      try {
        fetch('/api/plc/disconnect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: payload,
          keepalive: true
        });
      } catch {
        if (navigator.sendBeacon) {
          const blob = new Blob([payload], { type: 'application/json' });
          navigator.sendBeacon('/api/plc/disconnect', blob);
        }
      }
    }
  });
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer);
})
</script>
