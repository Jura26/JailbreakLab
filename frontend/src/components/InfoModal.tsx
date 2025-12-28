import { X, ExternalLink, BookOpen } from "lucide-react";

interface InfoModalProps {
   isOpen: boolean;
   onClose: () => void;
   title: string;
   body: string;
   references: string[];
}

export default function InfoModal({
   isOpen,
   onClose,
   title,
   body,
   references,
}: InfoModalProps) {
   if (!isOpen) return null;

   return (
      <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 animate-fade-in">
         {/* Backdrop with blur effect */}
         <div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
            style={{
               animation: "fadeIn 0.2s ease-out",
            }}
         />

         {/* Modal container with slide-up animation */}
         <div
            className="relative max-w-3xl w-full"
            style={{
               animation: "slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
            }}
         >
            <div className="bg-gradient-to-br from-[#1a1a24] to-[#141420] backdrop-blur-2xl rounded-2xl border border-[#2d2d3d] shadow-2xl overflow-hidden">
               {/* Header with gradient background */}
               <div className="relative bg-gradient-to-r from-[#6366f1]/10 via-[#a855f7]/10 to-[#6366f1]/10 border-b border-[#2d2d3d] px-8 py-6">
                  <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjAzKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-50" />
                  <div className="relative flex items-start justify-between gap-4">
                     <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-gradient-to-br from-[#6366f1] to-[#a855f7] shadow-lg shadow-[#6366f1]/30">
                           <BookOpen className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="text-2xl font-bold bg-gradient-to-r from-[#f8fafc] to-[#cbd5e1] bg-clip-text text-transparent">
                           {title}
                        </h3>
                     </div>
                     <button
                        onClick={onClose}
                        className="group close-button p-2 rounded-xl bg-[#252532]/50 border border-[#2d2d3d] text-[#cbd5e1] hover:bg-[#ef4444]/10 hover:border-[#ef4444]/50 hover:text-[#ef4444] transition-all duration-200"
                     >
                        <X size={20} />
                     </button>
                  </div>
               </div>

               {/* Content area with better spacing and typography */}
               <div className="px-8 py-6 max-h-[60vh] overflow-y-auto custom-scrollbar">
                  <div className="space-y-6">
                     {/* Description section */}
                     <div>
                        <p className="text-base leading-relaxed text-[#e2e8f0] text-pretty">
                           {body}
                        </p>
                     </div>

                     {/* References section with enhanced styling */}
                     {references.length > 0 && (
                        <div className="pt-4 border-t border-[#2d2d3d]">
                           <div className="flex items-center gap-2 mb-4">
                              <div className="p-1.5 rounded-lg bg-[#3b82f6]/10 border border-[#3b82f6]/20">
                                 <ExternalLink className="w-4 h-4 text-[#3b82f6]" />
                              </div>
                              <h4 className="text-sm font-semibold text-[#f8fafc] uppercase tracking-wide">
                                 References & Resources
                              </h4>
                           </div>
                           <div className="space-y-2">
                              {references.map((r, i) => (
                                 <a
                                    key={i}
                                    href={r}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="group flex items-start gap-3 p-3 rounded-lg bg-[#252532]/50 border border-[#2d2d3d] hover:border-[#3b82f6]/50 hover:bg-[#3b82f6]/5 transition-all duration-200"
                                 >
                                    <ExternalLink className="w-4 h-4 text-[#3b82f6] flex-shrink-0 mt-0.5 group-hover:scale-110 transition-transform duration-200" />
                                    <span className="text-sm text-[#cbd5e1] group-hover:text-[#3b82f6] break-all leading-relaxed transition-colors duration-200">
                                       {r}
                                    </span>
                                 </a>
                              ))}
                           </div>
                        </div>
                     )}
                  </div>
               </div>

               {/* Footer with action button */}
               <div className="px-8 py-4 bg-[#0f0f1a]/50 border-t border-[#2d2d3d] flex justify-end">
                  <button
                     onClick={onClose}
                     className="got-it-button px-6 py-2.5 bg-gradient-to-r from-[#6366f1] to-[#a855f7] hover:from-[#4f46e5] hover:to-[#9333ea] rounded-xl text-white font-medium shadow-lg shadow-[#6366f1]/30 hover:shadow-[#6366f1]/50 hover:scale-105 transition-all duration-200"
                  >
                     Got it!
                  </button>
               </div>
            </div>
         </div>
      </div>
   );
}
