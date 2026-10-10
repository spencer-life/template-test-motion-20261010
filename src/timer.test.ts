import { describe, expect, it } from "vitest";
import { formatClock, progressPercent, remainingSeconds } from "./timer";

describe("formatClock", () => {
  it("formats a non-negative countdown as minutes and seconds", () => {
    expect(formatClock(0)).toBe("00:00");
    expect(formatClock(754)).toBe("12:34");
    expect(formatClock(3600)).toBe("60:00");
  });

  it("clamps negative time to zero", () => {
    expect(formatClock(-4)).toBe("00:00");
  });
});

describe("remainingSeconds", () => {
  it("rounds partial seconds up so the display does not reach zero early", () => {
    expect(remainingSeconds(2500, 1501)).toBe(1);
    expect(remainingSeconds(2500, 1500)).toBe(1);
    expect(remainingSeconds(2500, 1500.1)).toBe(1);
  });

  it("clamps an expired deadline to zero", () => {
    expect(remainingSeconds(1000, 1500)).toBe(0);
  });
});

describe("progressPercent", () => {
  it("reports the elapsed share of a session", () => {
    expect(progressPercent(100, 100)).toBe(0);
    expect(progressPercent(100, 50)).toBe(50);
    expect(progressPercent(100, 0)).toBe(100);
  });

  it("clamps invalid remaining time and empty durations", () => {
    expect(progressPercent(100, 120)).toBe(0);
    expect(progressPercent(100, -5)).toBe(100);
    expect(progressPercent(0, 0)).toBe(0);
  });
});
