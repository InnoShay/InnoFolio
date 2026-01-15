"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Loader2, ArrowRight, ArrowLeft } from "lucide-react";

const careerStages = [
    { id: "student", icon: "🎓", label: "Student" },
    { id: "fresher", icon: "🌱", label: "Fresh Graduate" },
    { id: "junior", icon: "💼", label: "1-3 Years Exp" },
    { id: "mid", icon: "📈", label: "4-7 Years Exp" },
    { id: "senior", icon: "⭐", label: "8+ Years Exp" },
    { id: "switcher", icon: "🔄", label: "Career Switcher" },
];

export default function OnboardingPage() {
    const [step, setStep] = useState(1);
    const [fullName, setFullName] = useState("");
    const [careerStage, setCareerStage] = useState("");
    const [targetRole, setTargetRole] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const { user, profile, updateProfile, refreshProfile, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !user) {
            router.push("/login");
        }
        if (profile?.full_name) {
            setFullName(profile.full_name);
        }
    }, [user, profile, isLoading, router]);

    const handleComplete = async () => {
        if (!fullName || !careerStage || !targetRole) {
            setError("Please complete all fields");
            return;
        }

        setLoading(true);
        setError("");

        const { error: updateError } = await updateProfile({
            full_name: fullName,
            career_stage: careerStage,
            target_role: targetRole,
        });

        if (updateError) {
            setError(updateError.message);
            setLoading(false);
            return;
        }

        await refreshProfile();
        router.push("/");
    };

    const canProceed = () => {
        if (step === 1) return fullName.length >= 2;
        if (step === 2) return careerStage !== "";
        if (step === 3) return targetRole.length >= 2;
        return false;
    };

    if (isLoading) {
        return (
            <div className="onboarding-container">
                <div className="onboarding-loading">
                    <Loader2 size={32} className="spin" />
                </div>
            </div>
        );
    }

    return (
        <div className="onboarding-container">
            <div className="onboarding-card">
                {/* Progress */}
                <div className="onboarding-progress">
                    {[1, 2, 3].map((s) => (
                        <div key={s} className={`progress-step ${step >= s ? "active" : ""} ${step === s ? "current" : ""}`}>
                            {s}
                        </div>
                    ))}
                </div>

                {/* Step 1: Name */}
                {step === 1 && (
                    <div className="onboarding-step">
                        <h1>👋 Welcome to InnoFolio!</h1>
                        <p>Let's personalize your experience. What's your name?</p>
                        <input
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder="Enter your full name"
                            className="onboarding-input"
                            autoFocus
                        />
                    </div>
                )}

                {/* Step 2: Career Stage */}
                {step === 2 && (
                    <div className="onboarding-step">
                        <h1>📊 Where are you in your career?</h1>
                        <p>This helps us give you personalized advice</p>
                        <div className="stage-grid">
                            {careerStages.map((stage) => (
                                <button
                                    key={stage.id}
                                    className={`stage-option ${careerStage === stage.id ? "selected" : ""}`}
                                    onClick={() => setCareerStage(stage.id)}
                                >
                                    <span className="stage-icon">{stage.icon}</span>
                                    <span className="stage-label">{stage.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Step 3: Target Role */}
                {step === 3 && (
                    <div className="onboarding-step">
                        <h1>🎯 What role are you aiming for?</h1>
                        <p>This is the job title you want to achieve</p>
                        <input
                            type="text"
                            value={targetRole}
                            onChange={(e) => setTargetRole(e.target.value)}
                            placeholder="e.g., Software Engineer, Product Manager"
                            className="onboarding-input"
                            autoFocus
                        />
                    </div>
                )}

                {error && <div className="onboarding-error">{error}</div>}

                {/* Navigation */}
                <div className="onboarding-nav">
                    {step > 1 && (
                        <button
                            className="onboarding-btn secondary"
                            onClick={() => setStep(step - 1)}
                        >
                            <ArrowLeft size={18} />
                            Back
                        </button>
                    )}

                    {step < 3 ? (
                        <button
                            className="onboarding-btn primary"
                            onClick={() => setStep(step + 1)}
                            disabled={!canProceed()}
                        >
                            Continue
                            <ArrowRight size={18} />
                        </button>
                    ) : (
                        <button
                            className="onboarding-btn primary"
                            onClick={handleComplete}
                            disabled={!canProceed() || loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 size={18} className="spin" />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    Get Started
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
