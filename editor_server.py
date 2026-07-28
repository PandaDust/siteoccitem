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
import hashlib
import hmac
import http.server
import json
import os
import re
import secrets
import shutil
import subprocess
import threading
import time
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

# Comptes créés depuis l'éditeur. Stockés HORS du dépôt : le site est servi
# depuis un clone git sur le VPS, et un users.json placé dans BASE_DIR verrait
# ses empreintes de mots de passe poussées sur GitHub au premier enregistrement,
# puis écrasées à chaque déploiement. Le service systemd pose USERS_FILE.
USERS_FILE = Path(os.environ.get('USERS_FILE') or (BASE_DIR / 'users.json'))
PBKDF2_ITERATIONS = 600_000
# Sérialise les écritures concurrentes dans users.json.
_users_lock = threading.Lock()
# Basic Auth réémet les identifiants à CHAQUE requête ; sans ce cache, charger
# l'éditeur (page + JSON + images) déclencherait une dizaine de PBKDF2 à
# 600 000 itérations, soit plusieurs secondes d'attente. On mémorise l'empreinte
# de l'en-tête, jamais le mot de passe.
_auth_cache = {}
_auth_cache_lock = threading.Lock()
AUTH_CACHE_TTL = 300  # secondes

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

# Ressources exigeant l'accès « content » (éditeur de contenu principal)
MAIN_EDITOR_PATHS = {'/editor.html', '/api/save', '/api/upload-image'}
# Ressources exigeant l'accès « careers » (mini-éditeur RH, offres d'emploi)
RH_EDITOR_PATHS = {'/career-admin.html', '/api/save-careers', '/api/upload-careers-image'}
# Gestion des comptes : réservée aux administrateurs.
ADMIN_PATHS = {'/api/users/list', '/api/users/create', '/api/users/delete'}
# Accessibles à tout compte authentifié (profil courant, mot de passe personnel).
SELF_PATHS = {'/api/me', '/api/users/password'}

USERNAME_RE = re.compile(r'^[a-zA-Z0-9._-]{3,32}$')
MIN_PASSWORD_LEN = 8


def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt.encode('ascii'), PBKDF2_ITERATIONS,
    )
    return f'pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${dk.hex()}'


def _verify_password(password, stored):
    try:
        algo, iterations, salt, digest = stored.split('$')
        if algo != 'pbkdf2_sha256':
            return False
        dk = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt.encode('ascii'), int(iterations),
        )
    except (ValueError, AttributeError):
        return False
    return hmac.compare_digest(dk.hex(), digest)


def _load_users():
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('users', {}) if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        # Fichier illisible : on refuse les comptes créés plutôt que d'ouvrir
        # l'accès. Le compte maître (variables d'environnement) reste utilisable
        # pour se reconnecter et rétablir la situation.
        return {}


