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
import { onMounted, ref } from 'vue'
import { usePlcStore } from '../stores/plcStore'
import { useToast } from 'primevue/usetoast'
import api from '../services/api'
import Card from 'primevue/card'

const store = usePlcStore()
const toast = useToast()

const plcTypes = ref(['siemens', 'mitsubishi', 'rockwell', 'abb', 'fanuc'])

const getPlcIcon = (type) => {
    const map = { siemens: 'pi-server', mitsubishi: 'pi-box', rockwell: 'pi-cog', abb: 'pi-bolt', fanuc: 'pi-desktop' };
    return 'pi ' + (map[type] || 'pi-link');
};

const getPlcDesc = (type) => {
    const map = { siemens: 'S7 Comm · Snap7', mitsubishi: 'MC Protocol', rockwell: 'EtherNet/IP', abb: 'Modbus TCP', fanuc: 'GE Fanuc' };
    return map[type] || 'Protocol';
};

onMounted(() => {
  store.fetchSupportedTypes().then(() => {
    if (store.supportedTypes.length) plcTypes.value = store.supportedTypes;
  })
})

const onPlcTypeChange = () => {
    const type = store.connectionConfig.plc_type;
    if (type === 'siemens') store.connectionConfig.port = 102;
    else if (type === 'mitsubishi') store.connectionConfig.port = 5000;
    else if (type === 'abb') store.connectionConfig.port = 502;
    else if (type === 'rockwell') store.connectionConfig.port = 44818;
    else if (type === 'fanuc') store.connectionConfig.port = 18245;
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
    if (res.data.connected) toast.add({ severity: 'success', summary: 'Ping OK', detail: 'Link active', life: 3000 })
    else { toast.add({ severity: 'error', summary: 'Dead', detail: 'No response', life: 3000 }); store.isConnected = false }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e.message, life: 3000 }); store.isConnected = false
  }
}
</script>
