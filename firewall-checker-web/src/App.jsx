import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const [domainList, setDomainList] = useState([]);
  const [logs, setLogs] = useState([]);
  const [failedDomains, setFailedDomains] = useState(new Set());

  useEffect(() => {
    const fetchData = async () => {
      try {
        const domainsResponse = await fetch('/api/domains');
        const domains = await domainsResponse.json();
        setDomainList(domains);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setLogs(['데이터를 가져오는데 실패했습니다: ' + error.message]);
      }
    };
    fetchData();
  }, []);

  const handleDomainCheck = async () => {
    setLogs(['Starting domain check...']);
    const newFailedDomains = new Set();

    for (let index = 0; index < domainList.length; index++) {
      const domain = domainList[index];
      const originalDomain = domain[3]; // Extract the domain name from the array (URL field)
      if (originalDomain && originalDomain.trim() !== '') {
        // Sanitize the domain: remove protocol, path, and extra characters
        let cleanDomain = originalDomain.replace(/^(https?|ldap):\/\//, '');
        cleanDomain = cleanDomain.split('/')[0];
        cleanDomain = cleanDomain.split(',')[0];
        cleanDomain = cleanDomain.trim();

        if (cleanDomain) {
          try {
            const response = await fetch('/api/check-domain', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ domain: cleanDomain }),
            });
            const result = await response.json();
            setLogs(prevLogs => [...prevLogs, `> ${cleanDomain}`, result.message]);

            // Check if the result contains error message
            if (result.message.includes('을(를) 찾을 수 없습니다') || result.message.includes('오류')) {
              newFailedDomains.add(index);
            }
          } catch (error) {
            setLogs(prevLogs => [...prevLogs, `> ${cleanDomain}`, `오류: ${error.message}`]);
            newFailedDomains.add(index);
          }
        } else {
          setLogs(prevLogs => [...prevLogs, `> ${originalDomain} (Skipping invalid domain)`]);
          newFailedDomains.add(index);
        }
      } else {
        setLogs(prevLogs => [...prevLogs, `> (Skipping empty domain)`]);
        newFailedDomains.add(index);
      }
    }

    setFailedDomains(newFailedDomains);
    setLogs(prevLogs => [...prevLogs, 'Domain check finished.']);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Firewall Port Checker (Web)
            </Typography>
          </Toolbar>
        </AppBar>

        <Box sx={{ border: 1, borderColor: 'divider', m: 1, p: 1 }}>
            <Button variant="contained" sx={{mr: 1}} onClick={handleDomainCheck}>도메인 점검</Button>
            <Button variant="outlined">자동 점검 시작</Button>
        </Box>

        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
              <TableContainer component={Paper}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>업무</TableCell>
                      <TableCell>기관</TableCell>
                      <TableCell>IP</TableCell>
                      <TableCell>URL</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {domainList.map((domain, index) => (
                      <TableRow
                        key={index}
                        sx={{
                          backgroundColor: failedDomains.has(index) ? 'rgba(211, 47, 47, 0.2)' : 'inherit',
                          '&:hover': {
                            backgroundColor: failedDomains.has(index) ? 'rgba(211, 47, 47, 0.3)' : 'rgba(255, 255, 255, 0.08)',
                          }
                        }}
                      >
                        <TableCell>{domain[0]}</TableCell>
                        <TableCell>{domain[1]}</TableCell>
                        <TableCell>{domain[2]}</TableCell>
                        <TableCell>{domain[3]}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
        </Box>

        <Paper sx={{ m: 1, p: 2, flexShrink: 0, height: '30%', overflowY: 'auto' }}>
            <Typography variant="h6">실시간 로그</Typography>
            <pre>
              {logs.map((log, index) => (
                <div key={index}>{log}</div>
              ))}
            </pre>
        </Paper>

      </Box>
    </ThemeProvider>
  );
}

export default App;
