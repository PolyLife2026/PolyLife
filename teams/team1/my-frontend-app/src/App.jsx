import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ChallengeListPage from './pages/ChallengeListPage';
import ChallengeDetailPage from './pages/ChallengeDetailPage';
import CreateChallengePage from './pages/CreateChallengePage';
import EditChallengePage from './pages/EditChallengePage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/challenges" replace />} />
        <Route path="challenges" element={<ChallengeListPage />} />
        <Route path="challenges/new" element={<CreateChallengePage />} />
        <Route path="challenges/:id/edit" element={<EditChallengePage />} />
        <Route path="challenges/:id" element={<ChallengeDetailPage />} />
      </Route>
    </Routes>
  );
}
