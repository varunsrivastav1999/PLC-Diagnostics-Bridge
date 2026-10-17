<template>
  <Card class="telemetry-card control-panel flex-1 min-h-0 overflow-hidden">
    <template #content>
      <div class="flex h-full min-h-0 flex-col">
        <form @submit.prevent="handleConnect" class="flex min-h-0 flex-1 flex-col gap-2.5 overflow-y-auto pr-1">
          <div class="rounded-[1rem] border border-white/8 bg-white/3 p-3">
            <div class="flex items-center justify-between gap-3">
              <label class="text-[0.58rem] font-semibold uppercase tracking-[0.18em] text-slate-500">Protocol</label>
              <span class="status-pill status-pill-soft">{{ getPlcDesc(store.connectionConfig.plc_type) }}</span>
            </div>

            <Dropdown
              v-model="store.connectionConfig.plc_type"
              :options="plcTypes"
              @change="onPlcTypeChange"
              class="compact-field mt-2.5 w-full"
              :disabled="store.isConnected"
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-3">
                  <div class="vendor-glyph">
                    <PlcTypeIcon :type="slotProps.value" />
                  </div>
                  <div class="flex min-w-0 flex-col">
                    <span class="truncate text-[0.95rem] font-semibold uppercase tracking-[0.16em] text-white">
                      {{ slotProps.value }}
                    </span>
                    <span class="text-[0.66rem] text-slate-500">{{ getPlcDesc(slotProps.value) }}</span>
                  </div>
                </div>
              </template>

              <template #option="slotProps">
                <div class="flex items-center gap-3 py-1">
                  <div class="vendor-glyph">
                    <PlcTypeIcon :type="slotProps.option" />
                  </div>
                  <div class="flex min-w-0 flex-col">
                    <span class="text-[0.9rem] font-semibold uppercase tracking-[0.16em] text-white">{{ slotProps.option }}</span>
                    <span class="text-[0.66rem] text-slate-500">{{ getPlcDesc(slotProps.option) }}</span>
                  </div>
                </div>
              </template>
            </Dropdown>
          </div>

          <!-- Network Target Deck -->
          <div class="rounded-2xl border border-white/8 bg-slate-900/40 p-3.5 backdrop-blur-md">
            <div class="flex items-center justify-between mb-2.5">
              <span class="text-[0.62rem] font-bold uppercase tracking-[0.16em] text-slate-400">Network Endpoint</span>
              <span v-if="isIpComplete" class="inline-flex items-center gap-1 text-[0.6rem] font-bold text-emerald-400">
                <i class="pi pi-check-circle text-[9px]"></i> COMPLETE
              </span>
              <span v-else class="text-[0.6rem] text-slate-500 font-mono">
                IPv4
              </span>
            </div>

            <!-- IP and Port Side by Side or Stacked -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div class="sm:col-span-2 relative">
                <label class="block text-[0.55rem] font-bold uppercase tracking-[0.16em] text-slate-500 mb-1">Target IP</label>
                <div class="relative">
                  <InputText
                    v-model="store.connectionConfig.ip"
                    placeholder="192.168.0.10"
                    class="compact-field w-full font-mono text-sm tracking-wider pr-7"
                    spellcheck="false"
                    autocomplete="off"
                    @blur="onIpBlur"
                    @keydown.enter.prevent="onIpEnter"
                  />
                  <button
                    v-if="store.connectionConfig.ip && !store.autoDetectingPort"
                    type="button"
                    @click="clearIp"
                    class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 p-0.5 text-[10px]"
                    title="Clear IP"
                  >
                    <i class="pi pi-times"></i>
                  </button>
                </div>
              </div>

              <div>
                <div class="flex items-center justify-between mb-1">
                  <label class="text-[0.55rem] font-bold uppercase tracking-[0.16em] text-slate-500">Port</label>
                  <span v-if="store.lastDetectedPort" class="text-[0.55rem] font-bold text-emerald-400">
                    AUTO
                  </span>
                </div>
                <InputText
                  v-model="portValue"
                  type="text"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  maxlength="5"
                  class="compact-field w-full font-mono text-sm transition-all duration-300"
                  :class="{'!border-emerald-500 !ring-2 !ring-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.25)]': highlightPort}"
                  spellcheck="false"
                  autocomplete="off"
                  :disabled="store.isConnected"
                />
              </div>
            </div>

            <div class="mt-2 flex items-center justify-between text-[0.58rem] text-slate-500 font-mono">
              <span>Default: {{ getDefaultPort(store.connectionConfig.plc_type) }}</span>
              <span v-if="store.isConnected" class="text-amber-400 font-semibold lowercase">
                editing IP auto-refreshes link
              </span>
            </div>

            <!-- Auto-Link Realtime Cockpit Banner -->
            <div class="auto-link-strip mt-3" :class="{
              'auto-link-strip--active': store.isConnected,
              'auto-link-strip--detecting': store.autoDetectingPort || store.autoConnecting,
              'auto-link-strip--refreshing': store.autoLinkStatus === 'refreshing'
            }">
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2 min-w-0">
                  <span class="relative flex h-2 w-2 shrink-0">
                    <span v-if="store.autoDetectingPort || store.autoConnecting" class="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-75"></span>
                    <span class="relative inline-flex h-2 w-2 rounded-full" :class="{
                      'bg-emerald-400 shadow-[0_0_8px_#34d399]': store.isConnected,
                      'bg-cyan-400 shadow-[0_0_8px_#00f0ff]': store.autoDetectingPort || store.autoConnecting,
                      'bg-amber-400': store.autoLinkStatus === 'refreshing',
                      'bg-slate-600': !store.isConnected && !store.autoDetectingPort && !store.autoConnecting && store.autoLinkStatus !== 'refreshing'
                    }"></span>
                  </span>
                  <span class="text-[0.62rem] font-bold uppercase tracking-wider truncate" :class="{
                    'text-emerald-400': store.isConnected,
                    'text-cyan-300': store.autoDetectingPort || store.autoConnecting,
                    'text-amber-300': store.autoLinkStatus === 'refreshing',
                    'text-slate-400': !store.isConnected && !store.autoDetectingPort && !store.autoConnecting && store.autoLinkStatus !== 'refreshing'
                  }">
                    {{ autoLinkStatusHeading }}
                  </span>
                </div>

                <div class="flex items-center gap-1.5 shrink-0">
                  <button
                    v-if="store.connectionConfig.plc_type === 'mitsubishi' && !store.autoDetectingPort"
                    type="button"
                    @click="triggerAutoLink(store.connectionConfig.ip)"
                    :disabled="!isIpComplete || store.isConnecting"
                    class="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10 active:scale-95 disabled:opacity-40 disabled:pointer-events-none transition-all"
                    title="Auto-Detect MC Port and Connect"
                  >
                    <i class="pi pi-bolt text-[8px] mr-0.5"></i> PROBE
                  </button>
                </div>
              </div>

              <div class="mt-1 text-[0.64rem] font-medium leading-4" :class="store.isConnected ? 'text-slate-300 font-mono' : 'text-slate-400'">
                {{ store.autoLinkMessage }}
              </div>

              <div v-if="store.autoDetectingPort || store.autoConnecting" class="auto-link-progress-bar"></div>
            </div>

            <!-- Discovery Action Tools -->
            <div class="mt-2.5 flex items-center gap-1.5" v-if="store.connectionConfig.plc_type === 'mitsubishi' && !store.isConnected">
              <button
                type="button"
                @click="handleDiscoverPorts"
                :disabled="discoveringPorts || scanningSubnet || !store.connectionConfig.ip"
                class="flex-1 flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-lg text-[9px] font-black tracking-widest uppercase transition-all border"
                :class="discoveringPorts
                  ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400 cursor-wait'
                  : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 active:scale-95'"
              >
                <i :class="discoveringPorts ? 'pi pi-spin pi-spinner' : 'pi pi-search'" style="font-size: 9px;"></i>
                {{ discoveringPorts ? 'SCANNING...' : 'SCAN MC PORTS' }}
              </button>
              <button
                type="button"
                @click="handleSubnetScan"
                :disabled="discoveringPorts || scanningSubnet || !store.connectionConfig.ip"
                class="flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-lg text-[9px] font-black tracking-widest uppercase transition-all border border-slate-700 bg-slate-800/40 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 active:scale-95"
                title="Scan entire /24 subnet for Mitsubishi PLCs"
              >
                <i :class="scanningSubnet ? 'pi pi-spin pi-spinner' : 'pi pi-sitemap'" style="font-size: 9px;"></i>
                {{ scanningSubnet ? 'SUBNET...' : 'SUBNET SCAN' }}
              </button>
            </div>
          </div>

          <div v-if="store.connectionConfig.plc_type === 'siemens'" class="grid grid-cols-2 gap-2.5 animate-fadein">
            <div class="rounded-[1rem] border border-cyan-400/8 bg-cyan-400/[0.03] p-3">
              <label class="text-[0.58rem] font-semibold uppercase tracking-[0.18em] text-slate-500">Rack</label>
              <InputText
                type="number"
                v-model.number="store.connectionConfig.rack"
                class="compact-field mt-2.5 w-full font-mono text-sm"
                :disabled="store.isConnected"
              />
            </div>
            <div class="rounded-[1rem] border border-cyan-400/8 bg-cyan-400/[0.03] p-3">
              <label class="text-[0.58rem] font-semibold uppercase tracking-[0.18em] text-slate-500">Slot</label>
              <InputText
                type="number"
                v-model.number="store.connectionConfig.slot"
                class="compact-field mt-2.5 w-full font-mono text-sm"
                :disabled="store.isConnected"
              />
            </div>
          </div>

          <div class="bg-gradient-to-r rounded-[1rem] border border-white/8 from-slate-900/90 via-slate-900/75 to-cyan-950/25 p-3 animate-fadein">
            <div class="flex items-center gap-3">
              <Checkbox
                v-model="portCheckEnabled"
                :binary="true"
                inputId="port-diagnostics"
                @change="handlePortCheck"
                :disabled="store.checkingPort"
                class="cursor-pointer"
              />
              <label for="port-diagnostics" class="flex-1 cursor-pointer text-[0.62rem] font-semibold uppercase tracking-[0.2em] text-slate-400">
                Port Diagnostics
              </label>

              <ProgressSpinner v-if="store.checkingPort" style="width: 18px; height: 18px" :strokeWidth="4" />
              <template v-else-if="portCheckEnabled">
                <Tag
                  :value="getPortStatusText()"
                  :severity="getPortStatusSeverity()"
                  :class="[getPortStatusClass(), 'text-[0.64rem] font-semibold px-2.5 py-1 shadow-sm']"
                />
              </template>
            </div>

            <div v-if="portCheckEnabled" class="mt-3 flex items-center gap-2">
              <Checkbox
                v-model="continuousMonitoring"
                :binary="true"
                inputId="continuous-monitoring"
                @change="handleContinuousToggle"
                class="cursor-pointer"
              />
              <label for="continuous-monitoring" class="cursor-pointer text-[0.62rem] font-medium uppercase tracking-[0.16em] text-slate-500">
                Continuous Monitoring
              </label>
              <i v-if="continuousMonitoring" class="pi pi-refresh text-emerald-400 text-[10px] animate-spin"></i>
            </div>

            <div v-if="portCheckEnabled && !store.checkingPort" class="mt-2.5 grid grid-cols-2 gap-2">
              <div class="flex flex-col p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span class="text-[9px] font-mono font-bold uppercase tracking-wider text-slate-400">Status</span>
                <span class="text-xs font-mono font-black mt-0.5" :class="store.portStatus === 'open' ? 'text-emerald-400' : 'text-rose-400'">
                  {{ store.portStatus.toUpperCase() }}
                </span>
              </div>
              <div class="flex flex-col p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span class="text-[9px] font-mono font-bold uppercase tracking-wider text-slate-400">Response</span>
                <span class="text-xs font-mono font-black text-cyan-400 mt-0.5">
                  {{ store.responseTime ? `${store.responseTime}ms` : '—' }}
                </span>
              </div>
            </div>

            <p v-if="portCheckEnabled && !store.checkingPort" class="mt-3 text-xs leading-5 text-slate-500">
              {{ store.portMessage }}
            </p>
          </div>

          <div class="mt-auto border-t border-white/8 pt-3">
            <Button
              v-if="!store.isConnected"
              type="submit"
              label="CONNECT"
              icon="pi pi-power-off"
              class="action-button action-button--connect w-full"
              :loading="store.isConnecting"
            />

            <Button
              v-else
              type="button"
              @click="handleDisconnect"
              label="DISCONNECT"
              icon="pi pi-power-off"
              class="action-button action-button--disconnect w-full"
            />
          </div>
        </form>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { usePlcStore } from '../stores/plcStore'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'
