import { Link } from 'react-router-dom';
import { Activity } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-[#102C22] text-[#DDEBE0] border-t border-[#173D2D] py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-8 border-b border-[#173D2D]">
          {/* Brand */}
          <div className="space-y-2">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-[#B7E46A] text-[#102C22] flex items-center justify-center font-bold">
                <Activity className="w-4 h-4 text-[#102C22]" />
              </div>
              <span className="font-heading font-bold text-base text-white">
                AQI Next-Gen
              </span>
            </div>
            <p className="text-xs text-[#A8BFA9] leading-relaxed">
              Next-day India AQI and PM AQI forecasting across 50 supported Indian cities.
            </p>
          </div>

          {/* Navigation */}
          <div className="space-y-2.5 text-xs">
            <div className="font-semibold text-white">Platform</div>
            <ul className="space-y-1.5 text-[#A8BFA9]">
              <li><Link to="/forecast" className="hover:text-white">Forecasting</Link></li>
              <li><Link to="/analytics" className="hover:text-white">Historical Trends</Link></li>
              <li><Link to="/comparison" className="hover:text-white">City Comparison</Link></li>
              <li><Link to="/health-advisor" className="hover:text-white">Health Guidance</Link></li>
            </ul>
          </div>

          {/* Dataset Info */}
          <div className="space-y-2.5 text-xs">
            <div className="font-semibold text-white">Data Scope</div>
            <ul className="space-y-1.5 text-[#A8BFA9]">
              <li>Inputs: Daily pollution + weather data</li>
              <li>Coverage: 50 Indian cities</li>
              <li>Features: 118 per model</li>
              <li>Models: Two HistGradientBoosting models</li>
            </ul>
          </div>

          {/* Notice */}
          <div className="space-y-2 text-xs text-[#A8BFA9]">
            <div className="font-semibold text-white">Disclaimer</div>
            <p className="leading-relaxed text-[11px]">
              Predictions are model estimates based on available daily input data. Forecast values are not official CPCB measurements or a substitute for real-time monitoring.
            </p>
          </div>
        </div>

        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#A8BFA9]">
          <p>© {new Date().getFullYear()} AQI Next-Gen.</p>
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="hover:text-white">Dashboard</Link>
            <Link to="/signin" className="hover:text-white">Sign In</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
