import React from 'react';
import { Message } from '../types/chat';
import { AlertCircle, User, Bot } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const formatContent = (content: string) => {
    return content
      .split('\n')
      .map((line, index) => (
        <React.Fragment key={index}>
          {line}
          {index < content.split('\n').length - 1 && <br />}
        </React.Fragment>
      ));
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
            <p className="text-red-800 text-sm">
              {formatContent(message.content)}
            </p>
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
          <p className="text-sm leading-relaxed">
            {formatContent(message.content)}
          </p>
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