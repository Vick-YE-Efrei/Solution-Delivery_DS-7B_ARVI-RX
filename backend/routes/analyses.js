const express  = require('express')
const multer   = require('multer')
const axios    = require('axios')
const FormData = require('form-data')
const fs       = require('fs')
const path     = require('path')
const pool     = require('../config/db')
const { requireAuth, requireAdmin } = require('../middleware/auth')

const router = express.Router()

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000'

// Stockage local temporaire pour l'image uploadée
const upload = multer({
  dest: path.join(__dirname, '..', 'tmp_uploads'),
  limits: { fileSize: 20 * 1024 * 1024 }, // 20 MB
  fileFilter: (_, file, cb) => {
    const ok = ['image/png', 'image/jpeg', 'image/jpg'].includes(file.mimetype)
    cb(ok ? null : new Error('Format non supporté'), ok)
  },
})

// ─── POST /api/analyses/predict — upload image → FastAPI → MySQL ───────────
router.post('/predict', requireAuth, upload.single('image'), async (req, res) => {
  if (!req.file) return res.status(400).json({ message: 'Aucune image reçue.' })

  const mode      = req.body.mode      || 'toy'
  const model_key = req.body.model_key || 'medgemma_4b_pt'
  const filePath  = req.file.path
  const filename  = req.file.originalname

  try {
    // Transfert vers FastAPI
    const form = new FormData()
    form.append('file', fs.createReadStream(filePath), filename)

    const fastapiRes = await axios.post(
      `${FASTAPI_URL}/predict?mode=${mode}&model_key=${model_key}`,
      form,
      { headers: form.getHeaders(), timeout: 120_000 }
    )
    const pred = fastapiRes.data

    // Sauvegarde MySQL
    const threshold = 0.70
    const [result] = await pool.query(
      `INSERT INTO analyses
        (user_id, filename, mode, predicted_class, confidence, threshold,
         image_quality, justification, warning, model_name, prompt_version, latency_ms)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        req.user.id,
        filename,
        mode,
        pred.predicted_class,
        pred.confidence,
        threshold,
        pred.image_quality,
        pred.justification,
        pred.warning,
        pred.model_name,
        pred.prompt_version,
        pred.latency_ms,
      ]
    )

    return res.status(201).json({
      id: result.insertId,
      ...pred,
      filename,
      threshold,
    })
  } catch (err) {
    console.error('Predict error:', err.message)
    // Si FastAPI est hors ligne, retourner une erreur claire
    if (err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET') {
      return res.status(503).json({
        message: 'Le serveur de modèle (FastAPI) est inaccessible. Lancez-le avec : uvicorn api.main:app --reload',
      })
    }
    return res.status(500).json({ message: 'Erreur lors de l\'analyse.' })
  } finally {
    // Nettoyage du fichier temporaire
    fs.unlink(filePath, () => {})
  }
})

// ─── GET /api/analyses/me — historique de l'utilisateur connecté ───────────
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

// ─── GET /api/analyses — toutes les analyses (admin) ──────────────────────
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

// ─── GET /api/analyses/stats — métriques globales (admin) ─────────────────
router.get('/stats', requireAuth, requireAdmin, async (req, res) => {
  try {
    const [[totals]] = await pool.query(`
      SELECT
        COUNT(*)                                AS total,
        SUM(predicted_class = 'normal')         AS normal_count,
        SUM(predicted_class = 'suspected_opacity') AS opacity_count,
        SUM(predicted_class = 'uncertain')      AS uncertain_count,
        ROUND(AVG(confidence) * 100, 1)         AS avg_confidence,
        ROUND(AVG(latency_ms), 0)               AS avg_latency_ms
      FROM analyses
    `)
    const [[users]] = await pool.query(`
      SELECT COUNT(*)           AS total,
             SUM(role = 'user') AS user_count,
             SUM(role = 'admin') AS admin_count
      FROM users
    `)
    // Distribution par modèle
    const [byModel] = await pool.query(`
      SELECT model_name, COUNT(*) AS count,
             ROUND(AVG(confidence)*100,1) AS avg_conf
      FROM analyses
      GROUP BY model_name
      ORDER BY count DESC
    `)
    return res.json({ analyses: totals, users, by_model: byModel })
  } catch (err) {
    console.error(err)
    return res.status(500).json({ message: 'Erreur serveur.' })
  }
})

module.exports = router
