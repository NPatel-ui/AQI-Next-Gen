import { useState, useRef, useEffect } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { Menu, UserRound, LogOut, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const ROUTE_NAMES = {
  '/dashboard': 'Dashboard',
  '/forecast': 'Forecasting',
  '/analytics': 'Historical Analytics',
  '/comparison': 'City Comparison',
  '/health-advisor': 'Health Advisor',
  '/profile': 'My Profile',
};

export function Topbar({ onToggleMobile }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const currentTitle = ROUTE_NAMES[location.pathname] || 'Dashboard';

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

  const handleNavigateProfile = () => {
    setDropdownOpen(false);
    navigate('/profile');
  };

  const handleSignOut = async () => {
    setDropdownOpen(false);
    await logout();
    navigate('/');
  };

  return (
    <header className="h-14 bg-white border-b border-[#E3E8E1] px-4 sm:px-6 flex items-center justify-between gap-4 sticky top-0 z-30 shrink-0">
      {/* Left: Mobile Toggle & Page Title */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onToggleMobile}
          className="lg:hidden p-1.5 rounded-lg text-[#69766E] hover:text-[#17231C] hover:bg-[#F7F8F4] border border-[#E3E8E1] transition-colors"
          aria-label="Toggle navigation"
        >
          <Menu className="w-4 h-4" />
        </button>

        <h1 className="text-base font-bold font-heading text-[#17231C] truncate">
          {currentTitle}
        </h1>
      </div>

      {/* Right: Clickable User Avatar with Dropdown */}
      <div className="relative" ref={dropdownRef}>
        <button
          type="button"
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2 p-1 rounded-full hover:ring-2 hover:ring-[#173D2D]/20 transition-all focus:outline-none"
          aria-expanded={dropdownOpen}
          aria-haspopup="true"
        >
          {user?.avatarUrl ? (
            <img
              src={user.avatarUrl}
              alt={user.name || 'User Avatar'}
              className="w-8 h-8 rounded-full object-cover border border-[#E3E8E1]"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-[#173D2D] text-[#B7E46A] flex items-center justify-center font-bold text-xs shadow-xs">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
          )}
          <ChevronDown
            className={`w-3.5 h-3.5 text-[#69766E] transition-transform duration-200 hidden sm:block ${
              dropdownOpen ? 'rotate-180' : ''
            }`}
          />
        </button>

        {/* Dropdown Menu */}
        <AnimatePresence>
          {dropdownOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -4 }}
              transition={{ duration: 0.15 }}
              className="absolute right-0 mt-2 w-56 rounded-2xl bg-white border border-[#E3E8E1] shadow-lg py-1.5 z-50 text-xs text-[#17231C] focus:outline-none"
            >
              {/* User Header */}
              <div className="px-3.5 py-2.5 border-b border-[#E3E8E1]">
                <div className="font-semibold text-sm truncate text-[#17231C]">
                  {user?.name || 'Analyst'}
                </div>
                <div className="text-[11px] text-[#69766E] truncate mt-0.5">
                  {user?.email || 'analyst@aqi-forecaster.org'}
                </div>
              </div>

              {/* Action Items */}
              <div className="p-1">
                <button
                  type="button"
                  onClick={handleNavigateProfile}
                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-[#17231C] hover:bg-[#F7F8F4] transition-colors text-left"
                >
                  <UserRound className="w-4 h-4 text-[#173D2D]" />
                  <span>My Profile</span>
                </button>
              </div>

              <div className="p-1 border-t border-[#E3E8E1]">
                <button
                  type="button"
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-rose-600 hover:bg-rose-50 transition-colors text-left"
                >
                  <LogOut className="w-4 h-4 text-rose-500" />
                  <span>Sign Out</span>
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </header>
  );
}
