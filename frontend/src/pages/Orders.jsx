import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { orderService } from '../services/orderService'
import { drugService } from '../services/drugService'
import { branchService } from '../services/branchService'
import { ShoppingCart, Plus, Search, CheckCircle, QrCode } from 'lucide-react'

export default function Orders() {
  const { user } = useAuth()
  const [orders, setOrders] = useState([])
  const [drugs, setDrugs] = useState([])
  const [variants, setVariants] = useState({})
  const [branches, setBranches] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showBarcodeModal, setShowBarcodeModal] = useState(false)
  const [orderBarcode, setOrderBarcode] = useState('')
  const [barcode, setBarcode] = useState('')
  const [orderItems, setOrderItems] = useState([])
  const [currentItem, setCurrentItem] = useState({
    drug_id: null,
    drug_variant_id: null,
    quantity: 1,
  })

  const isCashier = user?.role === 'cashier'
  const isAdmin = user?.role === 'superadmin' || user?.role === 'operator'

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [drugsData, branchesData] = await Promise.all([
        drugService.getAll(),
        isAdmin ? branchService.getAll() : branchService.getByPharmacy(user?.pharmacy_id),
      ])
      setDrugs(drugsData)
      setBranches(branchesData)

      // Load variants
      for (const drug of drugsData) {
        try {
          const variantData = await drugService.getVariants(drug.id)
          setVariants((prev) => ({ ...prev, [drug.id]: variantData }))
        } catch (error) {
          console.error(`Variants yuklashda xatolik:`, error)
        }
      }

      if (isAdmin) {
        const ordersData = await orderService.getAll()
        setOrders(ordersData)
      }
    } catch (error) {
      console.error('Data yuklashda xatolik:', error)
    } finally {
      setLoading(false)
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
      setShowCreateModal(false)
      setShowBarcodeModal(true)
      setOrderItems([])
      loadData()
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
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
      loadData()
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
        <h1 className="text-3xl font-bold text-gray-900">Buyurtmalar</h1>
        {isCashier && (
          <button
            onClick={() => {
              setOrderItems([])
              setCurrentItem({ drug_id: null, drug_variant_id: null, quantity: 1 })
              setShowCreateModal(true)
            }}
            className="btn btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Buyurtma yaratish
          </button>
        )}
      </div>

      {/* Barcode Scanner */}
      {isCashier && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold mb-4">Barkod orqali tasdiqlash</h2>
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

      {orders.length === 0 && !isCashier ? (
        <div className="card text-center py-12">
          <ShoppingCart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Hozircha buyurtmalar mavjud emas</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Filial</th>
                <th>Status</th>
                <th>Mahsulotlar</th>
                <th>Jami</th>
                <th>Yaratilgan</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>{order.branch_id}</td>
                  <td>
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        order.status === 'confirmed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {order.status === 'confirmed' ? 'Tasdiqlangan' : 'Kutilmoqda'}
                    </span>
                  </td>
                  <td>
                    {order.items?.length || 0} ta mahsulot
                  </td>
                  <td className="font-medium">
                    {order.items?.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0) || 0} so'm
                  </td>
                  <td>{new Date(order.created_at).toLocaleString('uz-UZ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Order Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Yangi buyurtma</h2>
            <form onSubmit={handleCreateOrder} className="space-y-4">
              {/* Add Item Section */}
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
                </div>
              </div>

              {/* Order Items List */}
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
                    setShowCreateModal(false)
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

