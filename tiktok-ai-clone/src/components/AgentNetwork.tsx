import { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';
import { motion } from 'framer-motion';
import { AgentPersonality } from '../services/openaiService';

interface AgentNetworkProps {
  agents: AgentPersonality[];
  onAgentClick?: (agent: AgentPersonality) => void;
}

const NetworkContainer = styled.div`
  width: 100%;
  height: 300px;
  position: relative;
  margin: 20px 0;
  overflow: hidden;
  border-radius: 12px;
  background-color: rgba(0, 0, 0, 0.05);
`;

const AgentNode = styled(motion.div)<{ size: number; color: string }>`
  position: absolute;
  width: ${props => props.size}px;
  height: ${props => props.size}px;
  border-radius: 50%;
  background-color: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: ${props => props.size / 3}px;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 2;
`;

const ConnectionLine = styled.svg`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
`;

const AgentTooltip = styled(motion.div)`
  position: absolute;
  background-color: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 200px;
  z-index: 3;
`;

const TooltipHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 8px;
`;

const TooltipAvatar = styled.div<{ color: string }>`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: ${props => props.color};
  margin-right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  font-weight: bold;
`;

const TooltipName = styled.h4`
  margin: 0;
  font-size: 14px;
`;

const TooltipRole = styled.span`
  font-size: 12px;
  color: #666;
  margin-left: 4px;
`;

const TooltipBio = styled.p`
  margin: 8px 0;
  font-size: 12px;
  line-height: 1.4;
`;

const TooltipInterests = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
`;

const InterestTag = styled.span`
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  color: #666;
`;

// Get a color based on agent role
const getAgentColor = (role: string): string => {
  const colors: Record<string, string> = {
    creator: '#FE2C55',
    commenter: '#25F4EE',
    trendsetter: '#8A2BE2',
    critic: '#FF8C00',
    collaborator: '#1DB954',
  };
  
  return colors[role.toLowerCase()] || '#888888';
};

// Get initials from name
const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
};

const AgentNetwork: React.FC<AgentNetworkProps> = ({ agents, onAgentClick }) => {
  const [positions, setPositions] = useState<{ x: number; y: number }[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Calculate positions for agents in a network-like visualization
  useEffect(() => {
    if (!containerRef.current) return;
    
    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;
    const center = { x: width / 2, y: height / 2 };
    const radius = Math.min(width, height) * 0.35;
    
    // Position agents in a circle
    const newPositions = agents.map((_, index) => {
      const angle = (index / agents.length) * Math.PI * 2;
      // Add some randomness to make it look more organic
      const randomRadius = radius * (0.8 + Math.random() * 0.4);
      return {
        x: center.x + Math.cos(angle) * randomRadius,
        y: center.y + Math.sin(angle) * randomRadius,
      };
    });
    
    setPositions(newPositions);
  }, [agents, containerRef]);
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      const center = { x: width / 2, y: height / 2 };
      const radius = Math.min(width, height) * 0.35;
      
      const newPositions = agents.map((_, index) => {
        const angle = (index / agents.length) * Math.PI * 2;
        const randomRadius = radius * (0.8 + Math.random() * 0.4);
        return {
          x: center.x + Math.cos(angle) * randomRadius,
          y: center.y + Math.sin(angle) * randomRadius,
        };
      });
      
      setPositions(newPositions);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [agents]);
  
  // Handle agent click
  const handleAgentClick = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (selectedAgent === index) {
      setSelectedAgent(null);
      return;
    }
    
    setSelectedAgent(index);
    
    // Calculate tooltip position
    const rect = (e.target as HTMLElement).getBoundingClientRect();
    const containerRect = containerRef.current?.getBoundingClientRect() || { left: 0, top: 0 };
    
    setTooltipPosition({
      x: rect.left - containerRect.left + rect.width / 2,
      y: rect.top - containerRect.top,
    });
    
    // Call onAgentClick if provided
    if (onAgentClick) {
      onAgentClick(agents[index]);
    }
  };
  
  // Close tooltip when clicking outside
  const handleContainerClick = () => {
    setSelectedAgent(null);
  };
  
  return (
    <NetworkContainer ref={containerRef} onClick={handleContainerClick}>
      {/* Connection lines between agents */}
      <ConnectionLine>
        {positions.length > 0 &&
          agents.map((agent, i) => {
            // Connect each agent to 2-3 others
            const connections = [];
            const numConnections = 2 + Math.floor(Math.random() * 2);
            
            for (let j = 0; j < numConnections; j++) {
              // Connect to a random agent that isn't self
              const targetIndex = (i + 1 + Math.floor(Math.random() * (agents.length - 1))) % agents.length;
              
              if (positions[targetIndex]) {
                connections.push(
                  <line
                    key={`${i}-${targetIndex}`}
                    x1={positions[i].x}
                    y1={positions[i].y}
                    x2={positions[targetIndex].x}
                    y2={positions[targetIndex].y}
                    stroke={getAgentColor(agent.role)}
                    strokeWidth="1"
                    strokeOpacity="0.3"
                  />
                );
              }
            }
            
            return connections;
          })}
      </ConnectionLine>
      
      {/* Agent nodes */}
      {positions.length > 0 &&
        agents.map((agent, index) => {
          const size = 40 + (agent.role === 'creator' ? 10 : 0);
          const color = getAgentColor(agent.role);
          
          return (
            <AgentNode
              key={index}
              size={size}
              color={color}
              initial={{ scale: 0 }}
              animate={{ scale: 1, x: positions[index].x - size / 2, y: positions[index].y - size / 2 }}
              transition={{ delay: index * 0.1 }}
              onClick={(e) => handleAgentClick(index, e)}
              whileHover={{ scale: 1.1 }}
            >
              {getInitials(agent.name)}
            </AgentNode>
          );
        })}
      
      {/* Agent tooltip */}
      {selectedAgent !== null && positions[selectedAgent] && (
        <AgentTooltip
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          style={{
            left: tooltipPosition.x,
            top: tooltipPosition.y + 30,
            transform: 'translateX(-50%)',
          }}
        >
          <TooltipHeader>
            <TooltipAvatar color={getAgentColor(agents[selectedAgent].role)}>
              {getInitials(agents[selectedAgent].name)}
            </TooltipAvatar>
            <TooltipName>
              {agents[selectedAgent].name}
              <TooltipRole>({agents[selectedAgent].role})</TooltipRole>
            </TooltipName>
          </TooltipHeader>
          
          <TooltipBio>{agents[selectedAgent].bio}</TooltipBio>
          
          <TooltipInterests>
            {agents[selectedAgent].interests.map((interest, i) => (
              <InterestTag key={i}>{interest}</InterestTag>
            ))}
          </TooltipInterests>
        </AgentTooltip>
      )}
    </NetworkContainer>
  );
};

export default AgentNetwork; 