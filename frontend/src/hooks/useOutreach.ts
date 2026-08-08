import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { chooseOutreach, sendOutreach } from "../services/search";
import type { OutreachPlan } from "../types/api";

export function useOutreach() {
  const [preview, setPreview] = useState<OutreachPlan | null>(null);

  const choose = useMutation({
    mutationFn: chooseOutreach,
    onSuccess: (data) => {
      setPreview(data.plan);
    },
  });

  const send = useMutation({
    mutationFn: sendOutreach,
    onSuccess: (result) => {
      setPreview((current) =>
        current && current.id === result.plan_id ? { ...current, status: "sent" } : current,
      );
    },
  });

  return { choose, send, preview, setPreview };
}