def _save_users(users):
    """Écrit users.json de façon atomique (écriture puis remplacement).

    Une écriture directe interrompue laisserait un fichier tronqué : plus aucun
    compte créé ne fonctionnerait jusqu'à intervention manuelle.
    """
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = USERS_FILE.with_suffix('.json.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump({'users': users}, f, ensure_ascii=False, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, USERS_FILE)
    _auth_cache_clear()


def _auth_cache_clear():
    with _auth_cache_lock:
        _auth_cache.clear()


def _account_from_credentials(user, password):
    """Identifie un compte à partir d'un couple identifiant / mot de passe.

    Le compte maître provient des variables d'environnement, jamais de
    users.json : même un fichier vidé ou corrompu ne peut donc pas verrouiller
    l'accès à l'éditeur.
    """
    if AUTH_USER and AUTH_PASS and hmac.compare_digest(user, AUTH_USER) \
            and hmac.compare_digest(password, AUTH_PASS):
        return {
            'name': user, 'access': ['content', 'careers'],
            'admin': True, 'master': True,
        }

    # Compte RH hérité de la configuration, conservé pour ne pas rompre un
    # accès existant. Supprimable en retirant RH_AUTH_USER / RH_AUTH_PASS une
    # fois un vrai compte créé depuis l'éditeur.
    if RH_AUTH_USER and RH_AUTH_PASS and hmac.compare_digest(user, RH_AUTH_USER) \
            and hmac.compare_digest(password, RH_AUTH_PASS):
        return {
            'name': user, 'access': ['careers'],
            'admin': False, 'master': False, 'legacy': True,
        }

    entry = _load_users().get(user)
    if entry and _verify_password(password, entry.get('hash', '')):
        return {
            'name': user,
            'access': list(entry.get('access', [])),
            'admin': bool(entry.get('admin')),
            'master': False,
        }
    return None


def _authenticate(header):
    """Résout l'en-tête Authorization en compte, avec cache à durée limitée."""
    if not header or not header.startswith('Basic '):
        return None

    key = hashlib.sha256(header.encode('utf-8')).hexdigest()
    now = time.monotonic()
    with _auth_cache_lock:
        hit = _auth_cache.get(key)
        if hit and hit[1] > now:
            return hit[0]

    try:
        raw = base64.b64decode(header[6:]).decode('utf-8')
        user, _, password = raw.partition(':')
    except (ValueError, UnicodeDecodeError):
        return None

    account = _account_from_credentials(user, password)
    with _auth_cache_lock:
        # Les échecs sont mémorisés brièvement eux aussi : sans cela, un client
        # bouclant avec de mauvais identifiants relancerait un PBKDF2 complet
        # à chaque tentative.
        _auth_cache[key] = (account, now + AUTH_CACHE_TTL)
    return account


class Handler(http.server.SimpleHTTPRequestHandler):
    def _check_auth(self):
        """Vérifie que la requête a le droit d'atteindre le chemin demandé.

        Renseigne self.account au passage, pour que les handlers sachent qui
        agit (utile à la gestion des comptes).
        """
        path = urlsplit(self.path).path
        self.account = None

        if path in MAIN_EDITOR_PATHS:
            required = 'content'
        elif path in RH_EDITOR_PATHS:
            required = 'careers'
        elif path in ADMIN_PATHS:
            required = 'admin'
        elif path in SELF_PATHS:
            required = 'any'
        else:
            return True

        # Aucun compte maître configuré : on conserve le comportement
        # historique (éditeur ouvert) plutôt que de verrouiller un usage local.
        # Le service systemd du VPS définit toujours AUTH_USER / AUTH_PASS.
        if not AUTH_USER or not AUTH_PASS:
            self.account = {
                'name': 'anonyme', 'access': ['content', 'careers'],
                'admin': True, 'master': True, 'unconfigured': True,
            }
            return True

        account = _authenticate(self.headers.get('Authorization', ''))
        if account is None:
            return self._deny_auth()

        self.account = account
        if required == 'admin' and not account['admin']:
            # Authentifié mais sans le rôle : renvoyer 401 relancerait une
            # demande d'identifiants sans issue. 403 dit clairement que le
            # compte est valide mais non autorisé.
            return self._forbid('Réservé aux administrateurs')
        if required in ('content', 'careers') and required not in account['access']:
            return self._forbid('Ce compte n\'a pas accès à cette partie de l\'éditeur')
        return True

    def _deny_auth(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="OCCITEM"')
        self.send_header('Content-Length', '0')
        self.end_headers()
        return False

    def _forbid(self, message):
        body = json.dumps({'ok': False, 'error': message}, ensure_ascii=False).encode('utf-8')
        self.send_response(403)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
        return False

    def do_GET(self):
        if not self._check_auth():
            return
        path = urlsplit(self.path).path
        # Interceptés avant SimpleHTTPRequestHandler, qui chercherait sinon un
        # fichier portant ce nom sur le disque.
        if path == '/api/me':
            return self._me()
        if path == '/api/users/list':
            return self._users_list()
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
        elif path == '/api/users/create':
            self._user_create()
        elif path == '/api/users/delete':
            self._user_delete()
        elif path == '/api/users/password':
            self._user_password()
        else:
            self.send_error(404)

    def _read_json(self):
        length = int(self.headers.get('Content-Length', 0))
        if length <= 0 or length > 1024 * 1024:
            raise ValueError('Corps de requête invalide')
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def _me(self):
        a = self.account or {}
        self._respond(200, {
            'ok': True,
            'name': a.get('name'),
            'access': a.get('access', []),
            'admin': bool(a.get('admin')),
            'master': bool(a.get('master')),
        })

    def _users_list(self):
        users = _load_users()
        listed = [{
            'name': name,
            'access': list(entry.get('access', [])),
            'admin': bool(entry.get('admin')),
            'created': entry.get('created'),
            'master': False,
        } for name, entry in sorted(users.items())]

        # Le compte maître ne figure pas dans users.json : il est ajouté ici
        # pour que l'interface puisse l'afficher (et le marquer non supprimable).
        if AUTH_USER:
            listed.insert(0, {
                'name': AUTH_USER, 'access': ['content', 'careers'],
                'admin': True, 'created': None, 'master': True,
            })
        if RH_AUTH_USER:
            listed.append({
                'name': RH_AUTH_USER, 'access': ['careers'],
                'admin': False, 'created': None, 'master': False, 'legacy': True,
            })
        self._respond(200, {'ok': True, 'users': listed})

    def _user_create(self):
        try:
            data = self._read_json()
        except (ValueError, json.JSONDecodeError) as e:
            return self._respond(400, {'ok': False, 'error': f'Requête invalide : {e}'})

        name = (data.get('name') or '').strip()
        password = data.get('password') or ''
        access = [a for a in data.get('access', []) if a in ('content', 'careers')]
        is_admin = bool(data.get('admin'))

        if not USERNAME_RE.match(name):
            return self._respond(400, {'ok': False, 'error':
                'Identifiant invalide (3 à 32 caractères : lettres, chiffres, . _ -)'})
        if len(password) < MIN_PASSWORD_LEN:
            return self._respond(400, {'ok': False, 'error':
                f'Mot de passe trop court ({MIN_PASSWORD_LEN} caractères minimum)'})
        if not access and not is_admin:
            return self._respond(400, {'ok': False, 'error': 'Sélectionnez au moins un accès'})
        # Un homonyme du compte maître serait ignoré à la connexion (le maître
        # est vérifié en premier) : autant refuser clairement la création.
        if name in (AUTH_USER, RH_AUTH_USER):
            return self._respond(409, {'ok': False, 'error':
                'Cet identifiant est déjà utilisé par un compte de configuration'})

        with _users_lock:
            users = _load_users()
            if name in users:
                return self._respond(409, {'ok': False, 'error': 'Ce compte existe déjà'})
            users[name] = {
                'hash': _hash_password(password),
                'access': access,
                'admin': is_admin,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
            }
            _save_users(users)
        return self._respond(200, {'ok': True, 'name': name})

    def _user_delete(self):
        try:
            data = self._read_json()
        except (ValueError, json.JSONDecodeError) as e:
            return self._respond(400, {'ok': False, 'error': f'Requête invalide : {e}'})

        name = (data.get('name') or '').strip()
        if name in (AUTH_USER, RH_AUTH_USER):
            return self._respond(403, {'ok': False, 'error':
                'Les comptes définis dans la configuration ne peuvent pas être supprimés ici'})
        # Se supprimer soi-même déconnecterait l'administrateur en pleine action.
        if self.account and name == self.account.get('name'):
            return self._respond(400, {'ok': False, 'error':
                'Vous ne pouvez pas supprimer votre propre compte'})

        with _users_lock:
            users = _load_users()
            if name not in users:
                return self._respond(404, {'ok': False, 'error': 'Compte introuvable'})
            del users[name]
            _save_users(users)
        return self._respond(200, {'ok': True, 'name': name})

    def _user_password(self):
        """Changement de mot de passe : le sien, ou celui d'un autre si admin."""
        try:
            data = self._read_json()
        except (ValueError, json.JSONDecodeError) as e:
            return self._respond(400, {'ok': False, 'error': f'Requête invalide : {e}'})

        current = self.account or {}
        name = (data.get('name') or current.get('name') or '').strip()
        password = data.get('password') or ''

        if name != current.get('name') and not current.get('admin'):
            return self._respond(403, {'ok': False, 'error':
                'Seul un administrateur peut modifier le mot de passe d\'un autre compte'})
        if len(password) < MIN_PASSWORD_LEN:
            return self._respond(400, {'ok': False, 'error':
                f'Mot de passe trop court ({MIN_PASSWORD_LEN} caractères minimum)'})
        if name in (AUTH_USER, RH_AUTH_USER):
            return self._respond(403, {'ok': False, 'error':
                'Ce compte est défini dans la configuration du serveur : '
                'son mot de passe se change dans /etc/occitem/editor.env'})

        with _users_lock:
            users = _load_users()
            if name not in users:
                return self._respond(404, {'ok': False, 'error': 'Compte introuvable'})
            users[name]['hash'] = _hash_password(password)
            _save_users(users)
        return self._respond(200, {'ok': True, 'name': name})

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
