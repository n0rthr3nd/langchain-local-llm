
import { Conversation } from '../types';

type ViewType = 'chat' | 'knowledge';

interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  currentView: ViewType;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  onViewChange: (view: ViewType) => void;
}

export const ConversationList = ({
  conversations,
  currentConversationId,
  currentView,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onViewChange,
}: ConversationListProps) => {
  return (
    <div className="w-[280px] h-full bg-gemini-surface border-r border-gemini-border flex flex-col transition-all duration-300 ease-in-out">

      {/* Header Actions */}
      <div className="p-4 space-y-3">
        {/* New Chat Button - Prominent */}
        <button
          onClick={onNewConversation}
          className="w-full flex items-center gap-3 px-4 py-3 bg-gemini-hover hover:bg-opacity-80 text-gemini-text-primary rounded-full transition-all shadow-sm hover:shadow-md group"
        >
          <div className="p-1 bg-gemini-text-primary/10 rounded-full">
            <svg className="w-5 h-5 text-gemini-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <span className="font-medium text-sm">New Chat</span>
        </button>

        {/* View Switchers */}
        <div className="flex flex-col gap-1">
          <button
            onClick={() => onViewChange('chat')}
            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${currentView === 'chat'
              ? 'bg-blue-500/10 text-blue-400'
              : 'text-gemini-text-secondary hover:bg-gemini-hover hover:text-gemini-text-primary'
              }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <span>Chat</span>
          </button>

          <button
            onClick={() => onViewChange('knowledge')}
            className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${currentView === 'knowledge'
              ? 'bg-purple-500/10 text-purple-400'
              : 'text-gemini-text-secondary hover:bg-gemini-hover hover:text-gemini-text-primary'
              }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span>Knowledge Base</span>
          </button>
        </div>
      </div>

      {/* Recent Activity Label */}
      <div className="px-5 py-2">
        <span className="text-xs font-semibold text-gemini-text-secondary uppercase tracking-wider">Recent</span>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1 scrollbar-thin">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            onClick={() => onSelectConversation(conv.id)}
            className={`group flex items-center justify-between px-3 py-2 rounded-full cursor-pointer transition-all ${currentConversationId === conv.id
              ? 'bg-blue-500/10 text-blue-400' // Active state
              : 'text-gemini-text-secondary hover:bg-gemini-hover hover:text-gemini-text-primary'
              }`}
          >
            <div className="flex-1 min-w-0 pr-2">
              <p className="text-sm truncate font-medium">{conv.title}</p>
            </div>

            {/* Delete Action (visible on hover) */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteConversation(conv.id);
              }}
              className="opacity-0 group-hover:opacity-100 p-1 text-gemini-text-secondary hover:text-red-400 transition-all rounded hover:bg-gemini-hover"
              title="Delete conversation"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        ))}
        {conversations.length === 0 && (
          <div className="px-4 py-8 text-center text-sm text-gemini-text-secondary opacity-60">
            No history
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gemini-border">
        <div className="text-xs text-gemini-text-secondary flex justify-between items-center">
          <span>LangChain Local</span>
          <span className="bg-gemini-hover px-2 py-1 rounded text-[10px]">{conversations.length} chats</span>
        </div>
      </div>
    </div>
  );
};
