import { useMutation } from "@tanstack/react-query";
import { startSearch } from "../services/search";
import { useNavigation } from "../store/navigation";

export function useSearch() {
  const setJob = useNavigation((state) => state.setJob);
  const navigate = useNavigation((state) => state.navigate);

  return useMutation({
    mutationFn: startSearch,
    onSuccess: (data, variables) => {
      setJob(data.job_id, variables.query);
      navigate("progress");
    },
  });
}
