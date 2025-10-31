import { NavLink } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export const Sidebar = () => {
  const { user } = useAuth();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/transactions', label: 'Transacciones', icon: '💳' },
    { path: '/new-transaction', label: 'Nueva Transacción', icon: '➕' },
  ];

  // Add admin view for specific users if needed
  const isAdmin = user && user.id === parseInt(import.meta.env.VITE_ADMIN_USER_ID || '0');
  if (isAdmin) {
    navItems.push({ path: '/admin', label: 'Vista Admin', icon: '👥' });
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <span className="text-xl">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
