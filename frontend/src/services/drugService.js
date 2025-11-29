import api from './api'

export const drugService = {
  // Get all drugs
  getAll: async () => {
    const response = await api.get('/drugs/all')
    return response.data
  },

  // Get drugs with filters
  getList: async (params = {}) => {
    const response = await api.get('/drugs', { params })
    return response.data
  },

  // Search drugs
  search: async (query) => {
    const response = await api.get('/drugs/search', { params: { query } })
    return response.data
  },

  // Create drug
  create: async (data) => {
    const response = await api.post('/drugs', data)
    return response.data
  },

  // Drug Variants
  createVariant: async (data) => {
    const response = await api.post('/drugs/variants', data)
    return response.data
  },

  getVariants: async (drugId) => {
    const response = await api.get(`/drugs/variants/${drugId}`)
    return response.data
  },

  updateVariant: async (variantId, data) => {
    const response = await api.patch(`/drugs/variants/${variantId}`, data)
    return response.data
  },

  deleteVariant: async (variantId) => {
    await api.delete(`/drugs/variants/${variantId}`)
  },
}

