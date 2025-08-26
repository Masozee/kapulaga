import AppLayout from '@/components/AppLayout';
import { Headphones, MessageSquare, FileText, Shield, Wrench, Package, Users, HelpCircle, Settings } from 'lucide-react';

export default function SupportPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <div className="flex items-center space-x-3">
            <Headphones className="h-8 w-8 text-purple-500" />
            <h1 className="text-3xl font-bold text-gray-900">Support Center</h1>
          </div>
          <p className="text-gray-600 mt-2">Help desk, system management, and documentation</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Open Tickets</p>
                <p className="text-2xl font-bold text-gray-900">12</p>
              </div>
              <MessageSquare className="h-8 w-8 text-red-500" />
            </div>
            <div className="mt-2">
              <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">7 urgent</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <p className="text-2xl font-bold text-green-600">98.5%</p>
              </div>
              <Shield className="h-8 w-8 text-green-500" />
            </div>
            <div className="mt-2">
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">All systems operational</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Knowledge Base</p>
                <p className="text-2xl font-bold text-gray-900">147</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
            <div className="mt-2">
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Articles</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-gray-900">89</p>
              </div>
              <Users className="h-8 w-8 text-purple-500" />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow border p-6">
            <div className="flex items-center space-x-3 mb-4">
              <HelpCircle className="h-6 w-6 text-blue-500" />
              <h2 className="text-lg font-semibold text-gray-900">Help Desk</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <MessageSquare className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium">Support Tickets</span>
                  </div>
                  <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">7</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <MessageSquare className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Live Chat</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Knowledge Base</span>
                </div>
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Settings className="h-6 w-6 text-green-500" />
              <h2 className="text-lg font-semibold text-gray-900">System</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Shield className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">System Health</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Wrench className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Maintenance</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Package className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Backups</span>
                </div>
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border p-6">
            <div className="flex items-center space-x-3 mb-4">
              <FileText className="h-6 w-6 text-purple-500" />
              <h2 className="text-lg font-semibold text-gray-900">Documentation</h2>
            </div>
            <div className="space-y-3">
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">User Guides</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">API Documentation</span>
                </div>
              </button>
              <button className="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">Training Materials</span>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Recent Support Activity */}
        <div className="bg-white rounded-lg shadow border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Support Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border-l-4 border-red-500">
              <div className="flex items-center space-x-3">
                <MessageSquare className="h-5 w-5 text-red-500" />
                <div>
                  <p className="text-sm font-medium">High Priority: Login system down</p>
                  <p className="text-xs text-gray-600">Ticket #1247 • Reported by Front Desk</p>
                </div>
              </div>
              <span className="text-xs text-red-600 font-medium">2 mins ago</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
              <div className="flex items-center space-x-3">
                <Wrench className="h-5 w-5 text-yellow-500" />
                <div>
                  <p className="text-sm font-medium">Scheduled maintenance completed</p>
                  <p className="text-xs text-gray-600">Database optimization • 02:00 - 04:00 AM</p>
                </div>
              </div>
              <span className="text-xs text-yellow-600 font-medium">3 hours ago</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium">New user guide published</p>
                  <p className="text-xs text-gray-600">&ldquo;How to manage guest check-ins&rdquo;</p>
                </div>
              </div>
              <span className="text-xs text-green-600 font-medium">1 day ago</span>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg shadow border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">Database Server</span>
              </div>
              <span className="text-xs text-green-600">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">Web Application</span>
              </div>
              <span className="text-xs text-green-600">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium">Payment Gateway</span>
              </div>
              <span className="text-xs text-green-600">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-sm font-medium">Email Service</span>
              </div>
              <span className="text-xs text-yellow-600">Degraded</span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}