import React from 'react';
import { Message } from '../types/chat';
import { AlertCircle, User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  // Custom components for markdown rendering
  const markdownComponents = {
    // Make all links open in new tabs
    a: ({ node, ...props }: any) => (
      <a
        {...props}
        target="_blank"
        rel="noopener noreferrer"
        className={message.isUser ? 'text-blue-100 underline hover:text-white' : 'text-blue-600 underline hover:text-blue-800'}
      />
    ),
    // Style lists
    ul: ({ node, ...props }: any) => (
      <ul {...props} className="list-disc list-inside space-y-1" />
    ),
    ol: ({ node, ...props }: any) => (
      <ol {...props} className="list-decimal list-inside space-y-1" />
    ),
    // Style code blocks
    code: ({ node, inline, ...props }: any) =>
      inline ? (
        <code
          {...props}
          className={`px-1 py-0.5 rounded text-xs font-mono ${
            message.isUser
              ? 'bg-blue-700 text-blue-100'
              : 'bg-gray-100 text-gray-800'
          }`}
        />
      ) : (
        <code
          {...props}
          className={`block px-3 py-2 rounded text-xs font-mono whitespace-pre-wrap ${
            message.isUser
              ? 'bg-blue-700 text-blue-100'
              : 'bg-gray-100 text-gray-800'
          }`}
        />
      ),
    // Style paragraphs
    p: ({ node, ...props }: any) => (
      <p {...props} className="mb-2 last:mb-0" />
    ),
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (message.isError) {
    return (
      <div className="flex items-start space-x-3 mb-4">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
            <AlertCircle className="w-4 h-4 text-red-600" />
          </div>
        </div>
        <div className="flex-1">
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="text-red-800 text-sm prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={markdownComponents}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
          <span className="text-xs text-gray-500 mt-1 block">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-start space-x-3 mb-4 ${
      message.isUser ? 'flex-row-reverse space-x-reverse' : ''
    }`}>
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          message.isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-600'
        }`}>
          {message.isUser ? (
            <User className="w-4 h-4" />
          ) : (
            <Bot className="w-4 h-4" />
          )}
        </div>
      </div>

      <div className="flex-1 max-w-xs sm:max-w-md md:max-w-lg">
        <div className={`rounded-lg p-3 ${
          message.isUser
            ? 'bg-blue-600 text-white ml-auto'
            : 'bg-white border border-gray-200 text-gray-800'
        }`}>
          <div className="text-sm leading-relaxed prose prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={markdownComponents}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>
        <span className={`text-xs text-gray-500 mt-1 block ${
          message.isUser ? 'text-right' : 'text-left'
        }`}>
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
};

export default ChatMessage;