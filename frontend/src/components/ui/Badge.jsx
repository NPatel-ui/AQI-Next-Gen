export function Badge({ children, variant = 'default', size = 'md', className = '' }) {
  const sizeClasses = {
    sm: 'text-xs px-2.5 py-0.5',
    md: 'text-xs px-3 py-1 font-medium',
    lg: 'text-sm px-3.5 py-1.5 font-semibold',
  };

  const variantClasses = {
    default: 'bg-[#DDEBE0] text-[#173D2D] border border-[#A8BFA9]/40',
    forest: 'bg-[#173D2D] text-[#B7E46A] border border-[#102C22]',
    lime: 'bg-[#B7E46A] text-[#102C22] font-semibold',
    neutral: 'bg-[#F1F4EE] text-[#69766E] border border-[#E3E8E1]',
    outline: 'border border-[#A8BFA9] text-[#173D2D] bg-white/70 backdrop-blur-sm',
    warning: 'bg-[#FFFBEB] text-[#92400E] border border-[#FDE68A]',
    danger: 'bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA]',
    success: 'bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0]',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full transition-colors ${sizeClasses[size] || sizeClasses.md} ${variantClasses[variant] || variantClasses.default} ${className}`}
    >
      {children}
    </span>
  );
}

export function AqiBadge({ aqi, size = 'md', showValue = true }) {
  const num = Number(aqi);
  let bg = 'bg-[#ECFDF5]';
  let text = 'text-[#065F46]';
  let border = 'border-[#A7F3D0]';
  let label = 'Good';

  if (num > 400) {
    bg = 'bg-[#FFF1F2]';
    text = 'text-[#881337]';
    border = 'border-[#FECDD3]';
    label = 'Severe';
  } else if (num > 300) {
    bg = 'bg-[#FEF2F2]';
    text = 'text-[#991B1B]';
    border = 'border-[#FECACA]';
    label = 'Very Poor';
  } else if (num > 200) {
    bg = 'bg-[#FFF7ED]';
    text = 'text-[#9A3412]';
    border = 'border-[#FED7AA]';
    label = 'Poor';
  } else if (num > 100) {
    bg = 'bg-[#FFFBEB]';
    text = 'text-[#92400E]';
    border = 'border-[#FDE68A]';
    label = 'Moderate';
  } else if (num > 50) {
    bg = 'bg-[#F0FDF4]';
    text = 'text-[#166534]';
    border = 'border-[#BBF7D0]';
    label = 'Satisfactory';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold border ${bg} ${text} ${border} ${
        size === 'lg' ? 'px-3.5 py-1 text-sm' : 'px-2.5 py-0.5 text-xs'
      }`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70 animate-pulse" />
      {label} {showValue && !isNaN(num) && <span className="opacity-80">({Math.round(num)})</span>}
    </span>
  );
}

