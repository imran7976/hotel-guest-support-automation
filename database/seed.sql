-- ==============================================================================
-- AI-Powered Hotel Guest Support Automation System
-- Database Seed Data Script (MySQL 8.0+)
-- ==============================================================================

USE hotel_guest_support;

-- 1. Default Admin User (Password: AdminHotel2025!)
-- bcrypt hash for 'AdminHotel2025!'
INSERT INTO admin_users (email, hashed_password, full_name, role, is_active)
VALUES (
    'admin@grandhotelazure.demo',
    '$2b$12$e80y9m5bA7n.x32yLq7oDuXk5qVjZ8H2R2G9m/3k9L5Y1XvH2kMTe',
    'Front Office Manager',
    'manager',
    TRUE
) ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- 2. Rooms Data
INSERT INTO rooms (room_number, room_type, price_per_night, floor, status, max_occupancy, amenities, description) VALUES
('101', 'Superior King Room', 180.00, 1, 'available', 2, 'King Bed, Free High-Speed Wi-Fi, 55" Smart TV, Rain Shower, Coffee Maker', 'Spacious ground-floor king room overlooking peaceful courtyard gardens.'),
('102', 'Deluxe Twin Room', 160.00, 1, 'available', 2, '2 Twin Beds, Free High-Speed Wi-Fi, 50" Smart TV, Work Desk, Mini Bar', 'Quiet twin room perfect for traveling colleagues or friends.'),
('201', 'Deluxe Ocean View Suite', 320.00, 2, 'occupied', 3, 'King Bed, Private Balcony, Ocean View, Nespresso Machine, Bathtub, Luxury Robes', 'Panoramic ocean view suite with sunset vistas and a private sun terrace.'),
('202', 'Executive King Suite', 290.00, 2, 'available', 2, 'King Bed, Lounge Area, Executive Lounge Access, Ergonomic Workstation, Marble Bath', 'Designed for business travelers needing space and refined comfort.'),
('301', 'Grand Presidential Suite', 650.00, 3, 'available', 4, '2 Master King Bedrooms, Living Room, Dining Area, Kitchenette, Jacuzzi, Butler Service', 'Top floor luxury penthouse offering unparalleled luxury and 360-degree resort views.'),
('302', 'Family Garden Suite', 240.00, 3, 'available', 4, '1 King + 2 Twin Beds, Kids Corner, Double Vanity, Kitchenette', 'Spacious family haven tailored for comfort with child-friendly amenities.')
ON DUPLICATE KEY UPDATE room_type = VALUES(room_type);

-- 3. Guests Data
INSERT INTO guests (first_name, last_name, email, phone, vip_status) VALUES
('John', 'Smith', 'john@example.com', '+1-555-0144', TRUE),
('Emma', 'Watson', 'emma.watson@example.com', '+1-555-0182', FALSE),
('Michael', 'Chang', 'm.chang@example.com', '+1-555-0193', FALSE)
ON DUPLICATE KEY UPDATE first_name = VALUES(first_name);

-- 4. Bookings Data (John Smith booking GAH-78901)
INSERT INTO bookings (booking_reference, guest_id, room_id, check_in_date, check_out_date, number_of_guests, total_amount, status, special_requests) VALUES
('GAH-78901', 1, 3, CURDATE() + INTERVAL 1 DAY, CURDATE() + INTERVAL 4 DAY, 2, 960.00, 'confirmed', 'High floor requested, celebrating anniversary with complimentary fruit basket.'),
('GAH-44210', 2, 1, CURDATE() + INTERVAL 7 DAY, CURDATE() + INTERVAL 10 DAY, 1, 540.00, 'confirmed', 'Late arrival around 10:00 PM.'),
('GAH-11029', 3, 2, CURDATE() - INTERVAL 2 DAY, CURDATE() + INTERVAL 1 DAY, 2, 480.00, 'confirmed', 'Extra feather pillows requested.')
ON DUPLICATE KEY UPDATE booking_reference = VALUES(booking_reference);

-- 5. Hotel Knowledge Base (RAG) Data
INSERT INTO hotel_knowledge (category, title, content, keywords, is_active) VALUES
('check_in_out', 'Standard Check-in and Check-out Times', 
 'Our standard check-in time is 2:00 PM (14:00) and standard check-out time is 11:00 AM (11:00). Guests arriving prior to 2:00 PM are welcome to store luggage complimentary at the Concierge desk and enjoy the pool, lounge, and dining venues.', 
 'check-in, check-out, timing, arrival, departure, early check-in, late check-out, luggage storage', TRUE),

('check_in_out', 'Early Check-in Policy', 
 'Early check-in prior to 2:00 PM is subject to room availability upon arrival. Guaranteed early check-in before 10:00 AM requires booking the room for the preceding night. Please contact reception in advance to place an early check-in notation on your reservation.', 
 'early check-in, morning arrival, guarantee, availability', TRUE),

