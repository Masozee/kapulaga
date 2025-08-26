'use client';

import AppLayout from '@/components/AppLayout';
import { Hotel, TrendingUp, Users, Calendar, Phone, AlertTriangle, Newspaper, ChevronRight, PieChart as PieChartIcon } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, addMonths, subMonths } from 'date-fns';

export default function Home() {
  // Sample data for daily occupation comparison (current vs previous month)
  const occupationData = [
    { day: '1', currentMonth: 142, previousMonth: 151, difference: -9 },
    { day: '2', currentMonth: 138, previousMonth: 148, difference: -10 },
    { day: '3', currentMonth: 145, previousMonth: 156, difference: -11 },
    { day: '4', currentMonth: 149, previousMonth: 154, difference: -5 },
    { day: '5', currentMonth: 134, previousMonth: 147, difference: -13 },
    { day: '6', currentMonth: 156, previousMonth: 159, difference: -3 },
    { day: '7', currentMonth: 148, previousMonth: 153, difference: -5 },
    { day: '8', currentMonth: 139, previousMonth: 152, difference: -13 },
    { day: '9', currentMonth: 152, previousMonth: 158, difference: -6 },
    { day: '10', currentMonth: 147, previousMonth: 155, difference: -8 },
    { day: '11', currentMonth: 143, previousMonth: 149, difference: -6 },
    { day: '12', currentMonth: 155, previousMonth: 160, difference: -5 },
    { day: '13', currentMonth: 141, previousMonth: 154, difference: -13 },
    { day: '14', currentMonth: 150, previousMonth: 157, difference: -7 },
    { day: '15', currentMonth: 146, previousMonth: 151, difference: -5 },
    { day: '16', currentMonth: 144, previousMonth: 156, difference: -12 },
    { day: '17', currentMonth: 151, previousMonth: 159, difference: -8 },
    { day: '18', currentMonth: 148, previousMonth: 153, difference: -5 },
    { day: '19', currentMonth: 153, previousMonth: 161, difference: -8 },
    { day: '20', currentMonth: 140, previousMonth: 150, difference: -10 },
    { day: '21', currentMonth: 149, previousMonth: 158, difference: -9 },
    { day: '22', currentMonth: 145, previousMonth: 152, difference: -7 },
    { day: '23', currentMonth: 147, previousMonth: 155, difference: -8 },
    { day: '24', currentMonth: 152, previousMonth: 159, difference: -7 },
    { day: '25', currentMonth: 144, previousMonth: 151, difference: -7 },
    { day: '26', currentMonth: 148, previousMonth: 156, difference: -8 },
    { day: '27', currentMonth: 150, previousMonth: 157, difference: -7 },
    { day: '28', currentMonth: 146, previousMonth: 154, difference: -8 },
    { day: '29', currentMonth: 154, previousMonth: 162, difference: -8 },
    { day: '30', currentMonth: 149, previousMonth: 155, difference: -6 }
  ];

  // Sample news data
  const newsItems = [
    {
      title: 'New safety protocols implemented',
      description: 'Updated check-in procedures for guest safety',
      time: '2 hours ago'
    },
    {
      title: 'Staff training session scheduled',
      description: 'Customer service training on Friday 3 PM',
      time: '4 hours ago'
    },
    {
      title: 'Maintenance completed',
      description: 'HVAC system maintenance finished',
      time: '1 day ago'
    }
  ];

  // Emergency contacts
  const emergencyContacts = [
    { label: 'Security', number: '+1 (555) 0123' },
    { label: 'Maintenance', number: '+1 (555) 0124' },
    { label: 'Management', number: '+1 (555) 0125' },
    { label: 'Medical', number: '+1 (555) 0126' }
  ];

  // Demographic visitor data for pie chart
  const demographicData = [
    { name: 'Business Travelers', value: 45, color: '#005357' },
    { name: 'Leisure Tourists', value: 35, color: '#2baf6a' },
    { name: 'Conference Attendees', value: 12, color: '#60a5fa' },
    { name: 'Other', value: 8, color: '#a1a1aa' }
  ];

  // Calendar helper functions
  const currentDate = new Date();
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });
  const today = new Date();

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Kapulaga Hotel Management</h1>
            <p className="text-gray-600 mt-2">Welcome to your hotel management dashboard</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white shadow">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Total Rooms</h3>
                  <p className="text-sm text-gray-100 mt-1">Available hotel capacity</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <Hotel className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">156</div>
                <div className="text-sm text-gray-600">total rooms</div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Occupancy Rate</h3>
                  <p className="text-sm text-gray-100 mt-1">Current room utilization</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">89%</div>
                <div className="text-sm text-gray-600">occupancy rate</div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Active Guests</h3>
                  <p className="text-sm text-gray-100 mt-1">Currently checked in</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <Users className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">324</div>
                <div className="text-sm text-gray-600">active guests</div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Today's Check-ins</h3>
                  <p className="text-sm text-gray-100 mt-1">Scheduled arrivals</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <Calendar className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="text-center">
                <div className="text-3xl font-bold text-[#005357] mb-2">23</div>
                <div className="text-sm text-gray-600">check-ins today</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow">
          <div className="p-6 bg-[#005357] text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-white">Quick Actions</h3>
                <p className="text-sm text-gray-100 mt-1">Common hotel management tasks</p>
              </div>
            </div>
          </div>
          <div className="p-4 bg-gray-50">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="p-4 text-left bg-white hover:bg-gray-50 transition-colors rounded">
                <h3 className="font-medium text-gray-900">New Reservation</h3>
                <p className="text-sm text-gray-600 mt-1">Create a new booking for a guest</p>
              </button>
              <button className="p-4 text-left bg-white hover:bg-gray-50 transition-colors rounded">
                <h3 className="font-medium text-gray-900">Check-in Guest</h3>
                <p className="text-sm text-gray-600 mt-1">Process guest check-in</p>
              </button>
              <button className="p-4 text-left bg-white hover:bg-gray-50 transition-colors rounded">
                <h3 className="font-medium text-gray-900">Room Status</h3>
                <p className="text-sm text-gray-600 mt-1">Update room availability</p>
              </button>
            </div>
          </div>
        </div>

        {/* Bento Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6">
          {/* Demographic Visitor Chart - 1/3 width */}
          <div className="bg-white shadow md:col-span-1 lg:col-span-2">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Visitor Demographics</h3>
                  <p className="text-sm text-gray-100 mt-1">Guest type distribution</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <PieChartIcon className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="h-48 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={demographicData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {demographicData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 space-y-2">
                {demographicData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3" style={{ backgroundColor: item.color }}></div>
                      <span className="text-gray-700">{item.name}</span>
                    </div>
                    <span className="text-gray-900 font-medium">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Daily Occupation Chart - 2/3 width */}
          <div className="bg-white shadow md:col-span-2 lg:col-span-4">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Daily Occupation Comparison</h3>
                  <p className="text-sm text-gray-100 mt-1">Current vs Previous Month Performance</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="bg-gray-50">
              <div className="p-4">
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={occupationData} barCategoryGap="20%">
                      <XAxis 
                        dataKey="day" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fontSize: 10, fill: '#6B7280' }}
                        interval={2}
                      />
                      <YAxis 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fontSize: 10, fill: '#6B7280' }}
                        domain={[130, 165]}
                      />
                      <Bar 
                        dataKey="previousMonth" 
                        fill="#2baf6a" 
                        radius={[2, 2, 0, 0]}
                        name="Previous Month"
                      />
                      <Bar 
                        dataKey="currentMonth" 
                        fill="#005357" 
                        radius={[2, 2, 0, 0]}
                        name="Current Month"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex items-center justify-center mt-2">
                  <div className="flex items-center space-x-6 text-xs">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-[#005357]"></div>
                      <span className="text-gray-600">Current Month</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-[#2baf6a]"></div>
                      <span className="text-gray-600">Previous Month</span>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <span className="text-red-600 text-xs font-medium">
                        Avg: -7.8 rooms/day
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* News Card - 1/3 width */}
          <div className="bg-white shadow md:col-span-1 lg:col-span-2">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Latest News</h3>
                  <p className="text-sm text-gray-100 mt-1">Hotel updates and announcements</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <Newspaper className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50 space-y-3">
              {newsItems.map((news, index) => (
                <div key={index} className="bg-white p-3 mb-2 last:mb-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 text-sm">{news.title}</h4>
                      <p className="text-xs text-gray-600 mt-1">{news.description}</p>
                      <p className="text-xs text-gray-400 mt-1">{news.time}</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Calendar Card - 1/3 width */}
          <div className="bg-white shadow md:col-span-1 lg:col-span-2">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Calendar</h3>
                  <p className="text-sm text-gray-100 mt-1">{format(currentDate, 'MMMM yyyy')}</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <Calendar className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50">
              <div className="space-y-3">
                <div className="grid grid-cols-7 gap-1 text-xs text-gray-500">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="text-center py-1 font-medium">{day}</div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-1">
                  {Array.from({ length: monthStart.getDay() }).map((_, index) => (
                    <div key={index} className="h-7"></div>
                  ))}
                  {daysInMonth.map(day => (
                    <div
                      key={day.toISOString()}
                      className={`h-7 flex items-center justify-center text-xs cursor-pointer hover:bg-white ${
                        isSameDay(day, today)
                          ? 'bg-[#005357] text-white font-medium'
                          : 'text-gray-700 hover:bg-white'
                      }`}
                    >
                      {format(day, 'd')}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Emergency Contact Card - 1/3 width */}
          <div className="bg-white shadow md:col-span-1 lg:col-span-2">
            <div className="p-6 bg-[#005357] text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white">Emergency Contacts</h3>
                  <p className="text-sm text-gray-100 mt-1">Quick access to essential services</p>
                </div>
                <div className="w-8 h-8 bg-white flex items-center justify-center">
                  <Phone className="h-4 w-4 text-[#005357]" />
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50 space-y-2">
              {emergencyContacts.map((contact, index) => (
                <div key={index} className="bg-white p-3 flex items-center justify-between hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-red-100 flex items-center justify-center">
                      <AlertTriangle className="h-3 w-3 text-red-600" />
                    </div>
                    <span className="font-medium text-gray-900 text-sm">{contact.label}</span>
                  </div>
                  <a href={`tel:${contact.number}`} className="text-sm text-[#005357] hover:underline">
                    {contact.number}
                  </a>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
