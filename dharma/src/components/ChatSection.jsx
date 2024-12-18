import { ArrowUp, Image, Paperclip } from "lucide-react";
import React, { useRef, useEffect, useState } from "react";
import axios from "axios";
import useMessageStore from "@/store/useMessageStore";
import { Skeleton } from "./ui/skeleton";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { SidebarTrigger } from "./ui/sidebar";
import { Separator } from "./ui/separator";
import useThemeStore from "@/store/useThemeStore";
import Bubbles from "./Bubble";


function SkeletonDemo() {
  return (
    <div className="flex items-center space-x-4 ms-4">
      <Skeleton className="h-12 w-12 rounded-full  bg-slate-200" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-[250px] bg-slate-200" />
        <Skeleton className="h-4 w-[200px] bg-slate-200" />
      </div>
    </div>
  );
}

function ChatSection() {
  const { messages, addMessage, conversationId } = useMessageStore();
  const theme = useThemeStore((state) => state.theme);
  const [msg, setMsg] = useState("");
  const [sending, setSending] = useState(false);
  const [triggerSend, setTriggerSend] = useState(false);

  useEffect(() => {
    if (triggerSend) {
      handleSendMessage();
      setTriggerSend(false);
    }
  }, [msg, triggerSend]);

  const getContext = async (query) => {
    if (query === "") return "";
    if (!file) return "";
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_RAG_URL}/retrieve`,
        {
          params: { query: query },
        }
      );
      console.log(response.data.context);
      let context = "";
      response.data.context.forEach((message) => {
        context += message + " ";
      });
      return context;
    } catch (error) {
      console.error(error);
      toast.error(error.message);
      return "";
    }
  };

  const handleSendMessage = async () => {
    if (sending) return;
    if (msg === "") return;

    const formData = new FormData();
    formData.append("conversation_id", conversationId);

    const context = await getContext(msg);
    if (context !== "") {
      formData.append("message", msg + "\n\nContext: " + context);
    } else {
      formData.append("message", msg);
    }

    addMessage({ role: "user", content: msg });
    setSending(true);

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_URL}/chat`,
        formData
      );
      addMessage({ role: "assistant", content: response.data.response });
      setMsg("");
      setSending(false);
    } catch (error) {
      console.error(error);
      toast.error(error.message);
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };
  const chatEndRef = useRef(null);
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const handleResize = () => {
      document.documentElement.style.setProperty(
        "--vh",
        `${window.innerHeight * 0.01}px`
      );
    };
    window.addEventListener("resize", handleResize);
    handleResize();
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const [file, setFile] = useState(null);
  const handleRAG = async () => {
    // open file dialog
    const input = document.createElement("input");
    input.type = "file";
    input.onchange = async (e) => {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      const formData = new FormData();
      formData.append("file", selectedFile);

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_RAG_URL}/initialize`,
          formData
        );
        toast.success(response.data.message);
      } catch (error) {
        toast.error(error.message);
      }
    };
    input.click();
  };

  return (
    <div
      className="flex flex-col gap-1"
      style={{ height: "calc(var(--vh, 1vh) * 100)" }}
    >
      <header className="flex items-center gap-2 border-b px-4 py-3">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <p>Dharma Ai</p>
      </header>
      {/* chats */}
      <div className="flex flex-col gap-2 overflow-y-auto flex-1">
        {messages.length === 0 ? (
          <div className="flex flex-col gap-2 items-center justify-center h-full w-full">
            <p className="text-[30px] mb-2">What can I help with?</p>
            <div className="flex flex-row flex-wrap items-center justify-center gap-2 mx-4">
              {[
                "Images of Shinchan",
                "Search web for News in India",
                "Search Wilkipedia for Gas Giants",
                "What is the capital of India?",
                "What is the weather in Delhi ?",
                "Write code for a simple calculator",
              ].map((item, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className={`border rounded-full ${
                    theme == "dark" ? "bg-[#18181b]" : "bg-[#fafafa]"
                  }`}
                  onClick={() => {
                    setMsg(item);
                    setTriggerSend(true);
                  }}
                >
                  {item}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => {
              return <Bubbles key={index} message={message} />;
            })}
            {sending && <SkeletonDemo />}
          </>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* dock */}
      <div className="pt-1 flex flex-col gap-1 items-center justify-center">
        <div
          className={`${
            theme == "dark" ? "bg-[#18181b]" : "bg-[#fafafa]"
          } flex flex-col rounded-3xl overflow-hidden border-2 px-2 w-[90vw] sm:w-[600px]`}
        >
          {file && (
            <div className="flex flex-row items-center gap-2">
              <div className="bg-red-500 h-12 w-12 rounded-lg mt-3 flex items-center justify-center">
                {
                  {
                    "image/png": <Image />,
                    "image/jpeg": <Image />,
                    "image/jpg": <Image />,
                    "application/pdf": <p>PDF</p>,
                    "application/msword": <p>DOC</p>,
                    "application/xlsx": <p>XLS</p>,
                    "application/pptx": <p>PPT</p>,
                    "application/csv": <p>CSV</p>,
                  }[file?.type]
                }
              </div>
              <p>
                {file?.name} -{" "}
                {file?.size && (file.size / 1024 / 1024).toFixed(1)} MB
              </p>
            </div>
          )}
          <div className="flex flex-row items-center flex-1">
            <Button
              size="icon"
              variant="ghost"
              className="rounded-full -rotate-45"
              onClick={() => handleRAG()}
            >
              <Paperclip />
            </Button>
            <input
              type="text"
              placeholder="Enter here.."
              className="focus:outline-none p-3 bg-inherit flex-1"
              value={msg}
              onChange={(e) => setMsg(e.target.value)}
              onKeyPress={(e) => handleKeyPress(e)}
            />
            {sending ? (
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            ) : (
              <Button
                className="rounded-full h-8 w-8"
                size="icon"
                onClick={() => handleSendMessage()}
              >
                <ArrowUp style={{ width: "28px", height: "28px" }} />
              </Button>
            )}
          </div>
        </div>
        <p className="text-sm mb-1">
          Ai can make mistakes. Check important info.
        </p>
      </div>
    </div>
  );
}

export default ChatSection;