import PlcTypeIcon from './PlcTypeIcon.vue'
import api from '../services/api'

const store = usePlcStore()
const toast = useToast()

const plcTypes = ref(['siemens', 'mitsubishi', 'rockwell', 'abb', 'fanuc', 'opcua'])
const portCheckEnabled = ref(false)
const continuousMonitoring = ref(false)
const monitoringInterval = ref(null)
const discoveringPorts = ref(false)
const scanningSubnet = ref(false)
const autoCheckTimeout = ref(null)

const isCompleteIpv4 = (ip) => {
  if (!ip || typeof ip !== 'string') return false
  const trimmed = ip.trim()
  if (trimmed.startsWith('opc.tcp://')) return trimmed.length > 10
  const parts = trimmed.split('.')
  if (parts.length !== 4) return false
  return parts.every(part => part.length > 0 && /^\d+$/.test(part) && Number(part) >= 0 && Number(part) <= 255)
}

const isValidIp = (ip) => {
  return isCompleteIpv4(ip)
}

const isIpComplete = computed(() => isCompleteIpv4(store.connectionConfig.ip))

const autoLinkStatusHeading = computed(() => {
  if (store.isConnected) return 'LIVE MC LINK ACTIVE'
  if (store.autoDetectingPort) return 'PROBING MC PORTS...'
  if (store.autoConnecting) return 'ESTABLISHING HANDSHAKE...'
  if (store.autoLinkStatus === 'refreshing') return 'SESSION REFRESHED'
  if (store.autoLinkStatus === 'failed') return 'AUTO-LINK ALERT'
  return 'AUTO-LINK READY'
})

