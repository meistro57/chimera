const API_BASE_URL = '/api'

class APIClient {
  async request(method, endpoint, data = null) {
    const url = `${API_BASE_URL}${endpoint}`

    const options = {
      method: method.toUpperCase(),
      headers: {
        'Content-Type': 'application/json',
      },
    }

    if (data) {
      options.body = JSON.stringify(data)
    }

    try {
      const response = await fetch(url, options)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      // Handle empty responses
      const text = await response.text()
      return text ? JSON.parse(text) : {}

    } catch (error) {
      console.error(`API request failed: ${method} ${endpoint}`, error)
      throw error
    }
  }

  async get(endpoint) {
    return this.request('GET', endpoint)
  }

  async post(endpoint, data) {
    return this.request('POST', endpoint, data)
  }

  async put(endpoint, data) {
    return this.request('PUT', endpoint, data)
  }

  async delete(endpoint) {
    return this.request('DELETE', endpoint)
  }

  // Conversation-specific methods
  async getConversations() {
    return this.get('/conversations')
  }

  async createConversation(conversationData) {
    return this.post('/conversations', conversationData)
  }

  async getConversation(conversationId) {
    return this.get(`/conversations/${conversationId}`)
  }

  async getConversationMessages(conversationId) {
    return this.get(`/conversations/${conversationId}/messages`)
  }

  async startConversation(conversationId) {
    return this.post(`/conversations/${conversationId}/start`)
  }

  async stopConversation(conversationId) {
    return this.post(`/conversations/${conversationId}/stop`)
  }

  async getProviders() {
    return this.get('/providers')
  }

  async getPersonas() {
    return this.get('/personas')
  }
}

export const api = new APIClient()