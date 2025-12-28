import { Shield, Info } from "lucide-react";
import type { Defense } from "../types";
import defenses from "./defenses";

interface DefenseSelectorProps {
   selectedDefense: Defense;
   setSelectedDefense: (defense: Defense) => void;
   onInfoClick: (title: string, body: string, refs: string[]) => void;
}

export default function DefenseSelector({
   selectedDefense,
   setSelectedDefense,
   onInfoClick,
}: DefenseSelectorProps) {
   return (
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
            <div className="flex items-center gap-2">
               <select
                  value={selectedDefense.id}
                  onChange={(e) =>
                     setSelectedDefense(
                        defenses.find((d) => d.id === e.target.value) ||
                           defenses[0]
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
               <button
                  onClick={() => {
                     onInfoClick(
                        selectedDefense.name,
                        selectedDefense.longDescription ||
                           selectedDefense.description ||
                           "",
                        selectedDefense.references || []
                     );
                  }}
                  title={selectedDefense.description}
                  className="group info-button relative p-2.5 rounded-xl bg-gradient-to-br from-[#10b981]/10 to-[#059669]/5 border border-[#10b981]/30 text-[#10b981] hover:border-[#10b981] hover:shadow-lg hover:shadow-[#10b981]/20 hover:scale-105 transition-all duration-300 flex-shrink-0"
               >
                  <Info size={18} className="relative z-10" />
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#10b981]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
               </button>
            </div>
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
   );
}
