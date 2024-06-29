import { Client } from "@gradio/client";

export async function chatResponse(msg, chat_history) {
    try {
        const response = await fetch("http://127.0.0.1:7860/call/game", {
            method: "POST",
            headers: {
            "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "data": []
            })
        });

        const result = await response.json();
        
        return JSON.stringify(result);
    } catch (error) {
        console.error("Error getting chat response:", error);
        return "Sorry, there was an error.";
    }
  }