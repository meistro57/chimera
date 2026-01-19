import React, { useState, useEffect } from 'react';
import { Check, Plus, Settings } from 'lucide-react';
import PersonaAvatar from '../Chat/PersonaAvatar';
import ConnectionWizard from '../ConnectionWizard';

const DEFAULT_PERSONA_SELECTION = ["philosopher", "comedian", "scientist"];

const PersonaCards = ({ participants, setParticipants }) => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [selectedPersonas, setSelectedPersonas] = useState(["", "", ""]);
  const [tempValues, setTempValues] = useState([0.7, 0.7, 0.7]);
  const [availablePersonas, setAvailablePersonas] = useState(["philosopher", "comedian", "scientist", "chef", "awakening_mind"]);
  const [showConnectionWizard, setShowConnectionWizard] = useState(false);

  useEffect(() => {
    const normalized = (participants || DEFAULT_PERSONA_SELECTION)
      .slice(0, 3)
      .map((persona) => persona || "")
    const padded = [...normalized, ...Array(3 - normalized.length).fill("")]
    setSelectedPersonas(padded)
  }, [participants])

  const handleCardClick = (index) => {
    setSelectedCard(index);
  };

  const handlePersonaSelect = (index, persona) => {
    const newSelected = [...selectedPersonas];
    newSelected[index] = persona || "";
    setSelectedPersonas(newSelected);
  };

  const handleTempChange = (index, temp) => {
    const newTemps = [...tempValues];
    newTemps[index] = temp;
    setTempValues(newTemps);
  };

  const handleConfirm = () => {
    const newParticipants = selectedPersonas.filter(p => p);
    setParticipants(newParticipants);
    setSelectedCard(null);
  };

  return (
    <div className="flex space-x-6 justify-center">
      {["Chat Bot 1", "Chat Bot 2", "Chat Bot 3"].map((label, index) => (
        <div key={index} className="relative">
          <div
            onClick={() => handleCardClick(index)}
            className={`relative bg-white border-2 rounded-lg p-6 shadow-md hover:shadow-lg transition-all duration-500 cursor-pointer ${
              selectedPersonas[index] ? 'border-green-500' : 'border-gray-300'
            } ${selectedCard === index ? 'scale-150 z-10' : ''}`}
          >
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2">
                {selectedPersonas[index] ? (
                  <PersonaAvatar persona={selectedPersonas[index]} size="md" />
                ) : (
                  <div className="w-full h-full bg-gray-300 rounded-full flex items-center justify-center">
                    <Plus className="w-6 h-6 text-gray-600" />
                  </div>
                )}
              </div>
              <p className="text-sm font-medium">{label}</p>
              {selectedPersonas[index] && (
                <div className="mt-1">
                  <p className="text-xs text-gray-600 capitalize">
                    {selectedPersonas[index].replace('_', ' ')}
                  </p>
                  <div className="mt-1 flex justify-center">
                    <Check className="w-4 h-4 text-green-500" />
                  </div>
                </div>
              )}
            </div>
          </div>

          {selectedCard === index && (
            <div className="absolute top-full mt-4 bg-white border border-gray-300 rounded-lg p-4 shadow-lg z-20 w-80">
              <select
                value={selectedPersonas[index]}
                onChange={(e) => handlePersonaSelect(index, e.target.value)}
                className="w-full mb-4 p-2 border border-gray-300 rounded"
              >
                <option value="">Select Persona</option>
                {availablePersonas.map(persona => (
                  <option key={persona} value={persona}>{persona}</option>
                ))}
              </select>

              <div className="mb-4">
                <label className="block text-sm mb-2">Temperature: {tempValues[index]}</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={tempValues[index]}
                  onChange={(e) => handleTempChange(index, parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <button
                onClick={() => setShowConnectionWizard(true)}
                className="w-full mb-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center justify-center gap-2"
              >
                <Settings className="w-4 h-4" />
                API Configuration
              </button>

              <button
                onClick={handleConfirm}
                className="w-full p-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                OK
              </button>
            </div>
          )}
        </div>
      ))}
      {showConnectionWizard && (
        <ConnectionWizard onClose={() => setShowConnectionWizard(false)} />
      )}
    </div>
  );
};

export default PersonaCards;