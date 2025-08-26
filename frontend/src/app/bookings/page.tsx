'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import AppLayout from '@/components/AppLayout';
import * as Dialog from '@radix-ui/react-dialog';
import { 
  Calendar, 
  Users, 
  Clock, 
  Search, 
  Filter,
  Eye,
  Edit,
  X,
  Phone,
  Mail,
  MapPin,
  Bed,
  CreditCard,
  Plus,
  CheckCircle,
  User,
  Sparkles,
  Wrench,
  Ban,
  AlertTriangle,
  List,
  CalendarDays,
  MoreHorizontal,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  LogOut
} from 'lucide-react';

interface Guest {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  nationality: string;
}

interface ReservationRoom {
  id: number;
  room_number: string;
  room_type_name: string;
  rate: number;
  total_amount: number;
}

interface Reservation {
  id: number;
  reservation_number: string;
  guest_name: string;
  guest_details: Guest;
  check_in_date: string;
  check_out_date: string;
  nights: number;
  adults: number;
  children: number;
  status: string;
  status_display: string;
  booking_source: string;
  total_rooms: number;
  total_amount: number;
  created_at: string;
  rooms: ReservationRoom[];
  special_requests?: string;
  can_cancel: boolean;
}

const MOCK_RESERVATIONS: Reservation[] = [
  {
    id: 1,
    reservation_number: 'RSV123456',
    guest_name: 'John Smith',
    guest_details: {
      id: 1,
      full_name: 'John Smith',
      email: 'john.smith@email.com',
      phone: '+62-812-1111-0001',
      nationality: 'United States'
    },
    check_in_date: '2024-08-25',
    check_out_date: '2024-08-28',
    nights: 3,
    adults: 2,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'DIRECT',
    total_rooms: 1,
    total_amount: 6750000,
    created_at: '2024-08-23T10:30:00Z',
    rooms: [
      {
        id: 1,
        room_number: '101',
        room_type_name: 'Standard Room',
        rate: 2250000,
        total_amount: 6750000
      }
    ],
    special_requests: 'Late check-in requested',
    can_cancel: true
  },
  {
    id: 2,
    reservation_number: 'RSV789012',
    guest_name: 'Maria Rodriguez',
    guest_details: {
      id: 2,
      full_name: 'Maria Rodriguez',
      email: 'maria.rodriguez@email.com',
      phone: '+62-812-1111-0002',
      nationality: 'Spain'
    },
    check_in_date: '2024-08-24',
    check_out_date: '2024-08-26',
    nights: 2,
    adults: 1,
    children: 1,
    status: 'CHECKED_IN',
    status_display: 'Checked In',
    booking_source: 'OTA',
    total_rooms: 1,
    total_amount: 4800000,
    created_at: '2024-08-20T14:15:00Z',
    rooms: [
      {
        id: 2,
        room_number: '205',
        room_type_name: 'Deluxe Room',
        rate: 2400000,
        total_amount: 4800000
      }
    ],
    can_cancel: false
  },
  {
    id: 3,
    reservation_number: 'RSV345678',
    guest_name: 'Ahmad Pratama',
    guest_details: {
      id: 3,
      full_name: 'Ahmad Pratama',
      email: 'ahmad.pratama@email.com',
      phone: '+62-812-1111-0003',
      nationality: 'Indonesia'
    },
    check_in_date: '2024-08-26',
    check_out_date: '2024-08-29',
    nights: 3,
    adults: 2,
    children: 2,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'WEBSITE',
    total_rooms: 2,
    total_amount: 10800000,
    created_at: '2024-08-22T09:15:00Z',
    rooms: [
      {
        id: 3,
        room_number: '301',
        room_type_name: 'Family Suite',
        rate: 3600000,
        total_amount: 10800000
      }
    ],
    special_requests: 'Twin beds for children',
    can_cancel: true
  },
  {
    id: 4,
    reservation_number: 'RSV901234',
    guest_name: 'Sarah Johnson',
    guest_details: {
      id: 4,
      full_name: 'Sarah Johnson',
      email: 'sarah.johnson@email.com',
      phone: '+62-812-1111-0004',
      nationality: 'Australia'
    },
    check_in_date: '2024-08-27',
    check_out_date: '2024-08-30',
    nights: 3,
    adults: 1,
    children: 0,
    status: 'PENDING',
    status_display: 'Pending',
    booking_source: 'OTA',
    total_rooms: 1,
    total_amount: 6750000,
    created_at: '2024-08-24T16:20:00Z',
    rooms: [
      {
        id: 4,
        room_number: '102',
        room_type_name: 'Standard Room',
        rate: 2250000,
        total_amount: 6750000
      }
    ],
    can_cancel: true
  },
  {
    id: 5,
    reservation_number: 'RSV567890',
    guest_name: 'Hiroshi Tanaka',
    guest_details: {
      id: 5,
      full_name: 'Hiroshi Tanaka',
      email: 'hiroshi.tanaka@email.com',
      phone: '+62-812-1111-0005',
      nationality: 'Japan'
    },
    check_in_date: '2024-08-28',
    check_out_date: '2024-09-01',
    nights: 4,
    adults: 2,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'DIRECT',
    total_rooms: 1,
    total_amount: 12000000,
    created_at: '2024-08-21T11:45:00Z',
    rooms: [
      {
        id: 5,
        room_number: '401',
        room_type_name: 'Premium Room',
        rate: 3000000,
        total_amount: 12000000
      }
    ],
    special_requests: 'Vegetarian meals only',
    can_cancel: true
  },
  {
    id: 6,
    reservation_number: 'RSV234567',
    guest_name: 'Emma Wilson',
    guest_details: {
      id: 6,
      full_name: 'Emma Wilson',
      email: 'emma.wilson@email.com',
      phone: '+62-812-1111-0006',
      nationality: 'United Kingdom'
    },
    check_in_date: '2024-08-29',
    check_out_date: '2024-09-02',
    nights: 4,
    adults: 3,
    children: 1,
    status: 'CHECKED_OUT',
    status_display: 'Checked Out',
    booking_source: 'OTA',
    total_rooms: 2,
    total_amount: 14400000,
    created_at: '2024-08-19T13:30:00Z',
    rooms: [
      {
        id: 6,
        room_number: '201',
        room_type_name: 'Deluxe Room',
        rate: 2400000,
        total_amount: 9600000
      },
      {
        id: 7,
        room_number: '202',
        room_type_name: 'Deluxe Room',
        rate: 2400000,
        total_amount: 4800000
      }
    ],
    can_cancel: false
  },
  {
    id: 7,
    reservation_number: 'RSV890123',
    guest_name: 'Pierre Dubois',
    guest_details: {
      id: 7,
      full_name: 'Pierre Dubois',
      email: 'pierre.dubois@email.com',
      phone: '+62-812-1111-0007',
      nationality: 'France'
    },
    check_in_date: '2024-08-30',
    check_out_date: '2024-09-03',
    nights: 4,
    adults: 2,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'DIRECT',
    total_rooms: 1,
    total_amount: 18000000,
    created_at: '2024-08-18T08:15:00Z',
    rooms: [
      {
        id: 8,
        room_number: '501',
        room_type_name: 'Presidential Suite',
        rate: 4500000,
        total_amount: 18000000
      }
    ],
    special_requests: 'Champagne and flowers for anniversary',
    can_cancel: true
  },
  {
    id: 8,
    reservation_number: 'RSV456789',
    guest_name: 'Liu Wei',
    guest_details: {
      id: 8,
      full_name: 'Liu Wei',
      email: 'liu.wei@email.com',
      phone: '+62-812-1111-0008',
      nationality: 'China'
    },
    check_in_date: '2024-09-01',
    check_out_date: '2024-09-03',
    nights: 2,
    adults: 1,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'WEBSITE',
    total_rooms: 1,
    total_amount: 6000000,
    created_at: '2024-08-25T14:22:00Z',
    rooms: [
      {
        id: 9,
        room_number: '402',
        room_type_name: 'Premium Room',
        rate: 3000000,
        total_amount: 6000000
      }
    ],
    can_cancel: true
  },
  {
    id: 9,
    reservation_number: 'RSV012345',
    guest_name: 'Carlos Silva',
    guest_details: {
      id: 9,
      full_name: 'Carlos Silva',
      email: 'carlos.silva@email.com',
      phone: '+62-812-1111-0009',
      nationality: 'Brazil'
    },
    check_in_date: '2024-09-02',
    check_out_date: '2024-09-05',
    nights: 3,
    adults: 2,
    children: 1,
    status: 'PENDING',
    status_display: 'Pending',
    booking_source: 'OTA',
    total_rooms: 1,
    total_amount: 10800000,
    created_at: '2024-08-26T17:10:00Z',
    rooms: [
      {
        id: 10,
        room_number: '302',
        room_type_name: 'Family Suite',
        rate: 3600000,
        total_amount: 10800000
      }
    ],
    special_requests: 'High floor room with city view',
    can_cancel: true
  },
  {
    id: 10,
    reservation_number: 'RSV678901',
    guest_name: 'Anna Kowalski',
    guest_details: {
      id: 10,
      full_name: 'Anna Kowalski',
      email: 'anna.kowalski@email.com',
      phone: '+62-812-1111-0010',
      nationality: 'Poland'
    },
    check_in_date: '2024-09-03',
    check_out_date: '2024-09-06',
    nights: 3,
    adults: 1,
    children: 0,
    status: 'CANCELLED',
    status_display: 'Cancelled',
    booking_source: 'DIRECT',
    total_rooms: 1,
    total_amount: 7200000,
    created_at: '2024-08-17T12:05:00Z',
    rooms: [
      {
        id: 11,
        room_number: '203',
        room_type_name: 'Deluxe Room',
        rate: 2400000,
        total_amount: 7200000
      }
    ],
    can_cancel: false
  },
  {
    id: 11,
    reservation_number: 'RSV345612',
    guest_name: 'Ahmed Al-Rashid',
    guest_details: {
      id: 11,
      full_name: 'Ahmed Al-Rashid',
      email: 'ahmed.alrashid@email.com',
      phone: '+62-812-1111-0011',
      nationality: 'UAE'
    },
    check_in_date: '2024-09-04',
    check_out_date: '2024-09-08',
    nights: 4,
    adults: 2,
    children: 2,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'WEBSITE',
    total_rooms: 2,
    total_amount: 21600000,
    created_at: '2024-08-16T09:30:00Z',
    rooms: [
      {
        id: 12,
        room_number: '303',
        room_type_name: 'Family Suite',
        rate: 3600000,
        total_amount: 14400000
      },
      {
        id: 13,
        room_number: '304',
        room_type_name: 'Family Suite',
        rate: 3600000,
        total_amount: 7200000
      }
    ],
    special_requests: 'Halal meals and prayer mat',
    can_cancel: true
  },
  {
    id: 12,
    reservation_number: 'RSV789456',
    guest_name: 'Olivia Thompson',
    guest_details: {
      id: 12,
      full_name: 'Olivia Thompson',
      email: 'olivia.thompson@email.com',
      phone: '+62-812-1111-0012',
      nationality: 'Canada'
    },
    check_in_date: '2024-09-05',
    check_out_date: '2024-09-07',
    nights: 2,
    adults: 1,
    children: 0,
    status: 'CHECKED_IN',
    status_display: 'Checked In',
    booking_source: 'OTA',
    total_rooms: 1,
    total_amount: 4500000,
    created_at: '2024-08-28T15:45:00Z',
    rooms: [
      {
        id: 14,
        room_number: '103',
        room_type_name: 'Standard Room',
        rate: 2250000,
        total_amount: 4500000
      }
    ],
    can_cancel: false
  },
  {
    id: 13,
    reservation_number: 'RSV123789',
    guest_name: 'Hans Mueller',
    guest_details: {
      id: 13,
      full_name: 'Hans Mueller',
      email: 'hans.mueller@email.com',
      phone: '+62-812-1111-0013',
      nationality: 'Germany'
    },
    check_in_date: '2024-09-06',
    check_out_date: '2024-09-10',
    nights: 4,
    adults: 2,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'DIRECT',
    total_rooms: 1,
    total_amount: 12000000,
    created_at: '2024-08-15T11:20:00Z',
    rooms: [
      {
        id: 15,
        room_number: '403',
        room_type_name: 'Premium Room',
        rate: 3000000,
        total_amount: 12000000
      }
    ],
    special_requests: 'Extra towels and early breakfast',
    can_cancel: true
  },
  {
    id: 14,
    reservation_number: 'RSV456123',
    guest_name: 'Raj Patel',
    guest_details: {
      id: 14,
      full_name: 'Raj Patel',
      email: 'raj.patel@email.com',
      phone: '+62-812-1111-0014',
      nationality: 'India'
    },
    check_in_date: '2024-09-07',
    check_out_date: '2024-09-09',
    nights: 2,
    adults: 3,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'OTA',
    total_rooms: 2,
    total_amount: 9600000,
    created_at: '2024-08-27T10:15:00Z',
    rooms: [
      {
        id: 16,
        room_number: '204',
        room_type_name: 'Deluxe Room',
        rate: 2400000,
        total_amount: 4800000
      },
      {
        id: 17,
        room_number: '206',
        room_type_name: 'Deluxe Room',
        rate: 2400000,
        total_amount: 4800000
      }
    ],
    can_cancel: true
  },
  {
    id: 15,
    reservation_number: 'RSV789123',
    guest_name: 'Sofia Andersson',
    guest_details: {
      id: 15,
      full_name: 'Sofia Andersson',
      email: 'sofia.andersson@email.com',
      phone: '+62-812-1111-0015',
      nationality: 'Sweden'
    },
    check_in_date: '2024-09-08',
    check_out_date: '2024-09-11',
    nights: 3,
    adults: 2,
    children: 1,
    status: 'PENDING',
    status_display: 'Pending',
    booking_source: 'WEBSITE',
    total_rooms: 1,
    total_amount: 10800000,
    created_at: '2024-08-29T13:40:00Z',
    rooms: [
      {
        id: 18,
        room_number: '305',
        room_type_name: 'Family Suite',
        rate: 3600000,
        total_amount: 10800000
      }
    ],
    special_requests: 'Baby crib needed',
    can_cancel: true
  },
  {
    id: 16,
    reservation_number: 'RSV012789',
    guest_name: 'Marco Rossi',
    guest_details: {
      id: 16,
      full_name: 'Marco Rossi',
      email: 'marco.rossi@email.com',
      phone: '+62-812-1111-0016',
      nationality: 'Italy'
    },
    check_in_date: '2024-09-09',
    check_out_date: '2024-09-12',
    nights: 3,
    adults: 2,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'DIRECT',
    total_rooms: 1,
    total_amount: 13500000,
    created_at: '2024-08-14T16:55:00Z',
    rooms: [
      {
        id: 19,
        room_number: '502',
        room_type_name: 'Presidential Suite',
        rate: 4500000,
        total_amount: 13500000
      }
    ],
    special_requests: 'Wine tasting arrangement',
    can_cancel: true
  },
  {
    id: 17,
    reservation_number: 'RSV345789',
    guest_name: 'Jennifer Lee',
    guest_details: {
      id: 17,
      full_name: 'Jennifer Lee',
      email: 'jennifer.lee@email.com',
      phone: '+62-812-1111-0017',
      nationality: 'South Korea'
    },
    check_in_date: '2024-09-10',
    check_out_date: '2024-09-13',
    nights: 3,
    adults: 1,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'OTA',
    total_rooms: 1,
    total_amount: 9000000,
    created_at: '2024-08-30T09:25:00Z',
    rooms: [
      {
        id: 20,
        room_number: '404',
        room_type_name: 'Premium Room',
        rate: 3000000,
        total_amount: 9000000
      }
    ],
    can_cancel: true
  },
  {
    id: 18,
    reservation_number: 'RSV678345',
    guest_name: 'David Brown',
    guest_details: {
      id: 18,
      full_name: 'David Brown',
      email: 'david.brown@email.com',
      phone: '+62-812-1111-0018',
      nationality: 'New Zealand'
    },
    check_in_date: '2024-09-11',
    check_out_date: '2024-09-15',
    nights: 4,
    adults: 2,
    children: 2,
    status: 'PENDING',
    status_display: 'Pending',
    booking_source: 'WEBSITE',
    total_rooms: 2,
    total_amount: 21600000,
    created_at: '2024-08-31T14:10:00Z',
    rooms: [
      {
        id: 21,
        room_number: '306',
        room_type_name: 'Family Suite',
        rate: 3600000,
        total_amount: 14400000
      },
      {
        id: 22,
        room_number: '104',
        room_type_name: 'Standard Room',
        rate: 2250000,
        total_amount: 7200000
      }
    ],
    special_requests: 'Connecting rooms preferred',
    can_cancel: true
  },
  {
    id: 19,
    reservation_number: 'RSV901678',
    guest_name: 'Isabella Garcia',
    guest_details: {
      id: 19,
      full_name: 'Isabella Garcia',
      email: 'isabella.garcia@email.com',
      phone: '+62-812-1111-0019',
      nationality: 'Mexico'
    },
    check_in_date: '2024-09-12',
    check_out_date: '2024-09-14',
    nights: 2,
    adults: 2,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'DIRECT',
    total_rooms: 1,
    total_amount: 4800000,
    created_at: '2024-08-13T08:30:00Z',
    rooms: [
      {
        id: 23,
        room_number: '207',
        room_type_name: 'Deluxe Room',
        rate: 2400000,
        total_amount: 4800000
      }
    ],
    can_cancel: true
  },
  {
    id: 20,
    reservation_number: 'RSV234901',
    guest_name: 'Michael O\'Connor',
    guest_details: {
      id: 20,
      full_name: 'Michael O\'Connor',
      email: 'michael.oconnor@email.com',
      phone: '+62-812-1111-0020',
      nationality: 'Ireland'
    },
    check_in_date: '2024-09-13',
    check_out_date: '2024-09-17',
    nights: 4,
    adults: 1,
    children: 0,
    status: 'CONFIRMED',
    status_display: 'Confirmed',
    booking_source: 'OTA',
    total_rooms: 1,
    total_amount: 12000000,
    created_at: '2024-08-12T19:45:00Z',
    rooms: [
      {
        id: 24,
        room_number: '405',
        room_type_name: 'Premium Room',
        rate: 3000000,
        total_amount: 12000000
      }
    ],
    special_requests: 'Quiet room for business calls',
    can_cancel: true
  }
];

