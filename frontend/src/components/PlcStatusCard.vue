<template>
  <Card class="shrink-0 border-0 relative overflow-hidden">
    <template #content>
      <div class="absolute -right-4 -top-4 text-slate-800/15">
        <i class="pi pi-server" style="font-size: 6rem;"></i>
      </div>
      
      <div class="relative z-10">
        <div class="flex items-center gap-2 mb-3">
          <div class="h-1.5 w-1.5 rounded-full" :class="store.isConnected ? 'bg-emerald-500 shadow-[0_0_6px_#22c55e]' : 'bg-slate-600'"></div>
          <h2 class="text-[10px] font-black tracking-[0.2em] uppercase" :class="store.isConnected ? 'text-emerald-500' : 'text-slate-500'">Network Status</h2>
        </div>
        
        <div class="flex flex-col gap-2">
          <div class="flex justify-between items-center border-b border-slate-800/50 pb-1.5">
            <span class="text-slate-500 text-xs font-medium">Protocol</span>
            <span class="text-white font-bold uppercase tracking-wider text-[10px] bg-slate-800/80 px-2 py-0.5 rounded-md">{{ store.connectionConfig.plc_type }}</span>
          </div>
          <div class="flex justify-between items-center border-b border-slate-800/50 pb-1.5">
            <span class="text-slate-500 text-xs font-medium">Target</span>
            <span class="text-slate-300 font-mono text-xs">{{ store.connectionConfig.ip }}:{{ store.connectionConfig.port }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-slate-500 text-xs font-medium">Link</span>
            <span class="text-xs font-black tracking-widest uppercase" :class="store.isConnected ? 'text-emerald-400' : 'text-red-400'">
              {{ store.isConnected ? 'ACTIVE' : 'DOWN' }}
            </span>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { usePlcStore } from '../stores/plcStore'
import Card from 'primevue/card'
const store = usePlcStore()
</script>
