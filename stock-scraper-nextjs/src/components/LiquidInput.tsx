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
  integerOnly?: boolean; // 整数のみ入力を許可するオプション
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
  disabled = false,
  integerOnly = false
}: LiquidInputProps) {
  
  // 整数のみ入力を制限するキーボードイベントハンドラー
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (integerOnly && type === 'number') {
      // 数字、編集・ナビゲーション・システムキーのみ許可
      const allowedKeys = [
        'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 
        'Tab', 'Enter', 'Home', 'End', 'Escape'
      ];
      const isNumber = /^[0-9]$/.test(e.key);
      const isControlKey = e.ctrlKey || e.metaKey; // Ctrl+A, Ctrl+C, Ctrl+V など
      
      if (!isNumber && !allowedKeys.includes(e.key) && !isControlKey) {
        e.preventDefault();
      }
    }
  };
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-slate-200">
          {label}
          {required && <span className="text-red-400 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        onKeyDown={handleKeyDown}
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

