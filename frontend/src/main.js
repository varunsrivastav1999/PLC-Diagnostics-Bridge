import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './style.css'

import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'

import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Card from 'primevue/card'
import Toast from 'primevue/toast'
import Checkbox from 'primevue/checkbox'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            cssLayer: {
                name: 'primevue',
                order: 'tailwind-base, primevue, tailwind-utilities'
            }
        }
    }
})
app.use(ToastService)

// Directives
app.directive('tooltip', Tooltip)

// Global Components
app.component('Button', Button)
app.component('InputText', InputText)
app.component('Dropdown', Dropdown)
app.component('Card', Card)
app.component('Toast', Toast)
app.component('Checkbox', Checkbox)

app.mount('#app')
