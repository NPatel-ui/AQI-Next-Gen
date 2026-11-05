import { Loader2 } from 'lucide-react';

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  className = '',
  ...props
}) {
  const base =
    'relative inline-flex items-center justify-center font-medium transition-all duration-200 select-none disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#173D2D]/30';

  const sizeClasses = {
    sm: 'text-xs h-8 px-3 rounded-lg gap-1.5',
    md: 'text-sm h-10 px-4 rounded-xl gap-2 font-medium',
    lg: 'text-base h-12 px-6 rounded-xl gap-2.5 font-semibold',
    icon: 'h-10 w-10 rounded-xl justify-center p-0',
  };

  const variantClasses = {
    primary:
      'bg-[#173D2D] text-white hover:bg-[#102C22] shadow-sm hover:shadow border border-[#102C22]/30',
    lime: 'bg-[#B7E46A] text-[#102C22] hover:bg-[#A4D355] font-semibold shadow-sm hover:shadow-md border border-[#A4D355]',
    secondary:
      'bg-white text-[#173D2D] hover:bg-[#F7F8F4] border border-[#E3E8E1] shadow-xs hover:border-[#A8BFA9]',
    outline:
      'bg-transparent text-[#173D2D] border border-[#A8BFA9]/60 hover:bg-[#DDEBE0]/40 hover:border-[#173D2D]',
    ghost: 'bg-transparent text-[#69766E] hover:text-[#17231C] hover:bg-[#DDEBE0]/30',
    danger: 'bg-[#EF4444] text-white hover:bg-[#DC2626] shadow-sm',
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`${base} ${sizeClasses[size] || sizeClasses.md} ${variantClasses[variant] || variantClasses.primary} ${className}`}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin shrink-0" />
      ) : Icon && iconPosition === 'left' ? (
        <Icon className="w-4 h-4 shrink-0" />
      ) : null}

      <span>{children}</span>

      {!isLoading && Icon && iconPosition === 'right' && (
        <Icon className="w-4 h-4 shrink-0" />
      )}
    </button>
  );
}

