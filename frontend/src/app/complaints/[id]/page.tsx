'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import AppLayout, { HeaderActions } from '@/components/AppLayout';
import { 
  ArrowLeft,
  AlertTriangle,
  MessageSquare,
  User,
  Clock,
  CheckCircle,
  Edit,
  Star,
  Phone,
  Mail,
  Building,
  FileText,
  UserCheck,
  Flag,
  Plus,
  Send,
  Paperclip,
  Shield,
  Headphones,
  Bed,
  Bath,
  Coffee,
  Utensils,
  Users,
  History
} from 'lucide-react';

interface ComplaintResponse {
  id: number;
  responder_name: string;
  responder_role: string;
  response_text: string;
  response_date: string;
  action_taken: string;
}

interface TimelineEvent {
  id: string;
  type: 'complaint_created' | 'status_change' | 'response' | 'assignment' | 'resolution';
  title: string;
  description: string;
  timestamp: string;
  user?: string;
  user_role?: string;
  status_from?: string;
  status_to?: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
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

// Mock data for the complaint detail
const MOCK_COMPLAINT: Complaint = {
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
  description: 'The air conditioning in room 1205 has been making loud noises and not cooling the room effectively since yesterday evening. We tried adjusting the thermostat but nothing changed. The room temperature is uncomfortably warm, affecting our sleep quality. This is our 3rd night and we really need this resolved as it\'s affecting our vacation experience. We are loyal customers and have stayed at this hotel multiple times before. We hope this can be resolved quickly.',
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
      response_text: 'We have received your complaint and dispatched our technician to inspect the AC unit. Initial assessment shows the filter needs replacement and the unit requires servicing. We apologize for the inconvenience and will have this resolved within 2 hours.',
      response_date: '2024-08-24T15:15:00Z',
      action_taken: 'Technician dispatched, filter replacement scheduled, AC service arranged'
    },
    {
      id: 2,
      responder_name: 'Sarah Wilson',
      responder_role: 'Guest Relations Manager',
      response_text: 'Mr. Smith, we sincerely apologize for this inconvenience during your stay. As compensation for the discomfort, we have arranged a complimentary room upgrade and will provide a late checkout. Our engineering team is working to resolve this immediately.',
      response_date: '2024-08-24T16:30:00Z',
      action_taken: 'Room upgrade arranged, late checkout approved, guest compensation processed'
    }
  ],
  attachments: [
    '/complaints/images/ac-unit-1205.jpg',
    '/complaints/images/room-1205-temperature.jpg'
  ],
  location: 'Room 1205, Floor 12',
  incident_date: '2024-08-23T20:00:00Z'
};

