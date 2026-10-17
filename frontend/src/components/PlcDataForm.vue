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
            <!-- Latency Badge -->
            <div v-if="store.isConnected && latencyMs > 0" class="ml-3 flex items-center gap-1 px-2 py-0.5 rounded-full border text-[8px] font-black tracking-wider uppercase"
                 :class="latencyMs < 50 ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : latencyMs < 200 ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' : 'bg-red-500/10 border-red-500/30 text-red-400'">
              <div class="h-1.5 w-1.5 rounded-full animate-pulse" :class="latencyMs < 50 ? 'bg-emerald-400' : latencyMs < 200 ? 'bg-amber-400' : 'bg-red-400'"></div>
              {{ latencyMs }}ms
            </div>
          </div>
          
          <!-- Controls -->
          <div class="flex flex-wrap items-center gap-3">
            <!-- Fanuc specific mode toggle -->
            <div v-if="store.connectionConfig.plc_type === 'fanuc'" class="flex flex-wrap gap-1 p-0.5 bg-slate-950/80 rounded-lg border border-indigo-900/50">
              <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[9px] font-black tracking-widest uppercase transition-all duration-200" 
                      :class="fanucMode === 'pendant' ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                      @click="fanucMode = 'pendant'">
                <i class="pi pi-table" style="font-size: 9px;"></i> PRESETS (SPRAY SETTING)
              </button>
              <div class="w-px h-4 bg-slate-700/50 self-center mx-1"></div>
              
              <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[9px] font-black tracking-widest uppercase transition-all duration-200" 
                      :class="fanucMode === 'manual' ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                      @click="fanucMode = 'manual'">
                <i class="pi pi-sliders-v" style="font-size: 9px;"></i> MANUAL SETTING (BELL/GUN)
              </button>
              <div class="w-px h-4 bg-slate-700/50 self-center mx-1"></div>
              
              <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[9px] font-black tracking-widest uppercase transition-all duration-200" 
                      :class="fanucMode === 'gnmbsc' ? 'bg-fuchsia-500/15 text-fuchsia-400 border border-fuchsia-500/30' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                      @click="fanucMode = 'gnmbsc'">
                <i class="pi pi-cog" style="font-size: 9px;"></i> GNM/BSC
              </button>
              <div class="w-px h-4 bg-slate-700/50 self-center mx-1"></div>
              
              <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[9px] font-black tracking-widest uppercase transition-all duration-200" 
                      :class="fanucMode === 'colors' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                      @click="fanucMode = 'colors'">
                <i class="pi pi-palette" style="font-size: 9px;"></i> COLOR
              </button>
              <div class="w-px h-4 bg-slate-700/50 self-center mx-1"></div>
              
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
              <button v-if="store.connectionConfig.plc_type === 'mitsubishi'" class="flex items-center gap-1.5 px-4 py-1.5 rounded-md text-[10px] font-black tracking-widest uppercase transition-all duration-200" 
                      :class="operation === 'range_read' ? 'bg-fuchsia-500/15 text-fuchsia-400 border border-fuchsia-500/30 shadow-[0_0_8px_rgba(217,70,239,0.1)]' : 'text-slate-500 border border-transparent hover:text-slate-400'" 
                      @click="operation = 'range_read'">
                <i class="pi pi-table" style="font-size: 10px;"></i> TAG READ
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
          <div v-if="operation !== 'range_read'" class="grid gap-3" :class="showExtraField ? 'grid-cols-2' : 'grid-cols-1'">
            <div class="flex flex-col gap-1">
              <label class="text-[10px] font-black text-slate-500 tracking-[0.15em] uppercase">Data Type</label>
              <Dropdown v-model="form.data_type" :options="dataTypes" class="w-full text-xs" @change="onDataTypeChange" />
            </div>
            <div class="flex flex-col gap-1" v-if="form.data_type === 'BOOL'">
              <label class="text-[10px] font-black text-slate-500 tracking-[0.15em] uppercase">Bit Offset</label>
              <InputText type="number" v-model.number="form.bit_offset" class="font-mono text-xs" />
            </div>
            <div class="flex flex-col gap-1" v-if="form.data_type === 'STRING'">
              <label class="text-[10px] font-black text-cyan-500 tracking-[0.15em] uppercase">Registers</label>
              <InputText type="number" v-model.number="form.register_count" class="font-mono text-xs" />
              <span class="text-[8px] text-slate-600">{{ form.register_count * 2 }} chars max</span>
            </div>
          </div>

          <!-- Address -->
          <div v-if="operation !== 'range_read'" class="flex flex-col gap-1">
            <label class="text-[10px] font-black tracking-[0.15em] uppercase" :class="operation === 'read' ? 'text-cyan-500' : 'text-amber-500'">Address / Tag</label>
            <InputText v-model="form.address" :placeholder="exampleAddress" class="w-full font-mono text-sm tracking-wider" />
            <div class="flex items-center gap-1.5 mt-0.5">
              <i class="pi pi-info-circle text-slate-600" style="font-size: 9px;"></i>
              <span class="text-[9px] text-slate-600 tracking-wider">Format: <span class="text-slate-400">{{ exampleAddress }}</span></span>
            </div>
            <!-- Quick Address Presets -->
            <div v-if="quickAddresses.length > 0" class="flex flex-wrap items-center gap-1.5 mt-1.5">
              <span class="text-[9px] font-black uppercase text-slate-500 tracking-wider">Presets:</span>
              <button v-for="qa in quickAddresses" :key="qa.addr" type="button"
                      @click="applyQuickAddress(qa)"
                      :title="qa.desc"
                      class="px-2 py-0.5 rounded text-[9px] font-mono font-bold tracking-wider bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 hover:border-cyan-500/40 hover:bg-cyan-950/30 active:scale-95 transition-all">
                {{ qa.label }}
              </button>
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
          
          <!-- Range Read Controls -->
          <div v-if="operation === 'range_read'" class="flex flex-col gap-4 animate-fadein">
            <div class="flex flex-col gap-4">
              <div class="flex flex-col gap-1">
                <label class="text-[10px] font-black text-fuchsia-500 tracking-[0.15em] uppercase">Device Prefix</label>
                <Dropdown v-model="rangeForm.prefix" :options="['D', 'W', 'R', 'ZR', 'M', 'X', 'Y', 'L', 'F']" class="w-full text-xs" :disabled="!store.isConnected" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-[10px] font-black text-fuchsia-500 tracking-[0.15em] uppercase">Start Addr</label>
                <InputText type="number" v-model.number="rangeForm.start" class="font-mono text-xs w-full" :disabled="!store.isConnected" />
              </div>
              <div class="flex flex-col gap-1">
                <label class="text-[10px] font-black text-fuchsia-500 tracking-[0.15em] uppercase">Count</label>
                <InputText type="number" v-model.number="rangeForm.count" class="font-mono text-xs w-full" :disabled="!store.isConnected" />
              </div>
            </div>
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
                  :label="operation === 'read' ? 'READ' : operation === 'range_read' ? 'READ RANGE' : 'WRITE'" 
                  :icon="operation === 'read' || operation === 'range_read' ? 'pi pi-download' : 'pi pi-upload'" 
                  :class="operation === 'read' ? 'bg-cyan-600 hover:bg-cyan-500 border-none shadow-[0_0_12px_rgba(8,145,178,0.25)] text-white' : operation === 'range_read' ? 'bg-fuchsia-600 hover:bg-fuchsia-500 border-none shadow-[0_0_12px_rgba(217,70,239,0.25)] text-white' : 'bg-amber-600 hover:bg-amber-500 border-none shadow-[0_0_12px_rgba(217,119,6,0.25)] text-white'"
                  class="w-full font-black tracking-[0.15em] text-xs py-3" 
                  :disabled="!store.isConnected || (isPollingLocal && operation === 'read')" 
                  :loading="loading" />
        </form>

        <!-- Right: Telemetry & Signal Analyzer Deck -->
        <div class="flex-1 flex flex-col p-5 bg-gradient-to-b from-slate-950/90 to-slate-950/70 rounded-2xl border border-slate-800/60 relative overflow-hidden min-h-[340px] shadow-2xl backdrop-blur-md">
           <!-- Grid decoration -->
           <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: linear-gradient(#475569 1px, transparent 1px), linear-gradient(90deg, #475569 1px, transparent 1px); background-size: 20px 20px;"></div>
           
           <div class="relative z-10 w-full flex-1 flex flex-col min-h-0">
              <!-- READ display -->
              <div v-if="operation === 'read'" class="w-full h-full flex flex-col min-h-0">
                  <!-- Telemetry Top Toolbar -->
                  <div class="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-slate-800/60 shrink-0">
                      <div class="flex items-center gap-2">
                          <span class="relative flex h-2 w-2">
                            <span v-if="lastReadResult !== null" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="isBoolResult ? (boolResultValue ? 'bg-emerald-400' : 'bg-slate-400') : 'bg-cyan-400'"></span>
                            <span class="relative inline-flex rounded-full h-2 w-2" :class="lastReadResult !== null ? (isBoolResult ? (boolResultValue ? 'bg-emerald-500' : 'bg-slate-500') : 'bg-cyan-500') : 'bg-slate-600'"></span>
                          </span>
                          <span class="text-[10px] font-black tracking-[0.2em] uppercase" :class="lastReadResult !== null ? 'text-slate-200' : 'text-slate-500'">
                              {{ lastReadResult !== null ? 'TELEMETRY ACTIVE' : 'TELEMETRY STANDBY' }}
                          </span>
                          <span v-if="form.address" class="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-slate-900 border border-slate-700/60 text-cyan-400">
                              TAG: {{ form.address }}
                          </span>
                          <span v-if="lastReadMeta && lastReadMeta.latency" class="px-1.5 py-0.5 rounded font-mono text-[9px] font-bold bg-slate-900/80 text-slate-400 border border-slate-800">
                              {{ lastReadMeta.latency }}ms
                          </span>
                      </div>

                      <div class="flex items-center gap-2 ml-auto">
                          <div v-if="isPollingLocal" class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-[9px] font-black uppercase text-cyan-400">
                              <i class="pi pi-spin pi-spinner text-[10px]"></i>
                              <span>Watch · {{ store.pollingInterval }}ms</span>
                          </div>
                          <button v-if="lastReadResult !== null" type="button" @click="copyReadResult" title="Copy raw value" class="p-1 rounded text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 transition-all text-xs">
                              <i class="pi pi-copy"></i>
                          </button>
                          <button v-if="readHistory.length > 0" type="button" @click="clearReadHistory" title="Clear trace history" class="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800/80 transition-all text-xs">
                              <i class="pi pi-trash"></i>
                          </button>
                      </div>
                  </div>
                  
                  <!-- Main Signal Readout Center -->
                  <div class="flex-1 w-full flex flex-col justify-center items-center py-2 min-h-0">
                      <!-- 1. Logic State Analyzer for BOOL -->
                      <div v-if="lastReadResult !== null && isBoolResult" class="w-full max-w-lg p-5 rounded-2xl border transition-all duration-300 flex flex-col items-center justify-center relative overflow-hidden"
                           :class="boolResultValue ? 'bg-gradient-to-b from-emerald-950/40 to-slate-950/80 border-emerald-500/40 shadow-[0_0_35px_rgba(16,185,129,0.15)]' : 'bg-gradient-to-b from-slate-900/60 to-slate-950/90 border-slate-800/80 shadow-[0_4px_24px_rgba(0,0,0,0.4)]'">
                          
                          <!-- Top Relay Status Pill -->
                          <div class="flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase mb-3 border"
                               :class="boolResultValue ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300' : 'bg-slate-800/60 border-slate-700/60 text-slate-400'">
                              <i :class="boolResultValue ? 'pi pi-bolt' : 'pi pi-power-off'" style="font-size: 10px;"></i>
                              <span>{{ boolResultValue ? 'ENERGIZED (+24V DC)' : 'DE-ENERGIZED (0V DC)' }}</span>
                          </div>

                          <!-- Primary Digital State Readout -->
                          <div class="flex items-baseline gap-3 my-1">
                              <span class="text-6xl md:text-7xl font-mono font-black tracking-tight"
                                    :class="boolResultValue ? 'text-emerald-400 drop-shadow-[0_0_25px_rgba(52,211,153,0.4)]' : 'text-slate-300 drop-shadow-[0_0_15px_rgba(148,163,184,0.15)]'">
                                  {{ boolResultValue ? 'HIGH' : 'LOW' }}
                              </span>
                              <span class="px-2.5 py-1 rounded-md text-xs font-mono font-black border"
                                    :class="boolResultValue ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400' : 'bg-slate-800 border-slate-700 text-slate-400'">
                                  LOGIC {{ boolResultValue ? '1' : '0' }}
                              </span>
                          </div>

                          <!-- Technical State Description -->
                          <div class="text-[10px] font-mono tracking-wider text-slate-400 mt-2 text-center">
                              {{ boolResultValue ? 'Assertion Active · Dry Contact Closed · Bit High' : 'Assertion Inactive · Dry Contact Open · Bit Low' }}
                          </div>
                      </div>

                      <!-- 2. Numeric Readout for INT / DINT / REAL / FLOAT -->
                      <div v-else-if="lastReadResult !== null && form.data_type !== 'STRING'" class="w-full max-w-lg p-6 rounded-2xl bg-gradient-to-b from-cyan-950/20 to-slate-950/80 border border-cyan-500/30 shadow-[0_0_30px_rgba(6,182,212,0.1)] flex flex-col items-center justify-center">
                          <div class="text-[10px] font-mono font-black text-cyan-500 uppercase tracking-widest mb-2">
                              {{ form.data_type }} REGISTER VALUE
                          </div>
                          <div class="text-5xl md:text-6xl font-mono font-black text-white tracking-tight drop-shadow-[0_0_25px_rgba(255,255,255,0.2)] truncate max-w-full">
                              {{ lastReadResult }}
                          </div>
                          <div class="text-[10px] font-mono text-slate-400 mt-2">
                              Precision Radix: Standard IEEE / Decimal Representation
                          </div>
                      </div>

                      <!-- 3. String Readout -->
                      <div v-else-if="lastReadResult !== null" class="w-full max-w-lg p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col">
                          <div class="text-[10px] font-mono font-black text-cyan-400 uppercase tracking-widest mb-2 flex justify-between">
                              <span>ASCII String Buffer</span>
                              <span class="text-slate-500">{{ String(lastReadResult).length }} chars</span>
                          </div>
                          <div class="p-3 bg-black/50 rounded-xl border border-slate-800/80 font-mono text-lg text-emerald-400 tracking-wider break-all select-all">
                              "{{ lastReadResult }}"
                          </div>
                      </div>

                      <!-- 4. Awaiting Signal / Standby -->
                      <div v-else class="flex flex-col items-center justify-center gap-3 py-6">
                          <div class="relative flex items-center justify-center h-20 w-20 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-inner">
                              <span class="animate-ping absolute inline-flex h-12 w-12 rounded-full bg-cyan-500/10"></span>
                              <i class="pi pi-wave-pulse text-cyan-500 text-3xl"></i>
                          </div>
                          <div class="text-center">
                              <span class="text-slate-300 text-xs font-black uppercase tracking-[0.2em] block">Standby for Telemetry</span>
                              <span class="text-slate-500 text-[10px] tracking-wider block mt-1">Select an address and click READ or toggle Live Watch</span>
                          </div>
                      </div>
                  </div>

                  <!-- Radix & Bitmask Inspector Grid (shown when data is present) -->
                  <div v-if="lastReadResult !== null" class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 border-t border-slate-800/60 shrink-0">
                      <div class="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex flex-col">
                          <span class="text-[9px] font-mono font-bold text-slate-500 uppercase tracking-wider">Decimal</span>
                          <span class="text-xs font-mono font-black text-slate-200 mt-0.5 truncate">{{ formattedDec }}</span>
                      </div>
                      <div class="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex flex-col">
                          <span class="text-[9px] font-mono font-bold text-slate-500 uppercase tracking-wider">Hexadecimal</span>
                          <span class="text-xs font-mono font-black text-cyan-400 mt-0.5 font-bold truncate">{{ formattedHex }}</span>
                      </div>
                      <div class="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex flex-col">
                          <span class="text-[9px] font-mono font-bold text-slate-500 uppercase tracking-wider">Bitmask</span>
                          <span class="text-xs font-mono font-black text-emerald-400 mt-0.5 tracking-wider truncate">{{ formattedBin }}</span>
                      </div>
                      <div class="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex flex-col">
                          <span class="text-[9px] font-mono font-bold text-slate-500 uppercase tracking-wider">Type / Offset</span>
                          <span class="text-xs font-mono font-black text-amber-400 mt-0.5 truncate">{{ form.data_type }} {{ form.data_type === 'BOOL' ? '· b' + form.bit_offset : '' }}</span>
                      </div>
                  </div>

                  <!-- Rolling Signal Trace Log (collapsible / compact) -->
                  <div v-if="readHistory.length > 0" class="mt-3 pt-3 border-t border-slate-800/60 flex flex-col max-h-36 shrink-0">
                      <div class="flex items-center justify-between text-[9px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-1.5 px-1">
                          <span class="flex items-center gap-1.5">
                              <i class="pi pi-list text-[9px] text-cyan-400"></i> Signal Trace (Last {{ readHistory.length }})
                          </span>
                          <span class="text-slate-500 font-medium">Time (IST · AM/PM) · Addr · Value</span>
                      </div>
                      <div class="flex-1 overflow-y-auto custom-scroll space-y-1 pr-1 font-mono text-[10px]">
                          <div v-for="item in readHistory" :key="item.id" class="flex items-center justify-between px-2.5 py-1 rounded bg-slate-900/40 border border-slate-800/50 hover:bg-slate-800/50 transition-colors">
                              <div class="flex items-center gap-2">
                                  <span class="text-slate-500">{{ item.time }}</span>
                                  <span class="font-bold text-cyan-400">{{ item.address }}</span>
                              </div>
                              <div class="flex items-center gap-2">
                                  <span v-if="item.isBool" class="px-1.5 py-0.5 rounded text-[9px] font-black uppercase"
                                        :class="item.boolVal ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400 border border-slate-700'">
                                      {{ item.boolVal ? 'HIGH (1)' : 'LOW (0)' }}
                                  </span>
                                  <span v-else class="text-slate-200 font-bold truncate max-w-[120px]">
                                      {{ item.value }}
                                  </span>
                                  <span class="text-[9px] text-slate-600">{{ item.latency }}ms</span>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>
              
              <!-- WRITE display -->
              <div v-else-if="operation === 'write'" class="w-full h-full flex flex-col justify-center gap-6">
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
              <!-- RANGE READ display -->
              <div v-else-if="operation === 'range_read'" class="w-full h-full flex flex-col min-h-0">
                 <div class="flex items-center gap-2 mb-4 self-start shrink-0">
                      <div class="h-1.5 w-1.5 rounded-full bg-fuchsia-500 shadow-[0_0_6px_#d946ef]"></div>
                      <span class="text-[9px] font-black tracking-[0.3em] text-fuchsia-600 uppercase">Tags Browser</span>
                  </div>
                  
                  <div class="flex-1 w-full flex flex-col bg-black/40 border border-slate-800 rounded-xl min-h-0 overflow-hidden">
                      <!-- Static Header -->
                      <div v-if="rangeResults.length > 0" class="flex bg-slate-900 border-b border-slate-700 w-full shrink-0 pr-3">
                          <div class="px-4 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-800 w-24 shrink-0 flex items-center">Address</div>
                          <div class="flex-1 px-4 py-2 text-[9px] font-black text-fuchsia-400 tracking-widest uppercase border-r border-slate-800 flex items-center">Value (INT/BOOL)</div>
                          <div v-if="!rangeResults[0]?.isBit" class="px-4 py-2 text-[9px] font-black text-cyan-400 tracking-widest uppercase border-r border-slate-800 w-24 shrink-0 flex items-center">HEX</div>
                          <div v-if="!rangeResults[0]?.isBit" class="px-4 py-2 text-[9px] font-black text-emerald-400 tracking-widest uppercase border-r border-slate-800 w-24 shrink-0 flex items-center">ASCII</div>
                          <div class="px-4 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase w-32 text-center shrink-0 flex items-center justify-center">Action</div>
                      </div>
                      
                      <!-- Virtual Body -->
                      <VirtualScroller v-if="rangeResults.length > 0" :items="rangeResults" :itemSize="48" class="flex-1 w-full custom-scroll">
                          <template #item="{ item, options }">
                              <div class="flex border-b border-slate-800/50 hover:bg-fuchsia-900/10 h-[48px] items-center" :class="{ 'bg-slate-900/30': options.even }">
                                  <div class="w-24 px-4 border-r border-slate-800/50 text-xs font-mono font-bold text-slate-300 h-full flex items-center shrink-0">{{ item.addr }}</div>
                                  <div class="flex-1 px-4 border-r border-slate-800/50 h-full flex items-center">
                                     <InputText v-model="item.val" class="w-full !h-8 !py-1 !px-2 text-sm font-mono bg-slate-900/50 border-slate-700/50 focus:border-fuchsia-500 text-fuchsia-100" />
                                  </div>
                                  <div v-if="!item.isBit" class="w-24 px-4 border-r border-slate-800/50 text-xs font-mono font-bold text-cyan-500/70 h-full flex items-center shrink-0">{{ item.hexVal }}</div>
                                  <div v-if="!item.isBit" class="w-24 px-4 border-r border-slate-800/50 text-xs font-mono font-bold text-emerald-500/70 h-full flex items-center shrink-0">{{ item.asciiVal }}</div>
                                  <div class="w-32 px-4 flex items-center justify-center shrink-0 h-full">
                                     <Button @click="writeRangeItem(item)" icon="pi pi-send" class="!h-8 !w-8 bg-slate-800 hover:bg-amber-500 text-slate-400 hover:text-black border-none" v-tooltip.left="'Write'" />
                                  </div>
                              </div>
                          </template>
                      </VirtualScroller>

                      <div v-else class="flex flex-1 items-center justify-center">
                          <span class="text-[10px] font-black text-slate-600 tracking-widest uppercase">No Data</span>
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
                <span class="text-xs font-black text-amber-500 tracking-[0.3em] uppercase drop-shadow-md">PRESETS (SPRAY SETTING)</span>
              </div>
              <div class="flex items-center gap-3">
                 <!-- Active preset type badge -->
                 <span class="px-2 py-0.5 rounded-full text-[8px] font-black tracking-widest uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                   {{ fanucForm.preset_type }}
                 </span>
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
                <Button @click="writeAllFanucPresets" label="WRITE ALL" icon="pi pi-upload" 
                        class="bg-amber-600 hover:bg-amber-500 border-none text-[9px] font-black tracking-widest text-white px-4 h-8 shadow-[0_0_10px_rgba(245,158,11,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected || !fanucPresets" :loading="loading" />
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
            <div class="w-px h-6 bg-slate-700/50 self-center"></div>
            <Button @click="fetchActivePresets" label="ACTIVE PRESETS" icon="pi pi-sliders-h" class="bg-indigo-900/40 hover:bg-indigo-800 text-indigo-400 border border-indigo-800/50 text-[10px] font-black tracking-wider px-3 py-1.5" :disabled="!store.isConnected || loading" />
            <Button @click="fetchDiagColorConfig" label="COLOR CONFIG" icon="pi pi-palette" class="bg-emerald-900/40 hover:bg-emerald-800 text-emerald-400 border border-emerald-800/50 text-[10px] font-black tracking-wider px-3 py-1.5" :disabled="!store.isConnected || loading" />
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
            <div class="flex-1 overflow-auto bg-black border border-slate-800/50 shadow-[inset_0_0_30px_rgba(0,0,0,0.8)] scrollbar-custom relative">
              <div v-if="!diagnosticLog" class="absolute inset-0 flex flex-col items-center justify-center opacity-30 select-none">
                 <i class="pi pi-server text-4xl mb-3"></i>
                 <span class="font-black tracking-[0.2em] uppercase text-[10px]">Select Diagnostic File</span>
                 <span class="text-[9px] text-slate-500 mt-2 text-center max-w-xs uppercase tracking-widest">FTP LINK: errall.ls · erract.ls · errhist.ls · summary.dg · logbook.ls</span>
              </div>
              <table v-else class="w-full text-left border-collapse min-w-max">
                <thead class="sticky top-0 bg-slate-900/95 backdrop-blur-md z-10 shadow-lg border-b border-slate-700">
                  <tr>
                    <th class="px-4 py-3 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-800/50 w-24">DATE / TIME</th>
                    <th class="px-4 py-3 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-800/50 w-24 text-center">SEVERITY</th>
                    <th class="px-4 py-3 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-800/50 w-32">ALARM CODE</th>
                    <th class="px-4 py-3 text-[9px] font-black text-slate-400 tracking-widest uppercase">MESSAGE</th>
                  </tr>
                </thead>
                <tbody class="font-mono text-xs">
                  <tr v-for="(alarm, i) in parsedDiagnosticAlarms" :key="i" class="border-b border-slate-800/30 hover:bg-slate-800/50 transition-colors">
                    <td class="px-4 py-2.5 border-r border-slate-800/30 text-slate-500">
                      <div class="flex flex-col gap-0.5">
                        <span>{{ alarm.date }}</span>
                        <span class="text-[10px]">{{ alarm.time }}</span>
                      </div>
                    </td>
                    <td class="px-4 py-2.5 border-r border-slate-800/30 text-center">
                       <span class="px-2 py-0.5 rounded-md border text-[9px] font-black tracking-widest" :class="alarm.cls">
                         {{ alarm.severity }}
                       </span>
                    </td>
                    <td class="px-4 py-2.5 border-r border-slate-800/30 font-bold" :class="alarm.severity === 'FAULT' ? 'text-red-300' : alarm.severity === 'WARN' ? 'text-amber-300' : 'text-blue-300'">
                      {{ alarm.code }}
                    </td>
                    <td class="px-4 py-2.5 text-slate-300">
                      {{ alarm.message }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          </div>
        </template>

        <!-- Fanuc Color Setup -->
        <template v-if="store.connectionConfig.plc_type === 'fanuc' && fanucMode === 'colors'">
          <div class="flex flex-col flex-1 min-h-0 relative select-none">
          <div class="flex-1 flex flex-col bg-slate-800 rounded-3xl border border-slate-700 shadow-[0_10px_40px_rgba(0,0,0,0.5)] overflow-hidden relative p-3 pb-4">
            <div class="absolute top-0 left-0 right-0 h-2 bg-emerald-500"></div>
            
            <div class="flex items-center justify-between px-3 mt-1 py-2 mb-2">
              <div class="flex flex-col">
                <span class="text-[10px] font-black text-slate-400 tracking-widest uppercase mb-0.5">PaintTool System</span>
                <span class="text-xs font-black text-emerald-500 tracking-[0.3em] uppercase drop-shadow-md">Color Configuration</span>
              </div>
            </div>

            <div class="flex-1 flex flex-col bg-slate-950 rounded-xl border-[6px] border-slate-900 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]">
              <div class="flex gap-4 bg-emerald-900/40 border-b border-emerald-800/50 px-4 py-3 items-end">
                <div class="flex flex-col gap-1.5 w-40">
                  <label class="text-[9px] font-black text-emerald-200 tracking-widest uppercase">Configuration Type</label>
                  <Dropdown v-model="fanucColorMode" :options="[{label: 'Color Setup', value: 'setup'}, {label: 'Cycle Times', value: 'cycle'}]" optionLabel="label" optionValue="value" class="w-full text-xs font-bold bg-slate-900/80 border-emerald-500/30 text-white" :disabled="!store.isConnected" @change="fanucColors = null" />
                </div>
                
                <Button @click="fetchFanucColors" label="FETCH FROM ROBOT" icon="pi pi-cloud-download" 
                        class="ml-auto bg-emerald-600 hover:bg-emerald-500 border-none text-[9px] font-black tracking-widest text-white px-5 h-8 shadow-[0_0_10px_rgba(16,185,129,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected" :loading="loading" />
                <Button v-if="fanucColorMode === 'setup'" @click="saveAllFanucColors" label="SAVE ALL COLORS" icon="pi pi-save" 
                        class="bg-amber-600 hover:bg-amber-500 border-none text-[9px] font-black tracking-widest text-white px-4 h-8 shadow-[0_0_10px_rgba(245,158,11,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected || !fanucColors" :loading="loading" />
              </div>

              <div class="flex-1 overflow-auto relative bg-[#0f172a]">
                <div v-if="!fanucColors" class="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-slate-900/80 backdrop-blur-sm z-20">
                   <div class="p-4 rounded-full bg-slate-800/80 border border-slate-700 shadow-xl">
                      <i class="pi pi-palette text-emerald-400 text-3xl animate-pulse"></i>
                   </div>
                   <span class="text-[10px] font-black tracking-[0.2em] text-slate-400 uppercase drop-shadow">Awaiting Color Data</span>
                </div>
                
                <table v-else class="w-full text-left border-collapse min-w-max">
                  <thead class="sticky top-0 bg-slate-800/90 backdrop-blur-md z-10 shadow-lg border-b border-slate-700">
                    <tr>
                      <th class="px-3 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-700/50 w-12 text-center">CLR</th>
                      <th v-for="col in displayColorColumns" :key="col.key" class="px-3 py-2 text-[9px] font-black text-emerald-400 tracking-widest uppercase border-r border-slate-700/50 text-center">
                        {{ col.label }} <span class="text-slate-400 block text-[8px] mt-0.5 opacity-80">{{ col.unit }}</span>
                      </th>
                      <th v-if="fanucColorMode === 'setup'" class="px-3 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase w-14 text-center">
                        <i class="pi pi-send"></i>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in fanucColors" :key="index" class="border-b border-slate-800/50 hover:bg-emerald-900/20 transition-colors group">
                      <td class="px-3 py-1.5 text-center border-r border-slate-800/50 bg-slate-900/20 text-[10px] font-black text-slate-500 tracking-wider">
                         {{ String(index + 1).padStart(2, '0') }}
                      </td>
                      <td v-for="col in displayColorColumns" :key="col.key" class="px-1 py-1 border-r border-slate-800/30 text-center">
                         <span v-if="fanucColorMode === 'cycle'" class="font-mono text-sm text-emerald-200">{{ row[col.key] !== undefined ? Number(row[col.key]).toFixed(1) : '-' }}</span>
                         <InputText v-else type="number" 
                                    v-model.number="row[col.key]" 
                                    class="w-full text-center font-mono text-sm bg-transparent border border-transparent focus:border-emerald-500 hover:bg-slate-800 transition-colors p-1.5 focus:shadow-[0_0_8px_rgba(16,185,129,0.2)] text-emerald-300" />
                      </td>
                      <td v-if="fanucColorMode === 'setup'" class="px-1 py-1.5 text-center">
                        <Button @click="saveSingleColor(index)" icon="pi pi-send" class="h-7 w-7 bg-slate-700/50 hover:bg-emerald-500 border-none text-slate-400 hover:text-black transition-all active:scale-90" v-tooltip.left="'Write Color ' + (index + 1)" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          </div>
        </template>

        <!-- Fanuc Manual Settings -->
        <template v-if="store.connectionConfig.plc_type === 'fanuc' && fanucMode === 'manual'">
          <div class="flex flex-col flex-1 min-h-0 relative select-none">
          <div class="flex-1 flex flex-col bg-slate-800 rounded-3xl border border-slate-700 shadow-[0_10px_40px_rgba(0,0,0,0.5)] overflow-hidden relative p-3 pb-4">
            <div class="absolute top-0 left-0 right-0 h-2 bg-blue-500"></div>
            <div class="flex items-center justify-between px-3 mt-1 py-2 mb-2">
              <div class="flex flex-col">
                <span class="text-[10px] font-black text-slate-400 tracking-widest uppercase mb-0.5">PaintTool System</span>
                <span class="text-xs font-black text-blue-500 tracking-[0.3em] uppercase drop-shadow-md">MANUAL SETTING (BELL/GUN)</span>
              </div>
            </div>
            <div class="flex-1 flex flex-col bg-slate-950 rounded-xl border-[6px] border-slate-900 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]">
              <div class="flex gap-4 bg-blue-900/40 border-b border-blue-800/50 px-4 py-3 items-end">
                
                <div class="flex flex-col gap-1.5 w-40">
                  <label class="text-[9px] font-black text-blue-200 tracking-widest uppercase">Unit Type</label>
                  <Dropdown v-model="fanucManualMode" :options="[{label: 'BELL', value: 'BELL'}, {label: 'GUN', value: 'GUN'}]" optionLabel="label" optionValue="value" class="w-full text-xs font-bold bg-slate-900/80 border-blue-500/30 text-white" :disabled="!store.isConnected" @change="fanucManual = null" />
                </div>
                
                <Button @click="fetchFanucExtended('manual')" label="FETCH MANUAL SETTINGS" icon="pi pi-cloud-download" 
                        class="ml-auto bg-blue-600 hover:bg-blue-500 border-none text-[9px] font-black tracking-widest text-white px-5 h-8 shadow-[0_0_10px_rgba(37,99,235,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected" :loading="loading" />
                <Button @click="saveFanucExtended('manual')" label="SAVE MANUAL SETTINGS" icon="pi pi-save" 
                        class="bg-amber-600 hover:bg-amber-500 border-none text-[9px] font-black tracking-widest text-white px-4 h-8 shadow-[0_0_10px_rgba(245,158,11,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected || !fanucManual" :loading="loading" />
              </div>
              <div class="flex-1 overflow-auto relative bg-[#0f172a]">
                <div v-if="!fanucManual" class="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-slate-900/80 backdrop-blur-sm z-20">
                   <div class="p-4 rounded-full bg-slate-800/80 border border-slate-700 shadow-xl">
                      <i class="pi pi-sliders-v text-blue-400 text-3xl animate-pulse"></i>
                   </div>
                   <span class="text-[10px] font-black tracking-[0.2em] text-slate-400 uppercase drop-shadow">Awaiting Manual Data</span>
                </div>
                <table v-else class="w-full text-left border-collapse min-w-max">
                  <thead class="sticky top-0 bg-slate-800/90 backdrop-blur-md z-10 shadow-lg border-b border-slate-700">
                    <tr>
                      <th class="px-3 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-700/50 w-12 text-center">CH</th>
                      <th v-for="col in displayManualColumns" :key="col.key" class="px-3 py-2 text-[9px] font-black text-blue-400 tracking-widest uppercase border-r border-slate-700/50 text-center">
                        {{ col.label }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in fanucManual" :key="index" class="border-b border-slate-800/50 hover:bg-blue-900/20 transition-colors">
                      <td class="px-3 py-1.5 text-center border-r border-slate-800/50 bg-slate-900/20 text-[10px] font-black text-slate-500 tracking-wider">
                         {{ String(index + 1).padStart(2, '0') }}
                      </td>
                      <td v-for="col in displayManualColumns" :key="col.key" class="px-1 py-1 border-r border-slate-800/30 text-center">
                         <InputText type="number" v-model.number="row[col.key]" class="w-full text-center font-mono text-sm bg-transparent border border-transparent focus:border-blue-500 hover:bg-slate-800 transition-colors p-1.5 focus:shadow-[0_0_8px_rgba(59,130,246,0.2)] text-blue-300" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          </div>
        </template>

        <!-- Fanuc GNM/BSC Settings -->
        <template v-if="store.connectionConfig.plc_type === 'fanuc' && fanucMode === 'gnmbsc'">
          <div class="flex flex-col flex-1 min-h-0 relative select-none">
          <div class="flex-1 flex flex-col bg-slate-800 rounded-3xl border border-slate-700 shadow-[0_10px_40px_rgba(0,0,0,0.5)] overflow-hidden relative p-3 pb-4">
            <div class="absolute top-0 left-0 right-0 h-2 bg-fuchsia-500"></div>
            <div class="flex items-center justify-between px-3 mt-1 py-2 mb-2">
              <div class="flex flex-col">
                <span class="text-[10px] font-black text-slate-400 tracking-widest uppercase mb-0.5">PaintTool System</span>
                <span class="text-xs font-black text-fuchsia-500 tracking-[0.3em] uppercase drop-shadow-md">GNM/BSC</span>
              </div>
            </div>
            <div class="flex-1 flex flex-col bg-slate-950 rounded-xl border-[6px] border-slate-900 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]">
              <div class="flex gap-4 bg-fuchsia-900/40 border-b border-fuchsia-800/50 px-4 py-3 items-end">
                <Button @click="fetchFanucExtended('gnmbsc')" label="FETCH GNM/BSC" icon="pi pi-cloud-download" 
                        class="ml-auto bg-fuchsia-600 hover:bg-fuchsia-500 border-none text-[9px] font-black tracking-widest text-white px-5 h-8 shadow-[0_0_10px_rgba(217,70,239,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected" :loading="loading" />
                <Button @click="saveFanucExtended('gnmbsc')" label="SAVE GNM/BSC" icon="pi pi-save" 
                        class="bg-amber-600 hover:bg-amber-500 border-none text-[9px] font-black tracking-widest text-white px-4 h-8 shadow-[0_0_10px_rgba(245,158,11,0.4)] transition-all active:scale-95" 
                        :disabled="!store.isConnected || !fanucGnmBsc" :loading="loading" />
              </div>
              <div class="flex-1 overflow-auto relative bg-[#0f172a]">
                <div v-if="!fanucGnmBsc" class="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-slate-900/80 backdrop-blur-sm z-20">
                   <div class="p-4 rounded-full bg-slate-800/80 border border-slate-700 shadow-xl">
                      <i class="pi pi-cog text-fuchsia-400 text-3xl animate-spin-slow"></i>
                   </div>
                   <span class="text-[10px] font-black tracking-[0.2em] text-slate-400 uppercase drop-shadow">Awaiting GNM/BSC Data</span>
                </div>
                <table v-else class="w-full text-left border-collapse min-w-max">
                  <thead class="sticky top-0 bg-slate-800/90 backdrop-blur-md z-10 shadow-lg border-b border-slate-700">
                    <tr>
                      <th class="px-3 py-2 text-[9px] font-black text-slate-400 tracking-widest uppercase border-r border-slate-700/50 w-12 text-center">UNIT</th>
                      <th v-for="col in displayGnmBscColumns" :key="col.key" class="px-3 py-2 text-[9px] font-black text-fuchsia-400 tracking-widest uppercase border-r border-slate-700/50 text-center">
                        {{ col.label }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in fanucGnmBsc" :key="index" class="border-b border-slate-800/50 hover:bg-fuchsia-900/20 transition-colors">
                      <td class="px-3 py-1.5 text-center border-r border-slate-800/50 bg-slate-900/20 text-[10px] font-black text-slate-500 tracking-wider">
                         {{ String(index + 1).padStart(2, '0') }}
                      </td>
                      <td v-for="col in displayGnmBscColumns" :key="col.key" class="px-1 py-1 border-r border-slate-800/30 text-center">
                         <InputText type="number" v-model.number="row[col.key]" class="w-full text-center font-mono text-sm bg-transparent border border-transparent focus:border-fuchsia-500 hover:bg-slate-800 transition-colors p-1.5 focus:shadow-[0_0_8px_rgba(217,70,239,0.2)] text-fuchsia-300" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          </div>
        </template>


      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
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
const lastReadMeta = ref(null)
const readHistory = ref([])
const latencyMs = ref(0)
let latencyTimer = null

const dataTypes = ref(['BOOL', 'INT', 'DINT', 'REAL', 'FLOAT', 'STRING'])
const fanucPresetSchema = ref(null)
const fanucPresetTypes = computed(() => fanucPresetSchema.value ? Object.keys(fanucPresetSchema.value) : ['BELL', 'GUN'])

const form = ref({
  data_type: 'INT',
  address: '',
  bit_offset: 0,
  register_count: 10,
  write_val: ''
})

const rangeForm = ref({
  prefix: 'D',
  start: 0,
  count: 10
})

const rangeResults = ref([])


// Fanuc specific state
const fanucMode = ref('pendant') // 'pendant', 'diagnostics', 'colors'
const fanucForm = ref({
  job_no: 1,
  color_no: 1,
  preset_type: 'BELL'
})
const fanucPresets = ref(null)

const fetchFanucSchema = async () => {
    try {
        const res = await api.getFanucSchema();
        if (res.data.success) {
            fanucPresetSchema.value = res.data.schema;
        }
    } catch (e) {
        console.error("Failed to fetch Fanuc preset schema", e);
    }
}

// ─── Latency Polling ───
const pollLatency = async () => {
    if (!store.isConnected) { latencyMs.value = 0; return; }
    try {
        const cfg = store.connectionConfig;
        const res = await api.getLatency(cfg.plc_type, cfg.ip, cfg.port);
        if (res.data.success) {
            latencyMs.value = res.data.latency_ms || 0;
        }
    } catch { latencyMs.value = 0; }
}

onMounted(() => {
    fetchFanucSchema();
    fetchFanucColorSchema();
    fetchFanucExtendedSchema();
    latencyTimer = setInterval(pollLatency, 5000);
})

onUnmounted(() => {
    if (latencyTimer) clearInterval(latencyTimer);
})

const diagnosticLog = ref(null)

const fanucColorSchema = ref(null);
const fanucColorMode = ref('setup');
const fanucColors = ref(null);


const fanucExtendedSchema = ref(null);
const fanucManualMode = ref('BELL');
const fanucManual = ref(null);
const fanucGnmBsc = ref(null);

const fetchFanucExtendedSchema = async () => {
    try {
        const res = await api.getFanucExtendedSchema();
        if (res.data.success) {
            fanucExtendedSchema.value = res.data;
        }
    } catch (e) {
        console.error("Failed to fetch Fanuc extended schema", e);
    }
}

const fetchFanucExtended = async (type) => {
    if (!store.isConnected) return;
    loading.value = true;
    try {
        const payload = { ...store.connectionConfig, manual_type: type === 'manual' ? fanucManualMode.value : undefined };
        const res = await api.getFanucExtended(payload, type);
        if (res.data.success) {
            if (type === 'manual') fanucManual.value = res.data.value;
            if (type === 'gnmbsc') fanucGnmBsc.value = res.data.value;
            toast.add({ severity: 'success', summary: 'Data Fetched', detail: `Loaded ${type} data.`, life: 2500 });
        } else {
            toast.add({ severity: 'error', summary: 'Fetch Error', detail: res.data.message, life: 5000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: `Could not fetch ${type} data`, life: 4000 });
    } finally {
        loading.value = false;
    }
}

const saveFanucExtended = async (type) => {
    if (!store.isConnected) return;
    loading.value = true;
    try {
        const valueToSave = type === 'manual' ? fanucManual.value : fanucGnmBsc.value;
        const payload = { ...store.connectionConfig, data_type: 'STRING', address: 'EXT_SETUP', value: valueToSave, manual_type: type === 'manual' ? fanucManualMode.value : undefined };
        const res = await api.saveFanucExtended(payload, type);
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Data Saved', detail: `Saved ${type} config.`, life: 3000 });
        } else {
            toast.add({ severity: 'error', summary: 'Save Error', detail: res.data.message, life: 5000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: `Could not save ${type} data`, life: 4000 });
    } finally {
        loading.value = false;
    }
}

const displayManualColumns = computed(() => {
    if (!fanucExtendedSchema.value || !fanucExtendedSchema.value.manual_vars) return [];
    const vars = fanucExtendedSchema.value.manual_vars[fanucManualMode.value] || [];
    return vars.map(k => ({
        key: k,
        label: k.replace(/_/g, ' ').toUpperCase()
    }));
});

const displayGnmBscColumns = computed(() => {
    if (!fanucExtendedSchema.value || !fanucExtendedSchema.value.gnm_bsc_vars) return [];
    return fanucExtendedSchema.value.gnm_bsc_vars.map(k => ({
        key: k,
        label: k.replace(/_/g, ' ').toUpperCase()
    }));
});

const fetchFanucColorSchema = async () => {
    try {
        const res = await api.getFanucColorSchema();
        if (res.data.success) {
            fanucColorSchema.value = res.data;
        }
    } catch (e) {
        console.error("Failed to fetch Fanuc color schema", e);
    }
}

const fetchFanucColors = async () => {
    if (!store.isConnected) return;
    loading.value = true;
    try {
        const payload = { ...store.connectionConfig };
        const res = await api.getFanucColors(payload, fanucColorMode.value);
        if (res.data.success) {
            fanucColors.value = res.data.value;
            toast.add({ severity: 'success', summary: 'Colors Fetched', detail: `Loaded color ${fanucColorMode.value} data.`, life: 2500 });
        } else {
            toast.add({ severity: 'error', summary: 'Fetch Error', detail: res.data.message, life: 5000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Could not fetch color data', life: 4000 });
    } finally {
        loading.value = false;
    }
}

const saveAllFanucColors = async () => {
    if (!store.isConnected || !fanucColors.value) return;
    loading.value = true;
    try {
        const payload = { ...store.connectionConfig, data_type: 'STRING', address: 'COLOR_SETUP', value: fanucColors.value };
        const res = await api.saveFanucColors(payload, 'setup');
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Colors Saved', detail: 'All color configurations written to robot.', life: 3000 });
        } else {
            toast.add({ severity: 'error', summary: 'Save Error', detail: res.data.message, life: 5000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Could not save color data', life: 4000 });
    } finally {
        loading.value = false;
    }
}

const saveSingleColor = async (index) => {
    if (!store.isConnected || !fanucColors.value) return;
    loading.value = true;
    try {
        const payload = { ...store.connectionConfig, data_type: 'STRING', address: 'COLOR_SETUP', value: [fanucColors.value[index]] };
        const res = await api.saveFanucColors(payload, 'setup');
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Color Saved', detail: `Color ${index + 1} written to robot.`, life: 2500 });
        } else {
            toast.add({ severity: 'error', summary: 'Save Error', detail: res.data.message, life: 5000 });
        }
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Could not save color data', life: 4000 });
    } finally {
        loading.value = false;
    }
}

const displayColorColumns = computed(() => {
    if (!fanucColorSchema.value) return [];
    const keys = fanucColorMode.value === 'setup' ? fanucColorSchema.value.setup_vars : fanucColorSchema.value.cycle_vars;
    if (!keys) return [];
    
    return keys.map(k => ({
        key: k,
        label: k.replace(/_/g, ' ').toUpperCase(),
        unit: fanucColorMode.value === 'cycle' ? 'sec' : (k.includes('time') || k.includes('delay') ? 'sec' : k.includes('psi') ? 'psi' : k.includes('distance') ? 'mm' : k.includes('count') ? '#' : 'val')
    }));
});

// ─── Diagnostics ───

const fetchFanucDiagnostic = async (filename) => {
  if (!store.isConnected) return;
  loading.value = true;
  diagnosticLog.value = null;
  try {
    const payload = {
      ...store.connectionConfig,
      data_type: 'STRING',
      address: filename
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

const fetchActivePresets = async () => {
  if (!store.isConnected) return;
  loading.value = true;
  diagnosticLog.value = null;
  try {
    const payload = {
      ...store.connectionConfig,
      data_type: 'STRING',
      address: `${fanucForm.value.job_no},${fanucForm.value.color_no},${fanucForm.value.preset_type}`
    };
    const res = await api.readData(payload);
    if (res.data.success) {
      const presets = res.data.value;
      let log = `=== ACTIVE PRESETS ===\nJob: ${fanucForm.value.job_no}  Color: ${fanucForm.value.color_no}  Type: ${fanucForm.value.preset_type}\n${'─'.repeat(60)}\n`;
      presets.forEach((p, i) => {
        log += `Preset ${String(i+1).padStart(2,'0')}: ${Object.entries(p).filter(([k]) => !['job_no','color_no','preset_no'].includes(k)).map(([k,v]) => `${k}=${v}`).join('  ')}\n`;
      });
      diagnosticLog.value = log;
      toast.add({ severity: 'success', summary: 'Presets Loaded', detail: 'Active presets displayed in diagnostic log', life: 2500 });
    }
  } catch (error) {
    diagnosticLog.value = `[ERROR FETCHING PRESETS]\n${error.message}`;
  } finally {
    loading.value = false;
  }
}

const fetchDiagColorConfig = async () => {
  if (!store.isConnected) return;
  loading.value = true;
  diagnosticLog.value = null;
  try {
    const payload = { ...store.connectionConfig };
    const res = await api.getFanucColors(payload, 'setup');
    if (res.data.success) {
      const colors = res.data.value;
      let log = `=== COLOR CONFIGURATION ===\n${'─'.repeat(60)}\n`;
      colors.forEach((c) => {
        const vals = Object.entries(c).filter(([k]) => k !== 'color_no').map(([k,v]) => `${k}=${v}`).join('  ');
        if (vals.replace(/=0(\.0)?/g, '').trim()) {
          log += `Color ${String(c.color_no).padStart(2,'0')}: ${vals}\n`;
        }
      });
      if (log.split('\n').length <= 3) log += '(No color data configured on this controller)\n';
      diagnosticLog.value = log;
      toast.add({ severity: 'success', summary: 'Color Config', detail: 'Color configuration displayed', life: 2500 });
    }
  } catch (error) {
    diagnosticLog.value = `[ERROR FETCHING COLOR CONFIG]\n${error.message}`;
  } finally {
    loading.value = false;
  }
}

const clearDiagnosticLog = () => {
  diagnosticLog.value = null;
  toast.add({ severity: 'info', summary: 'Log Cleared', detail: 'Diagnostic log has been cleared', life: 1500 });
}

// Parse diagnostic log lines with alarm severity coloring
const parsedDiagnosticAlarms = computed(() => {
  if (!diagnosticLog.value) return [];
  const lines = diagnosticLog.value.split('\n');
  const alarms = [];
  
  lines.forEach(line => {
      const cleanLine = line.trim();
      if (cleanLine.length === 0 || cleanLine.startsWith('===')) return;
      
      let date = '-';
      let time = '-';
      let code = 'SYS';
      let msg = cleanLine.replace(/"/g, '').trim();
      let severity = 'INFO';
      let cls = 'bg-blue-500/10 text-blue-400 border-blue-500/30';

      const dateMatch = cleanLine.match(/(\d{1,2}-[A-Za-z]{3}-\d{2})\s+(\d{1,2}:\d{2}\s*(?::\d{2})?)/);
      if (dateMatch) {
          date = dateMatch[1];
          time = dateMatch[2];
          // Strip date from msg
          msg = msg.replace(dateMatch[0], '').trim();
      }
      
      const codeMatch = msg.match(/([A-Z]+-\d+)\s+(.*)/i);
      if (codeMatch) {
          code = codeMatch[1].toUpperCase();
          msg = codeMatch[2].trim();
      } else if (msg.includes('R E S E T')) {
          code = 'RESET';
          msg = 'Fault Reset';
      }
      
      // Remove trailing junk like 'WARN   00000000' from the message
      const tailMatch = msg.match(/(.*)\s+(WARN|FAULT|INFO|NONE)\s*\d*$/);
      if (tailMatch) {
          msg = tailMatch[1].trim();
      }
      
      if (cleanLine.includes('FAULT') || code.startsWith('SRVO') || code.startsWith('SYST') || code.startsWith('MOTN')) {
          severity = 'FAULT';
          cls = 'bg-red-500/10 text-red-400 border-red-500/30';
      } else if (cleanLine.includes('WARN') || code.startsWith('WARN') || code.startsWith('TPIF')) {
          severity = 'WARN';
          cls = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      } else if (code === 'RESET') {
          severity = 'INFO';
          cls = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      }
      
      // Only push if it's not just a bunch of numbers or empty
      if (msg.length > 2 && msg !== '00000000') {
          alarms.push({
              date: date,
              time: time,
              code: code,
              message: msg,
              severity: severity,
              cls: cls,
              raw: cleanLine
          });
      }
  });
  
  return alarms;
});

const displayColumns = computed(() => {
  const defaultColumns = [
    { key: 'fluid_rate', label: 'Fluid Rate', unit: 'cc/min', min: 0, max: 2000 },
    { key: 'atom_air', label: 'Atom Air', unit: 'L/min', min: 0, max: 800 },
    { key: 'fan_air', label: 'Fan Air', unit: 'L/min', min: 0, max: 800 },
    { key: 'estat_KV', label: 'E-Stat', unit: 'kV', min: 0, max: 100 }
  ];

  if (!fanucPresetSchema.value) return defaultColumns;
  
  const schemaKeys = fanucPresetSchema.value[fanucForm.value.preset_type] || [];
  if (!schemaKeys.length) return defaultColumns;

  // Map known keys to rich objects, or create generic ones
  const richMap = {
      'fluid_rate': { key: 'fluid_rate', label: 'Fluid Rate', unit: 'cc/min', min: 0, max: 2000 },
      'bell_speed': { key: 'bell_speed', label: 'Bell Speed', unit: 'krpm', min: 0, max: 100 },
      'disk_speed': { key: 'disk_speed', label: 'Disk Speed', unit: 'krpm', min: 0, max: 100 },
      'shape_air1': { key: 'shape_air1', label: 'Shape Air 1', unit: 'L/min', min: 0, max: 800 },
      'shape_air2': { key: 'shape_air2', label: 'Shape Air 2', unit: 'L/min', min: 0, max: 800 },
      'shape_air': { key: 'shape_air', label: 'Shape Air', unit: 'L/min', min: 0, max: 800 },
      'atom_air': { key: 'atom_air', label: 'Atom Air', unit: 'L/min', min: 0, max: 800 },
      'fan_air': { key: 'fan_air', label: 'Fan Air', unit: 'L/min', min: 0, max: 800 },
      'pressure': { key: 'pressure', label: 'Pressure', unit: 'psi', min: 0, max: 1000 },
      'estat_KV': { key: 'estat_KV', label: 'E-Stat', unit: 'kV', min: 0, max: 100 }
  };

  return schemaKeys.map(key => richMap[key] || { key: key, label: key.replace('_', ' ').toUpperCase(), unit: '', min: 0, max: 10000 });
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
  if (t === 'opcua') return form.value.data_type === 'BOOL' ? 'ns=2;s=Device.Running' : 'ns=2;s=Device.Speed';
  return 'Address';
})

const quickAddresses = computed(() => {
  const t = store.connectionConfig.plc_type;
  if (t === 'mitsubishi') return [
    { label: 'M0', addr: 'M0', type: 'BOOL', desc: 'Relay Bit 0' },
    { label: 'M100', addr: 'M100', type: 'BOOL', desc: 'Aux Relay 100' },
    { label: 'D0', addr: 'D0', type: 'INT', desc: 'Data Reg 0' },
    { label: 'D100', addr: 'D100', type: 'INT', desc: 'Data Reg 100' },
    { label: 'X0', addr: 'X0', type: 'BOOL', desc: 'Input 0' },
    { label: 'Y0', addr: 'Y0', type: 'BOOL', desc: 'Output 0' },
  ];
  if (t === 'siemens') return [
    { label: 'DB1.DBX0.0', addr: 'DB1.DBX0.0', type: 'BOOL', desc: 'DB1 Bit 0' },
    { label: 'DB1.DBW2', addr: 'DB1.DBW2', type: 'INT', desc: 'DB1 Word 2' },
    { label: 'DB1.DBD4', addr: 'DB1.DBD4', type: 'DINT', desc: 'DB1 DWord 4' },
    { label: 'MW0', addr: 'MW0', type: 'INT', desc: 'Memory Word 0' },
  ];
  if (t === 'opcua') return [
    { label: 'Device.Running', addr: 'ns=2;s=Device.Running', type: 'BOOL', desc: 'Motor State' },
    { label: 'Device.Speed', addr: 'ns=2;s=Device.Speed', type: 'INT', desc: 'Motor RPM' },
    { label: 'Device.Temp', addr: 'ns=2;s=Device.Temp', type: 'REAL', desc: 'Temperature' },
  ];
  if (t === 'abb' || t === 'modbus') return [
    { label: '00001', addr: '00001', type: 'BOOL', desc: 'Coil 1' },
    { label: '10001', addr: '10001', type: 'BOOL', desc: 'Discrete Input 1' },
    { label: '40001', addr: '40001', type: 'INT', desc: 'Holding Reg 1' },
    { label: '30001', addr: '30001', type: 'INT', desc: 'Input Reg 1' },
  ];
  return [
    { label: 'R0', addr: 'R0', type: 'INT', desc: 'Reg 0' },
    { label: 'R100', addr: 'R100', type: 'INT', desc: 'Reg 100' },
  ];
});

const applyQuickAddress = (qa) => {
  form.value.address = qa.addr;
  if (qa.type) {
    form.value.data_type = qa.type;
    onDataTypeChange();
  }
};

const isBoolResult = computed(() => {
  if (lastReadResult.value === null) return false;
  return form.value.data_type === 'BOOL' || typeof lastReadResult.value === 'boolean' || lastReadResult.value === 'true' || lastReadResult.value === 'false';
});

const boolResultValue = computed(() => {
  const val = lastReadResult.value;
  return val === true || val === 'true' || val === 1 || val === '1';
});

const formattedDec = computed(() => {
  if (lastReadResult.value === null) return '—';
  if (isBoolResult.value) return boolResultValue.value ? '1' : '0';
  if (typeof lastReadResult.value === 'number') return lastReadResult.value.toLocaleString();
  return String(lastReadResult.value);
});

const formattedHex = computed(() => {
  if (lastReadResult.value === null) return '0x00';
  if (isBoolResult.value) return boolResultValue.value ? '0x01' : '0x00';
  const num = Number(lastReadResult.value);
  if (!isNaN(num) && Number.isInteger(num)) {
    return '0x' + (num >>> 0).toString(16).toUpperCase().padStart(4, '0');
  }
  return '—';
});

const formattedBin = computed(() => {
  if (lastReadResult.value === null) return '0000 0000';
  if (isBoolResult.value) return boolResultValue.value ? '0000 0001' : '0000 0000';
  const num = Number(lastReadResult.value);
  if (!isNaN(num) && Number.isInteger(num)) {
    const b = (num >>> 0).toString(2).padStart(16, '0');
    return b.slice(0, 8) + ' ' + b.slice(8);
  }
  return '—';
});

const addReadHistoryItem = (val, meta) => {
  const isBool = meta.dataType === 'BOOL' || typeof val === 'boolean' || val === 'true' || val === 'false';
  const boolVal = isBool ? (val === true || val === 'true' || val === 1 || val === '1') : null;
  readHistory.value.unshift({
    id: Date.now() + Math.random(),
    time: meta.timestamp,
    address: meta.address,
    type: meta.dataType,
    value: val,
    latency: meta.latency,
    isBool,
    boolVal
  });
  if (readHistory.value.length > 15) {
    readHistory.value.pop();
  }
};

const clearReadHistory = () => {
  readHistory.value = [];
};

const copyReadResult = async () => {
  if (lastReadResult.value === null) return;
  try {
    await navigator.clipboard.writeText(String(lastReadResult.value));
    toast.add({ severity: 'info', summary: 'Copied', detail: `Copied ${lastReadResult.value} to clipboard`, life: 2000 });
  } catch (e) {
    // clipboard fallback
  }
};

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

const formatIndianTime = (date = new Date()) => {
  const parts = new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  }).formatToParts(date);

  let hour = '', minute = '', dayPeriod = '';
  for (const p of parts) {
    if (p.type === 'hour') hour = p.value;
    else if (p.type === 'minute') minute = p.value;
    else if (p.type === 'dayPeriod') dayPeriod = p.value.toUpperCase();
  }
  return `${hour.padStart(2, '0')}:${minute} ${dayPeriod}`;
};

const performRead = async () => {
    loading.value = true;
    const startT = performance.now();
    try {
        const payload = buildPayload();
        const res = await api.readData(payload);
        const callLatency = Math.round(performance.now() - startT);
        if (res.data.success) {
            lastReadResult.value = res.data.value;
            const now = new Date();
            const timeStr = formatIndianTime(now);
            const meta = {
                timestamp: timeStr,
                latency: res.data.latency_ms || callLatency,
                address: form.value.address,
                dataType: form.value.data_type,
                bitOffset: form.value.bit_offset,
                success: true
            };
            lastReadMeta.value = meta;
            addReadHistoryItem(res.data.value, meta);
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
            data_type: 'STRING',
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

const writeAllFanucPresets = async () => {
    if (!fanucPresets.value) return;
    loading.value = true;
    try {
        const payload = {
            ...store.connectionConfig,
            data_type: 'STRING',
            address: `${fanucForm.value.job_no},${fanucForm.value.color_no},${fanucForm.value.preset_type}`,
            value: fanucPresets.value
        };
        const res = await api.writeData(payload);
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'All Presets Written', detail: `All ${fanucPresets.value.length} presets synchronized`, life: 3000 });
        } else {
            toast.add({ severity: 'error', summary: 'Write Error', detail: res.data.message, life: 5000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Write Failed', detail: e.message, life: 5000 });
    } finally {
        loading.value = false;
    }
}

const submitOperation = () => {
    if (operation.value === 'range_read') {
        performRangeRead();
        return;
    }
    if (!form.value.address) {
        toast.add({ severity: 'warn', summary: 'Required', detail: 'Enter an address', life: 3000 });
        return;
    }
    if (operation.value === 'read') performRead();
    else performWrite();
}


const performRangeRead = async () => {
    loading.value = true;
    try {
        const isBit = ['M', 'X', 'Y', 'B', 'L', 'F', 'SM', 'TS', 'CS'].includes(rangeForm.value.prefix);
        const payload = {
            ...store.connectionConfig,
            data_type: isBit ? 'BIT_ARRAY' : 'WORD_ARRAY',
            address: `${rangeForm.value.prefix}${rangeForm.value.start}`,
            register_count: rangeForm.value.count || 10
        };
        const res = await api.readData(payload);
        if (res.data.success) {
            const arr = res.data.value;
            rangeResults.value = arr.map((v, i) => {
                const isWord = !isBit;
                let hexVal = '';
                let asciiVal = '';
                if (isWord) {
                    const w = Number(v) & 0xFFFF;
                    hexVal = '0x' + w.toString(16).toUpperCase().padStart(4, '0');
                    const low = w & 0xFF;
                    const high = (w >> 8) & 0xFF;
                    const c1 = (low >= 32 && low <= 126) ? String.fromCharCode(low) : '.';
                    const c2 = (high >= 32 && high <= 126) ? String.fromCharCode(high) : '.';
                    asciiVal = c1 + c2;
                }
                return {
                    addr: `${rangeForm.value.prefix}${rangeForm.value.start + i}`,
                    val: String(v),
                    hexVal,
                    asciiVal,
                    isBit
                }
            });
            toast.add({ severity: 'success', summary: 'Read OK', detail: `Fetched ${arr.length} tags`, life: 2000 });
        } else {
            toast.add({ severity: 'error', summary: 'Read Error', detail: res.data.message, life: 5000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Read Failed', detail: e.message, life: 5000 });
    } finally {
        loading.value = false;
    }
}

const writeRangeItem = async (item) => {
    loading.value = true;
    try {
        const isBit = ['M', 'X', 'Y', 'B', 'L', 'F', 'SM', 'TS', 'CS'].includes(rangeForm.value.prefix);
        const payload = {
            ...store.connectionConfig,
            data_type: isBit ? 'BOOL' : 'INT',
            address: item.addr,
            value: isBit ? (item.val === '1' || item.val.toLowerCase() === 'true') : Number(item.val)
        };
        const res = await api.writeData(payload);
        if (res.data.success) {
            toast.add({ severity: 'success', summary: 'Write OK', detail: `${item.addr} updated`, life: 2000 });
        } else {
            toast.add({ severity: 'error', summary: 'Write Error', detail: res.data.message, life: 5000 });
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Write Failed', detail: e.message, life: 5000 });
    } finally {
        loading.value = false;
    }
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
