import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, ArrowRight, Menu, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/Button';

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const navLinks = [
    { label: 'Overview', href: '#overview' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'Benchmarks', href: '#benchmarks' },
    { label: 'Dataset', href: '#dataset' },
  ];

  const handleLaunch = () => {
    navigate(isAuthenticated ? '/dashboard' : '/signin');
  };

  const handleScrollTo = (e, href) => {
    e.preventDefault();
    setMobileOpen(false);
    const elem = document.querySelector(href);
    if (elem) {
      elem.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-[#F7F8F4]/90 backdrop-blur-md border-b border-[#E3E8E1]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#173D2D] text-[#B7E46A] flex items-center justify-center font-bold">
            <Activity className="w-4 h-4 text-[#B7E46A]" />
          </div>
          <span className="font-heading font-bold text-base tracking-tight text-[#17231C]">
            AQI Forecaster
          </span>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-7">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={(e) => handleScrollTo(e, link.href)}
              className="text-xs font-medium text-[#69766E] hover:text-[#17231C] transition-colors"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Desktop Auth CTAs */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <Button
              onClick={() => navigate('/dashboard')}
              variant="primary"
              size="sm"
              icon={ArrowRight}
              iconPosition="right"
            >
              Dashboard
            </Button>
          ) : (
            <>
              <Link
                to="/signin"
                className="text-xs font-semibold text-[#17231C] hover:text-[#173D2D] px-2.5 py-1.5"
              >
                Sign In
              </Link>
              <Button
                onClick={handleLaunch}
                variant="lime"
                size="sm"
                icon={ArrowRight}
                iconPosition="right"
              >
                Launch Platform
              </Button>
            </>
          )}
        </div>

        {/* Mobile Hamburger Button */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-1.5 rounded-lg text-[#17231C] hover:bg-[#DDEBE0]/50"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileOpen && (
        <div className="md:hidden bg-white border-b border-[#E3E8E1] px-4 pt-3 pb-5 space-y-3 shadow-md">
          <nav className="space-y-1">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                onClick={(e) => handleScrollTo(e, link.href)}
                className="block px-3 py-2 rounded-lg text-xs font-medium text-[#17231C] hover:bg-[#F7F8F4]"
              >
                {link.label}
              </a>
            ))}
          </nav>
          <div className="pt-2 border-t border-[#E3E8E1] flex flex-col gap-2">
            {!isAuthenticated ? (
              <>
                <Link
                  to="/signin"
                  onClick={() => setMobileOpen(false)}
                  className="w-full text-center py-2 rounded-lg border border-[#E3E8E1] text-xs font-medium text-[#17231C]"
                >
                  Sign In
                </Link>
                <Button
                  onClick={handleLaunch}
                  variant="lime"
                  size="sm"
                  className="w-full"
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  Launch Platform
                </Button>
              </>
            ) : (
              <Button
                onClick={() => {
                  setMobileOpen(false);
                  navigate('/dashboard');
                }}
                variant="primary"
                size="sm"
                className="w-full"
                icon={ArrowRight}
                iconPosition="right"
              >
                Dashboard
              </Button>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
