export const MAX_BATCH_MB = import.meta.env?.VITE_VERCEL === "1" ? 4 : 50;
export const MAX_FILE_SIZE = Math.min(10, MAX_BATCH_MB) * 1024 * 1024;
export function validateFiles(files) {
  if(files.length > 50) return 'Upload at most 50 resumes.';
  if(files.some(f => !/\.(pdf|docx|txt)$/i.test(f.name))) return 'Use PDF, DOCX or TXT files.';
  if(files.some(f => f.size === 0 || f.size > MAX_FILE_SIZE)) return `Files must be nonempty and no larger than ${Math.min(10, MAX_BATCH_MB)} MB.`;
  if(files.reduce((sum,f)=>sum+f.size,0)>MAX_BATCH_MB*1024*1024) return `Use a batch smaller than ${MAX_BATCH_MB} MB.`;
  return '';
}
export function toCSV(rows, shortlist) {
  const quote = value => {
    let text = Array.isArray(value) ? value.join(', ') : String(value ?? '');
    if (/^\s*[=+\-@]/.test(text)) text = "'" + text;
    return '"' + text.replaceAll('"','""') + '"';
  };
  const values = [['Resume','Skill coverage (%)','Semantic similarity (%)','Matched skills','Missing skills','Shortlisted'], ...rows.map(r=>[r.name,r.coverage,r.semantic,r.matched,r.missing,shortlist.includes(r.id)?'Yes':'No'])];
  return '\uFEFF' + values.map(row=>row.map(quote).join(',')).join('\r\n');
}
export function downloadCSV(rows, shortlist, filename) {
  const url = URL.createObjectURL(new Blob([toCSV(rows,shortlist)],{type:'text/csv;charset=utf-8'}));
  const link = document.createElement('a'); link.href=url; link.download=filename; link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