const isValidPort = (port) => {
  const portNum = parseInt(port)
  return portNum > 0 && portNum <= 65535
}

const portValue = computed({
  get: () => String(store.connectionConfig.port ?? ''),
  set: (value) => {
    const digitsOnly = String(value ?? '').replace(/\D+/g, '').slice(0, 5)
    store.connectionConfig.port = digitsOnly ? Number(digitsOnly) : null
  }
})

const debouncedAutoCheck = () => {
  if (autoCheckTimeout.value) {
    clearTimeout(autoCheckTimeout.value)
  }
  autoCheckTimeout.value = setTimeout(() => {
    autoCheckPortStatus()
  }, 800)
}

const getPlcDesc = (type) => {
  const map = {
    siemens: 'S7 Comm · Snap7',
    mitsubishi: 'MC Protocol',
    rockwell: 'EtherNet/IP',
    abb: 'Modbus TCP',
    fanuc: 'Fanuc FTP Bridge',
    opcua: 'OPC-UA (IEC 62541)',
  }
  return map[type] || 'Protocol'
}

const getDefaultPort = (type) => {
  const ports = {
    siemens: 102,
    mitsubishi: 5000,
    rockwell: 44818,
    abb: 502,
    fanuc: 21,
    opcua: 4840,
  }
  return ports[type] ?? '—'
}

