import { Send, CheckCircle, XCircle, X } from "lucide-react";
import type { Prompt } from "../types";

interface ExecutionHistoryProps {
   prompts: Prompt[];
   isExecuting: boolean;
   onCancel: () => void;
}

export default function ExecutionHistory({
   prompts,
   isExecuting,
   onCancel,
}: ExecutionHistoryProps) {
   return (
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
                        Configure your attack, defense, and model, then send a
                        prompt
                     </p>
                  </div>
               </div>
            ) : (
               prompts.map((prompt, idx) => {
                  const scriptOutput = prompt.scriptOutput || "";
                  const wasCanceled =
                     scriptOutput.includes("Manually canceled");
                  const hadError = scriptOutput.startsWith("Error:");
                  const isFinal =
                     (typeof prompt.progress === "number" &&
                        prompt.progress >= 100) ||
                     wasCanceled ||
                     hadError;
                  // Consider failed only when blocked OR when processing finished and attackSuccess is false
                  const isFailed =
                     prompt.isBlocked ||
                     (isFinal && !prompt.attackSuccess) ||
                     wasCanceled ||
                     hadError;

                  return (
                     <div
                        key={idx}
                        className="bg-[#252532]/60 rounded-lg p-3 border border-[#2d2d3d] hover:border-[#3d3d4d] transition-all duration-200 animate-fade-in"
                     >
                        <div className="flex flex-wrap justify-between items-start gap-2 mb-3">
                           <div className="flex items-center gap-2">
                              {prompt.progress < 100 && !wasCanceled ? (
                                 <div className="w-5 h-5 rounded border-2 border-[#6366f1] border-t-transparent animate-spin" />
                              ) : isFailed ? (
                                 <div className="bg-[#ef4444]/10 p-1 rounded border border-[#ef4444]/20">
                                    <XCircle
                                       className="text-[#ef4444]"
                                       size={14}
                                    />
                                 </div>
                              ) : (
                                 <div className="bg-[#10b981]/10 p-1 rounded border border-[#10b981]/20">
                                    <CheckCircle
                                       className="text-[#10b981]"
                                       size={14}
                                    />
                                 </div>
                              )}

                              <span className="text-xs text-[#94a3b8] font-mono">
                                 {prompt.timestamp}
                              </span>
                           </div>

                           <div className="flex items-center flex-wrap gap-1.5 text-xs">
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
                              {/* Cancel button for running attack - show immediately */}
                              {isExecuting && idx === prompts.length - 1 && (
                                 <button
                                    onClick={onCancel}
                                    className="ml-1 bg-gradient-to-r from-[#ef4444] to-[#dc2626] hover:from-[#dc2626] hover:to-[#b91c1c] text-white px-3 py-0.5 rounded border border-[#ef4444]/20 font-bold transition-all duration-200 flex items-center gap-1.5 shadow-lg hover:shadow-[#ef4444]/20 hover:shadow-xl active:scale-95"
                                 >
                                    <X size={14} />
                                    <span>Cancel</span>
                                 </button>
                              )}
                           </div>
                        </div>

                        <p className="text-[#f8fafc] text-base leading-relaxed mb-2 break-words">
                           {prompt.text}
                        </p>

                        {prompt.progress !== undefined && (
                           <div className="w-full bg-[#2d2d3d] rounded-full h-1.5 mb-2 overflow-hidden">
                              <div
                                 className={`h-full rounded-full transition-all duration-300 ${
                                    isFailed
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
                                 isFailed
                                    ? "bg-[#ef4444]/5 border-[#ef4444]/20"
                                    : "bg-[#10b981]/5 border-[#10b981]/20"
                              }`}
                           >
                              <pre
                                 className={`text-sm font-mono whitespace-pre-wrap break-words ${
                                    isFailed
                                       ? "text-[#fca5a5]"
                                       : "text-[#6ee7b7]"
                                 }`}
                              >
                                 {prompt.scriptOutput}
                              </pre>
                           </div>
                        )}
                     </div>
                  );
               })
            )}
         </div>
      </div>
   );
}
