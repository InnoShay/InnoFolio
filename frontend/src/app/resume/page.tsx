"use client";

import Link from "next/link";
import { FileText, ExternalLink, Upload, CheckCircle } from "lucide-react";

const HIRESIGHT_URL = "https://hiresight-delta.vercel.app/";

export default function ResumePage() {
    const features = [
        "AI-powered resume scoring (1-100)",
        "Section-by-section analysis",
        "ATS compatibility check",
        "Improvement suggestions",
        "Grammar and clarity feedback",
    ];

    return (
        <div className="resume-container">
            <div className="resume-header">
                <h1>📄 Resume Analysis</h1>
                <p>Get AI-powered feedback on your resume</p>
            </div>

            <div className="resume-redirect-card">
                <div className="redirect-icon">
                    <FileText size={64} />
                </div>

                <h2>Analyze Your Resume with HireSight</h2>
                <p className="redirect-description">
                    We've built a dedicated AI resume analysis tool that provides comprehensive
                    feedback on your resume, including scoring, ATS compatibility, and
                    improvement suggestions.
                </p>

                <div className="features-list">
                    {features.map((feature, index) => (
                        <div key={index} className="feature-item">
                            <CheckCircle size={18} />
                            <span>{feature}</span>
                        </div>
                    ))}
                </div>

                <a
                    href={HIRESIGHT_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hiresight-button"
                >
                    <Upload size={20} />
                    Open HireSight Resume Analyzer
                    <ExternalLink size={16} />
                </a>

                <p className="redirect-note">
                    Opens in a new tab • Free to use • No signup required
                </p>
            </div>

            <div className="resume-tips-section">
                <h3>💡 Quick Resume Tips</h3>
                <div className="tips-grid">
                    <div className="tip-card">
                        <span className="tip-icon">📊</span>
                        <h4>Quantify Achievements</h4>
                        <p>Use numbers to show impact: "Increased sales by 25%"</p>
                    </div>
                    <div className="tip-card">
                        <span className="tip-icon">🎯</span>
                        <h4>Tailor for Each Job</h4>
                        <p>Match keywords from the job description</p>
                    </div>
                    <div className="tip-card">
                        <span className="tip-icon">✍️</span>
                        <h4>Use Action Verbs</h4>
                        <p>Start bullets with: Led, Developed, Achieved</p>
                    </div>
                    <div className="tip-card">
                        <span className="tip-icon">📝</span>
                        <h4>Keep it Concise</h4>
                        <p>1 page for freshers, 2 pages max for experienced</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
