"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
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
    ChevronRight,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Conversation {
    id: string;
    title: string;
    is_pinned: boolean;
    updated_at: string;
}

export function Sidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const { user, session, signOut, profile } = useAuth();
    const pathname = usePathname();

    useEffect(() => {
        if (session) {
            fetchConversations();
        }
    }, [session]);

    const fetchConversations = async () => {
        if (!session) return;

        try {
            const response = await fetch(`${API_URL}/api/conversations`, {
                headers: {
                    Authorization: `Bearer ${session.access_token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setConversations(data);
            }
        } catch (error) {
            console.error("Failed to fetch conversations:", error);
        }
    };

    const navItems = [
        { href: "/", icon: MessageSquare, label: "Chat" },
        { href: "/resume", icon: FileText, label: "Resume Analysis" },
    ];

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

                {/* Conversations */}
                {user && conversations.length > 0 && (
                    <div className="sidebar-section">
                        <h3 className="section-title">Recent Chats</h3>
                        <div className="conversation-list">
                            {conversations.slice(0, 5).map((conv) => (
                                <Link
                                    key={conv.id}
                                    href={`/chat/${conv.id}`}
                                    className="conversation-item"
                                    onClick={() => setIsOpen(false)}
                                >
                                    <span className="conv-title">{conv.title}</span>
                                    {conv.is_pinned && <Pin size={12} />}
                                </Link>
                            ))}
                        </div>
                    </div>
                )}

                {/* User section */}
                <div className="sidebar-footer">
                    {user ? (
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
                            <button onClick={() => signOut()} className="logout-btn" title="Sign out">
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
