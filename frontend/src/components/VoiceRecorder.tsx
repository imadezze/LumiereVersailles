import React, { useState, useRef, useEffect } from 'react';

interface VoiceRecorderProps {
  onTranscript: (transcript: string) => void;
  onError: (error: string) => void;
  disabled?: boolean;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ onTranscript, onError, disabled = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const mimeTypeRef = useRef<string>('');

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const getSupportedMimeType = (): string => {
    // List of mime types to try, in order of preference
    const mimeTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/ogg',
      'audio/wav',
    ];

    // Find the first supported mime type
    for (const mimeType of mimeTypes) {
      if (MediaRecorder.isTypeSupported(mimeType)) {
        return mimeType;
      }
    }

    // Fallback to empty string (browser will use default)
    return '';
  };

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Get supported mime type for this browser
      const mimeType = getSupportedMimeType();
      mimeTypeRef.current = mimeType;

      console.log('🎤 Using mime type:', mimeType || 'browser default');

      // Create MediaRecorder instance
      const mediaRecorder = new MediaRecorder(stream,
        mimeType ? { mimeType } : undefined
      );

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Collect audio data
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = async () => {
        // Stop all audio tracks
        stream.getTracks().forEach(track => track.stop());

        // Create audio blob from chunks using the recorded mime type
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mimeTypeRef.current || 'audio/webm'
        });

        console.log('🎙️ Created audio blob:', {
          size: audioBlob.size,
          type: audioBlob.type
        });

        // Send to transcription
        await transcribeAudio(audioBlob);
      };

      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error: any) {
      console.error('Error starting recording:', error);
      onError(error.message || 'Impossible d\'accéder au microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      // Import the API function dynamically to avoid circular dependencies
      const { chatApi } = await import('../services/api');

      const result = await chatApi.transcribeAudio(audioBlob);

      if (result.transcript && result.transcript.trim()) {
        onTranscript(result.transcript);
      } else {
        onError('Aucun texte détecté dans l\'enregistrement');
      }
    } catch (error: any) {
      console.error('Transcription error:', error);
      onError(error.message || 'Erreur lors de la transcription');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isProcessing}
      className={`voice-recorder-btn ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
      title={isRecording ? 'Arrêter l\'enregistrement' : 'Enregistrer un message vocal'}
      type="button"
    >
      {isProcessing ? (
        <span className="processing-icon">⏳</span>
      ) : isRecording ? (
        <span className="recording-icon">⏹️</span>
      ) : (
        <span className="mic-icon">🎤</span>
      )}
    </button>
  );
};

export default VoiceRecorder;