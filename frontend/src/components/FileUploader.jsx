/**
 * File upload component for OMR sheets
 */

import React, { useState, useRef } from 'react';
import { uploadOMRSheet } from '../api';
import { Upload, FileImage, AlertCircle, ChevronDown } from 'lucide-react';

const FileUploader = ({ 
  onUploadStart, 
  onUploadSuccess, 
  onUploadError, 
  availableKeys,
  serverConnected 
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedKey, setSelectedKey] = useState('exam1');
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      onUploadError('Please select a valid image file (.jpg, .jpeg, .png)');
      return;
    }

    // Validate file size (5MB limit)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      onUploadError('File size too large. Maximum allowed size is 5MB.');
      return;
    }

    setSelectedFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      onUploadError('Please select a file first');
      return;
    }

    if (!serverConnected) {
      onUploadError('Server is not connected. Please start the backend server.');
      return;
    }

    try {
      onUploadStart();
      const result = await uploadOMRSheet(selectedFile, selectedKey);
      onUploadSuccess(result);
    } catch (error) {
      onUploadError(error.message);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Upload OMR Sheet</h2>
        <p className="text-gray-600">
          Select your scanned OMR sheet image for automatic evaluation
        </p>
      </div>

      {/* File Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : selectedFile
            ? 'border-green-300 bg-green-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".jpg,.jpeg,.png"
          onChange={handleFileInputChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        {!selectedFile ? (
          <div>
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Drop your OMR sheet here, or click to browse
            </p>
            <p className="text-sm text-gray-500">
              Supports JPG, JPEG, PNG files up to 5MB
            </p>
          </div>
        ) : (
          <div>
            <FileImage className="mx-auto h-12 w-12 text-green-500 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {selectedFile.name}
            </p>
            <p className="text-sm text-gray-500 mb-4">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
            <button
              onClick={clearSelection}
              className="text-sm text-red-600 hover:text-red-800 underline"
            >
              Remove file
            </button>
          </div>
        )}
      </div>

      {/* Preview */}
      {preview && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Preview</h3>
          <div className="border rounded-lg overflow-hidden">
            <img
              src={preview}
              alt="OMR Sheet Preview"
              className="w-full h-64 object-contain bg-gray-50"
            />
          </div>
        </div>
      )}

      {/* Answer Key Selection */}
      <div className="mt-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Answer Key
        </label>
        <div className="relative">
          <select
            value={selectedKey}
            onChange={(e) => setSelectedKey(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 appearance-none bg-white"
          >
            {availableKeys.map((key) => (
              <option key={key} value={key}>
                {key.charAt(0).toUpperCase() + key.slice(1)}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 pointer-events-none" />
        </div>
      </div>

      {/* Server Status Warning */}
      {!serverConnected && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Server Disconnected</h3>
              <p className="text-sm text-red-700 mt-1">
                Please start the backend server before uploading files.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div className="mt-8">
        <button
          onClick={handleSubmit}
          disabled={!selectedFile || !serverConnected}
          className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
            selectedFile && serverConnected
              ? 'bg-primary-600 hover:bg-primary-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {!selectedFile
            ? 'Select a file to continue'
            : !serverConnected
            ? 'Server disconnected'
            : 'Process OMR Sheet'
          }
        </button>
      </div>

      {/* Instructions */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <h3 className="text-sm font-medium text-blue-800 mb-2">Instructions:</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Ensure the OMR sheet is clearly scanned with good contrast</li>
          <li>• The sheet should be properly aligned (not skewed)</li>
          <li>• All bubbles should be clearly visible</li>
          <li>• Use dark pencil marks for filled bubbles</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUploader;
