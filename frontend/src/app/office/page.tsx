import AppLayout from '@/components/AppLayout';
import { Building2, TrendingUp, Users, CreditCard, FileText, Settings, UserCog, Clock, Hotel } from 'lucide-react';

export default function OfficePage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <div className="flex items-center space-x-3">
            <Building2 className="h-8 w-8 text-blue-500" />
            <h1 className="text-3xl font-bold text-gray-900">Office Management</h1>
          </div>
          <p className="text-gray-600 mt-2">Administrative tools and financial management</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
                <p className="text-2xl font-bold text-gray-900">$45,231</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Employees</p>
                <p className="text-2xl font-bold text-gray-900">42</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Payments</p>
                <p className="text-2xl font-bold text-gray-900">$8,420</p>
              </div>
              <CreditCard className="h-8 w-8 text-orange-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Reports Generated</p>
                <p className="text-2xl font-bold text-gray-900">28</p>
              </div>
              <FileText className="h-8 w-8 text-purple-500" />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow border p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Settings className="h-6 w-6 text-blue-500" />
              <h2 className="text-lg font-semibold text-gray-900">Administration</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Hotel className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Hotel Settings</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <UserCog className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">User Management</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Analytics</span>
                </div>
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border p-6">
            <div className="flex items-center space-x-3 mb-4">
              <CreditCard className="h-6 w-6 text-green-500" />
              <h2 className="text-lg font-semibold text-gray-900">Financial</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <CreditCard className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Payments</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Billing</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Revenue Reports</span>
                </div>
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Users className="h-6 w-6 text-purple-500" />
              <h2 className="text-lg font-semibold text-gray-900">Staff Management</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Employees</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Clock className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Schedules</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <CreditCard className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Payroll</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}