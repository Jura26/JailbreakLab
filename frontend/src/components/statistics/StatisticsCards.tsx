import {
   BarChart3,
   TrendingUp,
   Target,
   Shield,
   Clock,
   CheckCircle,
   AlertTriangle,
} from "lucide-react";

interface StatisticsCardsProps {
   totalTests: number;
   successRate: string;
   bestAttack: { name: string } | null;
   bestDefense: { name: string } | null;
   asrData: any;
   defenseBypassData: any;
   queryBudgetData: any;
   refusalData: any;
   additionalData: any;
   toolLeakageData: any;
   toolMisuseCount: number;
}

export default function StatisticsCards({
   totalTests,
   successRate,
   bestAttack,
   bestDefense,
   asrData,
   defenseBypassData,
   queryBudgetData,
   refusalData,
   additionalData,
   toolLeakageData,
   toolMisuseCount,
}: StatisticsCardsProps) {
   return (
      <>
         {/* Attack Metrics Cards */}
         <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#6366f1]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#6366f1]/10 p-1.5 rounded-lg border border-[#6366f1]/20">
                     <BarChart3 className="text-[#6366f1] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Total Tests
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#f8fafc]">
                  {totalTests.toLocaleString()}
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#ef4444]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#ef4444]/10 p-1.5 rounded-lg border border-[#ef4444]/20">
                     <TrendingUp className="text-[#ef4444] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Success Rate
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#ef4444]">
                  {successRate}%
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#f59e0b]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#f59e0b]/10 p-1.5 rounded-lg border border-[#f59e0b]/20">
                     <Target className="text-[#f59e0b] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Overall ASR
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#f59e0b]">
                  {asrData.overall_asr?.toFixed(1) || 0}%
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#a855f7]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#a855f7]/10 p-1.5 rounded-lg border border-[#a855f7]/20">
                     <Target className="text-[#a855f7] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Best Attack
                  </span>
               </div>
               <div className="text-sm font-bold text-[#f8fafc] truncate">
                  {bestAttack ? bestAttack.name : "N/A"}
               </div>
            </div>
         </div>

         {/* Defense Metrics Cards */}
         <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#10b981]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#10b981]/10 p-1.5 rounded-lg border border-[#10b981]/20">
                     <Shield className="text-[#10b981] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Best Defense
                  </span>
               </div>
               <div className="text-sm font-bold text-[#f8fafc] truncate">
                  {bestDefense ? bestDefense.name : "N/A"}
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#06b6d4]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#06b6d4]/10 p-1.5 rounded-lg border border-[#06b6d4]/20">
                     <Shield className="text-[#06b6d4] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Defense Bypass
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#06b6d4]">
                  {defenseBypassData.bypass_rate?.toFixed(1) || 0}%
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#10b981]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#10b981]/10 p-1.5 rounded-lg border border-[#10b981]/20">
                     <CheckCircle className="text-[#10b981] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Refusal Rate
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#10b981]">
                  {refusalData.refusal_rate?.toFixed(1) || 0}%
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#f59e0b]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#f59e0b]/10 p-1.5 rounded-lg border border-[#f59e0b]/20">
                     <Shield className="text-[#f59e0b] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Block Rate
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#f59e0b]">
                  {additionalData.block_rate?.toFixed(1) || 0}%
               </div>
            </div>
         </div>

         {/* Other Metrics Cards */}
         <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#8b5cf6]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#8b5cf6]/10 p-1.5 rounded-lg border border-[#8b5cf6]/20">
                     <Clock className="text-[#8b5cf6] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Median Time
                  </span>
               </div>
               <div className="text-lg font-bold text-[#8b5cf6]">
                  {queryBudgetData.median_time?.toFixed(1) || 0}s
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#8b5cf6]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#8b5cf6]/10 p-1.5 rounded-lg border border-[#8b5cf6]/20">
                     <Target className="text-[#8b5cf6] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Tool Misuse
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#8b5cf6]">
                  {toolLeakageData.tool_misuse_rate?.toFixed(1) || 0.0}%
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#06b6d4]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#06b6d4]/10 p-1.5 rounded-lg border border-[#06b6d4]/20">
                     <TrendingUp className="text-[#06b6d4] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Data Leakage
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#06b6d4]">
                  {toolLeakageData.data_leakage_rate?.toFixed(1) || 0.0}%
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl hover:border-[#ef4444]/30 transition-all duration-200">
               <div className="flex items-center gap-2 mb-2">
                  <div className="bg-[#ef4444]/10 p-1.5 rounded-lg border border-[#ef4444]/20">
                     <AlertTriangle className="text-[#ef4444] w-4 h-4" />
                  </div>
                  <span className="text-xs font-medium text-[#94a3b8] uppercase tracking-wider">
                     Tool Misuse Count
                  </span>
               </div>
               <div className="text-2xl font-bold text-[#ef4444]">
                  {toolMisuseCount.toLocaleString()}
               </div>
            </div>
         </div>
      </>
   );
}
