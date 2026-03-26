<template>
  <Card class="flex-1 border-0 overflow-hidden">
    <template #content>
      <div class="flex items-center gap-2 mb-4">
        <i class="pi pi-link text-indigo-400 text-sm"></i>
        <h2 class="text-[10px] font-black tracking-[0.2em] text-indigo-400 uppercase">Uplink Configuration</h2>
      </div>
      
      <form @submit.prevent="handleConnect" class="flex flex-col gap-3">
        <!-- PLC Brand -->
        <div class="flex flex-col gap-1">
          <label class="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Protocol</label>
          <Dropdown v-model="store.connectionConfig.plc_type" :options="plcTypes" @change="onPlcTypeChange" 
                    class="w-full" :disabled="store.isConnected">
            <template #value="slotProps">
              <div v-if="slotProps.value" class="flex items-center gap-2">
                <div class="h-5 w-5 rounded bg-indigo-500/15 flex items-center justify-center border border-indigo-500/30">
                   <i :class="getPlcIcon(slotProps.value)" class="text-indigo-400" style="font-size: 9px;"></i>
                </div>
                <span class="tracking-widest uppercase font-bold text-xs">{{ slotProps.value }}</span>
                <span class="text-[8px] text-slate-500 ml-auto">{{ getPlcDesc(slotProps.value) }}</span>
              </div>
            </template>
            <template #option="slotProps">
              <div class="flex items-center gap-3 py-0.5">
                <div class="h-7 w-7 rounded-lg bg-slate-800/80 flex items-center justify-center border border-slate-700/50">
                   <i :class="getPlcIcon(slotProps.option)" class="text-slate-300" style="font-size: 10px;"></i>
                </div>
                <div class="flex flex-col">
                  <span class="font-bold tracking-widest text-white uppercase text-xs">{{ slotProps.option }}</span>
                  <span class="text-[8px] text-slate-500 tracking-wider">{{ getPlcDesc(slotProps.option) }}</span>
                </div>
              </div>
            </template>
          </Dropdown>
        </div>
        
        <!-- IP & Port -->
        <div class="grid grid-cols-3 gap-2">
          <div class="col-span-2 flex flex-col gap-1">
            <label class="text-[10px] font-bold text-slate-500 tracking-widest uppercase">IPv4 Address</label>
            <InputText v-model="store.connectionConfig.ip" placeholder="192.168.0.10" class="font-mono text-xs" :disabled="store.isConnected" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Port</label>
            <InputText type="number" v-model.number="store.connectionConfig.port" class="font-mono text-xs" :disabled="store.isConnected" />
          </div>
        </div>
        
        <!-- Siemens extras -->
        <div v-if="store.connectionConfig.plc_type === 'siemens'" class="grid grid-cols-2 gap-2 animate-fadein">
          <div class="flex flex-col gap-1">
            <label class="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Rack</label>
            <InputText type="number" v-model.number="store.connectionConfig.rack" class="font-mono text-xs" :disabled="store.isConnected" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[10px] font-bold text-slate-500 tracking-widest uppercase">Slot</label>
            <InputText type="number" v-model.number="store.connectionConfig.slot" class="font-mono text-xs" :disabled="store.isConnected" />
          </div>
        </div>

        <!-- Port Status Check -->
        <div class="flex flex-col gap-2 p-3 bg-gradient-to-r from-slate-800/40 to-slate-800/20 rounded border border-slate-700/60 animate-fadein">
          <div class="flex items-center gap-3">
            <Checkbox v-model="portCheckEnabled" @change="handlePortCheck" :disabled="store.checkingPort" class="cursor-pointer" />
            <label class="text-[10px] font-bold text-slate-400 tracking-widest uppercase cursor-pointer flex-1">Identify Port Status</label>
            <ProgressSpinner v-if="store.checkingPort" style="width: 18px; height: 18px" :strokeWidth="4" />
            <template v-else>
              <Tag v-if="portCheckEnabled" :value="getPortStatusText()" 
                   :class="getPortStatusClass()"
                   class="text-[8px] font-bold px-2 py-0.5 shadow-sm" />
            </template>
          </div>
          
          <!-- Continuous Monitoring Toggle -->
          <div v-if="portCheckEnabled" class="flex items-center gap-2">
            <Checkbox v-model="continuousMonitoring" @change="handleContinuousToggle" class="cursor-pointer" />
            <label class="text-[9px] font-medium text-slate-500 tracking-wider uppercase cursor-pointer">Continuous Monitoring</label>
            <i v-if="continuousMonitoring" class="pi pi-refresh text-green-400 text-[8px] animate-spin"></i>
          </div>
          
          <!-- Detailed Port Info -->
          <div v-if="portCheckEnabled && !store.checkingPort" class="flex flex-col gap-1 text-[9px] text-slate-500">
            <div class="flex justify-between">
              <span>Status:</span>
              <span class="font-mono text-slate-400">{{ store.portStatus.toUpperCase() }}</span>
            </div>
            <div v-if="store.responseTime" class="flex justify-between">
              <span>Response:</span>
              <span class="font-mono text-slate-400">{{ store.responseTime }}ms</span>
            </div>
            <div class="text-[8px] text-slate-600 italic mt-1">
              {{ store.portMessage }}
            </div>
          </div>
        </div>

        <!-- Buttons -->
        <div class="flex gap-2 mt-2 pt-3 border-t border-slate-800/50">
          <Button v-if="!store.isConnected" type="submit" label="CONNECT" icon="pi pi-power-off" 
                  class="flex-1 text-xs font-black tracking-wider bg-indigo-600 hover:bg-indigo-500 border-none text-white shadow-[0_0_12px_rgba(99,102,241,0.2)]" 
                  :loading="store.isConnecting" />
          <Button v-else type="button" @click="handleDisconnect" label="DISCONNECT" icon="pi pi-power-off" severity="danger" 
                  class="flex-1 text-xs font-black tracking-wider text-white shadow-[0_0_12px_rgba(239,68,68,0.2)]" />
          <Button type="button" @click="handleTest" icon="pi pi-wifi" 
                  class="text-xs font-black bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-400" 
                  :disabled="!store.isConnected" v-tooltip.bottom="'Ping'" />
        </div>
      </form>
    </template>
  </Card>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { usePlcStore } from '../stores/plcStore'
