import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  LayoutDashboard,
  Building2,
  MapPin,
  Pill,
  Package,
  ShoppingCart,
  LogOut,
} from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  // Role-based navigation
  const getAllowedNavigation = () => {
    const role = user?.role
    const allNav = [
      { name: 'Bosh sahifa', href: '/', icon: LayoutDashboard, roles: ['superadmin', 'operator', 'pharmacy_admin', 'branch_admin', 'cashier', 'user'] },
      { name: 'Yaqin filiallar', href: '/nearby-branches', icon: MapPin, roles: ['superadmin', 'operator', 'pharmacy_admin', 'branch_admin', 'cashier', 'user'] },
      { name: 'Aptekalar', href: '/pharmacies', icon: Building2, roles: ['superadmin', 'operator', 'pharmacy_admin'] },
      { name: 'Filiallar', href: '/branches', icon: MapPin, roles: ['superadmin', 'operator', 'pharmacy_admin'] },
      { name: 'Dorilar', href: '/drugs', icon: Pill, roles: ['superadmin', 'operator', 'pharmacy_admin', 'branch_admin'] },
      { name: 'Ombor', href: '/inventory', icon: Package, roles: ['superadmin', 'operator', 'pharmacy_admin', 'branch_admin'] },
      { name: 'Buyurtmalar', href: '/orders', icon: ShoppingCart, roles: ['superadmin', 'operator', 'pharmacy_admin', 'branch_admin', 'cashier'] },
    ]
    return allNav.filter(item => item.roles.includes(role))
  }

  const navigation = getAllowedNavigation()

  const getRoleName = (role) => {
    const roles = {
      superadmin: 'Super Admin',
      operator: 'Operator',
      pharmacy_admin: 'Apteka Admini',
      branch_admin: 'Filial Admini',
      cashier: 'Kassir',
      user: 'Foydalanuvchi',
    }
    return roles[role] || role
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 border-b">
            <h1 className="text-2xl font-bold text-primary-600">Med</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User Info */}
          <div className="p-4 border-t">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {user?.full_name || user?.email}
                </p>
                <p className="text-xs text-gray-500">{getRoleName(user?.role)}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Chiqish
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="pl-64">
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

