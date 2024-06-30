// app.js
"use client"

import React, { useState } from "react";
import ChatWindow from "@/components/component/chat-window";
import {Welcome} from "@/components/component/welcome";

export default function App() {
  const [name, setName] = useState('');
  const [isNameEntered, setIsNameEntered] = useState(false);

  const handleNameSubmit = (name) => {
    setName(name);
    setIsNameEntered(true);
  };


  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "Game Master",
      content: "Welcome " + name + "! I am the Game Master. I will be guiding you through this adventure. Are you ready to begin?",
    }
  ]);

  return (
    <div>
      {!isNameEntered ? (
        <Welcome onNameSubmit={handleNameSubmit} />
      ) : (
        <ChatWindow messages={messages} setMessages={setMessages} />
      )}
    </div>
  );
}
