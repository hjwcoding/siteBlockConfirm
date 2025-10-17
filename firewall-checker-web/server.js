const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dist')));

// API: Domain Check
app.post('/api/check-domain', async (req, res) => {
  const { domain } = req.body;

  if (!domain) {
    return res.status(400).json({ error: 'Domain is required' });
  }

  exec(`nslookup ${domain}`, (error, stdout, stderr) => {
    let ip = null;

    // Check for explicit failure indicators first
    const isFailure = error || stdout.includes("can't find") || stdout.includes("Non-existent domain");

    if (!isFailure) {
      // If no explicit failure, try to parse a valid IP from the answer block
      let searchBlock = stdout;
      const nonAuthMarker = 'Non-authoritative answer:';
      const nonAuthIndex = stdout.indexOf(nonAuthMarker);

      if (nonAuthIndex !== -1) {
        searchBlock = stdout.substring(nonAuthIndex);
      } else {
        const serverAddrMatch = stdout.match(/Address:\s+((?:[0-9]{1,3}\.){3}[0-9]{1,3})/);
        if (serverAddrMatch) {
          const serverAddrEndIndex = stdout.indexOf(serverAddrMatch[0]) + serverAddrMatch[0].length;
          searchBlock = stdout.substring(serverAddrEndIndex);
        }
      }

      const ipMatches = searchBlock.match(/((?:[0-9]{1,3}\.){3}[0-9]{1,3})/g);
      if (ipMatches && ipMatches.length > 0) {
        ip = ipMatches[0];
      }
    }

    // Final decision: if we found an IP and there was no failure, it's a success
    if (ip) {
      res.json({ success: true, message: `IP 확인 성공! :: ${ip}`, ip });
    } else {
      res.json({ success: false, message: `오류: '${domain}'을(를) 찾을 수 없습니다.` });
    }
  });
});

// API: Get Tuples List
app.get('/api/tuples', (req, res) => {
  try {
    const filePath = path.join(__dirname, 'data', 'tuples_list.json');
    const data = fs.readFileSync(filePath, 'utf8');
    res.json(JSON.parse(data));
  } catch (error) {
    console.error('Failed to read tuples_list.json:', error);
    res.status(500).json({ error: 'Failed to read tuples list' });
  }
});

// API: Get Domain List
app.get('/api/domains', (req, res) => {
  try {
    const filePath = path.join(__dirname, 'data', 'domain_list.json');
    const data = fs.readFileSync(filePath, 'utf8');
    res.json(JSON.parse(data));
  } catch (error) {
    console.error('Failed to read domain_list.json:', error);
    res.status(500).json({ error: 'Failed to read domain list' });
  }
});

// Serve React app for all other routes (SPA fallback)
app.use((req, res, next) => {
  // If the request is not for an API route and file doesn't exist, serve index.html
  if (!req.path.startsWith('/api')) {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'), (err) => {
      if (err) {
        next(err);
      }
    });
  } else {
    next();
  }
});

// Get local IP address
function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      // Skip internal (loopback) and non-IPv4 addresses
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost';
}

app.listen(PORT, '0.0.0.0', () => {
  const localIP = getLocalIP();
  console.log('\n=================================================');
  console.log('🚀 Firewall Checker Web Server is running!');
  console.log('=================================================');
  console.log(`\n로컬 접속: http://localhost:${PORT}`);
  console.log(`네트워크 접속: http://${localIP}:${PORT}`);
  console.log('\n다른 PC에서 접속하려면:');
  console.log(`1. 브라우저에서 http://${localIP}:${PORT} 접속`);
  console.log('2. Windows 방화벽에서 포트 3000 허용 필요');
  console.log('=================================================\n');
});
