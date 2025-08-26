'use client';

import { useState, useEffect, useRef } from 'react';
import AppLayout, { HeaderActions } from '@/components/AppLayout';
import Link from 'next/link';
import { 
  Search,
  AlertTriangle,
  MessageSquare,
  User,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  Edit,
  Filter,
  Calendar,
  Star,
  Phone,
  Mail,
  MapPin,
  Grid3X3,
  List,
  Plus,
  X,
  Flag,
  Users,
  Building,
  Utensils,
  Wifi,
  Car,
  Bath,
  Bed,
  Coffee,
  Shield,
  AlertCircle,
  FileText,
  UserCheck,
  Headphones
} from 'lucide-react';

interface ComplaintResponse {
  id: number;
  responder_name: string;
  responder_role: string;
  response_text: string;
  response_date: string;
  action_taken: string;
}

interface Complaint {
  id: number;
  complaint_number: string;
  guest_name: string;
  guest_email: string;
  guest_phone: string;
  guest_room?: string;
  reservation_number?: string;
  category: 'room' | 'service' | 'food' | 'noise' | 'cleanliness' | 'amenities' | 'billing' | 'staff' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in_progress' | 'resolved' | 'closed' | 'escalated';
  subject: string;
  description: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  assigned_to?: string;
  department: string;
  satisfaction_rating?: number;
  compensation_offered?: string;
  compensation_amount?: number;
  follow_up_required: boolean;
  follow_up_date?: string;
  responses: ComplaintResponse[];
  attachments: string[];
  location?: string;
  incident_date?: string;
}

