-- PronIELTS Database Seed Script
-- Creates initial dialogs and phrases for testing
-- Run with: psql -h localhost -U pronielts -d pronielts -f seed_database.sql

-- Clear existing data (for development only)
-- TRUNCATE TABLE assessments, phrases, dialogs, users RESTART IDENTITY CASCADE;

-- Professional Dialog
INSERT INTO dialogs (title, category, description, difficulty_level, created_at) VALUES
('Tech Job Interview', 'Professional', 'Common technical interview questions', 'Advanced', CURRENT_TIMESTAMP);

INSERT INTO phrases (dialog_id, reference_text, "order", difficulty) VALUES
(1, 'Can you describe your experience with cloud computing platforms like AWS or Azure?', 1, 'Advanced'),
(1, 'How do you approach debugging a complex software issue?', 2, 'Advanced'),
(1, 'What is your experience with agile development methodologies?', 3, 'Intermediate'),
(1, 'Describe a challenging project you worked on recently.', 4, 'Advanced'),
(1, 'How do you stay updated with new technologies?', 5, 'Intermediate');

-- Travel Dialog
INSERT INTO dialogs (title, category, description, difficulty_level, created_at) VALUES
('Airport Check-in', 'Travel', 'Essential phrases for airport procedures', 'Beginner', CURRENT_TIMESTAMP);

INSERT INTO phrases (dialog_id, reference_text, "order", difficulty) VALUES
(2, 'I would like to check in for my flight to London.', 1, 'Beginner'),
(2, 'Do I need to pay for extra baggage?', 2, 'Beginner'),
(2, 'Can I have a window seat please?', 3, 'Beginner'),
(2, 'What time does the boarding start?', 4, 'Beginner'),
(2, 'Where is the departure gate?', 5, 'Beginner');

-- Restaurant Dialog
INSERT INTO dialogs (title, category, description, difficulty_level, created_at) VALUES
('Ordering Food', 'Restaurant', 'Common restaurant phrases', 'Beginner', CURRENT_TIMESTAMP);

INSERT INTO phrases (dialog_id, reference_text, "order", difficulty) VALUES
(3, 'I would like to make a reservation for two people.', 1, 'Beginner'),
(3, 'Can I see the menu please?', 2, 'Beginner'),
(3, 'I will have the grilled salmon with vegetables.', 3, 'Beginner'),
(3, 'Could we have the bill please?', 4, 'Beginner'),
(3, 'Do you accept credit cards?', 5, 'Beginner');

-- IELTS Part 1
INSERT INTO dialogs (title, category, description, difficulty_level, created_at) VALUES
('IELTS Speaking Part 1 - Personal Info', 'IELTS_Part1', 'Introduction and interview questions', 'Intermediate', CURRENT_TIMESTAMP);

INSERT INTO phrases (dialog_id, reference_text, "order", difficulty) VALUES
(4, 'What is your full name?', 1, 'Beginner'),
(4, 'Where do you come from?', 2, 'Beginner'),
(4, 'Do you work or are you a student?', 3, 'Intermediate'),
(4, 'What do you like about your hometown?', 4, 'Intermediate'),
(4, 'What are your hobbies and interests?', 5, 'Intermediate');

-- General Conversation
INSERT INTO dialogs (title, category, description, difficulty_level, created_at) VALUES
('Small Talk', 'General', 'Everyday conversation starters', 'Beginner', CURRENT_TIMESTAMP);

INSERT INTO phrases (dialog_id, reference_text, "order", difficulty) VALUES
(5, 'How are you today?', 1, 'Beginner'),
(5, 'What do you do for a living?', 2, 'Beginner'),
(5, 'What are your plans for the weekend?', 3, 'Beginner'),
(5, 'Have you seen any good movies lately?', 4, 'Intermediate'),
(5, 'What kind of music do you enjoy?', 5, 'Intermediate');

-- Success message
SELECT 'Database seeded successfully!' as status;
SELECT 'Dialogs:' as type, COUNT(*) as count FROM dialogs
UNION ALL
SELECT 'Phrases:' as type, COUNT(*) as count FROM phrases;
