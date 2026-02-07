import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  AuthResponse,
  LoginRequest,
  VerifyOTPRequest,
  Vendor,
  Menu,
  Item,
  Slot,
  Order,
  User,
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = 'http://localhost:8000'; // Adjust based on your backend setup

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired, clear storage and redirect to login
          AsyncStorage.removeItem('authToken');
          AsyncStorage.removeItem('user');
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication methods
  async login(data: LoginRequest): Promise<{ success: boolean; message: string }> {
    const response = await this.api.post('/auth/login', data);
    return response.data;
  }

  async verifyOTP(data: VerifyOTPRequest): Promise<AuthResponse> {
    const response = await this.api.post('/auth/verify-otp', data);
    const { token, user } = response.data;

    // Store token and user data
    await AsyncStorage.setItem('authToken', token);
    await AsyncStorage.setItem('user', JSON.stringify(user));

    return response.data;
  }

  async logout(): Promise<void> {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('user');
  }

  async getCurrentUser(): Promise<User | null> {
    const userStr = await AsyncStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // Vendor methods
  async getVendors(): Promise<Vendor[]> {
    const response = await this.api.get('/vendors');
    return response.data;
  }

  async getVendorDetails(vendorId: string): Promise<Vendor> {
    const response = await this.api.get(`/vendors/${vendorId}`);
    return response.data;
  }

  // Menu methods
  async getVendorMenus(vendorId: string): Promise<Menu[]> {
    const response = await this.api.get(`/vendors/${vendorId}/menus`);
    return response.data;
  }

  async getMenuItems(menuId: string): Promise<Item[]> {
    const response = await this.api.get(`/menus/${menuId}/items`);
    return response.data;
  }

  // Slot methods
  async getAvailableSlots(vendorId: string, date?: string): Promise<Slot[]> {
    const params = date ? { date } : {};
    const response = await this.api.get(`/vendors/${vendorId}/slots`, { params });
    return response.data;
  }

  // Order methods
  async placeOrder(vendorId: string, items: any[], slotId: string): Promise<Order> {
    const response = await this.api.post('/orders', {
      vendor_id: vendorId,
      items,
      slot_id: slotId,
    });
    return response.data;
  }

  async getOrderHistory(): Promise<Order[]> {
    const response = await this.api.get('/orders');
    return response.data;
  }

  async getOrderDetails(orderId: string): Promise<Order> {
    const response = await this.api.get(`/orders/${orderId}`);
    return response.data;
  }

  async cancelOrder(orderId: string): Promise<{ success: boolean; message: string }> {
    const response = await this.api.delete(`/orders/${orderId}`);
    return response.data;
  }

  async getOrderStatus(orderId: string): Promise<{ status: string; estimated_time?: number }> {
    const response = await this.api.get(`/orders/${orderId}/status`);
    return response.data;
  }

  // Utility methods
  async isAuthenticated(): Promise<boolean> {
    const token = await AsyncStorage.getItem('authToken');
    return !!token;
  }
}

export const apiService = new ApiService();
