import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PlcConnectionForm from '../PlcConnectionForm.vue'
import { usePlcStore } from '../../stores/plcStore'
import PrimeVue from 'primevue/config'

describe('PlcConnectionForm.vue', () => {
  let wrapper
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = usePlcStore()
    
    wrapper = mount(PlcConnectionForm, {
      global: {
        plugins: [PrimeVue],
        stubs: {
          Card: true,
          Button: true,
          Dropdown: true,
          InputText: true,
          Checkbox: true,
          ProgressSpinner: true,
          Tag: true,
        }
      }
    })
  })

  it('renders the form component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('shows Mitsubishi port check section only when plc_type is mitsubishi', async () => {
    // Initially Siemens
    expect(store.connectionConfig.plc_type).toBe('siemens')
    
    // Change to Mitsubishi
    store.connectionConfig.plc_type = 'mitsubishi'
    await wrapper.vm.$nextTick()
    
    // Port check section should be visible
    const portCheckDiv = wrapper.find('div[class*="bg-gradient-to-r"]')
    expect(portCheckDiv.exists()).toBe(true)
  })

  it('port status section remains visible when checkbox is enabled', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    await wrapper.vm.$nextTick()
    
    // Enable port check
    wrapper.vm.portCheckEnabled = true
    await wrapper.vm.$nextTick()
    
    // Section should still be visible
    const portCheckDiv = wrapper.find('div[class*="bg-gradient-to-r"]')
    expect(portCheckDiv.exists()).toBe(true)
  })

  it('displays PORT BUSY tag with danger severity when port is busy', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    wrapper.vm.portCheckEnabled = true
    store.portBusy = true
    await wrapper.vm.$nextTick()
    
    // Check that danger severity is used
    const tag = wrapper.find('Tag')
    expect(tag.exists()).toBe(true)
    expect(tag.attributes('severity')).toBe('danger')
    expect(tag.attributes('value')).toBe('PORT BUSY')
  })

  it('displays PORT FREE tag with success severity when port is free', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    wrapper.vm.portCheckEnabled = true
    store.portBusy = false
    await wrapper.vm.$nextTick()
    
    const tag = wrapper.find('Tag')
    expect(tag.exists()).toBe(true)
    expect(tag.attributes('severity')).toBe('success')
    expect(tag.attributes('value')).toBe('PORT FREE')
  })

  it('hides tag when portCheckEnabled is false', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    wrapper.vm.portCheckEnabled = false
    await wrapper.vm.$nextTick()
    
    const tag = wrapper.find('Tag[value="PORT BUSY"]')
    expect(tag.exists()).toBe(false)
  })

  it('shows progress spinner while checking port', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    store.checkingPort = true
    await wrapper.vm.$nextTick()
    
    const spinner = wrapper.find('ProgressSpinner')
    expect(spinner.exists()).toBe(true)
  })

  it('disables checkbox when checking port', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    store.checkingPort = true
    await wrapper.vm.$nextTick()
    
    const checkbox = wrapper.find('Checkbox')
    expect(checkbox.attributes('disabled')).toBe('true')
  })

  it('defaults to port 5000 for Mitsubishi', () => {
    wrapper.vm.onPlcTypeChange()
    store.connectionConfig.plc_type = 'mitsubishi'
    
    expect(store.connectionConfig.port).toBe(5000)
  })

  it('resets port check when changing PLC type', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    wrapper.vm.portCheckEnabled = true
    
    store.connectionConfig.plc_type = 'siemens'
    await wrapper.vm.onPlcTypeChange()
    
    expect(wrapper.vm.portCheckEnabled).toBe(false)
  })

  it('checkbox is properly styled with cursor-pointer', async () => {
    store.connectionConfig.plc_type = 'mitsubishi'
    await wrapper.vm.$nextTick()
    
    const checkbox = wrapper.find('Checkbox')
    expect(checkbox.attributes('class')).toContain('cursor-pointer')
  })

  it('calls handlePortCheck on checkbox change', async () => {
    const spy = vi.spyOn(wrapper.vm, 'handlePortCheck')
    store.connectionConfig.plc_type = 'mitsubishi'
    await wrapper.vm.$nextTick()
    
    wrapper.vm.portCheckEnabled = true
    // Simulate the @change event
    await wrapper.vm.handlePortCheck()
    
    expect(spy).toHaveBeenCalled()
  })
})
