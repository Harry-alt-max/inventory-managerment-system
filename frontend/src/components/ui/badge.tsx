import type { HTMLAttributes } from "react";

export type BadgeTone = "neutral" | "success" | "warning" | "danger" | "info" | "primary";

const TONE_CLASS: Record<BadgeTone, string> = {
  neutral: "bg-muted-tint text-fg-muted",
  success: "bg-success-tint text-success",
  warning: "bg-warning-tint text-warning",
  danger: "bg-danger-tint text-danger",
  info: "bg-info-tint text-info",
  primary: "bg-primary-tint text-primary",
};

/** 狀態徽章：狀態色文字 + 對應 tint 底（DESIGN.md「狀態徽章」）。 */
export function Badge({
  tone = "neutral",
  className = "",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: BadgeTone }) {
  return (
    <span
      className={`inline-flex items-center rounded-pill px-2 py-0.5 text-xs font-medium ${TONE_CLASS[tone]} ${className}`}
      {...props}
    />
  );
}
