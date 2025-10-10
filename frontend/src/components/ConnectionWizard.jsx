import React from 'react'

const ConnectionWizard = ({ onClose }) => {
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Configure AI Providers</h2>
        <p className="mb-4">
          You can configure API keys for various AI providers here.
          Enter your OpenRouter API key and click Save to enable live conversations!
        </p>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium">OpenRouter API Key:</label>
            <input
              type="text"
              className="mt-1 p-2 border border-gray-300 rounded w-full"
              placeholder="sk-or-v1-..."
              onChange={(e) => {
                // For now, save immediately on change
                const apiKey = e.target.value;
                if (apiKey.trim()) {
                  fetch('/api/providers/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ provider: 'openrouter', api_key: apiKey })
                  }).then(() => {
                    alert('OpenRouter API key saved! Refreshing provider status...');
                    // The providers will be reloaded automatically
                  }).catch(err => {
                    alert('Error saving API key: ' + err.message);
                  });
                }
              }}
            />
          </div>
        </div>
        <div className="flex justify-end mt-4">
          <button
            onClick={async () => {
              // Test the OpenRouter key
              try {
                const response = await fetch('/api/providers/test', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ provider: 'openrouter' })
                });
                const result = await response.json();
                if (result.status === 'success') {
                  alert(`✅ ${result.provider}: ${result.message}\n\nTest response: "${result.response_sample}"`);
                } else {
                  alert(`❌ ${result.provider}: ${result.message}`);
                }
              } catch (err) {
                alert('❌ Test failed: ' + err.message);
              }
            }}
            className="mr-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Test Key
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConnectionWizard;