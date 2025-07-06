#!/usr/bin/env python3
"""
Simple HTTP Server for Spotify Visualizations
==============================================
Serves HTML visualizations via HTTP for better viewing experience
"""

import http.server
import socketserver
import webbrowser
import os
import time
from threading import Timer

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1)
    webbrowser.open('http://localhost:8080')

def main():
    """Start HTTP server for visualizations"""
    # Change to visualizations directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    visualizations_dir = os.path.join(os.path.dirname(script_dir), 'visualizations')
    os.chdir(visualizations_dir)
    
    PORT = 8080
    
    print("🌐 SPOTIFY VISUALIZATIONS HTTP SERVER")
    print("="*50)
    print(f"🚀 Starting server on http://localhost:{PORT}")
    print(f"📁 Serving files from: {os.getcwd()}")
    
    # List available files
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    if html_files:
        print(f"\n📊 Available visualizations:")
        for file in sorted(html_files):
            print(f"   • http://localhost:{PORT}/{file}")
    else:
        print("\n❌ No HTML files found. Run analysis scripts first!")
        return
    
    # Start server
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"\n🌐 Server running at http://localhost:{PORT}")
            print("📱 Opening browser automatically...")
            print("🛑 Press Ctrl+C to stop the server")
            
            # Open browser automatically
            Timer(1.0, open_browser).start()
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
