"use client";

import { useState, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { Upload, FileText, CheckCircle, AlertTriangle, Loader2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AnalysisResult {
    id: string;
    filename: string;
    score: number;
    summary: string;
    sections: Record<string, any>;
    strengths: string[];
    improvements: string[];
    keywords: string[];
    ats_compatibility?: { score: number; issues: string[] };
    grammar_issues?: { original: string; suggested: string; issue: string }[];
}

export default function ResumePage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState("");
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { user, session } = useAuth();
    const router = useRouter();

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            if (selectedFile.size > 5 * 1024 * 1024) {
                setError("File must be less than 5MB");
                return;
            }
            setFile(selectedFile);
            setError("");
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            if (!droppedFile.type.includes("pdf") && !droppedFile.name.endsWith(".docx")) {
                setError("Only PDF and DOCX files are allowed");
                return;
            }
            setFile(droppedFile);
            setError("");
        }
    };

    const handleAnalyze = async () => {
        if (!file || !session) return;

        setUploading(true);
        setError("");

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch(`${API_URL}/api/resume/analyze-direct`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${session.access_token}`,
                },
                body: formData,
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Analysis failed");
            }

            const result = await response.json();
            setAnalysis(result);
        } catch (err: any) {
            setError(err.message || "Failed to analyze resume");
        }

        setUploading(false);
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return "score-excellent";
        if (score >= 60) return "score-good";
        if (score >= 40) return "score-fair";
        return "score-poor";
    };

    if (!user) {
        return (
            <div className="resume-container">
                <div className="resume-login-prompt">
                    <h2>Sign in to analyze your resume</h2>
                    <p>Get AI-powered feedback and a score for your resume</p>
                    <button onClick={() => router.push("/login")} className="auth-button primary">
                        Sign In
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="resume-container">
            <div className="resume-header">
                <h1>📄 Resume Analysis</h1>
                <p>Upload your resume and get AI-powered feedback</p>
            </div>

            {!analysis ? (
                <div className="upload-section">
                    <div
                        className={`upload-dropzone ${file ? "has-file" : ""}`}
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

                        {file ? (
                            <div className="file-selected">
                                <FileText size={48} />
                                <p className="file-name">{file.name}</p>
                                <p className="file-size">{(file.size / 1024).toFixed(1)} KB</p>
                            </div>
                        ) : (
                            <div className="upload-prompt">
                                <Upload size={48} />
                                <p>Drag and drop your resume here</p>
                                <p className="upload-hint">or click to browse</p>
                                <p className="upload-formats">PDF or DOCX, max 5MB</p>
                            </div>
                        )}
                    </div>

                    {error && <div className="upload-error">{error}</div>}

                    <button
                        onClick={handleAnalyze}
                        disabled={!file || uploading}
                        className="analyze-button"
                    >
                        {uploading ? (
                            <>
                                <Loader2 className="animate-spin" size={20} />
                                Analyzing...
                            </>
                        ) : (
                            <>Analyze Resume</>
                        )}
                    </button>
                </div>
            ) : (
                <div className="analysis-results">
                    {/* Score Card */}
                    <div className="score-card">
                        <div className={`score-circle ${getScoreColor(analysis.score)}`}>
                            <span className="score-number">{analysis.score}</span>
                            <span className="score-label">/100</span>
                        </div>
                        <h2>Resume Score</h2>
                        <p className="score-summary">{analysis.summary}</p>
                    </div>

                    {/* Strengths */}
                    <div className="analysis-section">
                        <h3>💪 Strengths</h3>
                        <ul className="strengths-list">
                            {analysis.strengths.map((strength, i) => (
                                <li key={i}>
                                    <CheckCircle size={16} />
                                    {strength}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Improvements */}
                    <div className="analysis-section">
                        <h3>📈 Improvements</h3>
                        <ul className="improvements-list">
                            {analysis.improvements.map((improvement, i) => (
                                <li key={i}>
                                    <AlertTriangle size={16} />
                                    {improvement}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Section Scores */}
                    {analysis.sections && Object.keys(analysis.sections).length > 0 && (
                        <div className="analysis-section">
                            <h3>📊 Section Analysis</h3>
                            <div className="section-scores">
                                {Object.entries(analysis.sections).map(([key, section]: [string, any]) => (
                                    <div key={key} className="section-score-item">
                                        <div className="section-name">{key.replace(/_/g, " ")}</div>
                                        <div className="section-score-bar">
                                            <div
                                                className="section-score-fill"
                                                style={{ width: `${(section.score || 0) * 10}%` }}
                                            ></div>
                                        </div>
                                        <span className="section-score-value">{section.score}/10</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Keywords */}
                    {analysis.keywords && analysis.keywords.length > 0 && (
                        <div className="analysis-section">
                            <h3>🔑 Key Skills Detected</h3>
                            <div className="keywords-list">
                                {analysis.keywords.map((keyword, i) => (
                                    <span key={i} className="keyword-tag">{keyword}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ATS Compatibility */}
                    {analysis.ats_compatibility && (
                        <div className="analysis-section">
                            <h3>🤖 ATS Compatibility</h3>
                            <div className="ats-score">
                                Score: {analysis.ats_compatibility.score}/10
                            </div>
                            {analysis.ats_compatibility.issues.length > 0 && (
                                <ul className="ats-issues">
                                    {analysis.ats_compatibility.issues.map((issue, i) => (
                                        <li key={i}>{issue}</li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    )}

                    <button
                        onClick={() => {
                            setAnalysis(null);
                            setFile(null);
                        }}
                        className="analyze-another-button"
                    >
                        Analyze Another Resume
                    </button>
                </div>
            )}
        </div>
    );
}
