"use client";

import { useState, useEffect, useRef, use } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { supabase } from "@/lib/supabase";
import { Send, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
    id?: string;
    role: "user" | "assistant";
    content: string;
}

export default function ChatPage({ params }: { params: Promise<{ id: string }> }) {
    const { id: conversationId } = use(params);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [conversationTitle, setConversationTitle] = useState("New Chat");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const { user, session, isLoading: authLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        if (!authLoading && !user) {
            router.push("/login");
            return;
        }

        if (user && conversationId) {
            loadConversation();
        }
    }, [user, authLoading, conversationId]);

    const loadConversation = async () => {
        try {
            // Load conversation details
            const { data: conv } = await supabase
                .from("conversations")
                .select("*")
                .eq("id", conversationId)
                .single();

            if (conv) {
                setConversationTitle(conv.title);
            }

            // Load messages
            const { data: msgs } = await supabase
                .from("messages")
                .select("*")
                .eq("conversation_id", conversationId)
                .order("created_at", { ascending: true });

            if (msgs) {
                setMessages(msgs.map(m => ({
                    id: m.id,
                    role: m.role,
                    content: m.content
                })));
            }
        } catch (error) {
            console.error("Failed to load conversation:", error);
        }
    };

    const saveMessage = async (role: string, content: string) => {
        try {
            await supabase.from("messages").insert({
                conversation_id: conversationId,
                role,
                content
            });
        } catch (error) {
            console.error("Failed to save message:", error);
        }
    };

    const updateConversationTitle = async (firstMessage: string) => {
        // Generate a title from the first message
        const title = firstMessage.length > 30
            ? firstMessage.substring(0, 30) + "..."
            : firstMessage;

        try {
            await supabase
                .from("conversations")
                .update({ title, updated_at: new Date().toISOString() })
                .eq("id", conversationId);

            setConversationTitle(title);
        } catch (error) {
            console.error("Failed to update title:", error);
        }
    };

    const sendMessage = async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMessage = inputValue.trim();
        setInputValue("");

        // Add user message
        setMessages(prev => [...prev, { role: "user", content: userMessage }]);
        await saveMessage("user", userMessage);

        // Update title if this is the first message
        if (messages.length === 0) {
            await updateConversationTitle(userMessage);
        }

        setIsLoading(true);

        try {
            const response = await fetch(`${API_URL}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) throw new Error("Chat request failed");

            const data = await response.json();
            const assistantMessage = data.response;

            setMessages(prev => [...prev, { role: "assistant", content: assistantMessage }]);
            await saveMessage("assistant", assistantMessage);

            // Update conversation timestamp
            await supabase
                .from("conversations")
                .update({ updated_at: new Date().toISOString() })
                .eq("id", conversationId);

        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Sorry, I encountered an error. Please try again."
            }]);
        }

        setIsLoading(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    if (authLoading) {
        return (
            <div className="chat-container">
                <div className="chat-loading">
                    <Loader2 size={32} className="spin" />
                </div>
            </div>
        );
    }

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h1>{conversationTitle}</h1>
            </div>

            <div className="messages-container">
                {messages.length === 0 ? (
                    <div className="welcome-section">
                        <div className="welcome-icon">💬</div>
                        <h2>Start a conversation</h2>
                        <p>Ask me anything about career advice, resume tips, interview prep, or job search strategies!</p>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`}>
                            <div className="message-avatar">
                                {msg.role === "user" ? "👤" : "🤖"}
                            </div>
                            <div className="message-content">
                                {msg.role === "assistant" ? (
                                    <div className="markdown-content">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                ) : (
                                    <p>{msg.content}</p>
                                )}
                            </div>
                        </div>
                    ))
                )}
                {isLoading && (
                    <div className="message assistant">
                        <div className="message-avatar">🤖</div>
                        <div className="message-content">
                            <div className="typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="input-container">
                <div className="input-wrapper">
                    <textarea
                        ref={textareaRef}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask me anything..."
                        disabled={isLoading}
                        rows={1}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!inputValue.trim() || isLoading}
                        className="send-button"
                    >
                        <Send size={20} />
                    </button>
                </div>
                <p className="powered-by">Powered by Gemini 2.5 Flash</p>
            </div>
        </div>
    );
}
