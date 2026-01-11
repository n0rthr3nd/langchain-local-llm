import React from 'react';
import { FileUploader } from './FileUploader';

export const KnowledgeBaseView: React.FC = () => {
    return (
        <div className="flex flex-col h-full bg-gemini-bg p-8 overflow-y-auto scrollbar-thin scrollbar-thumb-gemini-border">
            <header className="mb-8 max-w-4xl mx-auto w-full">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-purple-500/10 rounded-lg">
                        <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                    </div>
                    <h1 className="text-2xl font-bold text-gemini-text-primary">Knowledge Base</h1>
                </div>
                <p className="text-gemini-text-secondary text-sm max-w-2xl pl-12">
                    Manage context documents. Upload PDF, Markdown, or TXT files to ingest them into the vector database for Retrieval-Augmented Generation (RAG).
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto w-full">
                {/* Upload Section */}
                <div className="bg-gemini-surface rounded-2xl border border-gemini-border p-6 shadow-sm hover:shadow-md transition-shadow">
                    <h2 className="text-lg font-semibold text-gemini-text-primary mb-4 flex items-center gap-2">
                        <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        Ingest Documents
                    </h2>
                    <p className="text-gemini-text-secondary text-sm mb-6">
                        Select a file to process. Content will be chunked and stored in ChromaDB for retrieval during conversations.
                    </p>

                    <div className="bg-gemini-bg/50 rounded-xl p-4 border border-gemini-border border-dashed">
                        <FileUploader />
                    </div>

                    <div className="mt-6 p-4 bg-blue-500/5 border border-blue-500/10 rounded-xl">
                        <h4 className="text-xs font-semibold text-blue-400 mb-1 uppercase tracking-wide">Optimization Tip</h4>
                        <p className="text-xs text-blue-300/80 leading-relaxed">
                            For RPi 5 (8GB), we recommend <code className="bg-blue-900/30 px-1 py-0.5 rounded mx-1 text-blue-200">nomic-embed-text</code>.
                            Efficient and high-quality vector representations.
                        </p>
                    </div>
                </div>

                {/* Info / Stats Section */}
                <div className="bg-gemini-surface rounded-2xl border border-gemini-border p-6 shadow-sm hover:shadow-md transition-shadow">
                    <h2 className="text-lg font-semibold text-gemini-text-primary mb-4 flex items-center gap-2">
                        <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        How RAG Works
                    </h2>
                    <div className="space-y-4 text-sm text-gemini-text-secondary">
                        <div className="flex gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gemini-bg border border-gemini-border flex items-center justify-center text-xs font-medium">1</span>
                            <p><span className="font-semibold text-gemini-text-primary">Ingest:</span> Document is read and split into overlapping chunks.</p>
                        </div>
                        <div className="flex gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gemini-bg border border-gemini-border flex items-center justify-center text-xs font-medium">2</span>
                            <p><span className="font-semibold text-gemini-text-primary">Embedding:</span> Chunks are converted to vector numbers.</p>
                        </div>
                        <div className="flex gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gemini-bg border border-gemini-border flex items-center justify-center text-xs font-medium">3</span>
                            <p><span className="font-semibold text-gemini-text-primary">Store:</span> Vectors saved locally in ChromaDB.</p>
                        </div>
                        <div className="flex gap-3">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gemini-bg border border-gemini-border flex items-center justify-center text-xs font-medium">4</span>
                            <p><span className="font-semibold text-gemini-text-primary">Retrieve:</span> Queries search for similar chunks to provide context.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
