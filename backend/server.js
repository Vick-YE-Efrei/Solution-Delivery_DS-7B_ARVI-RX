const express = require('express')
const cors    = require('cors')
require('dotenv').config()

const app = express()

// Accepte tout localhost peu importe le port Vite
app.use(cors({
  origin: /^http:\/\/localhost(:\d+)?$/,
  credentials: true
}))
app.use(express.json())

app.use('/api/auth',     require('./routes/auth'))
app.use('/api/users',    require('./routes/users'))
app.use('/api/analyses', require('./routes/analyses'))

app.get('/api/health', (_, res) => res.json({ status: 'ok' }))

const PORT = process.env.PORT || 3000
app.listen(PORT, () => console.log(`Backend ARVI-RX → http://localhost:${PORT}`))
