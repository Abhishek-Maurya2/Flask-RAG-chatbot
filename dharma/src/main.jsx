import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { Toaster } from "@/components/ui/sonner";
import useThemeStore from "./store/useThemeStore.js";

const ThemedToaster = () => {
  const theme = useThemeStore((state) => state.theme);
  return (
    <Toaster
      position="top-center"
      toastOptions={{
        duration: 3000,
        style: {
          backgroundColor: theme === "dark" ? "#333" : "#f4f4f4",
          color: theme === "dark" ? "#f4f4f4" : "#333",
          border: theme === "dark" ? "1px solid #4d4d4d" : "1px solid #d4d4d4",
        },
      }}
    />
  );
};
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ThemedToaster />
    <App />
  </StrictMode>
);