('check_in_out', 'Late Check-out Policy', 
 'Late check-out until 1:00 PM is complimentary for VIP guests and subject to availability for all guests upon request on the morning of departure. Late check-out between 1:00 PM and 6:00 PM is charged at 50% of the daily room rate. Departures after 6:00 PM incur a full night charge.', 
 'late check-out, departure delay, afternoon, extra charges', TRUE),

('cancellation', 'Cancellation and Refund Policy', 
 'Reservations cancelled at least 48 hours prior to 2:00 PM local hotel time on the arrival date receive a 100% full refund with no penalty. Cancellations within 48 hours of check-in are subject to a fee equal to the first night room charge plus tax. Non-refundable promotional bookings cannot be cancelled or refunded automatically. All refund requests must be verified and authorized by human management.', 
 'cancel, cancellation, refund, penalty, 48 hours, non-refundable, money back', TRUE),

('wifi', 'Wi-Fi Access and Troubleshooting', 
 'Complimentary high-speed Wi-Fi is available across all guest rooms, suites, conference halls, and public spaces. Network Name (SSID): GrandAzure_Guest. Password: AzureGuest2025. If encountering connection difficulty: 1. Forget the network and reconnect. 2. Verify Wi-Fi is toggled on. 3. Visit captive.azurehotel.demo in your browser. 4. If issues persist, dial extension #44 from your room phone for immediate IT concierge assistance.', 
 'wifi, internet, password, ssid, connection, slow, network, trouble', TRUE),

('facilities', 'Swimming Pool and Wellness Spa', 
 'Our heated infinity pool is open daily from 6:00 AM to 10:00 PM. Complimentary cabanas and towel service are available poolside. The Azure Lotus Spa operates daily from 8:00 AM to 9:00 PM, offering deep tissue massage, organic facials, hydrotherapy, and a steam sauna. Reservations are recommended 24 hours in advance.', 
 'pool, swimming pool, hours, spa, massage, sauna, towels, cabana, wellness', TRUE),

('dining', 'Breakfast Buffet and Dining Venues', 
 'The Grand Verandah Restaurant serves an artisanal international breakfast buffet daily: Weekdays from 6:30 AM to 10:30 AM; Weekends and public holidays from 7:00 AM to 11:00 AM. In-room dining (Room Service) is available 24 hours a day by dialing extension #21 from your room phone. Coastal Catch Seafood Grill opens for dinner from 6:00 PM to 11:00 PM.', 
 'breakfast, dining, restaurant, room service, buffet, dinner, hours, food, meals', TRUE),

('facilities', 'Fitness Center and Gym', 
 'Our 24-hour state-of-the-art Fitness Center is located on the 2nd floor, accessible via your active room keycard. Facilities include Technogym treadmills, ellipticals, free weights up to 40kg, resistance machines, and a dedicated yoga/stretching studio.', 
 'gym, fitness, workout, exercise, 24 hours, weights, treadmills', TRUE),

('policies', 'Pet Policy', 
 'Grand Azure Resort warmly welcomes well-behaved domestic dogs and cats up to 15 kg (33 lbs). A one-time non-refundable deep cleaning fee of $75 per stay applies. Pets must remain leashed in public areas and are not permitted inside pool zones or spa facilities.', 
 'pets, dogs, cats, animal, pet fee, rules', TRUE),

('facilities', 'Airport Transfer & Shuttle Service', 
 'We provide luxury private transfers to and from International Airport (40 minutes drive). Private Mercedes Sedan is $85 one-way; Luxury 6-passenger Van is $120 one-way. Complimentary scheduled hourly shuttles depart between 6:00 AM and 10:00 PM. Reservations must be booked at least 6 hours in advance via the Concierge.', 
 'shuttle, airport transfer, transportation, taxi, car service, pickup, dropoff', TRUE),

('policies', 'Smoking Policy and House Rules', 
 'Grand Azure is a 100% non-smoking resort inside all guest rooms, balconies, and enclosed public spaces. Designated outdoor smoking lounges are clearly signposted in the beach promenade and garden courtyard. A $350 deep-cleaning restoration fee is assessed for smoking violations inside rooms.', 
 'smoking, cigarette, vape, fine, non-smoking, rules', TRUE),

('contact', 'Reception & Concierge Contact Information', 
 'Front Desk & Reception: 24/7. Phone: +1-555-0199 (Internal: Dial 0). Concierge Desk: Daily 7:00 AM - 11:00 PM (Internal: Dial 9). Duty Manager Emergency Contact: Internal Dial 911 or visit front desk immediately.', 
 'contact, reception, phone, concierge, manager, help desk, emergency', TRUE)
ON DUPLICATE KEY UPDATE content = VALUES(content);

-- 6. Sample Initial Workflow Log
INSERT INTO workflow_logs (workflow_name, execution_id, trigger_event, status, error_message, payload_json) VALUES
('Guest Inquiry Processing', 'exec_seed_001', 'webhook_inquiry', 'success', NULL, '{"source": "seed_demo", "status": "operational"}'),
('Daily Support Summary', 'exec_seed_002', 'cron_scheduled', 'success', NULL, '{"summary": "Daily audit ran successfully with 0 system errors."}')
ON DUPLICATE KEY UPDATE workflow_name = VALUES(workflow_name);

