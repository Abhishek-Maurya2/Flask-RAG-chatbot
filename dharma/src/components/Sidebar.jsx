import React, { useEffect, useState } from "react";
import ThemeToggleButton from "./ThemeToggleButton";
import axios from "axios";
import useMessageStore from "@/store/useMessageStore";
import { Button } from "./ui/button";
import { SidebarClose } from "lucide-react";
import useSideBar from "@/store/useSideBar";

function Sidebar() {
  const { setConversationId, loadMessage, clearMessages, trigger } =
    useMessageStore();
  const { isSideBarOpen, toggleSideBar } = useSideBar();

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const getHistory = async () => {
    try {
      const url = `${import.meta.env.VITE_URL}/list-history`;
      // console.log(url)
      const response = await axios.get(url);
      setHistory(response.data);
      // console.log(response.data);
    } catch (error) {
      console.error(error);
    }
  };
  const loadChatHistory = (data) => {
    // console.log(data.messages);
    setConversationId(data.conversation_id);
    loadMessage(data.messages);
  };
  const handleNewChat = async () => {
    setConversationId(Date.now().toString());
    clearMessages();
  };
  const ClearHistory = async () => {
    try {
      const response = await axios
        .get(`${import.meta.env.VITE_URL}/clear-history`)
        .then(() => {
          setHistory([]);
        });
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    getHistory().then(() => setLoading(false));
  }, [trigger]);

  return (
    <div
      className={`${
        isSideBarOpen ? "flex" : "hidden"
      } flex-col border-r w-[280px] h-full p-4 rounded-e-2xl gap-2 overflow-hidden`}
    >
      <div className="flex flex-row items-center justify-between mb-4">
        <p className="text-xl font-semibold">Dharma Ai</p>
        <Button
          size="icon"
          variant="outline"
          onClick={() => toggleSideBar(!isSideBarOpen)}
        >
          <SidebarClose />
        </Button>
      </div>
      <Button onClick={() => handleNewChat()}>New Chat</Button>
      <p className="text-xl mt-2">History</p>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="flex flex-col gap-2 h-[60vh] overflow-auto">
          {/* history is not a array */}
          {history
            .slice()
            .reverse()
            .map((item, index) => (
              <div key={index} className="flex flex-row justify-between">
                <button
                  onClick={() => loadChatHistory(item)}
                  className="p-1 rounded w-full text-start hover:bg-[#ffffff5f]"
                >
                  <p
                    className="
                  truncate
                  "
                  >
                    {item.messages[1].content}
                  </p>
                </button>
              </div>
            ))}
        </div>
      )}
      <Button onClick={() => ClearHistory()}>Delete History</Button>
      <ThemeToggleButton />
    </div>
  );
}

export default Sidebar;
