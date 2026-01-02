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
    <div className="flex-1 overflow-y-auto">
      {messages.length === 0 ? (
        <div className="h-full flex items-center justify-center text-gray-400">
          <div className="text-center">
            <h2 className="text-3xl font-semibold mb-2">ChatGPT Local con Ollama</h2>
            <p className="text-sm">Escribe un mensaje para comenzar</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message, index) => (
            <MessageItem key={index} message={message} />
          ))}
          {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
            <div className="py-6 px-4 bg-chat-assistant">
              <div className="max-w-3xl mx-auto flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-sm bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold">
                  A
                </div>
                <div className="flex-1 text-gray-100">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </>
      )}
    </div>
  );
};
