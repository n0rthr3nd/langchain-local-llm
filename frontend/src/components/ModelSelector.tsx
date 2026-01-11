import { useState, useEffect, useRef } from 'react';
import { ModelInfo, ChatSettings } from '../types';
import { api } from '../utils/api';

interface ModelSelectorProps {
  settings: ChatSettings;
  onSettingsChange: (settings: ChatSettings) => void;
}

export const ModelSelector = ({ settings, onSettingsChange }: ModelSelectorProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadModels();

    // Click outside handler
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const modelList = await api.getModels();
      const validModels = modelList.filter(model => model.name && model.name.trim());
      if (validModels.length > 0) {
        setModels(validModels);
      } else {
        setModels([{ name: 'gemma2:2b' }, { name: 'llama3.2' }, { name: 'mistral' }]);
      }
    } catch (error) {
      console.error('Error loading models:', error);
      setModels([{ name: 'gemma2:2b' }, { name: 'llama3.2' }, { name: 'mistral' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = (model: string) => {
    onSettingsChange({ ...settings, model });
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-3 py-1.5 text-gemini-text-secondary hover:text-gemini-text-primary hover:bg-gemini-hover rounded-lg transition-all text-sm font-medium"
      >
        <span>{settings.model}</span>
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 left-0 w-64 bg-gemini-surface rounded-xl shadow-2xl border border-gemini-border p-2 z-50 animate-fade-in">
          <div className="mb-2 px-2 py-1">
            <span className="text-xs font-semibold text-gemini-text-secondary uppercase">Model Selection</span>
          </div>

          <div className="space-y-1 max-h-60 overflow-y-auto scrollbar-thin">
            {models.map((model) => (
              <button
                key={model.name}
                onClick={() => {
                  handleModelChange(model.name);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${settings.model === model.name
                  ? 'bg-blue-500/10 text-blue-400'
                  : 'text-gemini-text-primary hover:bg-gemini-hover'
                  }`}
              >
                {model.name}
                {settings.model === model.name && (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            ))}
          </div>

          <div className="mt-2 pt-2 border-t border-gemini-border">
            <div className="px-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gemini-text-secondary">Temp: {settings.temperature}</span>
                <input
                  type="range" min="0" max="1" step="0.1"
                  value={settings.temperature}
                  onChange={(e) => onSettingsChange({ ...settings, temperature: parseFloat(e.target.value) })}
                  className="w-24 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
            <div className="flex items-center gap-2 mt-2 px-2 cursor-pointer hover:bg-gemini-hover rounded p-1"
              onClick={() => onSettingsChange({ ...settings, use_knowledge_base: !settings.use_knowledge_base })}>
              <div className={`w-4 h-4 border rounded flex items-center justify-center ${settings.use_knowledge_base ? 'bg-purple-500 border-purple-500' : 'border-gray-500'}`}>
                {settings.use_knowledge_base && <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
              </div>
              <span className="text-xs text-gemini-text-secondary select-none">Use Knowledge Base</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
