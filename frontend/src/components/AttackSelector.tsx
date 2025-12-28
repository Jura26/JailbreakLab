import { Sword, Info } from "lucide-react";
import type { Attack } from "../types";
import attacks from "./attacks";

interface AttackSelectorProps {
   selectedAttack: Attack;
   setSelectedAttack: (attack: Attack) => void;
   onInfoClick: (title: string, body: string, refs: string[]) => void;
}

export default function AttackSelector({
   selectedAttack,
   setSelectedAttack,
   onInfoClick,
}: AttackSelectorProps) {
   return (
      <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-6 border border-[#2d2d3d] shadow-2xl hover:border-[#ef4444]/30 transition-all duration-300 flex-1 flex flex-col justify-center">
         <div className="flex items-center gap-2 mb-4">
            <div className="bg-[#ef4444]/10 p-2 rounded-lg border border-[#ef4444]/20">
               <Sword className="text-[#ef4444] w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-[#f8fafc]">Attack Vector</h2>
         </div>

         <div className="relative mb-4">
            <div className="flex items-center gap-2">
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
               <button
                  onClick={() => {
                     onInfoClick(
                        selectedAttack.name,
                        selectedAttack.longDescription ||
                           selectedAttack.description ||
                           "",
                        selectedAttack.references || []
                     );
                  }}
                  title={selectedAttack.description}
                  className="group info-button relative p-2.5 rounded-xl bg-gradient-to-br from-[#ef4444]/10 to-[#dc2626]/5 border border-[#ef4444]/30 text-[#ef4444] hover:border-[#ef4444] hover:shadow-lg hover:shadow-[#ef4444]/20 hover:scale-105 transition-all duration-300 flex-shrink-0"
               >
                  <Info size={18} className="relative z-10" />
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#ef4444]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
               </button>
            </div>
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
   );
}
