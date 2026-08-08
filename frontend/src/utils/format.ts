export function formatPhone(value: string): string {
  const digits = value.replace(/\D/g, "");

  if (digits.length === 11) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  }

  if (digits.length === 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }

  return value;
}

export function formatEmail(value: string): string {
  return value.trim();
}

export function confidencePercent(confidence: number): number {
  const clamped = Math.max(0, Math.min(1, confidence));
  return Math.round(clamped * 100);
}
