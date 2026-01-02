import React, { useState, useEffect } from 'react';
import { ModelInfo, ChatSettings } from '../types';
import { api } from '../utils/api';

interface ModelSelectorProps {
  settings: ChatSettings;
  onSettingsChange: (settings: ChatSettings) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({ settings, onSettingsChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const modelList = await api.getModels();
      setModels(modelList);
    } catch (error) {
      console.error('Error loading models:', error);
      setModels([{ name: 'llama3.2' }, { name: 'mistral' }, { name: 'phi3:mini' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleModelChange = (model: string) => {
    onSettingsChange({ ...settings, model });
  };

  const handleTemperatureChange = (temperature: number) => {
    onSettingsChange({ ...settings, temperature });
  };

  const handleMaxTokensChange = (max_tokens: number) => {
    onSettingsChange({ ...settings, max_tokens });
  };

  const handleSystemPromptChange = (system_prompt: string) => {
    onSettingsChange({ ...settings, system_prompt });
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
        aria-label="Open settings"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span className="text-sm">{settings.model}</span>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 right-0 w-80 bg-gray-800 rounded-lg shadow-xl border border-gray-700 p-4 z-50">
          <h3 className="text-white font-semibold mb-4">Configuración</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-2">Modelo</label>
              <select
                value={settings.model}
                onChange={(e) => handleModelChange(e.target.value)}
                className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {loading ? (
                  <option>Cargando...</option>
                ) : (
                  models.map((model) => (
                    <option key={model.name} value={model.name}>
                      {model.name}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Temperature: {settings.temperature.toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={settings.temperature}
                onChange={(e) => handleTemperatureChange(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-300 mb-2">Max Tokens</label>
              <input
                type="number"
                min="128"
                max="4096"
                step="128"
                value={settings.max_tokens}
                onChange={(e) => handleMaxTokensChange(parseInt(e.target.value))}
                className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-300 mb-2">System Prompt</label>
              <textarea
                value={settings.system_prompt}
                onChange={(e) => handleSystemPromptChange(e.target.value)}
                className="w-full bg-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                rows={3}
              />
            </div>
          </div>

          <button
            onClick={() => setIsOpen(false)}
            className="mt-4 w-full bg-purple-500 hover:bg-purple-600 text-white rounded py-2 transition-colors"
          >
            Cerrar
          </button>
        </div>
      )}
    </div>
  );
};
