
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Activity,
  ArrowRight,
  Wind,
  LineChart,
  GitCompare,
  HeartPulse,
  ChevronRight,
} from 'lucide-react';

import { Navbar } from '../components/navigation/Navbar';
import { Footer } from '../components/navigation/Footer';
import { Button } from '../components/ui/Button';
import { BentoCard } from '../components/ui/BentoCard';
import { ELIGIBLE_CITIES } from '../utils/datasetInfo';
import { useAuth } from '../context/AuthContext';

export function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [demoCity, setDemoCity] = useState('Delhi');

  const demoForecasts = {
    Delhi: {
      predicted: 218,
      observed: 198,
      category: 'Poor',
      color: '#F97316',
      bg: '#FFF7ED',
      text: '#9A3412',
      pm25: 124.5,
      pm10: 215.0,
      mae: 39.1,
    },
    Mumbai: {
      predicted: 94,
      observed: 89,
      category: 'Satisfactory',
      color: '#22C55E',
      bg: '#F0FDF4',
      text: '#166534',
      pm25: 42.1,
      pm10: 88.0,
      mae: 13.4,
    },
    Bengaluru: {
      predicted: 82,
      observed: 78,
      category: 'Satisfactory',
      color: '#22C55E',
      bg: '#F0FDF4',
      text: '#166534',
      pm25: 35.8,
      pm10: 64.2,
      mae: 25.5,
    },
    Kolkata: {
      predicted: 142,
      observed: 138,
      category: 'Moderate',
      color: '#F59E0B',
      bg: '#FFFBEB',
      text: '#92400E',
      pm25: 68.4,
      pm10: 130.5,
      mae: 28.2,
    },
  };

  const currentDemo =
    demoForecasts[demoCity] || demoForecasts.Delhi;

  const handleStart = () => {
    navigate(isAuthenticated ? '/dashboard' : '/signin');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F8F4] text-[#17231C]">
      <Navbar />

      {/* HERO SECTION */}
      <section className="pt-10 pb-16 md:pt-16 md:pb-24 border-b border-[#E3E8E1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-8 items-center">

            {/* Left Hero Column */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="lg:col-span-7 space-y-5 max-w-2xl"
            >
              <h1 className="text-3xl sm:text-5xl font-extrabold font-heading text-[#17231C] tracking-tight leading-tight">
                Understand the Air. <br className="hidden sm:inline" />
                <span className="text-[#173D2D]">
                  Anticipate Tomorrow.
                </span>
              </h1>

              <p className="text-sm sm:text-base text-[#69766E] leading-relaxed">
                Explore next-day India AQI and PM AQI forecasts across 50 supported Indian cities using two trained machine-learning models and daily pollution and weather inputs.
              </p>

              {/* CTAs */}
              <div className="flex flex-wrap items-center gap-3 pt-1">
                <Button
                  onClick={() =>
                    navigate(isAuthenticated ? '/forecast' : '/signin')
                  }
                  variant="primary"
                  size="md"
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  Generate Next-Day Forecast
                </Button>

                <Button
                  onClick={handleStart}
                  variant="secondary"
                  size="md"
                >
                  Explore Dashboard
                </Button>
              </div>

              {/* 3 Project Statistics */}
              <div className="pt-5 border-t border-[#E3E8E1] grid grid-cols-3 gap-4">
                <div>
                  <div className="text-xl sm:text-2xl font-bold font-heading text-[#173D2D]">
                    77,600
                  </div>
                  <div className="text-xs text-[#69766E]">
                    Historical Daily Records
                  </div>
                </div>

                <div>
                  <div className="text-xl sm:text-2xl font-bold font-heading text-[#173D2D]">
                    50 Cities
                  </div>
                  <div className="text-xs text-[#69766E]">
                    Supported Indian Cities
                  </div>
                </div>

                <div>
                  <div className="text-xl sm:text-2xl font-bold font-heading text-[#173D2D]">
                    Next-day
                  </div>
                  <div className="text-xs text-[#69766E]">
                    Forecast Horizon
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Right Hero Column: Forecast Preview */}
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="lg:col-span-5 min-w-0"
            >
              <div className="rounded-2xl bg-[#102C22] text-white p-5 sm:p-6 border border-[#173D2D] shadow-md space-y-4">

                {/* City Picker Pills */}
                <div className="flex items-center justify-between pb-3 border-b border-white/10 gap-2">
                  <span className="text-xs text-[#A8BFA9] font-medium">
                    Illustrative UI Preview · Not a live forecast
                  </span>

                  <div className="flex items-center gap-1">
                    {['Delhi', 'Mumbai', 'Bengaluru', 'Kolkata'].map((c) => (
                      <button
                        key={c}
                        onClick={() => setDemoCity(c)}
                        className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                          demoCity === c
                            ? 'bg-[#B7E46A] text-[#102C22]'
                            : 'bg-white/10 text-white hover:bg-white/15'
                        }`}
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Main Forecast Numbers */}
                <div className="flex items-baseline justify-between gap-3">
                  <div>
                    <div className="text-xs text-[#A8BFA9]">
                      Predicted AQI
                    </div>

                    <div className="text-4xl font-extrabold font-heading text-white mt-0.5">
                      {currentDemo.predicted}
                    </div>
                  </div>

                  <div
                    className="px-3 py-1 rounded-lg text-xs font-bold border"
                    style={{
                      backgroundColor: currentDemo.bg,
                      color: currentDemo.text,
                      borderColor: currentDemo.color,
                    }}
                  >
                    {currentDemo.category}
                  </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2 p-3 rounded-xl bg-white/5 border border-white/10 text-xs">
                  <div>
                    <span className="text-[#A8BFA9] block text-[11px]">
                      Observed Base:
                    </span>
                    <span className="font-semibold text-white font-mono">
                      {currentDemo.observed} AQI
                    </span>
                  </div>

                  <div>
                    <span className="text-[#A8BFA9] block text-[11px]">
                      City Error (MAE):
                    </span>
                    <span className="font-semibold text-[#B7E46A] font-mono">
                      ±{currentDemo.mae}
                    </span>
                  </div>

                  <div>
                    <span className="text-[#A8BFA9] block text-[11px]">
                      PM2.5:
                    </span>
                    <span className="font-medium text-white">
                      {currentDemo.pm25} µg/m³
                    </span>
                  </div>

                  <div>
                    <span className="text-[#A8BFA9] block text-[11px]">
                      PM10:
                    </span>
                    <span className="font-medium text-white">
                      {currentDemo.pm10} µg/m³
                    </span>
                  </div>
                </div>

                {/* Footer link */}
                <div className="pt-2 flex items-center justify-between text-xs text-[#A8BFA9]">
                  <span className="text-[11px]">
                    CPCB Observation Benchmark
                  </span>

                  <Link
                    to="/forecast"
                    className="text-[#B7E46A] hover:underline flex items-center gap-1 font-medium"
                  >
                    Open Forecaster
                    <ChevronRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* PLATFORM MODULES */}
      <section id="overview" className="py-16 bg-white border-b border-[#E3E8E1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div>
            <h2 className="text-2xl font-bold font-heading text-[#17231C]">
              Platform Modules
            </h2>

            <p className="text-xs sm:text-sm text-[#69766E] mt-0.5">
              Tools for exploring city forecasts, long-term trends, and health guidelines.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <BentoCard title="AQI Forecasting" icon={Wind}>
              <p className="text-xs text-[#69766E] leading-relaxed mt-1">
                Generate next-day AQI predictions for any of the 18 eligible cities based on historical base dates.
              </p>
            </BentoCard>

            <BentoCard title="Historical Trends" icon={LineChart}>
              <p className="text-xs text-[#69766E] leading-relaxed mt-1">
                View 5-year monthly patterns showing winter peaks, monsoon dips, and annual trajectories.
              </p>
            </BentoCard>

            <BentoCard title="City Comparison" icon={GitCompare}>
              <p className="text-xs text-[#69766E] leading-relaxed mt-1">
                Compare air quality averages, seasonal curves, and model error between any two cities.
              </p>
            </BentoCard>

            <BentoCard title="Health Guidance" icon={HeartPulse}>
              <p className="text-xs text-[#69766E] leading-relaxed mt-1">
                Clear health advisories, mask recommendations, and precautions based on CPCB categories.
              </p>
            </BentoCard>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="py-16 bg-[#F7F8F4] border-b border-[#E3E8E1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div>
            <h2 className="text-2xl font-bold font-heading text-[#17231C]">
              How the Forecasting Engine Works
            </h2>

            <p className="text-xs sm:text-sm text-[#69766E] mt-0.5">
              A 3-step pipeline converting historical observations into next-day estimates.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <BentoCard title="1. Temporal Lags" variant="default">
              <p className="text-xs text-[#69766E] leading-relaxed mt-1">
                Calculates prior-day AQI (1, 2, and 7 days ago), 3-day and 7-day rolling means, and day-of-week signals.
              </p>
            </BentoCard>

            <BentoCard title="2. Pollutant Features" variant="default">
              <p className="text-xs text-[#69766E] leading-relaxed mt-1">
                Integrates daily concentrations of PM2.5, PM10, NO2, CO, SO2, and O3 to capture chemical interactions.
              </p>
            </BentoCard>

            <BentoCard title="3. HistGradientBoosting Models" variant="default">
              <p className="text-xs text-[#69766E] leading-relaxed mt-1">
                Two trained HistGradientBoosting models generate India AQI and PM AQI predictions from 118 engineered features each.
              </p>
            </BentoCard>
          </div>
        </div>
      </section>

      {/* MODEL EVALUATION */}
      <section id="benchmarks" className="py-16 bg-white border-b border-[#E3E8E1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div>
            <h2 className="text-2xl font-bold font-heading text-[#17231C]">Model Evaluation</h2>
            <p className="text-xs sm:text-sm text-[#69766E] mt-0.5">Test-set performance of the two deployed HistGradientBoosting models.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {name:'Full India AQI Model',mae:'19.95',rmse:'31.09',r2:'0.8091'},
              {name:'PM AQI Model',mae:'14.58',rmse:'28.31',r2:'0.8399'},
            ].map((model) => (
              <div key={model.name} className="rounded-xl border border-[#E3E8E1] bg-white p-5 space-y-3">
                <h3 className="font-bold text-sm text-[#17231C]">{model.name}</h3>
                <p className="text-xs text-[#69766E]">HistGradientBoosting Regressor · 118 engineered features</p>
                <div className="grid grid-cols-3 gap-2">
                  {[['MAE',model.mae],['RMSE',model.rmse],['R²',model.r2]].map(([label,value]) => (
                    <div key={label} className="p-3 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1]">
                      <div className="text-[11px] text-[#69766E]">{label}</div>
                      <div className="text-lg font-bold font-mono text-[#173D2D]">{value}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <p className="text-[11px] text-[#69766E]">MAE and RMSE are measured in AQI points. Evaluation metrics describe test-set performance and do not guarantee the error of an individual forecast.</p>
        </div>
      </section>

      {/* DATASET OVERVIEW */}
      <section id="dataset" className="py-16 bg-[#F7F8F4] border-b border-[#E3E8E1]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div>
            <h2 className="text-2xl font-bold font-heading text-[#17231C]">
              Supported Cities (50 Cities)
            </h2>

            <p className="text-xs sm:text-sm text-[#69766E] mt-0.5">
              All cities configured in the AQI Next-Gen daily data pipeline.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
            {ELIGIBLE_CITIES.map((c) => (
              <div
                key={c.name}
                className="p-3 rounded-lg bg-white border border-[#E3E8E1] text-xs"
              >
                <div className="font-semibold text-[#17231C] truncate">
                  {c.name}
                </div>

                <div className="text-[10px] text-[#69766E] truncate">
                  {c.state}
                </div>

              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CALL TO ACTION */}
      <section className="py-16 bg-[#102C22] text-white">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center space-y-4">
          <h2 className="text-2xl sm:text-4xl font-bold font-heading text-white">
            Explore Air Quality Predictions
          </h2>

          <p className="text-xs sm:text-sm text-[#A8BFA9] max-w-xl mx-auto">
            Access the forecasting dashboard, inspect historical trends, and review health advisories.
          </p>

          <div className="pt-2 flex items-center justify-center">
            <Button
              onClick={handleStart}
              variant="lime"
              size="md"
              icon={ArrowRight}
              iconPosition="right"
            >
              Open Dashboard
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
