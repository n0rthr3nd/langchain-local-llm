import React from 'react';
import { FileUploader } from './FileUploader';

export const KnowledgeBaseView: React.FC = () => {
    return (
        <div className="flex flex-col h-screen bg-chat-bg p-8 overflow-y-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Base de Conocimiento (RAG)</h1>
                <p className="text-gray-400 max-w-2xl">
                    Gestiona los documentos que el asistente utiliza como contexto.
                    Sube archivos PDF, Markdown o TXT para ingestarlos en la base de datos vectorial.
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Upload Section */}
                <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                        <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        Ingestar Documentos
                    </h2>
                    <p className="text-gray-400 text-sm mb-6">
                        Selecciona un archivo para procesarlo. El contenido será dividido en fragmentos (chunks) y almacenado
                        en ChromaDB para ser recuperado durante las conversaciones.
                    </p>

                    <div className="bg-gray-900/50 rounded-lg p-4">
                        <FileUploader />
                    </div>

                    <div className="mt-6 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
                        <h4 className="text-sm font-medium text-blue-300 mb-2">Nota sobre Modelos (RPi 5)</h4>
                        <p className="text-xs text-blue-200/80 leading-relaxed">
                            Para la Raspberry Pi 5 (8GB), el modelo de embeddings recomendado es
                            <code className="bg-blue-900/50 px-1 py-0.5 rounded mx-1">nomic-embed-text</code>.
                            Es altamente eficiente y produce representaciones vectoriales de alta calidad con bajo consumo de memoria.
                        </p>
                    </div>
                </div>

                {/* Info / Stats Section (Placeholder for future stats) */}
                <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 shadow-lg">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                        <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        ¿Cómo funciona?
                    </h2>
                    <div className="space-y-4 text-sm text-gray-300">
                        <p>
                            <span className="font-semibold text-white">1. Ingesta:</span> El documento se lee y se divide en fragmentos de texto solapados.
                        </p>
                        <p>
                            <span className="font-semibold text-white">2. Embedding:</span> Cada fragmento se convierte en un vector numérico usando el modelo de embeddings.
                        </p>
                        <p>
                            <span className="font-semibold text-white">3. Almacenamiento:</span> Los vectores se guardan en ChromaDB (local).
                        </p>
                        <p>
                            <span className="font-semibold text-white">4. Recuperación:</span> Cuando preguntas algo en el chat (activando "Use Knowledge Base"), el sistema busca los fragmentos más similares a tu pregunta y los usa para responder.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
