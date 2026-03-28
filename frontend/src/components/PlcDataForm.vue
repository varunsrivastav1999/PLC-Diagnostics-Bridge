<template>
  <Card class="telemetry-card data-matrix-card border-0 h-full overflow-auto flex flex-col">
    <template #content>
      <div class="flex h-full min-h-0 flex-col overflow-y-auto pr-1">
        <!-- Unified Header bar -->
        <div class="mb-4 flex flex-col gap-3 border-b border-slate-800/50 pb-3 xl:flex-row xl:items-center xl:justify-between">
          <!-- Title -->
          <div class="flex items-center gap-2">
            <template v-if="store.connectionConfig.plc_type === 'fanuc'">
               <div class="h-2 w-2 rounded-full animate-glow-pulse bg-indigo-500"></div>
               <span class="text-[10px] font-black tracking-[0.2em] uppercase text-indigo-500">Paint Robot Control</span>
            </template>
            <template v-else>
               <div class="h-2 w-2 rounded-full animate-glow-pulse" :class="operation === 'read' ? 'bg-cyan-500' : 'bg-amber-500'"></div>
               <span class="text-[10px] font-black tracking-[0.2em] uppercase" :class="operation === 'read' ? 'text-cyan-500' : 'text-amber-500'">Operations Terminal</span>
            </template>
          </div>
          
          <!-- Controls -->
          <div class="flex flex-wrap items-center gap-3">
            <!-- Fanuc specific mode toggle -->
            <div v-if="store.connectionConfig.plc_type === 'fanuc'" class="flex flex-wrap gap-1 p-0.5 bg-slate-950/80 rounded-lg border border-indigo-900/50">
              <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[9px] font-black tracking-widest uppercase transition-all duration-200" 
                      :class="fanucMode === 'pendant' ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                      @click="fanucMode = 'pendant'">
                <i class="pi pi-table" style="font-size: 9px;"></i> iPendant VIRTUAL
              </button>
              <div class="w-px h-4 bg-slate-700/50 self-center mx-1"></div>
              <!-- Fanuc Diagnostics -->
              <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[9px] font-black tracking-widest uppercase transition-all duration-200" 
                      :class="fanucMode === 'diagnostics' ? 'bg-red-500/15 text-red-400 border border-red-500/30' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                      @click="fanucMode = 'diagnostics'">
                <i class="pi pi-heartbeat" style="font-size: 9px;"></i> DIAGNOSTICS
              </button>
            </div>

            <!-- Standard Operation Toggle -->
            <div v-if="store.connectionConfig.plc_type !== 'fanuc'" class="flex flex-wrap gap-1 p-0.5 bg-slate-950/80 rounded-lg border border-slate-800/50">
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
        </div>

        <!-- Content area (Raw Terminal) -->
        <template v-if="store.connectionConfig.plc_type !== 'fanuc'">
          <div class="flex flex-col lg:flex-row gap-5 flex-1 min-h-0">
        <!-- Left: Controls -->
        <form @submit.prevent="submitOperation" class="flex flex-col gap-4 w-full lg:w-[42%] shrink-0 overflow-y-auto">
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
        <div class="flex-1 flex items-center justify-center p-6 bg-slate-950/60 rounded-2xl border border-slate-800/40 relative overflow-auto min-h-[250px]">
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

        <!-- Fanuc Paint Robot iPendant -->
        <template v-if="store.connectionConfig.plc_type === 'fanuc' && fanucMode === 'pendant'">
          <div class="flex flex-col flex-1 min-h-0 relative select-none">
          
          <!-- Hardware Pendant Shell -->
          <div class="flex-1 flex flex-col bg-slate-800 rounded-3xl border border-slate-700 shadow-[0_10px_40px_rgba(0,0,0,0.5)] overflow-hidden relative p-3 pb-4">
            <!-- Signature Yellow Bumper Accent -->
            <div class="absolute top-0 left-0 right-0 h-2 bg-amber-400"></div>
            
            <!-- Hardware Top Bezels / Branding -->
            <div class="flex items-center justify-between px-3 mt-1 py-2 mb-2">
              <div class="flex flex-col">
                <span class="text-[10px] font-black text-slate-400 tracking-widest uppercase mb-0.5">PaintTool Diagnostic</span>
                <span class="text-xs font-black text-amber-500 tracking-[0.3em] uppercase drop-shadow-md">iPendant Virtual</span>
              </div>
              <div class="flex items-center gap-1.5">
                 <div class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]"></div>
                 <span class="text-[9px] font-black tracking-widest text-slate-400">STATUS: READY</span>
              </div>
            </div>

            <!-- "Screen" bezel -->
            <div class="flex-1 flex flex-col bg-slate-950 rounded-xl border-[6px] border-slate-900 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]">
              
              <!-- Screen Top Control Bar (Software UI) -->
              <div class="flex gap-4 bg-blue-900/40 border-b border-blue-800/50 px-4 py-3 items-end">
                <div class="flex flex-col gap-1.5 w-20">
                  <label class="text-[9px] font-black text-blue-200 tracking-widest uppercase">Job No</label>
                  <InputText type="number" v-model.number="fanucForm.job_no" min="1" max="250" class="font-mono text-xs text-center font-bold bg-slate-900/80 border-blue-500/30 text-white" :disabled="!store.isConnected" />
                </div>
                <div class="flex flex-col gap-1.5 w-20">
                  <label class="text-[9px] font-black text-blue-200 tracking-widest uppercase">Color No</label>
                  <InputText type="number" v-model.number="fanucForm.color_no" min="1" max="30" class="font-mono text-xs text-center font-bold bg-slate-900/80 border-blue-500/30 text-white" :disabled="!store.isConnected" />
                </div>
                <div class="flex flex-col gap-1.5 w-32">
                  <label class="text-[9px] font-black text-blue-200 tracking-widest uppercase">Config Type</label>
                  <Dropdown v-model="fanucForm.preset_type" :options="fanucPresetTypes" class="w-full text-xs font-bold bg-slate-900/80 border-blue-500/30 text-white" :disabled="!store.isConnected" />
                </div>
                
                <Button @click="fetchFanucPresets" label="LOAD FROM ROBOT" icon="pi pi-refresh" 
                        class="ml-auto bg-blue-600 hover:bg-blue-500 border-none text-[9px] font-black tracking-widest text-white px-5 h-8 shadow-[0_0_10px_rgba(37,99,235,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected" :loading="loading" />
              </div>

              <!-- Screen Data Grid -->
              <div class="flex-1 overflow-auto relative bg-[#0f172a]">
                <div v-if="!fanucPresets" class="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-slate-900/80 backdrop-blur-sm z-20">
                   <div class="p-4 rounded-full bg-slate-800/80 border border-slate-700 shadow-xl">
                      <i class="pi pi-cloud-download text-blue-400 text-3xl animate-bounce"></i>
                   </div>
                   <span class="text-[10px] font-black tracking-[0.2em] text-slate-400 uppercase drop-shadow">Awaiting Robot Variables</span>
                </div>
                
                <table v-else class="w-full text-left border-collapse min-w-max">
                  <thead class="sticky top-0 bg-slate-800/90 backdrop-blur-md z-10 shadow-lg border-b border-slate-700">
                    <tr>
                      <th class="px-3 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-700/50 w-12 text-center">Nº</th>
                      <th v-for="col in displayColumns" :key="col.key" class="px-3 py-2 text-[9px] font-black text-amber-500 tracking-widest uppercase border-r border-slate-700/50 text-center">
                        {{ col.label }} <span class="text-blue-300 block text-[8px] mt-0.5 opacity-80">{{ col.unit }}</span>
                      </th>
                      <th class="px-3 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase w-20 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in fanucPresets" :key="index" class="border-b border-slate-800/50 hover:bg-blue-900/20 transition-colors group">
                      <td class="px-3 py-1.5 text-center border-r border-slate-800/50 bg-slate-900/20 text-[10px] font-black text-slate-500 tracking-wider">
                         {{ String(index + 1).padStart(2, '0') }}
                      </td>
                      <td v-for="col in displayColumns" :key="col.key" class="px-1 py-1 focus-within:bg-blue-900/30 border-r border-slate-800/30">
                         <InputText type="number" 
                                    v-model.number="row[col.key]" 
                                    :min="col.min" :max="col.max"
                                    @change="clampFanucValue(row, col)"
                                    class="w-full text-center font-mono text-sm bg-transparent border border-transparent focus:border-amber-500 hover:bg-slate-800 transition-colors p-1.5 focus:shadow-[0_0_8px_rgba(245,158,11,0.2)] text-slate-300" />
                      </td>
                      <td class="px-2 py-1.5 text-center">
                        <Button @click="updateFanucPresetRow(index)" icon="pi pi-send" class="h-8 w-8 bg-slate-700/50 hover:bg-amber-500 border-none text-slate-400 hover:text-black transition-all active:scale-90" v-tooltip.left="'Write Robot Preset ' + (index + 1)"/>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
          </div>
          </div>
        </template>

        <!-- Fanuc Diagnostics App -->
        <template v-if="store.connectionConfig.plc_type === 'fanuc' && fanucMode === 'diagnostics'">
          <div class="flex flex-col flex-1 min-h-0 relative bg-slate-900 rounded-xl overflow-hidden shadow-inner border border-slate-800">
          
          <!-- Top Tool Bar -->
          <div class="flex flex-wrap gap-2 p-3 bg-slate-950 border-b border-slate-800 shrink-0">
            <Button @click="fetchFanucDiagnostic('errall.ls')" label="ALL ALARMS" icon="pi pi-list" class="bg-red-900/40 hover:bg-red-800 text-red-400 border border-red-800/50 text-[10px] font-black tracking-wider px-3 py-1.5" :disabled="!store.isConnected || loading" />
            <Button @click="fetchFanucDiagnostic('erract.ls')" label="ACTIVE ALARMS" icon="pi pi-bell" class="bg-orange-900/40 hover:bg-orange-800 text-orange-400 border border-orange-800/50 text-[10px] font-black tracking-wider px-3 py-1.5" :disabled="!store.isConnected || loading" />
            <Button @click="fetchFanucDiagnostic('errhist.ls')" label="ALARM HISTORY" icon="pi pi-history" class="bg-amber-900/40 hover:bg-amber-800 text-amber-500 border border-amber-800/50 text-[10px] font-black tracking-wider px-3 py-1.5" :disabled="!store.isConnected || loading" />
            <Button @click="fetchFanucDiagnostic('summary.dg')" label="SYSTEM SUMMARY" icon="pi pi-server" class="bg-blue-900/40 hover:bg-blue-800 text-blue-400 border border-blue-800/50 text-[10px] font-black tracking-wider px-3 py-1.5" :disabled="!store.isConnected || loading" />
            <Button @click="fetchFanucDiagnostic('logbook.ls')" label="LOGBOOK" icon="pi pi-book" class="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600/50 text-[10px] font-black tracking-wider px-3 py-1.5" :disabled="!store.isConnected || loading" />
            <div class="flex-1"></div>
            <Button @click="clearDiagnosticLog" icon="pi pi-times" class="bg-slate-700 hover:bg-slate-600 text-slate-400 border border-slate-600/50 text-[10px] font-black tracking-wider px-3 py-1.5" v-tooltip.bottom="'Clear Log'" />
            <span v-if="loading" class="text-[10px] font-black text-amber-500 tracking-widest animate-pulse flex items-center"><i class="pi pi-spin pi-spinner mr-2"></i> FETCHING MD FILE...</span>
          </div>

          <!-- Log Viewer -->
          <div class="flex-1 flex flex-col min-h-0">
            <!-- Log Header -->
            <div v-if="diagnosticLog" class="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-700 shrink-0">
              <span class="text-[10px] font-black text-slate-400 tracking-widest uppercase">Diagnostic Output</span>
              <span class="text-[9px] text-slate-500">{{ diagnosticLog.split('\n').length }} lines</span>
            </div>

            <!-- Scrollable Log Content -->
            <div class="flex-1 p-4 overflow-auto font-mono text-xs whitespace-pre-wrap bg-black text-green-400 border border-slate-800/50 leading-relaxed shadow-[inset_0_0_30px_rgba(0,0,0,0.8)] scrollbar-custom">
              <div v-if="!diagnosticLog" class="h-full flex flex-col items-center justify-center opacity-30 select-none">
                 <i class="pi pi-server text-4xl mb-3"></i>
                 <span class="font-black tracking-[0.2em] uppercase text-[10px]">Select Diagnostic File</span>
                 <span class="text-[9px] text-slate-500 mt-2 text-center max-w-xs uppercase tracking-widest">FTP LINK: errall.ls · erract.ls · errhist.ls · summary.dg · logbook.ls</span>
              </div>
              <div v-else class="min-h-full break-words selection:bg-green-500/30">{{ diagnosticLog }}</div>
            </div>
          </div>
          </div>
        </template>
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
const fanucPresetTypes = ['BELL', 'GUN']

