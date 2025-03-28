/* eslint-disable */
// lib/apiUtils.ts
//  Mock fetchFinancialData and generateReport
export const fetchFinancialData = async (symbol: string): Promise<any> => {
  // Simulate fetching financial data from an API.
  await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay
  return {
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
  };
};

export const generateReport = async (predictionResult: any): Promise<any> => {
  await new Promise((resolve) => setTimeout(resolve, 500));
  const { forecast, modelParameters, accuracy } = predictionResult;

  const report = {
    summary: `The model predicts the following stock prices for the next week.  The model accuracy is ${accuracy.toFixed(
      2
    )}.`,
    forecast: forecast.map((value: number, index: number) => ({
      day: `Day ${index + 1}`,
      predictedPrice: value.toFixed(2),
    })),
    modelParameters: modelParameters,
    recommendation: "", // To be filled in
  };

  // Basic Recommendation Logic
  const firstDayPrediction = forecast[0];
  const lastDayPrediction = forecast[forecast.length - 1];

  if (lastDayPrediction > firstDayPrediction * 1.05) {
    report.recommendation =
      "The model predicts a significant upward trend.  Consider buying.";
  } else if (lastDayPrediction < firstDayPrediction * 0.95) {
    report.recommendation =
      "The model predicts a significant downward trend.  Consider selling.";
  } else {
    report.recommendation =
      "The model predicts a relatively stable trend.  Hold or trade cautiously.";
  }
  return report;
};
