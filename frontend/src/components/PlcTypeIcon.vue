<template>
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-full w-full">
    <g v-if="normalizedType === 'siemens'" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <rect x="3.5" y="5.5" width="17" height="13" rx="3.5" opacity="0.22" />
      <path d="M6.5 9H17.5" />
      <path d="M6.5 12H14.5" />
      <path d="M6.5 15H12.5" />
      <path d="M18 8.5V15.5" opacity="0.72" />
    </g>

    <g v-else-if="normalizedType === 'mitsubishi'" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 3.5L19.5 12L12 20.5L4.5 12L12 3.5Z" opacity="0.18" fill="currentColor" />
      <path d="M12 6.5L16.5 12L12 17.5L7.5 12L12 6.5Z" />
      <path d="M8 12H16" />
    </g>

    <g v-else-if="normalizedType === 'rockwell'" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="4" opacity="0.18" fill="currentColor" />
      <path d="M8 8H16V16" />
      <path d="M8 16L16 8" />
      <path d="M12 8V5.5" opacity="0.72" />
    </g>

    <g v-else-if="normalizedType === 'abb'" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="8" opacity="0.18" fill="currentColor" />
      <path d="M12 5.5V12L15.5 14.5" />
      <path d="M8.5 15.5H15.5" />
    </g>

    <g v-else-if="normalizedType === 'fanuc'" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M6 17.5H10.5L13 13.5L16.5 11L18.5 7.5" />
      <circle cx="18.5" cy="7.5" r="1.5" fill="currentColor" />
      <circle cx="12.8" cy="13.5" r="1.4" fill="currentColor" opacity="0.85" />
      <path d="M7 17.5V20" />
      <path d="M9.5 17.5V20" opacity="0.72" />
    </g>

    <g v-else stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="5" width="16" height="14" rx="3.5" opacity="0.18" fill="currentColor" />
      <path d="M8 12H16" />
      <path d="M12 8V16" />
    </g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: '',
  },
})

const normalizedType = computed(() => (props.type || '').toLowerCase())
</script>
