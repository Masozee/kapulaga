'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AppLayout, { HeaderActions } from '@/components/AppLayout';
import { 
  Search,
  Users,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Star,
  Award,
  CreditCard,
  User,
  Grid3X3,
  List,
  Filter,
  Plus,
  Settings,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  Badge,
  TrendingUp,
  Gift,
  Clock,
  CheckCircle,
  X,
  Heart,
  Crown,
  Diamond,
  Sparkles
} from 'lucide-react';

interface GuestRewards {
  program_name: string;
  member_number: string;
  tier_level: 'Bronze' | 'Silver' | 'Gold' | 'Platinum' | 'Diamond';
  points_balance: number;
  points_lifetime: number;
  tier_benefits: string[];
  next_tier_required: number;
  points_expiring: number;
  expiry_date: string;
  join_date: string;
}

interface GuestStay {
  id: number;
  reservation_number: string;
  check_in_date: string;
  check_out_date: string;
  nights: number;
  room_type: string;
  room_number: string;
  total_amount: number;
  points_earned: number;
  rating?: number;
  review?: string;
  status: 'completed' | 'cancelled' | 'no_show';
}

interface Guest {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  nationality: string;
  address: string;
  date_of_birth: string;
  gender: string;
  id_number: string;
  id_type: string;
  vip_status: boolean;
  preferences: string[];
  allergies: string[];
  emergency_contact_name: string;
  emergency_contact_phone: string;
  created_at: string;
  last_stay: string;
  total_stays: number;
  total_nights: number;
  total_spent: number;
  avg_rating: number;
  rewards?: GuestRewards;
  recent_stays: GuestStay[];
  notes: string;
  blacklisted: boolean;
  favorite_room_type?: string;
  preferred_floor?: number;
  marketing_consent: boolean;
}

