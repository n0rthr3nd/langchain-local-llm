import React from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ModelSelector } from './ModelSelector';
import { Message, ChatSettings } from '../types';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  settings: ChatSettings;
  onSendMessage: (message: string) => void;
  onStopGeneration: () => void;
  onRegenerateLastMessage: () => void;
  onClearMessages: () => void;
  onSettingsChange: (settings: ChatSettings) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  isStreaming,
  settings,
  onSendMessage,
  onStopGeneration,
  onRegenerateLastMessage,
  onClearMessages,
  onSettingsChange,
}) => {
  return (
    <div className="flex flex-col h-screen bg-chat-bg">
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <h1 className="text-white text-lg font-semibold">ChatGPT Local - Ollama</h1>
        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <>
              <button
                onClick={onRegenerateLastMessage}
                disabled={isLoading || messages.length < 2}
                className="px-3 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-white rounded-lg transition-colors text-sm"
                aria-label="Regenerate last message"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <button
                onClick={onClearMessages}
                disabled={isLoading}
                className="px-3 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-white rounded-lg transition-colors text-sm"
                aria-label="Clear messages"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </>
          )}
          <ModelSelector settings={settings} onSettingsChange={onSettingsChange} />
        </div>
      </header>

      <MessageList messages={messages} isLoading={isLoading} />

      <MessageInput
        onSendMessage={onSendMessage}
        isLoading={isLoading}
        isStreaming={isStreaming}
        onStopGeneration={onStopGeneration}
      />
    </div>
  );
};
