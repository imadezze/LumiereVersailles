import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Castle, Wifi, WifiOff } from 'lucide-react';
import { Message } from '../types/chat';
import { chatApi } from '../services/api';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';
import ChatInput from './ChatInput';
import QuickSuggestions from './QuickSuggestions';

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [conversationId] = useState(() => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    // Add welcome message
    const welcomeMessage: Message = {
      id: uuidv4(),
      content: `Bonjour ! Je suis votre assistant pour le Château de Versailles. Comment puis-je vous aider à planifier votre visite ?

Je peux vous renseigner sur :
• La météo et les conditions de visite
• Les itinéraires personnalisés
• Les billets et tarifs
• Les recommandations selon votre profil`,
      isUser: false,
      timestamp: new Date()
    };

    setMessages([welcomeMessage]);

    // Check backend connection
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      await chatApi.checkHealth();
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
      console.error('Backend connection failed:', error);
    }
  };

  const addMessage = (content: string, isUser: boolean, isError: boolean = false): Message => {
    const message: Message = {
      id: uuidv4(),
      content,
      isUser,
      timestamp: new Date(),
      isError
    };

    setMessages(prev => [...prev, message]);
    return message;
  };

  const handleSendMessage = async (messageContent: string) => {
    if (!messageContent.trim()) return;

    // Add user message
    addMessage(messageContent, true);

    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await chatApi.sendMessage({
        message: messageContent,
        conversation_id: conversationId
      });

      // Small delay for better UX
      setTimeout(() => {
        setIsTyping(false);
        addMessage(response.reponse || 'Réponse reçue', false);
      }, 500);

    } catch (error: any) {
      setIsTyping(false);
      addMessage(
        error.message || 'Désolé, je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants.',
        false,
        true
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 to-purple-900 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Castle className="w-8 h-8" />
            <div>
              <h1 className="text-xl font-bold">Assistant Château de Versailles</h1>
              <p className="text-sm opacity-90">Votre guide personnel pour une visite inoubliable</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {connectionStatus === 'connected' ? (
              <>
                <Wifi className="w-4 h-4 text-green-400" />
                <span className="text-xs text-green-400">Connecté</span>
              </>
            ) : connectionStatus === 'disconnected' ? (
              <>
                <WifiOff className="w-4 h-4 text-red-400" />
                <span className="text-xs text-red-400">Déconnecté</span>
              </>
            ) : (
              <span className="text-xs text-yellow-400">Connexion...</span>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {messages.length === 1 && (
          <QuickSuggestions onSuggestionClick={handleSuggestionClick} />
        )}

        {isTyping && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatContainer;