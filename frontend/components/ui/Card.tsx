import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  header?: React.ReactNode;
  footer?: React.ReactNode;
  glow?: boolean;
  cornerBrackets?: "green" | "red" | "blue" | "none";
  isBreach?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  header,
  footer,
  glow = false,
  cornerBrackets = "none",
  isBreach = false,
  className = "",
  ...props
}) => {
  let bracketClass = "";
  if (cornerBrackets === "green") bracketClass = "corner-brackets";
  if (cornerBrackets === "red") bracketClass = "corner-brackets-red";
  if (cornerBrackets === "blue") bracketClass = "corner-brackets-blue";

  return (
    <div
      className={`surveillance-card ${bracketClass} ${
        isBreach ? "breach-alert animate-breach-pulse" : ""
      } ${className}`}
      {...props}
    >
      {header && (
        <div className="px-4 py-2.5 border-b border-white/10 bg-white/[0.02] flex items-center justify-between text-xs font-mono">
          {header}
        </div>
      )}
      <div className="p-4">{children}</div>
      {footer && (
        <div className="px-4 py-2.5 border-t border-white/10 bg-white/[0.01]">
          {footer}
        </div>
      )}
    </div>
  );
};
