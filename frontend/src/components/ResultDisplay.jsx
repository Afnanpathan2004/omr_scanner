/**
 * Result display component for OMR evaluation results
 */

import React from 'react';
import ScoreCard from './ScoreCard';
import QuestionResultRow from './QuestionResultRow';
import { ArrowLeft, Download, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const ResultDisplay = ({ result, onStartOver }) => {
  const {
    score,
    total,
    percentage,
    marked_answers,
    correct_answers,
    result: questionResults,
    processing_info
  } = result;

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-50 border-green-200';
    if (percentage >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const exportResults = () => {
    const resultData = {
      score,
      total,
      percentage,
      timestamp: new Date().toISOString(),
      questions: Object.keys(correct_answers).map(qNum => ({
        question: qNum,
        marked: marked_answers[qNum] || 'Not Attempted',
        correct: correct_answers[qNum],
        status: questionResults[qNum]
      }))
    };

    const blob = new Blob([JSON.stringify(resultData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `omr-result-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-3xl font-bold text-gray-900">Evaluation Results</h2>
          <button
            onClick={onStartOver}
            className="flex items-center px-4 py-2 text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-md transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Upload Another Sheet
          </button>
        </div>

        {/* Score Card */}
        <ScoreCard
          score={score}
          total={total}
          percentage={percentage}
        />

        {/* Action Buttons */}
        <div className="flex gap-4 mt-6">
          <button
            onClick={exportResults}
            className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Results
          </button>
        </div>
      </div>

      {/* Detailed Results */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Question-wise Analysis</h3>
        
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <CheckCircle className="w-5 h-5 text-green-600 mr-1" />
              <span className="text-sm font-medium text-green-800">Correct</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {Object.values(questionResults).filter(r => r === 'correct').length}
            </div>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <XCircle className="w-5 h-5 text-red-600 mr-1" />
              <span className="text-sm font-medium text-red-800">Incorrect</span>
            </div>
            <div className="text-2xl font-bold text-red-600">
              {Object.values(questionResults).filter(r => r === 'incorrect').length}
            </div>
          </div>
          
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <AlertCircle className="w-5 h-5 text-gray-600 mr-1" />
              <span className="text-sm font-medium text-gray-800">Not Attempted</span>
            </div>
            <div className="text-2xl font-bold text-gray-600">
              {Object.values(questionResults).filter(r => r === 'not_attempted').length}
            </div>
          </div>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <AlertCircle className="w-5 h-5 text-yellow-600 mr-1" />
              <span className="text-sm font-medium text-yellow-800">Invalid</span>
            </div>
            <div className="text-2xl font-bold text-yellow-600">
              {Object.values(questionResults).filter(r => r === 'invalid').length}
            </div>
          </div>
        </div>

        {/* Question Results Table */}
        <div className="overflow-hidden border border-gray-200 rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Question
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Your Answer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Correct Answer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.keys(correct_answers).map((questionNum) => (
                <QuestionResultRow
                  key={questionNum}
                  questionNumber={questionNum}
                  markedAnswer={marked_answers[questionNum] || ''}
                  correctAnswer={correct_answers[questionNum]}
                  status={questionResults[questionNum]}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Processing Information */}
      {processing_info && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Bubbles Detected:</span>
              <span className="ml-2 text-gray-600">{processing_info.total_bubbles_detected}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Detection Threshold:</span>
              <span className="ml-2 text-gray-600">{processing_info.detection_threshold}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Processing Method:</span>
              <span className="ml-2 text-gray-600">{processing_info.image_processing}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultDisplay;
