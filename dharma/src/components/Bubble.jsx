import React from "react";
import useThemeStore from "@/store/useThemeStore";
import { Share2Icon, ThumbsDown, ThumbsUp, Volume2, Copy } from "lucide-react";
import { Button } from "./ui/button";
import { toast } from "sonner";
import axios from "axios";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { coldarkDark } from "react-syntax-highlighter/dist/esm/styles/prism";

const processBlocks = (block, index) => {
  const lines = block.split("\n");
  const language = lines[0];
  // remove first line
  let code = "";
  for (let i = 1; i < lines.length; i++) {
    code += lines[i] + "\n";
  }
  return (
    <div key={index}>
      <div className="flex items-center justify-between border rounded-t-2xl overflow-hidden px-2 bg-black text-white">
        <p>{language}</p>
        <Button
          size="icon"
          variant="ghost"
          onClick={() => {
            navigator.clipboard.writeText(code);
            toast.success("Code copied to clipboard");
          }}
        >
          <Copy />
        </Button>
      </div>
      <SyntaxHighlighter
        style={{ ...coldarkDark }}
        customStyle={{ margin: "0" }}
        language={language}
        className="rounded-b-2xl"
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
};

const textFormatter = (text) => {
  // Handle code blocks (```)
  const codeBlockRegex = /```(.*?)```/gs;
  const parts = text.split(codeBlockRegex);

  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return processBlocks(part, index);
    } else {
      // Bold (**)
      part = part.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      // Italic (*)
      part = part.replace(/\*(.*?)\*/g, "<em>$1</em>");
      // Bold-Italic (**_)
      part = part.replace(/\*\*(.*?)_.*?\*\*/g, "<strong><em>$1</em></strong>");
      // Line break (*)
      part = part.replace(/\n/g, "<br />");
      return <span key={index} dangerouslySetInnerHTML={{ __html: part }} />;
    }
  });
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
  const userFormattedText = (text) => {
    if (text.includes("Context: ")) {
      text = text.split("Context:")[0];
    }
    return text;
  };

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
            >
              {textFormatter(message.content)}
            </div>
          ) : (
            <div
              className={`p-2 rounded-lg max-w-[90vw] sm:max-w-[500px] bg-blue-500 text-sm`}
            >
              {userFormattedText(message.content)}
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

export default Bubbles;
