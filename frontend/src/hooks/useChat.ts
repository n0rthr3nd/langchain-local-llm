import { useState, useCallback, useRef } from 'react';
import { Message, ChatSettings } from '../types';
import { api } from '../utils/api';

export const useChat = (settings: ChatSettings) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string, useStreaming = true) => {
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (useStreaming) {
        setIsStreaming(true);
        const assistantMessage: Message = {
          role: 'assistant',
          content: '',
          timestamp: Date.now(),
        };

        setMessages(prev => [...prev, assistantMessage]);

        const stream = api.chatStream({
          messages: [...messages, userMessage],
          model: settings.model,
          temperature: settings.temperature,
          max_tokens: settings.max_tokens,
          system_prompt: settings.system_prompt,
        });

        for await (const chunk of stream) {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage.role === 'assistant') {
              lastMessage.content += chunk;
            }
            return newMessages;
          });
        }

        setIsStreaming(false);
      } else {
        const response = await api.chat({
          messages: [...messages, userMessage],
          model: settings.model,
          temperature: settings.temperature,
          max_tokens: settings.max_tokens,
          system_prompt: settings.system_prompt,
        });

        const assistantMessage: Message = {
          role: 'assistant',
          content: response.response,
          timestamp: Date.now(),
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, [messages, settings]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setIsLoading(false);
  }, []);

  const regenerateLastMessage = useCallback(() => {
    if (messages.length < 2) return;

    const newMessages = messages.slice(0, -1);
    const lastUserMessage = [...newMessages].reverse().find(m => m.role === 'user');

    if (lastUserMessage) {
      setMessages(newMessages);
      sendMessage(lastUserMessage.content);
    }
  }, [messages, sendMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    isStreaming,
    sendMessage,
    stopGeneration,
    regenerateLastMessage,
    clearMessages,
    setMessages,
  };
};