const form = ref({
  data_type: 'INT',
  address: '',
  bit_offset: 0,
  register_count: 10,
  write_val: ''
})

// Fanuc specific state
const fanucMode = ref('pendant') // 'pendant', 'diagnostics', or 'raw'
const fanucForm = ref({
  job_no: 1,
  color_no: 1,
  preset_type: 'BELL'
})
const fanucPresets = ref(null)
const diagnosticLog = ref(null)

const fetchFanucDiagnostic = async (filename) => {
  if (!store.isConnected) return;
  loading.value = true;
  diagnosticLog.value = null;
  try {
    const payload = {
      ...store.connectionConfig,
      data_type: 'STRING',
      address: filename // Raw file requested by name e.g. errall.ls
    };
    const res = await api.readData(payload);
    if (res.data.success) {
      diagnosticLog.value = res.data.value;
      toast.add({ severity: 'success', summary: 'File Downloaded', detail: `Successfully read ${filename} via FTP`, life: 2500 });
    }
  } catch (error) {
    diagnosticLog.value = `[ERROR FETCHING LOG]\n${error.response?.data?.detail || error.message}`;
    toast.add({ severity: 'error', summary: 'FTP Error', detail: 'Could not fetch diagnostic file', life: 4000 });
  } finally {
    loading.value = false;
  }
}

