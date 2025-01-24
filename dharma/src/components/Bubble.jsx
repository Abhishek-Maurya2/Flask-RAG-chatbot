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
  DropdownMenuLabel,
  DropdownMenuSeparator,
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

const textFormatter = (text) => {
  if (!text) return null;

  const codeBlockRegex = /```(.*?)```/gs;
  const parts = text.split(codeBlockRegex);

  return parts.map((part, index) => {
    if (index % 2 === 1) {
      return processBlocks(part, index);
    } else {
      // return { __html: marked(part) };
      return (
        <div
          key={index}
          className="markdown-container"
          dangerouslySetInnerHTML={
            { __html: marked(part) } // eslint-disable-line
          }
        />
      );

      //   // Combined link and image handler
      //   part = part.replace(
      //     // Match both markdown and direct URLs
      //     /(!\[(.*?)\]\((.*?)\)|(\[(.*?)\]\((.*?)\))|((https?|ftp):\/\/[^\s/$.?#].[^\s]*))/g,
      //     (
      //       match,
      //       _full,
      //       imgAlt,
      //       imgSrc,
      //       _linkFull,
      //       linkText,
      //       linkHref,
      //       directUrl
      //     ) => {
      //       // Handle markdown images
      //       if (imgSrc) {
      //         return `<img src="${imgSrc}" alt="${imgAlt}" class="w-[300px] h-[300px] object-cover rounded-xl">`;
      //       }

      //       // Handle markdown links
      //       if (linkHref) {
      //         return `<a href="${linkHref}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">${linkText}</a>`;
      //       }

      //       // Handle direct URLs
      //       if (directUrl) {
      //         const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(directUrl);
      //         return isImage
      //           ? `<img src="${directUrl}" alt="image" class="w-[300px] h-[300px] object-cover rounded-xl">`
      //           : `<a href="${directUrl}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">${directUrl}</a>`;
      //       }

      //       return match; // Return unchanged if no match
      //     }
      //   );

      //   // // Images (e.g. ![alt](src))
      //   // part = part.replace(
      //   //   /!\[(.*?)\]\((.*?)\)/g,
      //   //   '<img src="$2" alt="$1" class="w-[300px] h-[300px] object-cover rounded-xl">'
      //   // );

      //   // // Links (e.g. [text](href))
      //   // part = part.replace(
      //   //   /\[(.*?)\]\((.*?)\)/g,
      //   //   '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">$1</a>'
      //   // );

      //   // // // urls (e.g. https://example.com)
      //   // // part = part.replace(/((https?|ftp):\/\/[^\s/$.?#].[^\s]*)/g, (match) => {
      //   // //   if (
      //   // //     match.includes(".jpg") ||
      //   // //     match.includes(".png") ||
      //   // //     match.includes(".jpeg") ||
      //   // //     match.includes(".gif")
      //   // //   ) {
      //   // //     return `<img src="${match}" alt="image" class="w-[300px] h-[300px] object-cover rounded-xl">`;
      //   // //   }
      //   // //   return `<a href="${match}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">${match}</a>`;
      //   // // });

      //   // Tool used "<?THIS_MESSAGE_WAS_RESULT_OF_TOOL_USE_AND_NOT_TO_BE_COPIED?>"
      //   part = part.replace(
      //     "<?THIS_MESSAGE_WAS_RESULT_OF_TOOL_USE_AND_NOT_TO_BE_COPIED?>",
      //     `<div class="flex"><div class="flex flex-row items-center gap-2 bg-[#e6e6e6] dark:bg-[#1f1f1f] p-3 rounded-xl mt-2 border-2 hover:border-[#e8535397]"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-shapes" style="height: 26px; width: 26px;"><path d="M8.3 10a.7.7 0 0 1-.626-1.079L11.4 3a.7.7 0 0 1 1.198-.043L16.3 8.9a.7.7 0 0 1-.572 1.1Z"></path><rect x="3" y="14" width="7" height="7" rx="1"></rect><circle cx="17.5" cy="17.5" r="3.5"></circle></svg><p>This message was generated by a tool</p></div></div>`
      //   );

      //   part = part.replace(/`(.+?)`/g, "<code>$1</code>");

      //   // Convert headings (H1-H6)
      //   part = part.replace(/^###### (.+)$/gm, "<h6>$1</h6>");
      //   part = part.replace(/^##### (.+)$/gm, "<h5>$1</h5>");
      //   part = part.replace(/^#### (.+)$/gm, "<h4>$1</h4>");
      //   part = part.replace(/^### (.+)$/gm, "<h3>$1</h3>");
      //   part = part.replace(/^## (.+)$/gm, "<h2>$1</h2>");
      //   part = part.replace(/^# (.+)$/gm, "<h1>$1</h1>");

      //   // Convert bold (**text** or __text__)
      //   part = part.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      //   part = part.replace(/__(.+?)__/g, "<strong>$1</strong>");

      //   // Convert italic (*text* or _text_)
      //   part = part.replace(/\*(.+?)\*/g, "<em>$1</em>");
      //   part = part.replace(/_(.+?)_/g, "<em>$1</em>");

      //   // Convert ordered lists (1. text)
      //   part = part.replace(/^\s*\d+\.\s(.+)$/gm, "<li>$1</li>");
      //   part = part.replace(/(<li>.*<\/li>)/gm, "<ol>$1</ol>");
      //   part = part.replace(/<\/ol>\s*<ol>/g, ""); // Merge adjacent <ol> tags

      //   // Handle unordered lists (-, *, +) and sub-lists
      //   let ulRegex = /^\s*([-\*\+])\s+(.+)$/gm;
      //   part = part.replace(ulRegex, (match, symbol, content, offset, string) => {
      //     const depth = match.match(/^\s*/)[0].length / 2; // Assuming 2 spaces per indentation level
      //     const listType = symbol === "+" ? "ul" : "ul"; // Assuming + as unordered list marker
      //     const nestedList =
      //       "<ul>".repeat(depth) + `<li>${content}</li>` + "</ul>".repeat(depth);
      //     return nestedList;
      //   });

      //   // Convert blockquotes (> text)
      //   part = part.replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>");

      //   // Match entire table structure
      //   const tableRegex =
      //     /^\s*\|(.+?)\|\s*$(?:\r?\n\s*\|[-:\s]+?\|\s*$)?(?:\r?\n\s*\|.+?\|\s*$)*/gm;

      //   // Process the table
      //   part = part.replace(tableRegex, (match) => {
      //     const rows = match.trim().split("\n");
      //     const [header, separator, ...bodyRows] = rows;

      //     // Get alignment from separator row
      //     const alignments = separator
      //       .split("|")
      //       .filter(Boolean)
      //       .map((cell) => {
      //         if (cell.startsWith(":") && cell.endsWith(":")) return "center";
      //         if (cell.endsWith(":")) return "right";
      //         return "left";
      //       });

      //     // Process header
      //     const headerHTML = processRow(header, true, alignments);

      //     // Process body
      //     const bodyHTML = bodyRows
      //       .map((row) => processRow(row, false, alignments))
      //       .join("");

      //     return `
      // <table class="w-full text-sm text-center rounded-xl overflow-hidden shadow-md">
      //   <thead class="text-xs text-gray-700 uppercase bg-[#d5d4d4] dark:bg-gray-700 dark:text-gray-400">
      //     ${headerHTML}
      //   </thead>
      //   <tbody>
      //     ${bodyHTML}
      //   </tbody>
      // </table>`;

      //     function processRow(row, isHeader, alignments) {
      //       const cells = row.split("|").filter(Boolean);
      //       const tag = isHeader ? "th" : "td";
      //       const rowClass = isHeader ? "" : "";

      //       return `<tr class="${rowClass}">${cells
      //         .map((cell, i) => {
      //           const align = alignments[i];
      //           const cellClass = isHeader
      //             ? "py-4 font-medium text-gray-900 dark:text-white border"
      //             : "py-4 font-medium text-gray-900 dark:text-white border";
      //           return `<${tag} ${
      //             isHeader ? 'scope="col"' : ""
      //           } class="${cellClass}">${cell.trim()}</${tag}>`;
      //         })
      //         .join("")}</tr>`;
      //     }
      //   });

      //   // Convert line breaks
      //   part = part.replace(/\n/g, "<br>");

      //   return <div key={index} dangerouslySetInnerHTML={{ __html: part }}></div>;
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
                {textFormatter(message.content)}
              </div>
              {/* <div
                className="markdown-container"
                dangerouslySetInnerHTML={createMarkup()}
              /> */}
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
