/* eslint-disable */
"use client";
// app/components/FeedbackForm.tsx
import React, { useState } from "react";

interface FeedbackFormProps {
  onSubmit: (feedback: string) => void;
}

const FeedbackForm: React.FC<FeedbackFormProps> = ({ onSubmit }) => {
  const [feedback, setFeedback] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(feedback);
    setFeedback(""); // Clear the form after submission
  };

  return (
    <div className="bg-white/5 p-6 rounded-lg shadow-md border border-white/10">
      <h2 className="text-2xl font-semibold text-gray-200 mb-6">
        Feedback Form
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={feedback}
          onChange={(e) => setFeedback((e.target as HTMLTextAreaElement).value)}
          placeholder="Enter your feedback..."
          className="border border-gray-700 bg-gray-800 text-white p-4 rounded-md w-full min-h-[120px] focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-green-500/20 text-green-300 hover:bg-green-500/30 hover:text-green-200 px-6 py-3 rounded-md transition-colors w-full"
        >
          Submit Feedback
        </button>
      </form>
    </div>
  );
};

export default FeedbackForm;
