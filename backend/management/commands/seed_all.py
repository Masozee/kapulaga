from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Run all seed data commands in the correct order for Indonesian hotel management system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset database before seeding (WARNING: This will delete all data!)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏨 Starting Indonesian Hotel Management System seed data creation...\n')
        )

        if options['reset']:
            self.stdout.write(
                self.style.WARNING('⚠️  Resetting database... This will delete all existing data!')
            )
            # Run migrations to reset the database
            call_command('flush', '--noinput')
            self.stdout.write(self.style.SUCCESS('✅ Database reset completed\n'))

        # Define the correct order for seeding data
        seed_commands = [
            {
                'command': 'seed_rooms',
                'description': '🏠 Creating room types and rooms...',
                'app': 'rooms'
            },
            {
                'command': 'seed_guests', 
                'description': '👥 Creating guests and documents...',
                'app': 'guests'
            },
            {
                'command': 'seed_employees',
                'description': '👨‍💼 Creating departments, employees, and attendance...',
                'app': 'employees'
            },
            {
                'command': 'seed_inventory',
                'description': '📦 Creating inventory categories, suppliers, and stock...',
                'app': 'inventory'
            },
            {
                'command': 'seed_reservations',
                'description': '📅 Creating reservations and room assignments...',
                'app': 'reservations'
            },
            {
                'command': 'seed_checkin',
                'description': '🚪 Creating check-in/check-out records and room keys...',
                'app': 'checkin'
            },
            {
                'command': 'seed_payments',
                'description': '💳 Creating payment methods, bills, and payments...',
                'app': 'payments'
            },
            {
                'command': 'seed_reports',
                'description': '📊 Creating daily, monthly, and occupancy reports...',
                'app': 'reports'
            }
        ]

        total_commands = len(seed_commands)
        successful_commands = 0
        failed_commands = []

        for i, seed_info in enumerate(seed_commands, 1):
            self.stdout.write(f"\n[{i}/{total_commands}] {seed_info['description']}")
            
            try:
                call_command(seed_info['command'])
                successful_commands += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {seed_info['command']} completed successfully")
                )
            except Exception as e:
                failed_commands.append({
                    'command': seed_info['command'], 
                    'error': str(e),
                    'app': seed_info['app']
                })
                self.stdout.write(
                    self.style.ERROR(f"❌ {seed_info['command']} failed: {str(e)}")
                )

        # Print summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎉 SEED DATA CREATION SUMMARY"))
        self.stdout.write("="*60)
        
        self.stdout.write(f"✅ Successful commands: {successful_commands}/{total_commands}")
        
        if failed_commands:
            self.stdout.write(f"❌ Failed commands: {len(failed_commands)}")
            for failed in failed_commands:
                self.stdout.write(
                    self.style.ERROR(f"   - {failed['command']} ({failed['app']} app): {failed['error']}")
                )
            
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  Some commands failed. You may need to run them individually after fixing dependencies."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n🎊 All seed data created successfully!\n"
                    "Your Indonesian hotel management system is ready with comprehensive test data.\n"
                )
            )
            
            # Print some useful statistics
            self.stdout.write("📊 SYSTEM OVERVIEW:")
            try:
                from apps.rooms.models import Room, RoomType
                from apps.guests.models import Guest
                from apps.reservations.models import Reservation
                from apps.employees.models import Employee, Department
                from apps.payments.models import Payment
                
                self.stdout.write(f"   🏠 Rooms: {Room.objects.count()} rooms across {RoomType.objects.count()} room types")
                self.stdout.write(f"   👥 Guests: {Guest.objects.count()} registered guests")
                self.stdout.write(f"   📅 Reservations: {Reservation.objects.count()} total reservations")
                self.stdout.write(f"   👨‍💼 Staff: {Employee.objects.count()} employees in {Department.objects.count()} departments")
                self.stdout.write(f"   💰 Payments: {Payment.objects.count()} payment transactions")
                
                # Calculate occupancy
                occupied_rooms = Room.objects.filter(status='OCCUPIED').count()
                total_rooms = Room.objects.count()
                occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
                self.stdout.write(f"   🏨 Current Occupancy: {occupancy_rate:.1f}% ({occupied_rooms}/{total_rooms} rooms)")
                
            except ImportError:
                self.stdout.write("   📊 Statistics not available (some apps may not be ready)")

        self.stdout.write("\n" + "="*60)
        
        if not failed_commands:
            self.stdout.write(
                self.style.SUCCESS(
                    "🚀 Ready to start! You can now:\n"
                    "   • Access Django Admin to see all the seeded data\n"
                    "   • Test the hotel management functionality\n"
                    "   • Use the API endpoints for reservations, guests, etc.\n"
                )
            )