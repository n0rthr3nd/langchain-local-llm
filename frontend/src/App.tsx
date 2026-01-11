import { useState, useEffect } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { ConversationList } from './components/ConversationList';
import { KnowledgeBaseView } from './components/KnowledgeBaseView';
import { useChat } from './hooks/useChat';
import { storage } from './utils/storage';
import { Conversation, ChatSettings } from './types';

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'chat' | 'knowledge'>('chat');
  const [settings, setSettings] = useState<ChatSettings>(() => storage.getSettings());
  const [showSidebar, setShowSidebar] = useState(true);

  const {
    messages,
    isLoading,
    isStreaming,
    sendMessage,
    stopGeneration,
    regenerateLastMessage,
    clearMessages,
    setMessages,
  } = useChat(settings);

  useEffect(() => {
    const savedConversations = storage.getConversations();
    setConversations(savedConversations);
    if (savedConversations.length > 0) {
      const latest = savedConversations[0];
      setCurrentConversationId(latest.id);
      setMessages(latest.messages);
    }
  }, []);

  useEffect(() => {
    storage.saveSettings(settings);
  }, [settings]);

  useEffect(() => {
    if (currentConversationId && messages.length > 0) {
      saveCurrentConversation();
    }
  }, [messages]);

  const saveCurrentConversation = () => {
    if (!currentConversationId) return;

    const updatedConversations = conversations.map((conv) =>
      conv.id === currentConversationId
        ? {
          ...conv,
          messages,
          updatedAt: Date.now(),
          title: messages[0]?.content.slice(0, 50) || 'Nueva conversación',
        }
        : conv
    );

    setConversations(updatedConversations);
    storage.saveConversations(updatedConversations);
  };

  const handleNewConversation = () => {
    if (messages.length > 0 && currentConversationId) {
      saveCurrentConversation();
    }

    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'Nueva conversación',
      messages: [],
      model: settings.model,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    const updatedConversations = [newConversation, ...conversations];
    setConversations(updatedConversations);
    storage.saveConversations(updatedConversations);
    setCurrentConversationId(newConversation.id);
    clearMessages();
  };

  const handleSelectConversation = (id: string) => {
    if (currentConversationId && messages.length > 0) {
      saveCurrentConversation();
    }

    const conversation = conversations.find((conv) => conv.id === id);
    if (conversation) {
      setCurrentConversationId(id);
      setMessages(conversation.messages);
    }
  };

  const handleDeleteConversation = (id: string) => {
    const updatedConversations = conversations.filter((conv) => conv.id !== id);
    setConversations(updatedConversations);
    storage.saveConversations(updatedConversations);

    if (currentConversationId === id) {
      if (updatedConversations.length > 0) {
        const next = updatedConversations[0];
        setCurrentConversationId(next.id);
        setMessages(next.messages);
      } else {
        setCurrentConversationId(null);
        clearMessages();
      }
    }
  };

  const handleSendMessage = (content: string) => {
    if (!currentConversationId) {
      handleNewConversation();
    }
    sendMessage(content);
  };

  return (
    <div className="flex h-screen bg-gemini-bg text-gemini-text-primary overflow-hidden">
      {/* Sidebar - Conditional Render */}

      <div className={`${showSidebar ? 'w-[280px]' : 'w-0'} transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0 relative`}>
        <ConversationList
          conversations={conversations}
          currentConversationId={currentConversationId}
          currentView={currentView}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
          onViewChange={setCurrentView}
        />
      </div>

      <div className="flex-1 flex flex-col relative w-full h-full max-w-full">
        {/* Toggle Button - Floating top left if sidebar closed, or inside layout */}
        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className={`absolute top-4 ${showSidebar ? 'left-4 opacity-0 pointer-events-none' : 'left-4 opacity-100'} z-20 
            p-2 text-gemini-text-secondary hover:text-gemini-text-primary hover:bg-gemini-hover rounded-full transition-all`}
          aria-label="Toggle sidebar"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {currentView === 'chat' ? (
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            isStreaming={isStreaming}
            settings={settings}
            onSendMessage={handleSendMessage}
            onStopGeneration={stopGeneration}
            onRegenerateLastMessage={regenerateLastMessage}
            onClearMessages={clearMessages}
            onSettingsChange={setSettings}
          />
        ) : (
          <div className="flex-1 bg-gemini-bg p-6 overflow-auto">
            <KnowledgeBaseView />
          </div>
        )}
      </div>
    </div>
  );


}

export default App;
