import {
  ArrowUp,
  ArrowUpRight,
  File,
  LoaderCircle,
  Paperclip,
  X,
} from "lucide-react";
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
    const formData = new FormData();
    formData.append("query", query);
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_RAG_URL}/retrieve`,
        formData
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

    if (file.file) {
      const context = await getContext(msg);
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
    // if shift + enter, add new line
    if (e.key === "Enter" && e.shiftKey) {
      setMsg((prev) => prev + "\n");
    } else if (e.key === "Enter") {
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

  const [file, setFile] = useState({
    file: null,
    loading: false,
  });
  const handleRAG = async () => {
    // open file dialog
    const input = document.createElement("input");
    input.type = "file";
    input.onchange = async (e) => {
      const selectedFile = e.target.files[0];
      setFile(
        selectedFile
          ? {
              file: selectedFile,
              loading: true,
            }
          : { file: null, loading: false }
      );
      const formData = new FormData();
      formData.append("file", selectedFile);

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_RAG_URL}/initialize`,
          formData
        );
        toast.success(response.data.message);
        setFile({ file: selectedFile, loading: false });
      } catch (error) {
        toast.error(error.message);
        setFile({ file: null, loading: false });
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
            <div className="flex flex-row flex-wrap items-center justify-center gap-2.5 w-[90vw] sm:w-[80vw] md:w-[60vw]">
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
                  className="border
                  rounded-3xl
                  hover:text-[rgb(8,_112,_184)]
                  dark:bg-[#18181b]
                  bg-[#fafafa]
                  dark:hover:bg-[#2c2c30]
                  h-[150px] w-[120px] sm:h-[180px] sm:w-[150px]
                  flex items-end text-md md:text-xl sm:text-lg py-3 text-wrap text-start
                  hover:shadow-[0_5px_10px_rgba(8,_112,_184,_0.7)]
                  "
                  onClick={() => {
                    setMsg(item);
                    setTriggerSend(true);
                  }}
                >
                  <div className="flex flex-col items-center justify-between h-full w-full">
                    <div className="flex items-center justify-end w-full">
                      <ArrowUpRight style={{ width: "38px", height: "38px" }} />
                    </div>
                    {item}
                  </div>
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => {
              return <Bubbles key={index} message={message} idx = {index} />;
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
            theme == "dark" ? "bg-[#18181b]" : "bg-[#e6e6e6]"
          } flex flex-col rounded-3xl overflow-hidden border-2 px-2 w-[90vw] sm:w-[600px]`}
        >
          {file.file && (
            <div className="flex flex-row items-center justify-between gap-2">
              <div className="flex flex-row items-center gap-2">
                <div className="bg-red-500 h-12 w-12 rounded-lg mt-3 flex items-center justify-center">
                  {file.loading ? (
                    <LoaderCircle
                      className="
                  animate-spin
                  text-white
                  h-8
                  w-8
                "
                    />
                  ) : (
                    <File className="text-white h-8 w-8" />
                  )}
                </div>
                <p>
                  {file.file?.name} -{" "}
                  {file.file?.size && (file.file.size / 1024 / 1024).toFixed(1)}{" "}
                  MB
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full hover:bg-[#e8535397]"
                onClick={() =>
                  setFile({
                    file: null,
                    loading: false,
                  })
                }
              >
                <X />
              </Button>
            </div>
          )}
          <div className="flex flex-row items-center flex-1">
            <Button
              size="icon"
              variant="ghost"
              className="rounded-full -rotate-45 "
              onClick={() => handleRAG()}
            >
              <Paperclip
                style={{
                  width: "18px",
                  height: "18px",
                }}
              />
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
              <LoaderCircle className="animate-spin h-8 w-8" />
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
