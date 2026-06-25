const bcrypt = require('bcryptjs')
const pool   = require('./config/db')

async function seed() {
  const users = [
    { name: 'Admin ARVI',    email: 'admin@arvi.fr',   password: 'admin123',  role: 'admin' },
    { name: 'Marie Dupont',  email: 'marie@arvi.fr',   password: 'user123',   role: 'user'  },
    { name: 'Thomas Leroy',  email: 'thomas@arvi.fr',  password: 'user123',   role: 'user'  },
  ]

  for (const u of users) {
    const [existing] = await pool.query('SELECT id FROM users WHERE email = ?', [u.email])
    if (existing.length > 0) {
      console.log(`  [SKIP] ${u.email} existe déjà`)
      continue
    }
    const hash = await bcrypt.hash(u.password, 10)
    await pool.query(
      'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
      [u.name, u.email, hash, u.role]
    )
    console.log(`  [OK]   ${u.email} (${u.role}) créé`)
  }

  console.log('\nComptes disponibles :')
  console.log('  admin@arvi.fr   / admin123  → rôle admin')
  console.log('  marie@arvi.fr   / user123   → rôle user')
  console.log('  thomas@arvi.fr  / user123   → rôle user')

  process.exit(0)
}

seed().catch(err => { console.error(err); process.exit(1) })
