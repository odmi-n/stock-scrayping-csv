'use client';

import React from 'react';
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface LiquidGlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'dark' | 'light';
  hover?: boolean;
  float?: boolean;
  style?: React.CSSProperties;
}

export default function LiquidGlassCard({ 
  children, 
  className, 
  variant = 'default',
  hover = false,
  float = false,
  style
}: LiquidGlassCardProps) {
  const baseClasses = "glass-card p-6 transition-all duration-300";
  const hoverClasses = hover ? "hover:scale-105 hover:shadow-2xl" : "";
  const floatClasses = float ? "animate-float" : "";
  
  const variantClasses = {
    default: "glass-card",
    dark: "glass-card-dark",
    light: "bg-white/20 backdrop-blur-lg border border-white/30"
  };

  return (
    <div 
      className={cn(
        baseClasses,
        variantClasses[variant],
        hoverClasses,
        floatClasses,
        className
      )}
      style={style}
    >
      {children}
    </div>
  );
}