const getPortStatusText = () => {
  if (store.portStatus === 'open') return 'REACHABLE'
  if (store.portStatus === 'closed') return 'UNREACHABLE'
  if (store.portBusy === true) return 'REACHABLE'
  if (store.portBusy === false) return 'UNREACHABLE'
  return store.portStatus.toUpperCase()
}

const getPortStatusSeverity = () => {
  if (store.portStatus === 'open') return 'success'
  if (store.portStatus === 'closed') return 'danger'
  if (store.portStatus === 'timeout') return 'warn'
  if (store.portStatus === 'error' || store.portStatus === 'dns_error') return 'danger'
  if (store.portBusy === true) return 'success'
  if (store.portBusy === false) return 'danger'
  return 'info'
}

const getPortStatusClass = () => {
  if (store.portStatus === 'open') return 'port-free-tag'
  if (store.portStatus === 'closed') return 'port-busy-tag'
  if (store.portStatus === 'timeout') return 'port-timeout-tag'
  if (store.portStatus === 'error' || store.portStatus === 'dns_error') return 'port-error-tag'
  if (store.portBusy === true) return 'port-free-tag'
  if (store.portBusy === false) return 'port-busy-tag'
  return 'port-unknown-tag'
}

onMounted(() => {
  store.fetchSupportedTypes().then(() => {
    if (store.supportedTypes.length) plcTypes.value = store.supportedTypes
  })

  setTimeout(() => {
    autoCheckPortStatus()
  }, 1000)
})

