<template>
  <div class="flex flex-col xl:flex-row gap-4 w-full h-full overflow-hidden">
    <!-- Left Column -->
    <div class="w-full xl:w-[340px] xl:min-w-[340px] shrink-0 flex flex-col gap-4 overflow-y-auto pr-1">
      <PlcStatusCard />
      <PlcConnectionForm />
    </div>
    
    <!-- Right Column - fills remaining -->
    <div class="flex-1 min-w-0 overflow-hidden">
      <PlcDataForm class="w-full h-full" />
    </div>
  </div>
</template>

<script setup>
import PlcConnectionForm from '../components/PlcConnectionForm.vue'
import PlcDataForm from '../components/PlcDataForm.vue'
import PlcStatusCard from '../components/PlcStatusCard.vue'
</script>
