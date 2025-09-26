'use client';

import React, { useState, useEffect } from 'react';
import LiquidGlassCard from '@/components/LiquidGlassCard';
import LiquidButton from '@/components/LiquidButton';
import LiquidInput from '@/components/LiquidInput';

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
  const [minPrice, setMinPrice] = useState<number>(100);
  const [maxPrice, setMaxPrice] = useState<number>(500);
  const [status, setStatus] = useState<ScrapingStatus>({
    is_running: false,
    progress: 0,
    status_message: '準備完了',
    results: []
  });
  const [isLoading, setIsLoading] = useState(false);

  // ステータスチェック
  const checkStatus = async () => {
    try {
      const response = await fetch('/api/status');
      if (response.ok) {
        const statusData = await response.json();
        setStatus(statusData);
        return statusData;
      }
    } catch (error) {
      console.error('Status check failed:', error);
    }
    return null;
  };

  // スクレイピング開始
  const startScraping = async () => {
    if (minPrice > maxPrice) {
      alert('終値の下限は上限以下である必要があります。');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await fetch('/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          count,
          min_price: minPrice,
          max_price: maxPrice
        })
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || 'スクレイピングの開始に失敗しました');
      }

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
    checkStatus();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8 min-h-screen flex flex-col">
      {/* ヘッダー */}
      <div className="text-center mb-12 animate-float">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 tracking-tight">
          📈 銘柄コードスクレイパー
        </h1>
        <p className="text-xl text-white/80 max-w-2xl mx-auto">
          日本株の銘柄コードと価格情報を美しいLiquid Glassデザインで取得
        </p>
      </div>

      <div className="flex-1 grid lg:grid-cols-2 gap-8 max-w-7xl mx-auto w-full">
        {/* 左側: 入力フォーム */}
        <div className="space-y-6">
          <LiquidGlassCard hover className="animate-float" style={{animationDelay: '0.5s'}}>
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
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
                  value={minPrice}
                  onChange={(e) => setMinPrice(Number(e.target.value))}
                  min={1}
                  step={0.01}
                  required
                  placeholder="100"
                />
                
                <LiquidInput
                  label="終値上限 (円)"
                  type="number"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(Number(e.target.value))}
                  min={1}
                  step={0.01}
                  required
                  placeholder="500"
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
                <h3 className="text-lg font-semibold text-white">ステータス</h3>
              </div>
              
              <p className={`text-sm mb-4 ${status.error ? 'text-red-300' : 'text-white/90'}`}>
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
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center">
                📊 抽出結果
              </h2>
              {status.results.length > 0 && (
                <span className="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-medium">
                  {status.results.length} 件
                </span>
              )}
            </div>
            
            {status.results.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-6xl mb-4 opacity-30">📈</div>
                <p className="text-white/60 text-lg">
                  スクレイピングを開始すると、ここに結果が表示されます
                </p>
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                {status.results.map((result, index) => (
                  <div 
                    key={result.code}
                    className="flex justify-between items-center p-4 bg-white/10 rounded-lg hover:bg-white/20 transition-all duration-200 animate-float"
                    style={{animationDelay: `${index * 0.1}s`}}
                  >
                    <span className="font-mono text-lg font-bold text-blue-300">
                      {result.code}
                    </span>
                    <span className="text-white font-semibold">
                      ¥{result.price.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </LiquidGlassCard>
        </div>
      </div>

      {/* フッター */}
      <div className="text-center mt-12 text-white/50">
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

