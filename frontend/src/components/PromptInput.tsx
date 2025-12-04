import type React from "react";
import { Send, X } from "lucide-react";

interface PromptInputProps {
   message: string;
   setMessage: (message: string) => void;
   isExecuting: boolean;
   onSend: () => void;
   onCancel: () => void;
}

export default function PromptInput({
   message,
   setMessage,
   isExecuting,
   onSend,
   onCancel,
}: PromptInputProps) {
   const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
         e.preventDefault();
         onSend();
      }
   };

   return (
      <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
         <h2 className="text-xl font-bold text-[#f8fafc] mb-3">Test Prompt</h2>
         <div className="flex gap-2">
            <textarea
               value={message}
               onChange={(e) => setMessage(e.target.value)}
               onKeyPress={handleKeyPress}
               placeholder="Enter your test prompt here... (Press Enter to send, Shift+Enter for new line)"
               className="flex-1 bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-3 py-2 text-[#f8fafc] placeholder-[#64748b] hover:border-[#3d3d4d] focus:border-[#6366f1] resize-none h-20 text-base font-medium leading-relaxed"
               rows={3}
               disabled={isExecuting}
            />
            <div className="flex flex-col gap-2">
               <button
                  onClick={onSend}
                  disabled={!message.trim() || isExecuting}
                  className="bg-gradient-to-r from-[#6366f1] to-[#4f46e5] hover:from-[#4f46e5] hover:to-[#4338ca] disabled:from-[#2d2d3d] disabled:to-[#2d2d3d] text-white px-6 rounded-lg font-bold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-[#6366f1]/20 hover:shadow-2xl active:scale-95 text-sm flex-1"
               >
                  <Send size={16} />
                  <span className="hidden sm:inline">Send</span>
               </button>
               {isExecuting && (
                  <button
                     onClick={onCancel}
                     className="bg-gradient-to-r from-[#ef4444] to-[#dc2626] hover:from-[#dc2626] hover:to-[#b91c1c] text-white px-6 rounded-lg font-bold transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-[#ef4444]/20 hover:shadow-2xl active:scale-95 text-sm flex-1"
                  >
                     <X size={16} />
                     <span className="hidden sm:inline">Cancel</span>
                  </button>
               )}
            </div>
         </div>
      </div>
   );
}
