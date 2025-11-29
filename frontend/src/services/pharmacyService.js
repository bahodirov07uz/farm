import api from './api'

export const pharmacyService = {
  // Get all pharmacies (operator/superadmin only)
  getAll: async () => {
    const response = await api.get('/pharmacies')
    return response.data
  },

  // Create pharmacy request
  createRequest: async (data) => {
    const response = await api.post('/pharmacies/requests', data)
    return response.data
  },

  // Approve pharmacy request
  approveRequest: async (requestId) => {
    const response = await api.post(`/pharmacies/requests/${requestId}/approve`)
    return response.data
  },

  // Reject pharmacy request
  rejectRequest: async (requestId, reason) => {
    const response = await api.post(`/pharmacies/requests/${requestId}/reject`, { reason })
    return response.data
  },
}