import { useToast } from 'primevue/usetoast'
import api from '../services/api'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'

const store = usePlcStore()
const toast = useToast()

const plcTypes = ref(['siemens', 'mitsubishi', 'rockwell', 'abb', 'fanuc'])
const portCheckEnabled = ref(false)
const continuousMonitoring = ref(false)
const monitoringInterval = ref(null)
const autoCheckTimeout = ref(null)

// Validation functions
const isValidIp = (ip) => {
  const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  return ipRegex.test(ip)
}

const isValidPort = (port) => {
  const portNum = parseInt(port)
  return portNum > 0 && portNum <= 65535
}

// Debounced auto-check to prevent excessive API calls
const debouncedAutoCheck = () => {
  if (autoCheckTimeout.value) {
    clearTimeout(autoCheckTimeout.value)
  }
  autoCheckTimeout.value = setTimeout(() => {
    autoCheckPortStatus()
  }, 800) // Increased delay to 800ms
}

const getPlcIcon = (type) => {
    const map = { siemens: 'pi-server', mitsubishi: 'pi-box', rockwell: 'pi-cog', abb: 'pi-bolt', fanuc: 'pi-desktop' };
    return 'pi ' + (map[type] || 'pi-link');
};

const getPlcDesc = (type) => {
    const map = { siemens: 'S7 Comm · Snap7', mitsubishi: 'MC Protocol', rockwell: 'EtherNet/IP', abb: 'Modbus TCP', fanuc: 'fxvrlib Fanuc' };
    return map[type] || 'Protocol';
};

const getPortStatusText = () => {
  // In this UI semantics, 'open' means connection is available (free to connect), while 'closed' means not available (busy/unreachable).
  if (store.portStatus === 'open') return 'PORT FREE';
  if (store.portStatus === 'closed') return 'PORT BUSY';

  if (store.portBusy === true) return 'PORT BUSY';
  if (store.portBusy === false) return 'PORT FREE';

  return store.portStatus.toUpperCase();
};

const getPortStatusClass = () => {
  if (store.portStatus === 'open') return 'port-free-tag';
  if (store.portStatus === 'closed') return 'port-busy-tag';
  if (store.portStatus === 'timeout') return 'port-timeout-tag';
  if (store.portStatus === 'error' || store.portStatus === 'dns_error') return 'port-error-tag';

  if (store.portBusy === true) return 'port-busy-tag';
  if (store.portBusy === false) return 'port-free-tag';

  return 'port-unknown-tag';
};

