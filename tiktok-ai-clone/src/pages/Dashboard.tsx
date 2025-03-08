import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { 
  getUserBehaviorStats, 
  getVideoStats, 
  getInteractionStats,
  UserBehavior,
  AIVideo,
  UserInteraction
} from '../services/aiService';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const DashboardContainer = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f8f8f8;
  min-height: 100vh;
`;

const Header = styled.header`
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 28px;
  margin-bottom: 10px;
  color: #333;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #666;
  margin-bottom: 20px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
`;

const StatTitle = styled.h3`
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
`;

const StatValue = styled.div`
  font-size: 28px;
  font-weight: bold;
  color: #333;
`;

const ChartContainer = styled.div`
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
`;

const ChartTitle = styled.h3`
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
`;

const ChartGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
`;

const TableContainer = styled.div`
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.th`
  text-align: left;
  padding: 12px;
  border-bottom: 2px solid #eee;
  color: #666;
`;

const TableRow = styled.tr`
  &:nth-of-type(even) {
    background-color: #f9f9f9;
  }
  
  &:hover {
    background-color: #f0f0f0;
  }
`;

const TableCell = styled.td`
  padding: 12px;
  border-bottom: 1px solid #eee;
`;

const Dashboard = () => {
  const [userStats, setUserStats] = useState<any>(null);
  const [videoStats, setVideoStats] = useState<any>(null);
  const [interactionStats, setInteractionStats] = useState<any>(null);
  const [topVideos, setTopVideos] = useState<AIVideo[]>([]);
  const [recentInteractions, setRecentInteractions] = useState<UserInteraction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch all stats in parallel
        const [userStatsData, videoStatsData, interactionStatsData] = await Promise.all([
          getUserBehaviorStats(),
          getVideoStats(),
          getInteractionStats()
        ]);
        
        setUserStats(userStatsData);
        setVideoStats(videoStatsData);
        setInteractionStats(interactionStatsData);
        setTopVideos(videoStatsData.topVideos || []);
        setRecentInteractions(interactionStatsData.recentInteractions || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Prepare chart data
  const categoryData = {
    labels: userStats?.topCategories?.map((item: any) => item.category) || [],
    datasets: [
      {
        label: 'Category Popularity',
        data: userStats?.topCategories?.map((item: any) => item.count) || [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const interactionData = {
    labels: interactionStats?.byType?.map((item: any) => item.type) || [],
    datasets: [
      {
        label: 'Interactions by Type',
        data: interactionStats?.byType?.map((item: any) => item.count) || [],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading && !userStats) {
    return (
      <DashboardContainer>
        <Header>
          <Title>Dashboard</Title>
          <Subtitle>Loading data...</Subtitle>
        </Header>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <Header>
        <Title>Platform Dashboard</Title>
        <Subtitle>Real-time analytics and monitoring</Subtitle>
      </Header>
      
      <StatsGrid>
        <StatCard>
          <StatTitle>Total Users</StatTitle>
          <StatValue>{userStats?.totalUsers || 0}</StatValue>
        </StatCard>
        <StatCard>
          <StatTitle>Total Videos</StatTitle>
          <StatValue>{videoStats?.totalVideos || 0}</StatValue>
        </StatCard>
        <StatCard>
          <StatTitle>Total Interactions</StatTitle>
          <StatValue>{interactionStats?.totalInteractions || 0}</StatValue>
        </StatCard>
        <StatCard>
          <StatTitle>Avg. Watch Time</StatTitle>
          <StatValue>{interactionStats?.averageWatchTime?.toFixed(1) || 0}s</StatValue>
        </StatCard>
      </StatsGrid>
      
      <ChartGrid>
        <ChartContainer>
          <ChartTitle>Content Categories</ChartTitle>
          <div style={{ height: '300px', display: 'flex', justifyContent: 'center' }}>
            <Pie data={categoryData} options={{ maintainAspectRatio: false }} />
          </div>
        </ChartContainer>
        
        <ChartContainer>
          <ChartTitle>Interaction Types</ChartTitle>
          <div style={{ height: '300px' }}>
            <Bar 
              data={interactionData} 
              options={{ 
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true
                  }
                }
              }} 
            />
          </div>
        </ChartContainer>
      </ChartGrid>
      
      <TableContainer>
        <ChartTitle>Top Videos</ChartTitle>
        <Table>
          <thead>
            <tr>
              <TableHeader>Title</TableHeader>
              <TableHeader>Creator</TableHeader>
              <TableHeader>Category</TableHeader>
              <TableHeader>Views</TableHeader>
              <TableHeader>Likes</TableHeader>
              <TableHeader>Comments</TableHeader>
            </tr>
          </thead>
          <tbody>
            {topVideos.map((video) => (
              <TableRow key={video.id}>
                <TableCell>{video.originalTitle || 'Untitled'}</TableCell>
                <TableCell>{video.username}</TableCell>
                <TableCell>{video.category || 'Uncategorized'}</TableCell>
                <TableCell>{video.views || 0}</TableCell>
                <TableCell>{video.likes}</TableCell>
                <TableCell>{video.comments}</TableCell>
              </TableRow>
            ))}
            {topVideos.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} style={{ textAlign: 'center' }}>No videos available</TableCell>
              </TableRow>
            )}
          </tbody>
        </Table>
      </TableContainer>
      
      <TableContainer style={{ marginTop: '30px' }}>
        <ChartTitle>Recent Interactions</ChartTitle>
        <Table>
          <thead>
            <tr>
              <TableHeader>Video ID</TableHeader>
              <TableHeader>Action</TableHeader>
              <TableHeader>Duration</TableHeader>
              <TableHeader>Timestamp</TableHeader>
            </tr>
          </thead>
          <tbody>
            {recentInteractions.map((interaction) => (
              <TableRow key={`${interaction.videoId}-${interaction.timestamp.toString()}`}>
                <TableCell>{interaction.videoId.substring(0, 8)}...</TableCell>
                <TableCell>{interaction.action}</TableCell>
                <TableCell>{interaction.duration}s</TableCell>
                <TableCell>{formatDate(interaction.timestamp.toString())}</TableCell>
              </TableRow>
            ))}
            {recentInteractions.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} style={{ textAlign: 'center' }}>No recent interactions</TableCell>
              </TableRow>
            )}
          </tbody>
        </Table>
      </TableContainer>
    </DashboardContainer>
  );
};

export default Dashboard; 