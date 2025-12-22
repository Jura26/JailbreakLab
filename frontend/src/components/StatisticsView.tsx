import { useState, useEffect } from "react";
import { BarChart3, Filter, Target, Shield, TrendingUp } from "lucide-react";
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

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface StatRecord {
   id: string;
   created_at: string;
   session_id: string;
   model_type: string;
   attack_type: string;
   defense_type: string;
   attack_success: boolean;
   was_blocked: boolean;
}

interface FilterOptions {
   attack_types: string[];
   defense_types: string[];
   model_types: string[];
}

const COLORS = {
   success: "#22c55e",  // Green for successful attacks
   failure: "#ef4444",  // Red for failed attacks
};

export default function StatisticsView() {
   const [data, setData] = useState<StatRecord[]>([]);
   const [filters, setFilters] = useState<FilterOptions>({
      attack_types: [],
      defense_types: [],
      model_types: [],
   });
   const [selectedAttack, setSelectedAttack] = useState<string>("all");
   const [selectedDefense, setSelectedDefense] = useState<string>("all");
   const [loading, setLoading] = useState(true);

   // Fetch filter options on mount
   useEffect(() => {
      fetch(`${API_URL}/api/statistics/filters`)
         .then((res) => res.json())
         .then((data) => setFilters(data))
         .catch((err) => console.error("Error fetching filters:", err));
   }, []);

   // Fetch data when filters change
   useEffect(() => {
      setLoading(true);
      const params = new URLSearchParams();
      params.set("attack_type", selectedAttack);
      params.set("defense_type", selectedDefense);

      fetch(`${API_URL}/api/statistics?${params}`)
         .then((res) => res.json())
         .then((result) => {
            setData(result.data || []);
            setLoading(false);
         })
         .catch((err) => {
            console.error("Error fetching statistics:", err);
            setLoading(false);
         });
   }, [selectedAttack, selectedDefense]);

   // Calculate statistics
   const totalTests = data.length;
   const successfulAttacks = data.filter((d) => d.attack_success).length;
   const failedAttacks = totalTests - successfulAttacks;
   const successRate = totalTests > 0 ? ((successfulAttacks / totalTests) * 100).toFixed(1) : "0";

   // Pie chart data
   const pieData = [
      { name: "Attack Succeeded", value: successfulAttacks },
      { name: "Attack Failed", value: failedAttacks },
   ];

   // Success rate by attack type - derive from actual data
   const attackTypes = [...new Set(data.map((d) => d.attack_type))];
   const attackStats = attackTypes.map((attackType) => {
      const filtered = data.filter((d) => d.attack_type === attackType);
      const success = filtered.filter((d) => d.attack_success).length;
      const rate = filtered.length > 0 ? (success / filtered.length) * 100 : 0;
      return { name: attackType, successRate: rate, total: filtered.length };
   }).filter((d) => d.total > 0);

   // Success rate by defense type - derive from actual data
   const defenseTypes = [...new Set(data.map((d) => d.defense_type))];
   const defenseStats = defenseTypes.map((defenseType) => {
      const filtered = data.filter((d) => d.defense_type === defenseType);
      const success = filtered.filter((d) => d.attack_success).length;
      const rate = filtered.length > 0 ? (success / filtered.length) * 100 : 0;
      return { name: defenseType, successRate: rate, total: filtered.length };
   }).filter((d) => d.total > 0);

   // Success rate by model type - derive from actual data
   const modelTypes = [...new Set(data.map((d) => d.model_type))];
   const modelStats = modelTypes.map((modelType) => {
      const filtered = data.filter((d) => d.model_type === modelType);
      const success = filtered.filter((d) => d.attack_success).length;
      const rate = filtered.length > 0 ? (success / filtered.length) * 100 : 0;
      return { name: modelType, successRate: rate, total: filtered.length };
   }).filter((d) => d.total > 0);

   // Find best attack and defense
   const bestAttack = attackStats.length > 0
      ? attackStats.reduce((a, b) => (a.successRate > b.successRate ? a : b))
      : null;
   const bestDefense = defenseStats.length > 0
      ? defenseStats.reduce((a, b) => (a.successRate < b.successRate ? a : b))
      : null;

   return (
      <div className="flex flex-col gap-3 h-full overflow-hidden">
         {/* Filters */}
         <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-3 border border-[#2d2d3d]">
            <div className="flex items-center gap-2 mb-2">
               <div className="bg-[#6366f1]/10 p-1.5 rounded-lg border border-[#6366f1]/20">
                  <Filter className="text-[#6366f1] w-4 h-4" />
               </div>
               <h2 className="text-base font-bold text-[#f8fafc]">Filters</h2>
            </div>
            <div className="flex gap-4 flex-wrap">
               <div className="flex-1 min-w-[200px]">
                  <label className="text-sm text-[#94a3b8] mb-1 block">Attack Type</label>
                  <select
                     value={selectedAttack}
                     onChange={(e) => setSelectedAttack(e.target.value)}
                     className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-2 text-[#f8fafc] cursor-pointer hover:border-[#6366f1]/50 focus:border-[#6366f1] focus:outline-none text-sm"
                  >
                     <option value="all">All Attacks</option>
                     {filters.attack_types.map((type) => (
                        <option key={type} value={type}>
                           {type}
                        </option>
                     ))}
                  </select>
               </div>
               <div className="flex-1 min-w-[200px]">
                  <label className="text-sm text-[#94a3b8] mb-1 block">Defense Type</label>
                  <select
                     value={selectedDefense}
                     onChange={(e) => setSelectedDefense(e.target.value)}
                     className="w-full bg-[#252532] border-2 border-[#2d2d3d] rounded-lg px-4 py-2 text-[#f8fafc] cursor-pointer hover:border-[#6366f1]/50 focus:border-[#6366f1] focus:outline-none text-sm"
                  >
                     <option value="all">All Defenses</option>
                     {filters.defense_types.map((type) => (
                        <option key={type} value={type}>
                           {type}
                        </option>
                     ))}
                  </select>
               </div>
            </div>
         </div>

         {loading ? (
            <div className="flex items-center justify-center h-64">
               <div className="text-[#94a3b8]">Loading statistics...</div>
            </div>
         ) : totalTests === 0 ? (
            <div className="flex items-center justify-center h-64">
               <div className="text-[#94a3b8]">No data available. Run some tests first!</div>
            </div>
         ) : (
            <>
               {/* Summary Cards */}
               <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="text-[#6366f1] w-4 h-4" />
                        <span className="text-xs text-[#94a3b8]">Total Tests</span>
                     </div>
                     <div className="text-2xl font-bold text-[#f8fafc]">{totalTests}</div>
                  </div>
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="text-[#ef4444] w-4 h-4" />
                        <span className="text-xs text-[#94a3b8]">Success Rate</span>
                     </div>
                     <div className="text-2xl font-bold text-[#ef4444]">{successRate}%</div>
                  </div>
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <div className="flex items-center gap-2 mb-2">
                        <Target className="text-[#a855f7] w-4 h-4" />
                        <span className="text-xs text-[#94a3b8]">Best Attack</span>
                     </div>
                     <div className="text-sm font-bold text-[#f8fafc] truncate">
                        {bestAttack ? bestAttack.name : "N/A"}
                     </div>
                  </div>
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <div className="flex items-center gap-2 mb-2">
                        <Shield className="text-[#22c55e] w-4 h-4" />
                        <span className="text-xs text-[#94a3b8]">Best Defense</span>
                     </div>
                     <div className="text-sm font-bold text-[#f8fafc] truncate">
                        {bestDefense ? bestDefense.name : "N/A"}
                     </div>
                  </div>
               </div>

               {/* Charts Row 1 */}
               <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Pie Chart */}
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <h3 className="text-sm font-bold text-[#f8fafc] mb-4">Attack Success Distribution</h3>
                     <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                           <Pie
                              data={pieData}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={100}
                              paddingAngle={5}
                              dataKey="value"
                              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
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
                              }}
                              itemStyle={{ color: "#f8fafc" }}
                              labelStyle={{ color: "#f8fafc" }}
                           />
                           <Legend />
                        </PieChart>
                     </ResponsiveContainer>
                  </div>

                  {/* Attack Type Bar Chart */}
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <h3 className="text-sm font-bold text-[#f8fafc] mb-4">Success Rate by Attack Type</h3>
                     <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={attackStats} layout="vertical">
                           <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                           <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 12 }} />
                           <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={100} />
                           <Tooltip
                              contentStyle={{
                                 backgroundColor: "#1a1a24",
                                 border: "1px solid #2d2d3d",
                                 borderRadius: "8px",
                              }}
                              labelStyle={{ color: "#f8fafc" }}
                              formatter={(value: number | undefined) => [`${(value ?? 0).toFixed(1)}%`, "Success Rate"]}
                           />
                           <Bar dataKey="successRate" fill="#ef4444" radius={[0, 4, 4, 0]} />
                        </BarChart>
                     </ResponsiveContainer>
                  </div>
               </div>

               {/* Charts Row 2 */}
               <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Defense Type Bar Chart */}
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <h3 className="text-sm font-bold text-[#f8fafc] mb-4">Success Rate by Defense Type</h3>
                     <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={defenseStats} layout="vertical">
                           <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                           <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 12 }} />
                           <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                           <Tooltip
                              contentStyle={{
                                 backgroundColor: "#1a1a24",
                                 border: "1px solid #2d2d3d",
                                 borderRadius: "8px",
                              }}
                              labelStyle={{ color: "#f8fafc" }}
                              formatter={(value: number | undefined) => [`${(value ?? 0).toFixed(1)}%`, "Success Rate"]}
                           />
                           <Bar dataKey="successRate" fill="#22c55e" radius={[0, 4, 4, 0]} />
                        </BarChart>
                     </ResponsiveContainer>
                  </div>

                  {/* Model Type Bar Chart */}
                  <div className="bg-[#1a1a24]/80 backdrop-blur-xl rounded-xl p-4 border border-[#2d2d3d]">
                     <h3 className="text-sm font-bold text-[#f8fafc] mb-4">Success Rate by Model Type</h3>
                     <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={modelStats} layout="vertical">
                           <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                           <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" tick={{ fontSize: 12 }} />
                           <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={100} />
                           <Tooltip
                              contentStyle={{
                                 backgroundColor: "#1a1a24",
                                 border: "1px solid #2d2d3d",
                                 borderRadius: "8px",
                              }}
                              labelStyle={{ color: "#f8fafc" }}
                              formatter={(value: number | undefined) => [`${(value ?? 0).toFixed(1)}%`, "Success Rate"]}
                           />
                           <Bar dataKey="successRate" fill="#6366f1" radius={[0, 4, 4, 0]} />
                        </BarChart>
                     </ResponsiveContainer>
                  </div>
               </div>
            </>
         )}
      </div>
   );
}
