import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F7F8F4]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-3 border-[#173D2D] border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-[#69766E] font-medium tracking-wide">
            Verifying intelligence workspace...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }

  return children;
}