const clearDiagnosticLog = () => {
  diagnosticLog.value = null;
  toast.add({ severity: 'info', summary: 'Log Cleared', detail: 'Diagnostic log has been cleared', life: 1500 });
}

const displayColumns = computed(() => {
  if (fanucForm.value.preset_type === 'BELL') {
    return [
      { key: 'fluid_rate', label: 'Fluid Rate', unit: 'cc/min', min: 0, max: 2000 },
      { key: 'bell_speed', label: 'Bell Speed', unit: 'krpm', min: 0, max: 100 },
      { key: 'shape_air1', label: 'Shape Air 1', unit: 'L/min', min: 0, max: 800 },
      { key: 'estat_KV', label: 'E-Stat', unit: 'kV', min: 0, max: 100 },
      { key: 'shape_air2', label: 'Shape Air 2', unit: 'L/min', min: 0, max: 800 },
      { key: 'estat_uA', label: 'E-Stat Curr', unit: 'µA', min: 0, max: 250 }
    ];
  }
  // Default (GUN)
  return [
    { key: 'fluid_rate', label: 'Fluid Rate', unit: 'cc/min', min: 0, max: 2000 },
    { key: 'atom_air', label: 'Atom Air', unit: 'L/min', min: 0, max: 800 },
    { key: 'fan_air', label: 'Fan Air', unit: 'L/min', min: 0, max: 800 },
    { key: 'estat_KV', label: 'E-Stat', unit: 'kV', min: 0, max: 100 }
  ];
})

