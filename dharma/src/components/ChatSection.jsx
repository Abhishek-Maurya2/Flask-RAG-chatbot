import {
  ArrowUp,
  Copy,
  Send,
  Share2Icon,
  SidebarOpen,
  ThumbsDown,
  ThumbsUp,
  Volume2,
} from "lucide-react";
import React, { useRef, useEffect, useState } from "react";
import axios from "axios";
import useMessageStore from "@/store/useMessageStore";
import { Skeleton } from "./ui/skeleton";
import { toast } from "sonner";
import { Button } from "./ui/button";
import useSideBar from "@/store/useSideBar";
import { SidebarTrigger } from "./ui/sidebar";
import { Separator } from "./ui/separator";
import useThemeStore from "@/store/useThemeStore";

const textFormatter = (text) => {
  // console.log(text);
  // Order matters - process nested formatting first

  // Headers (support h1-h6)
  text = text.replace(/^#{1,6} (.*?)$/gm, (match, content) => {
    const level = match.split(" ")[0].length;
    return `<h${level}>${content}</h${level}>`;
  });

  // if (text.includes("[image_search_tool_used]")) {
  //   text = text.replace(
  //     /\[(.*?)\]\((.*?)\)/g,
  //     '<img src="$2" alt="$1" class="rounded h-[300px] w-[300px] mt-3"/>'
  //   );
  //   // remove the [image_search_tool_used] from the text
  //   text = text.replace(/\[image_search_tool_used\]/g, "");
  // } else if (text.includes("[web_search_tool_used]")) {
  //   text = text.replace(
  //     /\[(.*?)\]\((.*?)\)/g,
  //     '<a href="$2" class="text-blue-500" target="_blank">$1</a>'
  //   );
  //   // remove the [web_search_tool_used] from the text
  //   text = text.replace(/\[web_search_tool_used\]/g, "");
  // }

  // Bold
  text = text.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");

  // Italics
  text = text.replace(/\*(.*?)\*/g, "<i>$1</i>");

  // Underline
  // text = text.replace(/_(.*?)_/g, "<u>$1</u>");

  // Strikethrough
  text = text.replace(/~(.*?)~/g, "<s>$1</s>");

  // Code blocks with triple backticks
  text = text.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang ? ` class="language-${lang}"` : "";
    return `<pre class="bg-black text-white p-2 rounded-md overflow-auto"><code${language}>${code.trim()}</code></pre>`;
  });

  // Inline code with single backtick
  text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Blockquote
  text = text.replace(/^> (.*?)$/gm, "<blockquote>$1</blockquote>");

  // Bullet points (preserve existing functionality)
  text = text.replace(/^- (.*?)(?=\n|$)/gm, "<li>$1</li>");

  // Wrap lists in ul tags
  if (text.includes("<li>")) {
    text = "<ul>" + text + "</ul>";
  }

  // identify urls such that it starts with http or https and ends with space or )
  // text = text.replace(
  //   /((http|https):\/\/[^\s)]+)(?=\s|\)|$)/g,
  //   '<a href="$1" class="text-blue-500" target="_blank">$1</a>'
  // );
  // if found [image number](url) then replace with <img src="url" alt="text" class="rounded h-[300px] w-[300px] rouned-2xl mt-3 "/>
  // text = text.replace(
  //   /\[(.*?)\]\((.*?)\)/g,
  //   '<img src="$2" alt="$1" class="rounded h-[300px] w-[300px] rouned-2xl mt-3"/>'
  // );

  // if found ![text](url) then replace with <img src="url" alt="text" class="rounded h-[300px] w-[300px] rouned-2xl mt-3 "/>

  // if found [text](url) then replace with <a href="url" class="text-blue-500" target="_blank">text</a>
  text = text.replace(
    /\[(.*?)\]\((.*?)\)/g,
    '<a href="$2" class="text-blue-500" target="_blank">$1</a>'
  );

  //if \n is present then replace it with <br>
  text = text.replace(/\n/g, "<br>");

  // if (data:image/png is present then remove it untill space or )
  text = text.replace(/(\(data:image\/png)[^\s)]+(?=\s|\)|$)/g, "");

  return text;
};

