// ChatMessage.js

import React from "react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

export default function ChatMessage({ message }) {
  return (
    <div className={`fade-in flex items-start gap-3 ${message.sender === "You" ? "justify-end" : ""}`}>
      {message.sender === "You" ? (
        <div
          className={`bg-muted rounded-lg p-3 max-w-[70%] ${
            message.sender === "You" ? "bg-primary text-primary-foreground" : ""
          }`}
        >
          <p className="text-sm">{message.content}</p>
        </div>
      ) : (
        <>
          {/* <Avatar className="w-10 h-10">
            <AvatarImage src="/placeholder-user.jpg" />
            <AvatarFallback>{message.sender.charAt(0)}</AvatarFallback>
          </Avatar> */}
          <div
            className="bg-muted rounded-lg p-3 max-w-[70%]"
          >
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium">{message.sender}</span>
            </div>
            <p className="text-sm">{message.content}</p>
          </div>
        </>
      )}
    </div>
  );
}
