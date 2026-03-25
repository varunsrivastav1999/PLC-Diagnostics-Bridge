<template>
  <Card class="border-0 h-full overflow-hidden flex flex-col">
    <template #content>
      <!-- Header bar -->
      <div class="flex justify-between items-center border-b border-slate-800/50 pb-3 mb-4">
        <div class="flex items-center gap-2">
          <div class="h-2 w-2 rounded-full animate-glow-pulse" :class="operation === 'read' ? 'bg-cyan-500' : 'bg-amber-500'"></div>
          <span class="text-[10px] font-black tracking-[0.2em] uppercase" :class="operation === 'read' ? 'text-cyan-500' : 'text-amber-500'">Operations Terminal</span>
        </div>
        
        <div class="flex gap-1 p-0.5 bg-slate-950/80 rounded-lg border border-slate-800/50">
          <button class="flex items-center gap-1.5 px-4 py-1.5 rounded-md text-[10px] font-black tracking-widest uppercase transition-all duration-200" 
                  :class="operation === 'read' ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-[0_0_8px_rgba(34,211,238,0.1)]' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                  @click="operation = 'read'">
            <i class="pi pi-eye" style="font-size: 10px;"></i> READ
          </button>
          <button class="flex items-center gap-1.5 px-4 py-1.5 rounded-md text-[10px] font-black tracking-widest uppercase transition-all duration-200" 
                  :class="operation === 'write' ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-[0_0_8px_rgba(245,158,11,0.1)]' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                  @click="operation = 'write'">
            <i class="pi pi-pencil" style="font-size: 10px;"></i> WRITE
          </button>
        </div>
      </div>
      
      <!-- Content area -->
      <div class="flex flex-col lg:flex-row gap-5 flex-1 min-h-0">
        <!-- Left: Controls -->
        <form @submit.prevent="submitOperation" class="flex flex-col gap-4 w-full lg:w-[42%] shrink-0">
          <!-- Data type & bit offset & register count -->
          <div class="grid gap-3" :class="showExtraField ? 'grid-cols-2' : 'grid-cols-1'">
            <div class="flex flex-col gap-1">
              <label class="text-[10px] font-black text-slate-500 tracking-[0.15em] uppercase">Data Type</label>
              <Dropdown v-model="form.data_type" :options="dataTypes" class="w-full text-xs" :disabled="!store.isConnected" @change="onDataTypeChange" />
            </div>
            <div class="flex flex-col gap-1" v-if="form.data_type === 'BOOL'">
              <label class="text-[10px] font-black text-slate-500 tracking-[0.15em] uppercase">Bit Offset</label>
              <InputText type="number" v-model.number="form.bit_offset" class="font-mono text-xs" :disabled="!store.isConnected" />
            </div>
            <div class="flex flex-col gap-1" v-if="form.data_type === 'STRING'">
              <label class="text-[10px] font-black text-cyan-500 tracking-[0.15em] uppercase">Registers</label>
              <InputText type="number" v-model.number="form.register_count" class="font-mono text-xs" :disabled="!store.isConnected" />
              <span class="text-[8px] text-slate-600">{{ form.register_count * 2 }} chars max</span>
            </div>
          </div>

          <!-- Address -->
          <div class="flex flex-col gap-1">
            <label class="text-[10px] font-black tracking-[0.15em] uppercase" :class="operation === 'read' ? 'text-cyan-500' : 'text-amber-500'">Address / Tag</label>
            <InputText v-model="form.address" :placeholder="exampleAddress" class="w-full font-mono text-sm tracking-wider" :disabled="!store.isConnected" />
            <div class="flex items-center gap-1.5 mt-0.5">
              <i class="pi pi-info-circle text-slate-600" style="font-size: 9px;"></i>
              <span class="text-[9px] text-slate-600 tracking-wider">Format: <span class="text-slate-400">{{ exampleAddress }}</span></span>
            </div>
          </div>

          <!-- Write value / boolean toggle -->
          <div v-if="operation === 'write'" class="animate-fadein">
            <template v-if="form.data_type === 'BOOL'">
              <div class="p-3 border border-amber-500/20 rounded-xl bg-amber-950/10">
                <span class="text-[9px] font-black text-amber-500/60 tracking-widest uppercase block mb-2">Boolean State</span>
                <div class="flex gap-2">
                  <button type="button" class="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg border text-[10px] font-black tracking-widest uppercase transition-all" 
                       :class="form.write_val === true ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400 shadow-[0_0_10px_rgba(34,197,94,0.15)]' : 'bg-slate-900/50 border-slate-800 text-slate-600 hover:text-slate-400'" 
                       @click="form.write_val = true">
                    <i class="pi pi-check-circle" style="font-size: 11px;"></i> TRUE
                  </button>
                  <button type="button" class="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg border text-[10px] font-black tracking-widest uppercase transition-all" 
                       :class="form.write_val === false ? 'bg-red-500/15 border-red-500/40 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.15)]' : 'bg-slate-900/50 border-slate-800 text-slate-600 hover:text-slate-400'" 
                       @click="form.write_val = false">
                    <i class="pi pi-times-circle" style="font-size: 11px;"></i> FALSE
                  </button>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="p-3 border border-amber-500/20 rounded-xl bg-amber-950/10">
                <span class="text-[9px] font-black text-amber-500/60 tracking-widest uppercase block mb-2">Payload</span>
                <InputText v-model="form.write_val" class="w-full font-mono text-lg bg-black/30 border-none text-amber-400" placeholder="Enter value..." :disabled="!store.isConnected" />
              </div>
            </template>
          </div>
          
          <!-- Polling control for read -->
          <div v-else-if="operation === 'read'" class="flex items-center gap-3 p-3 border border-slate-800/50 rounded-xl bg-slate-950/30">
             <Checkbox v-model="isPollingLocal" :binary="true" @change="togglePolling" inputId="poll" :disabled="!store.isConnected" />
             <label for="poll" class="text-[10px] cursor-pointer font-black text-slate-400 tracking-widest uppercase">Live Watch</label>
             <div class="flex items-center gap-2 ml-auto" v-if="isPollingLocal">
                 <span class="text-[9px] font-bold text-slate-600 tracking-wider">ms</span>
                 <InputText type="number" v-model.number="store.pollingInterval" class="w-16 p-1 text-xs text-center font-bold bg-transparent border-none text-cyan-400" />
             </div>
          </div>

          <!-- Execute button -->
          <Button :type="isPollingLocal ? 'button' : 'submit'" 
                  :label="operation === 'read' ? 'READ' : 'WRITE'" 
                  :icon="operation === 'read' ? 'pi pi-download' : 'pi pi-upload'" 
                  :class="operation === 'read' ? 'bg-cyan-600 hover:bg-cyan-500 border-none shadow-[0_0_12px_rgba(8,145,178,0.25)] text-white' : 'bg-amber-600 hover:bg-amber-500 border-none shadow-[0_0_12px_rgba(217,119,6,0.25)] text-white'"
                  class="w-full font-black tracking-[0.15em] text-xs py-3" 
                  :disabled="!store.isConnected || (isPollingLocal && operation === 'read')" 
                  :loading="loading" />
        </form>

        <!-- Right: Display Terminal -->
        <div class="flex-1 flex items-center justify-center p-6 bg-slate-950/60 rounded-2xl border border-slate-800/40 relative overflow-hidden min-h-[250px]">
           <!-- Grid decoration -->
           <div class="absolute inset-0 opacity-[0.04]" style="background-image: linear-gradient(#475569 1px, transparent 1px), linear-gradient(90deg, #475569 1px, transparent 1px); background-size: 24px 24px;"></div>
           
           <div class="relative z-10 w-full h-full flex flex-col items-center justify-center">
              <!-- READ display -->
              <div v-if="operation === 'read'" class="w-full h-full flex flex-col justify-center items-center gap-4">
                  <div class="flex items-center gap-2">
                      <div class="h-1.5 w-1.5 rounded-full bg-cyan-500 shadow-[0_0_6px_#06b6d4]"></div>
                      <span class="text-[9px] font-black tracking-[0.3em] text-cyan-600 uppercase">Terminal Output</span>
                  </div>
                  
                  <div class="flex-1 w-full flex items-center justify-center">
                      <span v-if="lastReadResult !== null" class="text-6xl lg:text-8xl xl:text-9xl font-mono font-black tracking-tighter text-white drop-shadow-[0_0_30px_rgba(255,255,255,0.2)] truncate max-w-full overflow-hidden" style="font-family: 'JetBrains Mono', monospace;">
                          {{ lastReadResult }}
                      </span>
                      <div v-else class="flex flex-col items-center gap-3">
                          <div class="h-16 w-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center">
                            <i class="pi pi-wave-pulse text-slate-700 text-2xl"></i>
                          </div>
                          <span class="text-slate-700 text-[10px] uppercase tracking-[0.3em] font-black">Awaiting Signal</span>
                      </div>
                  </div>
                  
                  <div v-if="isPollingLocal" class="flex items-center gap-2 text-[9px] tracking-widest font-black uppercase text-cyan-500">
                      <i class="pi pi-spin pi-spinner" style="font-size: 10px;"></i> Watching · {{ store.pollingInterval }}ms
                  </div>
              </div>
              
              <!-- WRITE display -->
              <div v-else class="w-full h-full flex flex-col justify-center gap-6">
                  <div class="flex items-center gap-2">
                      <div class="h-1.5 w-1.5 rounded-full bg-amber-500 shadow-[0_0_6px_#f59e0b]"></div>
                      <span class="text-[9px] font-black tracking-[0.3em] text-amber-600 uppercase">Payload Preview</span>
                  </div>
                  
                  <div class="flex flex-col gap-5 flex-1 justify-center">
                      <div class="border-l-2 border-slate-700/50 pl-4">
                          <span class="block text-[9px] font-black text-slate-600 tracking-[0.2em] uppercase mb-1">Address</span>
                          <span class="font-mono text-xl text-slate-300 tracking-wider" style="font-family: 'JetBrains Mono', monospace;">{{ form.address || '—' }}</span>
                      </div>
                      <div class="border-l-2 border-amber-500/30 pl-4 py-1">
                          <span class="block text-[9px] font-black text-amber-500/50 tracking-[0.2em] uppercase mb-1">Value</span>
                          <span class="font-mono text-3xl lg:text-4xl text-amber-400 tracking-wider font-bold" style="font-family: 'JetBrains Mono', monospace;">{{ displayWriteVal }}</span>
                      </div>
                  </div>
              </div>
           </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { usePlcStore } from '../stores/plcStore'
