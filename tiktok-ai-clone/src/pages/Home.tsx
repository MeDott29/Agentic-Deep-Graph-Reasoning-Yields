import VideoFeed from '../components/VideoFeed';
import styled from '@emotion/styled';

const HomeContainer = styled.div`
  height: 100vh;
  overflow: hidden;
`;

const Home = () => {
  return (
    <HomeContainer>
      <VideoFeed />
    </HomeContainer>
  );
};

export default Home; 