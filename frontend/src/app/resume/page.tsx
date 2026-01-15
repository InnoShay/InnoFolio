"use client";

import { useState, useRef, useEffect } from "react";
import {
    Upload,
    FileText,
    Sparkles,
    CheckCircle,
    BarChart3,
    Shield,
    Lightbulb,
    PenTool,
    Send,
    Loader2,
    X,
    ExternalLink,
    Trophy
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const HIRESIGHT_URL = "https://hiresight-delta.vercel.app/";

interface Message {
    role: "user" | "assistant";
    content: string;
}

const analysisActions = [
    {
        id: "score",
        icon: BarChart3,
        label: "Resume Score",
        description: "Get a score out of 100",
        prompt: "Analyze my resume and give me a detailed score out of 100. Break down the scoring for each section.",
        color: "#6366f1"
    },
    {
        id: "sections",
        icon: FileText,
        label: "Section Analysis",
        description: "Review each section",
        prompt: "Provide a detailed section-by-section analysis of my resume. Cover Summary, Experience, Skills, and Education.",
        color: "#06b6d4"
    },
    {
        id: "ats",
        icon: Shield,
        label: "ATS Check",
        description: "Compatibility score",
        prompt: "Check my resume for ATS (Applicant Tracking System) compatibility. What issues might prevent it from passing ATS filters?",
        color: "#10b981"
    },
    {
        id: "improve",
        icon: Lightbulb,
        label: "Improvements",
        description: "Actionable suggestions",
        prompt: "Give me specific, actionable suggestions to improve my resume. Focus on the most impactful changes I can make.",
        color: "#f59e0b"
    },
    {
        id: "grammar",
        icon: PenTool,
        label: "Grammar Check",
        description: "Language & clarity",
        prompt: "Review my resume for grammar, spelling, and clarity issues. Suggest professional language improvements.",
        color: "#ec4899"
    }
];

export default function ResumePage() {
    const [file, setFile] = useState<File | null>(null);
    const [resumeText, setResumeText] = useState<string>("");
    const [isUploading, setIsUploading] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [activeAnalysis, setActiveAnalysis] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            await processFile(selectedFile);
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            await processFile(droppedFile);
        }
    };

    const processFile = async (selectedFile: File) => {
        // Validate file type
        if (!selectedFile.type.includes("pdf") && !selectedFile.name.endsWith(".docx")) {
            alert("Please upload a PDF or DOCX file");
            return;
        }

        // Validate file size (5MB max)
        if (selectedFile.size > 5 * 1024 * 1024) {
            alert("File must be less than 5MB");
            return;
        }

        setFile(selectedFile);
        setIsUploading(true);
        setMessages([]);

        try {
            const formData = new FormData();
            formData.append("file", selectedFile);

            const response = await fetch(`${API_URL}/api/resume/extract`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Failed to process resume");
            }

            const data = await response.json();
            setResumeText(data.text);

            // Add welcome message
            setMessages([{
                role: "assistant",
                content: `✅ **Resume uploaded successfully!**\n\nI've analyzed your resume "${selectedFile.name}". Choose an analysis option from the tiles above, or ask me anything about your resume!`
            }]);
        } catch (error) {
            console.error("Upload error:", error);
            alert("Failed to upload resume. Please try again.");
            setFile(null);
        }

        setIsUploading(false);
    };

    const removeFile = () => {
        setFile(null);
        setResumeText("");
        setMessages([]);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleAnalysisClick = async (action: typeof analysisActions[0]) => {
        if (!resumeText || isLoading) return;

        setActiveAnalysis(action.id);
        await sendMessage(action.prompt, action.label);
        setActiveAnalysis(null);
    };

    const sendMessage = async (message: string, actionLabel?: string) => {
        if (!message.trim() || !resumeText || isLoading) return;

        const userMessage: Message = {
            role: "user",
            content: actionLabel ? `📊 ${actionLabel}` : message
        };
        setMessages(prev => [...prev, userMessage]);
        setInputValue("");
        setIsLoading(true);

        try {
            const response = await fetch(`${API_URL}/api/resume/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: message,
                    resume_text: resumeText
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to get response");
            }

            const data = await response.json();
            const assistantMessage: Message = { role: "assistant", content: data.response };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Sorry, I encountered an error. Please try again."
            }]);
        }

        setIsLoading(false);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendMessage(inputValue);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputValue);
        }
    };

    return (
        <div className="resume-page">
            <div className="resume-page-header">
                <h1><Sparkles size={28} /> Resume Analysis</h1>
                <p>Upload your resume and get AI-powered feedback</p>
            </div>

            <div className="resume-layout">
                {/* Left Panel - Upload */}
                <div className="resume-upload-panel">
                    <div className="panel-header">
                        <Upload size={20} />
                        <h2>Upload Resume</h2>
                    </div>

                    {!file ? (
                        <div
                            className="upload-zone"
                            onDrop={handleDrop}
                            onDragOver={(e) => e.preventDefault()}
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf,.docx"
                                onChange={handleFileSelect}
                                hidden
                            />
                            <div className="upload-icon">
                                <Upload size={40} />
                            </div>
                            <p className="upload-title">Drop your resume here</p>
                            <p className="upload-subtitle">or click to browse</p>
                            <span className="upload-formats">PDF or DOCX • Max 5MB</span>
                        </div>
                    ) : (
                        <div className="file-uploaded">
                            {isUploading ? (
                                <div className="uploading-state">
                                    <Loader2 size={32} className="spin" />
                                    <p>Processing resume...</p>
                                </div>
                            ) : (
                                <>
                                    <div className="file-info">
                                        <FileText size={32} />
                                        <div className="file-details">
                                            <span className="file-name">{file.name}</span>
                                            <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                                        </div>
                                        <button className="remove-file" onClick={removeFile}>
                                            <X size={18} />
                                        </button>
                                    </div>
                                    <div className="file-status">
                                        <CheckCircle size={16} />
                                        <span>Ready for analysis</span>
                                    </div>
                                </>
                            )}
                        </div>
                    )}

                    {/* HireSight Link */}
                    <div className="compare-section">
                        <div className="compare-divider">
                            <span>After analysis</span>
                        </div>
                        <a
                            href={HIRESIGHT_URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="compare-link"
                        >
                            <Trophy size={18} />
                            <span>Compare with competitors</span>
                            <ExternalLink size={14} />
                        </a>
                    </div>
                </div>

                {/* Right Panel - Analysis & Chat */}
                <div className="resume-analysis-panel">
                    {/* Analysis Action Tiles */}
                    <div className="analysis-actions">
                        {analysisActions.map((action) => (
                            <button
                                key={action.id}
                                className={`action-tile ${!file || isUploading ? "disabled" : ""} ${activeAnalysis === action.id ? "active" : ""}`}
                                onClick={() => handleAnalysisClick(action)}
                                disabled={!file || isUploading || isLoading}
                                style={{ "--action-color": action.color } as React.CSSProperties}
                            >
                                <action.icon size={20} />
                                <span className="action-label">{action.label}</span>
                                <span className="action-desc">{action.description}</span>
                            </button>
                        ))}
                    </div>

                    {/* Chat Area */}
                    <div className="resume-chat">
                        <div className="chat-messages">
                            {messages.length === 0 ? (
                                <div className="chat-empty">
                                    <FileText size={48} />
                                    <p>Upload your resume to start the analysis</p>
                                    <span>Choose an action tile or ask a question</span>
                                </div>
                            ) : (
                                messages.map((msg, index) => (
                                    <div key={index} className={`chat-message ${msg.role}`}>
                                        <div className="message-bubble">
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
                                <div className="chat-message assistant">
                                    <div className="message-bubble">
                                        <div className="typing-dots">
                                            <span></span><span></span><span></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Chat Input */}
                        <form onSubmit={handleSubmit} className="chat-input-form">
                            <div className="chat-input-wrapper">
                                <textarea
                                    ref={textareaRef}
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder={file ? "Ask about your resume..." : "Upload a resume first"}
                                    disabled={!file || isLoading}
                                    rows={1}
                                />
                                <button
                                    type="submit"
                                    className="send-btn"
                                    disabled={!file || !inputValue.trim() || isLoading}
                                >
                                    <Send size={20} />
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
