import styled from '@emotion/styled';

const ProfileContainer = styled.div`
  padding: 80px 20px 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const ProfileHeader = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
`;

const Avatar = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 40px;
  font-weight: bold;
  margin-bottom: 16px;
`;

const Username = styled.h1`
  font-size: 24px;
  margin-bottom: 8px;
`;

const Stats = styled.div`
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const StatValue = styled.span`
  font-size: 18px;
  font-weight: bold;
`;

const StatLabel = styled.span`
  font-size: 14px;
  color: var(--text-secondary);
`;

const Bio = styled.p`
  text-align: center;
  margin-bottom: 24px;
  max-width: 400px;
`;

const EditProfileButton = styled.button`
  background-color: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    background-color: var(--bg-secondary);
  }
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 24px;
`;

// Base tab without isActive prop
const BaseTab = styled.button`
  flex: 1;
  padding: 16px;
  background: none;
  border: none;
  cursor: pointer;
`;

const ActiveTab = styled(BaseTab)`
  border-bottom: 2px solid var(--primary);
  color: var(--primary);
  font-weight: 600;
`;

const InactiveTab = styled(BaseTab)`
  border-bottom: none;
  color: var(--text-secondary);
  font-weight: 400;
`;

// Custom Tab component that doesn't pass isActive to DOM
const Tab = ({ isActive, onClick, children }) => {
  if (isActive) {
    return <ActiveTab onClick={onClick}>{children}</ActiveTab>;
  }
  return <InactiveTab onClick={onClick}>{children}</InactiveTab>;
};

const VideoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 2px;
`;

const VideoThumbnail = styled.div`
  aspect-ratio: 9/16;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  
  &:hover {
    opacity: 0.9;
  }
`;

const ThumbnailOverlay = styled.div`
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  align-items: center;
  color: white;
  font-size: 14px;
`;

const ViewCount = styled.span`
  margin-left: 4px;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
`;

const EmptyStateTitle = styled.h3`
  font-size: 20px;
  margin-bottom: 8px;
`;

const EmptyStateText = styled.p`
  color: var(--text-secondary);
  margin-bottom: 24px;
`;

const CreateButton = styled.button`
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    opacity: 0.9;
  }
`;

const Profile = () => {
  return (
    <ProfileContainer>
      <ProfileHeader>
        <Avatar>AI</Avatar>
        <Username>ai_creator</Username>
        <Stats>
          <StatItem>
            <StatValue>125</StatValue>
            <StatLabel>Following</StatLabel>
          </StatItem>
          <StatItem>
            <StatValue>10.5K</StatValue>
            <StatLabel>Followers</StatLabel>
          </StatItem>
          <StatItem>
            <StatValue>1.2M</StatValue>
            <StatLabel>Likes</StatLabel>
          </StatItem>
        </Stats>
        <Bio>
          AI-generated content creator | Exploring the future of digital creativity
        </Bio>
        <EditProfileButton>Edit Profile</EditProfileButton>
      </ProfileHeader>
      
      <TabsContainer>
        <Tab isActive={true}>Videos</Tab>
        <Tab isActive={false}>Liked</Tab>
      </TabsContainer>
      
      <EmptyState>
        <EmptyStateTitle>No videos yet</EmptyStateTitle>
        <EmptyStateText>
          Your AI-generated videos will appear here. Start creating!
        </EmptyStateText>
        <CreateButton>Create New Video</CreateButton>
      </EmptyState>
    </ProfileContainer>
  );
};

export default Profile;

 