const clampFanucValue = (row, col) => {
  let val = row[col.key];
  if (typeof val !== 'number' || isNaN(val)) val = 0;
  if (val < col.min) val = col.min;
  if (val > col.max) val = col.max;
  row[col.key] = val;
}

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
  if (t === 'mitsubishi') return form.value.data_type === 'BOOL' ? 'M10' : 'D100 or ZR100';
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

const fetchFanucPresets = async () => {
    loading.value = true;
    try {
        const payload = {
            ...store.connectionConfig,
            data_type: 'STRING', // Ignored by semantic parser
            address: `${fanucForm.value.job_no},${fanucForm.value.color_no},${fanucForm.value.preset_type}`
        };
        const res = await api.readData(payload);
        if (res.data.success) {
            fanucPresets.value = res.data.value;
            toast.add({ severity: 'success', summary: 'Presets Fetched', detail: 'Robot table loaded successfully', life: 2000 });
        } else {
            toast.add({ severity: 'error', summary: 'Fetch Error', detail: res.data.message, life: 5000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Fetch Failed', detail: e.message, life: 5000 });
    } finally {
        loading.value = false;
    }
}

const updateFanucPresetRow = async (index) => {
    loading.value = true;
    try {
        const payload = {
            ...store.connectionConfig,
            data_type: 'STRING',
            address: `${fanucForm.value.job_no},${fanucForm.value.color_no},${fanucForm.value.preset_type},${index + 1}`,
            value: fanucPresets.value[index]
        };
        const res = await api.writeData(payload);
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Preset Updated', detail: `Preset ${index + 1} synchronized via FTP`, life: 3000 });
        } else {
            toast.add({ severity: 'error', summary: 'Update Error', detail: res.data.message, life: 5000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Update Failed', detail: e.message, life: 5000 });
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
