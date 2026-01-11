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

export const ChatWindow = ({
  messages,
  isLoading,
  isStreaming,
  settings,
  onSendMessage,
  onStopGeneration,
  onRegenerateLastMessage,
  onClearMessages,
  onSettingsChange,
}: ChatWindowProps) => {
  return (
    <div className="flex flex-col h-full bg-gemini-bg relative">
      {/* Header - Transparent & Blurred */}
      <header className="absolute top-0 left-0 right-0 z-10 px-4 py-3 flex items-center justify-between bg-gemini-bg/80 backdrop-blur-md border-b border-transparent transition-all">
        <div className="flex items-center gap-2">
          <span className="text-gemini-text-primary font-medium text-lg tracking-tight">LangChain Local</span>
          <ModelSelector settings={settings} onSettingsChange={onSettingsChange} />
        </div>

        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <>
              <button
                onClick={onRegenerateLastMessage}
                disabled={isLoading || messages.length < 2}
                className="p-2 text-gemini-text-secondary hover:text-gemini-text-primary hover:bg-gemini-hover disabled:opacity-50 rounded-full transition-all"
                title="Regenerate last message"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <button
                onClick={onClearMessages}
                disabled={isLoading}
                className="p-2 text-gemini-text-secondary hover:text-gemini-text-primary hover:bg-gemini-hover disabled:opacity-50 rounded-full transition-all"
                title="Clear messages"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden relative flex flex-col pt-16">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>

      {/* Input Area - Floating at bottom */}
      <div className="w-full px-4 pb-6 pt-2 bg-gradient-to-t from-gemini-bg via-gemini-bg to-transparent z-10">
        <MessageInput
          onSendMessage={onSendMessage}
          isLoading={isLoading}
          isStreaming={isStreaming}
          onStopGeneration={onStopGeneration}
        />
      </div>
    </div>
  );
};
