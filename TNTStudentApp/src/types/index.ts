export interface User {
  id: string;
  phone: string;
  name?: string;
}

export interface Vendor {
  id: string;
  name: string;
  description: string;
  image_url?: string;
  rating: number;
  delivery_time: string;
  estimated_delivery: string;
}

export interface Menu {
  id: string;
  name: string;
  vendor_id: string;
  image_url?: string;
  description: string;
}

export interface Item {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url?: string;
  menu_id: string;
}

export interface CartItem {
  item_id: string;
  quantity: number;
  name: string;
  price: number;
  item: Item;
}

export interface Slot {
  id: string;
  time: string;
  available: boolean;
  start_time: string;
  end_time: string;
  available_capacity: number;
}

export interface Order {
  id: string;
  vendor_id: string;
  items: CartItem[];
  total: number;
  status: string;
  slot: Slot;
  created_at: string;
  vendor_name: string;
  slot_time: string;
  total_amount: number;
  estimated_minutes: number;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface LoginRequest {
  phone: string;
}

export interface VerifyOTPRequest {
  phone: string;
  otp: string;
}

export interface OrderData {
  vendorId: string;
  slot: Slot;
  items: CartItem[];
  totalPrice: number;
  totalItems: number;
}

export type RootStackParamList = {
  Login: undefined;
  OTP: { phone: string };
  VendorList: undefined;
  VendorDetail: { vendorId: string };
  Menu: { vendorId: string; menuId: string };
  SlotSelection: { vendorId: string; items: CartItem[] };
  OrderConfirmation: { orderData: OrderData };
  OrderHistory: undefined;
  OrderDetail: { orderId: string };
};
