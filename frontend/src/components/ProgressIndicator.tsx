import React from 'react';
import { Loader2 } from 'lucide-react';
import { ProgressIndicatorProps } from '../types';

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ progress, isVisible }) => {
  if (!isVisible || !progress) {
    return null;
  }

  return (
    <div className="px-4 py-2 animate-fade-in">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <Loader2 size={16} className="animate-spin text-primary-500 flex-shrink-0" />
            
            <div className="flex-1">
              <div className="text-sm text-gray-700 mb-2">
                {progress.message}
              </div>
              
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${Math.max(0, Math.min(100, progress.progress * 100))}%` }}
                />
              </div>
            </div>
            
            <div className="text-xs text-gray-500 font-mono">
              {Math.round(progress.progress * 100)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;
