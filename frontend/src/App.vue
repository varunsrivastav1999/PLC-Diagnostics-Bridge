<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-slate-950">
    <!-- Header -->
    <header class="shrink-0 w-full bg-slate-900/80 backdrop-blur-xl border-b border-slate-800/50 px-6 py-3 flex items-center justify-between z-50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-400 via-blue-500 to-indigo-600 flex items-center justify-center shadow-[0_0_20px_rgba(34,211,238,0.3)] p-1.5">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
            <!-- Chip body -->
            <rect x="9" y="9" width="14" height="14" rx="2" fill="white" fill-opacity="0.9"/>
            <!-- Pins top -->
            <rect x="12" y="5" width="2" height="5" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="15" y="5" width="2" height="5" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="18" y="5" width="2" height="5" rx="0.5" fill="white" fill-opacity="0.7"/>
            <!-- Pins bottom -->
            <rect x="12" y="22" width="2" height="5" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="15" y="22" width="2" height="5" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="18" y="22" width="2" height="5" rx="0.5" fill="white" fill-opacity="0.7"/>
            <!-- Pins left -->
            <rect x="5" y="12" width="5" height="2" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="5" y="15" width="5" height="2" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="5" y="18" width="5" height="2" rx="0.5" fill="white" fill-opacity="0.7"/>
            <!-- Pins right -->
            <rect x="22" y="12" width="5" height="2" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="22" y="15" width="5" height="2" rx="0.5" fill="white" fill-opacity="0.7"/>
            <rect x="22" y="18" width="5" height="2" rx="0.5" fill="white" fill-opacity="0.7"/>
            <!-- Center dot -->
            <circle cx="16" cy="16" r="2.5" fill="#3b82f6" opacity="0.8"/>
            <circle cx="16" cy="16" r="1" fill="white"/>
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-black tracking-[0.15em] text-white uppercase leading-tight">
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">PLC</span> Diagnostics
          </h1>
          <p class="text-[9px] font-bold tracking-[0.2em] text-slate-500 uppercase">Industrial Communication Bridge</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <div class="hidden md:flex items-center gap-4 text-[10px] font-bold tracking-widest text-slate-500 uppercase mr-4">
          <span>Siemens</span><span class="text-slate-700">|</span>
          <span>Mitsubishi</span><span class="text-slate-700">|</span>
          <span>Rockwell</span><span class="text-slate-700">|</span>
          <span>ABB</span><span class="text-slate-700">|</span>
          <span>Fanuc</span>
        </div>
        <div class="flex items-center gap-2 bg-slate-950/60 px-4 py-2 rounded-full border border-slate-800/60">
          <span class="relative flex h-2.5 w-2.5">
            <span v-if="store.isConnected" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5" :class="store.isConnected ? 'bg-emerald-500' : 'bg-slate-600'"></span>
          </span>
          <span class="text-[10px] font-black tracking-[0.15em] uppercase" :class="store.isConnected ? 'text-emerald-400' : 'text-slate-500'">
            {{ store.isConnected ? 'LINKED' : 'IDLE' }}
          </span>
        </div>
      </div>
    </header>

    <!-- Main Content - fills remaining space -->
    <main class="flex-1 overflow-hidden p-4 lg:p-5">
      <DashboardView class="h-full w-full" />
    </main>
  </div>
  <Toast />
</template>

<script setup>
import DashboardView from './views/DashboardView.vue'
import Toast from 'primevue/toast'
import { usePlcStore } from './stores/plcStore'
import { onMounted } from 'vue'

const store = usePlcStore()

onMounted(() => {
  window.addEventListener('beforeunload', () => {
    if (store.isConnected) {
      const data = new Blob([JSON.stringify({
        plc_type: store.connectionConfig.plc_type,
        ip: store.connectionConfig.ip,
        port: store.connectionConfig.port
      })], { type: 'application/json' });
      navigator.sendBeacon('/api/plc/disconnect', data);
    }
  });
})
</script>
