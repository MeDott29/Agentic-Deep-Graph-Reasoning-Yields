import { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import AgentNetwork from '../components/AgentNetwork';
import { generateAgentNetwork, AgentPersonality } from '../services/openaiService';

const DiscoverContainer = styled.div`
  padding: 80px 20px 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const SearchContainer = styled.div`
  margin-bottom: 24px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
  }
`;

const CategoriesContainer = styled.div`
  margin-bottom: 32px;
`;

const CategoryTitle = styled.h2`
  font-size: 20px;
  margin-bottom: 16px;
`;

const CategoryScroll = styled.div`
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 12px;
  
  &::-webkit-scrollbar {
    height: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--text-secondary);
    border-radius: 4px;
  }
`;

// Base category item without isActive prop
const BaseCategoryItem = styled.div`
  padding: 8px 16px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
`;

const ActiveCategoryItem = styled(BaseCategoryItem)`
  background-color: var(--primary);
  color: white;
  
  &:hover {
    background-color: var(--primary);
  }
`;

const InactiveCategoryItem = styled(BaseCategoryItem)`
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  
  &:hover {
    background-color: #e6e6e6;
  }
`;

// Custom CategoryItem component that doesn't pass isActive to DOM
const CategoryItem = ({ isActive, onClick, children }) => {
  if (isActive) {
    return <ActiveCategoryItem onClick={onClick}>{children}</ActiveCategoryItem>;
  }
  return <InactiveCategoryItem onClick={onClick}>{children}</InactiveCategoryItem>;
};

const TrendingContainer = styled.div`
  margin-bottom: 32px;
`;

const TrendingTitle = styled.h2`
  font-size: 20px;
  margin-bottom: 16px;
`;

const TrendingGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
`;

const TrendingItem = styled.div`
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const TrendingThumbnail = styled.div`
  aspect-ratio: 9/16;
  background-color: var(--bg-secondary);
  position: relative;
`;

const TrendingInfo = styled.div`
  padding: 12px;
`;

const TrendingHashtag = styled.h3`
  font-size: 16px;
  margin-bottom: 4px;
`;

const TrendingCount = styled.p`
  font-size: 14px;
  color: var(--text-secondary);
`;

const NetworkContainer = styled.div`
  margin-bottom: 32px;
`;

const NetworkTitle = styled.h2`
  font-size: 20px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
`;

const NetworkIcon = styled.span`
  margin-right: 8px;
  color: var(--primary);
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  background-color: var(--bg-secondary);
  border-radius: 12px;
`;

const AgentInfoCard = styled.div`
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const AgentHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 12px;
`;

const AgentAvatar = styled.div<{ color: string }>`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: ${props => props.color};
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
`;

const AgentInfo = styled.div`
  flex: 1;
`;

const AgentName = styled.h3`
  margin: 0 0 4px;
  font-size: 18px;
`;

const AgentRole = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  text-transform: capitalize;
`;

const AgentBio = styled.p`
  margin: 0 0 16px;
  font-size: 14px;
  line-height: 1.5;
`;

const AgentInterests = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
`;

const InterestTag = styled.span`
  background-color: var(--bg-secondary);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
`;

const AgentQuirks = styled.div`
  margin-top: 16px;
`;

const QuirkTitle = styled.h4`
  font-size: 14px;
  margin: 0 0 8px;
  color: var(--text-secondary);
`;

const QuirkList = styled.ul`
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
`;

const QuirkItem = styled.li`
  margin-bottom: 4px;
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

const Discover = () => {
  const [activeCategory, setActiveCategory] = useState('For You');
  const [agents, setAgents] = useState<AgentPersonality[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AgentPersonality | null>(null);
  const [loading, setLoading] = useState(true);
  
  const categories = [
    'For You', 'AI', 'Technology', 'Dance', 'Comedy', 'Food', 'Fashion', 'Beauty', 
    'Sports', 'Animals', 'DIY', 'Music', 'Art', 'Travel', 'Education'
  ];
  
  const trendingHashtags = [
    { tag: '#AIcreator', count: '1.2B views' },
    { tag: '#virtualinfluencer', count: '856.7M views' },
    { tag: '#digitalart', count: '723.4M views' },
    { tag: '#AItrends', count: '512.9M views' },
    { tag: '#futureisnow', count: '498.3M views' },
    { tag: '#techinnovation', count: '345.6M views' },
    { tag: '#AIlearning', count: '287.1M views' },
    { tag: '#nextlevel', count: '256.8M views' },
  ];
  
  // Load agent network
  useEffect(() => {
    const loadAgentNetwork = async () => {
      try {
        setLoading(true);
        const network = await generateAgentNetwork(10);
        setAgents(network);
      } catch (error) {
        console.error('Error loading agent network:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadAgentNetwork();
  }, []);
  
  // Handle agent click
  const handleAgentClick = (agent: AgentPersonality) => {
    setSelectedAgent(agent);
  };
  
  return (
    <DiscoverContainer>
      <SearchContainer>
        <SearchInput placeholder="Search" />
      </SearchContainer>
      
      <NetworkContainer>
        <NetworkTitle>
          <NetworkIcon>🔄</NetworkIcon>
          AI Agent Network
        </NetworkTitle>
        
        {loading ? (
          <LoadingContainer>
            <div className="loading-spinner" />
          </LoadingContainer>
        ) : (
          <AgentNetwork agents={agents} onAgentClick={handleAgentClick} />
        )}
        
        {selectedAgent && (
          <AgentInfoCard>
            <AgentHeader>
              <AgentAvatar color={getAgentColor(selectedAgent.role)}>
                {getInitials(selectedAgent.name)}
              </AgentAvatar>
              <AgentInfo>
                <AgentName>{selectedAgent.name}</AgentName>
                <AgentRole>{selectedAgent.role}</AgentRole>
              </AgentInfo>
            </AgentHeader>
            
            <AgentBio>{selectedAgent.bio}</AgentBio>
            
            <AgentInterests>
              {selectedAgent.interests.map((interest, index) => (
                <InterestTag key={index}>{interest}</InterestTag>
              ))}
            </AgentInterests>
            
            <AgentQuirks>
              <QuirkTitle>Personality Quirks:</QuirkTitle>
              <QuirkList>
                {selectedAgent.quirks.map((quirk, index) => (
                  <QuirkItem key={index}>{quirk}</QuirkItem>
                ))}
              </QuirkList>
            </AgentQuirks>
          </AgentInfoCard>
        )}
      </NetworkContainer>
      
      <CategoriesContainer>
        <CategoryTitle>Categories</CategoryTitle>
        <CategoryScroll>
          {categories.map(category => (
            <CategoryItem 
              key={category} 
              isActive={category === activeCategory}
              onClick={() => setActiveCategory(category)}
            >
              {category}
            </CategoryItem>
          ))}
        </CategoryScroll>
      </CategoriesContainer>
      
      <TrendingContainer>
        <TrendingTitle>Trending Hashtags</TrendingTitle>
        <TrendingGrid>
          {trendingHashtags.map(item => (
            <TrendingItem key={item.tag}>
              <TrendingThumbnail />
              <TrendingInfo>
                <TrendingHashtag>{item.tag}</TrendingHashtag>
                <TrendingCount>{item.count}</TrendingCount>
              </TrendingInfo>
            </TrendingItem>
          ))}
        </TrendingGrid>
      </TrendingContainer>
    </DiscoverContainer>
  );
};

export default Discover; 