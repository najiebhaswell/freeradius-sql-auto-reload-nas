# FreeRADIUS SQL Auto Reload NAS

Script dan konfigurasi untuk me-reload service FreeRADIUS secara otomatis ketika ada perubahan pada tabel NAS di database (misalnya melalui daloRADIUS).

## Langkah 1 — Buat Tabel & Trigger di MySQL

Login ke MySQL (sesuaikan username, password, dan nama database):
```bash
mysql -u root -p radius_Ds3lPX
```

Lalu jalankan SQL yang ada di file `nas_triggers.sql`:
```bash
mysql -u root -p radius_Ds3lPX < nas_triggers.sql
```

Atau jalankan SQL berikut secara manual:
```sql
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
```

## Langkah 2 — Install Dependencies

```bash
apt install python3 python3-pip -y
pip3 install pymysql
```

## Langkah 3 — Setup Script Reloader

Buat direktori untuk state marker:
```bash
mkdir -p /var/lib/reloader
```

Copy script `nas-reloader.py` ke `/usr/local/bin/` dan beri hak eksekusi:
```bash
cp nas-reloader.py /usr/local/bin/nas-reloader.py
chmod +x /usr/local/bin/nas-reloader.py
```

## Langkah 4 — Setup Config File

Copy `reloader.json` ke `/etc/`:
```bash
cp reloader.json /etc/reloader.json
```

Sesuaikan isinya dengan kredensial database kamu:
```json
{
  "database": {
    "host": "localhost",
    "username": "root",
    "password": "ISI_PASSWORD_MYSQL",
    "database": "radius_Ds3lPX"
  }
}
```

## Langkah 5 — Setup Systemd Service

Copy `nas-reloader.service` ke `/etc/systemd/system/`:
```bash
cp nas-reloader.service /etc/systemd/system/nas-reloader.service
```

Reload daemon dan aktifkan service:
```bash
systemctl daemon-reload
systemctl enable --now nas-reloader
```

## Langkah 6 — Test

Tambahkan NAS baru dari daloRADIUS, lalu cek log:
```bash
journalctl -u nas-reloader -f
```

Harusnya muncul:
```
NAS change detected (db=2, local=1). Restarting FreeRADIUS...
FreeRADIUS restarted successfully.
```

## Ringkasan Cara Kerja

1. DaloRADIUS melakukan `INSERT` ke tabel `nas`.
2. MySQL Trigger otomatis melakukan `INSERT` ke tabel `nas_changes`.
3. `nas-reloader.py` (loop tiap 30 detik) mendeteksi perubahan ID.
4. Menjalankan `systemctl restart freeradius`.
5. FreeRADIUS me-reload NAS dari Database.
