import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { branchService } from '../services/branchService'
import { MapPin, Navigation, Loader2 } from 'lucide-react'

export default function NearbyBranches() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [locPermissionError, setLocPermissionError] = useState('')
  const [userLocation, setUserLocation] = useState(null)
  const [branches, setBranches] = useState([])

  useEffect(() => {
    if (!navigator.geolocation) {
      setLocPermissionError('Brauzer geolokatsiyani qo‘llab-quvvatlamaydi')
      setLoading(false)
      return
    }

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords
        setUserLocation({ latitude, longitude })

        try {
          const data = await branchService.getNearby(latitude, longitude, 15)
          setBranches(data || [])
        } catch (error) {
          console.error('Yaqin filiallarni yuklashda xatolik:', error)
        } finally {
          setLoading(false)
        }
      },
      (err) => {
        console.error(err)
        setLocPermissionError('Joylashuvga ruxsat berilmadi. Iltimos, brauzer sozlamalaridan ruxsat bering.')
        setLoading(false)
      }
    )
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-2 text-gray-600">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Yaqin filiallar yuklanmoqda...</span>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Yaqin filiallar</h1>

      {locPermissionError && (
        <div className="mb-4 p-4 rounded-lg bg-red-50 text-red-700 text-sm">
          {locPermissionError}
        </div>
      )}

      {userLocation && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold mb-2 flex items-center">
            <Navigation className="w-4 h-4 mr-2 text-primary-600" />
            Sizning joylashuvingiz
          </h2>
          <p className="text-sm text-gray-600">
            Lat: {userLocation.latitude.toFixed(5)}, Lng: {userLocation.longitude.toFixed(5)}
          </p>
        </div>
      )}

      {branches.length === 0 ? (
        <div className="card">
          <p className="text-gray-600">
            Hozircha yaqin atrofda filiallar topilmadi.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {branches.map((item) => {
            const branch = item.branch
            return (
              <div key={branch.id} className="card flex flex-col">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                      <MapPin className="w-4 h-4 mr-2 text-primary-600" />
                      {branch.name}
                    </h3>
                    {branch.address && (
                      <p className="text-sm text-gray-600 mt-1">{branch.address}</p>
                    )}
                    {branch.phone && (
                      <p className="text-sm text-gray-500 mt-1">Tel: {branch.phone}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Masofa</p>
                    <p className="text-lg font-semibold text-primary-600">
                      {item.distance_km.toFixed(1)} km
                    </p>
                  </div>
                </div>

                {branch.latitude && branch.longitude && (
                  <div className="mb-3 rounded-lg overflow-hidden border">
                    <iframe
                      title={`map-${branch.id}`}
                      src={`https://www.google.com/maps?q=${branch.latitude},${branch.longitude}&z=15&output=embed`}
                      width="100%"
                      height="180"
                      style={{ border: 0 }}
                      loading="lazy"
                      referrerPolicy="no-referrer-when-downgrade"
                    />
                  </div>
                )}

                <div className="mt-auto flex gap-2">
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${branch.latitude},${branch.longitude}`}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-secondary flex-1 text-center"
                  >
                    Xaritada ochish
                  </a>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}


