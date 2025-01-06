import React, { useState } from "react";
import useThemeStore from "../store/useThemeStore";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const ThemeToggleButton = () => {
  const { theme, toggleTheme } = useThemeStore();
  const [isRotating, setIsRotating] = useState(false);

  const handleToggle = () => {
    setIsRotating(true);
    toggleTheme();
    toast.success("Theme changed");
    setTimeout(() => setIsRotating(false), 500); // Remove the class after the animation
  };

  return (
    <Button size="icon" variant="outline" onClick={handleToggle} className="rounded-full">
      {theme === "light" ? (
        <Moon className={isRotating ? "rotate" : ""} />
      ) : (
        <Sun className={isRotating ? "rotate" : ""} />
      )}
    </Button>
  );
};

export default ThemeToggleButton;