interface Room {
  id: number;
  number: string;
  room_type: string;
  floor: number;
  status: 'AVAILABLE' | 'OCCUPIED' | 'OUT_OF_ORDER' | 'CLEANING' | 'MAINTENANCE' | 'BLOCKED';
  capacity: number;
  amenities: string[];
  current_guest?: string;
  checkout_time?: string;
  checkin_time?: string;
}

const MOCK_ROOMS: Room[] = [
  // Floor 1 - Standard Rooms
  { 
    id: 101, 
    number: '101', 
    room_type: 'Standard', 
    floor: 1, 
    status: 'AVAILABLE', 
    capacity: 2, 
    amenities: ['WiFi', 'TV', 'AC'] 
  },
  { 
    id: 102, 
    number: '102', 
    room_type: 'Standard', 
    floor: 1, 
    status: 'OCCUPIED', 
    capacity: 2, 
    amenities: ['WiFi', 'TV', 'AC'], 
    current_guest: 'John Smith',
    checkout_time: '11:00 AM'
  },
  { 
    id: 103, 
    number: '103', 
    room_type: 'Standard', 
    floor: 1, 
    status: 'CLEANING', 
    capacity: 2, 
    amenities: ['WiFi', 'TV', 'AC'] 
  },
  { 
    id: 104, 
    number: '104', 
    room_type: 'Standard', 
    floor: 1, 
    status: 'AVAILABLE', 
    capacity: 2, 
    amenities: ['WiFi', 'TV', 'AC'] 
  },
  { 
    id: 105, 
    number: '105', 
    room_type: 'Standard', 
    floor: 1, 
    status: 'OCCUPIED', 
    capacity: 2, 
    amenities: ['WiFi', 'TV', 'AC'], 
    current_guest: 'Emma Wilson',
    checkout_time: '12:00 PM'
  },
  
  // Floor 2 - Deluxe Rooms
  { 
    id: 201, 
    number: '201', 
    room_type: 'Deluxe', 
    floor: 2, 
    status: 'OCCUPIED', 
    capacity: 3, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony'], 
    current_guest: 'Maria Rodriguez',
    checkout_time: '10:30 AM'
  },
  { 
    id: 202, 
    number: '202', 
    room_type: 'Deluxe', 
    floor: 2, 
    status: 'AVAILABLE', 
    capacity: 3, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony'] 
  },
  { 
    id: 203, 
    number: '203', 
    room_type: 'Deluxe', 
    floor: 2, 
    status: 'MAINTENANCE', 
    capacity: 3, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony'] 
  },
  { 
    id: 204, 
    number: '204', 
    room_type: 'Deluxe', 
    floor: 2, 
    status: 'AVAILABLE', 
    capacity: 3, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony'] 
  },
  { 
    id: 205, 
    number: '205', 
    room_type: 'Deluxe', 
    floor: 2, 
    status: 'BLOCKED', 
    capacity: 3, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony'] 
  },
  
  // Floor 3 - Suites
  { 
    id: 301, 
    number: '301', 
    room_type: 'Junior Suite', 
    floor: 3, 
    status: 'AVAILABLE', 
    capacity: 4, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony', 'Living Area'] 
  },
  { 
    id: 302, 
    number: '302', 
    room_type: 'Executive Suite', 
    floor: 3, 
    status: 'OUT_OF_ORDER', 
    capacity: 4, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony', 'Living Area', 'Kitchenette'] 
  },
  { 
    id: 303, 
    number: '303', 
    room_type: 'Presidential Suite', 
    floor: 3, 
    status: 'OCCUPIED', 
    capacity: 6, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony', 'Living Area', 'Kitchenette', 'Jacuzzi'], 
    current_guest: 'VIP Guest',
    checkout_time: '2:00 PM'
  },
  { 
    id: 304, 
    number: '304', 
    room_type: 'Junior Suite', 
    floor: 3, 
    status: 'CLEANING', 
    capacity: 4, 
    amenities: ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony', 'Living Area'] 
  },
  
  // Floor 4 - Premium Rooms
  { 
    id: 401, 
    number: '401', 
    room_type: 'Premium', 
    floor: 4, 
    status: 'AVAILABLE', 
    capacity: 2, 
    amenities: ['WiFi', 'TV', 'AC', 'City View'] 
  },
  { 
    id: 402, 
    number: '402', 
    room_type: 'Premium', 
    floor: 4, 
    status: 'AVAILABLE', 
    capacity: 2, 
    amenities: ['WiFi', 'TV', 'AC', 'City View'] 
  },
];

