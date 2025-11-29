import api from './api'

export const inventoryService = {
  // Add inventory
  add: async (data) => {
    const response = await api.post('/drugs/inventory', data)
    return response.data
  },

  // Update inventory
  update: async (inventoryId, data) => {
    const response = await api.patch(`/drugs/inventory/${inventoryId}`, data)
    return response.data
  },

  // Get total quantity for pharmacy
  getTotalForPharmacy: async (pharmacyId, drugId, drugVariantId = null) => {
    const params = drugVariantId ? { drug_variant_id: drugVariantId } : {}
    const response = await api.get(
      `/inventory/pharmacy/${pharmacyId}/drug/${drugId}/total`,
      { params }
    )
    return response.data
  },

  // Get inventory by branch
  getByBranch: async (branchId) => {
    const response = await api.get(`/inventory/branch/${branchId}`)
    return response.data
  },

  // Get inventory by pharmacy
  getByPharmacy: async (pharmacyId) => {
    const response = await api.get(`/inventory/pharmacy/${pharmacyId}`)
    return response.data
  },

  // Get branches that have a specific drug
  getBranchesWithDrug: async (drugId, { pharmacyId = null, minQuantity = 1 } = {}) => {
    const params = {}
    if (pharmacyId) params.pharmacy_id = pharmacyId
    if (minQuantity != null) params.min_quantity = minQuantity
    const response = await api.get(`/inventory/drug/${drugId}/branches`, { params })
    return response.data
  },
}

