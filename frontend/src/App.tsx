import AppLayout from "./layouts/AppLayout";
import NewSearchPage from "./pages/NewSearchPage";
import ProgressPage from "./pages/ProgressPage";
import LeadsPage from "./pages/LeadsPage";
import OutreachPage from "./pages/OutreachPage";
import { useNavigation } from "./store/navigation";

export default function App() {
  const view = useNavigation((state) => state.view);

  return (
    <AppLayout>
      {view === "new" && <NewSearchPage />}
      {view === "progress" && <ProgressPage />}
      {view === "leads" && <LeadsPage />}
      {view === "outreach" && <OutreachPage />}
    </AppLayout>
  );
}
