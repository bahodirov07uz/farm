import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { inventoryService } from '../services/inventoryService'
import { branchService } from '../services/branchService'
import { drugService } from '../services/drugService'
import { orderService } from '../services/orderService'
import { Package, Plus, Edit, TrendingUp, QrCode, Search } from 'lucide-react'

export default function Inventory() {
  const { user } = useAuth()
  const [inventories, setInventories] = useState([])
  const [branches, setBranches] = useState([])
  const [drugs, setDrugs] = useState([])
  const [variants, setVariants] = useState({})
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showTotalModal, setShowTotalModal] = useState(false)
  const [selectedDrug, setSelectedDrug] = useState(null)
  const [totalData, setTotalData] = useState(null)
  const [barcode, setBarcode] = useState('')
  const [selectedBranch, setSelectedBranch] = useState(null)
  const [formData, setFormData] = useState({
    branch_id: null,
    drug_id: null,
    drug_variant_id: null,
    quantity: 0,
    reorder_level: 0,
  })

  const isPharmacyAdmin = user?.role === 'pharmacy_admin'
  const isBranchAdmin = user?.role === 'branch_admin'
  const isCashier = user?.role === 'cashier'

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [branchesData, drugsData] = await Promise.all([
        isPharmacyAdmin
          ? branchService.getByPharmacy(user?.pharmacy_id)
          : user?.branch_id
          ? Promise.resolve([{ id: user.branch_id }])
          : Promise.resolve([]),
        drugService.getAll(),
      ])
      setBranches(branchesData || [])
      setDrugs(drugsData || [])

      // Set default branch
      if (user?.branch_id) {
        setSelectedBranch(user.branch_id)
        loadInventory(user.branch_id)
      } else if (branchesData && branchesData.length > 0) {
        setSelectedBranch(branchesData[0].id)
        loadInventory(branchesData[0].id)
      }

      // Load variants
      if (drugsData && drugsData.length > 0) {
        for (const drug of drugsData) {
          try {
            const variantData = await drugService.getVariants(drug.id)
            setVariants((prev) => ({ ...prev, [drug.id]: variantData || [] }))
          } catch (error) {
            console.error(`Variants yuklashda xatolik:`, error)
            setVariants((prev) => ({ ...prev, [drug.id]: [] }))
          }
        }
      }
    } catch (error) {
      console.error('Data yuklashda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadInventory = async (branchId) => {
    try {
      const data = await inventoryService.getByBranch(branchId)
      setInventories(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Inventory yuklashda xatolik:', error)
      setInventories([])
    }
  }

  const handleScanBarcode = async () => {
    if (!barcode.trim()) {
      alert('Barkodni kiriting')
      return
    }

    try {
      const result = await orderService.scan(barcode)
      alert('Buyurtma tasdiqlandi va ombordagi miqdor kamaytirildi!')
      setBarcode('')
      if (selectedBranch) {
        loadInventory(selectedBranch)
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const handleGetTotal = async (drugId, variantId = null) => {
    if (!user?.pharmacy_id) return
    try {
      const data = await inventoryService.getTotalForPharmacy(
        user.pharmacy_id,
        drugId,
        variantId
      )
      setTotalData(data)
      setShowTotalModal(true)
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await inventoryService.add(formData)
      setShowModal(false)
      setFormData({
        branch_id: selectedBranch || null,
        drug_id: null,
        drug_variant_id: null,
        quantity: 0,
        reorder_level: 0,
      })
      alert('Ombor qo\'shildi!')
      if (formData.branch_id) {
        loadInventory(formData.branch_id)
      }
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  if (loading) {
    return <div className="text-center py-8">Yuklanmoqda...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Ombor</h1>
        {isPharmacyAdmin && (
          <button
            onClick={() => {
              setFormData({
                branch_id: selectedBranch || branches[0]?.id || null,
                drug_id: null,
                drug_variant_id: null,
                quantity: 0,
                reorder_level: 0,
              })
              setShowModal(true)
            }}
            className="btn btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Ombor qo'shish
          </button>
        )}
      </div>

      {isPharmacyAdmin && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold mb-4">Aptekangizdagi umumiy miqdorlar</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {drugs.slice(0, 6).map((drug) => (
              <div
                key={drug.id}
                className="p-4 bg-gray-50 rounded-lg flex items-center justify-between"
              >
                <div>
                  <p className="font-medium">{drug.name}</p>
                  <p className="text-sm text-gray-600">{drug.code}</p>
                </div>
                <button
                  onClick={() => handleGetTotal(drug.id)}
                  className="btn btn-secondary text-sm flex items-center"
                >
                  <TrendingUp className="w-4 h-4 mr-1" />
                  Umumiy
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Barcode Scanner */}
      {(isBranchAdmin || isCashier) && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold mb-4">Barkod orqali buyurtma tasdiqlash</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleScanBarcode()}
              placeholder="Barkodni kiriting yoki skaner qiling"
              className="input flex-1"
            />
            <button onClick={handleScanBarcode} className="btn btn-primary flex items-center">
              <Search className="w-4 h-4 mr-2" />
              Tasdiqlash
            </button>
          </div>
        </div>
      )}

      {/* Branch Selector */}
      {isPharmacyAdmin && branches.length > 1 && (
        <div className="card mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filialni tanlang
          </label>
          <select
            value={selectedBranch || ''}
            onChange={(e) => {
              const branchId = parseInt(e.target.value)
              setSelectedBranch(branchId)
              loadInventory(branchId)
            }}
            className="input"
          >
            <option value="">Tanlang</option>
            {branches.map((branch) => (
              <option key={branch.id} value={branch.id}>
                {branch.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Inventory List */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Ombor ro'yxati</h2>
        {inventories.length === 0 ? (
          <p className="text-gray-600 text-center py-8">
            Hozircha ombor ma'lumotlari mavjud emas
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Dori</th>
                  <th>Variant</th>
                  <th>Miqdor</th>
                  <th>Qayta buyurtma darajasi</th>
                  <th>Filial</th>
                  <th>Amallar</th>
                </tr>
              </thead>
              <tbody>
                {inventories.map((inv) => (
                  <tr key={inv.id}>
                    <td>{inv.id}</td>
                    <td className="font-medium">
                      {inv.drug?.name || drugs.find(d => d.id === inv.drug_id)?.name || `Dori ID: ${inv.drug_id}`}
                    </td>
                    <td>
                      {inv.drug_variant?.name || (inv.drug_variant_id ? variants[inv.drug_id]?.find(v => v.id === inv.drug_variant_id)?.name : '-')}
                    </td>
                    <td>
                      <span className={inv.quantity <= inv.reorder_level ? 'text-red-600 font-bold' : ''}>
                        {inv.quantity}
                      </span>
                    </td>
                    <td>{inv.reorder_level}</td>
                    <td>{inv.branch?.name || `Filial ID: ${inv.branch_id}`}</td>
                    <td>
                      {(isBranchAdmin || isPharmacyAdmin) && (
                        <button
                          onClick={() => {
                            const newQty = prompt('Yangi miqdorni kiriting:', inv.quantity)
                            if (newQty !== null) {
                              inventoryService.update(inv.id, { quantity: parseInt(newQty) })
                                .then(() => {
                                  alert('Miqdor yangilandi!')
                                  if (selectedBranch) {
                                    loadInventory(selectedBranch)
                                  }
                                })
                                .catch((error) => {
                                  alert(error.response?.data?.detail || 'Xatolik yuz berdi')
                                })
                            }
                          }}
                          className="btn btn-secondary text-sm"
                        >
                          <Edit className="w-4 h-4 mr-1" />
                          Tahrirlash
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Inventory Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Ombor qo'shish</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filial *
                </label>
                <select
                  value={formData.branch_id || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, branch_id: parseInt(e.target.value) })
                  }
                  required
                  className="input"
                >
                  <option value="">Tanlang</option>
                  {branches.map((branch) => (
                    <option key={branch.id} value={branch.id}>
                      {branch.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dori *
                </label>
                <select
                  value={formData.drug_id || ''}
                  onChange={(e) => {
                    const drugId = parseInt(e.target.value)
                    setFormData({
                      ...formData,
                      drug_id: drugId,
                      drug_variant_id: null,
                    })
                    setSelectedDrug(drugs.find((d) => d.id === drugId))
                  }}
                  required
                  className="input"
                >
                  <option value="">Tanlang</option>
                  {drugs.map((drug) => (
                    <option key={drug.id} value={drug.id}>
                      {drug.name} ({drug.code})
                    </option>
                  ))}
                </select>
              </div>
              {selectedDrug && variants[selectedDrug.id] && variants[selectedDrug.id].length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Variant (ixtiyoriy)
                  </label>
                  <select
                    value={formData.drug_variant_id || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        drug_variant_id: e.target.value ? parseInt(e.target.value) : null,
                      })
                    }
                    className="input"
                  >
                    <option value="">Variant tanlamaslik</option>
                    {variants[selectedDrug.id].map((variant) => (
                      <option key={variant.id} value={variant.id}>
                        {variant.name} - {variant.price} so'm
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Miqdor *
                </label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) =>
                    setFormData({ ...formData, quantity: parseInt(e.target.value) })
                  }
                  required
                  min="0"
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Qayta buyurtma darajasi
                </label>
                <input
                  type="number"
                  value={formData.reorder_level}
                  onChange={(e) =>
                    setFormData({ ...formData, reorder_level: parseInt(e.target.value) })
                  }
                  min="0"
                  className="input"
                />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary flex-1">
                  Qo'shish
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn btn-secondary"
                >
                  Bekor qilish
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Total Quantity Modal */}
      {showTotalModal && totalData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Umumiy miqdor</h2>
            <div className="space-y-2">
              <p>
                <span className="font-medium">Apteka ID:</span> {totalData.pharmacy_id}
              </p>
              <p>
                <span className="font-medium">Dori ID:</span> {totalData.drug_id}
              </p>
              {totalData.drug_variant_id && (
                <p>
                  <span className="font-medium">Variant ID:</span> {totalData.drug_variant_id}
                </p>
              )}
              <p className="text-2xl font-bold text-primary-600 mt-4">
                Umumiy miqdor: {totalData.total_quantity} ta
              </p>
            </div>
            <button
              onClick={() => {
                setShowTotalModal(false)
                setTotalData(null)
              }}
              className="btn btn-primary w-full mt-4"
            >
              Yopish
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

