"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { supabase } from "@/lib/supabase";
import {
    MessageSquare,
    FileText,
    User,
    LogOut,
    Menu,
    X,
    Plus,
    Pin,
    Trash2,
} from "lucide-react";

interface Conversation {
    id: string;
    title: string;
    is_pinned: boolean;
    updated_at: string;
}

export function Sidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const { user, session, signOut, profile, isLoading } = useAuth();
    const pathname = usePathname();
    const router = useRouter();

    useEffect(() => {
        if (user && session) {
            fetchConversations();
        }
    }, [user, session]);

    const fetchConversations = async () => {
        if (!session) return;

        try {
            const { data, error } = await supabase
                .from("conversations")
                .select("*")
                .order("updated_at", { ascending: false })
                .limit(10);

            if (!error && data) {
                setConversations(data);
            }
        } catch (error) {
            console.error("Failed to fetch conversations:", error);
        }
    };

    const createNewChat = async () => {
        if (!session || !user) {
            router.push("/login");
            return;
        }

        try {
            const { data, error } = await supabase
                .from("conversations")
                .insert({ user_id: user.id, title: "New Chat" })
                .select()
                .single();

            if (!error && data) {
                setConversations(prev => [data, ...prev]);
                router.push(`/chat/${data.id}`);
            }
        } catch (error) {
            console.error("Failed to create conversation:", error);
        }
    };

    const deleteConversation = async (id: string, e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();

        try {
            await supabase.from("conversations").delete().eq("id", id);
            setConversations(prev => prev.filter(c => c.id !== id));
        } catch (error) {
            console.error("Failed to delete conversation:", error);
        }
    };

    const handleSignOut = async () => {
        await signOut();
        router.push("/login");
    };

    const navItems = [
        { href: "/", icon: MessageSquare, label: "Chat" },
        { href: "/resume", icon: FileText, label: "Resume Analysis" },
    ];

    // Don't show full sidebar on login/onboarding pages
    const isAuthPage = pathname?.startsWith("/login") || pathname?.startsWith("/onboarding") || pathname?.startsWith("/auth");
    if (isAuthPage) {
        return null;
    }

    return (
        <>
            {/* Mobile menu button */}
            <button className="mobile-menu-btn" onClick={() => setIsOpen(!isOpen)}>
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Sidebar */}
            <aside className={`sidebar ${isOpen ? "open" : ""}`}>
                <div className="sidebar-header">
                    <Link href="/" className="sidebar-logo">
                        <span className="logo-icon">📋</span>
                        <span className="logo-text">InnoFolio</span>
                    </Link>
                </div>

                {/* New Chat Button */}
                {user && (
                    <button className="new-chat-btn" onClick={createNewChat}>
                        <Plus size={18} />
                        <span>New Chat</span>
                    </button>
                )}

                {/* Navigation */}
                <nav className="sidebar-nav">
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`nav-item ${pathname === item.href ? "active" : ""}`}
                            onClick={() => setIsOpen(false)}
                        >
                            <item.icon size={20} />
                            <span>{item.label}</span>
                        </Link>
                    ))}
                </nav>

                {/* Recent Conversations */}
                {user && conversations.length > 0 && (
                    <div className="sidebar-section">
                        <h3 className="section-title">Recent Chats</h3>
                        <div className="conversation-list">
                            {conversations.map((conv) => (
                                <Link
                                    key={conv.id}
                                    href={`/chat/${conv.id}`}
                                    className={`conversation-item ${pathname === `/chat/${conv.id}` ? "active" : ""}`}
                                    onClick={() => setIsOpen(false)}
                                >
                                    <span className="conv-title">{conv.title}</span>
                                    <div className="conv-actions">
                                        {conv.is_pinned && <Pin size={12} />}
                                        <button
                                            className="delete-conv"
                                            onClick={(e) => deleteConversation(conv.id, e)}
                                        >
                                            <Trash2 size={12} />
                                        </button>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </div>
                )}

                {/* User section */}
                <div className="sidebar-footer">
                    {isLoading ? (
                        <div className="loading-user">Loading...</div>
                    ) : user ? (
                        <div className="user-menu">
                            <div className="user-info">
                                <div className="user-avatar">
                                    {profile?.full_name?.[0] || user.email?.[0]?.toUpperCase()}
                                </div>
                                <div className="user-details">
                                    <span className="user-name">{profile?.full_name || "User"}</span>
                                    <span className="user-email">{user.email}</span>
                                </div>
                            </div>
                            <button onClick={handleSignOut} className="logout-btn" title="Sign out">
                                <LogOut size={18} />
                            </button>
                        </div>
                    ) : (
                        <Link href="/login" className="signin-btn">
                            <User size={18} />
                            <span>Sign In</span>
                        </Link>
                    )}
                </div>
            </aside>

            {/* Overlay for mobile */}
            {isOpen && <div className="sidebar-overlay" onClick={() => setIsOpen(false)} />}
        </>
    );
}
