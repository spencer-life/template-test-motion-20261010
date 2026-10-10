export function remainingSeconds(endAtMilliseconds: number, nowMilliseconds: number): number {
  return Math.max(0, Math.ceil((endAtMilliseconds - nowMilliseconds) / 1000));
}

export function formatClock(totalSeconds: number): string {
  const wholeSeconds = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(wholeSeconds / 60);
  const seconds = wholeSeconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export function progressPercent(durationSeconds: number, remaining: number): number {
  if (durationSeconds <= 0) return 0;

  const elapsed = durationSeconds - Math.max(0, remaining);
  return Math.min(100, Math.max(0, (elapsed / durationSeconds) * 100));
}