const MOCK_GUESTS: Guest[] = [
  {
    id: 1,
    full_name: 'John Smith',
    email: 'john.smith@email.com',
    phone: '+1-555-0123',
    nationality: 'United States',
    address: '123 Main Street, New York, NY 10001',
    date_of_birth: '1985-06-15',
    gender: 'Male',
    id_number: 'P123456789',
    id_type: 'Passport',
    vip_status: false,
    preferences: ['Non-smoking', 'High floor', 'City view', 'King bed'],
    allergies: ['Nuts', 'Shellfish'],
    emergency_contact_name: 'Robert Smith',
    emergency_contact_phone: '+1-555-0199',
    created_at: '2023-01-15T10:30:00Z',
    last_stay: '2024-08-28T11:00:00Z',
    total_stays: 8,
    total_nights: 24,
    total_spent: 18500000,
    avg_rating: 4.8,
    rewards: {
      program_name: 'Kapulaga Rewards',
      member_number: 'KR123456789',
      tier_level: 'Gold',
      points_balance: 12450,
      points_lifetime: 28750,
      tier_benefits: ['Free WiFi', 'Late Checkout', 'Room Upgrade', 'Welcome Drink', 'Priority Booking'],
      next_tier_required: 6550,
      points_expiring: 2500,
      expiry_date: '2024-12-31',
      join_date: '2023-01-15'
    },
    recent_stays: [
      {
        id: 1,
        reservation_number: 'RSV123456',
        check_in_date: '2024-08-25',
        check_out_date: '2024-08-28',
        nights: 3,
        room_type: 'Deluxe King Suite',
        room_number: '1205',
        total_amount: 10125000,
        points_earned: 585,
        rating: 5,
        review: 'Excellent service, beautiful room with great city views.',
        status: 'completed'
      },
      {
        id: 2,
        reservation_number: 'RSV098765',
        check_in_date: '2024-06-12',
        check_out_date: '2024-06-15',
        nights: 3,
        room_type: 'Standard King',
        room_number: '803',
        total_amount: 6750000,
        points_earned: 390,
        rating: 4,
        status: 'completed'
      }
    ],
    notes: 'Prefers rooms with city view. Allergic to nuts and shellfish - inform restaurant staff.',
    blacklisted: false,
    favorite_room_type: 'Deluxe King Suite',
    preferred_floor: 12,
    marketing_consent: true
  },
  {
    id: 2,
    full_name: 'Sarah Johnson',
    email: 'sarah.johnson@email.com',
    phone: '+1-555-0456',
    nationality: 'Canada',
    address: '456 Queen Street, Toronto, ON M5V 3A8',
    date_of_birth: '1990-03-22',
    gender: 'Female',
    id_number: 'C987654321',
    id_type: 'Passport',
    vip_status: true,
    preferences: ['Non-smoking', 'Quiet floor', 'Ocean view', 'Extra pillows'],
    allergies: [],
    emergency_contact_name: 'Michael Johnson',
    emergency_contact_phone: '+1-555-0789',
    created_at: '2022-08-20T14:15:00Z',
    last_stay: '2024-07-18T11:00:00Z',
    total_stays: 15,
    total_nights: 45,
    total_spent: 35250000,
    avg_rating: 4.9,
    rewards: {
      program_name: 'Kapulaga Rewards',
      member_number: 'KR987654321',
      tier_level: 'Platinum',
      points_balance: 28950,
      points_lifetime: 67800,
      tier_benefits: ['Free WiFi', 'Late Checkout', 'Room Upgrade', 'Welcome Drink', 'Priority Booking', 'Lounge Access', 'Free Breakfast'],
      next_tier_required: 2200,
      points_expiring: 1800,
      expiry_date: '2025-03-31',
      join_date: '2022-08-20'
    },
    recent_stays: [
      {
        id: 3,
        reservation_number: 'RSV567890',
        check_in_date: '2024-07-15',
        check_out_date: '2024-07-18',
        nights: 3,
        room_type: 'Presidential Suite',
        room_number: '2001',
        total_amount: 20250000,
        points_earned: 1170,
        rating: 5,
        review: 'Outstanding experience! The presidential suite was perfect.',
        status: 'completed'
      }
    ],
    notes: 'VIP guest. Prefers quiet floors and ocean views. Very loyal customer.',
    blacklisted: false,
    favorite_room_type: 'Presidential Suite',
    preferred_floor: 20,
    marketing_consent: true
  },
  {
    id: 3,
    full_name: 'Ahmad Rahman',
    email: 'ahmad.rahman@email.com',
    phone: '+62-812-3456-7890',
    nationality: 'Indonesia',
    address: 'Jl. Sudirman No. 123, Jakarta 10220',
    date_of_birth: '1978-11-10',
    gender: 'Male',
    id_number: '3171051011780001',
    id_type: 'KTP',
    vip_status: false,
    preferences: ['Non-smoking', 'Halal food', 'Prayer mat', 'Qibla direction'],
    allergies: ['Pork', 'Alcohol'],
    emergency_contact_name: 'Siti Rahman',
    emergency_contact_phone: '+62-812-9876-5432',
    created_at: '2023-05-10T09:00:00Z',
    last_stay: '2024-05-20T11:00:00Z',
    total_stays: 6,
    total_nights: 18,
    total_spent: 13500000,
    avg_rating: 4.5,
    rewards: {
      program_name: 'Kapulaga Rewards',
      member_number: 'KR456789123',
      tier_level: 'Silver',
      points_balance: 8750,
      points_lifetime: 15450,
      tier_benefits: ['Free WiFi', 'Late Checkout', 'Room Upgrade', 'Welcome Drink'],
      next_tier_required: 4550,
      points_expiring: 0,
      expiry_date: '2025-05-31',
      join_date: '2023-05-10'
    },
    recent_stays: [
      {
        id: 4,
        reservation_number: 'RSV234567',
        check_in_date: '2024-05-17',
        check_out_date: '2024-05-20',
        nights: 3,
        room_type: 'Executive Twin',
        room_number: '1012',
        total_amount: 7875000,
        points_earned: 455,
        rating: 4,
        status: 'completed'
      }
    ],
    notes: 'Muslim guest. Requires halal food options and prayer facilities. Very respectful guest.',
    blacklisted: false,
    favorite_room_type: 'Executive Twin',
    marketing_consent: true
  }
];

