import { supabase } from './supabase';

const API_BASE_URL = 'http://localhost:5000';

export const paymentService = {
  // Create a PayTR payment session
  async createPaytrSession(paymentData) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('No active session');
      }

      const response = await fetch(`${API_BASE_URL}/payments/paytr/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(paymentData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create payment session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating payment session:', error);
      throw error;
    }
  },

  // Check order status
  async getOrderStatus(merchantOid) {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('No active session');
      }

      const response = await fetch(`${API_BASE_URL}/payments/paytr/status?merchant_oid=${merchantOid}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get order status');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting order status:', error);
      throw error;
    }
  },

  // Poll order status until final state
  async pollOrderStatus(merchantOid, maxAttempts = 30, interval = 2000) {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const status = await this.getOrderStatus(merchantOid);
        
        if (status.status === 'paid' || status.status === 'failed') {
          return status;
        }
        
        // Wait before next attempt
        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        console.error(`Poll attempt ${attempt + 1} failed:`, error);
        // Continue polling even if one attempt fails
        await new Promise(resolve => setTimeout(resolve, interval));
      }
    }
    
    throw new Error('Order status polling timed out');
  }
};
