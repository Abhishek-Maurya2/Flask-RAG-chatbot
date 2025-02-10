import React, { useState } from "react";
import useThemeStore from "@/store/useThemeStore";
import {
  Share2Icon,
  ThumbsDown,
  ThumbsUp,
  Volume2,
  Copy,
  MoreHorizontal,
  Clipboard,
  Pencil,
  Trash2,
  Delete,
} from "lucide-react";
import { Button } from "./ui/button";
import { toast } from "sonner";
import axios from "axios";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { coldarkDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { marked } from "marked";
import "../MarkdownStyles.css";
import { motion, AnimatePresence } from "framer-motion";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { AnimatedButton } from "./ThemeToggleButton";
import useMessageStore from "@/store/useMessageStore";


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

const FormatedResponse = (text) => {
  if (!text) return null;

  const codeBlockRegex = /```(.*?)```/gs;
  const parts = text.split(codeBlockRegex);

  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return processBlocks(part, index);
    } else {
      return (
        <div
          key={index}
          className="markdown-container"
          dangerouslySetInnerHTML={{ __html: marked(part) }}
        />
      );
    }
  });
};

const handleSpeak = async (msg) => {
  const API = import.meta.env.VITE_DEEPGRAM_API_KEY;
  const DEEPGRAM_URL = "https://api.deepgram.com/v1/speak?model=aura-hera-en";

  const formData = new FormData();
  formData.append("text", msg);
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
        console.log(res);
        const audioBlob = new Blob([res.data], { type: "audio/mpeg" });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
      });
  } catch (error) {
    console.error(error);
  }
};

const Bubbles = ({ message, idx }) => {
  const theme = useThemeStore((state) => state.theme);
  const userFormattedText = (text) => {
    if (text.includes("Context: ")) {
      text = text.split("Context:")[0];
    }
    return text;
  };
  const [hover, setHover] = useState(false);

  const DeleteMessage = async (idx) => {
    const { conversationId } = useMessageStore.getState();
    try {
      const url = `${import.meta.env.VITE_URL}/delete/${conversationId}/${idx}`;
      await axios.delete(url);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <>
      {message.role === "user" && (
        <div className="flex items-center justify-end gap-2 mx-4 w-[90vw] md:w-[70vw] my-2">
          <motion.div
            className="flex flex-row gap-2"
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
          >
            <AnimatePresence>
              {hover && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20, transition: { delay: 0.7 } }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                >
                  <DropdownMenu>
                    <DropdownMenuTrigger>
                      <AnimatedButton
                        icon={MoreHorizontal}
                        size="icon"
                        variant="ghost"
                      />
                    </DropdownMenuTrigger>

                    <DropdownMenuContent className="rounded-2xl p-2">
                      <DropdownMenuItem className="rounded-full">
                        <Button
                          onClick={() => {
                            navigator.clipboard.writeText(message.content);
                            toast.success("Copied to clipboard");
                          }}
                          variant="ghost"
                          size="icon"
                          className="flex flex-row items-center justify-start gap-2 px-2 m-0 h-8"
                        >
                          <Clipboard className="w-5 h-5" />
                          Copy
                        </Button>
                      </DropdownMenuItem>
                      <DropdownMenuItem className="rounded-full">
                        <Button
                          onClick={() => {
                            navigator.clipboard.writeText(message.content);
                            toast.success("Copied to clipboard");
                          }}
                          variant="ghost"
                          size="icon"
                          className="flex flex-row items-center justify-start gap-2 px-2 m-0 h-8"
                        >
                          <Pencil className="w-5 h-5" />
                          Edit
                        </Button>
                      </DropdownMenuItem>
                      <DropdownMenuItem className="rounded-full">
                        <Button
                          onClick={() => {
                            DeleteMessage(idx);
                            toast.success("Message Deleted");
                          }}
                          variant="ghost"
                          size="icon"
                          className="flex flex-row items-center justify-start gap-2 px-2 m-0 h-8"
                        >
                          <Trash2 className="w-5 h-5" />
                          Delete
                        </Button>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </motion.div>
              )}
            </AnimatePresence>

            <div
              className={`rounded-3xl px-5 py-2.5 ${
                theme === "dark" ? "bg-[#1f1f1f]" : "bg-[#d5d4d4]"
              } max-w-[70vw] sm:max-w-[50vw] break-words`}
            >
              {userFormattedText(message.content)}
            </div>
          </motion.div>
        </div>
      )}
      {/* assistant */}
      {message.role === "assistant" && (
        <div className="w-full flex items-center justify-center">
          <div className="flex flex-row gap-4">
            <div className="bg-amber-500 h-6 w-6 rounded-full"></div>
            <div className="flex flex-col justify-start w-[80vw] md:w-[60vw]">
              <div className="break-words markdown-container">
                {FormatedResponse(message.content)}
              </div>
              {/* options */}
              <div className="flex flex-row mt-2">
                <AnimatedButton
                  onClick={() => handleSpeak(message.content)}
                  icon={Volume2}
                  label={"Speak Aloud"}
                  variant="ghost"
                  size="icon"
                />
                <AnimatedButton
                  onClick={() => {
                    navigator.clipboard.writeText(message.content);
                    toast.success("Copied to clipboard");
                  }}
                  icon={Copy}
                  label={"Copy Text"}
                  variant="ghost"
                  size="icon"
                />
                <AnimatedButton
                  onClick={() => {
                    navigator.share({
                      title: "Dharma Ai",
                      text: message.content,
                    });
                  }}
                  icon={Share2Icon}
                  label={"Share"}
                  variant="ghost"
                  size="icon"
                />
                <AnimatedButton
                  onClick={() => {
                    toast.success("Thanks for the feedback");
                  }}
                  icon={ThumbsUp}
                  label={"Like"}
                  variant="ghost"
                  size="icon"
                />
                <AnimatedButton
                  onClick={() => {
                    toast.error("Thanks for the feedback");
                  }}
                  icon={ThumbsDown}
                  label={"Dislike"}
                  variant="ghost"
                  size="icon"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Bubbles;
