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
      <div className="mt-1 flex items-center justify-between border rounded-t-2xl overflow-hidden px-2 bg-black text-white">
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
  console.log(text);
  const codeBlockRegex = /```(.*?)```/gs;
  const parts = text.split(codeBlockRegex);

  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return processBlocks(part, index);
    } else {
      // Image ![alt](url)
      part = part.replace(
        /!\[(.*?)\]\((http[s]?:\/\/[^\s]+)\)/g,
        '<img src="$2" alt="$1" class="rounded h-[300px] w-[300px]" />'
      );
      // URL [text](url)
      part = part.replace(
        /\[(.*?)\]\((http[s]?:\/\/[^\s]+)\)/g,
        '<a href="$2" class="text-blue-500 hover:underline">$1</a>'
      );

      // Bold-Italic (**_)
      part = part.replace(/\*\*(.*?)_.*?\*\*/g, "<strong><em>$1</em></strong>");
      // Bold (**)
      part = part.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      // Italic (*)
      part = part.replace(/\*(.*?)\*/g, "<em>$1</em>");
      // Line break (*)
      part = part.replace(/\n/g, "<br />");
      // Underline (__)
      part = part.replace(/__(.*?)__/g, "<u>$1</u>");
      // Strikethrough (~~)
      part = part.replace(/~~(.*?)~~/g, "<del>$1</del>");
      // Inline code (`)
      part = part.replace(
        /`(.*?)`/g,
        "<code class='bg-gray-800 rounded p-0.5 mx-1 text-white px-2'>$1</code>"
      );
      // #### Heading
      part = part.replace(/#### (.*?)/g, "<h3>$1</h3>");
      // ### Heading
      part = part.replace(/### (.*?)/g, "<h2>$1</h2>");
      // ## Heading
      part = part.replace(/## (.*?)/g, "<h1>$1</h1>");
      // # Heading
      part = part.replace(/# (.*?)/g, "<h1>$1</h1>");
      // > Blockquote
      part = part.replace(/^> (.*?)/gm, "<blockquote>$1</blockquote>");
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
    <>
      {message.role === "user" && (
        <div className="flex justify-end items-end mx-4 sm:mx-[5vw] my-2">
          <div
            className={`rounded-full px-4 py-2 ${
              theme === "dark" ? "bg-[#1f1f1f]" : "bg-[#d5d4d4]"
            }`}
          >
            {userFormattedText(message.content)}
          </div>
          {/* <div className="h-4 w-4 bg-red-500 rounded-full"></div> */}
        </div>
      )}
      {/* assistant */}
      {message.role === "assistant" && (
        <div className="w-full flex items-center justify-center">
          <div className="flex flex-row gap-4">
            <div className="bg-amber-500 h-6 w-6 rounded-full"></div>
            <div className="flex flex-col justify-start w-[80vw] sm:w-[60vw]">
              <div className="break-words">
                {textFormatter(message.content)}
              </div>
              {/* options */}
              <div className="flex flex-row mt-2">
                <Button
                  size="icon"
                  variant="ghost"
                  className="rounded-full"
                  onClick={() => handleSpeak(message.content)}
                >
                  <Volume2 />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className="rounded-full"
                  onClick={() => {
                    navigator.clipboard.writeText(message.content);
                    toast.success("Copied to clipboard");
                  }}
                >
                  <Copy />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className="rounded-full"
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
                  variant="ghost"
                  className="rounded-full"
                  onClick={() => {
                    toast.success("Thanks for the feedback");
                  }}
                >
                  <ThumbsUp />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className="rounded-full"
                  onClick={() => {
                    toast.error("Thanks for the feedback");
                  }}
                >
                  <ThumbsDown />
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Bubbles;
