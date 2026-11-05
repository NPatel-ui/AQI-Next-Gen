import { motion } from 'framer-motion';

export function StatCard({
  title,
  value,
  unit = '',
  description,
  trend,
  trendType = 'neutral',
  icon: Icon,
  badge,
  variant = 'default',
  className = '',
}) {
  const trendColors = {
    positive: 'text-emerald-700 bg-emerald-50 border-emerald-200',
    negative: 'text-rose-700 bg-rose-50 border-rose-200',
    neutral: 'text-[#69766E] bg-[#F1F4EE] border-[#E3E8E1]',
  };

  const bgStyles = {
    default: 'bg-white border-[#E3E8E1]',
    forest: 'bg-[#173D2D] border-[#102C22] text-white',
    mint: 'bg-[#DDEBE0]/40 border-[#A8BFA9]/40',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`min-w-0 p-4 rounded-xl border transition-all ${
        bgStyles[variant] || bgStyles.default
      } ${className}`}
    >
      <div className="flex items-center justify-between gap-2 mb-2">
        <span
          className={`text-xs font-medium truncate ${
            variant === 'forest' ? 'text-[#A8BFA9]' : 'text-[#69766E]'
          }`}
        >
          {title}
        </span>
        {Icon && (
          <div
            className={`w-6 h-6 rounded-md flex items-center justify-center shrink-0 ${
              variant === 'forest'
                ? 'bg-white/10 text-[#B7E46A]'
                : 'bg-[#DDEBE0] text-[#173D2D]'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-1.5 flex-wrap">
        <span
          className={`text-2xl font-bold font-heading tracking-tight ${
            variant === 'forest' ? 'text-white' : 'text-[#17231C]'
          }`}
        >
          {value}
        </span>
        {unit && (
          <span
            className={`text-xs font-medium ${
              variant === 'forest' ? 'text-[#A8BFA9]' : 'text-[#69766E]'
            }`}
          >
            {unit}
          </span>
        )}
      </div>

      {(trend || description || badge) && (
        <div className="mt-2.5 pt-2 border-t border-[#E3E8E1]/60 flex items-center justify-between gap-2 text-xs">
          {description && (
            <span
              className={`truncate text-[11px] ${
                variant === 'forest' ? 'text-[#A8BFA9]' : 'text-[#69766E]'
              }`}
            >
              {description}
            </span>
          )}

          {trend && (
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${trendColors[trendType]}`}
            >
              {trend}
            </span>
          )}

          {badge && <div>{badge}</div>}
        </div>
      )}
    </motion.div>
  );
}
