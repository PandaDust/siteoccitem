#!/usr/bin/env python3
"""Serveur local pour l'éditeur de contenu OCCITEM.
Lancer : python editor_server.py
Ouvrir  : http://localhost:8080/editor.html

Authentification : si les variables d'environnement AUTH_USER et AUTH_PASS
sont définies, un Basic Auth est exigé sur l'éditeur de contenu
(editor.html + /api/save + /api/upload-image). Si RH_AUTH_USER et RH_AUTH_PASS
sont définies, un Basic Auth (avec des identifiants distincts) est exigé sur
le mini-éditeur RH (career-admin.html + /api/save-careers +
/api/upload-careers-image). Le reste du site
(index.html, carriere.html, content.json, careers.json, assets...) reste
public. À activer avant toute exposition externe (ex : tunnel ngrok).
"""
import base64
import hmac
import http.server
import json
import os
import re
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

PORT = 8081
BASE_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = BASE_DIR / 'assets'
CONTENT_FILE = BASE_DIR / 'content.json'
CAREERS_FILE = BASE_DIR / 'careers.json'
AUTH_USER = os.environ.get('AUTH_USER')
AUTH_PASS = os.environ.get('AUTH_PASS')
RH_AUTH_USER = os.environ.get('RH_AUTH_USER')
RH_AUTH_PASS = os.environ.get('RH_AUTH_PASS')

MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 Mo
IMAGE_PATH_RE = re.compile(r'^assets/[A-Za-z0-9_\-./]+\.(png|jpg|jpeg|webp)$', re.IGNORECASE)

# Synchronisation git : chaque enregistrement est commité puis poussé sur
# GitHub. Désactivée par défaut — en édition locale, les commits doivent rester
# à la main de l'utilisateur. Le service systemd du VPS pose GIT_AUTO_SYNC=1.
GIT_AUTO_SYNC = os.environ.get('GIT_AUTO_SYNC') == '1'
GIT_LOG_FILE = BASE_DIR / 'git-sync.log'
# Sérialise les synchronisations : deux enregistrements rapprochés lanceraient
# sinon deux rebase/push concurrents dans le même dépôt.
_git_lock = threading.Lock()


def _git_log(message):
    stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(GIT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f'[{stamp}] {message}\n')
    except OSError:
        pass


def _git(*args, timeout=120):
    return subprocess.run(
        ('git',) + args, cwd=BASE_DIR,
        capture_output=True, text=True, timeout=timeout,
    )


def _git_sync_worker(paths, message):
    with _git_lock:
        try:
            _git('add', '--', *paths)
            # Rien d'indexé : l'enregistrement n'a pas modifié le contenu
            # (réécriture à l'identique). Inutile de créer un commit vide.
            if _git('diff', '--cached', '--quiet').returncode == 0:
                return
            r = _git('commit', '-m', message)
            if r.returncode != 0:
                _git_log(f'ECHEC commit : {r.stderr.strip()}')
                return
            _git_log(f'commit : {message}')

            # Rebase avant push : sans lui, un push local fait entre-temps
            # ferait rejeter le nôtre et le contenu du client resterait bloqué
            # sur le VPS jusqu'au cron de rattrapage.
            r = _git('pull', '--rebase')
            if r.returncode != 0:
                _git_log(f'ECHEC pull --rebase : {r.stderr.strip()} — rebase annule')
                _git('rebase', '--abort')
                return

            r = _git('push')
            if r.returncode != 0:
                # Le commit reste local ; le cron de rattrapage le poussera.
                _git_log(f'ECHEC push : {r.stderr.strip()}')
                return
            _git_log('push : OK')
        except subprocess.TimeoutExpired:
            _git_log('ECHEC : timeout git')
        except Exception as e:
            _git_log(f'ECHEC : {e}')


def git_sync(paths, message):
    """Commit + push en tâche de fond des fichiers modifiés par l'éditeur.

    Lancé dans un thread : le push distant prend 1 à 2 secondes, et l'interface
    ne doit pas rester figée en attendant GitHub. En cas d'échec, le commit
    subsiste localement et sera repris par le cron de rattrapage.
    """
    if not GIT_AUTO_SYNC:
        return
    threading.Thread(
        target=_git_sync_worker, args=(list(paths), message), daemon=True,
    ).start()

