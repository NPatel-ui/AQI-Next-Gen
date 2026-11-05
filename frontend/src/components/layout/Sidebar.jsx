import { NavLink, Link, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Wind,
  LineChart,
  GitCompare,
  HeartPulse,
  UserRound,
  LogOut,
  Activity,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export function Sidebar({ onCloseMobile }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    onCloseMobile?.();
    await logout();
    navigate('/');
  };

  const navItems = [
    {
      to: '/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      to: '/forecast',
      label: 'Forecasting',
      icon: Wind,
    },
    {
      to: '/analytics',
      label: 'Historical Analytics',
      icon: LineChart,
    },
    {
      to: '/comparison',
      label: 'City Comparison',
      icon: GitCompare,
    },
    {
      to: '/health-advisor',
      label: 'Health Advisor',
      icon: HeartPulse,
    },
    {
      to: '/profile',
      label: 'My Profile',
      icon: UserRound,
    },
  ];

  return (
    <aside className="w-60 h-full bg-[#102C22] text-white flex flex-col justify-between shrink-0 select-none border-r border-[#173D2D]">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-[#173D2D]">
          <Link to="/dashboard" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#B7E46A] flex items-center justify-center text-[#102C22] font-bold">
              <Activity className="w-4 h-4 text-[#102C22]" />
            </div>
            <div>
              <div className="font-heading font-bold text-sm tracking-tight text-white">
                AQI Forecaster
              </div>
              <div className="text-[11px] text-[#A8BFA9]">
                Air Quality Platform
              </div>
            </div>
          </Link>
        </div>

        {/* Navigation links */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `group flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-[#173D2D] text-[#B7E46A] border border-[#B7E46A]/20'
                      : 'text-[#DDEBE0] hover:text-white hover:bg-white/5'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      className={`w-4 h-4 shrink-0 transition-colors ${
                        isActive ? 'text-[#B7E46A]' : 'text-[#A8BFA9] group-hover:text-white'
                      }`}
                    />
                    <span className="truncate">{item.label}</span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer / User Session */}
      <div className="p-3 border-t border-[#173D2D] bg-[#0D221A]/50">
        <Link
          to="/profile"
          onClick={onCloseMobile}
          className="px-3 py-2 rounded-lg bg-[#173D2D]/40 mb-2 flex items-center justify-between gap-2 hover:bg-[#173D2D]/70 transition-colors group"
        >
          <div className="min-w-0">
            <div className="text-xs font-semibold text-white truncate group-hover:text-[#B7E46A] transition-colors">
              {user?.name || 'User'}
            </div>
            <div className="text-[10px] text-[#A8BFA9] truncate">
              {user?.email || 'Logged in'}
            </div>
          </div>
          <span className="w-2 h-2 rounded-full bg-[#B7E46A] shrink-0" />
        </Link>

        <button
          onClick={handleSignOut}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 text-xs font-medium text-[#A8BFA9] hover:text-white hover:bg-white/5 rounded-lg transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
