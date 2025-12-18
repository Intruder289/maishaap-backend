-- SQL query to approve the test user
-- Run this in your PostgreSQL database or Django dbshell

-- Step 1: Check current status
SELECT 
    u.id, 
    u.username, 
    u.email, 
    u.is_active,
    p.is_approved,
    p.approved_at
FROM auth_user u
LEFT JOIN accounts_profile p ON p.user_id = u.id
WHERE u.username = 'testuser_20251006_100841';

-- Step 2: Approve the user
UPDATE auth_user 
SET is_active = true 
WHERE username = 'testuser_20251006_100841';

UPDATE accounts_profile 
SET is_approved = true, approved_at = NOW() 
WHERE user_id = (SELECT id FROM auth_user WHERE username = 'testuser_20251006_100841');

-- Step 3: Verify the update
SELECT 
    u.id, 
    u.username, 
    u.email, 
    u.is_active,
    p.is_approved,
    p.approved_at
FROM auth_user u
LEFT JOIN accounts_profile p ON p.user_id = u.id
WHERE u.username = 'testuser_20251006_100841';
