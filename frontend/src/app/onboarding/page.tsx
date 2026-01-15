"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

const careerStages = [
    { id: "student", label: "Student", icon: "🎓" },
    { id: "fresher", label: "Fresh Graduate", icon: "🌱" },
    { id: "experienced", label: "Working Professional", icon: "💼" },
    { id: "career_changer", label: "Career Changer", icon: "🔄" },
];

export default function OnboardingPage() {
    const [step, setStep] = useState(1);
    const [fullName, setFullName] = useState("");
    const [careerStage, setCareerStage] = useState("");
    const [targetRole, setTargetRole] = useState("");
    const [loading, setLoading] = useState(false);
    const { user, profile, updateProfile } = useAuth();
    const router = useRouter();

    const handleComplete = async () => {
        setLoading(true);

        const { error } = await updateProfile({
            full_name: fullName || profile?.full_name,
            career_stage: careerStage,
            target_role: targetRole,
        });

        if (!error) {
            router.push("/");
        }

        setLoading(false);
    };

    return (
        <div className="onboarding-container">
            <div className="onboarding-card">
                <div className="onboarding-progress">
                    <div className={`step ${step >= 1 ? "active" : ""}`}>1</div>
                    <div className="step-line"></div>
                    <div className={`step ${step >= 2 ? "active" : ""}`}>2</div>
                    <div className="step-line"></div>
                    <div className={`step ${step >= 3 ? "active" : ""}`}>3</div>
                </div>

                {step === 1 && (
                    <div className="onboarding-step">
                        <h1>Welcome to InnoFolio! 👋</h1>
                        <p>Let&apos;s personalize your experience. What&apos;s your name?</p>

                        <div className="form-group">
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                placeholder="Your name"
                                className="onboarding-input"
                            />
                        </div>

                        <button
                            onClick={() => setStep(2)}
                            className="onboarding-button"
                            disabled={!fullName.trim()}
                        >
                            Continue
                        </button>
                    </div>
                )}

                {step === 2 && (
                    <div className="onboarding-step">
                        <h1>Where are you in your career?</h1>
                        <p>This helps me give you more relevant advice.</p>

                        <div className="career-stages">
                            {careerStages.map((stage) => (
                                <button
                                    key={stage.id}
                                    onClick={() => setCareerStage(stage.id)}
                                    className={`stage-card ${careerStage === stage.id ? "selected" : ""}`}
                                >
                                    <span className="stage-icon">{stage.icon}</span>
                                    <span className="stage-label">{stage.label}</span>
                                </button>
                            ))}
                        </div>

                        <div className="onboarding-buttons">
                            <button onClick={() => setStep(1)} className="onboarding-button secondary">
                                Back
                            </button>
                            <button
                                onClick={() => setStep(3)}
                                className="onboarding-button"
                                disabled={!careerStage}
                            >
                                Continue
                            </button>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="onboarding-step">
                        <h1>What&apos;s your target role?</h1>
                        <p>I&apos;ll tailor my advice to help you get there.</p>

                        <div className="form-group">
                            <input
                                type="text"
                                value={targetRole}
                                onChange={(e) => setTargetRole(e.target.value)}
                                placeholder="e.g., Software Engineer, Product Manager"
                                className="onboarding-input"
                            />
                        </div>

                        <div className="onboarding-buttons">
                            <button onClick={() => setStep(2)} className="onboarding-button secondary">
                                Back
                            </button>
                            <button
                                onClick={handleComplete}
                                className="onboarding-button"
                                disabled={loading}
                            >
                                {loading ? "Saving..." : "Get Started 🚀"}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
