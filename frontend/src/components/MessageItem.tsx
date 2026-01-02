import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Message } from '../types';

interface MessageItemProps {
  message: Message;
}

export const MessageItem = ({ message }: MessageItemProps) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <div className={`py-6 px-4 ${isUser ? 'bg-chat-user' : isSystem ? 'bg-gray-700' : 'bg-chat-assistant'}`}>
      <div className="max-w-3xl mx-auto flex gap-4">
        <div className="flex-shrink-0 w-8 h-8 rounded-sm bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold">
          {isUser ? 'U' : isSystem ? 'S' : 'A'}
        </div>
        <div className="flex-1 text-gray-100 prose prose-invert max-w-none">
          {isUser || isSystem ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                code(props) {
                  const { children, className, ...rest } = props;
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <code className={`${className} block bg-gray-800 p-4 rounded-lg overflow-x-auto`} {...rest}>
                      {children}
                    </code>
                  ) : (
                    <code className="bg-gray-800 px-1 py-0.5 rounded text-sm" {...rest}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
};
