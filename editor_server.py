#!/usr/bin/env python3
"""Serveur local pour l'éditeur de contenu OCCITEM.
Lancer : python editor_server.py
Ouvrir  : http://localhost:8080/editor.html
"""
import http.server
import json
import os
import shutil
from pathlib import Path

PORT = 8081
BASE_DIR = Path(__file__).parent.resolve()
CONTENT_FILE = BASE_DIR / 'content.json'


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/save':
            self._save()
        else:
            self.send_error(404)

    def _save(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
            if CONTENT_FILE.exists():
                shutil.copy2(CONTENT_FILE, CONTENT_FILE.with_suffix('.json.bak'))
            with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._respond(200, {'ok': True})
        except json.JSONDecodeError as e:
            self._respond(400, {'ok': False, 'error': f'JSON invalide : {e}'})
        except Exception as e:
            self._respond(500, {'ok': False, 'error': str(e)})

    def _respond(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f'  {self.address_string()} — {fmt % args}')


if __name__ == '__main__':
    os.chdir(BASE_DIR)
    try:
        httpd = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    except OSError:
        print(f'Erreur : le port {PORT} est déjà utilisé.')
        print(f'Modifiez la variable PORT dans ce fichier, ou libérez le port avec :')
        print(f'  kill $(lsof -ti:{PORT})')
        raise SystemExit(1)
    print(f'Éditeur OCCITEM → http://localhost:{PORT}/editor.html')
    print('Ctrl+C pour arrêter\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServeur arrêté.')