// ── Auto-Detect MC Port & Auto-Connect Controller ──
let autoLinkDebounceTimer = null
let currentScanToken = 0

const triggerAutoLink = async (targetIp) => {
  const ip = (targetIp || store.connectionConfig.ip || '').trim()
  if (!isCompleteIpv4(ip)) return
  if (store.isConnected) return
  if (store.autoDetectingPort || store.autoConnecting) return

  const thisToken = ++currentScanToken

  if (store.connectionConfig.plc_type === 'mitsubishi') {
    highlightPort.value = true
    discoveringPorts.value = true
    
    const result = await store.autoDiscoverAndConnect(ip)
    
    // Check if token was superseded by a newer IP change
    if (thisToken !== currentScanToken) return

    discoveringPorts.value = false
    setTimeout(() => { highlightPort.value = false }, 2500)

    if (result.success) {
      toast.add({
        severity: 'success',
        summary: `✓ MC Port ${store.connectionConfig.port} Auto-Connected`,
        detail: `Detected MC Protocol on port ${store.connectionConfig.port} and established live connection to ${ip}`,
        life: 4000
      })
    } else {
      toast.add({
        severity: 'warn',
        summary: 'MC Auto-Link',
        detail: result.message || 'Auto-connect could not be completed.',
        life: 6000
      })
    }
  } else {
    // Other protocols: connect with default or configured port
    store.autoLinkStatus = 'connecting'
    store.autoLinkMessage = `Connecting to ${store.connectionConfig.plc_type} on ${ip}:${store.connectionConfig.port}...`
    const connResult = await store.connectPlc()
    if (thisToken !== currentScanToken) return

    if (connResult.success) {
      store.autoLinkStatus = 'connected'
      store.autoLinkMessage = `✓ Linked to ${store.connectionConfig.plc_type} at ${ip}:${store.connectionConfig.port}`
      toast.add({
        severity: 'success',
        summary: 'Connected',
        detail: connResult.message,
        life: 3000
      })
    } else {
      store.autoLinkStatus = 'failed'
      store.autoLinkMessage = `Connection failed: ${connResult.message}`
    }
  }
}

