// app.js
"use client"

import React, { useState } from "react";
import ChatWindow from "@/components/component/chat-window";

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "Game Master",
      content: "Welcome to Chameleon, enter your name to begin.",
    }
  ]);

  return (
    <div>
      <ChatWindow messages={messages} setMessages={setMessages} />
    </div>
  );
}
