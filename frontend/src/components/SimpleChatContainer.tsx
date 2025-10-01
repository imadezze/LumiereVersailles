import React, { useState, useEffect, useRef } from 'react';
import { Message, ToolUsage } from '../types/chat';
import { chatApi } from '../services/api';
import ToolUsageIndicator from './ToolUsageIndicator';
import VoiceRecorder from './VoiceRecorder';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const SimpleChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [isClearingConversation, setIsClearingConversation] = useState(false);
  const [conversationId] = useState(() => `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Markdown components factory - determines styling based on message type
  const getMarkdownComponents = (isUser: boolean) => ({
    // Make all links open in new tabs with appropriate styling
    a: ({ node, ...props }: any) => (
      <a
        {...props}
        target="_blank"
        rel="noopener noreferrer"
        className={isUser ? 'message-link' : 'message-link'}
        style={{
          color: isUser ? '#ffffff' : '#3498db',
          textDecoration: 'underline',
          wordBreak: 'break-all'
        }}
      />
    ),
    // Style lists with appropriate spacing
    ul: ({ node, ...props }: any) => (
      <ul {...props} style={{ listStyleType: 'disc', paddingLeft: '1.5rem', margin: '0.5rem 0' }} />
    ),
    ol: ({ node, ...props }: any) => (
      <ol {...props} style={{ listStyleType: 'decimal', paddingLeft: '1.5rem', margin: '0.5rem 0' }} />
    ),
    li: ({ node, ...props }: any) => (
      <li {...props} style={{ marginBottom: '0.25rem' }} />
    ),
    // Style paragraphs to avoid excessive spacing
    p: ({ node, ...props }: any) => (
      <p {...props} style={{ margin: '0.5rem 0' }} />
    ),
    // Style code blocks
    code: ({ node, inline, ...props }: any) =>
      inline ? (
        <code
          {...props}
          style={{
            backgroundColor: isUser ? 'rgba(255, 255, 255, 0.2)' : '#f3f4f6',
            padding: '0.125rem 0.25rem',
            borderRadius: '0.25rem',
            fontSize: '0.875rem',
            fontFamily: 'monospace'
          }}
        />
      ) : (
        <code
          {...props}
          style={{
            display: 'block',
            backgroundColor: isUser ? 'rgba(255, 255, 255, 0.2)' : '#f3f4f6',
            padding: '0.75rem',
            borderRadius: '0.25rem',
            fontSize: '0.875rem',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            margin: '0.5rem 0'
          }}
        />
      ),
    // Style headings if needed
    h1: ({ node, ...props }: any) => (
      <h1 {...props} style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: '0.75rem 0' }} />
    ),
    h2: ({ node, ...props }: any) => (
      <h2 {...props} style={{ fontSize: '1.125rem', fontWeight: 'bold', margin: '0.75rem 0' }} />
    ),
    h3: ({ node, ...props }: any) => (
      <h3 {...props} style={{ fontSize: '1rem', fontWeight: 'bold', margin: '0.5rem 0' }} />
    ),
    // Style strong/bold
    strong: ({ node, ...props }: any) => (
      <strong {...props} style={{ fontWeight: 'bold' }} />
    ),
    // Style em/italic
    em: ({ node, ...props }: any) => (
      <em {...props} style={{ fontStyle: 'italic' }} />
    ),
  });

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

**Je peux vous renseigner sur :**

- 📚 L'histoire et les informations sur le château
- 🔍 Les événements et actualités en temps réel
- 🌤️ La météo et les conditions de visite
- 🗺️ Les itinéraires et temps de trajet
- 🚌 Les différents moyens de transport
- 🎫 Les billets, tarifs et horaires
- 🌳 Les jardins, fontaines et événements
- ✨ Les recommandations selon votre profil`,
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

  const handleVoiceTranscript = async (transcript: string) => {
    if (!transcript.trim() || isLoading) return;

    // Add user message
    addMessage(transcript, true);

    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await chatApi.sendMessage({
        message: transcript,
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

  const handleVoiceError = (error: string) => {
    addMessage(
      `❌ Erreur d'enregistrement vocal : ${error}`,
      false,
      true
    );
  };

  const handleNewConversation = async () => {
    if (isClearingConversation) return; // Prevent double clicks

    setIsClearingConversation(true);

    try {
      // Call backend to clear conversation history (both backend storage and agent memory)
      await chatApi.clearConversation(conversationId);
      console.log('🔄 New conversation started - Backend and agent history cleared');
    } catch (error) {
      console.warn('Failed to clear backend conversation:', error);
      // Continue anyway - frontend still gets cleared
    }

    // Clear all messages and show welcome message
    const welcomeMessage: Message = {
      id: Date.now().toString(),
      content: `Bonjour ! Je suis votre assistant pour le Château de Versailles. Comment puis-je vous aider à planifier votre visite ?

**Je peux vous renseigner sur :**

- 📚 L'histoire et les informations sur le château
- 🔍 Les événements et actualités en temps réel
- 🌤️ La météo et les conditions de visite
- 🗺️ Les itinéraires et temps de trajet
- 🚌 Les différents moyens de transport
- 🎫 Les billets, tarifs et horaires
- 🌳 Les jardins, fontaines et événements
- ✨ Les recommandations selon votre profil`,
      isUser: false,
      timestamp: new Date()
    };

    setMessages([welcomeMessage]);
    setIsClearingConversation(false);
  };

  const suggestions = [
    "Parle-moi de l'histoire du Château de Versailles",
    "Quel temps fait-il à Versailles aujourd'hui ?",
    "Quels sont les horaires d'ouverture ?",
    "Comment aller à Versailles depuis Paris Gare du Nord ?",
    "Je visite Versailles en famille demain",
    "Quel est le meilleur moment pour visiter ?"
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

          <div className="header-actions">
            <button
              onClick={handleNewConversation}
              className="new-conversation-btn"
              title="Nouvelle conversation"
              disabled={isClearingConversation}
            >
              {isClearingConversation ? '⏳ Nettoyage...' : '🔄 Nouvelle conversation'}
            </button>

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
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={getMarkdownComponents(message.isUser)}
                >
                  {message.content}
                </ReactMarkdown>
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
          <VoiceRecorder
            onTranscript={handleVoiceTranscript}
            onError={handleVoiceError}
            disabled={isLoading}
          />
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tapez votre question ou utilisez le micro..."
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