import React, { useState, useEffect, useRef } from 'react';
import { Message, ToolUsage } from '../types/chat';
import { chatApi } from '../services/api';
import ToolUsageIndicator from './ToolUsageIndicator';

const SimpleChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
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
      id: Date.now().toString(),
      content: `Bonjour ! Je suis votre assistant pour le Château de Versailles. Comment puis-je vous aider à planifier votre visite ?

Je peux vous renseigner sur :
• La météo et les conditions de visite 🌤️
• Les itinéraires et temps de trajet 🗺️
• Les différents moyens de transport 🚌🚗🚴‍♂️
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

  const addMessage = (content: string, isUser: boolean, isError: boolean = false, toolsUsed?: ToolUsage[]): Message => {
    const message: Message = {
      id: Date.now().toString() + Math.random(),
      content,
      isUser,
      timestamp: new Date(),
      isError,
      toolsUsed
    };

    setMessages(prev => [...prev, message]);
    return message;
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const messageContent = input.trim();
    setInput('');

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
        addMessage(response.reponse || 'Réponse reçue', false, false, response.tools_used);
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
    setInput(suggestion);
  };

  const suggestions = [
    "Quel temps fait-il à Versailles aujourd'hui ?",
    "Comment aller à Versailles depuis Paris Gare du Nord ?",
    "Je visite Versailles en famille demain",
    "Combien de temps faut-il depuis l'aéroport CDG ?",
    "Quel est le meilleur moment pour visiter ?",
    "Comment se rendre à Versailles depuis la Tour Eiffel ?"
  ];

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="header-content">
          <div className="header-title">
            <span className="castle-icon">🏰</span>
            <div>
              <h1>Assistant Château de Versailles</h1>
              <p>Votre guide personnel pour une visite inoubliable</p>
            </div>
          </div>

          <div className="status-indicator">
            {connectionStatus === 'connected' ? (
              <>
                <span className="status-dot status-connected"></span>
                <span>Connecté</span>
              </>
            ) : connectionStatus === 'disconnected' ? (
              <>
                <span className="status-dot status-disconnected"></span>
                <span>Déconnecté</span>
              </>
            ) : (
              <span>Connexion...</span>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.isUser ? 'user' : 'bot'} ${message.isError ? 'error' : ''}`}>
            <div className="message-avatar">
              {message.isUser ? '👤' : '🤖'}
            </div>
            <div className="message-bubble">
              <div className="message-content">
                {message.content.split('\n').map((line, index) => (
                  <React.Fragment key={index}>
                    {line}
                    {index < message.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
              {message.toolsUsed && message.toolsUsed.length > 0 && (
                <ToolUsageIndicator toolsUsed={message.toolsUsed} />
              )}
              <div className="message-time">
                {message.timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {messages.length === 1 && (
          <div className="suggestions">
            <p>Suggestions rapides :</p>
            <div className="suggestion-buttons">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="suggestion-btn"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {isTyping && (
          <div className="typing-indicator">
            <div className="message-avatar">🤖</div>
            <div className="typing-content">
              <span>Assistant écrit</span>
              <div className="typing-dots">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        <form onSubmit={handleSendMessage} className="input-group">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tapez votre question ici..."
            disabled={isLoading}
            rows={1}
            maxLength={500}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(e);
              }
            }}
          />
          <button type="submit" disabled={!input.trim() || isLoading}>
            {isLoading ? '⏳' : '➤'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SimpleChatContainer;