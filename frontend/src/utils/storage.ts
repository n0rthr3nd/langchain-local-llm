import { Conversation } from '../types';

const CONVERSATIONS_KEY = 'chatgpt-conversations';
const SETTINGS_KEY = 'chatgpt-settings';

export const storage = {
  getConversations(): Conversation[] {
    const data = localStorage.getItem(CONVERSATIONS_KEY);
    return data ? JSON.parse(data) : [];
  },

  saveConversations(conversations: Conversation[]): void {
    localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
  },

  getSettings() {
    const data = localStorage.getItem(SETTINGS_KEY);
    return data ? JSON.parse(data) : {
      model: 'llama3.2',
      temperature: 0.7,
      max_tokens: 2048,
      system_prompt: 'Eres un asistente útil.',
    };
  },

  saveSettings(settings: any): void {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  },

  exportConversations(): string {
    return JSON.stringify(this.getConversations(), null, 2);
  },

  importConversations(jsonString: string): void {
    try {
      const conversations = JSON.parse(jsonString);
      this.saveConversations(conversations);
    } catch (error) {
      throw new Error('Invalid JSON format');
    }
  },
};
