import { motion } from 'framer-motion';

export function BentoCard({
  children,
  title,
  subtitle,
  icon: Icon,
  badge,
  action,
  className = '',
  headerClassName = '',
  contentClassName = '',
  variant = 'default',
  hoverEffect = true,
  animate = true,
}) {
  const variantStyles = {
    default: 'bg-white border-[#E3E8E1] text-[#17231C]',
    forest: 'bg-[#173D2D] border-[#102C22] text-white',
    deepForest: 'bg-[#102C22] border-[#0D221A] text-white',
    softMint: 'bg-[#DDEBE0]/40 border-[#A8BFA9]/40 text-[#173D2D]',
    subtle: 'bg-[#F7F8F4] border-[#E3E8E1] text-[#17231C]',
  };

  const Wrapper = animate ? motion.div : 'div';
  const animationProps = animate
    ? {
        initial: { opacity: 0, y: 8 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.25, ease: 'easeOut' },
      }
    : {};

  return (
    <Wrapper
      {...animationProps}
      className={`min-w-0 rounded-2xl border p-4 sm:p-5 transition-all duration-150 flex flex-col relative ${
        variantStyles[variant] || variantStyles.default
      } ${hoverEffect ? 'hover:shadow-xs' : ''} ${className}`}
    >
      {(title || subtitle || Icon || badge || action) && (
        <div
          className={`flex items-start justify-between gap-3 mb-3 shrink-0 ${headerClassName}`}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            {Icon && (
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                  variant === 'forest' || variant === 'deepForest'
                    ? 'bg-white/10 text-[#B7E46A]'
                    : 'bg-[#DDEBE0] text-[#173D2D]'
                }`}
              >
                <Icon className="w-4 h-4" />
              </div>
            )}
            <div className="min-w-0">
              {title && (
                <h3
                  className={`text-sm font-semibold leading-tight truncate ${
                    variant === 'forest' || variant === 'deepForest'
                      ? 'text-white'
                      : 'text-[#17231C]'
                  }`}
                >
                  {title}
                </h3>
              )}
              {subtitle && (
                <p
                  className={`text-[11px] mt-0.5 leading-snug line-clamp-1 ${
                    variant === 'forest' || variant === 'deepForest'
                      ? 'text-[#A8BFA9]'
                      : 'text-[#69766E]'
                  }`}
                >
                  {subtitle}
                </p>
              )}
            </div>
          </div>

          {(badge || action) && (
            <div className="flex items-center gap-2 shrink-0">
              {badge}
              {action}
            </div>
          )}
        </div>
      )}

      <div className={`min-w-0 flex-1 flex flex-col ${contentClassName}`}>{children}</div>
    </Wrapper>
  );
}
