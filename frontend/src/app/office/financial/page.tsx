import OfficeLayout from '@/components/OfficeLayout';
import { DollarSign, CreditCard, TrendingUp, FileText } from 'lucide-react';

export default function FinancialPage() {
  return (
    <OfficeLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Financial Management</h1>
          <p className="text-gray-600 mt-2">Revenue tracking, payments, and financial reporting</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white shadow border">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Total Revenue</h3>
                  <p className="text-sm text-gray-600 mt-1">This month</p>
                </div>
                <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                  <DollarSign className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">$245,680</div>
                <div className="text-sm text-gray-600">monthly revenue</div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow border">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Outstanding</h3>
                  <p className="text-sm text-gray-600 mt-1">Pending payments</p>
                </div>
                <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                  <CreditCard className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">$8,420</div>
                <div className="text-sm text-gray-600">outstanding</div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow border">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Profit Margin</h3>
                  <p className="text-sm text-gray-600 mt-1">Net profit percentage</p>
                </div>
                <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">32.5%</div>
                <div className="text-sm text-gray-600">profit margin</div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow border">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Invoices</h3>
                  <p className="text-sm text-gray-600 mt-1">Generated this month</p>
                </div>
                <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                  <FileText className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">156</div>
                <div className="text-sm text-gray-600">invoices</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white shadow border">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Payment Processing</h3>
                  <p className="text-sm text-gray-600 mt-1">Transaction management</p>
                </div>
                <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                  <CreditCard className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50 space-y-3">
              <button className="w-full p-3 text-left bg-white hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-900">Process Payments</h3>
                <p className="text-sm text-gray-600 mt-1">Handle guest payments and billing</p>
              </button>
              <button className="w-full p-3 text-left bg-white hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-900">Refund Management</h3>
                <p className="text-sm text-gray-600 mt-1">Process refunds and cancellations</p>
              </button>
              <button className="w-full p-3 text-left bg-white hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-900">Payment History</h3>
                <p className="text-sm text-gray-600 mt-1">View transaction history</p>
              </button>
            </div>
          </div>

          <div className="bg-white shadow border">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Financial Reports</h3>
                  <p className="text-sm text-gray-600 mt-1">Revenue and expense reporting</p>
                </div>
                <div className="w-8 h-8 bg-[#005357] flex items-center justify-center">
                  <FileText className="h-4 w-4 text-white" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50 space-y-3">
              <button className="w-full p-3 text-left bg-white hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-900">Revenue Reports</h3>
                <p className="text-sm text-gray-600 mt-1">Monthly and annual revenue analysis</p>
              </button>
              <button className="w-full p-3 text-left bg-white hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-900">Expense Tracking</h3>
                <p className="text-sm text-gray-600 mt-1">Monitor operational expenses</p>
              </button>
              <button className="w-full p-3 text-left bg-white hover:bg-gray-50 transition-colors">
                <h3 className="font-medium text-gray-900">Tax Reports</h3>
                <p className="text-sm text-gray-600 mt-1">Generate tax-ready financial reports</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </OfficeLayout>
  );
}