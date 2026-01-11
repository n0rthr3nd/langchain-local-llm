import { useEffect, useRef } from 'react';
import { Message } from '../types';
import { MessageItem } from './MessageItem';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export const MessageList = ({ messages, isLoading }: MessageListProps) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gemini-border scrollbar-track-transparent">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-gemini-text-secondary px-4 animate-fade-in">
          <div className="bg-gemini-surface p-6 rounded-full mb-6">
            <svg className="w-12 h-12 text-gemini-secondary" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="currentColor" stroke="none" />
            </svg>
          </div>
          <h2 className="text-2xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-2">
            Hello, Human
          </h2>
          <p className="text-sm opacity-80 max-w-md text-center">
            I'm your local AI assistant. I can help you code, write summaries, or organize your thoughts.
          </p>
        </div>
      ) : (
        <div className="py-4 space-y-2">
          {messages.map((message, index) => (
            <MessageItem key={index} message={message} />
          ))}
          {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
            <div className="py-4 px-4 animate-pulse">
              <div className="max-w-4xl mx-auto flex gap-6">
                <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
                  <svg className="w-6 h-6 text-gemini-primary animate-spin" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="currentColor" stroke="none" />
                  </svg>
                </div>
                <div className="text-gemini-text-secondary text-sm flex items-center">Thinking...</div>
              </div>
            </div>
          )}
          <div ref={bottomRef} className="h-10" />
        </div>
      )}
    </div>
  );
};
