"use client";

import "./App.css";
import type React from "react";
import { useState } from "react";
import {
   Shield,
   Sword,
   Brain,
   Send,
   Info,
   CheckCircle,
   XCircle,
   Zap,
} from "lucide-react";
import attacks from "./components/attacks";
import defenses from "./components/defenses";
import models from "./components/models";

interface Attack {
   id: string;
   name: string;
   description: string;
}

interface Defense {
   id: string;
   name: string;
   description: string;
}

interface Model {
   id: string;
   name: string;
   description: string;
}

interface Prompt {
   text: string;
   timestamp: string;
   attack: Attack;
   defense: Defense;
   model: Model;
   scriptOutput: string;
   progress?: number;
   gpuInfo?: string;
   isBlocked?: boolean;
}

function App() {
   const [selectedAttack, setSelectedAttack] = useState<Attack>(attacks[0]);
   const [selectedDefense, setSelectedDefense] = useState<Defense>(defenses[0]);
   const [selectedModel, setSelectedModel] = useState<Model>(models[0]);
   const [message, setMessage] = useState("");
   const [prompts, setPrompts] = useState<Prompt[]>([]);

   const handleSend = async () => {
      if (!message.trim()) return;

      const currentMessage = message;
      setMessage("");

      let newIndex: number;
      setPrompts((prev) => {
         newIndex = prev.length;
         return [
            ...prev,
            {
               text: currentMessage,
               timestamp: new Date().toLocaleTimeString(),
               attack: selectedAttack,
               defense: selectedDefense,
               model: selectedModel,
               scriptOutput: "",
               progress: 0,
               gpuInfo: "",
            },
         ];
      });

      try {
         const response = await fetch(
            "http://34.16.168.145:8000/api/prompt/stream",
            {
               method: "POST",
               headers: { "Content-Type": "application/json" },
               body: JSON.stringify({
                  prompt: currentMessage,
                  attack: selectedAttack.id,
                  defense: selectedDefense.id,
                  model: selectedModel.id,
                  isBlocked: false,
               }),
            }
         );

         if (!response.body) {
            const text = await response.text();
            setPrompts((prev) => {
               const copy = [...prev];
               copy[newIndex] = {
                  ...copy[newIndex],
                  scriptOutput: text,
                  progress: 100,
               };
               return copy;
            });
            return;
         }

         const reader = response.body.getReader();
         const decoder = new TextDecoder();
         let done = false;
         let localAccum = "";

         let gpuCapturedForThisPrompt = false;
         let blockedPrompt = false;

         while (!done) {
            const result = await reader.read();
            done = !!result.done;
            if (result.value) {
               const text = decoder.decode(result.value, { stream: true });
               const lines = text.split("\n");

               for (const line of lines) {
                  const trimmed = line.trim();
                  if (!trimmed) continue;

                  if (!blockedPrompt && trimmed.startsWith("Blocked input")) {
                     setPrompts((prev) => {
                        const copy = [...prev];
                        if (!copy[newIndex]) return prev;
                        copy[newIndex] = {
                           ...copy[newIndex],
                           isBlocked: true,
                        };
                        return copy;
                     });
                     blockedPrompt = true;
                     continue;
                  }
                  if (
                     !gpuCapturedForThisPrompt &&
                     (trimmed.startsWith("No compatible GPU") ||
                        trimmed.startsWith("GPU name:"))
                  ) {
                     setPrompts((prev) => {
                        const copy = [...prev];
                        if (!copy[newIndex]) return prev;
                        copy[newIndex] = {
                           ...copy[newIndex],
                           gpuInfo: trimmed,
                        };
                        return copy;
                     });
                     gpuCapturedForThisPrompt = true;
                     continue;
                  }

                  if (trimmed.startsWith("[PROGRESS]")) {
                     const percent = Number.parseFloat(
                        trimmed.replace("[PROGRESS]", "").trim()
                     );
                     if (!isNaN(percent)) {
                        setPrompts((prev) => {
                           const copy = [...prev];
                           if (!copy[newIndex]) return prev;
                           copy[newIndex] = {
                              ...copy[newIndex],
                              progress: percent,
                           };
                           return copy;
                        });
                     }
                  } else {
                     localAccum += line + "\n";
                     setPrompts((prev) => {
                        const copy = [...prev];
                        if (!copy[newIndex]) return prev;
                        copy[newIndex] = {
                           ...copy[newIndex],
                           scriptOutput: localAccum,
                        };
                        return copy;
                     });
                  }
               }
            }
         }

         setPrompts((prev) => {
            const copy = [...prev];
            if (!copy[newIndex]) return prev;
            copy[newIndex] = { ...copy[newIndex], progress: 100 };
            return copy;
         });
      } catch (err) {
         console.error("Streaming error:", err);
         setPrompts((prev) => {
            const copy = [...prev];
            if (!copy[newIndex]) return prev;
            copy[newIndex] = {
               ...copy[newIndex],
               scriptOutput: `Error: ${String(err)}`,
               progress: 0,
            };
            return copy;
         });
      }
   };

   const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
         e.preventDefault();
         handleSend();
      }
   };

   return (
      <div className="min-h-screen w-full bg-gradient-to-br from-[#0a0a0f] via-[#0f0f1a] to-[#0a0a0f] p-3 md:p-4">
         <div className="max-w-[1800px] mx-auto">
            <header className="mb-4 text-center">
               <div className="flex items-center justify-center gap-2 mb-2">
                  <Zap className="text-[#6366f1] w-7 h-7" />
                  <h1 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-[#f8fafc] to-[#cbd5e1] bg-clip-text text-transparent">
                     AI Security Tester
                  </h1>
               </div>
               <p className="text-[#94a3b8] text-sm max-w-2xl mx-auto leading-relaxed">
                  Test AI model vulnerabilities with various attack and defense
                  mechanisms
               </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr] gap-3 lg:gap-4">
               <div className="flex flex-col gap-3 h-[calc(100vh-180px)] overflow-y-auto">
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-6 border border-[#2d2d3d] shadow-2xl hover:border-[#ef4444]/30 transition-all duration-300 flex-1 flex flex-col justify-center">
                     <div className="flex items-center gap-2 mb-4">
                        <div className="bg-[#ef4444]/10 p-2 rounded-lg border border-[#ef4444]/20">
                           <Sword className="text-[#ef4444] w-5 h-5" />
                        </div>
                        <h2 className="text-lg font-bold text-[#f8fafc]">
                           Attack Vector
                        </h2>
                     </div>

                     <div className="relative mb-4">
                        <select
                           value={selectedAttack.id}
                           onChange={(e) =>
                              setSelectedAttack(
                                 attacks.find((a) => a.id === e.target.value) ||
                                    attacks[0]
                              )
                           }
                           className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-3 text-[#f8fafc] cursor-pointer hover:border-[#ef4444]/50 focus:border-[#ef4444] focus:outline-none font-medium text-base appearance-none pr-10 transition-all duration-200"
                           style={{
                              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23ef4444'%3E%3Cpath strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                              backgroundRepeat: "no-repeat",
                              backgroundPosition: "right 0.5rem center",
                              backgroundSize: "1.5rem 1.5rem",
                           }}
                        >
                           {attacks.map((attack) => (
                              <option
                                 key={attack.id}
                                 value={attack.id}
                                 className="bg-[#252532] py-2"
                              >
                                 {attack.name}
                              </option>
                           ))}
                        </select>
                     </div>

                     <div className="bg-[#ef4444]/5 border border-[#ef4444]/20 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                           <Info
                              className="text-[#ef4444] flex-shrink-0 mt-0.5"
                              size={16}
                           />
                           <p className="text-sm text-[#cbd5e1] leading-relaxed">
                              {selectedAttack.description}
                           </p>
                        </div>
                     </div>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-6 border border-[#2d2d3d] shadow-2xl hover:border-[#10b981]/30 transition-all duration-300 flex-1 flex flex-col justify-center">
                     <div className="flex items-center gap-2 mb-4">
                        <div className="bg-[#10b981]/10 p-2 rounded-lg border border-[#10b981]/20">
                           <Shield className="text-[#10b981] w-5 h-5" />
                        </div>
                        <h2 className="text-lg font-bold text-[#f8fafc]">
                           Defense Mechanism
                        </h2>
                     </div>

                     <div className="relative mb-4">
                        <select
                           value={selectedDefense.id}
                           onChange={(e) =>
                              setSelectedDefense(
                                 defenses.find(
                                    (d) => d.id === e.target.value
                                 ) || defenses[0]
                              )
                           }
                           className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-3 text-[#f8fafc] cursor-pointer hover:border-[#10b981]/50 focus:border-[#10b981] focus:outline-none font-medium text-base appearance-none pr-10 transition-all duration-200"
                           style={{
                              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2310b981'%3E%3Cpath strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                              backgroundRepeat: "no-repeat",
                              backgroundPosition: "right 0.5rem center",
                              backgroundSize: "1.5rem 1.5rem",
                           }}
                        >
                           {defenses.map((defense) => (
                              <option
                                 key={defense.id}
                                 value={defense.id}
                                 className="bg-[#252532] py-2"
                              >
                                 {defense.name}
                              </option>
                           ))}
                        </select>
                     </div>

                     <div className="bg-[#10b981]/5 border border-[#10b981]/20 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                           <Info
                              className="text-[#10b981] flex-shrink-0 mt-0.5"
                              size={16}
                           />
                           <p className="text-sm text-[#cbd5e1] leading-relaxed">
                              {selectedDefense.description}
                           </p>
                        </div>
                     </div>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-6 border border-[#2d2d3d] shadow-2xl hover:border-[#3b82f6]/30 transition-all duration-300 flex-1 flex flex-col justify-center">
                     <div className="flex items-center gap-2 mb-4">
                        <div className="bg-[#3b82f6]/10 p-2 rounded-lg border border-[#3b82f6]/20">
                           <Brain className="text-[#3b82f6] w-5 h-5" />
                        </div>
                        <h2 className="text-lg font-bold text-[#f8fafc]">
                           Target Model
                        </h2>
                     </div>

                     <div className="relative mb-4">
                        <select
                           value={selectedModel.id}
                           onChange={(e) =>
                              setSelectedModel(
                                 models.find((m) => m.id === e.target.value) ||
                                    models[0]
                              )
                           }
                           className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-3 text-[#f8fafc] cursor-pointer hover:border-[#3b82f6]/50 focus:border-[#3b82f6] focus:outline-none font-medium text-base appearance-none pr-10 transition-all duration-200"
                           style={{
                              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%233b82f6'%3E%3Cpath strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                              backgroundRepeat: "no-repeat",
                              backgroundPosition: "right 0.5rem center",
                              backgroundSize: "1.5rem 1.5rem",
                           }}
                        >
                           {models.map((model) => (
                              <option
                                 key={model.id}
                                 value={model.id}
                                 className="bg-[#252532] py-2"
                              >
                                 {model.name}
                              </option>
                           ))}
                        </select>
                     </div>

                     <div className="bg-[#3b82f6]/5 border border-[#3b82f6]/20 rounded-lg p-4">
                        <div className="flex items-start gap-2">
                           <Info
                              className="text-[#3b82f6] flex-shrink-0 mt-0.5"
                              size={16}
                           />
                           <p className="text-sm text-[#cbd5e1] leading-relaxed">
                              {selectedModel.description}
                           </p>
                        </div>
                     </div>
                  </div>
               </div>

               <div className="flex flex-col gap-3 h-[calc(100vh-180px)]">
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl flex-1 flex flex-col overflow-hidden">
                     <h2 className="text-xl font-bold text-[#f8fafc] mb-3 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#6366f1] animate-pulse" />
                        Execution History
                     </h2>

                     <div className="flex-1 overflow-y-auto pr-2 space-y-3">
                        {prompts.length === 0 ? (
                           <div className="h-full flex items-center justify-center">
                              <div className="text-center py-8">
                                 <div className="bg-[#6366f1]/10 w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-3 border border-[#6366f1]/20">
                                    <Send className="text-[#6366f1] w-7 h-7" />
                                 </div>
                                 <p className="text-[#94a3b8] text-lg font-medium mb-1">
                                    Ready to test
                                 </p>
                                 <p className="text-[#64748b] text-sm">
                                    Configure your attack, defense, and model,
                                    then send a prompt
                                 </p>
                              </div>
                           </div>
                        ) : (
                           prompts.map((prompt, idx) => (
                              <div
                                 key={idx}
                                 className="bg-[#252532]/60 rounded-lg p-3 border border-[#2d2d3d] hover:border-[#3d3d4d] transition-all duration-200 animate-fade-in"
                              >
                                 <div className="flex flex-wrap justify-between items-start gap-2 mb-3">
                                    <div className="flex items-center gap-2">
                                       {prompt.isBlocked ||
                                       (prompt.scriptOutput || "").startsWith(
                                          "Error:"
                                       ) ? (
                                          <div className="bg-[#ef4444]/10 p-1 rounded border border-[#ef4444]/20">
                                             <XCircle
                                                className="text-[#ef4444]"
                                                size={14}
                                             />
                                          </div>
                                       ) : prompt.progress === 100 ? (
                                          <div className="bg-[#10b981]/10 p-1 rounded border border-[#10b981]/20">
                                             <CheckCircle
                                                className="text-[#10b981]"
                                                size={14}
                                             />
                                          </div>
                                       ) : (
                                          <div className="w-5 h-5 rounded border-2 border-[#6366f1] border-t-transparent animate-spin" />
                                       )}

                                       <span className="text-xs text-[#94a3b8] font-mono">
                                          {prompt.timestamp}
                                       </span>
                                    </div>

                                    <div className="flex flex-wrap gap-1.5 text-xs">
                                       {prompt.gpuInfo && (
                                          <span className="px-2 py-0.5 bg-[#f59e0b]/10 text-[#f59e0b] rounded border border-[#f59e0b]/20 font-medium">
                                             {prompt.gpuInfo}
                                          </span>
                                       )}
                                       <span className="px-2 py-0.5 bg-[#ef4444]/10 text-[#ef4444] rounded border border-[#ef4444]/20 font-medium">
                                          {prompt.attack.name}
                                       </span>
                                       <span className="px-2 py-0.5 bg-[#10b981]/10 text-[#10b981] rounded border border-[#10b981]/20 font-medium">
                                          {prompt.defense.name}
                                       </span>
                                       <span className="px-2 py-0.5 bg-[#3b82f6]/10 text-[#3b82f6] rounded border border-[#3b82f6]/20 font-medium">
                                          {prompt.model.name}
                                       </span>
                                    </div>
                                 </div>

                                 <p className="text-[#f8fafc] text-base leading-relaxed mb-2 break-words">
                                    {prompt.text}
                                 </p>

                                 {prompt.progress !== undefined && (
                                    <div className="w-full bg-[#2d2d3d] rounded-full h-1.5 mb-2 overflow-hidden">
                                       <div
                                          className={`h-full rounded-full transition-all duration-300 ${
                                             prompt.isBlocked
                                                ? "bg-gradient-to-r from-[#ef4444] to-[#dc2626]"
                                                : "bg-gradient-to-r from-[#10b981] to-[#059669]"
                                          }`}
                                          style={{
                                             width: `${prompt.progress}%`,
                                          }}
                                       />
                                    </div>
                                 )}

                                 {prompt.scriptOutput && (
                                    <div
                                       className={`rounded-lg p-2 border ${
                                          prompt.isBlocked ||
                                          (
                                             prompt.scriptOutput || ""
                                          ).startsWith("Error:")
                                             ? "bg-[#ef4444]/5 border-[#ef4444]/20"
                                             : "bg-[#10b981]/5 border-[#10b981]/20"
                                       }`}
                                    >
                                       <pre
                                          className={`text-sm font-mono whitespace-pre-wrap break-words ${
                                             prompt.isBlocked ||
                                             (
                                                prompt.scriptOutput || ""
                                             ).startsWith("Error:")
                                                ? "text-[#fca5a5]"
                                                : "text-[#6ee7b7]"
                                          }`}
                                       >
                                          {prompt.scriptOutput}
                                       </pre>
                                    </div>
                                 )}
                              </div>
                           ))
                        )}
                     </div>
                  </div>

                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
                     <h2 className="text-xl font-bold text-[#f8fafc] mb-3">
                        Test Prompt
                     </h2>
                     <div className="flex gap-2">
                        <textarea
                           value={message}
                           onChange={(e) => setMessage(e.target.value)}
                           onKeyPress={handleKeyPress}
                           placeholder="Enter your test prompt here... (Press Enter to send, Shift+Enter for new line)"
                           className="flex-1 bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-3 py-2 text-[#f8fafc] placeholder-[#64748b] hover:border-[#3d3d4d] focus:border-[#6366f1] resize-none h-20 text-base font-medium leading-relaxed"
                           rows={3}
                        />
                        <button
                           onClick={handleSend}
                           disabled={!message.trim()}
                           className="bg-gradient-to-r from-[#6366f1] to-[#4f46e5] hover:from-[#4f46e5] hover:to-[#4338ca] disabled:from-[#2d2d3d] disabled:to-[#2d2d3d] text-white px-6 rounded-lg font-bold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-[#6366f1]/20 hover:shadow-2xl active:scale-95 text-sm"
                        >
                           <Send size={16} />
                           <span className="hidden sm:inline">Send</span>
                        </button>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </div>
   );
}

export default App;