const ComplaintDetailPage = () => {
  const params = useParams();
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [loading, setLoading] = useState(true);
  const [newResponse, setNewResponse] = useState('');
  const [newActionTaken, setNewActionTaken] = useState('');
  const [newStatus, setNewStatus] = useState('');

  useEffect(() => {
    // Simulate API call
    const loadComplaint = async () => {
      setLoading(true);
      // In a real app, this would be: const response = await fetch(`/api/complaints/${params.id}/`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
      setComplaint(MOCK_COMPLAINT);
      setLoading(false);
    };

    loadComplaint();
  }, [params.id]);

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'long',
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

  const handleAddResponse = () => {
    if (!newResponse.trim()) return;

    const response: ComplaintResponse = {
      id: Date.now(),
      responder_name: 'Current User', // In real app, get from auth context
      responder_role: 'Staff Member',
      response_text: newResponse,
      response_date: new Date().toISOString(),
      action_taken: newActionTaken
    };

    if (complaint) {
      setComplaint({
        ...complaint,
        responses: [...complaint.responses, response],
        updated_at: new Date().toISOString()
      });
    }

    setNewResponse('');
    setNewActionTaken('');
  };

  const handleStatusUpdate = () => {
    if (!newStatus || !complaint) return;

    setComplaint({
      ...complaint,
      status: newStatus as 'open' | 'in_progress' | 'resolved' | 'closed' | 'escalated',
      updated_at: new Date().toISOString(),
      resolved_at: newStatus === 'resolved' || newStatus === 'closed' ? new Date().toISOString() : undefined
    });

    setNewStatus('');
  };

  const getEventIconColor = (type: string) => {
    switch (type) {
      case 'complaint_created': return 'bg-red-500';
      case 'assignment': return 'bg-purple-500';
      case 'response': return 'bg-green-500';
      case 'status_change': return 'bg-yellow-500';
      case 'resolution': return 'bg-blue-500';
      default: return 'bg-[#005357]';
    }
  };

  const generateTimelineEvents = (complaint: Complaint): TimelineEvent[] => {
    const events: TimelineEvent[] = [];
    
    // Initial complaint created
    events.push({
      id: 'created',
      type: 'complaint_created',
      title: 'Complaint Submitted',
      description: `Guest ${complaint.guest_name} submitted a complaint about "${complaint.subject}"`,
      timestamp: complaint.created_at,
      user: complaint.guest_name,
      user_role: 'Guest',
      icon: AlertTriangle,
      color: 'bg-red-100 text-red-800'
    });

    // Assignment event (if assigned)
    if (complaint.assigned_to) {
      events.push({
        id: 'assigned',
        type: 'assignment',
        title: 'Complaint Assigned',
        description: `Assigned to ${complaint.assigned_to}`,
        timestamp: complaint.created_at, // In real app, would have separate timestamp
        user: 'System',
        user_role: 'System',
        icon: UserCheck,
        color: 'bg-purple-100 text-purple-800'
      });
    }

    // Add all responses
    complaint.responses.forEach((response) => {
      events.push({
        id: `response-${response.id}`,
        type: 'response',
        title: 'Staff Response',
        description: response.response_text + (response.action_taken ? `\n\nActions Taken: ${response.action_taken}` : ''),
        timestamp: response.response_date,
        user: response.responder_name,
        user_role: response.responder_role,
        icon: MessageSquare,
        color: 'bg-green-100 text-green-800'
      });
    });

    // Status changes (simulated - in real app would track actual status changes)
    if (complaint.status === 'in_progress') {
      events.push({
        id: 'status-progress',
        type: 'status_change',
        title: 'Status Updated',
        description: 'Complaint status changed to In Progress',
        timestamp: complaint.updated_at,
        status_from: 'open',
        status_to: 'in_progress',
        icon: Clock,
        color: 'bg-yellow-100 text-yellow-800'
      });
    }

    // Resolution event (if resolved)
    if (complaint.resolved_at) {
      events.push({
        id: 'resolved',
        type: 'resolution',
        title: 'Complaint Resolved',
        description: 'Complaint has been marked as resolved',
        timestamp: complaint.resolved_at,
        icon: CheckCircle,
        color: 'bg-blue-100 text-blue-800'
      });
    }

    // Sort events by timestamp
    return events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="p-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (!complaint) {
    return (
      <AppLayout>
        <div className="p-6">
          <div className="text-center">
            <AlertTriangle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Complaint Not Found</h2>
            <p className="text-gray-600 mb-6">The complaint you&apos;re looking for doesn&apos;t exist or has been removed.</p>
            <Link 
              href="/complaints"
              className="inline-flex items-center space-x-2 bg-[#005357] text-white px-4 py-2 hover:bg-[#004147] transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Complaints</span>
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-4">
          <Link 
            href="/complaints"
            className="inline-flex items-center space-x-2 text-gray-600 hover:text-[#005357] transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="text-sm font-medium">Back to Complaints</span>
          </Link>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold text-gray-900">Complaint Details</h1>
                <span className={`inline-flex px-3 py-1 text-sm font-medium rounded ${getStatusColor(complaint.status)}`}>
                  {complaint.status.replace('_', ' ')}
                </span>
                <span className={`inline-flex px-3 py-1 text-sm font-medium rounded ${getPriorityColor(complaint.priority)}`}>
                  {complaint.priority}
                </span>
              </div>
              <p className="text-gray-600 mt-2">
                {complaint.complaint_number} • Created on {formatDateTime(complaint.created_at)}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button className="flex items-center space-x-2 bg-[#005357] text-white px-4 py-2 text-sm font-medium hover:bg-[#004147] transition-colors">
                <Edit className="h-4 w-4" />
                <span>Update Status</span>
              </button>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Guest Information */}
          <div className="bg-[#005357] p-6 sticky top-6 self-start">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-white">Guest Information & Complaint Details</h2>
              <p className="text-green-100">Information provided by the guest</p>
            </div>
            
            <div className="space-y-6">
            {/* Guest Information */}
            <div className="bg-[#004147] shadow">
              <div className="p-6 border-b border-[#003035]">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-white">Guest Information</h3>
                    <p className="text-sm text-green-100 mt-1">Contact details and reservation info</p>
                  </div>
                  <div className="w-8 h-8 bg-[#2baf6a] flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
              <div className="p-4 bg-[#003035]">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-green-200">Guest Name</label>
                    <p className="text-white font-bold text-lg">{complaint.guest_name}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 gap-3">
                    <div className="flex items-center space-x-2">
                      <Mail className="h-4 w-4 text-green-300" />
                      <span className="text-green-100">{complaint.guest_email}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Phone className="h-4 w-4 text-green-300" />
                      <span className="text-green-100">{complaint.guest_phone}</span>
                    </div>
                    {complaint.guest_room && (
                      <div className="flex items-center space-x-2">
                        <Building className="h-4 w-4 text-green-300" />
                        <span className="text-green-100">Room {complaint.guest_room}</span>
                      </div>
                    )}
                    {complaint.reservation_number && (
                      <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4 text-green-300" />
                        <span className="text-green-100">Reservation: {complaint.reservation_number}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Complaint Description */}
            <div className="bg-[#004147] shadow">
              <div className="p-6 border-b border-[#003035]">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-white">Complaint Description</h3>
                    <p className="text-sm text-green-100 mt-1">Guest&apos;s detailed complaint</p>
                  </div>
                  <div className="w-8 h-8 bg-[#2baf6a] flex items-center justify-center">
                    <MessageSquare className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
              <div className="p-4 bg-[#003035]">
                <div className="space-y-4">
                  <div>
                    <h4 className="text-lg font-bold text-white mb-3">{complaint.subject}</h4>
                    <p className="text-green-100 leading-relaxed whitespace-pre-wrap">
                      {complaint.description}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Attachments */}
            <div className="bg-[#004147] shadow">
              <div className="p-6 border-b border-[#003035]">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-white">Attachments</h3>
                    <p className="text-sm text-green-100 mt-1">Supporting documents and images</p>
                  </div>
                  <div className="w-8 h-8 bg-[#2baf6a] flex items-center justify-center">
                    <Paperclip className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
              <div className="p-4 bg-[#003035]">
                {complaint.attachments.length > 0 ? (
                  <div className="space-y-2">
                    {complaint.attachments.map((attachment, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-[#004147] border border-[#005357] rounded">
                        <FileText className="h-5 w-5 text-green-300" />
                        <span className="text-sm text-green-100 flex-1">{attachment.split('/').pop()}</span>
                        <button className="text-green-300 hover:text-green-200 text-sm font-medium">
                          View
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Paperclip className="h-12 w-12 text-green-300 mx-auto mb-2" />
                    <p className="text-green-100">No attachments</p>
                  </div>
                )}
              </div>
            </div>
            </div>
          </div>

          {/* Middle Column - Internal Details */}
          <div className="space-y-6">
            {/* Complaint Details */}
            <div className="bg-white shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Internal Details</h3>
                    <p className="text-sm text-gray-600 mt-1">Category and assignment information</p>
                  </div>
                  <div className="w-8 h-8 bg-gray-600 flex items-center justify-center">
                    {getCategoryIcon(complaint.category)}
                  </div>
                </div>
              </div>
              <div className="p-4 bg-gray-50">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Category</label>
                    <div className="flex items-center space-x-2 mt-1">
                      {getCategoryIcon(complaint.category, "h-4 w-4 text-gray-600")}
                      <span className="font-medium text-gray-900">{getCategoryName(complaint.category)}</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-600">Department</label>
                    <p className="text-gray-900 font-medium">{complaint.department}</p>
                  </div>
                  
                  {complaint.assigned_to && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Assigned To</label>
                      <p className="text-gray-900 font-medium">{complaint.assigned_to}</p>
                    </div>
                  )}
                  
                  {complaint.location && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Location</label>
                      <p className="text-gray-900">{complaint.location}</p>
                    </div>
                  )}
                  
                  {complaint.incident_date && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Incident Date</label>
                      <p className="text-gray-900">{formatDateTime(complaint.incident_date)}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Status Information */}
            <div className="bg-white shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Status Information</h3>
                    <p className="text-sm text-gray-600 mt-1">Follow-up and satisfaction details</p>
                  </div>
                  <div className="w-8 h-8 bg-gray-600 flex items-center justify-center">
                    <Flag className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
              <div className="p-4 bg-gray-50">
                <div className="space-y-4">
                  {complaint.follow_up_required && complaint.follow_up_date && (
                    <div className="p-3 bg-orange-50 border border-orange-200 rounded">
                      <div className="flex items-center space-x-2 text-orange-800">
                        <Clock className="h-4 w-4" />
                        <span className="font-medium">Follow-up Required</span>
                      </div>
                      <p className="text-orange-700 mt-1 text-sm">Due: {formatDateTime(complaint.follow_up_date)}</p>
                    </div>
                  )}
                  
                  {complaint.satisfaction_rating && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Guest Satisfaction</label>
                      <div className="flex items-center space-x-2 mt-1">
                        {[1,2,3,4,5].map(star => (
                          <Star 
                            key={star} 
                            className={`h-4 w-4 ${star <= complaint.satisfaction_rating! ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                          />
                        ))}
                        <span className="text-gray-600 text-sm">({complaint.satisfaction_rating}/5)</span>
                      </div>
                    </div>
                  )}

                  {complaint.compensation_offered && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded">
                      <div className="text-green-800">
                        <span className="font-medium">Compensation Offered</span>
                        <p className="mt-1 text-sm">{complaint.compensation_offered}</p>
                        {complaint.compensation_amount && (
                          <p className="font-medium text-green-600 mt-1">
                            Amount: {formatCurrency(complaint.compensation_amount)}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="text-sm text-gray-600">
                    <p><span className="font-medium">Created:</span> {formatDateTime(complaint.created_at)}</p>
                    <p><span className="font-medium">Last Updated:</span> {formatDateTime(complaint.updated_at)}</p>
                    {complaint.resolved_at && (
                      <p><span className="font-medium">Resolved:</span> {formatDateTime(complaint.resolved_at)}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Quick Actions</h3>
                    <p className="text-sm text-gray-600 mt-1">Update complaint status</p>
                  </div>
                  <div className="w-8 h-8 bg-gray-600 flex items-center justify-center">
                    <Shield className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
              <div className="p-4 bg-gray-50">
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Change Status</label>
                    <select
                      value={newStatus}
                      onChange={(e) => setNewStatus(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                    >
                      <option value="">Select new status...</option>
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
                      <option value="escalated">Escalated</option>
                    </select>
                  </div>
                  <button 
                    onClick={handleStatusUpdate}
                    disabled={!newStatus}
                    className="w-full bg-[#005357] text-white px-4 py-2 text-sm font-medium hover:bg-[#004147] transition-colors disabled:opacity-50"
                  >
                    Update Status
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Timeline & Actions */}
          <div className="space-y-6">
            {/* Complaint Timeline */}
            <div className="bg-white shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Complaint Timeline</h3>
                    <p className="text-sm text-gray-600 mt-1">Complete history from submission to resolution</p>
                  </div>
                  <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                    <History className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
              <div className="p-6 bg-gray-50">
                <div className="flow-root">
                  <ul className="-mb-8">
                    {generateTimelineEvents(complaint).map((event, eventIdx) => (
                      <li key={event.id}>
                        <div className="relative pb-8">
                          {eventIdx !== generateTimelineEvents(complaint).length - 1 ? (
                            <span
                              className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                              aria-hidden="true"
                            />
                          ) : null}
                          <div className="relative flex space-x-3">
                            <div>
                              <span className={`h-8 w-8 rounded-full ${getEventIconColor(event.type)} flex items-center justify-center ring-8 ring-white`}>
                                <event.icon className="h-4 w-4 text-white" aria-hidden="true" />
                              </span>
                            </div>
                            <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                              <div>
                                <p className="text-sm font-medium text-gray-900">{event.title}</p>
                                <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">{event.description}</p>
                                {event.user && (
                                  <p className="text-xs text-gray-500 mt-1">
                                    by {event.user} {event.user_role && `(${event.user_role})`}
                                  </p>
                                )}
                                {event.type === 'response' && (
                                  <div className="mt-2 text-xs">
                                    <span className={`inline-flex px-2 py-1 rounded ${event.color}`}>
                                      Staff Response
                                    </span>
                                  </div>
                                )}
                                {event.type === 'status_change' && event.status_from && event.status_to && (
                                  <div className="mt-2 text-xs">
                                    <span className="text-gray-500">
                                      Status changed from <span className="font-medium">{event.status_from}</span> to <span className="font-medium">{event.status_to}</span>
                                    </span>
                                  </div>
                                )}
                              </div>
                              <div className="whitespace-nowrap text-right text-sm text-gray-500">
                                <time dateTime={event.timestamp}>
                                  {formatDateTime(event.timestamp)}
                                </time>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Add Response */}
            <div className="bg-white shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Add Response</h3>
                    <p className="text-sm text-gray-600 mt-1">Respond to the guest&apos;s complaint</p>
                  </div>
                  <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                    <Plus className="h-4 w-4 text-white" />
                  </div>
                </div>
              </div>
              <div className="p-4 bg-gray-50">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Response Message</label>
                    <textarea
                      value={newResponse}
                      onChange={(e) => setNewResponse(e.target.value)}
                      placeholder="Type your response to the guest..."
                      className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                      rows={4}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Actions Taken (Optional)</label>
                    <textarea
                      value={newActionTaken}
                      onChange={(e) => setNewActionTaken(e.target.value)}
                      placeholder="Describe what actions were taken to resolve the issue..."
                      className="w-full px-3 py-2 border border-gray-300 focus:ring-[#005357] focus:border-[#005357] text-sm"
                      rows={3}
                    />
                  </div>
                  
                  <button 
                    onClick={handleAddResponse}
                    disabled={!newResponse.trim()}
                    className="w-full flex items-center justify-center space-x-2 bg-[#005357] text-white px-4 py-2 text-sm font-medium hover:bg-[#004147] transition-colors disabled:opacity-50"
                  >
                    <Send className="h-4 w-4" />
                    <span>Send Response</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default ComplaintDetailPage;