const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// Read the Excel file
const workbook = XLSX.readFile(path.join(__dirname, '통합 문서.xlsx'));

// Get the first sheet
const sheetName = workbook.SheetNames[0];
const worksheet = workbook.Sheets[sheetName];

// Convert to JSON (with all data, use defval to keep nulls consistent)
const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: null });

// Remove the header row and empty rows
const dataRows = jsonData.filter((row, index) => {
  // Skip empty rows
  if (!row || row.length === 0 || row.every(cell => cell === null || cell === undefined || cell === '')) return false;
  // Skip header row (contains "No", "구분", "서비스명", etc.)
  if (row[0] === 'No' || row[0] === 'NO' || row[1] === '구분') return false;
  return true;
});

// Ensure all rows have exactly 8 columns (No, 구분, 서비스명, IP, PORT, 도메인, 비고, 확인일자)
const normalizedRows = dataRows.map(row => {
  // Pad with nulls if needed
  while (row.length < 8) {
    row.push(null);
  }
  // Trim to 8 columns if longer
  return row.slice(0, 8);
});

// Keep original Excel order (no sorting)

// Write to domain_list.json
const outputPath = path.join(__dirname, 'data', 'domain_list.json');
fs.writeFileSync(outputPath, JSON.stringify(normalizedRows, null, 4), 'utf8');

console.log(`Successfully converted Excel to JSON!`);
console.log(`Total rows: ${normalizedRows.length}`);
console.log(`Output file: ${outputPath}`);
console.log(`\nSample row structure (8 columns):`);
console.log(`[No, 구분, 서비스명, IP, PORT, 도메인, 비고, 확인일자]`);
console.log(`First row:`, normalizedRows[0]);
