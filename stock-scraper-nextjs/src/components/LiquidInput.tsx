'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface LiquidInputProps {
  label?: string;
  placeholder?: string;
  value?: string | number;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: 'text' | 'number' | 'email' | 'password';
  required?: boolean;
  min?: number;
  max?: number;
  step?: number;
  className?: string;
  disabled?: boolean;
}

export default function LiquidInput({
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  required = false,
  min,
  max,
  step,
  className,
  disabled = false
}: LiquidInputProps) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-white/90">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        className={cn(
          "liquid-input w-full px-4 py-3 rounded-lg transition-all duration-300 focus:transform focus:scale-105 disabled:opacity-50 disabled:cursor-not-allowed",
          className
        )}
      />
    </div>
  );
}

