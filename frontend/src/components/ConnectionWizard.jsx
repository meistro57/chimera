import { useState } from 'react';

const ConnectionWizard = ({ onClose }) => {
  const [keys, setKeys] = useState({
    openai_api_key: '',
    anthropic_api_key: '',
    deepseek_api_key: '',
    google_ai_api_key: '',
    openrouter_api_key: '',
    lm_studio_url: 'http://localhost:1234',
    ollama_url: 'http://localhost:11434'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/settings/update-api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keys)
      });
      if (response.ok) {
        alert('API keys updated successfully!');
        onClose();
        window.location.reload(); // Refresh to update header status
      }
    } catch (error) {
      alert('Error updating keys');
    }
  };

  const handleInputChange = (e) => {
    setKeys({ ...keys, [e.target.name]: e.target.value });
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Configure AI Providers</h2>
        <form onSubmit={handleSubmit}>
          <div className="space-y-3">
            {Object.keys(keys).map((key) => (
              <div key={key}>
                <label className="block text-sm font-medium">
                  {key.replace('_', ' ').toUpperCase()}:
                </label>
                <input
                  type={key.includes('url') ? 'url' : 'text'}
                  name={key}
                  value={keys[key]}
                  onChange={handleInputChange}
                  className="mt-1 p-2 border border-gray-300 rounded w-full"
                  placeholder={key.includes('url') ? 'http://localhost:1234' : 'sk-...'}
                />
              </div>
            ))}
          </div>
          <div className="flex justify-end mt-4">
            <button
              type="button"
              onClick={onClose}
              className="mr-2 px-4 py-2 bg-gray-300 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded"
            >
              Save Configuration
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ConnectionWizard;