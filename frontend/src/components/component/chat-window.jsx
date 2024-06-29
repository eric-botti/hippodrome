// ChatWindow.js
"use client";

import React, {useEffect, useState} from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import ChatMessage from "@/components/component/chat-message";
import { useWebSocketChat} from "@/components/component/WebSocket";

export default function ChatWindow({ messages, setMessages }) {
  const [newMessage, setNewMessage] = useState("");

  const { sendMessage, onMessageReceived } = useWebSocketChat('ws://127.0.0.1:8000/ws');

  const handleSendMessage = async () => {
    if (newMessage.trim() !== "") {
      const newMessageObj = {
        id: messages.length + 1,
        sender: "You",
        content: newMessage,
      };

      sendMessage(newMessageObj);
      setMessages([...messages, newMessageObj]);

      setNewMessage("");
    }
  };

  useEffect(() => {
    onMessageReceived((newBotMessageObj) => {
      console.log('Received message:', newBotMessageObj);
      setMessages(messages => [...messages, newBotMessageObj]);
    });
  }, []);


  return (
    <div className="flex flex-col h-screen lg:max-w-screen-md mx-auto">
      <h1 className="text-3xl font-bold text-center mt-10">for breakfast</h1>
      <div className="flex-1 overflow-auto p-4">
        <ScrollArea className="h-full">
          <div className="grid gap-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
          </div>
        </ScrollArea>
      </div>
      <div className="bg-background border-t px-4 py-3">
        <div className="relative">
          <Textarea
            placeholder="Type your message..."
            value={newMessage}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            onChange={(e) => setNewMessage(e.target.value)}
            className="min-h-[48px] rounded-2xl resize-none p-4 border border-neutral-400 shadow-sm pr-16"
          />
          <Button
            type="button"
            size="icon"
            className="absolute w-8 h-8 top-3 right-3"
            onClick={handleSendMessage}
          >
            <ArrowUpIcon className="w-4 h-4" />
            <span className="sr-only">Send</span>
          </Button>
        </div>
      </div>
    </div>
  );
}

function ArrowUpIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m5 12 7-7 7 7" />
      <path d="M12 19V5" />
    </svg>
  );
}