// Watch IP changes: automatically refresh existing connection and trigger auto-detect
watch(() => store.connectionConfig.ip, async (newIp, oldIp) => {
  if (newIp === oldIp) return

  if (autoLinkDebounceTimer) {
    clearTimeout(autoLinkDebounceTimer)
    autoLinkDebounceTimer = null
  }

  currentScanToken++

  // If IP changed while connected, automatically refresh session and disconnect old link
  if (store.isConnected) {
    await store.disconnectPlc()
    store.resetAutoLink(`IP changed to "${newIp}". Old session cleared; detecting new target...`)
    toast.add({
      severity: 'info',
      summary: 'IP Changed · Session Refreshed',
      detail: `Disconnected previous target. Refreshing for new IP: ${newIp}`,
      life: 3000
    })
  } else if (store.autoLinkStatus === 'connected') {
    store.resetAutoLink('Target IP modified. Ready for new address.')
  }

  // When IP input is completed, automatically detect the MC port and connect
  if (isCompleteIpv4(newIp)) {
    debouncedAutoCheck()

    if (store.autoLinkEnabled) {
      store.autoLinkStatus = 'refreshing'
      store.autoLinkMessage = `Valid IP entered (${newIp}). Auto-detecting MC port in 500ms...`
      autoLinkDebounceTimer = setTimeout(() => {
        triggerAutoLink(newIp)
      }, 500)
    }
  } else {
    store.autoLinkStatus = 'refreshing'
    store.autoLinkMessage = 'Entering IP address... (awaiting full IPv4)'
  }
})

const onIpBlur = () => {
  if (isCompleteIpv4(store.connectionConfig.ip) && !store.isConnected && store.autoLinkEnabled) {
    if (autoLinkDebounceTimer) {
      clearTimeout(autoLinkDebounceTimer)
      autoLinkDebounceTimer = null
    }
    triggerAutoLink(store.connectionConfig.ip)
  }
}

const onIpEnter = () => {
  if (isCompleteIpv4(store.connectionConfig.ip) && !store.isConnected) {
    if (autoLinkDebounceTimer) {
      clearTimeout(autoLinkDebounceTimer)
      autoLinkDebounceTimer = null
    }
    triggerAutoLink(store.connectionConfig.ip)
  }
}

const clearIp = async () => {
  if (store.isConnected) {
    await store.disconnectPlc()
  }
  store.connectionConfig.ip = ''
  store.resetAutoLink('IP cleared. Enter new IP address.')
}

watch(() => store.connectionConfig.port, (newPort, oldPort) => {
  if (newPort !== oldPort && isValidPort(newPort) && store.connectionConfig.ip) {
    debouncedAutoCheck()
  }
})

watch(() => store.connectionConfig.plc_type, (newType, oldType) => {
  if (newType !== oldType && store.connectionConfig.ip && store.connectionConfig.port) {
    portCheckEnabled.value = false
    continuousMonitoring.value = false
    stopContinuousMonitoring()
    setTimeout(() => autoCheckPortStatus(), 300)
  }
})

const onPlcTypeChange = () => {
  const type = store.connectionConfig.plc_type
  portCheckEnabled.value = false

  if (type === 'siemens') store.connectionConfig.port = 102
  else if (type === 'mitsubishi') {
    store.connectionConfig.port = 5000
    if (isCompleteIpv4(store.connectionConfig.ip) && store.autoLinkEnabled && !store.isConnected) {
      setTimeout(() => triggerAutoLink(store.connectionConfig.ip), 200)
    }
  }
  else if (type === 'abb') store.connectionConfig.port = 502
  else if (type === 'rockwell') store.connectionConfig.port = 44818
  else if (type === 'fanuc') store.connectionConfig.port = 21
  else if (type === 'opcua') store.connectionConfig.port = 4840
}

