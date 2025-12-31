# Простой HTTP сервер через PowerShell (без Python/Node.js)
# Использует встроенный .NET HttpListener

$port = 8000
$publicPath = Join-Path $PSScriptRoot "public"

Write-Host "🎤 Запуск караоке-сайта..." -ForegroundColor Green
Write-Host "📁 Папка: $publicPath" -ForegroundColor Cyan
Write-Host "🌐 Откройте в браузере: http://localhost:$port" -ForegroundColor Yellow
Write-Host ""
Write-Host "Нажмите Ctrl+C для остановки" -ForegroundColor Gray
Write-Host ""

# Открываем браузер
Start-Process "http://localhost:$port"

# Создаем HTTP сервер
Add-Type -TypeDefinition @"
using System;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public class SimpleHttpServer {
    private HttpListener listener;
    private string basePath;
    private int port;

    public SimpleHttpServer(string path, int p) {
        basePath = path;
        port = p;
        listener = new HttpListener();
        listener.Prefixes.Add("http://localhost:" + port + "/");
    }

    public void Start() {
        listener.Start();
        Console.WriteLine("Сервер запущен на http://localhost:" + port + "/");
        
        Task.Run(() => {
            while (listener.IsListening) {
                try {
                    var context = listener.GetContext();
                    ThreadPool.QueueUserWorkItem(ProcessRequest, context);
                } catch (Exception) {
                    break;
                }
            }
        });
    }

    private void ProcessRequest(object state) {
        var context = (HttpListenerContext)state;
        var request = context.Request;
        var response = context.Response;

        try {
            string path = request.Url.LocalPath;
            if (path == "/") path = "/index.html";
            
            string filePath = Path.Combine(basePath, path.TrimStart('/').Replace('/', Path.DirectorySeparatorChar));
            
            if (File.Exists(filePath)) {
                byte[] buffer = File.ReadAllBytes(filePath);
                string contentType = GetContentType(filePath);
                
                response.ContentType = contentType;
                response.ContentLength64 = buffer.Length;
                response.StatusCode = 200;
                response.OutputStream.Write(buffer, 0, buffer.Length);
            } else {
                response.StatusCode = 404;
                string notFound = "404 Not Found: " + path;
                byte[] buffer = Encoding.UTF8.GetBytes(notFound);
                response.ContentType = "text/plain; charset=utf-8";
                response.ContentLength64 = buffer.Length;
                response.OutputStream.Write(buffer, 0, buffer.Length);
            }
        } catch (Exception ex) {
            response.StatusCode = 500;
            string error = "Error: " + ex.Message;
            byte[] buffer = Encoding.UTF8.GetBytes(error);
            response.ContentType = "text/plain; charset=utf-8";
            response.ContentLength64 = buffer.Length;
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
            case ".gif": return "image/gif";
            case ".svg": return "image/svg+xml";
            default: return "text/plain; charset=utf-8";
        }
    }

    public void Stop() {
        if (listener.IsListening) {
            listener.Stop();
        }
    }
}
"@

try {
    $server = New-Object SimpleHttpServer $publicPath $port
    $server.Start()
    
    # Ждем нажатия Ctrl+C
    Write-Host "Сервер работает. Нажмите любую клавишу для остановки..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    $server.Stop()
    Write-Host "`nСервер остановлен." -ForegroundColor Yellow
} catch {
    Write-Host "Ошибка: $_" -ForegroundColor Red
}


