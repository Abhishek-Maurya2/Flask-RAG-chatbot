import { create } from "zustand";

const useMessageStore = create((Set) => ({
  messages: [],
  conversationId: Date.now().toString(),
  trigger: 0,
  addMessage: (message) =>
    Set((state) => ({
      messages: [...state.messages, message],
      trigger: state.trigger + 1,
    })),

  clearMessages: () => Set({ messages: [] }),

  setConversationId: (id) => Set({ conversationId: id }),

  loadMessage: (messages) => {
    Set((state) => {
      const newMessages = messages.filter(
        (msg) =>
          msg.role === "user" ||
          (msg.role === "assistant" && msg.content != null)
      );
      return { messages: newMessages, trigger: state.trigger + 1 };
    });
  },
}));

export default useMessageStore;
