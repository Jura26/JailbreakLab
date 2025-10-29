import './App.css'
import React, { useState } from 'react';
import { Shield, Sword, Brain, Send, Info } from 'lucide-react';
import attacks from './components/attacks';
import defenses from "./components/defenses"
import models from "./components/models"

function App() {
    const [selectedAttack, setSelectedAttack] = useState(attacks[0]);
    const [selectedDefense, setSelectedDefense] = useState(defenses[0]);
    const [selectedModel, setSelectedModel] = useState(models[0]);
    const [message, setMessage] = useState('');
    const [prompts] = useState<Array<{
        text: string;
        timestamp: string;
    }>>([]);

    const handleSend = async () => {
        if (!message.trim()) return;

        try {
            const response = await fetch("http://localhost:3000/api/prompt", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    prompt: message,
                    attack: selectedAttack.id,
                    defense: selectedDefense.id,
                    model: selectedModel.id,
                }),
            });

            const data = await response.json();

            console.log("Odgovor backend-a:", data);
        } catch (error) {
            console.error("Greška prilikom slanja POST zahtjeva:", error);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };
    return <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-5">
        <div className="max-w-7xl mx-auto">

            {/* Configuration Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Attack Selection */}
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <div className="flex items-center gap-2 mb-4">
                        <Sword className="text-red-400" size={24} />
                        <h2 className="text-xl font-semibold text-white">Attack Type</h2>
                    </div>
                    <select value={selectedAttack.id} onChange={e => setSelectedAttack(attacks.find(a => a.id === e.target.value) || attacks[0])} className="w-full bg-white/5 border border-white/30 rounded-lg px-4 py-2 text-white mb-4 focus:outline-none focus:ring-2 focus:ring-red-400">
                        {attacks.map(attack => <option key={attack.id} value={attack.id} className="bg-slate-800">
                            {attack.name}
                        </option>)}
                    </select>
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                            <Info className="text-red-400 flex-shrink-0 mt-1" size={16} />
                            <p className="text-sm text-red-100">
                                {selectedAttack.description}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Defense Selection */}
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <div className="flex items-center gap-2 mb-4">
                        <Shield className="text-green-400" size={24} />
                        <h2 className="text-xl font-semibold text-white">Defense Type</h2>
                    </div>
                    <select value={selectedDefense.id} onChange={e => setSelectedDefense(defenses.find(d => d.id === e.target.value) || defenses[0])} className="w-full bg-white/5 border border-white/30 rounded-lg px-4 py-2 text-white mb-4 focus:outline-none focus:ring-2 focus:ring-green-400">
                        {defenses.map(defense => <option key={defense.id} value={defense.id} className="bg-slate-800">
                            {defense.name}
                        </option>)}
                    </select>
                    <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                            <Info className="text-green-400 flex-shrink-0 mt-1" size={16} />
                            <p className="text-sm text-green-100">
                                {selectedDefense.description}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Model Selection */}
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <div className="flex items-center gap-2 mb-4">
                        <Brain className="text-blue-400" size={24} />
                        <h2 className="text-xl font-semibold text-white">Model</h2>
                    </div>
                    <select value={selectedModel.id} onChange={e => setSelectedModel(models.find(m => m.id === e.target.value) || models[0])} className="w-full bg-white/5 border border-white/30 rounded-lg px-4 py-2 text-white mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400">
                        {models.map(model => <option key={model.id} value={model.id} className="bg-slate-800">
                            {model.name}
                        </option>)}
                    </select>
                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                            <Info className="text-blue-400 flex-shrink-0 mt-1" size={16} />
                            <p className="text-sm text-blue-100">
                                {selectedModel.description}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Prompt Display Area */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 mb-6 h-[300px]">
                <h2 className="text-xl font-semibold text-white mb-4">
                    Prompt History
                </h2>
                <div className="space-y-3 max-h-[200px] overflow-y-auto">
                    {prompts.length === 0 ?
                        <div className="text-center text-purple-300 py-12">
                            <p>No prompts sent yet. Type a message below to get started.</p>
                        </div>
                        : prompts.map((prompt, index) =>
                            <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs text-purple-300">{prompt.timestamp}</span>
                                    <div className="flex gap-2 text-xs">
                                        <span className="px-2 py-1 bg-red-500/20 text-red-300 rounded">
                                            {selectedAttack.name}
                                        </span>
                                        <span className="px-2 py-1 bg-green-500/20 text-green-300 rounded">
                                            {selectedDefense.name}
                                        </span>
                                        <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded">
                                            {selectedModel.name}
                                        </span>
                                    </div>
                                </div>
                                <p className="text-white wrap-break-word">{prompt.text}</p>
                            </div>)}
                </div>
            </div>

            {/* Message Input Area */}
            <div className="bg-white/10 h-1/6 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h2 className="text-xl font-semibold text-white mb-4">Send Prompt</h2>
                <div className="flex gap-4">
                    <textarea value={message} onChange={e => setMessage(e.target.value)} onKeyPress={handleKeyPress} placeholder="Type your test prompt here..." className="flex-1 bg-white/5 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none" rows={1} />
                    <button onClick={handleSend} disabled={!message.trim()} className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 self-end">
                        <Send size={20} />
                        Send
                    </button>
                </div>
            </div>
        </div>
    </div>;
}

export default App
