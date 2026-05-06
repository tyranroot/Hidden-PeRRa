#!/usr/bin/env python3

import sys
import os
import re
import requests
import time
import random
from urllib.parse import urljoin, urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

init(autoreset=True)

# Colors
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
W = Fore.WHITE
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    clear()
    print(f"""{C}{BOLD}
                                                                              
       ██╗  ██╗██╗██████╗ ██████╗ ███████╗███╗   ██╗██╗  ██╗            
       ██║  ██║██║██╔══██╗██╔══██╗██╔════╝████╗  ██║╚██╗██╔╝                  
       ███████║██║██║  ██║██████╔╝█████╗  ██╔██╗ ██║ ╚███╔╝                   
       ██╔══██║██║██║  ██║██╔══██╗██╔══╝  ██║╚██╗██║ ██╔██╗                   
       ██║  ██║██║██████╔╝██║  ██║███████╗██║ ╚████║██╔╝ ██╗                  
       ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝                               
                    Professional Hidden Elements Finder                            
                            Coded by: TyranRoot
                                                                              
{RESET}""")
    print(f"{Y}{BOLD}[!] Find hidden parameters, fields, directories, API endpoints{RESET}")
    print(f"{Y}{BOLD}[!] Use only on websites you OWN or have PERMISSION to test!{RESET}\n")

