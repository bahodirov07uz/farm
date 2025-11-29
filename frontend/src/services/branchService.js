import api from './api'

export const branchService = {
  // Get all branches (operator/superadmin only)
  getAll: async () => {
    const response = await api.get('/branches/all')
    return response.data
  },

  // Get branches by pharmacy
  getByPharmacy: async (pharmacyId) => {
    const response = await api.get('/branches', { params: { pharmacy_id: pharmacyId } })
    return response.data
  },

  // Get nearby branches for any user
  getNearby: async (latitude, longitude, radiusKm = 10) => {
    const response = await api.get('/branches/nearby', {
      params: {
        latitude,
        longitude,
        radius_km: radiusKm,
      },
    })
    return response.data
  },

  // Create branch
  create: async (data) => {
    const response = await api.post('/branches', data)
    return response.data
  },

  // Update branch
  update: async (branchId, data) => {
    const response = await api.patch(`/branches/${branchId}`, data)
    return response.data
  },

  // Delete branch
  delete: async (branchId) => {
    await api.delete(`/branches/${branchId}`)
  },

  // Assign branch admin
  assignAdmin: async (branchId, userId) => {
    const response = await api.post(`/branches/${branchId}/assign-admin`, { user_id: userId })
    return response.data
  },
}

