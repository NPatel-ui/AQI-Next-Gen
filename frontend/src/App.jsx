import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

// Public Pages
import { LandingPage } from './pages/LandingPage';
import { SignInPage } from './pages/SignInPage';
import { SignUpPage } from './pages/SignUpPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';

// Protected Pages
import { DashboardPage } from './pages/DashboardPage';
import { ForecastPage } from './pages/ForecastPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { HealthAdvisorPage } from './pages/HealthAdvisorPage';
import { ProfilePage } from './pages/ProfilePage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/signin" element={<SignInPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Protected Workspace Routes inside AppLayout */}
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="/health-advisor" element={<HealthAdvisorPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>

          {/* Catch-all redirect to Landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
