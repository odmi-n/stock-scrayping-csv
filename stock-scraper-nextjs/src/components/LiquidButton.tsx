'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface LiquidButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  loading?: boolean;
}

export default function LiquidButton({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  size = 'md',
  className,
  loading = false
}: LiquidButtonProps) {
  const baseClasses = "liquid-button rounded-lg font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none";
  
  const sizeClasses = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg"
  };
  
  const variantClasses = {
    primary: "text-white hover:shadow-lg",
    secondary: "text-white/80 hover:text-white",
    ghost: "text-white/70 hover:text-white hover:bg-white/10"
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        baseClasses,
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
    >
      {loading ? (
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          処理中...
        </div>
      ) : (
        children
      )}
    </button>
  );
}

