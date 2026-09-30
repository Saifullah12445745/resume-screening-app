import io
import unittest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from main import app

class ApiTests(unittest.TestCase):
    def setUp(self): self.client = TestClient(app)
    def test_screen_and_duplicate(self):
        response = self.client.post('/api/screen', data={'job_description':'Python and Docker developer', 'required_skills':'python,docker'}, files=[('files',('alice.txt',b'Python developer','text/plain')), ('files',('copy.txt',b'Python developer','text/plain'))])
        self.assertEqual(response.status_code,200)
        body = response.json()
        self.assertEqual(body['candidates'][0]['coverage'],50)
        self.assertEqual(body['candidates'][0]['missing'],['docker'])
        self.assertEqual(len(body['issues']),1)
    def test_pdf(self):
        stream = io.BytesIO(); pdf = canvas.Canvas(stream)
        pdf.drawString(50,700,'Python Docker developer'); pdf.save()
        response = self.client.post('/api/screen', data={'job_description':'Python developer', 'required_skills':'python'}, files={'files':('cv.pdf',stream.getvalue(),'application/pdf')})
        self.assertEqual(response.json()['candidates'][0]['coverage'],100)
    def test_validation(self):
        for data in [{'job_description':' ', 'required_skills':'python'}, {'job_description':'Python'}, {'job_description':'Python','method':'bad'}]:
            response = self.client.post('/api/screen',data=data,files={'files':('a.txt',b'Python','text/plain')})
            self.assertEqual(response.status_code,400)
    def test_bad_document_does_not_stop_batch(self):
        response = self.client.post('/api/screen',data={'job_description':'Python','required_skills':'python'},files=[('files',('bad.pdf',b'broken','application/pdf')),('files',('good.txt',b'Python','text/plain'))])
        self.assertEqual(len(response.json()['candidates']),1)
        self.assertEqual(len(response.json()['issues']),1)
    def test_suggestions(self):
        response = self.client.post('/api/suggest-skills',data={'job_description':'C++ Node.js JavaScript'})
        self.assertEqual(response.json()['skills'],['c++','javascript','node.js'])

if __name__ == '__main__': unittest.main()
