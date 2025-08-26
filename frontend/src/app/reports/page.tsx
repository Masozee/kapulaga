'use client';

import { useState } from 'react';
import AppLayout from '@/components/AppLayout';
import {
  BarChart3,
  Calendar,
  Clock,
  TrendingUp,
  TrendingDown,
  Users,
  Wrench,
  CheckCircle,
  AlertTriangle,
  DollarSign,
  FileText,
  Download,
  Filter,
  RefreshCw,
  Eye,
  PieChart,
  Activity,
  Target,
  Award,
  Timer,
  Building,
  Settings,
  HardHat,
  Package,
  Zap,
  Thermometer,
  Droplets,
  Wifi,
  Shield
} from 'lucide-react';

interface DailyReport {
  date: string;
  total_requests: number;
  completed: number;
  pending: number;
  urgent: number;
  average_resolution_time: number; // in hours
  cost_incurred: number;
  top_category: string;
  efficiency_rate: number; // percentage
}

interface MonthlyReport {
  month: string;
  year: number;
  total_requests: number;
  completed: number;
  pending: number;
  cancelled: number;
  total_cost: number;
  average_cost_per_request: number;
  technician_performance: TechnicianPerformance[];
  category_breakdown: CategoryBreakdown[];
  trend_comparison: number; // percentage change from previous month
}

interface TechnicianPerformance {
  id: number;
  name: string;
  requests_completed: number;
  average_time: number;
  efficiency_score: number;
  customer_satisfaction: number;
}

interface CategoryBreakdown {
  category: string;
  count: number;
  percentage: number;
  total_cost: number;
}

// Mock data
const MOCK_DAILY_REPORTS: DailyReport[] = [
  {
    date: '2024-08-26',
    total_requests: 15,
    completed: 12,
    pending: 3,
    urgent: 2,
    average_resolution_time: 4.5,
    cost_incurred: 3250000,
    top_category: 'HVAC',
    efficiency_rate: 87
  },
  {
    date: '2024-08-25',
    total_requests: 18,
    completed: 15,
    pending: 3,
    urgent: 1,
    average_resolution_time: 3.8,
    cost_incurred: 4100000,
    top_category: 'Electrical',
    efficiency_rate: 92
  },
  {
    date: '2024-08-24',
    total_requests: 12,
    completed: 10,
    pending: 2,
    urgent: 3,
    average_resolution_time: 5.2,
    cost_incurred: 2800000,
    top_category: 'Plumbing',
    efficiency_rate: 78
  },
  {
    date: '2024-08-23',
    total_requests: 20,
    completed: 18,
    pending: 2,
    urgent: 2,
    average_resolution_time: 4.1,
    cost_incurred: 5200000,
    top_category: 'HVAC',
    efficiency_rate: 95
  }
];

const MOCK_MONTHLY_REPORTS: MonthlyReport[] = [
  {
    month: 'August',
    year: 2024,
    total_requests: 425,
    completed: 398,
    pending: 15,
    cancelled: 12,
    total_cost: 125000000,
    average_cost_per_request: 294117,
    trend_comparison: 8.5, // 8.5% increase from July
    technician_performance: [
      {
        id: 1,
        name: 'Ahmad Technical',
        requests_completed: 45,
        average_time: 3.2,
        efficiency_score: 94,
        customer_satisfaction: 4.8
      },
      {
        id: 2,
        name: 'Budi Elevator Tech',
        requests_completed: 32,
        average_time: 5.8,
        efficiency_score: 91,
        customer_satisfaction: 4.9
      },
      {
        id: 3,
        name: 'Joko Plumber',
        requests_completed: 38,
        average_time: 4.1,
        efficiency_score: 88,
        customer_satisfaction: 4.6
      },
      {
        id: 4,
        name: 'IT Support Team',
        requests_completed: 28,
        average_time: 2.9,
        efficiency_score: 96,
        customer_satisfaction: 4.7
      }
    ],
    category_breakdown: [
      {
        category: 'HVAC',
        count: 125,
        percentage: 29.4,
        total_cost: 45000000
      },
      {
        category: 'Electrical',
        count: 98,
        percentage: 23.1,
        total_cost: 32000000
      },
      {
        category: 'Plumbing',
        count: 87,
        percentage: 20.5,
        total_cost: 22000000
      },
      {
        category: 'Elevator',
        count: 45,
        percentage: 10.6,
        total_cost: 18000000
      },
      {
        category: 'IT/Network',
        count: 42,
        percentage: 9.9,
        total_cost: 5500000
      },
      {
        category: 'General',
        count: 28,
        percentage: 6.5,
        total_cost: 2500000
      }
    ]
  }
];