import { useToast } from 'primevue/usetoast'
import api from '../services/api'
import Card from 'primevue/card'

const store = usePlcStore()
const toast = useToast()

const operation = ref('read')
const loading = ref(false)
const isPollingLocal = ref(false)
const lastReadResult = ref(null)

const dataTypes = ref(['BOOL', 'INT', 'DINT', 'REAL', 'FLOAT', 'STRING'])

const form = ref({
  data_type: 'INT',
  address: '',
  bit_offset: 0,
  register_count: 10,
  write_val: ''
})

const showExtraField = computed(() => {
  return form.value.data_type === 'BOOL' || form.value.data_type === 'STRING';
})

const displayWriteVal = computed(() => {
  if (form.value.data_type === 'BOOL') {
    return form.value.write_val === true ? 'TRUE' : 'FALSE';
  }
  return form.value.write_val || '—';
})

const exampleAddress = computed(() => {
  const t = store.connectionConfig.plc_type;
  if (t === 'siemens') return form.value.data_type === 'BOOL' ? 'DB1.DBX0.0' : 'DB1.DBW2';
  if (t === 'mitsubishi') return form.value.data_type === 'BOOL' ? 'M10' : 'D100';
  if (t === 'rockwell') return 'MyTag';
  if (t === 'abb') return form.value.data_type === 'BOOL' ? '00001' : '40001';
  if (t === 'fanuc') return 'R100';
  return 'Address';
})

