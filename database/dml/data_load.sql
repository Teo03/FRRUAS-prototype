SET search_path TO project;

TRUNCATE TABLE reservations RESTART IDENTITY CASCADE;
TRUNCATE TABLE resources RESTART IDENTITY CASCADE;
TRUNCATE TABLE locations RESTART IDENTITY CASCADE;
TRUNCATE TABLE resource_types RESTART IDENTITY CASCADE;
TRUNCATE TABLE users RESTART IDENTITY CASCADE;
TRUNCATE TABLE user_types RESTART IDENTITY CASCADE;

INSERT INTO user_types (type_name, description) VALUES
    ('Student', 'Students can view resource availability and access permitted resources for study and project work'),
    ('Teaching Staff', 'Faculty members who can reserve resources for lectures, labs, office hours, and research activities'),
    ('Administrator', 'System administrators who manage resources, approve reservations, and analyze usage data');

-- All seed users have password: password123
INSERT INTO users (first_name, last_name, email, password, type_id) VALUES
    ('Ana', 'Petrovska', 'ana.petrovska@finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 3),
    ('Marko', 'Dimitrovski', 'marko.dimitrovski@finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 3),
    ('Elena', 'Stojanova', 'elena.stojanova@finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 2),
    ('Nikola', 'Trajkovski', 'nikola.trajkovski@finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 2),
    ('Ivana', 'Kostadinova', 'ivana.kostadinova@finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 2),
    ('Aleksandar', 'Georgieski', 'aleksandar.georgieski@finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 2),
    ('Stefan', 'Nikolov', 'stefan.nikolov@students.finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 1),
    ('Martina', 'Ilievska', 'martina.ilievska@students.finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 1),
    ('David', 'Angelovski', 'david.angelovski@students.finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 1),
    ('Teodora', 'Manceva', 'teodora.manceva@students.finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 1),
    ('Filip', 'Ristovski', 'filip.ristovski@students.finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 1),
    ('Milena', 'Jovanovska', 'milena.jovanovska@students.finki.ukim.mk', '$2b$12$Y.WHm77o3R.5UXdGKzdpru4B08oGuzP1Ifdvgd8/jBeB2KgxQjZQW', 1);

INSERT INTO resource_types (type_name, is_physical) VALUES
    ('Classroom', TRUE),
    ('Computer Laboratory', TRUE),
    ('Projector', TRUE),
    ('Conference Room', TRUE),
    ('3D Printer', TRUE),
    ('Software License', FALSE),
    ('Virtual Machine', FALSE),
    ('Online Service', FALSE);

INSERT INTO locations (building, room) VALUES
    ('FINKI-A', '101'),
    ('FINKI-A', '102'),
    ('FINKI-A', '201'),
    ('FINKI-A', '202'),
    ('FINKI-A', '301'),
    ('FINKI-B', 'Lab 1'),
    ('FINKI-B', 'Lab 2'),
    ('FINKI-B', 'Lab 3'),
    ('FINKI-B', 'Lab 4'),
    ('TMF', 'Conference Hall'),
    ('TMF', 'Meeting Room A'),
    ('TMF', 'Meeting Room B'),
    ('Library', 'Study Room 1'),
    ('Library', 'Study Room 2');

INSERT INTO resources (name, description, available_from, available_to, available_weekends, type_id, location_id) VALUES
    ('Classroom 101', 'Standard classroom with 60 seats, whiteboard, and built-in projector', '08:00', '20:00', FALSE, 1, 1),
    ('Classroom 102', 'Small classroom with 30 seats, suitable for seminars and group work', '08:00', '20:00', FALSE, 1, 2),
    ('Lecture Hall 201', 'Large lecture hall with 150 seats, amphitheater style seating', '08:00', '22:00', TRUE, 1, 3),
    ('Classroom 202', 'Standard classroom with 45 seats, equipped with smart board', '08:00', '20:00', FALSE, 1, 4),
    ('Programming Lab 1', 'Computer lab with 25 workstations, Linux/Windows dual boot, for programming courses', '08:00', '22:00', TRUE, 2, 6),
    ('Programming Lab 2', 'Computer lab with 25 workstations, focused on web development tools', '08:00', '22:00', TRUE, 2, 7),
    ('Networking Lab', 'Specialized lab with network equipment, routers, switches for hands-on practice', '09:00', '18:00', FALSE, 2, 8),
    ('Database Lab', 'Lab with 20 workstations pre-configured with PostgreSQL, MySQL, Oracle', '08:00', '20:00', FALSE, 2, 9),
    ('Portable Projector Epson EB-X51', 'Portable projector 3800 lumens, XGA resolution, HDMI and VGA inputs', '08:00', '20:00', TRUE, 3, NULL),
    ('Portable Projector BenQ MH733', 'Full HD portable projector 4000 lumens, ideal for large rooms', '08:00', '20:00', TRUE, 3, NULL),
    ('Main Conference Hall', 'Large conference hall with 100 seats, video conferencing system, recording equipment', '08:00', '20:00', FALSE, 4, 10),
    ('Meeting Room A', 'Medium meeting room with 20 seats, whiteboard, TV screen for presentations', '08:00', '18:00', FALSE, 4, 11),
    ('Meeting Room B', 'Small meeting room with 10 seats, suitable for thesis defenses and small meetings', '08:00', '18:00', FALSE, 4, 12),
    ('Prusa i3 MK3S+', '3D printer for student projects, PLA/PETG filaments, max build volume 25x21x21cm', '09:00', '17:00', FALSE, 5, 6),
    ('Ultimaker S3', 'Professional dual-extrusion 3D printer, supports various materials', '09:00', '17:00', FALSE, 5, 6),
    ('Study Room 1', 'Quiet study room in library with 8 seats, power outlets, WiFi', '08:00', '22:00', TRUE, 1, 13),
    ('Study Room 2', 'Group study room in library with 12 seats and whiteboard', '08:00', '22:00', TRUE, 1, 14);

INSERT INTO resources (name, description, available_from, available_to, available_weekends, type_id, location_id) VALUES
    ('MATLAB Academic License', 'Network license for MATLAB R2024a with all toolboxes, 50 concurrent users', '00:00', '23:59', TRUE, 6, NULL),
    ('JetBrains Educational Pack', 'Access to IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs', '00:00', '23:59', TRUE, 6, NULL),
    ('Microsoft Azure Dev Tools', 'Azure subscription for students with $100 credit and free services', '00:00', '23:59', TRUE, 6, NULL),
    ('Adobe Creative Cloud', 'Full Creative Cloud suite - Photoshop, Illustrator, Premiere Pro, etc.', '00:00', '23:59', TRUE, 6, NULL),
    ('GPU Compute Server', 'Virtual server with NVIDIA Tesla T4, 16GB VRAM, for ML/AI projects', '00:00', '23:59', TRUE, 7, NULL),
    ('Development VM Pool', 'Pool of 10 Ubuntu VMs, 4 vCPU, 8GB RAM each, for student projects', '00:00', '23:59', TRUE, 7, NULL),
    ('Windows Server Instance', 'Windows Server 2022 VM for .NET development and testing', '00:00', '23:59', TRUE, 7, NULL),
    ('GitHub Enterprise', 'GitHub Enterprise account with unlimited private repositories', '00:00', '23:59', TRUE, 8, NULL),
    ('AWS Academy Sandbox', 'AWS sandbox environment for cloud computing courses', '00:00', '23:59', TRUE, 8, NULL),
    ('Google Cloud Credits', 'Google Cloud Platform credits for student projects and research', '00:00', '23:59', TRUE, 8, NULL);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-03 09:00:00', '2026-02-03 11:00:00', 'completed', 'Database Systems Lecture - Week 1', '2026-01-15 10:00:00', 'a1b2c3d4-e5f6-4789-abcd-ef0123456789', 3, 1, 3),
    ('2026-02-10 09:00:00', '2026-02-10 11:00:00', 'approved', 'Database Systems Lecture - Week 2', '2026-01-15 10:00:00', 'a1b2c3d4-e5f6-4789-abcd-ef0123456789', 3, 1, 3),
    ('2026-02-17 09:00:00', '2026-02-17 11:00:00', 'approved', 'Database Systems Lecture - Week 3', '2026-01-15 10:00:00', 'a1b2c3d4-e5f6-4789-abcd-ef0123456789', 3, 1, 3),
    ('2026-02-24 09:00:00', '2026-02-24 11:00:00', 'pending', 'Database Systems Lecture - Week 4', '2026-01-15 10:00:00', 'a1b2c3d4-e5f6-4789-abcd-ef0123456789', 3, NULL, 3);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-04 14:00:00', '2026-02-04 16:00:00', 'completed', 'Web Development Lab - Week 1', '2026-01-16 09:30:00', 'b2c3d4e5-f6a7-4890-bcde-f01234567890', 4, 1, 5),
    ('2026-02-11 14:00:00', '2026-02-11 16:00:00', 'approved', 'Web Development Lab - Week 2', '2026-01-16 09:30:00', 'b2c3d4e5-f6a7-4890-bcde-f01234567890', 4, 1, 5),
    ('2026-02-18 14:00:00', '2026-02-18 16:00:00', 'approved', 'Web Development Lab - Week 3', '2026-01-16 09:30:00', 'b2c3d4e5-f6a7-4890-bcde-f01234567890', 4, 1, 5);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-05 15:00:00', '2026-02-05 18:00:00', 'approved', 'Group study session for Algorithms exam', '2026-02-01 14:00:00', NULL, 7, 2, 16),
    ('2026-02-06 10:00:00', '2026-02-06 13:00:00', 'approved', 'Project team meeting - Software Engineering', '2026-02-02 11:30:00', NULL, 8, 2, 17),
    ('2026-02-07 09:00:00', '2026-02-07 12:00:00', 'pending', 'Thesis writing session', '2026-02-03 08:00:00', NULL, 9, NULL, 16);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-10 14:00:00', '2026-02-10 16:00:00', 'approved', 'Master thesis defense - Machine Learning topic', '2026-01-25 09:00:00', NULL, 5, 1, 13);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-08 09:00:00', '2026-02-08 17:00:00', 'approved', 'Guest lecture requiring portable projector', '2026-02-01 08:00:00', NULL, 6, 2, 9),
    ('2026-02-12 10:00:00', '2026-02-12 12:00:00', 'rejected', 'Projector needed but already booked', '2026-02-05 15:00:00', NULL, 4, 1, 9);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-06 09:00:00', '2026-02-06 17:00:00', 'approved', 'Printing prototype for IoT course project', '2026-02-01 16:00:00', NULL, 10, 2, 14),
    ('2026-02-07 09:00:00', '2026-02-07 17:00:00', 'pending', '3D print parts for robotics competition', '2026-02-04 10:00:00', NULL, 11, NULL, 15);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-01 00:00:00', '2026-06-30 23:59:00', 'approved', 'MATLAB license for numerical analysis course', '2026-01-20 11:00:00', NULL, 3, 1, 18),
    ('2026-02-01 00:00:00', '2026-06-30 23:59:00', 'approved', 'GPU server access for deep learning research', '2026-01-22 14:00:00', NULL, 5, 1, 23),
    ('2026-02-01 00:00:00', '2026-06-30 23:59:00', 'approved', 'AWS Academy access for cloud computing course', '2026-01-23 09:00:00', NULL, 4, 2, 27);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-05 00:00:00', '2026-03-05 23:59:00', 'approved', 'Development VM for semester project', '2026-02-01 08:30:00', NULL, 7, 2, 24),
    ('2026-02-05 00:00:00', '2026-03-05 23:59:00', 'pending', 'Windows Server VM for .NET project', '2026-02-04 12:00:00', NULL, 12, NULL, 25);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-15 10:00:00', '2026-02-15 12:00:00', 'cancelled', 'Meeting cancelled due to scheduling conflict', '2026-02-01 09:00:00', NULL, 6, 1, 12);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-06 08:00:00', '2026-02-06 10:00:00', 'approved', 'Morning lecture - Operating Systems', '2026-01-20 10:00:00', NULL, 3, 1, 1),
    ('2026-02-06 10:15:00', '2026-02-06 12:15:00', 'approved', 'Computer Networks Lecture', '2026-01-20 10:30:00', NULL, 4, 1, 1),
    ('2026-02-06 14:00:00', '2026-02-06 16:00:00', 'approved', 'Software Engineering Seminar', '2026-01-20 11:00:00', NULL, 5, 1, 1);

INSERT INTO reservations (start_time, end_time, status, purpose, created_at, recurrence_group_id, user_id, approved_by, resource_id) VALUES
    ('2026-02-05 09:00:00', '2026-02-05 13:00:00', 'completed', 'Network configuration practice - CCNA prep', '2026-01-28 14:00:00', NULL, 4, 2, 7),
    ('2026-02-12 09:00:00', '2026-02-12 13:00:00', 'approved', 'Firewall and security lab session', '2026-02-03 09:00:00', NULL, 4, 2, 7);