onMounted(() => {
  store.fetchSupportedTypes().then(() => {
    if (store.supportedTypes.length) plcTypes.value = store.supportedTypes;
  })
  
  // Auto-check port status on mount
  setTimeout(() => {
    autoCheckPortStatus()
  }, 1000)
})

// Watch for IP and port changes to auto-check port status
watch(() => store.connectionConfig.ip, (newIp, oldIp) => {
  // Only trigger if IP actually changed and is valid
  if (newIp !== oldIp && isValidIp(newIp) && store.connectionConfig.port) {
    debouncedAutoCheck()
  }
})

watch(() => store.connectionConfig.port, (newPort, oldPort) => {
  // Only trigger if port actually changed and is valid
  if (newPort !== oldPort && isValidPort(newPort) && store.connectionConfig.ip) {
    debouncedAutoCheck()
  }
})

// Watch for PLC type changes
watch(() => store.connectionConfig.plc_type, (newType, oldType) => {
  if (newType !== oldType && store.connectionConfig.ip && store.connectionConfig.port) {
    // Reset port check when PLC type changes
    portCheckEnabled.value = false
    continuousMonitoring.value = false
    stopContinuousMonitoring()
    // Auto-check after PLC type change
    setTimeout(() => autoCheckPortStatus(), 300)
  }
})

const onPlcTypeChange = () => {
    const type = store.connectionConfig.plc_type;
    portCheckEnabled.value = false;
    if (type === 'siemens') store.connectionConfig.port = 102;
    else if (type === 'mitsubishi') store.connectionConfig.port = 5000;
    else if (type === 'abb') store.connectionConfig.port = 502;
    else if (type === 'rockwell') store.connectionConfig.port = 44818;
    else if (type === 'fanuc') store.connectionConfig.port = 21;
}

const handleConnect = async () => {
  const result = await store.connectPlc()
  if (result.success) toast.add({ severity: 'success', summary: 'Connected', detail: result.message, life: 3000 })
  else toast.add({ severity: 'error', summary: 'Failed', detail: result.message, life: 5000 })
}

const handleDisconnect = async () => {
  const result = await store.disconnectPlc()
  toast.add({ severity: 'info', summary: 'Disconnected', detail: result.message, life: 3000 })
}

const handleTest = async () => {
  try {
    const res = await api.testConnection(store.connectionConfig)
    if (res.data.success) toast.add({ severity: 'success', summary: 'Ping OK', detail: 'Link active', life: 3000 })
    else { toast.add({ severity: 'error', summary: 'Dead', detail: 'No response', life: 3000 }); store.isConnected = false }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e.message, life: 3000 }); store.isConnected = false
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
        summary = 'Port Free'
        break
      case 'closed':
        severity = 'error'
        summary = 'Port Busy'
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
    
    // Auto-hide if port is free and not monitoring continuously
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
  }, 5000) // Check every 5 seconds
  
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
  // Only auto-check if port check is not already enabled and not currently checking
  if (!portCheckEnabled.value && !store.checkingPort && store.connectionConfig.ip && store.connectionConfig.port) {
    try {
      const result = await store.checkPortBusy()
      if (result.success) {
        // Auto-enable the port check display to show the status
        portCheckEnabled.value = true
        
        // Auto-hide after 5 seconds if port is free
        if (result.port_status === 'closed') {
          setTimeout(() => {
            if (!continuousMonitoring.value) {
              portCheckEnabled.value = false
            }
          }, 5000)
        }
      }
    } catch (error) {
      // Silent fail for auto-check
      console.log('Auto port check failed:', error)
    }
  }
}

onUnmounted(() => {
  // Clean up timeouts and intervals
  if (autoCheckTimeout.value) {
    clearTimeout(autoCheckTimeout.value)
  }
  if (monitoringInterval.value) {
    clearInterval(monitoringInterval.value)
  }
})
</script>

<style scoped>
.port-busy-tag {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  color: white;
  border: 1px solid #dc2626;
}

.port-free-tag {
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: white;
  border: 1px solid #16a34a;
}

.port-timeout-tag {
  background: linear-gradient(135deg, #ca8a04, #a16207);
  color: white;
  border: 1px solid #ca8a04;
}

.port-error-tag {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  color: white;
  border: 1px solid #dc2626;
}

.port-unknown-tag {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: white;
  border: 1px solid #6b7280;
}
</style>