const onDataTypeChange = () => {
    if (form.value.data_type === 'BOOL') {
        form.value.write_val = false;
        form.value.bit_offset = 0;
    } else if (form.value.data_type === 'STRING') {
        form.value.write_val = '';
        form.value.register_count = 10;
    } else {
        form.value.write_val = '';
    }
}

const buildPayload = () => {
    const p = { ...store.connectionConfig };
    p.data_type = form.value.data_type;
    p.address = form.value.address;
    p.bit_offset = (form.value.data_type === 'BOOL' && form.value.bit_offset != null) ? Number(form.value.bit_offset) || 0 : 0;
    p.register_count = form.value.data_type === 'STRING' ? (Number(form.value.register_count) || 10) : 1;
    return p;
}

const performRead = async () => {
    loading.value = true;
    try {
        const payload = buildPayload();
        const res = await api.readData(payload);
        if (res.data.success) {
            lastReadResult.value = res.data.value;
        } else {
            if (isPollingLocal.value) { isPollingLocal.value = false; togglePolling(); }
            toast.add({ severity: 'error', summary: 'Read Error', detail: res.data.message, life: 5000 });
        }
    } catch (e) {
        if (isPollingLocal.value) { isPollingLocal.value = false; togglePolling(); }
        toast.add({ severity: 'error', summary: 'Read Failed', detail: e.message, life: 5000 });
    } finally {
        loading.value = false;
    }
}

const performWrite = async () => {
    loading.value = true;
    try {
        const payload = buildPayload();
        payload.value = form.value.write_val;
        const res = await api.writeData(payload);
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Write OK', detail: 'Value injected', life: 3000 });
            if (form.value.data_type !== 'BOOL') form.value.write_val = '';
        } else {
            toast.add({ severity: 'error', summary: 'Write Error', detail: res.data.message, life: 5000 });
        }
    } catch(e) {
        toast.add({ severity: 'error', summary: 'Write Failed', detail: e.message, life: 5000 });
    } finally {
        loading.value = false;
    }
}

const submitOperation = () => {
    if (!form.value.address) {
        toast.add({ severity: 'warn', summary: 'Required', detail: 'Enter an address', life: 3000 });
        return;
    }
    if (operation.value === 'read') performRead();
    else performWrite();
}

const togglePolling = () => {
    if (isPollingLocal.value) {
        if (!form.value.address) {
             toast.add({ severity: 'warn', summary: 'Required', detail: 'Enter an address to watch', life: 3000 });
             setTimeout(() => { isPollingLocal.value = false; }, 0);
             return;
        }
        store.startPolling(performRead);
    } else {
        store.stopPolling();
    }
}

watch(() => store.isConnected, (val) => {
    if (!val && isPollingLocal.value) {
        isPollingLocal.value = false;
        store.stopPolling();
    }
})
</script>
