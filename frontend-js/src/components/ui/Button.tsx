import { cn } from "@/lib/utils";
import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  size?: "default" | "small" | "large";
  children: React.ReactNode;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "default",
  children,
  className,
  ...props
}) => {
  return (
    <button
      className={cn(
        "flex justify-center items-center gap-2.5 rounded-lg",
        variant === "primary" && "bg-white text-[#00A599] font-semibold",
        variant === "secondary" && "bg-transparent text-white",
        size === "default" && "w-[266px] py-[17px] px-[10px] text-lg",
        size === "small" && "p-1.5 text-sm",
        size === "large" && "p-4 text-xl",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
