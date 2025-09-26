/**
 * Individual question result row component
 */

import React from 'react';
import { CheckCircle, XCircle, AlertCircle, Minus } from 'lucide-react';

const QuestionResultRow = ({ questionNumber, markedAnswer, correctAnswer, status }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'correct':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'incorrect':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'not_attempted':
        return <Minus className="w-5 h-5 text-gray-400" />;
      case 'invalid':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'correct':
        return 'Correct';
      case 'incorrect':
        return 'Incorrect';
      case 'not_attempted':
        return 'Not Attempted';
      case 'invalid':
        return 'Invalid';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'correct':
        return 'text-green-600 bg-green-50';
      case 'incorrect':
        return 'text-red-600 bg-red-50';
      case 'not_attempted':
        return 'text-gray-600 bg-gray-50';
      case 'invalid':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getRowBgColor = (status) => {
    switch (status) {
      case 'correct':
        return 'bg-green-50';
      case 'incorrect':
        return 'bg-red-50';
      default:
        return 'bg-white hover:bg-gray-50';
    }
  };

  return (
    <tr className={`${getRowBgColor(status)} transition-colors`}>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-gray-700">{questionNumber}</span>
          </div>
        </div>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          {markedAnswer ? (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${
              status === 'correct' ? 'bg-green-100 text-green-800' : 
              status === 'incorrect' ? 'bg-red-100 text-red-800' : 
              'bg-gray-100 text-gray-800'
            }`}>
              {markedAnswer}
            </span>
          ) : (
            <span className="text-gray-400 italic">Not marked</span>
          )}
        </div>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
          {correctAnswer}
        </span>
      </td>
      
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          {getStatusIcon(status)}
          <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
            {getStatusText(status)}
          </span>
        </div>
      </td>
    </tr>
  );
};

export default QuestionResultRow;
