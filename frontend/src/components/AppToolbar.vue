<template>
  <header class="bg-slate-900 text-white p-4 shadow-md flex justify-between items-center border-b border-slate-700">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold">PLC</div>
      <h1 class="text-xl font-bold tracking-wide">Industrial Communication Test Tool</h1>
    </div>
    <div class="flex items-center gap-4 text-sm font-medium bg-slate-800 px-4 py-1.5 rounded-full border border-slate-700">
      <span :class="store.isConnected ? 'text-green-400' : 'text-slate-400'" class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full" :class="store.isConnected ? 'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)]' : 'bg-slate-400'"></span>
        {{ store.isConnected ? 'Connected' : 'Disconnected' }}
      </span>
    </div>
  </header>
</template>

<script setup>
import { usePlcStore } from '../stores/plcStore'
const store = usePlcStore()
</script>
