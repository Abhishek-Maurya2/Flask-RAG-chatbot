import React, { useState } from "react";
import useThemeStore from "../store/useThemeStore";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { motion } from "framer-motion";

const MButton = motion(Button);

export const AnimatedButton = ({
  icon: Icon,
  label,
  onClick,
  rotate = false,
  textSize = "text-md",
  size = "default",
  variant = "outline",
}) => {
  const [hover, setHover] = useState(false);
  const [iconRotate, setIconRotate] = useState(false);
  var classes = "";

  const handleClick = () => {
    if (rotate) {
      setIconRotate(!iconRotate);
    }
    onClick && onClick();
  };

  if (size === "default") {
    classes =
      "flex flex-row items-center justify-start gap-1 rounded-full py-6";
  } else if (size === "icon") {
    classes = "flex flex-row items-center justify-start gap-1 rounded-full";
  }

  const getWidth = () => {
    if (!label) return 48;
    if (size === "default") {
      return hover ? 200 : 48;
    }
    return hover ? 130 : 48;
  };
  if (!label) {
    return (
      <MButton
        variant={variant}
        onClick={handleClick}
        size="icon"
        className="rounded-full"
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        transition={{ duration: 0.5 }}
      >
        {Icon && (
          <motion.div
            animate={iconRotate ? { rotate: 360 } : { rotate: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Icon />
          </motion.div>
        )}
      </MButton>
    );
  }
  return (
    <MButton
      variant={variant}
      onClick={handleClick}
      className={classes}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      animate={{ width: getWidth() }}
      transition={{ duration: 0.5 }}
    >
      {Icon && (
        <motion.div
          animate={iconRotate ? { rotate: 360 } : { rotate: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Icon />
        </motion.div>
      )}
      {hover && label && (
        <motion.p
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -20, opacity: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className={textSize}
        >
          {label}
        </motion.p>
      )}
    </MButton>
  );
};

export const ThemeToggleButton = () => {
  const { theme, toggleTheme } = useThemeStore();
  const handleToggle = () => {
    toggleTheme();
    toast.success("Theme changed");
  };

  return (
    <AnimatedButton
      onClick={handleToggle}
      icon={theme === "light" ? Moon : Sun}
      label="Change Theme"
      rotate={true}
    />
  );
};
