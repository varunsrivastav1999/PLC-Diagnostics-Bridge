<template>
  <div class="app-shell">
    <header class="app-topbar">
      <div class="flex flex-col gap-2.5 xl:flex-row xl:items-center xl:justify-between">
        <div class="flex min-w-0 items-center gap-2.5">
          <div class="h-9 w-9 shrink-0 rounded-[0.95rem] border border-cyan-400/18 bg-slate-950/70 p-1.5 shadow-[0_16px_30px_rgba(8,145,178,0.14)] sm:h-10 sm:w-10 sm:rounded-[1rem]">
            <PlcBrandMark compact />
          </div>
          <div class="min-w-0">
            <div class="command-kicker">PLC Diagnostic Tool</div>
            <div class="mt-1 text-[0.95rem] font-semibold tracking-[-0.03em] text-white sm:text-[1.02rem]">
              Live data operations
            </div>
          </div>
        </div>

        <div class="app-topbar__summary">
          <div class="app-topbar__meta">
            <span class="app-topbar__label">Protocol</span>
            <div class="flex items-center gap-2">
              <span class="vendor-glyph">
                <PlcTypeIcon :type="store.connectionConfig.plc_type" />
              </span>
              <span class="app-topbar__value uppercase">{{ store.connectionConfig.plc_type }}</span>
            </div>
          </div>

          <div class="app-topbar__meta">
            <span class="app-topbar__label">IP Address</span>
            <span class="app-topbar__value app-topbar__value--mono">{{ activeIp }}</span>
          </div>

          <div class="app-topbar__meta">
            <span class="app-topbar__label">Port</span>
            <span class="app-topbar__value app-topbar__value--mono">{{ activePort }}</span>
          </div>

          <div class="app-topbar__meta">
            <span class="app-topbar__label">Link State</span>
            <div class="flex items-center gap-2">
              <span class="h-2.5 w-2.5 rounded-full" :class="store.isConnected ? 'bg-emerald-400 shadow-[0_0_14px_rgba(74,222,128,0.65)]' : 'bg-slate-600'"></span>
              <span class="app-topbar__value" :class="store.isConnected ? 'text-emerald-300' : 'text-slate-300'">
                {{ store.isConnected ? 'Live' : 'Standby' }}
              </span>
            </div>
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
import { computed, onMounted } from 'vue'
import DashboardView from './views/DashboardView.vue'
import Toast from 'primevue/toast'
import { usePlcStore } from './stores/plcStore'
import PlcBrandMark from './components/PlcBrandMark.vue'
import PlcTypeIcon from './components/PlcTypeIcon.vue'

const store = usePlcStore()

const activeIp = computed(() => store.connectionConfig.ip || '—')
const activePort = computed(() => `${store.connectionConfig.port ?? '—'}`)

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
