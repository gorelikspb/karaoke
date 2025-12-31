# Простой HTTP сервер для караоке-сайта
# Использует встроенные возможности PowerShell

$port = 8000
$publicPath = Join-Path $PSScriptRoot "public"

Write-Host "🎤 Запуск караоке-сайта..." -ForegroundColor Green
Write-Host "📁 Папка: $publicPath" -ForegroundColor Cyan
Write-Host "🌐 URL: http://localhost:$port" -ForegroundColor Yellow
Write-Host ""
Write-Host "Нажмите Ctrl+C для остановки" -ForegroundColor Gray
Write-Host ""

# Проверяем наличие Node.js
$nodeVersion = Get-Command node -ErrorAction SilentlyContinue

if ($nodeVersion) {
    Write-Host "✅ Используем Node.js http-server" -ForegroundColor Green
    Set-Location $publicPath
    npx --yes http-server -p $port -o
} else {
    # Альтернатива: используем встроенный .NET HttpListener
    Write-Host "⚠️  Node.js не найден. Используем простой сервер..." -ForegroundColor Yellow
    
    Add-Type -TypeDefinition @"
    using System;
    using System.IO;
    using System.Net;
    using System.Text;
    using System.Threading;

    public class SimpleHttpServer {
        private HttpListener listener;
        private string basePath;
        private int port;

        public SimpleHttpServer(string path, int p) {
            basePath = path;
            port = p;
            listener = new HttpListener();
            listener.Prefixes.Add($"http://localhost:{port}/");
        }

        public void Start() {
            listener.Start();
            Console.WriteLine($"Сервер запущен на http://localhost:{port}/");
            
            while (listener.IsListening) {
                var context = listener.GetContext();
                ThreadPool.QueueUserWorkItem(ProcessRequest, context);
            }
        }

        private void ProcessRequest(object state) {
            var context = (HttpListenerContext)state;
            var request = context.Request;
            var response = context.Response;

            try {
                string path = request.Url.LocalPath;
                if (path == "/") path = "/index.html";
                
                string filePath = Path.Combine(basePath, path.TrimStart('/').Replace('/', '\\'));
                
                if (File.Exists(filePath)) {
                    byte[] buffer = File.ReadAllBytes(filePath);
                    string contentType = GetContentType(filePath);
                    
                    response.ContentType = contentType;
                    response.ContentLength64 = buffer.Length;
                    response.StatusCode = 200;
                    response.OutputStream.Write(buffer, 0, buffer.Length);
                } else {
                    response.StatusCode = 404;
                    byte[] buffer = Encoding.UTF8.GetBytes("404 Not Found");
                    response.OutputStream.Write(buffer, 0, buffer.Length);
                }
            } catch (Exception ex) {
                response.StatusCode = 500;
                byte[] buffer = Encoding.UTF8.GetBytes($"Error: {ex.Message}");
                response.OutputStream.Write(buffer, 0, buffer.Length);
            } finally {
                response.OutputStream.Close();
            }
        }

        private string GetContentType(string filePath) {
            string ext = Path.GetExtension(filePath).ToLower();
            switch (ext) {
                case ".html": return "text/html; charset=utf-8";
                case ".css": return "text/css";
                case ".js": return "application/javascript";
                case ".json": return "application/json";
                case ".png": return "image/png";
                case ".jpg": case ".jpeg": return "image/jpeg";
                default: return "text/plain";
            }
        }

        public void Stop() {
            listener.Stop();
        }
    }
"@

    $server = New-Object SimpleHttpServer $publicPath $port
    Start-Process "http://localhost:$port"
    $server.Start()
}


