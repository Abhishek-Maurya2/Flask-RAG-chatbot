import React, { useEffect } from "react";
import useThemeStore from "./store/useThemeStore";
import Main from "./Pages/Main";

function App() {
  const { theme } = useThemeStore();
  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  return (
    <>
      <Main />
    </>
  );
}

export default App;
