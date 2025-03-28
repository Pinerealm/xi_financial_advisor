// import { StateGraph } from "@langchain/langgraph";
// // import { Client } from "@langchain/core/runnables";
// import { generateReport, fetchFinancialData } from "./apiUtils";

// interface LangGraphResult {
//   financialData: any;
//   predictionResult: any;
//   report: any;
//   visualizationData: { labels: string[]; values: number[] };
// }

// // Mock AutoARIMA function (for demonstration)
// const AutoARIMA = async (data: number[]): Promise<any> => {
//   // Simulate an ARIMA prediction
//   await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate delay
//   const forecast = data.slice(-5).map((val) => val + Math.random() * 10 - 5); // Example forecast
//   return {
//     forecast: forecast,
//     modelParameters: { p: 1, d: 1, q: 1 }, // Example parameters
//     accuracy: 0.85, // Example accuracy
//   };
// };

// export async function runLangGraph(symbol: string): Promise<LangGraphResult> {
//   // Define the state type for the graph
//   type GraphState = {
//     financialData?: any;
//     predictionResult?: any;
//     report?: any;
//     visualizationData?: { labels: string[]; values: number[] };
//   };

//   // Create a new state graph
//   const graph = new StateGraph<GraphState>({
//     channels: {
//       financialData: null,
//       predictionResult: null,
//       report: null,
//       visualizationData: null,
//     },
//   })
//     .addNode("ingest", async (state: GraphState) => {
//       const data = await fetchFinancialData(symbol);
//       return { financialData: data };
//     })
//     .addNode("analyze", async (state: GraphState) => {
//       if (!state.financialData) throw new Error("No financial data");
//       const prediction = await AutoARIMA(state.financialData.close);
//       return { predictionResult: prediction };
//     })
//     .addNode("report", async (state: GraphState) => {
//       if (!state.predictionResult) throw new Error("No prediction result");
//       const reportData = await generateReport(state.predictionResult);
//       return { report: reportData };
//     })
//     .addNode("visualize", async (state: GraphState) => {
//       if (!state.predictionResult) throw new Error("No prediction result");
//       const labels = state.predictionResult.forecast.map(
//         (_: number, index: number) => `Day ${index + 1}`
//       );
//       const values = state.predictionResult.forecast;
//       return { visualizationData: { labels, values } };
//     });

//   // Define the workflow
//   graph
//     .addEdge("ingest", "analyze")
//     .addEdge("analyze", "report")
//     .addEdge("report", "visualize");

//   // Compile the graph
//   const workflow = graph.compile();

//   // Run the workflow
//   const result = await workflow.invoke({});

//   // Return the visualization data
//   return result.visualizationData;
// }
