-- SEED DATA FOR RELIEF SYSTEM

-- 1. Seed Roles
INSERT INTO roles (id, name) VALUES 
(1, 'Admin'),
(2, 'Resident'),
(3, 'RescueTeam')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Seed Default Users
-- Passwords: 
-- admin123 -> password_hash for Werkzeug security: 'scrypt:32768:8:1$yX8VvW2T$7841cbf679abec7102ad0dbd032ab41416972d73f1d8c1c4fdf4b1263d91cf0eb9658ec8d10b77648356cc5bc1050e8d0e74ff1841344487440409cd836dfc24'
-- citizen123 -> password_hash: 'scrypt:32768:8:1$yX8VvW2T$b4c73e028b1fb2fa3e46efbd6372b6a22ee61ec2b32ee81bcf704db35d9472605e263d6f4618e47be88bb5d105a2e88a0e74ff1841344487440409cd836dfc24'
-- rescue123 -> password_hash: 'scrypt:32768:8:1$yX8VvW2T$cb9742a0b127ff28238ee84de3dcb2955f261ec2b32ee81bcf704db35d9472605e263d6f4618e47be88bb5d105a2e88a0e74ff1841344487440409cd836dfc24'
INSERT INTO users (id, phone, password_hash, full_name, role_id, is_active, created_at) VALUES
(1, '0901234567', 'scrypt:32768:8:1$yX8VvW2T$7841cbf679abec7102ad0dbd032ab41416972d73f1d8c1c4fdf4b1263d91cf0eb9658ec8d10b77648356cc5bc1050e8d0e74ff1841344487440409cd836dfc24', 'Quản Trị Viên', 1, 1, NOW()),
(2, '0987654321', 'scrypt:32768:8:1$yX8VvW2T$b4c73e028b1fb2fa3e46efbd6372b6a22ee61ec2b32ee81bcf704db35d9472605e263d6f4618e47be88bb5d105a2e88a0e74ff1841344487440409cd836dfc24', 'Nguyễn Văn Dân', 2, 1, NOW()),
(3, '0912345678', 'scrypt:32768:8:1$yX8VvW2T$cb9742a0b127ff28238ee84de3dcb2955f261ec2b32ee81bcf704db35d9472605e263d6f4618e47be88bb5d105a2e88a0e74ff1841344487440409cd836dfc24', 'Đội Trưởng Cứu Hộ A', 3, 1, NOW())
ON DUPLICATE KEY UPDATE phone=VALUES(phone);

-- 3. Seed Rescue Team Profile
INSERT INTO rescue_teams (id, user_id, team_name, leader_name, contact_phone, status, current_lat, current_lng) VALUES
(1, 3, 'Đội Cứu Hộ Phản Ứng Nhanh Số 1', 'Đội Trưởng Cứu Hộ A', '0912345678', 'ACTIVE', 21.0285, 105.8542)
ON DUPLICATE KEY UPDATE team_name=VALUES(team_name);

-- 4. Seed Emergency Contacts
INSERT INTO emergency_contacts (id, name, phone, icon_type, sort_order, is_active) VALUES
(1, '113 Công an', '113', 'shield', 1, 1),
(2, '114 Cứu hỏa & Cứu nạn', '114', 'flame', 2, 1),
(3, '115 Cấp cứu y tế', '115', 'heart-pulse', 3, 1),
(4, 'Đường dây nóng Hỗ trợ Thiên tai Quốc gia', '18001022', 'phone-call', 4, 1)
ON DUPLICATE KEY UPDATE name=VALUES(name), phone=VALUES(phone);

-- 5. Seed Sample Disaster Warning
INSERT INTO disasters (id, title, description, alert_level, latitude, longitude, radius_km, status, occurred_at) VALUES
(1, 'Lũ quét và sạt lở đất do bão lớn', 'Vùng đồi núi phía Tây đang có nguy cơ sạt lở cao do lượng mưa vượt quá 300mm. Yêu cầu người dân di tản đến vùng an toàn.', 'RED', 21.0300, 105.8400, 15.0, 'ACTIVE', NOW())
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- 6. Seed Sample Alerts
INSERT INTO alerts (id, disaster_id, title, message, target_area, alert_level) VALUES
(1, 1, 'CẢNH BÁO KHẨN CẤP: SẠT LỞ VÙNG ĐỒI NÚI', 'Di tản ngay lập tức khỏi vùng sạt lở, tập trung tại nhà văn hóa quận.', 'Quận Ba Đình, Quận Hoàn Kiếm, TP. Hà Nội', 'RED')
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- 7. Seed Sample Community Posts (some unverified, some verified)
INSERT INTO community_posts (id, user_id, title, content, post_type, latitude, longitude, verification_status, upvotes, downvotes, created_at) VALUES
(1, 2, 'Ngập sâu tại ngã tư Cầu Giấy', 'Nước ngập nửa bánh xe máy, xe ga không đi qua được, mọi người nên tránh tuyến đường này.', 'FLOOD', 21.0350, 105.8000, 'VERIFIED', 5, 0, NOW() - INTERVAL 1 HOUR),
(2, 2, 'Sạt lở taluy âm đường ven đồi', 'Sạt lở một phần mặt đường nhựa, các phương tiện ô tô không thể qua lại.', 'LANDSLIDE', 21.0100, 105.8100, 'UNVERIFIED', 2, 0, NOW() - INTERVAL 10 MINUTE)
ON DUPLICATE KEY UPDATE title=VALUES(title);