# Ressources protégées par les identifiants de l'éditeur de contenu (Mathieu)
MAIN_EDITOR_PATHS = {'/editor.html', '/api/save', '/api/upload-image'}
# Ressources protégées par les identifiants du mini-éditeur RH (offres d'emploi)
RH_EDITOR_PATHS = {'/career-admin.html', '/api/save-careers', '/api/upload-careers-image'}


class Handler(http.server.SimpleHTTPRequestHandler):
    def _check_auth(self):
        path = urlsplit(self.path).path
        if path in MAIN_EDITOR_PATHS:
            user, password = AUTH_USER, AUTH_PASS
        elif path in RH_EDITOR_PATHS:
            user, password = RH_AUTH_USER, RH_AUTH_PASS
        else:
            return True

        if not user or not password:
            return True
        expected = 'Basic ' + base64.b64encode(f'{user}:{password}'.encode()).decode()
        got = self.headers.get('Authorization', '')
        if hmac.compare_digest(got, expected):
            return True
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="OCCITEM"')
        self.send_header('Content-Length', '0')
        self.end_headers()
        return False

    def do_GET(self):
        if not self._check_auth():
            return
        super().do_GET()

    def do_POST(self):
        if not self._check_auth():
            return
        path = urlsplit(self.path).path
        if path == '/api/save':
            self._save()
        elif path == '/api/upload-image':
            self._upload_image()
        elif path == '/api/save-careers':
            self._save_careers()
        elif path == '/api/upload-careers-image':
            self._upload_image()
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
            git_sync(['content.json'], 'contenu : mise à jour depuis l\'éditeur')
            self._respond(200, {'ok': True})
        except json.JSONDecodeError as e:
            self._respond(400, {'ok': False, 'error': f'JSON invalide : {e}'})
        except Exception as e:
            self._respond(500, {'ok': False, 'error': str(e)})

    def _save_careers(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
            if CAREERS_FILE.exists():
                shutil.copy2(CAREERS_FILE, CAREERS_FILE.with_suffix('.json.bak'))
            with open(CAREERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            git_sync(['careers.json'], 'carrières : mise à jour des offres')
            self._respond(200, {'ok': True})
        except json.JSONDecodeError as e:
            self._respond(400, {'ok': False, 'error': f'JSON invalide : {e}'})
        except Exception as e:
            self._respond(500, {'ok': False, 'error': str(e)})

    def _upload_image(self):
        try:
            qs = parse_qs(urlsplit(self.path).query)
            target = (qs.get('target') or [''])[0]
            if not IMAGE_PATH_RE.match(target):
                return self._respond(400, {'ok': False, 'error': 'Chemin d\'image invalide'})

            dest = (BASE_DIR / target).resolve()
            if not dest.is_relative_to(ASSETS_DIR) or not dest.parent.is_dir():
                return self._respond(400, {'ok': False, 'error': 'Emplacement d\'image invalide'})

            length = int(self.headers.get('Content-Length', 0))
            if length <= 0 or length > MAX_IMAGE_SIZE:
                return self._respond(413, {'ok': False, 'error': 'Fichier trop volumineux (max 20 Mo)'})
            body = self.rfile.read(length)

            if dest.exists():
                shutil.copy2(dest, dest.with_suffix(dest.suffix + '.bak'))
            with open(dest, 'wb') as f:
                f.write(body)
            git_sync([target], f'image : remplacement de {target}')
            self._respond(200, {'ok': True, 'path': target})
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
    print(f'Éditeur OCCITEM       → http://localhost:{PORT}/editor.html')
    print(f'Éditeur RH — carrières → http://localhost:{PORT}/career-admin.html')
    if AUTH_USER and AUTH_PASS:
        print(f'Authentification éditeur de contenu activée (utilisateur : {AUTH_USER})')
    else:
        print('⚠ Éditeur de contenu sans authentification (AUTH_USER / AUTH_PASS non définies) — à éviter en exposition externe.')
    if RH_AUTH_USER and RH_AUTH_PASS:
        print(f'Authentification éditeur RH activée (utilisateur : {RH_AUTH_USER})')
    else:
        print('⚠ Éditeur RH sans authentification (RH_AUTH_USER / RH_AUTH_PASS non définies) — à éviter en exposition externe.')
    if GIT_AUTO_SYNC:
        print(f'Synchronisation git activée — chaque enregistrement est commité et poussé (journal : {GIT_LOG_FILE.name})')
    else:
        print('Synchronisation git désactivée (GIT_AUTO_SYNC≠1) — les commits restent manuels.')
    print('Ctrl+C pour arrêter\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServeur arrêté.')
