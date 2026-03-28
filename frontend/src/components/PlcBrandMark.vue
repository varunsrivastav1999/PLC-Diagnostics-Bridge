<template>
  <div class="plc-brand-mark" :class="{ compact }" aria-hidden="true">
    <svg viewBox="0 0 88 88" fill="none" xmlns="http://www.w3.org/2000/svg" class="brand-svg">
      <defs>
        <linearGradient id="plc-core" x1="18" y1="18" x2="70" y2="70" gradientUnits="userSpaceOnUse">
          <stop stop-color="#67E8F9" />
          <stop offset="0.55" stop-color="#38BDF8" />
          <stop offset="1" stop-color="#F59E0B" />
        </linearGradient>
        <linearGradient id="plc-shell" x1="16" y1="10" x2="74" y2="78" gradientUnits="userSpaceOnUse">
          <stop stop-color="#94A3B8" stop-opacity="0.9" />
          <stop offset="1" stop-color="#0F172A" stop-opacity="0.85" />
        </linearGradient>
      </defs>

      <circle cx="44" cy="44" r="35" class="halo" />
      <circle cx="44" cy="44" r="27.5" class="orbit orbit-a" />
      <circle cx="44" cy="44" r="18.5" class="orbit orbit-b" />

      <path
        d="M44 12L68.5 26.2V54.8L44 69L19.5 54.8V26.2L44 12Z"
        fill="url(#plc-shell)"
        class="shell"
      />
      <path
        d="M44 24L58.5 32.4V48.8L44 57.2L29.5 48.8V32.4L44 24Z"
        fill="url(#plc-core)"
        class="core"
      />
      <path d="M32 44H56" class="trace pulse" />
      <path d="M44 32V56" class="trace pulse" />
      <path d="M21 33H29" class="pin" />
      <path d="M21 44H29" class="pin" />
      <path d="M21 55H29" class="pin" />
      <path d="M59 33H67" class="pin" />
      <path d="M59 44H67" class="pin" />
      <path d="M59 55H67" class="pin" />
      <circle cx="44" cy="44" r="4.5" class="nucleus" />
    </svg>
  </div>
</template>

<script setup>
defineProps({
  compact: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.plc-brand-mark {
  position: relative;
  width: 100%;
  height: 100%;
}

.brand-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 18px 28px rgba(14, 165, 233, 0.18));
}

.halo {
  fill: rgba(8, 47, 73, 0.52);
}

.orbit {
  fill: none;
  stroke: rgba(103, 232, 249, 0.18);
  stroke-width: 1.4;
  stroke-dasharray: 7 8;
  transform-origin: center;
}

.orbit-a {
  animation: plc-spin 16s linear infinite;
}

.orbit-b {
  animation: plc-spin-reverse 18s linear infinite;
}

.shell {
  stroke: rgba(148, 163, 184, 0.3);
  stroke-width: 1.2;
}

.core {
  animation: plc-breathe 3.6s ease-in-out infinite;
}

.trace,
.pin {
  stroke: rgba(241, 245, 249, 0.88);
  stroke-width: 2.4;
  stroke-linecap: round;
}

.pin {
  opacity: 0.72;
}

.pulse {
  animation: plc-pulse 2.8s ease-in-out infinite;
}

.nucleus {
  fill: rgba(255, 255, 255, 0.96);
  animation: plc-breathe 3.2s ease-in-out infinite;
}

.compact .brand-svg {
  filter: drop-shadow(0 10px 18px rgba(14, 165, 233, 0.14));
}

@keyframes plc-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes plc-spin-reverse {
  from {
    transform: rotate(360deg);
  }
  to {
    transform: rotate(0deg);
  }
}

@keyframes plc-breathe {
  0%,
  100% {
    opacity: 0.88;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.04);
  }
}

@keyframes plc-pulse {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}
</style>
