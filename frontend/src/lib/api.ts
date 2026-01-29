const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

export interface ChatRequest {
    message: string;
    conversation_history?: ChatMessage[];
    session_id?: string;
}

export interface ChatResponse {
    response: string;
    sources: string[];
    session_id: string;
}

export interface Suggestion {
    icon: string;
    title: string;
    prompt: string;
}

/**
 * Send a chat message and get a response
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
    });

    if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Stream a chat response for real-time typing effect
 */
export async function* streamChatMessage(
    request: ChatRequest
): AsyncGenerator<string, void, unknown> {
    const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
    });

    if (!response.ok) {
        throw new Error(`Chat stream request failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
        throw new Error("No response body");
    }

    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
            if (line.startsWith("data: ")) {
                const data = line.slice(6);
                if (data === "[DONE]") {
                    return;
                }
                try {
                    const parsed = JSON.parse(data);
                    if (parsed.content) {
                        yield parsed.content;
                    }
                } catch {
                    // Skip invalid JSON
                }
            }
        }
    }
}

/**
 * Get starter prompt suggestions
 */
export async function getSuggestions(): Promise<Suggestion[]> {
    try {
        const response = await fetch(`${API_URL}/api/suggestions`);
        if (!response.ok) {
            throw new Error("Failed to fetch suggestions");
        }
        const data = await response.json();
        return data.suggestions;
    } catch {
        // Return default suggestions if API is not available
        return [
            {
                icon: "📄",
                title: "Resume Review",
                prompt: "How can I improve my resume for a software engineering role?",
            },
            {
                icon: "🎯",
                title: "Interview Prep",
                prompt: "What are the most common interview questions for freshers?",
            },
            {
                icon: "💼",
                title: "Job Search",
                prompt: "What's the best strategy for finding my first job?",
            },
            {
                icon: "🗺️",
                title: "Career Path",
                prompt: "What skills should I learn to become a full-stack developer?",
            },
        ];
    }
}

/**
 * Health check for the API
 */
export async function checkApiHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}
