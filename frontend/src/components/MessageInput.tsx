import { useState, useRef, useEffect } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  isStreaming: boolean;
  onStopGeneration: () => void;
}

export const MessageInput = ({
  onSendMessage,
  isLoading,
  isStreaming,
  onStopGeneration,
}: MessageInputProps) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
      if (textareaRef.current) textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="relative bg-gemini-surface rounded-3xl shadow-lg border border-gemini-border focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
        <div className="flex items-end pl-4 pr-3 py-3 gap-2">
          {/* File Upload Button - Placeholder for functionality */}
          <button
            type="button"
            className="p-2 text-gemini-text-secondary hover:text-gemini-text-primary hover:bg-gemini-hover rounded-full transition-colors pb-2.5"
            title="Attach file (demo)"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            className="flex-1 bg-transparent text-gemini-text-primary placeholder-gemini-text-secondary resize-none focus:outline-none max-h-48 py-2 font-light"
            rows={1}
            disabled={isLoading}
            aria-label="Message input"
          />

          <div className="pb-1">
            {isStreaming ? (
              <button
                type="button"
                onClick={onStopGeneration}
                className="p-2 rounded-full bg-gemini-text-primary text-gemini-bg hover:opacity-90 transition-colors"
                aria-label="Stop generation"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <rect x="6" y="6" width="8" height="8" />
                </svg>
              </button>
            ) : (
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="p-2 rounded-full bg-gemini-text-primary text-gemini-bg disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90 transition-all"
                aria-label="Send message"
              >
                <svg className="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </form>
      <div className="mt-2 text-[10px] text-center text-gemini-text-secondary opacity-60">
        Gemini may display inaccurate info, including about people, so double-check its responses.
      </div>
    </div>
  );
};
