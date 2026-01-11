import { Filter } from "lucide-react";

interface FilterOptions {
   attack_types: string[];
   defense_types: string[];
   model_types: string[];
}

interface StatisticsFiltersProps {
   filters: FilterOptions;
   selectedAttack: string;
   selectedDefense: string;
   onAttackChange: (value: string) => void;
   onDefenseChange: (value: string) => void;
}

export default function StatisticsFilters({
   filters,
   selectedAttack,
   selectedDefense,
   onAttackChange,
   onDefenseChange,
}: StatisticsFiltersProps) {
   return (
      <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
         <div className="flex items-center gap-2 mb-4">
            <div className="bg-[#6366f1]/10 p-2 rounded-lg border border-[#6366f1]/20">
               <Filter className="text-[#6366f1] w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-[#f8fafc]">Filters</h2>
         </div>
         <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
               <label className="text-sm font-medium text-[#94a3b8] mb-2 block">
                  Attack Type
               </label>
               <select
                  value={selectedAttack}
                  onChange={(e) => onAttackChange(e.target.value)}
                  className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-2.5 text-[#f8fafc] cursor-pointer hover:border-[#ef4444]/50 focus:border-[#ef4444] focus:outline-none font-medium text-sm appearance-none transition-all duration-200"
                  style={{
                     backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23ef4444'%3E%3Cpath strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                     backgroundRepeat: "no-repeat",
                     backgroundPosition: "right 0.5rem center",
                     backgroundSize: "1.5rem 1.5rem",
                  }}
               >
                  <option value="all">All Attacks</option>
                  {filters?.attack_types?.map((type) => (
                     <option key={type} value={type}>
                        {type}
                     </option>
                  ))}
               </select>
            </div>
            <div>
               <label className="text-sm font-medium text-[#94a3b8] mb-2 block">
                  Defense Type
               </label>
               <select
                  value={selectedDefense}
                  onChange={(e) => onDefenseChange(e.target.value)}
                  className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-2.5 text-[#f8fafc] cursor-pointer hover:border-[#10b981]/50 focus:border-[#10b981] focus:outline-none font-medium text-sm appearance-none transition-all duration-200"
                  style={{
                     backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2310b981'%3E%3Cpath strokeLinecap='round' strokeLinejoin='round' strokeWidth='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                     backgroundRepeat: "no-repeat",
                     backgroundPosition: "right 0.5rem center",
                     backgroundSize: "1.5rem 1.5rem",
                  }}
               >
                  <option value="all">All Defenses</option>
                  {filters?.defense_types?.map((type) => (
                     <option key={type} value={type}>
                        {type}
                     </option>
                  ))}
               </select>
            </div>
         </div>
      </div>
   );
}