const GuestsPage = () => {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'card' | 'table'>('table');
  const [filterTier, setFilterTier] = useState<string>('all');
  const [filterVIP, setFilterVIP] = useState<boolean | null>(null);
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<number | null>(null);
  
  // Advanced filter states
  const [filterCountry, setFilterCountry] = useState('');
  const [minSpent, setMinSpent] = useState('');
  const [maxSpent, setMaxSpent] = useState('');
  const [minStays, setMinStays] = useState('');
  const [lastStayFrom, setLastStayFrom] = useState('');
  const [lastStayTo, setLastStayTo] = useState('');
  const [hasAllergies, setHasAllergies] = useState<boolean | null>(null);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'Bronze': return 'bg-orange-100 text-orange-800';
      case 'Silver': return 'bg-gray-100 text-gray-800';
      case 'Gold': return 'bg-yellow-100 text-yellow-800';
      case 'Platinum': return 'bg-purple-100 text-purple-800';
      case 'Diamond': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'Bronze': return <Award className="h-3 w-3" />;
      case 'Silver': return <Badge className="h-3 w-3" />;
      case 'Gold': return <Crown className="h-3 w-3" />;
      case 'Platinum': return <Star className="h-3 w-3" />;
      case 'Diamond': return <Diamond className="h-3 w-3" />;
      default: return <Award className="h-3 w-3" />;
    }
  };

  // Enhanced filtering logic
  const resetFilters = () => {
    setFilterTier('all');
    setFilterVIP(null);
    setFilterCountry('');
    setMinSpent('');
    setMaxSpent('');
    setMinStays('');
    setLastStayFrom('');
    setLastStayTo('');
    setHasAllergies(null);
    setSearchTerm('');
  };

  const filteredGuests = MOCK_GUESTS.filter(guest => {
    if (searchTerm && !guest.full_name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !guest.email.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !guest.phone.includes(searchTerm)) {
      return false;
    }
    if (filterTier !== 'all' && guest.rewards?.tier_level !== filterTier) {
      return false;
    }
    if (filterVIP !== null && guest.vip_status !== filterVIP) {
      return false;
    }
    if (filterCountry && !guest.nationality.toLowerCase().includes(filterCountry.toLowerCase())) {
      return false;
    }
    if (minSpent && guest.total_spent < parseInt(minSpent)) {
      return false;
    }
    if (maxSpent && guest.total_spent > parseInt(maxSpent)) {
      return false;
    }
    if (minStays && guest.total_stays < parseInt(minStays)) {
      return false;
    }
    if (lastStayFrom && new Date(guest.last_stay) < new Date(lastStayFrom)) {
      return false;
    }
    if (lastStayTo && new Date(guest.last_stay) > new Date(lastStayTo)) {
      return false;
    }
    if (hasAllergies !== null && (guest.allergies.length > 0) !== hasAllergies) {
      return false;
    }
    return true;
  });

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (activeDropdown !== null) {
        setActiveDropdown(null);
      }
    };

    if (activeDropdown !== null) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [activeDropdown]);

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Guest Database</h1>
            <p className="text-gray-600 mt-2">Manage guest profiles, loyalty rewards, and stay history</p>
          </div>
          <HeaderActions />
        </div>

        {/* Filter Button & View Switcher */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowAdvancedFilter(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-[#005357] text-white text-sm font-medium hover:bg-[#004147] transition-colors"
            >
              <Settings className="h-4 w-4" />
              <span>Advanced Filter</span>
            </button>
            
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 transition-colors">
              <Plus className="h-4 w-4" />
              <span>New Guest</span>
            </button>
          </div>
          
          {/* View Mode Switcher */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">View:</span>
            <div className="flex border border-gray-300 overflow-hidden">
              <button
                onClick={() => setViewMode('card')}
                className={`flex items-center space-x-2 px-4 py-2 text-sm transition-colors ${
                  viewMode === 'card' 
                    ? 'bg-[#005357] text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Grid3X3 className="h-4 w-4" />
                <span>Cards</span>
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`flex items-center space-x-2 px-4 py-2 text-sm transition-colors ${
                  viewMode === 'table' 
                    ? 'bg-[#005357] text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <List className="h-4 w-4" />
                <span>Table</span>
              </button>
            </div>
          </div>
        </div>

        {/* Advanced Filter Modal */}
        {showAdvancedFilter && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              {/* Modal Header */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Advanced Filter</h2>
                    <p className="text-sm text-gray-600 mt-1">Find guests with specific criteria</p>
                  </div>
                  <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                    <Filter className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>

              {/* Modal Content */}
              <div className="p-6 bg-gray-50">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Basic Filters */}
                  <div className="bg-white p-4 border border-gray-200">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Basic Information</h3>
                    <div className="grid grid-cols-1 gap-4">
                      {/* Search */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Search Guests</label>
                        <div className="relative">
                          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                          <input
                            type="text"
                            placeholder="Name, email, or phone..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                          />
                        </div>
                      </div>

                      {/* Country Filter */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Country/Nationality</label>
                        <input
                          type="text"
                          placeholder="Filter by country..."
                          value={filterCountry}
                          onChange={(e) => setFilterCountry(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        />
                      </div>

                      {/* VIP Status */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">VIP Status</label>
                        <select
                          value={filterVIP === null ? 'all' : filterVIP.toString()}
                          onChange={(e) => setFilterVIP(e.target.value === 'all' ? null : e.target.value === 'true')}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm appearance-none"
                        >
                          <option value="all">All Guests</option>
                          <option value="true">VIP Only</option>
                          <option value="false">Regular Only</option>
                        </select>
                      </div>

                      {/* Tier Filter */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Loyalty Tier</label>
                        <select
                          value={filterTier}
                          onChange={(e) => setFilterTier(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm appearance-none"
                        >
                          <option value="all">All Tiers</option>
                          <option value="Bronze">Bronze</option>
                          <option value="Silver">Silver</option>
                          <option value="Gold">Gold</option>
                          <option value="Platinum">Platinum</option>
                          <option value="Diamond">Diamond</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Advanced Filters */}
                  <div className="bg-white p-4 border border-gray-200">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Advanced Criteria</h3>
                    <div className="grid grid-cols-1 gap-4">
                      {/* Spending Range */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Total Spending Range (IDR)</label>
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="number"
                            placeholder="Min spending"
                            value={minSpent}
                            onChange={(e) => setMinSpent(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                          />
                          <input
                            type="number"
                            placeholder="Max spending"
                            value={maxSpent}
                            onChange={(e) => setMaxSpent(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                          />
                        </div>
                      </div>

                      {/* Minimum Stays */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Minimum Number of Stays</label>
                        <input
                          type="number"
                          placeholder="Min stays"
                          value={minStays}
                          onChange={(e) => setMinStays(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        />
                      </div>

                      {/* Last Stay Range */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Last Stay Date Range</label>
                        <div className="grid grid-cols-2 gap-2">
                          <input
                            type="date"
                            value={lastStayFrom}
                            onChange={(e) => setLastStayFrom(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                          />
                          <input
                            type="date"
                            value={lastStayTo}
                            onChange={(e) => setLastStayTo(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                          />
                        </div>
                      </div>

                      {/* Has Allergies */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Allergy Information</label>
                        <select
                          value={hasAllergies === null ? 'all' : hasAllergies.toString()}
                          onChange={(e) => setHasAllergies(e.target.value === 'all' ? null : e.target.value === 'true')}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm appearance-none"
                        >
                          <option value="all">All Guests</option>
                          <option value="true">Has Allergies</option>
                          <option value="false">No Allergies</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Filter Actions */}
                <div className="flex justify-between items-center mt-6 pt-6 border-t border-gray-200">
                  <button 
                    onClick={resetFilters}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    Reset All Filters
                  </button>
                  <div className="flex space-x-3">
                    <button 
                      onClick={() => setShowAdvancedFilter(false)}
                      className="px-6 py-2 bg-gray-100 text-gray-700 text-sm font-medium hover:bg-gray-200 transition-colors"
                    >
                      Cancel
                    </button>
                    <button 
                      onClick={() => setShowAdvancedFilter(false)}
                      className="px-6 py-2 bg-[#005357] text-white text-sm font-medium hover:bg-[#004147] transition-colors"
                    >
                      Apply Filters ({filteredGuests.length} guests)
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Guests Display */}
        {viewMode === 'card' ? (
          /* Card View */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGuests.map((guest) => (
              <div key={guest.id} className="bg-white shadow">
                {/* Guest Card Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <button 
                          onClick={() => router.push(`/guests/${guest.id}`)}
                          className="text-xl font-bold text-gray-900 hover:text-[#005357] transition-colors text-left"
                        >
                          {guest.full_name}
                        </button>
                        {guest.vip_status && (
                          <span className="inline-flex items-center space-x-1 bg-yellow-100 text-yellow-800 px-2 py-1 text-xs font-medium rounded">
                            <Star className="h-3 w-3 fill-current" />
                            <span>VIP</span>
                          </span>
                        )}
                      </div>
                      <div className="space-y-1 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Mail className="h-3 w-3" />
                          <span className="truncate">{guest.email}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Phone className="h-3 w-3" />
                          <span>{guest.phone}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <MapPin className="h-3 w-3" />
                          <span>{guest.nationality}</span>
                        </div>
                      </div>
                    </div>
                    <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                      <User className="h-4 w-4 text-white" />
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-gray-50">
                  {/* Rewards Info */}
                  {guest.rewards && (
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center space-x-1 px-2 py-1 text-xs font-bold rounded ${getTierColor(guest.rewards.tier_level)}`}>
                            {getTierIcon(guest.rewards.tier_level)}
                            <span>{guest.rewards.tier_level}</span>
                          </span>
                          <span className="text-xs text-gray-600">{guest.rewards.program_name}</span>
                        </div>
                        <button 
                          onClick={() => router.push(`/guests/${guest.id}`)}
                          className="text-xs bg-[#005357] text-white px-2 py-1 rounded hover:bg-[#004147]"
                        >
                          View Points
                        </button>
                      </div>
                      <div className="text-xs text-gray-600">
                        <p>{guest.rewards.points_balance.toLocaleString()} points available</p>
                      </div>
                    </div>
                  )}

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-[#005357]">{guest.total_stays}</div>
                      <div className="text-xs text-gray-600">Stays</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-[#005357]">{guest.total_nights}</div>
                      <div className="text-xs text-gray-600">Nights</div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-600">Total Spent</span>
                      <span className="font-medium text-gray-900">{formatCurrency(guest.total_spent)}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-600">Last Stay</span>
                      <span className="font-medium text-gray-900">{formatDate(guest.last_stay)}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-600">Avg Rating</span>
                      <div className="flex items-center space-x-1">
                        <Star className="h-3 w-3 text-yellow-400 fill-current" />
                        <span className="font-medium text-gray-900">{guest.avg_rating}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="grid grid-cols-2 gap-2">
                    <button 
                      onClick={() => router.push(`/guests/${guest.id}`)}
                      className="text-xs bg-gray-100 text-gray-700 px-3 py-2 hover:bg-gray-200 transition-colors"
                    >
                      <Eye className="h-3 w-3 inline mr-1" />
                      View Profile
                    </button>
                    <button className="text-xs bg-[#005357] text-white px-3 py-2 hover:bg-[#004147] transition-colors">
                      <Edit className="h-3 w-3 inline mr-1" />
                      Edit
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Table View */
          <div className="bg-white shadow">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Guest Database</h3>
                  <p className="text-sm text-gray-600 mt-1">Complete guest profiles and loyalty information</p>
                </div>
                <div className="flex items-center space-x-4">
                  {/* Search Form */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search guests..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-64 pl-10 pr-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                    />
                  </div>
                  <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                    <Users className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[#005357]">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-bold text-white">
                      Guest
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-white">
                      Contact
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-white">
                      Rewards
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-white">
                      Stay History
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-white">
                      Spending
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-white">
                      Last Stay
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-white">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredGuests.map((guest) => (
                    <tr key={guest.id} className="hover:bg-gray-50">
                      {/* Guest Info */}
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                            <User className="h-5 w-5 text-gray-600" />
                          </div>
                          <div>
                            <div className="flex items-center space-x-2">
                              <button 
                                onClick={() => router.push(`/guests/${guest.id}`)}
                                className="font-bold text-gray-900 hover:text-[#005357] transition-colors text-left"
                              >
                                {guest.full_name}
                              </button>
                              {guest.vip_status && (
                                <Star className="h-3 w-3 text-yellow-400 fill-current" />
                              )}
                            </div>
                            <p className="text-xs text-gray-600">{guest.nationality}</p>
                          </div>
                        </div>
                      </td>

                      {/* Contact */}
                      <td className="px-6 py-4">
                        <div className="text-sm space-y-1">
                          <div className="text-gray-900">{guest.email}</div>
                          <div className="text-gray-600 text-xs">{guest.phone}</div>
                        </div>
                      </td>

                      {/* Rewards */}
                      <td className="px-6 py-4">
                        {guest.rewards ? (
                          <div className="space-y-1">
                            <div className="flex items-center space-x-2">
                              <span className={`inline-flex items-center space-x-1 px-2 py-1 text-xs font-bold rounded ${getTierColor(guest.rewards.tier_level)}`}>
                                {getTierIcon(guest.rewards.tier_level)}
                                <span>{guest.rewards.tier_level}</span>
                              </span>
                            </div>
                            <div className="text-xs text-gray-600">
                              {guest.rewards.points_balance.toLocaleString()} pts
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-500">No rewards</span>
                        )}
                      </td>

                      {/* Stay History */}
                      <td className="px-6 py-4">
                        <div className="text-sm space-y-1">
                          <div className="flex items-center space-x-4">
                            <div className="text-center">
                              <div className="font-bold text-[#005357]">{guest.total_stays}</div>
                              <div className="text-xs text-gray-600">stays</div>
                            </div>
                            <div className="text-center">
                              <div className="font-bold text-[#005357]">{guest.total_nights}</div>
                              <div className="text-xs text-gray-600">nights</div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Star className="h-3 w-3 text-yellow-400 fill-current" />
                            <span className="text-xs text-gray-600">{guest.avg_rating} avg rating</span>
                          </div>
                        </div>
                      </td>

                      {/* Spending */}
                      <td className="px-6 py-4">
                        <div className="text-right">
                          <div className="text-sm font-bold text-[#005357]">
                            {formatCurrency(guest.total_spent)}
                          </div>
                          <div className="text-xs text-gray-600">total spent</div>
                        </div>
                      </td>

                      {/* Last Stay */}
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {formatDate(guest.last_stay)}
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="px-6 py-4">
                        <div className="relative">
                          <button 
                            onClick={() => setActiveDropdown(activeDropdown === guest.id ? null : guest.id)}
                            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </button>
                          
                          {/* Dropdown Menu */}
                          {activeDropdown === guest.id && (
                            <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 shadow-lg z-50">
                              <div className="py-1">
                                <button
                                  onClick={() => {
                                    router.push(`/guests/${guest.id}`);
                                    setActiveDropdown(null);
                                  }}
                                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                                >
                                  <Eye className="h-4 w-4" />
                                  <span>View Profile</span>
                                </button>
                                <button
                                  onClick={() => setActiveDropdown(null)}
                                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                                >
                                  <Edit className="h-4 w-4" />
                                  <span>Edit Guest</span>
                                </button>
                                <div className="border-t border-gray-100 my-1"></div>
                                <button
                                  onClick={() => {
                                    router.push(`/guests/${guest.id}`);
                                    setActiveDropdown(null);
                                  }}
                                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                                >
                                  <Award className="h-4 w-4" />
                                  <span>View Rewards</span>
                                </button>
                                <button
                                  onClick={() => setActiveDropdown(null)}
                                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                                >
                                  <Calendar className="h-4 w-4" />
                                  <span>Booking History</span>
                                </button>
                                <button
                                  onClick={() => setActiveDropdown(null)}
                                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                                >
                                  <Plus className="h-4 w-4" />
                                  <span>New Reservation</span>
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}



        {/* No Results */}
        {filteredGuests.length === 0 && (
          <div className="text-center py-12">
            <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No guests found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default GuestsPage;