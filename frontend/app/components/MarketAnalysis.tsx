/* eslint-disable */

// app/components/MarketAnalysis.tsx
import React from "react";

interface MarketAnalysisProps {
  predictionResult: any;
}

const MarketAnalysis: React.FC<MarketAnalysisProps> = ({
  predictionResult,
}) => {
  if (!predictionResult) return null;

  return (
    <div className="bg-white/5 p-6 rounded-lg shadow-md border border-white/10">
      <h2 className="text-2xl font-semibold text-gray-200 mb-6">
        Market Analysis
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-300 mb-2">
            Predicted Forecast
          </h3>
          <ul className="list-disc list-inside space-y-1">
            {predictionResult.forecast.map((value: number, index: number) => (
              <li key={index} className="text-gray-400">
                Day {index + 1}:{" "}
                <span className="text-yellow-400 font-medium">
                  {value.toFixed(2)}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-300 mb-2">
            Model Parameters
          </h3>
          <p className="text-gray-400">
            p:{" "}
            <span className="text-green-400 font-medium">
              {predictionResult.modelParameters.p}
            </span>
            , d:{" "}
            <span className="text-green-400 font-medium">
              {predictionResult.modelParameters.d}
            </span>
            , q:{" "}
            <span className="text-green-400 font-medium">
              {predictionResult.modelParameters.q}
            </span>
          </p>
          <h3 className="text-lg font-semibold text-gray-300 mt-4 mb-2">
            Accuracy
          </h3>
          <p className="text-gray-400">
            <span className="text-purple-400 font-medium">
              {(predictionResult.accuracy * 100).toFixed(2)}%
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default MarketAnalysis;
