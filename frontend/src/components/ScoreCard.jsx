/**
 * Score card component displaying overall results
 */

import React from 'react';
import { Trophy, Target, TrendingUp } from 'lucide-react';

const ScoreCard = ({ score, total, percentage }) => {
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

  const getGrade = (percentage) => {
    if (percentage >= 90) return 'A+';
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B';
    if (percentage >= 60) return 'C';
    if (percentage >= 50) return 'D';
    return 'F';
  };

  return (
    <div className={`border-2 rounded-lg p-6 ${getScoreBgColor(percentage)}`}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main Score */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <Trophy className={`w-6 h-6 mr-2 ${getScoreColor(percentage)}`} />
            <h3 className="text-lg font-semibold text-gray-800">Score</h3>
          </div>
          <div className={`text-4xl font-bold ${getScoreColor(percentage)}`}>
            {score}/{total}
          </div>
          <div className="text-sm text-gray-600 mt-1">Questions Correct</div>
        </div>

        {/* Percentage */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <TrendingUp className={`w-6 h-6 mr-2 ${getScoreColor(percentage)}`} />
            <h3 className="text-lg font-semibold text-gray-800">Percentage</h3>
          </div>
          <div className={`text-4xl font-bold ${getScoreColor(percentage)}`}>
            {percentage}%
          </div>
          <div className="text-sm text-gray-600 mt-1">Overall Score</div>
        </div>

        {/* Grade */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <Target className={`w-6 h-6 mr-2 ${getScoreColor(percentage)}`} />
            <h3 className="text-lg font-semibold text-gray-800">Grade</h3>
          </div>
          <div className={`text-4xl font-bold ${getScoreColor(percentage)}`}>
            {getGrade(percentage)}
          </div>
          <div className="text-sm text-gray-600 mt-1">Letter Grade</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{score} of {total} correct</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              percentage >= 80
                ? 'bg-green-500'
                : percentage >= 60
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default ScoreCard;
