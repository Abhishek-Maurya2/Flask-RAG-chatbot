import ChatSection from "@/components/ChatSection";
import Sidebar from "@/components/Sidebar";
import useSideBar from "@/store/useSideBar";
import React, { useEffect } from "react";

function Main() {
  // const { isSideBarOpen, toggleSideBar } = useSideBar();

  // useEffect(() => {
  //   const handleResize = () => {
  //     if (window.innerWidth < 768) {
  //       toggleSideBar(false);
  //     } else {
  //       toggleSideBar(true);
  //     }
  //   };
  //   window.addEventListener("resize", handleResize);
  //   handleResize();
  //   console.log(isSideBarOpen);
  //   return () => window.removeEventListener("resize", handleResize);
  // }, []);

  return (
    <div className="h-[93vh] sm:h-[100vh] w-full flex flex-row overflow-hidden">
      <Sidebar />
      <ChatSection />
    </div>
  );
}

export default Main;
