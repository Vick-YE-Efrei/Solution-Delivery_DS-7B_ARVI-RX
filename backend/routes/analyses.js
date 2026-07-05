const express  = require('express')
const multer   = require('multer')
const axios    = require('axios')
const FormData = require('form-data')
const fs       = require('fs')
const path     = require('path')
const pool     = require('../config/db')
const { requireAuth, requireAdmin } = require('../middleware/auth')

const router = express.Router()

const FASTAPI_URL = (process.env.FASTAPI_URL || 'http://localhost:8001').replace(/\/$/, '')
const MODEL_PROVIDER = (process.env.MODEL_PROVIDER || 'remote').toLowerCase()
const MODEL_KEY = 'medgemma_4b_pt'
const WARNING = 'Prototype pedagogique. Non destine au diagnostic. Validation par un professionnel qualifie requise.'

const upload = multer({
  dest: path.join(__dirname, '..', 'tmp_uploads'),
  limits: { fileSize: 20 * 1024 * 1024 },
  fileFilter: (_, file, cb) => {
    const ok = ['image/png', 'image/jpeg', 'image/jpg'].includes(file.mimetype)
    cb(ok ? null : new Error('Format non supporte. Utilisez PNG, JPG ou JPEG.'), ok)
  },
})

function normalizeMode(value) {
  return value === 'improved' ? 'improved' : 'baseline'
}

function mockPredict(filename, mode) {
  const start = Date.now()
  const name = String(filename || '').toLowerCase()

  let predictedClass = 'uncertain'
  let confidence = 0.52
  let visualEvidence = ['Aucun signe suffisamment fiable dans le mode de demonstration.']
  let justification = 'Mode mock local: reponse generee sans appel a MedGemma, uniquement pour tester le flux frontend, backend et MySQL.'

  if (name.includes('normal')) {
    predictedClass = 'normal'
    confidence = mode === 'improved' ? 0.74 : 0.70
    visualEvidence = ['Nom de fichier de demonstration associe a un cas normal.']
    justification = 'Mode mock local: le cas est classe normal pour valider le parcours applicatif.'
  } else if (
    name.includes('opacity') ||
    name.includes('opacite') ||
    name.includes('pneumonia') ||
    name.includes('pneumonie')
  ) {
    predictedClass = 'suspected_opacity'
    confidence = mode === 'improved' ? 0.76 : 0.71
    visualEvidence = ['Nom de fichier de demonstration associe a une opacite suspectee.']
    justification = 'Mode mock local: le cas est classe suspected_opacity pour valider le parcours applicatif.'
  }

  return {
    image_quality: 'good',
    predicted_class: predictedClass,
    confidence,
    visual_evidence: visualEvidence,
    justification,
    limitations: [
      'mock local sans modele medical',
      'resultat non clinique',
      'utilise seulement pour tester l interface et la journalisation',
    ],
    warning: WARNING,
    model_name: 'medgemma-4b-pt-mock',
    prompt_version: mode === 'improved' ? 'mock_improved_v1' : 'mock_baseline_v1',
    latency_ms: Date.now() - start,
  }
}

async function remotePredict(filePath, filename, mode) {
  const form = new FormData()
  form.append('file', fs.createReadStream(filePath), filename)

  const { data } = await axios.post(
    `${FASTAPI_URL}/predict?mode=${encodeURIComponent(mode)}&model_key=${MODEL_KEY}`,
    form,
    { headers: form.getHeaders(), timeout: 300_000 }
  )

  return data
}

async function saveAnalysis({ userId, filename, mode, pred }) {
  const threshold = 0.70
  const [result] = await pool.query(
    `INSERT INTO analyses
      (user_id, filename, mode, predicted_class, confidence, threshold,
       image_quality, justification, warning, model_name, prompt_version, latency_ms)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      userId,
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

  return {
    id: result.insertId,
    ...pred,
    filename,
    threshold,
  }
}

router.post('/predict', requireAuth, (req, res, next) => {
  upload.single('image')(req, res, (err) => {
    if (err) {
      console.error('[MULTER ERROR]', err.code, err.message)
      return res.status(400).json({ message: err.message || 'Erreur upload.' })
    }
    next()
  })
}, async (req, res) => {
  if (!req.file) return res.status(400).json({ message: 'Aucune image recue.' })

  const mode = normalizeMode(req.body.mode)
  const filePath = req.file.path
  const filename = req.file.originalname

  try {
    const pred = MODEL_PROVIDER === 'mock'
      ? mockPredict(filename, mode)
      : await remotePredict(filePath, filename, mode)

    const payload = await saveAnalysis({
      userId: req.user.id,
      filename,
      mode,
      pred,
    })

    return res.status(201).json(payload)
  } catch (err) {
    console.error('Predict error:', err.message)
    console.error('Model response body:', JSON.stringify(err.response?.data))

    if (err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET' || err.code === 'ENOTFOUND') {
      return res.status(503).json({
        message: 'Le serveur MedGemma est inaccessible. Pour tester sans Colab, mettez MODEL_PROVIDER=mock dans backend/.env. Pour Colab/ngrok, mettez MODEL_PROVIDER=remote et FASTAPI_URL=https://votre-url.ngrok-free.app.',
      })
    }

    return res.status(500).json({
      message: err.response?.data?.detail || err.response?.data?.message || 'Erreur lors de l analyse.',
    })
  } finally {
    fs.unlink(filePath, () => {})
  }
})

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

router.get('/stats', requireAuth, requireAdmin, async (req, res) => {
  try {
    const [[totals]] = await pool.query(`
      SELECT
        COUNT(*) AS total,
        SUM(predicted_class = 'normal') AS normal_count,
        SUM(predicted_class = 'suspected_opacity') AS opacity_count,
        SUM(predicted_class = 'uncertain') AS uncertain_count,
        ROUND(AVG(confidence) * 100, 1) AS avg_confidence,
        ROUND(AVG(latency_ms), 0) AS avg_latency_ms
      FROM analyses
    `)
    const [[users]] = await pool.query(`
      SELECT COUNT(*) AS total,
             SUM(role = 'user') AS user_count,
             SUM(role = 'admin') AS admin_count
      FROM users
    `)
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