class HiddenXPro:
    def __init__(self, target):
        self.target = target.rstrip('/')
        self.domain = urlparse(target).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        self.results = {
            'target': target,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'hidden_form_fields': [],
            'hidden_parameters': [],
            'hidden_directories': [],
            'hidden_api_endpoints': [],
            'hidden_comments': [],
            'status_codes': {}
        }
    
    def log(self, msg, typ="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        if typ == "info":
            print(f"{C}[{ts}]{RESET} {msg}")
        elif typ == "success":
            print(f"{G}[{ts}] ✓{RESET} {msg}")
        elif typ == "warning":
            print(f"{Y}[{ts}] ⚠{RESET} {msg}")
        elif typ == "error":
            print(f"{R}[{ts}] ✗{RESET} {msg}")
        elif typ == "found":
            print(f"{R}[{ts}] 💀 FOUND!{RESET} {msg}")
    
    def fetch_page(self, url, retry=3):
        """Fetch page content with retry"""
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=15, allow_redirects=True)
                self.results['status_codes'][response.status_code] = self.results['status_codes'].get(response.status_code, 0) + 1
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403 or response.status_code == 429:
                    self.log(f"Rate limited (HTTP {response.status_code}), waiting...", "warning")
                    time.sleep(5)
                else:
                    self.log(f"HTTP {response.status_code} for {url}", "warning")
                    return None
            except requests.exceptions.Timeout:
                self.log(f"Timeout for {url}, retry {attempt+1}/{retry}", "warning")
                time.sleep(2)
            except Exception as e:
                self.log(f"Error: {str(e)[:50]}", "error")
                return None
        return None
    
    def check_robots_txt(self):
        """Check robots.txt for hidden paths"""
        self.log("Checking robots.txt...", "info")
        robots_url = urljoin(self.target, '/robots.txt')
        content = self.fetch_page(robots_url)
        
        if content:
            paths = re.findall(r'Disallow:\s*(.+)', content)
            for path in paths:
                if path.strip():
                    self.results['hidden_directories'].append(path.strip())
                    self.log(f"Found in robots.txt: {path.strip()}", "found")
    
    def check_sitemap(self):
        """Check sitemap.xml for hidden paths"""
        self.log("Checking sitemap.xml...", "info")
        sitemap_url = urljoin(self.target, '/sitemap.xml')
        content = self.fetch_page(sitemap_url)
        
        if content:
            urls = re.findall(r'<loc>(.*?)</loc>', content)
            for url in urls[:20]:
                if url not in self.results['hidden_api_endpoints']:
                    self.results['hidden_api_endpoints'].append(url)
                    self.log(f"Found in sitemap: {url}", "found")
    
    def find_hidden_form_fields(self, html, url):
        """Find hidden form fields"""
        self.log("Searching for hidden form fields...", "info")
        soup = BeautifulSoup(html, 'html.parser')
        
        forms = soup.find_all('form')
        for form in forms:
            hidden_fields = form.find_all('input', {'type': 'hidden'})
            for field in hidden_fields:
                name = field.get('name', 'Unknown')
                value = field.get('value', 'Empty')
                self.results['hidden_form_fields'].append({
                    'form_action': form.get('action', url),
                    'field_name': name,
                    'field_value': value[:50] + '...' if len(value) > 50 else value
                })
                self.log(f"Hidden field: {name} = {value[:30]}", "found")
    
    def find_hidden_parameters(self, html, url):
        """Find hidden parameters"""
        self.log("Searching for hidden parameters...", "info")
        
        patterns = [
            r'[?&]([a-zA-Z_][a-zA-Z0-9_]*)=',
            r'params\[["\']([^"\']+)["\']\]',
            r'data\[["\']([^"\']+)["\']\]',
            r'\.get\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']',
            r'url: ["\']([^"\']+)["\']',
            r'endpoint: ["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if match not in [p['name'] for p in self.results['hidden_parameters']]:
                    self.results['hidden_parameters'].append({
                        'name': match,
                        'source': 'JavaScript/HTML'
                    })
                    self.log(f"Parameter: {match}", "found")
    
    def find_hidden_directories(self):
        """Brute force hidden directories with better wordlist"""
        self.log("Scanning for hidden directories...", "info")
        
        common_dirs = [
            'admin', 'login', 'wp-admin', 'administrator', 'admincp', 'cpanel',
            'phpmyadmin', 'mysql', 'backup', 'backups', 'config', 'configuration',
            'logs', 'log', 'tmp', 'temp', 'uploads', 'upload', 'downloads',
            'api', 'v1', 'v2', 'v3', 'api/v1', 'api/v2', 'rest', 'graphql',
            'test', 'dev', 'staging', 'stage', 'development', 'testing',
            'old', 'new', 'hidden', 'secret', 'private', 'internal',
            '.git', '.env', '.htaccess', '.ssh', '.well-known', 'cgi-bin',
            'database', 'db', 'sql', 'dump', 'export', 'import',
            'assets', 'static', 'public', 'resources', 'files', 'data',
            'includes', 'modules', 'plugins', 'themes', 'lib', 'vendor',
            'docs', 'documentation', 'guide', 'manual', 'help',
            'ajax', 'ajax.php', 'action.php', 'process.php', 'handler.php'
        ]
        
        found = []
        
        def check_dir(dir_name):
            url = urljoin(self.target, dir_name + '/')
            response = self.session.get(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                found.append(dir_name)
                self.log(f"Directory: /{dir_name}/", "found")
            elif response.status_code == 403:
                self.log(f"Directory /{dir_name}/ (403 Forbidden)", "warning")
            elif response.status_code == 401:
                self.log(f"Directory /{dir_name}/ (401 Auth Required)", "warning")
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            executor.map(check_dir, common_dirs)
        
        self.results['hidden_directories'] = found
    
    def find_hidden_api_endpoints(self, html):
        """Find hidden API endpoints"""
        self.log("Searching for API endpoints...", "info")
        
        patterns = [
            r'https?://[^"\']*api[^"\']*',
            r'https?://[^"\']*/v\d+[^"\']*',
            r'["\'](/api/[^"\']+)["\']',
            r'["\'](/v\d+/[^"\']+)["\']',
            r'["\'](/rest/[^"\']+)["\']',
            r'["\'](/graphql)[^"\']*["\']',
            r'\.get\(["\'](/[^"\']+)["\']',
            r'\.post\(["\'](/[^"\']+)["\']'
        ]
        
        endpoints = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if match.startswith('/'):
                    full_url = urljoin(self.target, match)
                elif match.startswith('http'):
                    full_url = match
                else:
                    continue
                
                if full_url not in endpoints:
                    endpoints.add(full_url)
                    self.results['hidden_api_endpoints'].append(full_url)
                    self.log(f"API: {full_url}", "found")
    
    def find_hidden_comments(self, html):
        """Find hidden comments"""
        self.log("Searching for hidden comments...", "info")
        
        comment_pattern = r'<!--(.*?)-->'
        matches = re.findall(comment_pattern, html, re.DOTALL)
        
        important_keywords = ['TODO', 'FIXME', 'NOTE', 'HACK', 'BUG', 'SECURITY', 'API', 'KEY', 'SECRET', 'PASSWORD']
        
        for match in matches:
            match = match.strip()
            if len(match) > 10:
                is_important = any(keyword in match.upper() for keyword in important_keywords)
                self.results['hidden_comments'].append({
                    'comment': match[:200],
                    'type': 'Important' if is_important else 'Regular'
                })
                if is_important:
                    self.log(f"Important comment: {match[:80]}", "found")
    
    def scan(self):
        """Main scan function"""
        self.log(f"Starting hidden elements scan on {self.target}", "info")
        print()
        
        # Check robots.txt and sitemap first
        self.check_robots_txt()
        self.check_sitemap()
        
        # Fetch main page
        html = self.fetch_page(self.target)
        if not html:
            self.log("Failed to fetch main page! Trying alternative methods...", "warning")
            # Try with different user agents
            for ua in USER_AGENTS:
                self.session.headers['User-Agent'] = ua
                html = self.fetch_page(self.target)
                if html:
                    self.log(f"Success with User-Agent: {ua[:50]}...", "success")
                    break
        
        if not html:
            self.log("Could not fetch target URL! Website may be blocking bots.", "error")
            return
        
        # Run scans that need HTML
        self.find_hidden_form_fields(html, self.target)
        self.find_hidden_parameters(html, self.target)
        self.find_hidden_api_endpoints(html)
        self.find_hidden_comments(html)
        
        # Run directory scan
        self.find_hidden_directories()
        
        print()
        self.log("Scan completed!", "success")
    
    def generate_html_report(self):
        """Generate HTML report"""
        filename = f"hiddenx_report_{self.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        hidden_fields_html = ""
        for item in self.results['hidden_form_fields']:
            hidden_fields_html += f"<tr><td style='padding:8px;border-bottom:1px solid #333;'>{item['form_action']}</td><td style='padding:8px;border-bottom:1px solid #333;'>{item['field_name']}</td><td style='padding:8px;border-bottom:1px solid #333;'>{item['field_value']}</td></tr>"
        
        hidden_params_html = ""
        for item in self.results['hidden_parameters']:
            hidden_params_html += f"<tr><td style='padding:8px;border-bottom:1px solid #333;'>{item['name']}</td><td style='padding:8px;border-bottom:1px solid #333;'>{item['source']}</td></tr>"
        
        hidden_dirs_html = ""
        for item in self.results['hidden_directories']:
            hidden_dirs_html += f"<tr><td style='padding:8px;border-bottom:1px solid #333;'><a href='{urljoin(self.target, item+'/')}' target='_blank' style='color:#0f0;'>{item}/</a></td></tr>"
        
        api_html = ""
        for item in self.results['hidden_api_endpoints']:
            api_html += f"<tr><td style='padding:8px;border-bottom:1px solid #333;'><a href='{item}' target='_blank' style='color:#0f0;'>{item}</a></td></tr>"
        
        comments_html = ""
        for item in self.results['hidden_comments']:
            color = '#ff4444' if item['type'] == 'Important' else '#888'
            comments_html += f"<tr><td style='padding:8px;border-bottom:1px solid #333;color:{color};'>{item['type']}</td><td style='padding:8px;border-bottom:1px solid #333;'>{item['comment']}</td></tr>"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>HiddenX - {self.domain}</title>
<style>
body{{background:#0a0a0a;font-family:monospace;color:#0f0;padding:20px;}}
.container{{max-width:1200px;margin:0 auto;}}
h1{{color:#0f0;border-bottom:2px solid #0f0;}}
h2{{color:#0ff;margin-top:30px;}}
.card{{background:#0a1520;border:1px solid #0f0;border-radius:10px;padding:20px;margin-bottom:20px;}}
table{{width:100%;border-collapse:collapse;}}
th{{text-align:left;padding:10px;background:#0a1520;border-bottom:2px solid #0f0;color:#0ff;}}
td{{padding:10px;border-bottom:1px solid #333;word-break:break-all;}}
a{{color:#0f0;text-decoration:none;}}
.footer{{text-align:center;margin-top:40px;color:#666;}}
.summary{{display:inline-block;margin:10px;padding:10px;background:#0a1520;border-radius:5px;}}
</style>
</head>
<body>
<div class="container">
<h1>🔍 HiddenX  - Security Report</h1>
<div class="card">
<p><strong>Target:</strong> {self.target}</p>
<p><strong>Scan Date:</strong> {self.results['timestamp']}</p>
</div>
<div class="card">
<h2>📊 Summary</h2>
<div class="summary">Form Fields: {len(self.results['hidden_form_fields'])}</div>
<div class="summary">Parameters: {len(self.results['hidden_parameters'])}</div>
<div class="summary">Directories: {len(self.results['hidden_directories'])}</div>
<div class="summary">API Endpoints: {len(self.results['hidden_api_endpoints'])}</div>
<div class="summary">Comments: {len(self.results['hidden_comments'])}</div>
</div>
<div class="card"><h2>📝 Hidden Form Fields</h2><table><tr><th>Form Action</th><th>Field Name</th><th>Value</th></tr>{hidden_fields_html or '<tr><td colspan="3">None found</td></tr>'}</table></div>
<div class="card"><h2>🔍 Hidden Parameters</h2><table><tr><th>Parameter</th><th>Source</th></tr>{hidden_params_html or '<tr><td colspan="2">None found</td></tr>'}</table></div>
<div class="card"><h2>📁 Hidden Directories</h2><table><tr><th>Directory</th></tr>{hidden_dirs_html or '<tr><td>None found</td></tr>'}</table></div>
<div class="card"><h2>🌐 API Endpoints</h2><table><tr><th>URL</th></tr>{api_html or '<tr><td>None found</td></tr>'}</table></div>
<div class="card"><h2>💬 Hidden Comments</h2><table><tr><th>Type</th><th>Comment</th></tr>{comments_html or '<tr><td colspan="2">None found</td></tr>'}</table></div>
<div class="footer">Generated by HiddenX  | Educational Only | TyraxZero</div>
</div>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename

def main():
    banner()
    
    target = input(f"  {C}{BOLD}[>]{RESET} Target URL (https://example.com): {W}").strip()
    
    if not target.startswith('http'):
        target = 'https://' + target
    
    print(f"\n{Y}[!] Scanning {target} for hidden elements{RESET}\n")
    
    scanner = HiddenXPro(target)
    scanner.scan()
    
    report = scanner.generate_html_report()
    print(f"\n{G}[✓] Report saved: {report}{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Stopped by user{RESET}")
