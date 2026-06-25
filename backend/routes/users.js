const express = require('express')
const pool    = require('../config/db')
const { requireAuth, requireAdmin } = require('../middleware/auth')

const router = express.Router()

// GET /api/users — admin seulement
router.get('/', requireAuth, requireAdmin, async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT u.id, u.name, u.email, u.role, u.created_at,
             COUNT(a.id) AS analysis_count
      FROM users u
      LEFT JOIN analyses a ON a.user_id = u.id
      GROUP BY u.id
      ORDER BY u.created_at DESC
    `)
    return res.json(rows)
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

module.exports = router
