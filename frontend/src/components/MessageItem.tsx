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
    <div className={`py-4 px-4 ${isUser ? '' : ''}`}>
      <div className={`max-w-4xl mx-auto flex gap-6 ${isUser ? 'flex-row-reverse' : ''}`}>

        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center 
            ${isUser ? 'bg-gemini-surface' : isSystem ? 'bg-red-900/20 text-red-400' : ''}
            ${!isUser && !isSystem ? 'bg-transparent' : ''}
        `}>
          {isUser ? (
            <svg className="w-5 h-5 text-gemini-text-secondary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          ) : isSystem ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          ) : (
            // Gemini star/sparkle icon
            <svg className="w-6 h-6 text-gemini-primary animate-pulse" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="currentColor" stroke="none" />
            </svg>
          )}
        </div>

        {/* Content */}
        <div className={`flex-1 text-gemini-text-primary overflow-hidden
             ${isUser
            ? 'bg-gemini-surface rounded-2xl rounded-tr-sm px-5 py-3 text-right'
            : 'bg-transparent prose prose-invert prose-p:leading-relaxed prose-pre:bg-gemini-surface prose-pre:rounded-xl max-w-none'
          }
        `}>
          {isUser || isSystem ? (
            <p className={`whitespace-pre-wrap ${isUser ? 'text-gemini-text-primary' : 'text-red-400 font-mono text-sm'}`}>
              {message.content}
            </p>
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
                      className={`${className}`}
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
