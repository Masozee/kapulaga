'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import * as Separator from '@radix-ui/react-separator';
import * as Tooltip from '@radix-ui/react-tooltip';
import {
  Wrench,
  Bed,
  Package,
  MessageSquare,
  ClipboardCheck,
  AlertTriangle,
  Clock,
  Settings,
  User,
  ArrowLeft,
  Headphones,
  CheckSquare,
  ShoppingCart,
  Home,
  Bell,
  FileText
} from 'lucide-react';

interface MenuItem {
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  badge?: string;
}

const SupportSidebar = () => {
  const pathname = usePathname();

  const mainNavItems: MenuItem[] = [
    { name: 'Support Dashboard', icon: Headphones, href: '/support' },
    { name: 'Back to Main', icon: ArrowLeft, href: '/' },
  ];

  const supportActions: MenuItem[] = [
    { name: 'Maintenance', icon: Wrench, href: '/support/maintenance', badge: '3' },
    { name: 'Housekeeping', icon: Bed, href: '/support/housekeeping', badge: '7' },
    { name: 'Amenities Request', icon: Package, href: '/support/amenities', badge: '2' },
    { name: 'Work Orders', icon: ClipboardCheck, href: '/support/workorders' },
    { name: 'Emergency', icon: AlertTriangle, href: '/support/emergency' },
    { name: 'Reports', icon: FileText, href: '/support/reports' },
  ];

  const bottomActions: MenuItem[] = [
    { name: 'Support Settings', icon: Settings, href: '/support/settings' },
    { name: 'Profile', icon: User, href: '/profile' },
  ];

  const isActive = (href: string) => {
    if (href === '/support') return pathname === '/support';
    if (href === '/') return false;
    return pathname.startsWith(href);
  };

  return (
    <Tooltip.Provider delayDuration={300}>
      <div className="w-20 bg-white shadow flex flex-col">
        {/* Header */}
        <div className="p-4">
          <div className="flex items-center justify-center">
            <div className="w-10 h-10 bg-gray-50 flex items-center justify-center p-1">
              <Image
                src="/logo.png"
                alt="Kapulaga Hotel Logo"
                width={32}
                height={32}
                className="object-contain"
              />
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

          {/* Support Operations */}
          <div className="space-y-1 px-2">
            {supportActions.map((item) => {
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

export default SupportSidebar;