const MOCK_COMPLAINTS: Complaint[] = [
  {
    id: 1,
    complaint_number: 'CMP2024001',
    guest_name: 'John Smith',
    guest_email: 'john.smith@email.com',
    guest_phone: '+1-555-0123',
    guest_room: '1205',
    reservation_number: 'RSV123456',
    category: 'room',
    priority: 'high',
    status: 'in_progress',
    subject: 'Air conditioning not working properly',
    description: 'The air conditioning in room 1205 has been making loud noises and not cooling the room effectively since yesterday evening. We tried adjusting the thermostat but nothing changed. The room temperature is uncomfortably warm, affecting our sleep quality.',
    created_at: '2024-08-24T14:30:00Z',
    updated_at: '2024-08-24T16:45:00Z',
    assigned_to: 'Engineering Department',
    department: 'Engineering',
    follow_up_required: true,
    follow_up_date: '2024-08-25T10:00:00Z',
    responses: [
      {
        id: 1,
        responder_name: 'Ahmad Maintenance',
        responder_role: 'Engineering Supervisor',
        response_text: 'We have received your complaint and dispatched our technician to inspect the AC unit. Initial assessment shows the filter needs replacement and the unit requires servicing.',
        response_date: '2024-08-24T15:15:00Z',
        action_taken: 'Technician dispatched, filter replacement scheduled'
      }
    ],
    attachments: ['/complaints/images/ac-unit-1205.jpg'],
    location: 'Room 1205, Floor 12',
    incident_date: '2024-08-23T20:00:00Z'
  },
  {
    id: 2,
    complaint_number: 'CMP2024002',
    guest_name: 'Sarah Johnson',
    guest_email: 'sarah.johnson@email.com',
    guest_phone: '+1-555-0456',
    guest_room: '2001',
    reservation_number: 'RSV567890',
    category: 'service',
    priority: 'medium',
    status: 'resolved',
    subject: 'Delayed room service and cold food',
    description: 'Ordered room service at 7:30 PM for dinner. The food arrived at 9:15 PM, almost 2 hours late. When it finally arrived, the food was cold and the soup had a skin formed on top. Very disappointed with the service quality.',
    created_at: '2024-08-23T21:20:00Z',
    updated_at: '2024-08-24T08:30:00Z',
    resolved_at: '2024-08-24T08:30:00Z',
    assigned_to: 'F&B Department',
    department: 'Food & Beverage',
    satisfaction_rating: 4,
    compensation_offered: 'Full meal refund and complimentary breakfast',
    compensation_amount: 450000,
    follow_up_required: false,
    responses: [
      {
        id: 2,
        responder_name: 'Maria Santos',
        responder_role: 'F&B Manager',
        response_text: 'We sincerely apologize for the delayed service and cold food. This was due to kitchen staffing issues during peak hours. We have provided a full refund and arranged complimentary breakfast for your stay.',
        response_date: '2024-08-24T08:30:00Z',
        action_taken: 'Full refund processed, complimentary breakfast arranged, kitchen staffing reviewed'
      }
    ],
    attachments: [],
    location: 'Room 2001, Presidential Suite',
    incident_date: '2024-08-23T19:30:00Z'
  },
  {
    id: 3,
    complaint_number: 'CMP2024003',
    guest_name: 'Ahmad Rahman',
    guest_email: 'ahmad.rahman@email.com',
    guest_phone: '+62-812-3456-7890',
    guest_room: '1012',
    reservation_number: 'RSV234567',
    category: 'cleanliness',
    priority: 'medium',
    status: 'open',
    subject: 'Bathroom not properly cleaned',
    description: 'Upon check-in, found hair in the bathtub and water stains on the mirror. Towels had stains and the toilet was not properly cleaned. This is unacceptable for a hotel of this standard.',
    created_at: '2024-08-24T16:00:00Z',
    updated_at: '2024-08-24T16:00:00Z',
    assigned_to: 'Housekeeping Department',
    department: 'Housekeeping',
    follow_up_required: true,
    follow_up_date: '2024-08-25T09:00:00Z',
    responses: [],
    attachments: ['/complaints/images/bathroom-1012-before.jpg'],
    location: 'Room 1012, Floor 10',
    incident_date: '2024-08-24T15:30:00Z'
  },
  {
    id: 4,
    complaint_number: 'CMP2024004',
    guest_name: 'Lisa Wong',
    guest_email: 'lisa.wong@email.com',
    guest_phone: '+65-9876-5432',
    guest_room: '805',
    reservation_number: 'RSV345678',
    category: 'noise',
    priority: 'high',
    status: 'escalated',
    subject: 'Loud construction noise early morning',
    description: 'Starting from 6:00 AM, there has been extremely loud construction noise from nearby building works. This has disturbed our sleep for the past 3 days. We were not informed about ongoing construction when booking.',
    created_at: '2024-08-22T07:15:00Z',
    updated_at: '2024-08-24T11:20:00Z',
    assigned_to: 'General Manager',
    department: 'Management',
    follow_up_required: true,
    follow_up_date: '2024-08-25T14:00:00Z',
    responses: [
      {
        id: 3,
        responder_name: 'David Chen',
        responder_role: 'Front Office Manager',
        response_text: 'We apologize for the inconvenience. The construction is beyond our control but we should have informed guests. We are offering room relocation to a quieter floor and partial refund for affected nights.',
        response_date: '2024-08-23T10:30:00Z',
        action_taken: 'Room relocation offered, partial refund processed, guest communication policy updated'
      },
      {
        id: 4,
        responder_name: 'Robert Park',
        responder_role: 'General Manager',
        response_text: 'This matter has been escalated to me. We are implementing new procedures to inform guests about potential disturbances and offering additional compensation.',
        response_date: '2024-08-24T11:20:00Z',
        action_taken: 'Additional compensation approved, new guest communication procedures implemented'
      }
    ],
    attachments: ['/complaints/audio/construction-noise-recording.mp3'],
    location: 'Room 805, Floor 8',
    incident_date: '2024-08-22T06:00:00Z'
  },
  {
    id: 5,
    complaint_number: 'CMP2024005',
    guest_name: 'Michael Brown',
    guest_email: 'michael.brown@email.com',
    guest_phone: '+44-20-7946-0958',
    category: 'billing',
    priority: 'low',
    status: 'closed',
    subject: 'Incorrect charges on bill',
    description: 'Found charges for minibar items that we did not consume. The bill shows 2 bottles of wine and various snacks totaling $85, but we never opened the minibar during our 2-night stay.',
    created_at: '2024-08-20T11:45:00Z',
    updated_at: '2024-08-21T09:15:00Z',
    resolved_at: '2024-08-21T09:15:00Z',
    assigned_to: 'Front Office',
    department: 'Front Office',
    satisfaction_rating: 5,
    compensation_offered: 'Incorrect charges removed',
    compensation_amount: 1275000,
    follow_up_required: false,
    responses: [
      {
        id: 5,
        responder_name: 'Jennifer Lee',
        responder_role: 'Front Office Supervisor',
        response_text: 'We have reviewed the minibar sensors and found a malfunction that registered false consumption. All incorrect charges have been removed from your bill.',
        response_date: '2024-08-21T09:15:00Z',
        action_taken: 'Minibar sensor calibrated, charges reversed, billing system updated'
      }
    ],
    attachments: ['/complaints/docs/billing-dispute-proof.pdf'],
    incident_date: '2024-08-20T10:00:00Z'
  }
];

const ComplaintsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'card' | 'table'>('table');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  const [filterDepartment, setFilterDepartment] = useState<string>('all');
  const [filterDateFrom, setFilterDateFrom] = useState<string>('');
  const [filterDateTo, setFilterDateTo] = useState<string>('');
  const [openDropdown, setOpenDropdown] = useState<number | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpenDropdown(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      case 'escalated': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'urgent': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string, className: string = "h-4 w-4 text-white") => {
    switch (category) {
      case 'room': return <Bed className={className} />;
      case 'service': return <UserCheck className={className} />;
      case 'food': return <Utensils className={className} />;
      case 'noise': return <Headphones className={className} />;
      case 'cleanliness': return <Bath className={className} />;
      case 'amenities': return <Coffee className={className} />;
      case 'billing': return <FileText className={className} />;
      case 'staff': return <Users className={className} />;
      default: return <AlertTriangle className={className} />;
    }
  };

  const getCategoryName = (category: string) => {
    switch (category) {
      case 'room': return 'Room Issues';
      case 'service': return 'Service';
      case 'food': return 'Food & Beverage';
      case 'noise': return 'Noise';
      case 'cleanliness': return 'Cleanliness';
      case 'amenities': return 'Amenities';
      case 'billing': return 'Billing';
      case 'staff': return 'Staff';
      default: return 'Other';
    }
  };

  const filteredComplaints = MOCK_COMPLAINTS.filter(complaint => {
    if (searchTerm && 
        !complaint.guest_name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !complaint.complaint_number.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !complaint.subject.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !complaint.guest_email.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    if (filterStatus !== 'all' && complaint.status !== filterStatus) {
      return false;
    }
    if (filterPriority !== 'all' && complaint.priority !== filterPriority) {
      return false;
    }
    if (filterCategory !== 'all' && complaint.category !== filterCategory) {
      return false;
    }
    return true;
  });

  const getStatusStats = () => {
    return {
      open: MOCK_COMPLAINTS.filter(c => c.status === 'open').length,
      in_progress: MOCK_COMPLAINTS.filter(c => c.status === 'in_progress').length,
      resolved: MOCK_COMPLAINTS.filter(c => c.status === 'resolved').length,
      escalated: MOCK_COMPLAINTS.filter(c => c.status === 'escalated').length,
      urgent: MOCK_COMPLAINTS.filter(c => c.priority === 'urgent').length,
    };
  };

  const stats = getStatusStats();

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Guest Complaints</h1>
            <p className="text-gray-600 mt-2">Track and resolve guest complaints efficiently</p>
          </div>
          <div className="flex items-center space-x-2">
            <button className="flex items-center space-x-2 bg-[#005357] text-white px-4 py-2 text-sm font-medium hover:bg-[#004147] transition-colors">
              <Plus className="h-4 w-4" />
              <span>New Complaint</span>
            </button>
            <HeaderActions />
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.open}</div>
                <div className="text-sm text-gray-600">Open</div>
              </div>
              <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                <AlertCircle className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>
          <div className="bg-white shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.in_progress}</div>
                <div className="text-sm text-gray-600">In Progress</div>
              </div>
              <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                <Clock className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>
          <div className="bg-white shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.resolved}</div>
                <div className="text-sm text-gray-600">Resolved</div>
              </div>
              <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                <CheckCircle className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>
          <div className="bg-white shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.escalated}</div>
                <div className="text-sm text-gray-600">Escalated</div>
              </div>
              <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                <Flag className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>
          <div className="bg-white shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.urgent}</div>
                <div className="text-sm text-gray-600">Urgent</div>
              </div>
              <div className="w-8 h-8 bg-red-600 flex items-center justify-center">
                <AlertTriangle className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search complaints, guests, or complaint numbers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
            />
          </div>
          
          <div className="flex items-center space-x-2 h-10">
            {/* Advanced Filter Button */}
            <button
              onClick={() => setShowAdvancedFilter(true)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors h-full"
            >
              <Filter className="h-4 w-4" />
              <span>Advanced Filter</span>
            </button>
            
            {/* View Mode Toggle */}
            <div className="flex border border-gray-300 h-full">
              <button
                onClick={() => setViewMode('card')}
                className={`flex items-center justify-center px-3 py-2 text-xs transition-colors h-full ${
                  viewMode === 'card' 
                    ? 'bg-[#005357] text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Grid3X3 className="h-3 w-3" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`flex items-center justify-center px-3 py-2 text-xs transition-colors border-l border-gray-300 h-full ${
                  viewMode === 'table' 
                    ? 'bg-[#005357] text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <List className="h-3 w-3" />
              </button>
            </div>
          </div>
        </div>

        {/* Results Summary */}
        <div className="text-sm text-gray-600">
          {filteredComplaints.length} complaint{filteredComplaints.length !== 1 ? 's' : ''} found
        </div>

        {/* Complaints Display */}
        {viewMode === 'card' ? (
          /* Card View */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredComplaints.map((complaint) => (
              <div key={complaint.id} className="bg-white shadow">
                {/* Card Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{complaint.complaint_number}</h3>
                      <p className="text-sm text-gray-600 mt-1">{complaint.subject}</p>
                    </div>
                    <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                      {getCategoryIcon(complaint.category)}
                    </div>
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-4 bg-gray-50">
                  {/* Guest Info */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">{complaint.guest_name}</span>
                      <div className="flex items-center space-x-1">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(complaint.status)}`}>
                          {complaint.status.replace('_', ' ')}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(complaint.priority)}`}>
                          {complaint.priority}
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-600 space-y-1">
                      <div>{complaint.guest_email}</div>
                      {complaint.guest_room && <div>Room {complaint.guest_room}</div>}
                    </div>
                  </div>

                  {/* Category & Department */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getCategoryIcon(complaint.category, "h-4 w-4 text-gray-600")}
                        <span className="text-sm font-medium text-gray-700">{getCategoryName(complaint.category)}</span>
                      </div>
                      <span className="text-xs text-gray-500">{complaint.department}</span>
                    </div>
                  </div>

                  {/* Description */}
                  <div className="mb-4">
                    <p className="text-sm text-gray-700 line-clamp-3">
                      {complaint.description}
                    </p>
                  </div>

                  {/* Response Info */}
                  <div className="mb-4 text-xs text-gray-600">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <MessageSquare className="h-3 w-3" />
                        <span>{complaint.responses.length} response{complaint.responses.length !== 1 ? 's' : ''}</span>
                      </div>
                      <span>{formatDateTime(complaint.created_at)}</span>
                    </div>
                    {complaint.assigned_to && (
                      <div className="flex items-center space-x-2 mt-1">
                        <UserCheck className="h-3 w-3" />
                        <span>Assigned: {complaint.assigned_to}</span>
                      </div>
                    )}
                  </div>

                  {/* Follow-up Notice */}
                  {complaint.follow_up_required && complaint.follow_up_date && (
                    <div className="mb-4 p-2 bg-orange-50 border border-orange-200 text-xs text-orange-800">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>Follow-up due: {formatDateTime(complaint.follow_up_date)}</span>
                      </div>
                    </div>
                  )}

                  {/* Compensation */}
                  {complaint.compensation_offered && (
                    <div className="mb-4 p-2 bg-green-50 border border-green-200 text-xs">
                      <div className="text-green-800">
                        <strong>Compensation:</strong> {complaint.compensation_offered}
                        {complaint.compensation_amount && (
                          <span className="block text-green-600 font-medium">
                            {formatCurrency(complaint.compensation_amount)}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Satisfaction Rating */}
                  {complaint.satisfaction_rating && (
                    <div className="mb-4 flex items-center space-x-2">
                      <span className="text-xs text-gray-600">Rating:</span>
                      <div className="flex items-center space-x-1">
                        {[1,2,3,4,5].map(star => (
                          <Star 
                            key={star} 
                            className={`h-3 w-3 ${star <= complaint.satisfaction_rating! ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                          />
                        ))}
                        <span className="text-xs text-gray-600 ml-1">{complaint.satisfaction_rating}/5</span>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="grid grid-cols-2 gap-2">
                    <Link 
                      href={`/complaints/${complaint.id}`}
                      className="text-xs bg-gray-100 text-gray-700 px-3 py-2 hover:bg-gray-200 transition-colors text-center"
                    >
                      <Eye className="h-3 w-3 inline mr-1" />
                      View Details
                    </Link>
                    <button className="text-xs bg-[#005357] text-white px-3 py-2 hover:bg-[#004147] transition-colors">
                      <Edit className="h-3 w-3 inline mr-1" />
                      Update
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
                  <h3 className="text-xl font-bold text-gray-900">Complaints Overview</h3>
                  <p className="text-sm text-gray-600 mt-1">Track and manage all guest complaints</p>
                </div>
                <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                  <MessageSquare className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[#005357]">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Complaint
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Guest
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Category
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Priority
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Assigned To
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Created
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-white">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredComplaints.map((complaint) => (
                    <tr key={complaint.id} className="hover:bg-gray-50">
                      {/* Complaint Info */}
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-bold text-gray-900">{complaint.complaint_number}</div>
                          <div className="text-sm text-gray-900 font-medium">{complaint.subject}</div>
                          <div className="text-xs text-gray-600 line-clamp-2">{complaint.description}</div>
                        </div>
                      </td>

                      {/* Guest Info */}
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <div className="font-medium text-gray-900">{complaint.guest_name}</div>
                          <div className="text-gray-600 text-xs">{complaint.guest_email}</div>
                          {complaint.guest_room && (
                            <div className="text-gray-600 text-xs">Room {complaint.guest_room}</div>
                          )}
                        </div>
                      </td>

                      {/* Category */}
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          {getCategoryIcon(complaint.category, "h-4 w-4 text-gray-600")}
                          <span className="text-sm text-gray-700">{getCategoryName(complaint.category)}</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">{complaint.department}</div>
                      </td>

                      {/* Status */}
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${getStatusColor(complaint.status)}`}>
                          {complaint.status.replace('_', ' ')}
                        </span>
                        {complaint.responses.length > 0 && (
                          <div className="text-xs text-gray-500 mt-1 flex items-center space-x-1">
                            <MessageSquare className="h-3 w-3" />
                            <span>{complaint.responses.length} response{complaint.responses.length !== 1 ? 's' : ''}</span>
                          </div>
                        )}
                      </td>

                      {/* Priority */}
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${getPriorityColor(complaint.priority)}`}>
                          {complaint.priority}
                        </span>
                        {complaint.follow_up_required && complaint.follow_up_date && (
                          <div className="text-xs text-orange-600 mt-1 flex items-center space-x-1">
                            <Clock className="h-3 w-3" />
                            <span>Follow-up due</span>
                          </div>
                        )}
                      </td>

                      {/* Assigned To */}
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {complaint.assigned_to || 'Unassigned'}
                        </div>
                      </td>

                      {/* Created */}
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {formatDateTime(complaint.created_at)}
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="px-6 py-4">
                        <div className="relative" ref={openDropdown === complaint.id ? dropdownRef : null}>
                          <button
                            onClick={() => setOpenDropdown(openDropdown === complaint.id ? null : complaint.id)}
                            className="flex items-center justify-center w-8 h-8 text-gray-400 hover:text-gray-600 transition-colors"
                          >
                            •••
                          </button>
                          {openDropdown === complaint.id && (
                            <div className="absolute right-0 mt-1 w-48 bg-white shadow-lg border py-1 z-10">
                              <Link
                                href={`/complaints/${complaint.id}`}
                                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                onClick={() => setOpenDropdown(null)}
                              >
                                <Eye className="h-4 w-4 inline mr-2" />
                                View Details
                              </Link>
                              <button
                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                onClick={() => setOpenDropdown(null)}
                              >
                                <Edit className="h-4 w-4 inline mr-2" />
                                Edit Complaint
                              </button>
                              <button
                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                onClick={() => setOpenDropdown(null)}
                              >
                                <UserCheck className="h-4 w-4 inline mr-2" />
                                Assign Staff
                              </button>
                              <div className="border-t border-gray-100 my-1"></div>
                              <button
                                className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                onClick={() => setOpenDropdown(null)}
                              >
                                <XCircle className="h-4 w-4 inline mr-2" />
                                Close Complaint
                              </button>
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

        {/* Advanced Filter Modal */}
        {showAdvancedFilter && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              {/* Modal Header */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Advanced Filter</h3>
                    <p className="text-sm text-gray-600 mt-1">Filter complaints by multiple criteria</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                      <Filter className="h-4 w-4 text-white" />
                    </div>
                    <button
                      onClick={() => setShowAdvancedFilter(false)}
                      className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Modal Content */}
              <div className="p-6 bg-gray-50">
                <div className="space-y-6">
                  {/* Basic Filters */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Basic Filters</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                        <select
                          value={filterStatus}
                          onChange={(e) => setFilterStatus(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        >
                          <option value="all">All Status</option>
                          <option value="open">Open</option>
                          <option value="in_progress">In Progress</option>
                          <option value="resolved">Resolved</option>
                          <option value="closed">Closed</option>
                          <option value="escalated">Escalated</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                        <select
                          value={filterPriority}
                          onChange={(e) => setFilterPriority(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        >
                          <option value="all">All Priority</option>
                          <option value="low">Low</option>
                          <option value="medium">Medium</option>
                          <option value="high">High</option>
                          <option value="urgent">Urgent</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                        <select
                          value={filterCategory}
                          onChange={(e) => setFilterCategory(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        >
                          <option value="all">All Categories</option>
                          <option value="room">Room Issues</option>
                          <option value="service">Service</option>
                          <option value="food">Food & Beverage</option>
                          <option value="noise">Noise</option>
                          <option value="cleanliness">Cleanliness</option>
                          <option value="amenities">Amenities</option>
                          <option value="billing">Billing</option>
                          <option value="staff">Staff</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Advanced Filters */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Advanced Filters</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
                        <select
                          value={filterDepartment}
                          onChange={(e) => setFilterDepartment(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        >
                          <option value="all">All Departments</option>
                          <option value="Engineering">Engineering</option>
                          <option value="Food & Beverage">Food & Beverage</option>
                          <option value="Housekeeping">Housekeeping</option>
                          <option value="Front Office">Front Office</option>
                          <option value="Management">Management</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Date Range */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Date Range</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Created From</label>
                        <input
                          type="date"
                          value={filterDateFrom}
                          onChange={(e) => setFilterDateFrom(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Created To</label>
                        <input
                          type="date"
                          value={filterDateTo}
                          onChange={(e) => setFilterDateTo(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                    <button
                      onClick={() => {
                        setFilterStatus('all');
                        setFilterPriority('all');
                        setFilterCategory('all');
                        setFilterDepartment('all');
                        setFilterDateFrom('');
                        setFilterDateTo('');
                      }}
                      className="text-sm text-gray-600 hover:text-gray-800"
                    >
                      Clear All Filters
                    </button>
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => setShowAdvancedFilter(false)}
                        className="px-4 py-2 border border-gray-300 text-gray-700 text-sm hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => setShowAdvancedFilter(false)}
                        className="px-4 py-2 bg-[#005357] text-white text-sm hover:bg-[#004147]"
                      >
                        Apply Filters
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* No Results */}
        {filteredComplaints.length === 0 && (
          <div className="text-center py-12">
            <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No complaints found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default ComplaintsPage;