const BookingsPage = () => {
  const router = useRouter();
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<string>('created_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [showAddReservation, setShowAddReservation] = useState(false);
  const [wizardStep, setWizardStep] = useState(1);
  const itemsPerPage = 10;

  const wizardSteps = [
    { id: 1, number: 1, title: 'Guest Information', description: 'Personal details and contact info' },
    { id: 2, number: 2, title: 'Booking Details', description: 'Dates, rooms, and preferences' },
    { id: 3, number: 3, title: 'Payment Information', description: 'Billing and payment details' },
    { id: 4, number: 4, title: 'Review & Confirm', description: 'Final review and confirmation' }
  ];

  const resetWizard = () => {
    setWizardStep(1);
    setShowAddReservation(false);
  };


  const handleNavigateToPayment = (reservation: Reservation) => {
    const params = new URLSearchParams({
      reservationId: reservation.id.toString(),
      guest: reservation.guest_name,
      room: reservation.rooms?.[0]?.room_number || '',
      checkIn: reservation.check_in_date,
      checkOut: reservation.check_out_date,
      amount: reservation.total_amount.toString()
    });
    
    router.push(`/payments?${params.toString()}`);
  };

  useEffect(() => {
    // Simulate API call
    const loadReservations = async () => {
      setLoading(true);
      // In a real app, this would be: const response = await fetch('/api/reservations/');
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
      setReservations(MOCK_RESERVATIONS);
      setRooms(MOCK_ROOMS);
      setLoading(false);
    };

    loadReservations();
  }, []);

  // Generate week dates starting from today
  const getWeekDates = () => {
    const today = new Date();
    const dates = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  const weekDates = getWeekDates();

  const getRoomStatusColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE': return 'bg-green-100 text-green-800';
      case 'OCCUPIED': return 'bg-red-100 text-red-800';
      case 'CLEANING': return 'bg-yellow-100 text-yellow-800';
      case 'MAINTENANCE': return 'bg-orange-100 text-orange-800';
      case 'BLOCKED': return 'bg-purple-100 text-purple-800';
      case 'OUT_OF_ORDER': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoomStatusIcon = (status: string) => {
    const iconProps = { className: "h-4 w-4" };
    switch (status) {
      case 'AVAILABLE': return <CheckCircle {...iconProps} className="h-4 w-4 text-green-600" />;
      case 'OCCUPIED': return <User {...iconProps} className="h-4 w-4 text-red-600" />;
      case 'CLEANING': return <Sparkles {...iconProps} className="h-4 w-4 text-yellow-600" />;
      case 'MAINTENANCE': return <Wrench {...iconProps} className="h-4 w-4 text-orange-600" />;
      case 'BLOCKED': return <Ban {...iconProps} className="h-4 w-4 text-purple-600" />;
      case 'OUT_OF_ORDER': return <AlertTriangle {...iconProps} className="h-4 w-4 text-gray-600" />;
      default: return <CheckCircle {...iconProps} className="h-4 w-4 text-gray-400" />;
    }
  };

  const formatCalendarDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };


  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CONFIRMED': return 'bg-blue-100 text-blue-800';
      case 'CHECKED_IN': return 'bg-green-100 text-green-800';
      case 'CHECKED_OUT': return 'bg-gray-100 text-gray-800';
      case 'CANCELLED': return 'bg-red-100 text-red-800';
      case 'PENDING': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount);
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
    setCurrentPage(1); // Reset to first page when sorting
  };

  const getSortedAndPaginatedReservations = () => {
    // First, sort the reservations
    const sorted = [...reservations].sort((a, b) => {
      let aValue: string | number | Date = a[sortField as keyof Reservation] as string | number | Date;
      let bValue: string | number | Date = b[sortField as keyof Reservation] as string | number | Date;
      
      // Handle nested properties
      if (sortField === 'guest_name') {
        aValue = a.guest_name;
        bValue = b.guest_name;
      } else if (sortField === 'check_in_date') {
        aValue = new Date(a.check_in_date);
        bValue = new Date(b.check_in_date);
      } else if (sortField === 'total_amount') {
        aValue = a.total_amount;
        bValue = b.total_amount;
      } else if (sortField === 'created_at') {
        aValue = new Date(a.created_at);
        bValue = new Date(b.created_at);
      } else if (sortField === 'adults') {
        aValue = a.adults;
        bValue = b.adults;
      } else if (sortField === 'room_number') {
        aValue = a.rooms[0]?.room_number || '';
        bValue = b.rooms[0]?.room_number || '';
      } else if (sortField === 'status') {
        aValue = a.status;
        bValue = b.status;
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    // Then paginate
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return sorted.slice(startIndex, endIndex);
  };

  const getTotalPages = () => Math.ceil(reservations.length / itemsPerPage);

  const getSortIcon = (field: string) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? 
      <ChevronUp className="h-3 w-3 inline ml-1 text-white" /> : 
      <ChevronDown className="h-3 w-3 inline ml-1 text-white" />;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <AppLayout>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Bookings & Reservations</h1>
            <p className="text-sm text-gray-600 mt-1">Manage all hotel reservations and bookings</p>
          </div>
        </div>
      </div>

      {/* Add Reservation Button */}
      <div className="flex justify-end mb-6">
        <button 
          onClick={() => setShowAddReservation(true)}
          className="flex items-center space-x-2 bg-[#005357] text-white px-4 py-4 text-sm font-bold hover:bg-[#004147] transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>Add Reservation</span>
        </button>
      </div>

      {/* Reservations Table */}
      <div className="bg-white shadow">
        {/* Table Header */}
        <div className="p-6">
          <div>
            <h3 className="text-3xl font-bold text-gray-900">All Reservations</h3>
            <p className="text-sm text-gray-600 mt-1">
              {reservations.length} total reservations • Page {currentPage} of {getTotalPages()}
            </p>
          </div>
        </div>
          
          {/* Advanced Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#005357]">
                <tr>
                  <th className="text-left py-4 px-6 text-sm font-bold text-white uppercase tracking-wider">
                    <button 
                      className="flex items-center hover:text-gray-200 transition-colors"
                      onClick={() => handleSort('guest_name')}
                    >
                      Guest & Reservation
                      {getSortIcon('guest_name')}
                    </button>
                  </th>
                  <th className="text-left py-4 px-6 text-sm font-bold text-white uppercase tracking-wider">
                    <button 
                      className="flex items-center hover:text-gray-200 transition-colors"
                      onClick={() => handleSort('check_in_date')}
                    >
                      Dates & Duration
                      {getSortIcon('check_in_date')}
                    </button>
                  </th>
                  <th className="text-left py-4 px-6 text-sm font-bold text-white uppercase tracking-wider">
                    <button 
                      className="flex items-center hover:text-gray-200 transition-colors"
                      onClick={() => handleSort('adults')}
                    >
                      Guests & Rooms
                      {getSortIcon('adults')}
                    </button>
                  </th>
                  <th className="text-left py-4 px-6 text-sm font-bold text-white uppercase tracking-wider">
                    <button 
                      className="flex items-center hover:text-gray-200 transition-colors"
                      onClick={() => handleSort('room_number')}
                    >
                      Room Details
                      {getSortIcon('room_number')}
                    </button>
                  </th>
                  <th className="text-left py-4 px-6 text-sm font-bold text-white uppercase tracking-wider">
                    <button 
                      className="flex items-center hover:text-gray-200 transition-colors"
                      onClick={() => handleSort('total_amount')}
                    >
                      Amount
                      {getSortIcon('total_amount')}
                    </button>
                  </th>
                  <th className="text-left py-4 px-6 text-sm font-bold text-white uppercase tracking-wider">
                    <button 
                      className="flex items-center hover:text-gray-200 transition-colors"
                      onClick={() => handleSort('status')}
                    >
                      Status
                      {getSortIcon('status')}
                    </button>
                  </th>
                  <th className="text-right py-4 px-6 text-sm font-bold text-white uppercase tracking-wider">
                    <div className="flex items-center justify-end">
                      <span>Actions</span>
                      <ChevronDown className="h-3 w-3 ml-1 text-white opacity-70" />
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {reservations.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">No reservations found</p>
                    </td>
                  </tr>
                ) : (
                  getSortedAndPaginatedReservations().map((reservation) => (
                    <tr key={reservation.id} className="hover:bg-gray-50 transition-colors">
                      {/* Guest & Reservation */}
                      <td className="px-6 py-4">
                        <div>
                          <Link
                            href={`/bookings/${reservation.id}`}
                            className="font-semibold text-gray-900 hover:text-[#005357] hover:underline transition-colors cursor-pointer"
                          >
                            {reservation.guest_name}
                          </Link>
                          <p className="text-sm text-gray-600">{reservation.reservation_number}</p>
                          <p className="text-xs text-gray-500">
                            {formatDate(reservation.created_at)} • {reservation.booking_source}
                          </p>
                        </div>
                      </td>

                      {/* Dates & Duration */}
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">{formatDate(reservation.check_in_date)}</p>
                          <p className="text-sm text-gray-500">to {formatDate(reservation.check_out_date)}</p>
                          <p className="text-sm font-medium text-[#005357]">{reservation.nights} nights</p>
                        </div>
                      </td>

                      {/* Guests & Rooms */}
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">
                            {reservation.adults} adults
                            {reservation.children > 0 && `, ${reservation.children} children`}
                          </p>
                          <p className="text-sm text-gray-500">{reservation.total_rooms} room(s)</p>
                        </div>
                      </td>

                      {/* Room Details */}
                      <td className="px-6 py-4">
                        <div>
                          {reservation.rooms && reservation.rooms.length > 0 ? (
                            <div className="space-y-1">
                              {reservation.rooms.map((room, index) => (
                                <div key={index}>
                                  <p className="font-medium text-gray-900">Room {room.room_number}</p>
                                  <p className="text-sm text-gray-500">{room.room_type_name}</p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-500">No rooms assigned</p>
                          )}
                        </div>
                      </td>

                      {/* Amount */}
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-bold text-base text-gray-900">
                            {formatCurrency(reservation.total_amount)}
                          </p>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium ${getStatusColor(reservation.status)}`}>
                          {reservation.status_display}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="px-6 py-4">
                        <div className="relative flex justify-end">
                          <button
                            onClick={() => setOpenMenuId(openMenuId === reservation.id ? null : reservation.id)}
                            className="flex items-center justify-center p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors rounded"
                            title="More actions"
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </button>
                          
                          {openMenuId === reservation.id && (
                            <>
                              {/* Backdrop */}
                              <div 
                                className="fixed inset-0 z-10" 
                                onClick={() => setOpenMenuId(null)}
                              ></div>
                              
                              {/* Dropdown Menu */}
                              <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded shadow-lg z-20">
                                <div className="py-1">
                                  <Link
                                    href={`/bookings/${reservation.id}`}
                                    className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                                    onClick={() => setOpenMenuId(null)}
                                  >
                                    <Eye className="h-4 w-4" />
                                    <span>View Details</span>
                                  </Link>
                                  <button
                                    onClick={() => setOpenMenuId(null)}
                                    className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors w-full text-left"
                                  >
                                    <Edit className="h-4 w-4" />
                                    <span>Edit Reservation</span>
                                  </button>
                                  <div className="border-t border-gray-100 my-1"></div>
                                  
                                  {/* Status-based Actions */}
                                  {(reservation.status === 'confirmed' || reservation.status === 'CONFIRMED') && (
                                    <>
                                      <button
                                        onClick={() => {
                                          alert('Guest checked in successfully!');
                                          setOpenMenuId(null);
                                        }}
                                        className="flex items-center space-x-2 px-4 py-2 text-sm text-green-600 hover:bg-green-50 transition-colors w-full text-left"
                                      >
                                        <CheckCircle className="h-4 w-4" />
                                        <span>Check In</span>
                                      </button>
                                      <button
                                        onClick={() => {
                                          handleNavigateToPayment(reservation);
                                          setOpenMenuId(null);
                                        }}
                                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors w-full text-left"
                                      >
                                        <CreditCard className="h-4 w-4" />
                                        <span>Process Payment</span>
                                      </button>
                                    </>
                                  )}
                                  
                                  {(reservation.status === 'checked_in' || reservation.status === 'CHECKED_IN') && (
                                    <>
                                      <button
                                        onClick={() => {
                                          alert('Guest checked out successfully!');
                                          setOpenMenuId(null);
                                        }}
                                        className="flex items-center space-x-2 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 transition-colors w-full text-left"
                                      >
                                        <LogOut className="h-4 w-4" />
                                        <span>Check Out</span>
                                      </button>
                                      <button
                                        onClick={() => setOpenMenuId(null)}
                                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors w-full text-left"
                                      >
                                        <CreditCard className="h-4 w-4" />
                                        <span>Process Additional Charges</span>
                                      </button>
                                    </>
                                  )}
                                  
                                  {(reservation.status === 'pending' || reservation.status === 'PENDING' || reservation.status === 'partial_paid' || reservation.status === 'PARTIAL_PAID') && (
                                    <>
                                      <button
                                        onClick={() => {
                                          handleNavigateToPayment(reservation);
                                          setOpenMenuId(null);
                                        }}
                                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors w-full text-left"
                                      >
                                        <CreditCard className="h-4 w-4" />
                                        <span>Process Payment</span>
                                      </button>
                                      <button
                                        onClick={() => {
                                          alert('Reservation confirmed!');
                                          setOpenMenuId(null);
                                        }}
                                        className="flex items-center space-x-2 px-4 py-2 text-sm text-green-600 hover:bg-green-50 transition-colors w-full text-left"
                                      >
                                        <CheckCircle className="h-4 w-4" />
                                        <span>Confirm Reservation</span>
                                      </button>
                                    </>
                                  )}
                                  
                                  {(reservation.status === 'checked_out' || reservation.status === 'CHECKED_OUT') && (
                                    <div className="px-4 py-2 text-sm text-gray-500 italic">
                                      Guest has checked out
                                    </div>
                                  )}
                                  
                                  {(reservation.status === 'cancelled' || reservation.status === 'CANCELLED') && (
                                    <div className="px-4 py-2 text-sm text-red-500 italic">
                                      Reservation cancelled
                                    </div>
                                  )}
                                  {reservation.can_cancel && (
                                    <>
                                      <div className="border-t border-gray-100 my-1"></div>
                                      <button
                                        onClick={() => setOpenMenuId(null)}
                                        className="flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors w-full text-left"
                                      >
                                        <X className="h-4 w-4" />
                                        <span>Cancel Reservation</span>
                                      </button>
                                    </>
                                  )}
                                </div>
                              </div>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {reservations.length > 0 && (
            <div className="px-6 py-4 flex items-center justify-between bg-white">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(getTotalPages(), currentPage + 1))}
                  disabled={currentPage === getTotalPages()}
                  className="ml-3 relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
              
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing{' '}
                    <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span>
                    {' '}to{' '}
                    <span className="font-medium">
                      {Math.min(currentPage * itemsPerPage, reservations.length)}
                    </span>
                    {' '}of{' '}
                    <span className="font-medium">{reservations.length}</span>
                    {' '}results
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 text-sm font-medium text-gray-500 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </button>
                    
                    {Array.from({ length: getTotalPages() }, (_, i) => i + 1).map((page) => (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`relative inline-flex items-center px-4 py-2 text-sm font-medium transition-colors ${
                          page === currentPage
                            ? 'z-10 bg-[#005357] text-white'
                            : 'bg-white text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    ))}
                    
                    <button
                      onClick={() => setCurrentPage(Math.min(getTotalPages(), currentPage + 1))}
                      disabled={currentPage === getTotalPages()}
                      className="relative inline-flex items-center px-2 py-2 text-sm font-medium text-gray-500 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>

      {/* Add Reservation Modal */}
      <Dialog.Root open={showAddReservation} onOpenChange={setShowAddReservation}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
          <Dialog.Content className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white shadow-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto z-50">
            {/* Header */}
            <div className="p-6 bg-[#005357]">
              <div className="flex items-center justify-between">
                <div>
                  <Dialog.Title className="text-xl font-bold text-white">
                    New Reservation
                  </Dialog.Title>
                  <p className="text-sm text-gray-200 mt-1">Create a new booking for a guest</p>
                </div>
                <Dialog.Close asChild>
                  <button className="p-2 text-white hover:text-gray-200">
                    <X className="h-5 w-5" />
                  </button>
                </Dialog.Close>
              </div>
            </div>

            {/* Step Navigation */}
            <div className="px-6 py-4 bg-white border-b border-gray-200">
              <nav className="flex justify-center">
                <ol className="flex items-center space-x-8">
                  {wizardSteps.map((step) => (
                    <li key={step.id} className="flex items-center">
                      <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                        wizardStep >= step.id 
                          ? 'bg-[#005357] text-white' 
                          : 'bg-gray-200 text-gray-600'
                      }`}>
                        {step.id}
                      </div>
                      <span className={`ml-2 text-sm font-medium ${
                        wizardStep >= step.id ? 'text-[#005357]' : 'text-gray-500'
                      }`}>
                        {step.title}
                      </span>
                      {step.number < wizardSteps.length && (
                        <div className={`w-8 h-0.5 ml-8 ${
                          wizardStep > step.id ? 'bg-[#005357]' : 'bg-gray-200'
                        }`} />
                      )}
                    </li>
                  ))}
                </ol>
              </nav>
            </div>

            {/* Form Content */}
            <div className="p-6 bg-gray-50">
              <form className="space-y-6">
                {/* Step 1: Guest Information */}
                {wizardStep === 1 && (
                  <div className="bg-white p-6 rounded shadow">
                    <h3 className="font-bold text-gray-900 mb-4">Guest Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                        <input
                          type="text"
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                          placeholder="Enter guest full name"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                        <input
                          type="email"
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                          placeholder="guest@email.com"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
                        <input
                          type="tel"
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                          placeholder="+1 (555) 123-4567"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                        <textarea
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                          rows={3}
                          placeholder="Enter guest address"
                        ></textarea>
                      </div>
                    </div>
                  </div>
                )}

                {/* Step 2: Booking Details */}
                {wizardStep === 2 && (
                  <div className="bg-white p-6 rounded shadow">
                    <h3 className="font-bold text-gray-900 mb-4">Booking Details</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Check-in Date *</label>
                        <input
                          type="date"
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Check-out Date *</label>
                        <input
                          type="date"
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Number of Guests *</label>
                        <select
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                        >
                          <option value="">Select guests</option>
                          <option value="1">1 Guest</option>
                          <option value="2">2 Guests</option>
                          <option value="3">3 Guests</option>
                          <option value="4">4+ Guests</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Room Type *</label>
                        <select
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                        >
                          <option value="">Select room type</option>
                          <option value="standard">Standard Room</option>
                          <option value="deluxe">Deluxe Room</option>
                          <option value="suite">Suite</option>
                          <option value="presidential">Presidential Suite</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Step 3: Room Selection */}
                {wizardStep === 3 && (
                  <div className="bg-white p-6 rounded shadow">
                    <h3 className="font-bold text-gray-900 mb-4">Select Room</h3>
                    <div className="space-y-4">
                      {[
                        { number: '101', type: 'Standard', price: 120, available: true },
                        { number: '102', type: 'Standard', price: 120, available: false },
                        { number: '201', type: 'Deluxe', price: 180, available: true },
                        { number: '301', type: 'Suite', price: 350, available: true },
                      ].map((room) => (
                        <div
                          key={room.number}
                          className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                            room.available
                              ? 'border-gray-200 hover:border-[#005357] hover:bg-gray-50'
                              : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium text-gray-900">Room {room.number}</h4>
                              <p className="text-sm text-gray-500">{room.type}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-gray-900">${room.price}/night</p>
                              <p className={`text-xs ${room.available ? 'text-green-600' : 'text-red-600'}`}>
                                {room.available ? 'Available' : 'Occupied'}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Step 4: Payment */}
                {wizardStep === 4 && (
                  <div className="bg-white p-6 rounded shadow">
                    <h3 className="font-bold text-gray-900 mb-4">Payment Information</h3>
                    <div className="grid grid-cols-1 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method *</label>
                        <select
                          required
                          className="w-full px-3 py-2 bg-gray-50 rounded focus:ring-2 focus:ring-[#005357] focus:outline-none"
                        >
                          <option value="">Select payment method</option>
                          <option value="cash">Cash</option>
                          <option value="card">Credit/Debit Card</option>
                          <option value="bank">Bank Transfer</option>
                        </select>
                      </div>
                      
                      {/* Booking Summary */}
                      <div className="mt-6 p-4 bg-gray-50 rounded">
                        <h4 className="font-medium text-gray-900 mb-3">Booking Summary</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Room 101 (2 nights)</span>
                            <span>$240.00</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Service charge</span>
                            <span>$24.00</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Tax (10%)</span>
                            <span>$26.40</span>
                          </div>
                          <div className="border-t pt-2 flex justify-between font-bold">
                            <span>Total</span>
                            <span>$290.40</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Navigation buttons */}
                <div className="flex justify-between pt-6">
                  <button
                    type="button"
                    onClick={() => setWizardStep(Math.max(1, wizardStep - 1))}
                    disabled={wizardStep === 1}
                    className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
                      wizardStep === 1
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Previous
                  </button>
                  
                  {wizardStep < 4 ? (
                    <button
                      type="button"
                      onClick={() => setWizardStep(Math.min(4, wizardStep + 1))}
                      className="px-4 py-2 bg-[#005357] text-white text-sm font-medium rounded hover:bg-[#004449] transition-colors"
                    >
                      Next
                    </button>
                  ) : (
                    <button
                      type="submit"
                      className="px-4 py-2 bg-[#005357] text-white text-sm font-medium rounded hover:bg-[#004449] transition-colors"
                    >
                      Complete Reservation
                    </button>
                  )}
                </div>
              </form>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      {/* Payment processing now redirects to POS page */}
    </AppLayout>
  );
};

export default BookingsPage;