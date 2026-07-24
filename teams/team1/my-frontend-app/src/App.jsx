import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import ChallengeListPage from './pages/ChallengeListPage';
import ChallengeDetailPage from './pages/ChallengeDetailPage';
import CreateChallengePage from './pages/CreateChallengePage';
import EditChallengePage from './pages/EditChallengePage';
import CompetitionListPage from './pages/CompetitionListPage';
import CompetitionDetailPage from './pages/CompetitionDetailPage';
import CreateCompetitionPage from './pages/CreateCompetitionPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="challenges" element={<ChallengeListPage />} />
        <Route path="challenges/new" element={<CreateChallengePage />} />
        <Route path="challenges/:id/edit" element={<EditChallengePage />} />
        <Route path="challenges/:id" element={<ChallengeDetailPage />} />
        <Route path="competitions" element={<CompetitionListPage />} />
        <Route path="competitions/new" element={<CreateCompetitionPage />} />
        <Route path="competitions/:id" element={<CompetitionDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
