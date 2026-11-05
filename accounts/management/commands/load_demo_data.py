from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserRole
from challenges.models import ChallengeCategory, Challenge, ChallengeStatus, ChallengePriority
from solutions.models import SolutionProposal, SolutionVote, DiscussionComment
from collaboration.models import ProjectTeam, TeamMembership, TeamRole, MembershipStatus, ProjectTask, TaskStatus, ProjectMilestone
from partnerships.models import OrganizationProfile, OrganizationType, PartnershipRequest, PartnershipStatus, SponsoredChallenge
from impact.models import ImpactReport

User = get_user_model()


class Command(BaseCommand):
    help = "Loads safe, realistic demonstration data clearly tagged as [DEMO]."

    def handle(self, *args, **kwargs):
        self.stdout.write("Populating SocioSolve demonstration data...")

        # 1. Categories
        categories_data = [
            ("Water Conservation", "water-conservation", "Solutions for clean drinking water, leak prevention, rainwater harvesting, and industrial wastewater treatment.", "bi-droplet"),
            ("Environment & Climate", "environment-climate", "Reforestation, biodiversity protection, renewable energy, and carbon offset initiatives.", "bi-tree"),
            ("Education & Literacy", "education-literacy", "Equal access to quality learning, STEM kits, digital literacy, and community libraries.", "bi-book"),
            ("Healthcare & Sanitation", "healthcare-sanitation", "Public hygiene, maternal wellness, community clinics, and disease prevention.", "bi-heart-pulse"),
            ("Waste Management & Recycling", "waste-management", "Zero-waste programs, plastic circular economy, organic composting, and e-waste collection.", "bi-recycle"),
            ("Public Safety & Infrastructure", "public-safety", "Street lighting, pedestrian road safety, flood barriers, and emergency preparedness.", "bi-shield-check"),
            ("Sustainable Transportation", "transportation", "Bike-sharing networks, electric community shuttles, and accessible public transit.", "bi-bicycle"),
            ("Social Welfare & Equality", "social-welfare", "Food rescue banks, homeless outreach, youth mentoring, and inclusive digital accessibility.", "bi-people"),
        ]

        cats = {}
        for name, slug, desc, icon in categories_data:
            cat, _ = ChallengeCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'icon_class': icon}
            )
            cats[slug] = cat
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(cats)} categories."))

        # 2. Users (all roles)
        users_data = [
            ("admin", "admin@sociosolve.org", "Admin", "User", UserRole.ADMINISTRATOR, "SocioSolve Foundation", "Platform Administrator", "System Architecture, Django, Moderation", "Social Impact, Open Tech", "Global", True),
            ("maya_student", "maya@mit.edu", "Maya", "Lin", UserRole.STUDENT, "MIT Environmental Engineering", "Senior undergraduate passionate about decentralized water purification.", "Python, IoT Sensors, Water Engineering, Circuit Design", "Water Conservation, IoT, Environmental Tech", "Cambridge, MA", False),
            ("dr_roberts", "roberts@cambridge.ac.uk", "Dr. Arthur", "Roberts", UserRole.UNIVERSITY, "Cambridge Global Challenges Lab", "Professor of Sustainable Resource Management and community lab director.", "Research Methodology, Environmental Policy, Grants, Life-Cycle Analysis", "Clean Water, Renewable Energy, Circular Economy", "Cambridge, UK", False),
            ("sarah_citizen", "sarah.m@austincommunity.org", "Sarah", "Miller", UserRole.CITIZEN, "Austin Community Action Board", "Neighborhood community organizer and youth mentor.", "Community Mobilization, Public Relations, Grassroots Organizing", "Education Access, Public Safety, Urban Gardening", "Austin, TX", False),
            ("greentech_corp", "partnerships@greentechcorp.com", "Elena", "Vance", UserRole.COMPANY, "GreenTech Solutions Corp", "Corporate sustainability director focused on ESG community partnerships.", "Corporate Grants, Solar Energy, Supply Chain, ESG", "Clean Tech, Renewable Energy, Waste Recycling", "San Francisco, CA", False),
            ("cleanwater_ngo", "info@cleanwaterfoundation.org", "Tariq", "Hassan", UserRole.NGO, "Global Clean Water Trust", "Field director implementing community water filtration across semi-arid regions.", "Water Filtration, Field Logistics, Community Training", "Water Security, Public Health, Sanitation", "Nairobi, Kenya", False),
        ]

        users = {}
        for username, email, first, last, role, org, bio, skills, interests, loc, is_staff in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'role': role,
                    'organization_name': org,
                    'bio': bio,
                    'skills': skills,
                    'interests': interests,
                    'location': loc,
                    'is_staff': is_staff,
                    'is_superuser': is_staff,
                }
            )
            if created or not user.has_usable_password():
                user.set_password("SocioSolve2026!")
                user.save()
            users[username] = user
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(users)} demo users (Password: SocioSolve2026!)."))

        # 3. Organization Profiles
        OrganizationProfile.objects.get_or_create(
            user=users['dr_roberts'],
            defaults={
                'official_name': "Cambridge Global Challenges Lab",
                'org_type': OrganizationType.UNIVERSITY,
                'headquarters': "Cambridge, UK",
                'established_year': 1880,
                'mission_statement': "Fostering academic research into low-cost decentralized water and climate technologies.",
                'focus_areas': "Water Purification, Solar Thermal, Ecological Economics",
                'resources_available': "Access to environmental testing labs, faculty advisors, student internship credits.",
                'website': "https://www.cam.ac.uk",
                'verified': True,
            }
        )

        OrganizationProfile.objects.get_or_create(
            user=users['greentech_corp'],
            defaults={
                'official_name': "GreenTech Solutions Corp",
                'org_type': OrganizationType.COMPANY,
                'headquarters': "San Francisco, CA",
                'established_year': 2012,
                'mission_statement': "Investing corporate resources and engineering expertise into community environmental resilience.",
                'focus_areas': "Smart Grid, Solar Energy, Water Monitoring",
                'resources_available': "$5,000 community mini-grants, engineering mentorship, hardware component donations.",
                'website': "https://greentech-example.org",
                'verified': True,
            }
        )

        OrganizationProfile.objects.get_or_create(
            user=users['cleanwater_ngo'],
            defaults={
                'official_name': "Global Clean Water Trust",
                'org_type': OrganizationType.NGO,
                'headquarters': "Nairobi, Kenya",
                'established_year': 2008,
                'mission_statement': "Empowering underserved communities through sustainable clean water infrastructure.",
                'focus_areas': "Deep Boreholes, Slow Sand Filters, Hygiene Workshops",
                'resources_available': "Field operators, volunteer teams, supply chain access for PVC filtration media.",
                'website': "https://cleanwater-example.org",
                'verified': True,
            }
        )

        # 4. Challenges (Clearly marked as [DEMO])
        c1, _ = Challenge.objects.get_or_create(
            slug="water-wastage-dormitory-tanks-demo",
            defaults={
                'title': "[DEMO] Chronic Water Wastage From Overhead Dormitory Tanks",
                'description': "Across campus residential blocks, mechanical float valves frequently fail on the 10,000-liter rooftop storage tanks. This causes thousands of gallons of treated drinking water to overflow continuously into storm drains every morning before maintenance responds. Residents suffer intermittent pressure while campus water bills surge.",
                'category': cats['water-conservation'],
                'location': "North Campus Residences, Quad B",
                'affected_community': "2,400 on-campus students and residential facilities staff",
                'status': ChallengeStatus.IN_PROGRESS,
                'priority': ChallengePriority.HIGH,
                'creator': users['maya_student'],
                'views_count': 142,
                'moderation_status': 'approved',
                'ai_analysis_cache': {
                    "suggested_category": "Water Conservation",
                    "potential_root_causes": [
                        "Aging mechanical ball-float valves susceptible to mineral scaling and friction lockup",
                        "Absence of electronic high-water shutoff interlocks linked to pump motors",
                        "Delayed maintenance reporting cycle between students and facility managers"
                    ],
                    "affected_stakeholders": [
                        "Student dorm residents experiencing water shortages during peak evening hours",
                        "Campus facility operations and plumbing maintenance teams",
                        "University sustainability office managing municipal water consumption quotas"
                    ],
                    "suggested_priority": "high",
                    "priority_explanation": "Continuous loss of municipal potable water incurs heavy institutional utility costs and undermines university net-zero water sustainability targets.",
                    "missing_information": [
                        "Specific flow-rate of municipal pumps feeding the header tanks",
                        "Availability of Wi-Fi or LoRaWAN coverage on the dormitory rooftops for IoT telemetry"
                    ],
                    "disclaimer": "AI-generated recommendation. Requires local human review and verification."
                }
            }
        )

        c2, _ = Challenge.objects.get_or_create(
            slug="riverside-plastic-clogging-canal-demo",
            defaults={
                'title': "[DEMO] Single-Use Plastic Waste Choking East River Drainage Canal",
                'description': "During seasonal downpours, non-biodegradable food containers, plastic bottles, and shopping bags wash down the commercial boulevard directly into the East River drainage canal. This causes flash flooding in the adjacent low-income neighborhood and discharges toxic microplastics into the downstream marshland reserve.",
                'category': cats['waste-management'],
                'location': "East River Canal & 4th Avenue Basin",
                'affected_community': "5,000 neighborhood residents and local coastal fishermen",
                'status': ChallengeStatus.OPEN,
                'priority': ChallengePriority.CRITICAL,
                'creator': users['sarah_citizen'],
                'views_count': 98,
                'moderation_status': 'approved',
            }
        )

        c3, _ = Challenge.objects.get_or_create(
            slug="digital-literacy-underprivileged-youth-demo",
            defaults={
                'title': "[DEMO] Digital Literacy & Coding Access Gap for Rural Middle Schools",
                'description': "Three regional middle schools have obsolete computer labs with no reliable internet or modern STEM curriculum. Eighth graders are advancing to secondary school with zero foundational exposure to coding, digital safety, or computer literacy, widening the rural-urban educational divide.",
                'category': cats['education-literacy'],
                'location': "Greenfield District Rural School Cluster",
                'affected_community': "450 public middle school students",
                'status': ChallengeStatus.RESOLVED,
                'priority': ChallengePriority.MEDIUM,
                'creator': users['dr_roberts'],
                'views_count': 210,
                'moderation_status': 'approved',
            }
        )

        # 5. Solution Proposals
        p1, _ = SolutionProposal.objects.get_or_create(
            challenge=c1,
            title="[DEMO] Dual Ultrasonic IoT Water Level Sensors with Automated Solenoid Cutoff",
            defaults={
                'author': users['maya_student'],
                'summary': "Install solar-powered ultrasonic distance sensors above the dormitory tanks connected to ESP32 microcontrollers. When water level exceeds 92%, an electronic relay closes the motorized supply valve and sounds a dashboard alert.",
                'detailed_plan': "Phase 1: Measure tank dimensions and calibrate JSN-SR04T waterproof ultrasonic sensors.\nPhase 2: Assemble solar-recharged ESP32 modules transmitting via campus Wi-Fi.\nPhase 3: Wire inline brass motorized solenoid valves into the main pump feed line.\nPhase 4: Build a real-time web telemetry dashboard for campus facility operators.",
                'resources_needed': "2x JSN-SR04T ultrasonic sensors, 1x ESP32 microcontroller, 1x 12V motorized ball valve, 10W mini solar panel, weatherproof enclosure.",
                'estimated_timeline': "3 weeks",
                'estimated_budget': "$180 per tank",
                'status': 'accepted',
                'upvotes_count': 18,
            }
        )

        p2, _ = SolutionProposal.objects.get_or_create(
            challenge=c1,
            title="[DEMO] Overflow Redirection into Native Flora Rain Garden",
            defaults={
                'author': users['sarah_citizen'],
                'summary': "Construct a passive PVC overflow bypass pipe that routes inadvertent tank spills into a tiered native rain garden on the dormitory lawn instead of the storm sewer.",
                'detailed_plan': "Install 3-inch PVC downspout extensions to direct overflow into gravel drainage swales planted with water-tolerant native perennial sedges and irises.",
                'resources_needed': "PVC piping, gravel, native wetland plants, garden spades, student volunteer labor.",
                'estimated_timeline': "2 weekends",
                'estimated_budget': "$250 total",
                'status': 'proposed',
                'upvotes_count': 9,
            }
        )

        # 6. Votes
        SolutionVote.objects.get_or_create(proposal=p1, user=users['maya_student'])
        SolutionVote.objects.get_or_create(proposal=p1, user=users['dr_roberts'])
        SolutionVote.objects.get_or_create(proposal=p1, user=users['sarah_citizen'])
        SolutionVote.objects.get_or_create(proposal=p1, user=users['greentech_corp'])
        p1.update_upvotes_count()

        SolutionVote.objects.get_or_create(proposal=p2, user=users['sarah_citizen'])
        SolutionVote.objects.get_or_create(proposal=p2, user=users['cleanwater_ngo'])
        p2.update_upvotes_count()

        # 7. Comments
        DiscussionComment.objects.get_or_create(
            challenge=c1,
            author=users['dr_roberts'],
            content="Our Cambridge engineering workshop can donate two tested ultrasonic transceivers for this prototype. Let us know if you need PCB etching assistance."
        )
        DiscussionComment.objects.get_or_create(
            proposal=p1,
            author=users['greentech_corp'],
            content="GreenTech Solutions can fund the commercial brass ball valves through our student innovation micro-grant program."
        )

        # 8. Project Team
        team1, _ = ProjectTeam.objects.get_or_create(
            challenge=c1,
            name="[DEMO] Dorm Water Guardians",
            defaults={
                'proposal': p1,
                'description': "Cross-disciplinary engineering and facilities student coalition deploying smart telemetry to halt dormitory tank overflow.",
                'created_by': users['maya_student'],
                'is_active': True,
            }
        )

        TeamMembership.objects.get_or_create(
            team=team1,
            user=users['maya_student'],
            defaults={'role': TeamRole.LEAD, 'status': MembershipStatus.ACCEPTED, 'join_message': 'Project founder and lead developer.'}
        )
        TeamMembership.objects.get_or_create(
            team=team1,
            user=users['dr_roberts'],
            defaults={'role': TeamRole.ADVISOR, 'status': MembershipStatus.ACCEPTED, 'join_message': 'Faculty technical advisor on telemetry reliability.'}
        )
        TeamMembership.objects.get_or_create(
            team=team1,
            user=users['sarah_citizen'],
            defaults={'role': TeamRole.CONTRIBUTOR, 'status': MembershipStatus.ACCEPTED, 'join_message': 'Volunteer community outreach and student survey lead.'}
        )

        # 9. Project Tasks
        now = timezone.now().date()
        ProjectTask.objects.get_or_create(
            team=team1,
            title="Breadboard IoT Sensor and Solenoid Relay",
            defaults={
                'description': "Flash ESP32 firmware and verify cutoff trigger at 90% water depth threshold.",
                'assigned_to': users['maya_student'],
                'created_by': users['maya_student'],
                'status': TaskStatus.DONE,
                'priority': 'high',
                'due_date': now - timedelta(days=5),
            }
        )
        ProjectTask.objects.get_or_create(
            team=team1,
            title="Inspect Rooftop Tank Mounting Brackets",
            defaults={
                'description': "Survey tank manhole access and measure pipe threading for solenoid installation.",
                'assigned_to': users['sarah_citizen'],
                'created_by': users['maya_student'],
                'status': TaskStatus.IN_PROGRESS,
                'priority': 'medium',
                'due_date': now + timedelta(days=3),
            }
        )
        ProjectTask.objects.get_or_create(
            team=team1,
            title="Finalize Facilities Maintenance API Webhook",
            defaults={
                'description': "Connect automated alert notification to campus facility management email gateway.",
                'assigned_to': users['maya_student'],
                'created_by': users['maya_student'],
                'status': TaskStatus.TODO,
                'priority': 'medium',
                'due_date': now + timedelta(days=10),
            }
        )

        # 10. Milestones
        ProjectMilestone.objects.get_or_create(
            team=team1,
            title="Prototype Hardware Lab Sign-Off",
            defaults={
                'description': "Pass sensor waterproof immersion test and fail-safe relay operation.",
                'target_date': now - timedelta(days=4),
                'is_completed': True,
                'completed_date': now - timedelta(days=3),
                'created_by': users['maya_student'],
            }
        )
        ProjectMilestone.objects.get_or_create(
            team=team1,
            title="Rooftop Pilot Deployment on Block B",
            defaults={
                'description': "Full physical installation on 10,000L tank with live telemetry.",
                'target_date': now + timedelta(days=14),
                'is_completed': False,
                'created_by': users['maya_student'],
            }
        )

        # 11. Partnerships & Sponsorship
        PartnershipRequest.objects.get_or_create(
            organization=users['greentech_corp'],
            challenge=c1,
            defaults={
                'team': team1,
                'offered_support': "$1,200 Seed Funding & 2 Senior IoT Mentors",
                'message': "GreenTech would like to sponsor the hardware costs for 5 dormitory tank retrofits and assist with LoRaWAN gateway setup.",
                'status': PartnershipStatus.APPROVED,
            }
        )

        SponsoredChallenge.objects.get_or_create(
            challenge=c1,
            defaults={
                'sponsor': users['greentech_corp'],
                'grant_amount': 2500.00,
                'currency': 'USD',
                'benefits': "Direct prototyping grant, corporate showcase feature at GreenTech Summit, student engineering internship interviews.",
                'application_deadline': now + timedelta(days=30),
                'is_active': True,
            }
        )

        # 12. Impact Reports (Showing Verified vs Estimated!)
        # Report 1 (Verified impact report on resolved Challenge 3)
        ImpactReport.objects.get_or_create(
            challenge=c3,
            title="[DEMO] Greenfield Rural Computer Lab Modernization & STEM Curriculum",
            defaults={
                'reported_by': users['dr_roberts'],
                'summary': "Refurbished 45 desktop workstations with Linux, installed mesh Wi-Fi across 3 rural middle schools, and graduated 450 students through a 12-week introductory Python & Digital Literacy course.",
                'beneficiaries_reached': 450,
                'is_verified': True,  # Officially verified by school district audit
                'metrics_data': {
                    "workstations_donated": 45,
                    "student_graduates": 450,
                    "girls_in_stem_percent": 54,
                    "cost_per_student_usd": 12.50
                },
                'environmental_impact': "Diverted 45 corporate laptops from electronic landfill by refurbishing components.",
                'social_impact': "100% of eighth graders demonstrated basic digital literacy; 8 students won regional science fair awards.",
                'challenges_overcome': "Unstable rural electrical grid mitigated by installing battery-backed surge protectors.",
                'future_sustainability_plan': "School district adopted lab maintenance into annual operational budget."
            }
        )

        # Report 2 (Self-reported preliminary impact on Challenge 1)
        ImpactReport.objects.get_or_create(
            challenge=c1,
            title="[DEMO] Phase 1 Pilot Water Conservation Results (Preliminary)",
            defaults={
                'reported_by': users['maya_student'],
                'team': team1,
                'summary': "Bench testing and single-tank pilot cut overflow events by 95% over the first two weeks of continuous observation.",
                'beneficiaries_reached': 600,
                'is_verified': False,  # Self-reported / preliminary estimate
                'metrics_data': {
                    "estimated_gallons_saved": 45000,
                    "pilot_tanks_equipped": 1,
                    "overflow_alerts_triggered": 14
                },
                'environmental_impact': "Conserved an estimated 45,000 gallons of treated municipal drinking water.",
                'social_impact': "Eliminated dorm resident water outages during morning peak hours.",
                'challenges_overcome': "Addressed sensor condensation with silicone conformal coating.",
                'future_sustainability_plan': "Expanding to all 4 dormitory blocks with GreenTech grant funding."
            }
        )

        self.stdout.write(self.style.SUCCESS("All demonstration data successfully loaded!"))
