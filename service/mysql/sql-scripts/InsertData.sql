insert into user_database.users (user_id, username, password, salt, email)
values (1, 'HNYDUW0MHB', 0x3B89BCF90E89EDCDED3A5A2C9EF09B42E4DC8C6546684673D94075C54F31B6B4,
        0x5394EB5170420D904AE20376F27DFA2D1717E796974C1A4C1459BC18662C40D6, 'HNYDUW0MHB@HNYDUW0MHB.de');
insert into user_database.users (user_id, username, password, salt, email)
values (2, 'V4NW2JZWK1', 0xD93FAF7381A9D1E9061254F08493D05BE7F86735CDDF406DBD11CCA25217ADC5,
        0x0486DA420F64D19020F2350F7344D4ECA394BF2940009B1226BD003E291863AC, 'V4NW2JZWK1@V4NW2JZWK1.de');
insert into user_database.users (user_id, username, password, salt, email)
values (3, 'ZTFJ82SHWA', 0xB7A25165CB37132C05CF379811EFDC44D6247B35F35CB7D34A5F9E7D55102FD1,
        0x98F1C85A1D0DE9CDE9A498AB1D6D6511772D666425F862CCB7E4F248DE8B2E2F, 'ZTFJ82SHWA@ZTFJ82SHWA.de');
insert into user_database.users (user_id, username, password, salt, email)
values (4, 'XS4SF4E22Q', 0xF25F2929DF21DC1E37D9A85F0FD0F867AE64009C73DBF6C855AC097A92DB93D1,
        0xB05EF79CD9C447E7FA1767C14AC249552A19F0A7F0487BE611B2A87E0F537F4E, 'XS4SF4E22Q@XS4SF4E22Q.de');
INSERT INTO user_database.users (user_id, username, password, salt, email)
VALUES (5, 'a', 0xF1AC15AEFDB16530B77F5036CF7FED4FF461F2D9709A6563E8E871948C53095C,
        0xC8B5AE72F73CA1EAA5F58BBAC804D503B4193C8271E683AB2D1C597B14E6E29C, 'a@a.de');
INSERT INTO user_database.users (user_id, username, password, salt, email, is_doctor)
VALUES (7, 'doctor01', UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), '01@01.de', 1);
INSERT INTO user_database.users (user_id, username, password, salt, email, is_doctor)
VALUES (8, 'doctor02', UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), '02@02.de', 1);
INSERT INTO user_database.users (user_id, username, password, salt, email, is_doctor)
VALUES (9, 'doctor03', UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), '03@03.de', 1);
INSERT INTO user_database.users (user_id, username, password, salt, email, is_doctor)
VALUES (10, 'doctor04', UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), '04@04.de', 1);
INSERT INTO user_database.users (user_id, username, password, salt, email, is_doctor)
VALUES (11, 'doctor05', UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), UNHEX(REPLACE(CONCAT(UUID(),UUID()), '-','')), '05@05.de', 1);
