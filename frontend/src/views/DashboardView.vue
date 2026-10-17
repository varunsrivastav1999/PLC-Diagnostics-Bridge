<template>
  <div class="dashboard-grid h-full min-h-0">
    <aside class="dashboard-rail">
      <PlcConnectionForm />
    </aside>

    <section class="dashboard-workspace flex flex-col min-h-0">
      <PlcDataForm class="w-full min-h-0 flex-1" />
    </section>
  </div>
</template>

<script setup>
import PlcConnectionForm from '../components/PlcConnectionForm.vue'
import PlcDataForm from '../components/PlcDataForm.vue'
</script>
