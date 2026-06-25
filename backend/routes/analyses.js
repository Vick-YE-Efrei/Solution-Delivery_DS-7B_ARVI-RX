const express = require('express')
const pool    = require('../config/db')
const { requireAuth, requireAdmin } = require('../middleware/auth')

const router = express.Router()

// POST /api/analyses — enregistrer une analyse
router.post('/', requireAuth, async (req, res) => {
  const { filename, mode, predicted_class, confidence, threshold,
          image_quality, justification, warning, model_name, prompt_version, latency_ms } = req.body
  try {
    const [result] = await pool.query(
      `INSERT INTO analyses
        (user_id, filename, mode, predicted_class, confidence, threshold,
         image_quality, justification, warning, model_name, prompt_version, latency_ms)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [req.user.id, filename, mode, predicted_class, confidence, threshold,
       image_quality, justification, warning, model_name, prompt_version, latency_ms]
    )
    return res.status(201).json({ id: result.insertId })
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

// GET /api/analyses/me — historique de l'utilisateur connecté
router.get('/me', requireAuth, async (req, res) => {
  try {
    const [rows] = await pool.query(
      'SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC',
      [req.user.id]
    )
    return res.json(rows)
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

// GET /api/analyses — toutes les analyses (admin)
router.get('/', requireAuth, requireAdmin, async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT a.*, u.name AS user_name, u.email AS user_email
      FROM analyses a
      JOIN users u ON u.id = a.user_id
      ORDER BY a.created_at DESC
    `)
    return res.json(rows)
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

// GET /api/analyses/stats — métriques globales (admin)
router.get('/stats', requireAuth, requireAdmin, async (req, res) => {
  try {
    const [[totals]] = await pool.query(`
      SELECT
        COUNT(*) AS total,
        SUM(predicted_class = 'normal') AS normal_count,
        SUM(predicted_class = 'suspected_opacity') AS opacity_count,
        SUM(predicted_class = 'uncertain') AS uncertain_count,
        ROUND(AVG(confidence) * 100, 1) AS avg_confidence
      FROM analyses
    `)
    const [[users]] = await pool.query(`
      SELECT COUNT(*) AS total,
             SUM(role = 'user') AS user_count,
             SUM(role = 'admin') AS admin_count
      FROM users
    `)
    return res.json({ analyses: totals, users })
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

module.exports = router
