import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Message } from '../types';
import { CodeBlock } from './CodeBlock';

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
                  const { children, className } = props;
                  const inline = !className;

                  return (
                    <CodeBlock
                      className={className}
                      inline={inline}
                    >
                      {String(children).replace(/\n$/, '')}
                    </CodeBlock>
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
