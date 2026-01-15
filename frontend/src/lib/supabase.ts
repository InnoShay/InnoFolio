import { createClient, SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

// Create a mock client if credentials are not available
let supabase: SupabaseClient;

if (supabaseUrl && supabaseAnonKey) {
    supabase = createClient(supabaseUrl, supabaseAnonKey);
} else {
    // Create a dummy client that won't throw errors
    // This allows the app to work without Supabase for basic chat functionality
    console.warn("Supabase credentials not configured. Auth features will be disabled.");
    supabase = {
        auth: {
            getSession: async () => ({ data: { session: null }, error: null }),
            onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => { } } } }),
            signUp: async () => ({ data: { user: null, session: null }, error: new Error("Supabase not configured") }),
            signInWithPassword: async () => ({ data: { user: null, session: null }, error: new Error("Supabase not configured") }),
            signInWithOAuth: async () => ({ error: new Error("Supabase not configured") }),
            signOut: async () => ({ error: null }),
            getUser: async () => ({ data: { user: null }, error: null }),
        },
        from: () => ({
            select: () => ({ eq: () => ({ single: async () => ({ data: null, error: null }) }) }),
            upsert: async () => ({ error: null }),
        }),
    } as unknown as SupabaseClient;
}

export { supabase };
