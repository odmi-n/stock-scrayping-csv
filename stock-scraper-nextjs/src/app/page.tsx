'use client';

import React, { useState, useEffect, useMemo } from 'react';
import LiquidGlassCard from '@/components/LiquidGlassCard';
import LiquidButton from '@/components/LiquidButton';
import LiquidInput from '@/components/LiquidInput';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'https://odmin.pythonanywhere.com';

interface StockResult {
  code: string;
  price: number;
}

interface ScrapingStatus {
  is_running: boolean;
  progress: number;
  status_message: string;
  results: StockResult[];
  error?: string;
}

export default function Home() {
  const [count, setCount] = useState<number>(30);
  const [minPrice, setMinPrice] = useState<number | null>(100);
  const [maxPrice, setMaxPrice] = useState<number | null>(500);
  const [status, setStatus] = useState<ScrapingStatus>({
    is_running: false,
    progress: 0,
    status_message: '準備完了',
    results: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [sortKey, setSortKey] = useState<'code' | 'price'>('code');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const sortedResults = useMemo(() => {
    const results = status.results || [];
    const copy = results.slice();
    copy.sort((a, b) => {
      if (sortKey === 'price') {
        const diff = (a.price ?? 0) - (b.price ?? 0);
        return sortDir === 'asc' ? diff : -diff;
      }
      // code: prefer numeric comparison, fallback to string
      const aNum = Number(a.code);
      const bNum = Number(b.code);
      let cmp: number;
      if (!Number.isNaN(aNum) && !Number.isNaN(bNum)) {
        cmp = aNum - bNum;
      } else {
        cmp = String(a.code).localeCompare(String(b.code));
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return copy;
  }, [status.results, sortKey, sortDir]);

  const toggleSort = (key: 'code' | 'price') => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  // ステータスチェック
  const checkStatus = async () => {
    try {
      console.log('Fetching status from API...');
      const response = await fetch(`${API_BASE_URL}/api/status`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache'
        }
      });
      
      console.log('Status response:', response.status, response.statusText);
      
      if (response.ok) {
        try {
          const text = await response.text();
          console.log('Response text:', text);
          
          if (!text) {
            console.error('Empty response from API');
            return null;
          }
          
          const statusData = JSON.parse(text);
          console.log('Parsed status data:', statusData);
          setStatus(statusData);
          return statusData;
        } catch (parseError) {
          console.error('JSON parse error in status check:', parseError);
          const text = await response.text();
          console.error('Response text:', text);
        }
      } else {
        console.error('Status check failed with status:', response.status);
        const text = await response.text();
        console.error('Error response text:', text);
      }
    } catch (error) {
      console.error('Status check failed:', error);
      throw error;
    }
    return null;
  };

  // スクレイピング開始
  const startScraping = async () => {
    // null値のチェック
    if (minPrice === null || maxPrice === null) {
      alert('価格の範囲を入力してください。');
      return;
    }
    
    if (minPrice <= 0 || maxPrice <= 0) {
      alert('価格は1円以上を入力してください。');
      return;
    }
    
    if (minPrice > maxPrice) {
      alert('終値の下限は上限以下である必要があります。');
      return;
    }

    setIsLoading(true);
    
    try {
      console.log('Starting scraping with params:', { count, minPrice, maxPrice });
      const response = await fetch(`${API_BASE_URL}/api/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          count,
          min_price: minPrice,
          max_price: maxPrice
        })
      });
      
      console.log('Scrape response:', response.status, response.statusText);

      if (!response.ok) {
        let errorMessage = 'スクレイピングの開始に失敗しました';
        try {
          const result = await response.json();
          errorMessage = result.error || errorMessage;
        } catch (parseError) {
          // JSONパースエラーの場合は、レスポンステキストを取得
          const text = await response.text();
          console.error('JSON parse error:', parseError);
          console.error('Response text:', text);
          errorMessage = `サーバーエラー: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const result = await response.json();

      // ステータスポーリング開始
      const interval = setInterval(async () => {
        const statusData = await checkStatus();
        if (statusData && !statusData.is_running) {
          clearInterval(interval);
          setIsLoading(false);
        }
      }, 1000);

    } catch (error) {
      console.error('Scraping failed:', error);
      setStatus(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'エラーが発生しました',
        status_message: 'エラーが発生しました'
      }));
      setIsLoading(false);
    }
  };

  // 初期ステータスチェック
  useEffect(() => {
    const initializeApp = async () => {
      try {
        await checkStatus();
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setStatus(prev => ({
          ...prev,
          error: 'APIサーバーに接続できません。ページを再読み込みしてください。',
          status_message: 'エラーが発生しました'
        }));
      }
    };
    
    initializeApp();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8 min-h-screen flex flex-col">
      {/* ヘッダー */}
      <div className="text-center mb-12 animate-float">
        <h1 className="text-5xl md:text-6xl font-bold text-slate-100 mb-4 tracking-tight">
          📈 銘柄コードスクレイパー
        </h1>
        <p className="text-xl text-slate-300 max-w-2xl mx-auto">
          日本株の銘柄コードと価格情報を美しいLiquid Glassデザインで取得
        </p>
      </div>

      <div className="flex-1 grid lg:grid-cols-2 gap-8 max-w-7xl mx-auto w-full">
        {/* 左側: 入力フォーム */}
        <div className="space-y-6">
          <LiquidGlassCard hover className="animate-float" style={{animationDelay: '0.5s'}}>
            <h2 className="text-2xl font-bold text-slate-100 mb-6 flex items-center">
              ⚙️ 設定
            </h2>
            
            <div className="space-y-6">
              <LiquidInput
                label="抽出銘柄数"
                type="number"
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
                min={1}
                max={1000}
                required
                placeholder="30"
              />
              
              <div className="grid grid-cols-2 gap-4">
                <LiquidInput
                  label="終値下限 (円)"
                  type="number"
                  value={minPrice || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '') {
                      setMinPrice(null);
                    } else {
                      const numValue = parseInt(value);
                      if (!isNaN(numValue)) {
                        setMinPrice(numValue);
                      }
                    }
                  }}
                  min={1}
                  required
                  placeholder="100"
                  integerOnly
                />
                
                <LiquidInput
                  label="終値上限 (円)"
                  type="number"
                  value={maxPrice || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '') {
                      setMaxPrice(null);
                    } else {
                      const numValue = parseInt(value);
                      if (!isNaN(numValue)) {
                        setMaxPrice(numValue);
                      }
                    }
                  }}
                  min={1}
                  required
                  placeholder="500"
                  integerOnly
                />
              </div>
            </div>
            
            <div className="mt-8">
              <LiquidButton
                onClick={startScraping}
                disabled={isLoading || status.is_running}
                loading={isLoading || status.is_running}
                size="lg"
                className="w-full text-lg animate-pulse-glow"
              >
                🚀 スクレイピング開始
              </LiquidButton>
            </div>
          </LiquidGlassCard>

          {/* ステータス表示 */}
          {(status.status_message !== '準備完了' || status.error) && (
            <LiquidGlassCard className={`animate-float ${status.error ? 'border-red-400/50' : 'border-blue-400/50'}`} style={{animationDelay: '1s'}}>
              <div className="flex items-center mb-4">
                <div className={`w-3 h-3 rounded-full mr-3 ${status.is_running ? 'bg-green-400 animate-pulse' : status.error ? 'bg-red-400' : 'bg-blue-400'}`}></div>
                <h3 className="text-lg font-semibold text-slate-100">ステータス</h3>
              </div>
              
              <p className={`text-sm mb-4 ${status.error ? 'text-red-300' : 'text-slate-300'}`}>
                {status.error || status.status_message}
              </p>
              
              {status.is_running && (
                <div className="w-full bg-white/20 rounded-full h-2 mb-2">
                  <div 
                    className="bg-gradient-to-r from-blue-400 to-purple-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${status.progress}%` }}
                  ></div>
                </div>
              )}
              
              {!status.is_running && status.progress > 0 && (
                <div className="text-xs text-white/70">
                  進行状況: {status.progress}%
                </div>
              )}
            </LiquidGlassCard>
          )}
        </div>

        {/* 右側: 結果表示 */}
        <div className="space-y-6">
          <LiquidGlassCard hover className="h-full animate-float" style={{animationDelay: '1.5s'}}>
            <div className="flex items-center justify-between mb-6 gap-3 flex-wrap">
              <h3 className="text-2xl font-bold text-slate-100 flex items-center">
                📊 抽出結果
              </h3>
              <div className="flex items-center gap-3">
                {status.results.length > 0 && (
                  <span className="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-medium">
                    {status.results.length} 件
                  </span>
                )}
                {/* Sort controls */}
                <div className="flex items-center gap-2 bg-white/10 rounded-lg p-1 border border-white/20">
                  <button
                    onClick={() => toggleSort('code')}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      sortKey === 'code' ? 'bg-white/20 text-white' : 'text-slate-200 hover:bg-white/10'
                    }`}
                    aria-label="Sort by code"
                  >
                    銘柄{sortKey === 'code' ? (sortDir === 'asc' ? '▲' : '▼') : ''}
                  </button>
                  <button
                    onClick={() => toggleSort('price')}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      sortKey === 'price' ? 'bg-white/20 text-white' : 'text-slate-200 hover:bg-white/10'
                    }`}
                    aria-label="Sort by price"
                  >
                    価格{sortKey === 'price' ? (sortDir === 'asc' ? '▲' : '▼') : ''}
                  </button>
                </div>
              </div>
            </div>
            
            {status.results.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-6xl mb-4 opacity-30">📈</div>
                <p className="text-slate-400 text-lg">
                  スクレイピングを開始すると、ここに結果が表示されます
                </p>
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                {sortedResults.map((result, index) => (
                  <div 
                    key={result.code}
                    className="flex justify-between items-center p-4 bg-white/10 rounded-lg hover:bg-white/20 transition-all duration-200 animate-float"
                    style={{animationDelay: `${index * 0.1}s`}}
                  >
                    <span className="font-mono text-lg font-bold text-blue-300">
                      {result.code}
                    </span>
                    <span className="text-slate-100 font-semibold">
                      ¥{Math.round(result.price).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </LiquidGlassCard>
        </div>
      </div>

      {/* フッター */}
      <div className="text-center mt-12 text-slate-500">
        <p className="text-sm">
          Powered by Next.js & Liquid Glass Design
        </p>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.3);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.5);
        }
      `}</style>
    </div>
  );
}

