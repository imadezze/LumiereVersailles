import React from 'react';
import { ToolUsage } from '../types/chat';

interface ToolUsageIndicatorProps {
  toolsUsed: ToolUsage[];
}

const ToolUsageIndicator: React.FC<ToolUsageIndicatorProps> = ({ toolsUsed }) => {
  if (!toolsUsed || toolsUsed.length === 0) {
    return null;
  }

  const getToolIcon = (toolName: string): string => {
    if (toolName.includes('weather')) {
      return '🌤️';
    } else if (toolName.includes('travel')) {
      return '🗺️';
    } else if (toolName.includes('knowledge') || toolName.includes('search_versailles')) {
      return '📚';
    } else if (toolName.includes('versailles')) {
      return '🏰';
    }
    return '🔧';
  };

  const getToolDisplayName = (toolName: string): string => {
    if (toolName.includes('weather')) {
      return 'Météo';
    } else if (toolName.includes('travel')) {
      return 'Itinéraire';
    } else if (toolName.includes('knowledge') || toolName.includes('search_versailles')) {
      return 'Base de connaissances';
    } else if (toolName.includes('versailles')) {
      return 'Versailles';
    }
    return toolName;
  };

  const formatArgs = (args: Record<string, any>): string => {
    const entries = Object.entries(args);
    if (entries.length === 0) return '';

    return entries
      .map(([key, value]) => {
        if (key === 'visit_date') return `📅 ${value}`;
        if (key === 'origin_address') return `📍 De ${value}`;
        if (key === 'compare_modes') return value ? '🚌🚗🚴‍♂️🚶‍♂️' : '';
        if (key === 'query') return `🔍 "${value}"`;
        if (key === 'max_results') return `📊 ${value} résultats`;
        return `${key}: ${value}`;
      })
      .filter(Boolean)
      .join(' • ');
  };

  const getToolType = (toolName: string): string => {
    if (toolName.includes('knowledge') || toolName.includes('search_versailles')) {
      return 'knowledge';
    } else if (toolName.includes('weather')) {
      return 'weather';
    } else if (toolName.includes('travel')) {
      return 'travel';
    }
    return 'other';
  };

  return (
    <div className="tool-usage-indicator">
      <div className="tool-usage-header">
        <span className="tools-icon">🛠️</span>
        <span className="tools-text">Outils utilisés :</span>
      </div>
      <div className="tool-list">
        {toolsUsed.map((tool, index) => (
          <div key={index} className="tool-item" data-tool-type={getToolType(tool.name)}>
            <span className="tool-icon">{getToolIcon(tool.name)}</span>
            <span className="tool-name">{getToolDisplayName(tool.name)}</span>
            {tool.args && Object.keys(tool.args).length > 0 && (
              <span className="tool-args">({formatArgs(tool.args)})</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ToolUsageIndicator;