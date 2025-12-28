import {
   PieChart,
   Pie,
   Cell,
   BarChart,
   Bar,
   XAxis,
   YAxis,
   CartesianGrid,
   Tooltip,
   ResponsiveContainer,
   Legend,
} from "recharts";

const COLORS = {
   success: "#10b981",
   failure: "#ef4444",
};

interface StatisticsChartsProps {
   pieData: { name: string; value: number }[];
   attackStats: { name: string; successRate: number; total: number }[];
   defenseStats: { name: string; successRate: number; total: number }[];
   modelStats: { name: string; successRate: number; total: number }[];
   asrData: any;
   defenseBypassData: any;
   queryBudgetData: any;
   refusalData: any;
}

export default function StatisticsCharts({
   pieData,
   attackStats,
   defenseStats,
   modelStats,
   asrData,
   defenseBypassData,
   queryBudgetData,
   refusalData,
}: StatisticsChartsProps) {
   return (
      <>
         {/* Charts Section */}
         <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
                  Attack Success Distribution
               </h3>
               <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                     <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={70}
                        outerRadius={110}
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) =>
                           `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`
                        }
                        labelLine={false}
                     >
                        <Cell fill={COLORS.success} />
                        <Cell fill={COLORS.failure} />
                     </Pie>
                     <Tooltip
                        contentStyle={{
                           backgroundColor: "#1a1a24",
                           border: "1px solid #2d2d3d",
                           borderRadius: "8px",
                           padding: "8px",
                        }}
                        itemStyle={{ color: "#f8fafc", fontWeight: 500 }}
                        labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                     />
                     <Legend
                        wrapperStyle={{ paddingTop: "20px" }}
                        iconType="circle"
                     />
                  </PieChart>
               </ResponsiveContainer>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#ef4444] animate-pulse" />
                  Success Rate by Attack Type
               </h3>
               <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={attackStats} layout="vertical">
                     <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#2d2d3d"
                        opacity={0.5}
                     />
                     <XAxis
                        type="number"
                        domain={[0, 100]}
                        stroke="#94a3b8"
                        tick={{ fontSize: 12, fill: "#94a3b8" }}
                     />
                     <YAxis
                        type="category"
                        dataKey="name"
                        stroke="#94a3b8"
                        tick={{ fontSize: 11, fill: "#94a3b8" }}
                        width={110}
                     />
                     <Tooltip
                        contentStyle={{
                           backgroundColor: "#1a1a24",
                           border: "1px solid #2d2d3d",
                           borderRadius: "8px",
                           padding: "8px",
                        }}
                        labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                        formatter={(value: number | undefined) => [
                           `${(value ?? 0).toFixed(1)}%`,
                           "Success Rate",
                        ]}
                     />
                     <Bar
                        dataKey="successRate"
                        fill="#ef4444"
                        radius={[0, 8, 8, 0]}
                     />
                  </BarChart>
               </ResponsiveContainer>
            </div>
         </div>

         <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
                  Success Rate by Defense Type
               </h3>
               <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={defenseStats} layout="vertical">
                     <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#2d2d3d"
                        opacity={0.5}
                     />
                     <XAxis
                        type="number"
                        domain={[0, 100]}
                        stroke="#94a3b8"
                        tick={{ fontSize: 12, fill: "#94a3b8" }}
                     />
                     <YAxis
                        type="category"
                        dataKey="name"
                        stroke="#94a3b8"
                        tick={{ fontSize: 11, fill: "#94a3b8" }}
                        width={130}
                     />
                     <Tooltip
                        contentStyle={{
                           backgroundColor: "#1a1a24",
                           border: "1px solid #2d2d3d",
                           borderRadius: "8px",
                           padding: "8px",
                        }}
                        labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                        formatter={(value: number | undefined) => [
                           `${(value ?? 0).toFixed(1)}%`,
                           "Success Rate",
                        ]}
                     />
                     <Bar
                        dataKey="successRate"
                        fill="#10b981"
                        radius={[0, 8, 8, 0]}
                     />
                  </BarChart>
               </ResponsiveContainer>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#3b82f6] animate-pulse" />
                  Success Rate by Model Type
               </h3>
               <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={modelStats} layout="vertical">
                     <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#2d2d3d"
                        opacity={0.5}
                     />
                     <XAxis
                        type="number"
                        domain={[0, 100]}
                        stroke="#94a3b8"
                        tick={{ fontSize: 12, fill: "#94a3b8" }}
                     />
                     <YAxis
                        type="category"
                        dataKey="name"
                        stroke="#94a3b8"
                        tick={{ fontSize: 11, fill: "#94a3b8" }}
                        width={100}
                     />
                     <Tooltip
                        contentStyle={{
                           backgroundColor: "#1a1a24",
                           border: "1px solid #2d2d3d",
                           borderRadius: "8px",
                           padding: "8px",
                        }}
                        labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                        formatter={(value: number | undefined) => [
                           `${(value ?? 0).toFixed(1)}%`,
                           "Success Rate",
                        ]}
                     />
                     <Bar
                        dataKey="successRate"
                        fill="#3b82f6"
                        radius={[0, 8, 8, 0]}
                     />
                  </BarChart>
               </ResponsiveContainer>
            </div>
         </div>

         {/* Advanced Metrics Charts */}
         <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] animate-pulse" />
                  Attack Success Rate by Attack Type
               </h3>
               <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                     data={Object.entries(asrData.by_attack || {}).map(
                        ([name, rate]) => ({ name, successRate: rate })
                     )}
                     layout="vertical"
                  >
                     <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#2d2d3d"
                        opacity={0.5}
                     />
                     <XAxis
                        type="number"
                        domain={[0, 100]}
                        stroke="#94a3b8"
                        tick={{ fontSize: 12, fill: "#94a3b8" }}
                     />
                     <YAxis
                        type="category"
                        dataKey="name"
                        stroke="#94a3b8"
                        tick={{ fontSize: 11, fill: "#94a3b8" }}
                        width={130}
                     />
                     <Tooltip
                        contentStyle={{
                           backgroundColor: "#1a1a24",
                           border: "1px solid #2d2d3d",
                           borderRadius: "8px",
                           padding: "8px",
                        }}
                        labelStyle={{ color: "#f8fafc", fontWeight: 600 }}
                        formatter={(value: number | undefined) => [
                           `${(value ?? 0).toFixed(1)}%`,
                           "ASR",
                        ]}
                     />
                     <Bar
                        dataKey="successRate"
                        fill="#f59e0b"
                        radius={[0, 8, 8, 0]}
                     />
                  </BarChart>
               </ResponsiveContainer>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#06b6d4] animate-pulse" />
                  Defense Bypass Analysis
               </h3>
               <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Bypass Rate</span>
                     <span className="text-[#06b6d4] font-bold">
                        {defenseBypassData.bypass_rate?.toFixed(1) || 0}%
                     </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Baseline ASR</span>
                     <span className="text-[#f8fafc] font-bold">
                        {defenseBypassData.baseline_asr?.toFixed(1) || 0}%
                     </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Delta</span>
                     <span
                        className={`font-bold ${
                           defenseBypassData.delta > 0
                              ? "text-[#ef4444]"
                              : "text-[#10b981]"
                        }`}
                     >
                        {defenseBypassData.delta?.toFixed(1) || 0}%
                     </span>
                  </div>
               </div>
            </div>
         </div>

         <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#8b5cf6] animate-pulse" />
                  Query Budget Metrics
               </h3>
               <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Median Queries</span>
                     <span className="text-[#8b5cf6] font-bold">
                        {queryBudgetData.median_queries?.toFixed(0) || 0}
                     </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Median Tokens</span>
                     <span className="text-[#f8fafc] font-bold">
                        {queryBudgetData.median_tokens?.toFixed(0) || 0}
                     </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Median Time</span>
                     <span className="text-[#8b5cf6] font-bold">
                        {queryBudgetData.median_time?.toFixed(1) || 0}s
                     </span>
                  </div>
               </div>
            </div>

            <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d] shadow-2xl">
               <h3 className="text-base font-bold text-[#f8fafc] mb-4 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
                  Refusal & Safety Metrics
               </h3>
               <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Refusal Rate</span>
                     <span className="text-[#10b981] font-bold">
                        {refusalData.refusal_rate?.toFixed(1) || 0}%
                     </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">
                        Safe Completion Rate
                     </span>
                     <span className="text-[#f8fafc] font-bold">
                        {refusalData.safe_completion_rate?.toFixed(1) || 0}%
                     </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-[#252532] rounded-lg">
                     <span className="text-[#94a3b8]">Over-refusal Rate</span>
                     <span className="text-[#ef4444] font-bold">
                        {refusalData.over_refusal_rate?.toFixed(1) || 0}%
                     </span>
                  </div>
               </div>
            </div>
         </div>
      </>
   );
}
