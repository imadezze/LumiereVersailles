import React from 'react';
import { Cloud, Users, Euro, Clock } from 'lucide-react';

interface QuickSuggestionsProps {
  onSuggestionClick: (suggestion: string) => void;
}

const QuickSuggestions: React.FC<QuickSuggestionsProps> = ({ onSuggestionClick }) => {
  const suggestions = [
    {
      text: "Quel temps fait-il à Versailles aujourd'hui ?",
      icon: <Cloud className="w-4 h-4" />,
      label: "Météo"
    },
    {
      text: "Je visite Versailles en famille demain",
      icon: <Users className="w-4 h-4" />,
      label: "Visite famille"
    },
    {
      text: "Combien coûtent les billets ?",
      icon: <Euro className="w-4 h-4" />,
      label: "Tarifs"
    },
    {
      text: "Quel est le meilleur moment pour visiter ?",
      icon: <Clock className="w-4 h-4" />,
      label: "Conseils timing"
    }
  ];

  return (
    <div className="mb-4">
      <p className="text-sm text-gray-600 mb-2">Suggestions rapides :</p>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSuggestionClick(suggestion.text)}
            className="flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 transition-colors duration-200 rounded-full px-3 py-2 text-sm text-gray-700 border border-gray-200"
          >
            {suggestion.icon}
            <span>{suggestion.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickSuggestions;