import ChatSection from "@/components/ChatSection";
import React from "react";

import { AppSidebar } from "@/components/app-sidebar";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

function Main() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <ChatSection />
      </SidebarInset>
    </SidebarProvider>
  );
}

export default Main;
