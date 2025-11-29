import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { pharmacyService } from '../services/pharmacyService'
import { Building2, Plus, Check, X } from 'lucide-react'

export default function Pharmacies() {
  const { user } = useAuth()
  const [pharmacies, setPharmacies] = useState([])
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [selectedRequest, setSelectedRequest] = useState(null)
  const [formData, setFormData] = useState({ name: '', address: '', phone: '' })
  const [rejectReason, setRejectReason] = useState('')

  const isAdmin = user?.role === 'superadmin' || user?.role === 'operator'
  const isPharmacyAdmin = user?.role === 'pharmacy_admin'

  useEffect(() => {
    if (isAdmin || isPharmacyAdmin) {
      loadPharmacies()
    } else {
      setLoading(false)
    }
  }, [isAdmin, isPharmacyAdmin])

  const loadPharmacies = async () => {
    try {
      const data = await pharmacyService.getAll()
      setPharmacies(data)
    } catch (error) {
      console.error('Pharmacies yuklashda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateRequest = async (e) => {
    e.preventDefault()
    try {
      await pharmacyService.createRequest(formData)
      setShowCreateModal(false)
      setFormData({ name: '', address: '', phone: '' })
      alert('So\'rov yuborildi! Operator tomonidan ko\'rib chiqiladi.')
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const handleApprove = async () => {
    try {
      await pharmacyService.approveRequest(selectedRequest.id)
      setShowApproveModal(false)
      setSelectedRequest(null)
      loadPharmacies()
      alert('Apteka tasdiqlandi!')
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  const handleReject = async () => {
    try {
      await pharmacyService.rejectRequest(selectedRequest.id, rejectReason)
      setShowApproveModal(false)
      setSelectedRequest(null)
      setRejectReason('')
      alert('So\'rov rad etildi')
    } catch (error) {
      alert(error.response?.data?.detail || 'Xatolik yuz berdi')
    }
  }

  if (!isAdmin && !isPharmacyAdmin) {
    return (
      <div className="card">
        <p className="text-gray-600">Sizda bu sahifaga kirish huquqi yo'q.</p>
      </div>
    )
  }

  if (loading) {
    return <div className="text-center py-8">Yuklanmoqda...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Aptekalar</h1>
        {!isAdmin && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Apteka so'rovi yaratish
          </button>
        )}
      </div>

      {pharmacies.length === 0 ? (
        <div className="card text-center py-12">
          <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Hozircha aptekalar mavjud emas</p>
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
                <th>Yaratilgan</th>
              </tr>
            </thead>
            <tbody>
              {pharmacies.map((pharmacy) => (
                <tr key={pharmacy.id}>
                  <td>{pharmacy.id}</td>
                  <td className="font-medium">{pharmacy.name}</td>
                  <td>{pharmacy.address || '-'}</td>
                  <td>{pharmacy.phone || '-'}</td>
                  <td>{new Date(pharmacy.created_at).toLocaleDateString('uz-UZ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Request Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Apteka so'rovi yaratish</h2>
            <form onSubmit={handleCreateRequest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Apteka nomi
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
                  Yuborish
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
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

