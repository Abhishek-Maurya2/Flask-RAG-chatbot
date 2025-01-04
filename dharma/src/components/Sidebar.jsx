import React, { useEffect, useState } from "react";
import ThemeToggleButton from "./ThemeToggleButton";
import axios from "axios";
import useMessageStore from "@/store/useMessageStore";
import useThemeStore from "@/store/useThemeStore";
import { Button } from "./ui/button";
import { ClipboardPlus, Trash2 } from "lucide-react";
import { toast } from "sonner";

function SidebarComponent() {
  const { theme } = useThemeStore();
  const [systemPrompt, setSystemPrompt] = useState(false);
  const [systemMessage, setSystemMessage] = useState("");
  const { setConversationId, loadMessage, clearMessages, trigger } =
    useMessageStore();

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const pingRAG = async () => {
    try {
      const url = `${import.meta.env.VITE_RAG_URL}`;
      const response = await axios.get(url);
    } catch (error) {
      console.error(error);
    }
  };
  const getHistory = async () => {
    try {
      const url = `${import.meta.env.VITE_URL}/history`;
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
  const handleDelete = async (id) => {
    try {
      await axios
        .delete(`${import.meta.env.VITE_URL}/delete/${id}`)
        .then(() => {
          toast("Chat Deleted", "success");
          getHistory();
        });
    } catch (error) {
      toast.error("Failed to delete chat", "error");
      console.error(error);
    }
  };
  const handleNewChat = async () => {
    setConversationId(Date.now().toString());
    clearMessages();
  };
  const ClearHistory = async () => {
    try {
      await axios.delete(`${import.meta.env.VITE_URL}/delete`).then(() => {
        setHistory([]);
      });
      handleNewChat();
    } catch (error) {
      console.error(error);
    }
  };

  const handleSystemPrompt = async () => {
    try {
      const form = new FormData();
      form.append("system_prompt", systemMessage);
      const response = await axios
        .post(`${import.meta.env.VITE_URL}/set-system-prompt`, form)
        .then(() => {
          setSystemPrompt(false);
          toast("System Prompt Updated", "success");
        });
    } catch (error) {
      console.error(error);
      toast("Failed to update System Prompt", "error");
    }
  };
  const getSystemPrompt = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_URL}/get-system-prompt`
      );
      // console.log(response);
      setSystemMessage(response.data.system_prompt);
    } catch (error) {
      console.error(error);
    }
  };
  useEffect(() => {
    getHistory().then(() => setLoading(false));
  }, [trigger]);
  useEffect(() => {
    pingRAG();
    getSystemPrompt();
  }, []);
  return (
    <div className={`flex flex-col justify-between w-full h-full px-4 py-2`}>
      <Button onClick={() => handleNewChat()}>New Chat</Button>
      <p className="text-xl mt-2">History</p>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="flex flex-col gap-2 h-[63vh] overflow-hidden">
          {/* history is not a array */}
          {history
            .slice()
            .reverse()
            .map((item, index) => (
              <div key={index} className="flex flex-row justify-between gap-1">
                <Button
                  onClick={() => loadChatHistory(item)}
                  variant="ghost"
                  className="w-full flex flex-col items-start ps-2 truncate"
                >
                  {item.messages[1].content}
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className={`${
                    theme == "dark" ? "hover:danger" : "hover:bg-[#ff9c9ca9] hover:text-red-500"
                  }`}
                  onClick={() => handleDelete(item.conversation_id)}
                >
                  <Trash2
                  style={{width: "17px", height: "17px"}}
                  />
                </Button>
              </div>
            ))}
        </div>
      )}
      <div className="flex flex-col gap-2 justify-between">
        <Button
          className="hover:border hover:text-red-500 hover:bg-[#f35c5c11] border-red-500"
          onClick={() => ClearHistory()}
        >
          Delete History
        </Button>
        <div className="flex gap-1">
          <ThemeToggleButton />
          <Button
            variant="outline"
            size="icon"
            onClick={() => setSystemPrompt(!systemPrompt)}
          >
            <ClipboardPlus />
          </Button>
        </div>
      </div>
      {systemPrompt && (
        <div
          className="fixed top-0 left-0 right-0 bottom-0 flex items-center justify-center"
          style={{
            backgroundColor:
              theme === "dark"
                ? "rgba(255, 255, 255, 0.1)"
                : "rgba(0, 0, 0, 0.5)",
          }}
        >
          <div className="flex flex-col gap-3 rounded-xl bg-black p-4 w-[80vw] sm:w-[30vw] border">
            <p className="text-2xl font-semibold">Customize Prompt</p>
            <p className="text-md">
              What would you like Luna to know about you to provide better
              responses?
            </p>
            <textarea
              placeholder="Enter your System Prompt"
              className="rounded p-2 bg-inherit border outline-none min-h-52"
              value={systemMessage || ""}
              onChange={(e) => setSystemMessage(e.target.value)}
            ></textarea>
            <div className="flex gap-4 justify-end">
              <Button
                variant="outline"
                className="rounded-full"
                onClick={() => setSystemPrompt(false)}
              >
                Cancel
              </Button>
              <Button
                className="rounded-full"
                onClick={() => {
                  handleSystemPrompt();
                }}
              >
                Save
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SidebarComponent;