const handleConnect = async () => {
  if (!isValidIp(store.connectionConfig.ip)) {
    toast.add({ severity: 'warn', summary: 'Invalid IP', detail: 'Enter a valid IPv4 address before connecting.', life: 3000 })
    return
  }
  if (!isValidPort(store.connectionConfig.port)) {
    toast.add({ severity: 'warn', summary: 'Invalid Port', detail: 'Enter a valid TCP port between 1 and 65535.', life: 3000 })
    return
  }

  const result = await store.connectPlc()
  if (result.success) toast.add({ severity: 'success', summary: 'Connected', detail: result.message, life: 3000 })
  else toast.add({ severity: 'error', summary: 'Failed', detail: result.message, life: 5000 })
}

const handleDisconnect = async () => {
  const result = await store.disconnectPlc()
  toast.add({ severity: 'info', summary: 'Disconnected', detail: result.message, life: 3000 })
}

const highlightPort = ref(false)

const handleDiscoverPorts = async () => {
  if (!store.connectionConfig.ip || discoveringPorts.value) return
  discoveringPorts.value = true
  toast.add({ severity: 'info', summary: 'Scanning', detail: `Scanning ${store.connectionConfig.ip} — checking 55+ MC Protocol ports...`, life: 4000 })
  try {
    const res = await api.discoverPorts(store.connectionConfig.ip)
    const data = res.data
    if (data.success && data.recommended_port) {
      store.connectionConfig.port = data.recommended_port
      
      // Visual feedback: briefly highlight the port input
      highlightPort.value = true
      setTimeout(() => { highlightPort.value = false }, 2000)

      const discovery = data.discovery || {}
      const mcPorts = discovery.mc_ports || []
      toast.add({
        severity: 'success',
        summary: `✓ MC Port ${data.recommended_port} Auto-Detected`,
        detail: `MC Protocol active on port${mcPorts.length > 1 ? 's' : ''}: ${mcPorts.join(', ')} — scanned ${discovery.ports_scanned} ports in ${discovery.scan_time_ms}ms`,
        life: 6000
      })
    } else {
      // Show detailed diagnosis from backend
      const diagnosis = data.diagnosis || data.discovery?.diagnosis || 'No MC Protocol ports detected.'
      const discovery = data.discovery || {}
      const tcpPorts = discovery.tcp_ports || []
      const summary = discovery.reachable === false
        ? 'PLC Not Reachable'
        : tcpPorts.length > 0
          ? `TCP Open (${tcpPorts.join(',')}) — No MC Protocol`
          : 'No MC Port Found'
      toast.add({
        severity: 'warn',
        summary,
        detail: diagnosis,
        life: 10000
      })
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Scan Failed', detail: e.message, life: 5000 })
  } finally {
    discoveringPorts.value = false
  }
}

const handleSubnetScan = async () => {
  if (!store.connectionConfig.ip || scanningSubnet.value) return
  scanningSubnet.value = true
  const ip = store.connectionConfig.ip
  const subnet = ip.split('.').slice(0, 3).join('.') + '.0/24'
  toast.add({ severity: 'info', summary: `Scanning ${subnet}`, detail: 'Checking 254 IPs × 22 ports with 32 threads — this takes ~15-30 seconds...', life: 8000 })
  try {
    const res = await api.discoverSubnet(ip)
    const data = res.data
    const plcs = data.plcs_found || []
    if (plcs.length > 0) {
      // Auto-fill with the first found PLC
      const first = plcs[0]
      store.connectionConfig.ip = first.ip
      store.connectionConfig.port = first.mc_ports[0]
      
      highlightPort.value = true
      setTimeout(() => { highlightPort.value = false }, 2000)
      const plcList = plcs.map(p => `${p.ip}:${p.mc_ports.join(',')}`).join(' | ')
      toast.add({
        severity: 'success',
        summary: `✓ Found ${plcs.length} Mitsubishi PLC(s)`,
        detail: `${plcList} — auto-filled ${first.ip}:${first.mc_ports[0]} (scan: ${data.scan_time_ms}ms)`,
        life: 10000
      })
    } else {
      const reachable = data.reachable_ips || []
      toast.add({
        severity: 'warn',
        summary: `No Mitsubishi PLCs on ${subnet}`,
        detail: reachable.length > 0
          ? `${reachable.length} device(s) found with open TCP ports but none running MC Protocol: ${reachable.slice(0, 8).join(', ')}${reachable.length > 8 ? '...' : ''}`
          : `No devices with open MC Protocol ports found on the subnet. Check PLC network configuration.`,
        life: 10000
      })
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Subnet Scan Failed', detail: e.message, life: 5000 })
  } finally {
    scanningSubnet.value = false
  }
}

const handlePortCheck = async () => {
  if (continuousMonitoring.value) {
    startContinuousMonitoring()
  } else {
    stopContinuousMonitoring()
    await performPortCheck()
  }
}

const performPortCheck = async () => {
  const result = await store.checkPortBusy()
  if (result.success) {
    const status = result.port_status || 'unknown'
    let severity = 'info'
    let summary = 'Port Status'

    switch (status) {
      case 'open':
        severity = 'success'
        summary = 'Port Reachable'
        break
      case 'closed':
        severity = 'error'
        summary = 'Port Unreachable'
        break
      case 'timeout':
        severity = 'warn'
        summary = 'Port Timeout'
        break
      case 'error':
      case 'dns_error':
        severity = 'error'
        summary = 'Port Check Error'
        break
      default:
        severity = 'info'
        summary = 'Port Status Unknown'
    }

    toast.add({
      severity,
      summary: `${summary}${result.response_time ? ` (${result.response_time}ms)` : ''}`,
      detail: result.message,
      life: 4000
    })

    if (status === 'closed' && !continuousMonitoring.value) {
      setTimeout(() => {
        portCheckEnabled.value = false
      }, 3000)
    }
  } else {
    if (!continuousMonitoring.value) {
      portCheckEnabled.value = false
    }
    toast.add({ severity: 'error', summary: 'Check Failed', detail: result.message, life: 3000 })
  }
}

const startContinuousMonitoring = () => {
  if (monitoringInterval.value) return

  monitoringInterval.value = setInterval(async () => {
    if (portCheckEnabled.value && continuousMonitoring.value) {
      await performPortCheck()
    }
  }, 5000)

  toast.add({
    severity: 'info',
    summary: 'Monitoring Started',
    detail: 'Port status will be checked every 5 seconds',
    life: 3000
  })
}

const stopContinuousMonitoring = () => {
  if (monitoringInterval.value) {
    clearInterval(monitoringInterval.value)
    monitoringInterval.value = null
    toast.add({
      severity: 'info',
      summary: 'Monitoring Stopped',
      detail: 'Continuous port monitoring disabled',
      life: 2000
    })
  }
}

const handleContinuousToggle = () => {
  if (continuousMonitoring.value) {
    startContinuousMonitoring()
  } else {
    stopContinuousMonitoring()
  }
}

const autoCheckPortStatus = async () => {
  if (!portCheckEnabled.value && !store.checkingPort && store.connectionConfig.ip && store.connectionConfig.port) {
    try {
      const result = await store.checkPortBusy()
      if (result.success) {
        portCheckEnabled.value = true

        if (result.port_status === 'closed') {
          setTimeout(() => {
            if (!continuousMonitoring.value) {
              portCheckEnabled.value = false
            }
          }, 5000)
        }
      }
    } catch (error) {
      console.log('Auto port check failed:', error)
    }
  }
}

onUnmounted(() => {
  if (autoCheckTimeout.value) {
    clearTimeout(autoCheckTimeout.value)
  }
  if (monitoringInterval.value) {
    clearInterval(monitoringInterval.value)
  }
})
</script>
