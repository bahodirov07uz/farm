import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { drugService } from '../services/drugService'
import { Pill, Plus, Edit, Trash2, Package } from 'lucide-react'

export default function Drugs() {
  const { user } = useAuth()
  const [drugs, setDrugs] = useState([])
  const [variants, setVariants] = useState({})
  const [loading, setLoading] = useState(true)
  const [showDrugModal, setShowDrugModal] = useState(false)
  const [showVariantModal, setShowVariantModal] = useState(false)
  const [selectedDrug, setSelectedDrug] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [drugForm, setDrugForm] = useState({
    name: '',
    code: '',
    description: '',
    price: 0,
    images: [],
    is_active: true,
  })
  const [variantForm, setVariantForm] = useState({
    drug_id: null,
    name: '',
    sku: '',
    price: 0,
    is_active: true,
  })

  const isOperator = user?.role === 'superadmin' || user?.role === 'operator' || user?.role === 'branch_admin'

  useEffect(() => {
    loadDrugs()
  }, [])

  const loadDrugs = async () => {
    try {
      // Always use getAll() to get all drugs from backend
      const data = await drugService.getAll()
      if (data && Array.isArray(data)) {
        setDrugs(data)
        // Load variants for each drug
        for (const drug of data) {
          try {
            const variantData = await drugService.getVariants(drug.id)
            if (variantData && Array.isArray(variantData)) {
              setVariants((prev) => ({ ...prev, [drug.id]: variantData }))
            }
          } catch (error) {
            console.error(`Variants yuklashda xatolik (drug ${drug.id}):`, error)
            // Set empty array if variants fail to load
            setVariants((prev) => ({ ...prev, [drug.id]: [] }))
          }
        }
      } else {
        setDrugs([])
      }
    } catch (error) {
      console.error('Drugs yuklashda xatolik:', error)
      setDrugs([])
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadDrugs()
      return
    }
    try {
      const data = await drugService.search(searchQuery)
      if (Array.isArray(data)) {
        setDrugs(data)
        // Load variants for search results
        for (const drug of data) {
          try {
            const variantData = await drugService.getVariants(drug.id)
            setVariants((prev) => ({ ...prev, [drug.id]: variantData || [] }))
          } catch (error) {
            console.error(`Variants yuklashda xatolik:`, error)
            setVariants((prev) => ({ ...prev, [drug.id]: [] }))
          }
        }
      } else {
        setDrugs([])
      }
    } catch (error) {
      console.error('Qidiruvda xatolik:', error)
      setDrugs([])
    }
  }

  const handleCreateDrug = async (e) => {
    e.preventDefault()
    try {
      await drugService.create(drugForm)
      setShowDrugModal(false)
      setDrugForm({ name: '', code: '', description: '', price: 0, images: [], is_active: true })
      loadDrugs()
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const handleCreateVariant = async (e) => {
    e.preventDefault()
    try {
      await drugService.createVariant(variantForm)
      setShowVariantModal(false)
      setVariantForm({ drug_id: null, name: '', sku: '', price: 0, is_active: true })
      loadDrugs()
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const handleDeleteVariant = async (variantId) => {
    if (!confirm('Variantni o\'chirishni tasdiqlaysizmi?')) return
    try {
      await drugService.deleteVariant(variantId)
      loadDrugs()
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
        <h1 className="text-3xl font-bold text-gray-900">Dorilar</h1>
        <div className="flex gap-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Qidirish..."
              className="input w-64"
            />
            <button onClick={handleSearch} className="btn btn-secondary">
              Qidirish
            </button>
          </div>
          {isOperator && (
            <button
              onClick={() => {
                setDrugForm({ name: '', code: '', description: '', price: 0, images: [], is_active: true })
                setShowDrugModal(true)
              }}
              className="btn btn-primary flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Dori qo'shish
            </button>
          )}
        </div>
      </div>

      {drugs.length === 0 ? (
        <div className="card text-center py-12">
          <Pill className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Hozircha dorilar mavjud emas</p>
        </div>
      ) : (
        <div className="space-y-6">
          {drugs.map((drug) => (
            <div key={drug.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold">{drug.name}</h3>
                    <span className="text-sm text-gray-500">({drug.code})</span>
                    {drug.is_active ? (
                      <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">Faol</span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">Nofaol</span>
                    )}
                  </div>
                  {drug.description && (
                    <p className="text-gray-600 text-sm mb-2">{drug.description}</p>
                  )}
                  <p className="text-lg font-medium text-primary-600">
                    Asosiy narx: {drug.price} so'm
                  </p>
                  {drug.images && drug.images.length > 0 && (
                    <div className="flex gap-2 mt-2">
                      {drug.images.map((img, idx) => (
                        <img
                          key={idx}
                          src={img}
                          alt={`${drug.name} ${idx + 1}`}
                          className="w-16 h-16 object-cover rounded border"
                        />
                      ))}
                    </div>
                  )}
                </div>
                {isOperator && (
                  <button
                    onClick={() => {
                      setSelectedDrug(drug)
                      setVariantForm({ drug_id: drug.id, name: '', sku: '', price: drug.price, is_active: true })
                      setShowVariantModal(true)
                    }}
                    className="btn btn-secondary flex items-center text-sm"
                  >
                    <Package className="w-4 h-4 mr-1" />
                    Variant qo'shish
                  </button>
                )}
              </div>

              {/* Variants */}
              {variants[drug.id] && variants[drug.id].length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <h4 className="font-medium text-gray-700 mb-2">Variantlar:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {variants[drug.id].map((variant) => (
                      <div
                        key={variant.id}
                        className="p-3 bg-gray-50 rounded-lg flex items-center justify-between"
                      >
                        <div>
                          <p className="font-medium">{variant.name}</p>
                          <p className="text-sm text-gray-600">SKU: {variant.sku}</p>
                          <p className="text-sm font-medium text-primary-600">
                            {variant.price} so'm
                          </p>
                        </div>
                        {isOperator && (
                          <button
                            onClick={() => handleDeleteVariant(variant.id)}
                            className="p-1 text-red-600 hover:bg-red-50 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create Drug Modal */}
      {showDrugModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Yangi dori</h2>
            <form onSubmit={handleCreateDrug} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dori nomi *
                </label>
                <input
                  type="text"
                  value={drugForm.name}
                  onChange={(e) => setDrugForm({ ...drugForm, name: e.target.value })}
                  required
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Kod *
                </label>
                <input
                  type="text"
                  value={drugForm.code}
                  onChange={(e) => setDrugForm({ ...drugForm, code: e.target.value })}
                  required
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tavsif
                </label>
                <textarea
                  value={drugForm.description}
                  onChange={(e) => setDrugForm({ ...drugForm, description: e.target.value })}
                  className="input"
                  rows="3"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Narx (so'm) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={drugForm.price}
                  onChange={(e) => setDrugForm({ ...drugForm, price: parseFloat(e.target.value) })}
                  required
                  min="0"
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rasm URLlari (har birini yangi qatorda)
                </label>
                <textarea
                  value={drugForm.images.join('\n')}
                  onChange={(e) =>
                    setDrugForm({
                      ...drugForm,
                      images: e.target.value.split('\n').filter((url) => url.trim()),
                    })
                  }
                  className="input"
                  rows="3"
                  placeholder="https://example.com/image1.jpg&#10;https://example.com/image2.jpg"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={drugForm.is_active}
                  onChange={(e) => setDrugForm({ ...drugForm, is_active: e.target.checked })}
                  className="w-4 h-4 text-primary-600 rounded"
                />
                <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                  Faol
                </label>
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary flex-1">
                  Yaratish
                </button>
                <button
                  type="button"
                  onClick={() => setShowDrugModal(false)}
                  className="btn btn-secondary"
                >
                  Bekor qilish
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Variant Modal */}
      {showVariantModal && selectedDrug && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {selectedDrug.name} uchun variant
            </h2>
            <form onSubmit={handleCreateVariant} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Variant nomi * (masalan: "5 tablet", "10 tablet")
                </label>
                <input
                  type="text"
                  value={variantForm.name}
                  onChange={(e) => setVariantForm({ ...variantForm, name: e.target.value })}
                  required
                  className="input"
                  placeholder="5 tablet"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  SKU (Stock Keeping Unit) *
                </label>
                <input
                  type="text"
                  value={variantForm.sku}
                  onChange={(e) => setVariantForm({ ...variantForm, sku: e.target.value })}
                  required
                  className="input"
                  placeholder="PAR-5T"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Narx (so'm) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={variantForm.price}
                  onChange={(e) =>
                    setVariantForm({ ...variantForm, price: parseFloat(e.target.value) })
                  }
                  required
                  min="0"
                  className="input"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="variant_active"
                  checked={variantForm.is_active}
                  onChange={(e) =>
                    setVariantForm({ ...variantForm, is_active: e.target.checked })
                  }
                  className="w-4 h-4 text-primary-600 rounded"
                />
                <label htmlFor="variant_active" className="ml-2 text-sm text-gray-700">
                  Faol
                </label>
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary flex-1">
                  Yaratish
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowVariantModal(false)
                    setSelectedDrug(null)
                  }}
                  className="btn btn-secondary"
                >
                  Bekor qilish
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