const handleSpeak = async (msg) => {
  const API = import.meta.env.VITE_DEEPGRAM_API_KEY;
  const DEEPGRAM_URL = "https://api.deepgram.com/v1/speak?model=aura-hera-en";

  const formData = new FormData();
  formData.append("text", textFormatter(msg));
  try {
    await axios
      .post(DEEPGRAM_URL, formData, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${API}`,
        },
        responseType: "arraybuffer", // Ensure the response is treated as binary data
      })
      .then((res) => {
        const audioBlob = new Blob([res.data], { type: "audio/mpeg" });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
      });
  } catch (error) {
    console.error(error);
  }
};
const Bubbles = ({ message }) => {
  const theme = useThemeStore((state) => state.theme);
  return (
    <div
      className={`flex flex-row px-2 ${
        message.role === "assistant" ? "justify-start" : "justify-end"
      }`}
    >
      <div
        className={`
      flex gap-2 ${
        message.role === "assistant"
          ? "items-start flex-row"
          : "items-end flex-row-reverse"
      }
        `}
      >
        <div
          className={`h-4 w-4 rounded-full
            ${
              message.role === "assistant"
                ? "bg-gradient-to-br from-blue-500 to-red-500"
                : "bg-gradient-to-br from-blue-500"
            }
        
        `}
        ></div>
        {/* {message.content} */}
        <div className="flex flex-col gap-1 items-start">
          {message.role == "assistant" ? (
            <div
              className={`p-2 rounded-lg max-w-[90vw] sm:max-w-[500px] border text-sm ${
                theme == "dark" ? "bg-[#18181b]" : "bg-[#fafafa]"
              }`}
              dangerouslySetInnerHTML={{
                __html: textFormatter(message.content),
              }}
            ></div>
          ) : (
            <div
              className={`p-2 rounded-lg max-w-[90vw] sm:max-w-[500px] bg-blue-500 text-sm`}
            >
              {message.content}
            </div>
          )}
          {message.role == "assistant" && (
            <div className="border rounded-lg">
              <Button
                size="icon"
                variant="outline"
                className="border-0"
                onClick={() => handleSpeak(message.content)}
              >
                <Volume2 />
              </Button>
              <Button
                size="icon"
                variant="outline"
                className="border-0"
                onClick={() => {
                  navigator.clipboard.writeText(message.content);
                  toast.success("Copied to clipboard");
                }}
              >
                <Copy />
              </Button>
              <Button
                size="icon"
                variant="outline"
                className="border-0"
                onClick={() => {
                  navigator.share({
                    title: "Dharma Ai",
                    text: message.content,
                  });
                }}
              >
                <Share2Icon />
              </Button>
              <Button
                size="icon"
                variant="outline"
                className="border-0"
                onClick={() => {
                  toast.success("Thanks for the feedback");
                }}
              >
                <ThumbsUp />
              </Button>
              <Button
                size="icon"
                variant="outline"
                className="border-0"
                onClick={() => {
                  toast.error("Thanks for the feedback");
                }}
              >
                <ThumbsDown />
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

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

  const handleSendMessage = async () => {
    if (sending) return;
    if (msg === "") return;
    const formData = new FormData();
    formData.append("conversation_id", conversationId);
    formData.append("message", msg);
    formData.append("provide-web-Access", true);
    addMessage({ role: "user", content: msg });
    setSending(true);

    try {
      const response = await axios
        .post(`${import.meta.env.VITE_URL}/chat`, formData)
        .then((res) => {
          addMessage({ role: "assistant", content: res.data.response });
          // console.log(res.data);
          setMsg("");
          setSending(false);
          // handleSpeak(res.data.response);
        });
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
          } flex items-center justify-center rounded-full overflow-hidden border-2 px-2`}
        >
          <input
            type="text"
            placeholder="Enter here.."
            className="focus:outline-none w-[80vw] sm:w-[600px] p-3 bg-inherit"
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
        <p className="text-sm">Ai can make mistakes. Check important info.</p>
      </div>
    </div>
  );
}

export default ChatSection;
