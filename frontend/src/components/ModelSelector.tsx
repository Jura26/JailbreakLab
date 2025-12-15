import { Brain, Info } from "lucide-react";
import type { Model } from "../types";
import models from "./models";

interface ModelSelectorProps {
   selectedModel: Model;
   setSelectedModel: (model: Model) => void;
}

export default function ModelSelector({
   selectedModel,
   setSelectedModel,
}: ModelSelectorProps) {
   return (
      <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-6 border border-[#2d2d3d] shadow-2xl hover:border-[#3b82f6]/30 transition-all duration-300 flex-1 flex flex-col justify-center">
         <div className="flex items-center gap-2 mb-4">
            <div className="bg-[#3b82f6]/10 p-2 rounded-lg border border-[#3b82f6]/20">
               <Brain className="text-[#3b82f6] w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-[#f8fafc]">Target Model</h2>
         </div>

         <div className="relative mb-4">
            <select
               value={selectedModel.id}
               onChange={(e) =>
                  setSelectedModel(
                     models.find((m) => m.id === e.target.value) || models[0]
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
   );
}
