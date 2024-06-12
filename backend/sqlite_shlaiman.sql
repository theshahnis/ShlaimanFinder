PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "group" (
	id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, passcode VARCHAR(4), 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO "group" VALUES(1,'admin',NULL);
INSERT INTO "group" VALUES(2,'Jera','0000');
INSERT INTO "group" VALUES(3,'test','1234');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	email VARCHAR(150) NOT NULL, 
	username VARCHAR(150) NOT NULL, 
	password VARCHAR(150) NOT NULL, 
	superuser BOOLEAN, 
	group_id INTEGER, 
	profile_image VARCHAR(150), passcode_attempts INTEGER, note TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	FOREIGN KEY(group_id) REFERENCES "group" (id)
);
INSERT INTO user VALUES(1,'theshahnis@gmail.com','theshahnis','pbkdf2:sha256:600000$foOt6Tf635T4Ni0g$45841eb4a47510d96dbf98930dc7fc4878463e0faa7f5d03aa03a4567a5c6a60',1,3,'a647632cc1ed61f7.jpg',0,'Blablabla note');
INSERT INTO user VALUES(2,'tester@test.com','tester','pbkdf2:sha256:600000$bBUUuMGP1xLqU87u$2b59a7738491a10a4c632ce9489c5e03fec7ce23be746a8d67c49f4de3c6587d',0,3,NULL,NULL,NULL);
INSERT INTO user VALUES(3,'asdasdasd@testo.com','asdasd','pbkdf2:sha256:600000$1n3q0wJribNhcdrO$2a76c85012016a3c1f6f4a5ad988a5d9dd8a1b0e3bb774dc239862f13c7bd822',0,3,NULL,NULL,NULL);
INSERT INTO user VALUES(4,'teasd@test.com','tesasd','pbkdf2:sha256:600000$ZmadbrSqCftx3mye$79bebb9019e7ba276574d95c95db44f9f9454cbfcd26eb99162da72e3d4b1151',0,3,NULL,0,NULL);
INSERT INTO user VALUES(5,'teasd1@test.com','Shlaiman','pbkdf2:sha256:600000$9pY6tk3iPJ8PLOVk$437547e8fe625767c9b77b755e1f0c848d8d0e343a44c1608a000ad06c66051c',0,3,'dae09f06cb3808f6.jpg',0,NULL);
INSERT INTO user VALUES(6,'asdasd@test.com','blabla','pbkdf2:sha256:600000$xb9gg2QGy77LOeMi$efe1c1923a8c5aad5da458bca4a1f6fd60382f2e21f6738c6a8f9ca5b81783fc',0,3,'ba1a0eb3982d444a.gif',0,'');
INSERT INTO user VALUES(7,'vbvbvbvb@asd.com','vbvbvbvb','pbkdf2:sha256:600000$NHfK2eqPKcDAXcdx$26a16bc702b820c28e1ede0f57fe17460c226e3d5dec566375e9ea2e35710d22',0,NULL,NULL,0,NULL);
CREATE TABLE location (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	timestamp DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO location VALUES(1,1,31.928700500000001482,34.849548099999999805,'2024-06-07 19:51:12.401784');
INSERT INTO location VALUES(2,5,32.093299999999999271,34.794199999999996463,'2024-05-29 18:12:50.805426');
INSERT INTO location VALUES(3,6,31.670272000000000644,34.576793600000002015,'2024-06-07 12:44:00.804118');
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('90de7c641a1a');
CREATE TABLE meeting_point (
	id INTEGER NOT NULL, 
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	group_id INTEGER NOT NULL, username VARCHAR(150) NOT NULL, note TEXT, image VARCHAR(150), duration INTEGER, created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES "group" (id)
);
INSERT INTO meeting_point VALUES(1,32.033031983816748322,34.768295288085944605,3,'asd','asd',NULL,3,'2024-05-31 10:52:11.950183');
INSERT INTO meeting_point VALUES(2,32.019642738704767737,34.766921997070319605,3,'asdasdasd','asdasd',NULL,3,'2024-05-31 10:54:43.645519');
INSERT INTO meeting_point VALUES(3,32.024882241610768574,34.797821044921882105,3,'jkhkjh','654654',NULL,1,'2024-05-31 11:30:15.887525');
INSERT INTO meeting_point VALUES(4,32.034690948750515816,34.839706420898444605,3,'מסעדה','שדגשדגשדגשדג',NULL,2,'2024-05-31 11:58:59.139588');
CREATE TABLE static_location (
	id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	note TEXT, 
	image VARCHAR(150), 
	PRIMARY KEY (id)
);
CREATE TABLE user_show (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	show_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(show_id) REFERENCES show (id)
);
INSERT INTO user_show VALUES(3,6,3);
INSERT INTO user_show VALUES(4,1,3);
INSERT INTO user_show VALUES(5,1,16);
INSERT INTO user_show VALUES(6,1,12);
INSERT INTO user_show VALUES(8,1,8);
INSERT INTO user_show VALUES(9,6,11);
INSERT INTO user_show VALUES(10,6,1);
INSERT INTO user_show VALUES(11,6,16);
INSERT INTO user_show VALUES(12,6,18);
INSERT INTO user_show VALUES(13,1,2);
INSERT INTO user_show VALUES(14,1,6);
INSERT INTO user_show VALUES(15,1,11);
INSERT INTO user_show VALUES(16,1,1);
CREATE TABLE show (
	id INTEGER NOT NULL, 
	name VARCHAR(80) NOT NULL, 
	start_time DATETIME NOT NULL, 
	end_time DATETIME NOT NULL, 
	stage VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO show VALUES(1,'Electric Callboy','2024-06-27 23:15:00.000000','2024-06-28 00:45:00.000000','Eagle');
INSERT INTO show VALUES(2,'Bad Religion','2024-06-27 22:15:00.000000','2024-06-27 23:15:00.000000','Vulture');
INSERT INTO show VALUES(3,'Get The Shot','2024-06-27 22:15:00.000000','2024-06-27 23:15:00.000000','Buzzard');
INSERT INTO show VALUES(4,'Authority Zero','2024-06-27 23:15:00.000000','2024-06-28 00:00:00.000000','Hawk');
INSERT INTO show VALUES(5,'Emo Night Mainland','2024-06-27 17:00:00.000000','2024-06-28 01:00:00.000000','Raven');
INSERT INTO show VALUES(6,'Body Count','2024-06-27 21:15:00.000000','2024-06-27 22:15:00.000000','Eagle');
INSERT INTO show VALUES(8,'Body Count ft. Ice-T','2024-06-27 21:15:00.000000','2024-06-27 22:15:00.000000','Eagle');
INSERT INTO show VALUES(9,'Madball','2024-06-27 19:45:00.000000','2024-06-27 20:30:00.000000','Eagle');
INSERT INTO show VALUES(10,'Shadow of Intent','2024-06-27 18:15:00.000000','2024-06-27 19:00:00.000000','Eagle');
INSERT INTO show VALUES(11,'Imminence','2024-06-27 20:30:00.000000','2024-06-27 21:15:00.000000','Vulture');
INSERT INTO show VALUES(12,'Movements','2024-06-27 19:00:00.000000','2024-06-27 19:45:00.000000','Vulture');
INSERT INTO show VALUES(13,'Knosis','2024-06-27 17:30:00.000000','2024-06-27 18:15:00.000000','Vulture');
INSERT INTO show VALUES(14,'Ploegendienst','2024-06-27 20:30:00.000000','2024-06-27 21:15:00.000000','Buzzard');
INSERT INTO show VALUES(15,'Hot Mulligan','2024-06-27 19:00:00.000000','2024-06-27 19:45:00.000000','Buzzard');
INSERT INTO show VALUES(16,'Gel','2024-06-27 17:30:00.000000','2024-06-27 18:15:00.000000','Buzzard');
INSERT INTO show VALUES(17,'Sha La Lees','2024-06-27 21:15:00.000000','2024-06-27 22:00:00.000000','Hawk');
INSERT INTO show VALUES(18,'Death Lens','2024-06-27 19:45:00.000000','2024-06-27 20:30:00.000000','Hawk');
INSERT INTO show VALUES(19,'Pressure Pact','2024-06-27 18:15:00.000000','2024-06-27 19:00:00.000000','Hawk');
COMMIT;