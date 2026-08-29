import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost" | "outline" | "success";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "secondary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  className = "",
  disabled,
  ...props
}) => {
  const base =
    "inline-flex items-center justify-center font-medium font-sans rounded-md transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed select-none ";

  const sizeStyles = {
    sm: "text-xs px-2.5 py-1.5 gap-1.5",
    md: "text-sm px-3.5 py-2 gap-2",
    lg: "text-base px-5 py-2.5 gap-2.5",
  }[size];

  const variantStyles = {
    primary:
      "bg-brand-primary hover:bg-blue-600 text-white shadow-sm shadow-blue-500/20 focus:ring-blue-500 border border-blue-400/30",
    secondary:
      "bg-surface-100 hover:bg-surface-50 text-slate-200 border border-surface-border hover:border-slate-600 focus:ring-slate-400",
    success:
      "bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-500/20 border border-emerald-400/30 focus:ring-emerald-500",
    danger:
      "bg-red-600 hover:bg-red-500 text-white shadow-sm shadow-red-500/20 border border-red-400/30 focus:ring-red-500",
    outline:
      "bg-transparent hover:bg-surface-100 text-slate-300 border border-surface-border focus:ring-slate-400",
    ghost:
      "bg-transparent hover:bg-surface-100 text-slate-400 hover:text-slate-200 focus:ring-slate-400",
  }[variant];

  return (
    <button
      className={`${base} ${sizeStyles} ${variantStyles} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-1" />
      ) : (
        leftIcon
      )}
      {children}
      {!isLoading && rightIcon}
    </button>
  );
};
