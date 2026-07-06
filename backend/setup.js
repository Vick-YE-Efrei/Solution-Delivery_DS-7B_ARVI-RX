const mysql  = require('mysql2/promise')
const bcrypt = require('bcryptjs')
require('dotenv').config()

async function setup() {
  // Connexion sans base pour pouvoir la créer
  const conn = await mysql.createConnection({
    host:     process.env.DB_HOST     || 'localhost',
    port:     process.env.DB_PORT     || 3306,
    user:     process.env.DB_USER     || 'root',
    password: process.env.DB_PASSWORD || '',
  })

  const db = process.env.DB_NAME || 'arvi_db'

  console.log(`\n[1/3] Création de la base "${db}"...`)
  await conn.query(`CREATE DATABASE IF NOT EXISTS \`${db}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci`)
  await conn.query(`USE \`${db}\``)

  console.log('[2/3] Création des tables...')
  await conn.query(`
    CREATE TABLE IF NOT EXISTS users (
      id         INT AUTO_INCREMENT PRIMARY KEY,
      name       VARCHAR(100) NOT NULL,
      email      VARCHAR(150) NOT NULL UNIQUE,
      password   VARCHAR(255) NOT NULL,
      role       ENUM('admin','user') NOT NULL DEFAULT 'user',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `)

  await conn.query(`
    CREATE TABLE IF NOT EXISTS analyses (
      id             INT AUTO_INCREMENT PRIMARY KEY,
      user_id        INT NOT NULL,
      filename       VARCHAR(255),
      mode           ENUM('baseline','improved') DEFAULT 'baseline',
      predicted_class ENUM('normal','suspected_opacity','uncertain'),
      confidence     FLOAT,
      threshold      FLOAT,
      image_quality  VARCHAR(50),
      justification  TEXT,
      warning        TEXT,
      model_name     VARCHAR(100),
      prompt_version VARCHAR(50),
      latency_ms     INT,
      created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
  `)

  console.log('[3/3] Insertion des utilisateurs...')
  const users = [
    { name: 'Admin ARVI',   email: 'admin@arvi.fr',  password: 'admin123', role: 'admin' },
    { name: 'Marie Dupont', email: 'marie@arvi.fr',  password: 'user123',  role: 'user'  },
    { name: 'Thomas Leroy', email: 'thomas@arvi.fr', password: 'user123',  role: 'user'  },
  ]

  for (const u of users) {
    const [existing] = await conn.query('SELECT id FROM users WHERE email = ?', [u.email])
    if (existing.length > 0) {
      console.log(`  [SKIP] ${u.email} existe déjà`)
      continue
    }
    const hash = await bcrypt.hash(u.password, 10)
    await conn.query('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
      [u.name, u.email, hash, u.role])
    console.log(`  [OK]   ${u.email} (${u.role})`)
  }

  await conn.end()

  console.log('\nSetup terminé. Comptes disponibles :')
  console.log('  admin@arvi.fr  / admin123  → admin')
  console.log('  marie@arvi.fr  / user123   → user')
  console.log('  thomas@arvi.fr / user123   → user\n')
}

setup().catch(err => { console.error('\nErreur :', err.message); process.exit(1) })
