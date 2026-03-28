<template>
  <div class="dashboard-grid h-full min-h-0">
    <aside class="dashboard-rail">
      <PlcConnectionForm />
    </aside>

    <section class="dashboard-workspace">
      <div class="workspace-strip">  
        <div class="workspace-strip__meta">
          <span class="vendor-glyph">
            <PlcTypeIcon :type="store.connectionConfig.plc_type" />
          </span>
          <span class="status-pill status-pill-soft uppercase">{{ store.connectionConfig.plc_type }}</span>
          <span class="status-pill status-pill-soft font-mono normal-case tracking-normal">{{ ipLabel }}</span>
          <span class="status-pill status-pill-soft font-mono normal-case tracking-normal">{{ portNumberLabel }}</span>
          <span class="status-pill" :class="store.isConnected ? 'status-pill-live' : 'status-pill-idle'">{{ sessionLabel }}</span>
          <span class="status-pill status-pill-soft">{{ portLabel }}</span>
          <span class="status-pill status-pill-soft">{{ responseLabel }}</span>
        </div>
      </div>

      <PlcDataForm class="w-full min-h-0 flex-1" />
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePlcStore } from '../stores/plcStore'
import PlcConnectionForm from '../components/PlcConnectionForm.vue'
import PlcDataForm from '../components/PlcDataForm.vue'
import PlcTypeIcon from '../components/PlcTypeIcon.vue'

const store = usePlcStore()

const ipLabel = computed(() => `IP ${store.connectionConfig.ip || '—'}`)
const portNumberLabel = computed(() => `Port ${store.connectionConfig.port ?? '—'}`)
const portLabel = computed(() => {
  if (store.portStatus === 'open') return 'Reachable'
  if (store.portStatus === 'closed') return 'Closed'
  if (store.portStatus === 'timeout') return 'Timeout'
  if (store.portStatus === 'dns_error') return 'DNS Error'
  if (store.portStatus === 'error') return 'Error'
  return 'Awaiting scan'
})
const responseLabel = computed(() => {
  if (store.responseTime) return `${store.responseTime} ms`
  return 'No sample'
})
const sessionLabel = computed(() => (store.isConnected ? 'Linked' : 'Standby'))
</script>
