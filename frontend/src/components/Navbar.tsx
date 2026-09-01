import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  ShieldAlert, 
  SlidersHorizontal, 
  BarChart3, 
  Cpu, 
  RefreshCw, 
  LogOut, 
  LogIn, 
  User as UserIcon,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { api } from '../services/api';

interface NavbarProps {
  onDemoLoaded?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onDemoLoaded }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const handleLoadDemo = async () => {
    try {
      setLoadingDemo(true);
      const res = await api.loadDemoData();
      setNotification(`Loaded ${res.total_incidents} prioritized incidents!`);
      if (onDemoLoaded) onDemoLoaded();
      setTimeout(() => setNotification(null), 4000);
    } catch (err: any) {
      alert(`Error loading demo data: ${err.message}`);
    } finally {
      setLoadingDemo(false);
    }
  };

  const navLinks = [
    { to: '/', label: 'Triage Queue', icon: ShieldAlert },
    { to: '/simulator', label: 'What-If Simulator', icon: SlidersHorizontal },
    { to: '/analytics', label: 'SOC Analytics', icon: BarChart3 },
    { to: '/admin', label: 'ML Performance', icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#080c14]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-rose-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:border-cyan-400 transition-colors shadow-[0_0_15px_rgba(6,182,212,0.2)]">
              <ShieldAlert className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-white flex items-center gap-2">
                CYBER PRIORITIZATION
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-300">
                  ML + Rules
                </span>
              </span>
              <p className="text-[11px] text-slate-400 font-mono">SOC Decision Engine &bull; 65% ML / 35% Rules</p>
            </div>
          </Link>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map(({ to, label, icon: Icon }) => {
            const isActive = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-cyan-400 border border-cyan-500/30 shadow-inner'
                    : 'text-slate-300 hover:text-white hover:bg-slate-850'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* Notification Toast pill if demo loaded */}
          {notification && (
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 text-xs font-mono rounded-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 animate-fade-in">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              {notification}
            </div>
          )}

          {/* Seed Demo Incidents Button */}
          <button
            onClick={handleLoadDemo}
            disabled={loadingDemo}
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-mono font-semibold rounded-lg bg-gradient-to-r from-cyan-600/90 to-blue-600/90 hover:from-cyan-500 hover:to-blue-500 text-white border border-cyan-400/40 shadow-[0_0_12px_rgba(6,182,212,0.25)] transition-all active:scale-95 disabled:opacity-50"
            title="Seed 100 realistic cyber incidents & 10 critical assets"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingDemo ? 'animate-spin' : ''}`} />
            <span>{loadingDemo ? 'INGESTING...' : 'LOAD DEMO INCIDENTS'}</span>
          </button>

          {/* User Profile / Auth */}
          {isAuthenticated && user ? (
            <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
              <div className="flex flex-col text-right">
                <span className="text-xs font-semibold text-slate-200">{user.full_name}</span>
                <span className="text-[10px] font-mono text-cyan-400 capitalize">{user.role}</span>
              </div>
              <button
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition-colors"
                title="Log Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
