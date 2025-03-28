/* eslint-disable */
// Next.js 15+ with TypeScript & Tailwind CSS Project Structure:
// financial-analysis-app/
// ├── app/
// │   ├── components/
// │   │   ├── DataIngestion.tsx
// │   │   ├── MarketAnalysis.tsx
// │   │   ├── ReportGeneration.tsx
// │   │   ├── FeedbackForm.tsx
// │   │   ├── Visualization.tsx
// │   │   ├── VoiceInteraction.tsx
// │   │   └── ...
// │   ├── page.tsx
// │   └── layout.tsx
// ├── lib/
// │   ├── langGraphUtils.ts
// │   ├── apiUtils.ts
// │   ├── mlUtils.ts
// │   ├── voiceUtils.ts (Optional)
// │   └── ...
// ├── public/
// │   └── ...
// ├── package.json
// ├── tailwind.config.js
// ├── postcss.config.js
// ├── tsconfig.json

// app/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import DataIngestion from "./components/DataIngestion";
import MarketAnalysis from "./components/MarketAnalysis";
import ReportGeneration from "./components/ReportGeneration";
import FeedbackForm from "./components/FeedbackForm";
import Visualization from "./components/Visualization";
// import { runLangGraph } from "@/lib/LangGraphUtils";

interface VisualizationData {
  labels: string[];
  values: number[];
}

interface PageProps {
  // Add any page-level props here if needed
}

export default function Home({}: PageProps) {
  const [financialData, setFinancialData] = useState<any>(null);
  const [predictionResult, setPredictionResult] = useState<any>(null);
  const [report, setReport] = useState<any>(null);
  const [visualizationData, setVisualizationData] =
    useState<VisualizationData | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [voiceInput, setVoiceInput] = useState<string | null>(null);
  const [voiceOutput, setVoiceOutput] = useState<string | null>(null);

  const handleRunAnalysis = async (symbol: string) => {
    try {
      const simulatedResponse = {
        financialData: {
          symbol: symbol,
          dates: [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
          ],
          open: [150.0, 152.0, 155.0, 154.0, 156.0],
          high: [153.0, 154.5, 156.0, 155.5, 157.0],
          low: [149.5, 151.5, 153.0, 152.0, 154.0],
          close: [151.0, 153.0, 154.0, 153.5, 155.0],
          volume: [1000000, 1200000, 1100000, 950000, 1050000],
        },
        predictionResult: {
          forecast: [156.5, 157.8, 159.2, 160.5, 161.9],
          modelParameters: { p: 1, d: 1, q: 1 },
          accuracy: 0.92,
        },
        report: {
          summary:
            "The model predicts a steady increase in price over the next week.",
          forecast: [
            { day: "Day 1", predictedPrice: "156.50" },
            { day: "Day 2", predictedPrice: "157.80" },
            { day: "Day 3", predictedPrice: "159.20" },
            { day: "Day 4", predictedPrice: "160.50" },
            { day: "Day 5", predictedPrice: "161.90" },
          ],
          recommendation: "Consider buying.",
        },
        visualizationData: {
          labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
          values: [156.5, 157.8, 159.2, 160.5, 161.9],
        },
      };

      setFinancialData(simulatedResponse.financialData);
      setPredictionResult(simulatedResponse.predictionResult);
      setReport(simulatedResponse.report);
      setVisualizationData(simulatedResponse.visualizationData);
    } catch (error) {
      console.error("Error running LangGraph:", error);
    }
  };

  const handleFeedbackSubmit = (feedbackData: string) => {
    setFeedback(feedbackData);
  };

  const handleVoiceInput = (input: string) => {
    setVoiceInput(input);
  };

  const handleVoiceOutput = (output: string) => {
    setVoiceOutput(output);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">
        Financial Market Analysis System
      </h1>
      <DataIngestion onDataFetched={handleRunAnalysis} />
      {predictionResult && (
        <div className="mt-4">
          <MarketAnalysis predictionResult={predictionResult} />
        </div>
      )}
      {report && (
        <div className="mt-4">
          <ReportGeneration report={report} />
        </div>
      )}
      {visualizationData && (
        <div className="mt-4">
          <Visualization data={visualizationData} />
        </div>
      )}
      {report && (
        <div className="mt-4">
          <FeedbackForm onSubmit={handleFeedbackSubmit} />
        </div>
      )}
      {/* Optional Voice Interaction */}
      {/* <VoiceInteraction onInput={handleVoiceInput} onOutput={handleVoiceOutput} /> */}
    </div>
  );
}
