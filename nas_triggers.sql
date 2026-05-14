-- Tabel untuk tracking perubahan NAS
CREATE TABLE IF NOT EXISTS `nas_changes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `changed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `action` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Trigger saat INSERT ke tabel nas
CREATE TRIGGER nas_insert AFTER INSERT ON nas
FOR EACH ROW INSERT INTO nas_changes (action) VALUES ('insert');

-- Trigger saat UPDATE ke tabel nas
CREATE TRIGGER nas_update AFTER UPDATE ON nas
FOR EACH ROW INSERT INTO nas_changes (action) VALUES ('update');

-- Trigger saat DELETE dari tabel nas
CREATE TRIGGER nas_delete AFTER DELETE ON nas
FOR EACH ROW INSERT INTO nas_changes (action) VALUES ('delete');

-- Seed agar ada entry awal
INSERT INTO nas_changes (action) VALUES ('init');
