'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import * as Separator from '@radix-ui/react-separator';
import * as Tooltip from '@radix-ui/react-tooltip';
import {
  Building2,
  Users,
  Headphones,
  Hotel,
  Calendar,
  CreditCard,
  FileText,
  Settings,
  UserCheck,
  Bed,
  DoorOpen,
  Package,
  UserCog,
  Clock,
  TrendingUp,
  HelpCircle,
  Wrench,
  Shield,
  Home,
  User
} from 'lucide-react';

interface MenuItem {
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  badge?: string;
}

const Sidebar = () => {
  const pathname = usePathname();

  const mainNavItems: MenuItem[] = [
    { name: 'Dashboard', icon: Home, href: '/' },
  ];

  const frontlineActions: MenuItem[] = [
    { name: 'Bookings', icon: Calendar, href: '/bookings', badge: '12' },
    { name: 'Room Status', icon: Bed, href: '/rooms' },
    { name: 'Guest Profiles', icon: Users, href: '/guests' },
    { name: 'Complaints', icon: HelpCircle, href: '/complaints', badge: '5' },
    { name: 'Housekeeping', icon: Package, href: '/housekeeping', badge: '8' },
    { name: 'Maintenance', icon: Wrench, href: '/maintenance' },
    { name: 'Payments', icon: CreditCard, href: '/payments' },
    { name: 'Reports', icon: FileText, href: '/reports' },
  ];

  const bottomActions: MenuItem[] = [
    { name: 'Settings', icon: Settings, href: '/settings' },
    { name: 'Profile', icon: User, href: '/profile' },
  ];

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  return (
    <Tooltip.Provider delayDuration={300}>
      <div className="w-20 bg-white shadow flex flex-col">
        {/* Header */}
        <div className="p-4">
          <div className="flex items-center justify-center">
            <div className="w-10 h-10 bg-gray-100 flex items-center justify-center">
              <Hotel className="h-6 w-6 text-gray-600" />
            </div>
          </div>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          <div className="space-y-2 px-2">
            {mainNavItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <Tooltip.Root key={item.href}>
                  <Tooltip.Trigger asChild>
                    <Link
                      href={item.href}
                      className={`relative flex items-center justify-center w-16 h-14 transition-all duration-200 group ${
                        active
                          ? 'shadow-sm'
                          : 'hover:bg-gray-100'
                      }`}
                    >
                      <div className={`w-10 h-10 flex items-center justify-center transition-transform group-hover:scale-110 ${
                        active ? 'bg-[#005357]' : 'bg-gray-100'
                      }`}>
                        <Icon className={`h-6 w-6 ${
                          active ? 'text-white' : 'text-gray-600'
                        }`} />
                      </div>
                      {item.badge && (
                        <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs flex items-center justify-center">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  </Tooltip.Trigger>
                  <Tooltip.Portal>
                    <Tooltip.Content
                      side="right"
                      sideOffset={12}
                      className="bg-gray-900 text-white px-2 py-1 text-sm shadow-lg z-50"
                    >
                      {item.name}
                      <Tooltip.Arrow className="fill-gray-900" />
                    </Tooltip.Content>
                  </Tooltip.Portal>
                </Tooltip.Root>
              );
            })}
          </div>

          <Separator.Root className="my-4 mx-2 bg-gray-200 h-px" />

          {/* Frontline Operations */}
          <div className="space-y-1 px-2">
            {frontlineActions.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <Tooltip.Root key={item.href}>
                  <Tooltip.Trigger asChild>
                    <Link
                      href={item.href}
                      className={`relative flex items-center justify-center w-16 h-12 transition-all duration-200 group ${
                        active
                          ? ''
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className={`w-8 h-8 flex items-center justify-center transition-transform group-hover:scale-110 ${
                        active ? 'bg-[#005357]' : 'bg-gray-100'
                      }`}>
                        <Icon className={`h-5 w-5 ${
                          active ? 'text-white' : 'text-gray-600'
                        }`} />
                      </div>
                      {item.badge && (
                        <span className="absolute -top-0.5 -right-0.5 h-4 w-4 bg-red-500 text-white text-xs flex items-center justify-center">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  </Tooltip.Trigger>
                  <Tooltip.Portal>
                    <Tooltip.Content
                      side="right"
                      sideOffset={12}
                      className="bg-gray-900 text-white px-2 py-1 text-sm shadow-lg z-50"
                    >
                      {item.name}
                      <Tooltip.Arrow className="fill-gray-900" />
                    </Tooltip.Content>
                  </Tooltip.Portal>
                </Tooltip.Root>
              );
            })}
          </div>
        </nav>

        {/* Bottom Actions */}
        <div className="p-2">
          <div className="space-y-1">
            {bottomActions.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <Tooltip.Root key={item.href}>
                  <Tooltip.Trigger asChild>
                    <Link
                      href={item.href}
                      className={`relative flex items-center justify-center w-16 h-12 transition-all duration-200 group ${
                        active
                          ? ''
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className={`w-8 h-8 flex items-center justify-center transition-transform group-hover:scale-110 ${
                        active ? 'bg-[#005357]' : 'bg-gray-100'
                      }`}>
                        <Icon className={`h-5 w-5 ${
                          active ? 'text-white' : 'text-gray-600'
                        }`} />
                      </div>
                    </Link>
                  </Tooltip.Trigger>
                  <Tooltip.Portal>
                    <Tooltip.Content
                      side="right"
                      sideOffset={12}
                      className="bg-gray-900 text-white px-2 py-1 text-sm shadow-lg z-50"
                    >
                      {item.name}
                      <Tooltip.Arrow className="fill-gray-900" />
                    </Tooltip.Content>
                  </Tooltip.Portal>
                </Tooltip.Root>
              );
            })}
          </div>
        </div>
      </div>
    </Tooltip.Provider>
  );
};

export default Sidebar;