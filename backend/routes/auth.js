const express  = require('express')
const bcrypt   = require('bcryptjs')
const jwt      = require('jsonwebtoken')
const pool     = require('../config/db')
const { requireAuth } = require('../middleware/auth')
require('dotenv').config()

const router = express.Router()

// POST /api/auth/register
router.post('/register', async (req, res) => {
  const { name, email, password } = req.body
  if (!name || !email || !password) {
    return res.status(400).json({ message: 'Tous les champs sont obligatoires.' })
  }
  if (password.length < 6) {
    return res.status(400).json({ message: 'Le mot de passe doit contenir au moins 6 caractères.' })
  }
  try {
    const [existing] = await pool.query('SELECT id FROM users WHERE email = ?', [email])
    if (existing.length > 0) {
      return res.status(409).json({ message: 'Un compte existe déjà avec cet e-mail.' })
    }
    const hash = await bcrypt.hash(password, 10)
    await pool.query(
      'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
      [name, email, hash, 'user']
    )
    return res.status(201).json({ message: 'Compte créé avec succès.' })
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { email, password } = req.body
  if (!email || !password) {
    return res.status(400).json({ message: 'E-mail et mot de passe requis.' })
  }
  try {
    const [rows] = await pool.query('SELECT * FROM users WHERE email = ?', [email])
    if (rows.length === 0) {
      return res.status(401).json({ message: 'Identifiants incorrects.' })
    }
    const user = rows[0]
    const match = await bcrypt.compare(password, user.password)
    if (!match) {
      return res.status(401).json({ message: 'Identifiants incorrects.' })
    }
    const token = jwt.sign(
      { id: user.id, name: user.name, email: user.email, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN }
    )
    return res.json({
      token,
      user: { id: user.id, name: user.name, email: user.email, role: user.role }
    })
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

// GET /api/auth/me
router.get('/me', requireAuth, async (req, res) => {
  try {
    const [rows] = await pool.query(
      'SELECT id, name, email, role, created_at FROM users WHERE id = ?',
      [req.user.id]
    )
    if (rows.length === 0) return res.status(404).json({ message: 'Utilisateur introuvable.' })
    return res.json(rows[0])
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

module.exports = router
