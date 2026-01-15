"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function AuthCallbackPage() {
    const router = useRouter();

    useEffect(() => {
        const handleCallback = async () => {
            const { data: { session }, error } = await supabase.auth.getSession();

            if (error) {
                console.error("Auth callback error:", error);
                router.push("/login?error=auth_failed");
                return;
            }

            if (session) {
                // Check if user has completed onboarding
                const { data: profile } = await supabase
                    .from("profiles")
                    .select("career_stage")
                    .eq("id", session.user.id)
                    .single();

                if (!profile?.career_stage) {
                    // New user, needs onboarding
                    router.push("/onboarding");
                } else {
                    // Existing user, go to main app
                    router.push("/");
                }
            } else {
                router.push("/login");
            }
        };

        handleCallback();
    }, [router]);

    return (
        <div className="auth-callback">
            <div className="callback-loading">
                <div className="spinner"></div>
                <p>Completing sign in...</p>
            </div>
        </div>
    );
}
