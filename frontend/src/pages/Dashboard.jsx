import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { pharmacyService } from '../services/pharmacyService'
import { branchService } from '../services/branchService'
import { drugService } from '../services/drugService'
import { orderService } from '../services/orderService'
import { Building2, MapPin, Pill, ShoppingCart, Search, Plus, QrCode } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    pharmacies: 0,
    branches: 0,
    drugs: 0,
    orders: 0,
  })
  const [loading, setLoading] = useState(true)
  
  // For regular users
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [showOrderModal, setShowOrderModal] = useState(false)
  const [showBarcodeModal, setShowBarcodeModal] = useState(false)
  const [orderBarcode, setOrderBarcode] = useState('')
  const [orderItems, setOrderItems] = useState([])
  const [currentItem, setCurrentItem] = useState({
    drug_id: null,
    drug_variant_id: null,
    quantity: 1,
  })
  const [drugs, setDrugs] = useState([])
  const [variants, setVariants] = useState({})
  const [branches, setBranches] = useState([])
  const [selectedDrugBranches, setSelectedDrugBranches] = useState([])
  const [showDrugBranchesModal, setShowDrugBranchesModal] = useState(false)

  const isRegularUser = user?.role === 'user'

  useEffect(() => {
    if (isRegularUser) {
      loadUserData()
    } else {
      loadStats()
    }
  }, [isRegularUser])

  const loadUserData = async () => {
    try {
      const [drugsData, branchesData] = await Promise.all([
        drugService.getAll().catch(() => []),
        user?.pharmacy_id 
          ? branchService.getByPharmacy(user.pharmacy_id).catch(() => [])
          : Promise.resolve([]),
      ])
      setDrugs(drugsData || [])
      setBranches(branchesData || [])

      // Load variants for all drugs
      if (drugsData && drugsData.length > 0) {
        for (const drug of drugsData) {
          try {
            const variantData = await drugService.getVariants(drug.id)
            setVariants((prev) => ({ ...prev, [drug.id]: variantData || [] }))
          } catch (error) {
            console.error(`Variants yuklashda xatolik (drug ${drug.id}):`, error)
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

  const loadStats = async () => {
    try {
      const [pharmacies, branches, drugs, orders] = await Promise.all([
        user?.role === 'superadmin' || user?.role === 'operator'
          ? pharmacyService.getAll().catch(() => [])
          : Promise.resolve([]),
        user?.role === 'superadmin' || user?.role === 'operator'
          ? branchService.getAll().catch(() => [])
          : branchService.getByPharmacy(user?.pharmacy_id).catch(() => []),
        drugService.getAll().catch(() => []),
        user?.role === 'superadmin' || user?.role === 'operator'
          ? orderService.getAll({ limit: 1 }).catch(() => [])
          : Promise.resolve([]),
      ])

      setStats({
        pharmacies: pharmacies.length || 0,
        branches: branches.length || 0,
        drugs: drugs.length || 0,
        orders: orders.length || 0,
      })
    } catch (error) {
      console.error('Stats yuklashda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([])
      return
    }
    try {
      const data = await drugService.search(searchQuery)
      setSearchResults(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Qidiruvda xatolik:', error)
      setSearchResults([])
    }
  }

  const handleAddItem = () => {
    const drug = drugs.find((d) => d.id === currentItem.drug_id)
    if (!drug) return

    const variant = currentItem.drug_variant_id
      ? variants[currentItem.drug_id]?.find((v) => v.id === currentItem.drug_variant_id)
      : null

    const item = {
      drug_id: currentItem.drug_id,
      drug_variant_id: currentItem.drug_variant_id || null,
      quantity: currentItem.quantity,
      drug_name: drug.name,
      variant_name: variant?.name || null,
      price: variant?.price || drug.price,
    }

    setOrderItems([...orderItems, item])
    setCurrentItem({ drug_id: null, drug_variant_id: null, quantity: 1 })
  }

  const handleRemoveItem = (index) => {
    setOrderItems(orderItems.filter((_, i) => i !== index))
  }

  const handleCreateOrder = async (e) => {
    e.preventDefault()
    if (orderItems.length === 0) {
      alert('Kamida bitta mahsulot qo\'shing')
      return
    }

    try {
      const orderData = {
        branch_id: user?.branch_id || branches[0]?.id,
        items: orderItems.map((item) => ({
          drug_id: item.drug_id,
          drug_variant_id: item.drug_variant_id,
          qty: item.quantity,
        })),
      }

      const result = await orderService.create(orderData)
      setOrderBarcode(result.barcode)
      setShowOrderModal(false)
      setShowBarcodeModal(true)
      setOrderItems([])
      alert('Buyurtma yaratildi!')
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const statCards = [
    {
      title: 'Aptekalar',
      value: stats.pharmacies,
      icon: Building2,
      color: 'bg-blue-500',
    },
    {
      title: 'Filiallar',
      value: stats.branches,
      icon: MapPin,
      color: 'bg-green-500',
    },
    {
      title: 'Dorilar',
      value: stats.drugs,
      icon: Pill,
      color: 'bg-purple-500',
    },
    {
      title: 'Buyurtmalar',
      value: stats.orders,
      icon: ShoppingCart,
      color: 'bg-orange-500',
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Yuklanmoqda...</div>
      </div>
    )
  }

  // Regular user dashboard
  if (isRegularUser) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Bosh sahifa</h1>

        {/* Drug Search */}
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Dori qidirish</h2>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Dori nomi yoki kodini kiriting..."
              className="input flex-1"
            />
            <button onClick={handleSearch} className="btn btn-primary flex items-center">
              <Search className="w-4 h-4 mr-2" />
              Qidirish
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="space-y-2">
              {searchResults.map((drug) => (
                <div key={drug.id} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-medium">{drug.name}</p>
                      <p className="text-sm text-gray-600">{drug.code}</p>
                      {drug.description && (
                        <p className="text-sm text-gray-500 mt-1">{drug.description}</p>
                      )}
                      <p className="text-sm font-medium text-primary-600 mt-1">
                        {drug.price} so'm
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          const data = await inventoryService.getBranchesWithDrug(drug.id, {
                            pharmacyId: user?.pharmacy_id || null,
                            minQuantity: 1,
                          })
                          setSelectedDrugBranches(data || [])
                          setShowDrugBranchesModal(true)
                        } catch (error) {
                          console.error('Filiallar bo\'yicha mavjudlikni yuklashda xatolik:', error)
                          setSelectedDrugBranches([])
                          setShowDrugBranchesModal(true)
                        }
                      }}
                      className="btn btn-secondary text-sm"
                    >
                      Mavjud filiallar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Create Order */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Buyurtma yaratish</h2>
            <button
              onClick={() => {
                setOrderItems([])
                setCurrentItem({ drug_id: null, drug_variant_id: null, quantity: 1 })
                setShowOrderModal(true)
              }}
              className="btn btn-primary flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Yangi buyurtma
            </button>
          </div>
        </div>

        {/* Create Order Modal */}
        {showOrderModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="card w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <h2 className="text-xl font-bold mb-4">Yangi buyurtma</h2>
              <form onSubmit={handleCreateOrder} className="space-y-4">
                <div className="border-b pb-4">
                  <h3 className="font-medium mb-3">Mahsulot qo'shish</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <select
                      value={currentItem.drug_id || ''}
                      onChange={(e) => {
                        const drugId = parseInt(e.target.value)
                        setCurrentItem({
                          drug_id: drugId,
                          drug_variant_id: null,
                          quantity: 1,
                        })
                      }}
                      className="input"
                    >
                      <option value="">Dori tanlang</option>
                      {drugs.map((drug) => (
                        <option key={drug.id} value={drug.id}>
                          {drug.name}
                        </option>
                      ))}
                    </select>

                    {currentItem.drug_id && variants[currentItem.drug_id]?.length > 0 && (
                      <select
                        value={currentItem.drug_variant_id || ''}
                        onChange={(e) =>
                          setCurrentItem({
                            ...currentItem,
                            drug_variant_id: e.target.value ? parseInt(e.target.value) : null,
                          })
                        }
                        className="input"
                      >
                        <option value="">Variant tanlamaslik</option>
                        {variants[currentItem.drug_id].map((variant) => (
                          <option key={variant.id} value={variant.id}>
                            {variant.name}
                          </option>
                        ))}
                      </select>
                    )}

                    <div className="flex gap-2">
                      <input
                        type="number"
                        value={currentItem.quantity}
                        onChange={(e) =>
                          setCurrentItem({ ...currentItem, quantity: parseInt(e.target.value) || 1 })
                        }
                        min="1"
                        className="input"
                        placeholder="Miqdor"
                      />
                      <button
                        type="button"
                        onClick={handleAddItem}
                        className="btn btn-secondary"
                      >
                        Qo'shish
                      </button>
                    </div>

        {/* Drug availability by branches modal */}
        {showDrugBranchesModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="card w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-bold mb-4">Filiallar bo'yicha mavjudlik</h2>
              {selectedDrugBranches.length === 0 ? (
                <p className="text-gray-600">Bu doridan hozircha zaxirada yo'q.</p>
              ) : (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Filial</th>
                      <th>Variant</th>
                      <th>Miqdor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedDrugBranches.map((inv) => (
                      <tr key={inv.id}>
                        <td>{inv.branch?.name || `Filial ID: ${inv.branch_id}`}</td>
                        <td>{inv.drug_variant?.name || '-'}</td>
                        <td>{inv.quantity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              <button
                type="button"
                onClick={() => {
                  setShowDrugBranchesModal(false)
                  setSelectedDrugBranches([])
                }}
                className="btn btn-primary w-full mt-4"
              >
                Yopish
              </button>
            </div>
          </div>
        )}
                  </div>
                </div>

                {orderItems.length > 0 && (
                  <div>
                    <h3 className="font-medium mb-2">Buyurtma mahsulotlari:</h3>
                    <div className="space-y-2">
                      {orderItems.map((item, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <div>
                            <p className="font-medium">{item.drug_name}</p>
                            {item.variant_name && (
                              <p className="text-sm text-gray-600">Variant: {item.variant_name}</p>
                            )}
                            <p className="text-sm text-gray-600">
                              {item.quantity} x {item.price} = {item.quantity * item.price} so'm
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleRemoveItem(index)}
                            className="text-red-600 hover:text-red-700"
                          >
                            O'chirish
                          </button>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-lg font-bold">
                        Jami: {orderItems.reduce((sum, item) => sum + item.price * item.quantity, 0)} so'm
                      </p>
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={orderItems.length === 0}
                    className="btn btn-primary flex-1"
                  >
                    Buyurtma yaratish
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowOrderModal(false)
                      setOrderItems([])
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

        {/* Barcode Modal */}
        {showBarcodeModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="card w-full max-w-md text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                <QrCode className="w-8 h-8 text-primary-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Buyurtma yaratildi!</h2>
              <p className="text-gray-600 mb-4">Buyurtma barkodi:</p>
              <div className="bg-gray-100 p-4 rounded-lg mb-4">
                <p className="text-2xl font-mono font-bold text-primary-600">{orderBarcode}</p>
              </div>
              <p className="text-sm text-gray-500 mb-4">
                Bu barkodni kassirga ko'rsating yoki skaner qiling
              </p>
              <button
                onClick={() => {
                  setShowBarcodeModal(false)
                  setOrderBarcode('')
                }}
                className="btn btn-primary w-full"
              >
                Yopish
              </button>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Admin/Operator dashboard
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Bosh sahifa</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.title} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Xush kelibsiz!</h2>
        <p className="text-gray-600">
          {user?.full_name || user?.email}, Med farmatsevtika tizimiga xush kelibsiz.
        </p>
        <p className="text-gray-600 mt-2">
          Sizning rolingiz: <span className="font-medium">{user?.role}</span>
        </p>
      </div>
    </div>
  )
}

