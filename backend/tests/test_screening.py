import io
import unittest
import zipfile
from screening import extract_text, extract_skills, skill_comparison, export_csv, chunks

class ScreeningTests(unittest.TestCase):
    def test_skill_boundaries_and_symbols(self):
        self.assertEqual(extract_skills('C++ C# Node.js JavaScript git Docker'), ['c#', 'c++', 'docker', 'git', 'javascript', 'node.js'])
        self.assertEqual(extract_skills('digital reaction mysql'), ['mysql'])
    def test_aliases(self):
        self.assertEqual(extract_skills('NodeJS PostgreSQL PowerBI'), ['node.js', 'postgresql', 'power bi'])
    def test_coverage(self):
        self.assertEqual(skill_comparison('Python', ['python', 'docker']), (['python'], ['docker'], 50.0))
        self.assertIsNone(skill_comparison('Python', [])[2])
    def test_txt_and_invalid(self):
        self.assertEqual(extract_text('resume.TXT', b'Python developer'), 'Python developer')
        for name, data in [('r.txt', b''), ('r.exe', b'hi'), ('r.txt', b'   ')]:
            with self.assertRaises(ValueError): extract_text(name, data)
    def test_docx(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as z:
            z.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Python developer</w:t></w:r></w:p></w:body></w:document>')
        self.assertEqual(extract_text('r.docx', buffer.getvalue()), 'Python developer')
    def test_export(self):
        csv = export_csv([{'Resume':'=HYPERLINK("x")','Text':'PRIVATE'}]).decode('utf-8-sig')
        self.assertNotIn('PRIVATE', csv)
        self.assertIn("'=HYPERLINK", csv)
    def test_chunk_tail(self):
        self.assertEqual(chunks('one two three', 2), ['one two', 'three'])

if __name__ == '__main__': unittest.main()