const ReportsPage = () => {
  const [activeTab, setActiveTab] = useState<'daily' | 'monthly'>('daily');
  const [selectedDate, setSelectedDate] = useState('2024-08-26');
  const [selectedMonth, setSelectedMonth] = useState('August 2024');

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'hvac': return <Thermometer className="h-4 w-4" />;
      case 'plumbing': return <Droplets className="h-4 w-4" />;
      case 'electrical': return <Zap className="h-4 w-4" />;
      case 'elevator': return <Building className="h-4 w-4" />;
      case 'it/network': return <Wifi className="h-4 w-4" />;
      case 'general': return <Wrench className="h-4 w-4" />;
      case 'security': return <Shield className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const currentDailyReport = MOCK_DAILY_REPORTS.find(report => report.date === selectedDate) || MOCK_DAILY_REPORTS[0];
  const currentMonthlyReport = MOCK_MONTHLY_REPORTS[0];

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Maintenance Reports</h1>
          <p className="text-gray-600 mt-2">Comprehensive daily and monthly maintenance analytics</p>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'daily', name: 'Daily Reports', icon: Calendar },
              { id: 'monthly', name: 'Monthly Reports', icon: BarChart3 }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'daily' | 'monthly')}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-[#005357] text-[#005357]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {activeTab === 'daily' ? (
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-gray-400" />
                <select
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-[#005357] focus:border-[#005357]"
                >
                  {MOCK_DAILY_REPORTS.map((report) => (
                    <option key={report.date} value={report.date}>
                      {formatDate(report.date)}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4 text-gray-400" />
                <select
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                  className="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-[#005357] focus:border-[#005357]"
                >
                  <option value="August 2024">August 2024</option>
                  <option value="July 2024">July 2024</option>
                  <option value="June 2024">June 2024</option>
                </select>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-4 py-2 text-sm font-medium rounded hover:bg-gray-200 transition-colors">
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
            <button className="flex items-center space-x-2 bg-[#005357] text-white px-4 py-2 text-sm font-medium rounded hover:bg-[#004147] transition-colors">
              <Download className="h-4 w-4" />
              <span>Export PDF</span>
            </button>
          </div>
        </div>

        {/* Reports Content */}
        {activeTab === 'daily' && (
          <div className="space-y-6">
            {/* Daily Overview Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Total Requests</h3>
                      <div className="text-sm text-gray-100 mt-1">{formatDate(currentDailyReport.date)}</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#005357] mb-2">{currentDailyReport.total_requests}</div>
                    <div className="text-sm text-gray-600">requests received</div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Completed</h3>
                      <div className="text-sm text-gray-100 mt-1">Finished today</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">{currentDailyReport.completed}</div>
                    <div className="text-sm text-gray-600">
                      {Math.round((currentDailyReport.completed / currentDailyReport.total_requests) * 100)}% completion rate
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Avg Resolution</h3>
                      <div className="text-sm text-gray-100 mt-1">Time to complete</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">{currentDailyReport.average_resolution_time}h</div>
                    <div className="text-sm text-gray-600">average time</div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Daily Cost</h3>
                      <div className="text-sm text-gray-100 mt-1">Total expenses</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-[#005357] mb-2">{formatCurrency(currentDailyReport.cost_incurred)}</div>
                    <div className="text-sm text-gray-600">incurred today</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Daily Details */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white shadow">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Performance Metrics</h3>
                      <p className="text-sm text-gray-100 mt-1">Key performance indicators for today</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-white rounded">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                          <Target className="h-4 w-4 text-green-600" />
                        </div>
                        <span className="text-sm font-medium text-gray-900">Efficiency Rate</span>
                      </div>
                      <span className="text-lg font-bold text-green-600">{currentDailyReport.efficiency_rate}%</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-white rounded">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                          <AlertTriangle className="h-4 w-4 text-orange-600" />
                        </div>
                        <span className="text-sm font-medium text-gray-900">Urgent Requests</span>
                      </div>
                      <span className="text-lg font-bold text-orange-600">{currentDailyReport.urgent}</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-white rounded">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Clock className="h-4 w-4 text-blue-600" />
                        </div>
                        <span className="text-sm font-medium text-gray-900">Pending Requests</span>
                      </div>
                      <span className="text-lg font-bold text-blue-600">{currentDailyReport.pending}</span>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-white rounded">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                          {getCategoryIcon(currentDailyReport.top_category)}
                        </div>
                        <span className="text-sm font-medium text-gray-900">Top Category</span>
                      </div>
                      <span className="text-lg font-bold text-purple-600">{currentDailyReport.top_category}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Recent Daily Trends</h3>
                      <p className="text-sm text-gray-100 mt-1">Last 4 days comparison</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="space-y-3">
                    {MOCK_DAILY_REPORTS.map((report, index) => (
                      <div key={report.date} className={`p-3 rounded ${selectedDate === report.date ? 'bg-[#005357] text-white' : 'bg-white'}`}>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className={`font-medium ${selectedDate === report.date ? 'text-white' : 'text-gray-900'}`}>
                              {formatDate(report.date)}
                            </div>
                            <div className={`text-sm ${selectedDate === report.date ? 'text-gray-200' : 'text-gray-600'}`}>
                              {report.completed}/{report.total_requests} completed • {report.efficiency_rate}% efficiency
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`font-bold ${selectedDate === report.date ? 'text-white' : 'text-[#005357]'}`}>
                              {formatCurrency(report.cost_incurred)}
                            </div>
                            <div className={`text-xs ${selectedDate === report.date ? 'text-gray-200' : 'text-gray-500'}`}>
                              {report.average_resolution_time}h avg
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'monthly' && (
          <div className="space-y-6">
            {/* Monthly Overview Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Total Requests</h3>
                      <div className="text-sm text-gray-100 mt-1">{currentMonthlyReport.month} {currentMonthlyReport.year}</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#005357] mb-2">{currentMonthlyReport.total_requests}</div>
                    <div className="flex items-center justify-center space-x-1 text-sm">
                      <TrendingUp className="h-3 w-3 text-green-500" />
                      <span className="text-green-600">+{currentMonthlyReport.trend_comparison}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Completion Rate</h3>
                      <div className="text-sm text-gray-100 mt-1">Successfully resolved</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">
                      {Math.round((currentMonthlyReport.completed / currentMonthlyReport.total_requests) * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">{currentMonthlyReport.completed} completed</div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Total Cost</h3>
                      <div className="text-sm text-gray-100 mt-1">Monthly expenses</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-[#005357] mb-2">{formatCurrency(currentMonthlyReport.total_cost)}</div>
                    <div className="text-sm text-gray-600">this month</div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow hover:bg-[#005357] hover:text-white transition-colors duration-200 cursor-pointer group">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Avg Cost/Request</h3>
                      <div className="text-sm text-gray-100 mt-1">Per maintenance item</div>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-2">{formatCurrency(currentMonthlyReport.average_cost_per_request)}</div>
                    <div className="text-sm text-gray-600">average</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Monthly Details */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Category Breakdown */}
              <div className="bg-white shadow">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Category Breakdown</h3>
                      <p className="text-sm text-gray-100 mt-1">Requests by maintenance type</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="space-y-3">
                    {currentMonthlyReport.category_breakdown.map((category, index) => (
                      <div key={category.category} className="flex items-center justify-between p-3 bg-white rounded">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-[#005357] rounded-full flex items-center justify-center text-white">
                            {getCategoryIcon(category.category)}
                          </div>
                          <div>
                            <span className="font-medium text-gray-900">{category.category}</span>
                            <div className="text-sm text-gray-600">{category.percentage}% of total</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-[#005357]">{category.count}</div>
                          <div className="text-sm text-gray-600">{formatCurrency(category.total_cost)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Technician Performance */}
              <div className="bg-white shadow">
                <div className="p-6 bg-[#005357] text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Technician Performance</h3>
                      <p className="text-sm text-gray-100 mt-1">Top performers this month</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-gray-50">
                  <div className="space-y-3">
                    {currentMonthlyReport.technician_performance.map((tech, index) => (
                      <div key={tech.id} className="flex items-center justify-between p-3 bg-white rounded">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <HardHat className="h-4 w-4 text-blue-600" />
                          </div>
                          <div>
                            <span className="font-medium text-gray-900">{tech.name}</span>
                            <div className="text-sm text-gray-600">
                              {tech.requests_completed} requests • {tech.average_time}h avg
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center space-x-1">
                            <Award className="h-4 w-4 text-yellow-500" />
                            <span className="font-bold text-[#005357]">{tech.efficiency_score}%</span>
                          </div>
                          <div className="text-sm text-gray-600">★ {tech.customer_satisfaction}/5</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Monthly Summary */}
            <div className="bg-white shadow">
              <div className="p-6 bg-[#005357] text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-white">Monthly Summary</h3>
                    <p className="text-sm text-gray-100 mt-1">Complete overview of {currentMonthlyReport.month} {currentMonthlyReport.year}</p>
                  </div>
                </div>
              </div>
              <div className="p-4 bg-gray-50">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-white rounded">
                    <div className="text-2xl font-bold text-[#005357] mb-2">{currentMonthlyReport.completed}</div>
                    <div className="text-sm text-gray-600">Completed</div>
                  </div>
                  <div className="text-center p-4 bg-white rounded">
                    <div className="text-2xl font-bold text-orange-600 mb-2">{currentMonthlyReport.pending}</div>
                    <div className="text-sm text-gray-600">Pending</div>
                  </div>
                  <div className="text-center p-4 bg-white rounded">
                    <div className="text-2xl font-bold text-red-600 mb-2">{currentMonthlyReport.cancelled}</div>
                    <div className="text-sm text-gray-600">Cancelled</div>
                  </div>
                  <div className="text-center p-4 bg-white rounded">
                    <div className="text-2xl font-bold text-green-600 mb-2">
                      {currentMonthlyReport.technician_performance.length}
                    </div>
                    <div className="text-sm text-gray-600">Active Techs</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default ReportsPage;