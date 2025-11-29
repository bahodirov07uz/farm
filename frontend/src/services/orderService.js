import api from './api'

export const orderService = {
  // Create order
  create: async (data) => {
    const response = await api.post('/orders/', data)
    return response.data
  },

  // Get order by ID
  getById: async (orderId) => {
    const response = await api.get(`/orders/${orderId}`)
    return response.data
  },

  // Get all orders (admin only)
  getAll: async (params = {}) => {
    const response = await api.get('/orders/', { params })
    return response.data
  },

  // Scan and confirm order
  scan: async (barcode) => {
    const response = await api.post(`/orders/scan/${barcode}`)
    return response.data
  },
}

