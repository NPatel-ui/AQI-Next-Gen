import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function AppLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-[#F7F8F4] overflow-hidden">
      {/* Desktop Persistent Sidebar */}
      <div className="hidden lg:block shrink-0">
        <Sidebar />
      </div>

      {/* Mobile Drawer Backdrop & Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 lg:hidden flex">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileMenuOpen(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-xs"
            />

            {/* Sidebar drawer */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 250 }}
              className="relative w-72 max-w-[85vw] h-full z-10 flex flex-col"
            >
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="absolute top-4 right-4 z-20 p-1.5 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
                aria-label="Close menu"
              >
                <X className="w-5 h-5" />
              </button>
              <Sidebar onCloseMobile={() => setMobileMenuOpen(false)} />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <Topbar onToggleMobile={() => setMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-0 focus:outline-none">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

