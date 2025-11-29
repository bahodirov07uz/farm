import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { branchService } from '../services/branchService'
import { pharmacyService } from '../services/pharmacyService'
import { MapPin, Plus, Edit, Trash2 } from 'lucide-react'

export default function Branches() {
  const { user } = useAuth()
  const [branches, setBranches] = useState([])
  const [pharmacies, setPharmacies] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingBranch, setEditingBranch] = useState(null)
  const [formData, setFormData] = useState({ name: '', address: '', phone: '', pharmacy_id: null })

  const isAdmin = user?.role === 'superadmin' || user?.role === 'operator'
  const isPharmacyAdmin = user?.role === 'pharmacy_admin'

  useEffect(() => {
    loadBranches()
    if (isAdmin) {
      loadPharmacies()
    }
  }, [])

  const loadBranches = async () => {
    try {
      let data
      if (isAdmin) {
        data = await branchService.getAll()
      } else {
        data = await branchService.getByPharmacy(user?.pharmacy_id)
      }
      setBranches(data)
    } catch (error) {
      console.error('Branches yuklashda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadPharmacies = async () => {
    try {
      const data = await pharmacyService.getAll()
      setPharmacies(data)
    } catch (error) {
      console.error('Pharmacies yuklashda xatolik:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingBranch) {
        await branchService.update(editingBranch.id, formData)
      } else {
        await branchService.create(formData)
      }
      setShowModal(false)
      setEditingBranch(null)
      setFormData({ name: '', address: '', phone: '', pharmacy_id: null })
      loadBranches()
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const handleEdit = (branch) => {
    setEditingBranch(branch)
    setFormData({
      name: branch.name,
      address: branch.address || '',
      phone: branch.phone || '',
      pharmacy_id: branch.pharmacy_id,
    })
    setShowModal(true)
  }

  const handleDelete = async (branchId) => {
    if (!confirm('Filialni o\'chirishni tasdiqlaysizmi?')) return
    try {
      await branchService.delete(branchId)
      loadBranches()
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
        <h1 className="text-3xl font-bold text-gray-900">Filiallar</h1>
        {(isPharmacyAdmin || isAdmin) && (
          <button
            onClick={() => {
              setEditingBranch(null)
              setFormData({ name: '', address: '', phone: '', pharmacy_id: user?.pharmacy_id || null })
              setShowModal(true)
            }}
            className="btn btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Filial qo'shish
          </button>
        )}
      </div>

      {branches.length === 0 ? (
        <div className="card text-center py-12">
          <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Hozircha filiallar mavjud emas</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nomi</th>
                <th>Manzil</th>
                <th>Telefon</th>
                <th>Apteka ID</th>
                <th>Amallar</th>
              </tr>
            </thead>
            <tbody>
              {branches.map((branch) => (
                <tr key={branch.id}>
                  <td>{branch.id}</td>
                  <td className="font-medium">{branch.name}</td>
                  <td>{branch.address || '-'}</td>
                  <td>{branch.phone || '-'}</td>
                  <td>{branch.pharmacy_id}</td>
                  <td>
                    <div className="flex gap-2">
                      {(isPharmacyAdmin || isAdmin) && (
                        <>
                          <button
                            onClick={() => handleEdit(branch)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(branch.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingBranch ? 'Filialni tahrirlash' : 'Yangi filial'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {isAdmin && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Apteka
                  </label>
                  <select
                    value={formData.pharmacy_id || ''}
                    onChange={(e) => setFormData({ ...formData, pharmacy_id: parseInt(e.target.value) })}
                    required
                    className="input"
                  >
                    <option value="">Tanlang</option>
                    {pharmacies.map((pharmacy) => (
                      <option key={pharmacy.id} value={pharmacy.id}>
                        {pharmacy.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filial nomi
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Manzil
                </label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefon
                </label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="input"
                />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary flex-1">
                  {editingBranch ? 'Saqlash' : 'Yaratish'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingBranch(null)
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

